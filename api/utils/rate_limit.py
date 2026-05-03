"""
LokMat API — Rate limiting middleware.

Two-layer rate limiting per GEMINI.md:
- 60 req/min per user (general)
- 10 req/min on inference endpoints
"""

import logging
import time
from collections import defaultdict
from typing import Any

from fastapi import Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware

from api.config import settings

logger = logging.getLogger(__name__)

# In-memory rate limiter (production uses Redis via cache_service)
_counters: dict[str, list[float]] = defaultdict(list)

# Inference-heavy endpoints
INFERENCE_PATHS = {"/chat", "/assistant/chat"}


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Per-user rate limiting middleware.

    Per GEMINI.md:
    - Default: 60 req/min per user
    - Inference: 10 req/min per user
    """

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        """Check rate limit before processing request."""
        # Skip health and auth endpoints
        if request.url.path in ("/health", "/", "/docs", "/redoc", "/openapi.json"):
            return await call_next(request)  # type: ignore
        if request.url.path.startswith("/auth"):
            return await call_next(request)  # type: ignore

        # Identify user by token or IP
        user_id = self._get_user_id(request)
        path = request.url.path

        # Determine limit
        if path in INFERENCE_PATHS:
            limit = settings.inference_rate_limit_per_minute
            window_key = f"{user_id}:inference"
        else:
            limit = settings.rate_limit_per_minute
            window_key = f"{user_id}:general"

        # Check limit
        now = time.time()
        window = 60  # 1 minute

        # Clean old entries
        _counters[window_key] = [
            ts for ts in _counters[window_key] if now - ts < window
        ]

        if len(_counters[window_key]) >= limit:
            retry_after = int(window - (now - _counters[window_key][0]))
            logger.warning(
                "Rate limit exceeded",
                extra={"user": user_id, "path": path, "limit": limit},
            )
            return Response(
                content=f'{{"detail":"Rate limit exceeded. Try again in {retry_after}s","retry_after":{retry_after}}}',
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                headers={
                    "Content-Type": "application/json",
                    "Retry-After": str(retry_after),
                },
            )

        _counters[window_key].append(now)
        return await call_next(request)  # type: ignore

    @staticmethod
    def _get_user_id(request: Request) -> str:
        """Extract user identifier from auth header or IP."""
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            # Use a hash of the token as the user ID
            token = auth[7:]
            return f"token:{token[:16]}"
        # Fallback to IP
        client = request.client
        return f"ip:{client.host}" if client else "ip:unknown"
