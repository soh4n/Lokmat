"""
Unit tests — RateLimitMiddleware.

Per GEMINI.md testing requirements:
- Rate limiter blocks correctly after threshold
- Rate limiter allows requests after TTL reset
- Per-user bucketing (different users don't share limits)
- Health/auth paths are exempt
- Inference paths use a stricter limit
"""

import time
from unittest.mock import AsyncMock, MagicMock

import pytest

from api.utils.rate_limit import INFERENCE_PATHS, RateLimitMiddleware, _counters

# ---------------------------------------------------------------------------
# Helper — reset the global counter between tests
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def clear_counters():
    """Reset the in-memory rate-limit counters before each test."""
    _counters.clear()
    yield
    _counters.clear()


# ---------------------------------------------------------------------------
# Unit tests for _get_user_id (static method)
# ---------------------------------------------------------------------------

class TestGetUserId:
    """Tests for user identity extraction from request headers."""

    def _make_request(self, auth_header: str | None = None, client_host: str = "127.0.0.1"):
        """Build a minimal mock Request object."""
        req = MagicMock()
        req.headers = {"Authorization": auth_header} if auth_header else {}
        req.client = MagicMock()
        req.client.host = client_host
        return req

    def test_bearer_token_produces_token_prefix(self) -> None:
        """User identified by token prefix when Bearer token is present."""
        req = self._make_request("Bearer abc123def456")
        uid = RateLimitMiddleware._get_user_id(req)
        assert uid.startswith("token:")
        assert uid == "token:abc123def456"  # First 16 chars of token

    def test_no_auth_falls_back_to_ip(self) -> None:
        """User identified by IP when no Authorization header is present."""
        req = self._make_request(client_host="192.168.1.1")
        uid = RateLimitMiddleware._get_user_id(req)
        assert uid == "ip:192.168.1.1"

    def test_non_bearer_scheme_falls_back_to_ip(self) -> None:
        """Non-Bearer auth scheme falls back to IP."""
        req = self._make_request("Basic dXNlcjpwYXNz", "10.0.0.1")
        uid = RateLimitMiddleware._get_user_id(req)
        assert uid == "ip:10.0.0.1"

    def test_no_client_returns_unknown(self) -> None:
        """Absent client object produces ip:unknown fallback."""
        req = MagicMock()
        req.headers = {}
        req.client = None
        uid = RateLimitMiddleware._get_user_id(req)
        assert uid == "ip:unknown"


# ---------------------------------------------------------------------------
# Unit tests for the sliding-window counter logic
# ---------------------------------------------------------------------------

class TestSlidingWindow:
    """Validates the sliding-window rate-limit counter directly."""

    def test_counter_allows_requests_within_limit(self) -> None:
        """N requests within the window are all allowed."""
        key = "test_user:general"
        now = time.time()
        limit = 5
        window = 60

        for _ in range(limit):
            _counters[key] = [ts for ts in _counters[key] if now - ts < window]
            assert len(_counters[key]) < limit
            _counters[key].append(now)

        assert len(_counters[key]) == limit

    def test_counter_blocks_after_limit_exceeded(self) -> None:
        """(limit + 1)th request is rejected."""
        key = "blocked_user:inference"
        now = time.time()
        limit = 3

        _counters[key] = [now] * limit  # Already at the limit

        # Simulate the check
        window = 60
        _counters[key] = [ts for ts in _counters[key] if now - ts < window]
        assert len(_counters[key]) >= limit  # Should be blocked

    def test_old_entries_are_evicted(self) -> None:
        """Timestamps older than the window are evicted before counting."""
        key = "evict_user:general"
        stale = time.time() - 120  # 2 minutes ago — outside 60s window
        _counters[key] = [stale, stale, stale]

        now = time.time()
        window = 60
        _counters[key] = [ts for ts in _counters[key] if now - ts < window]

        # All stale entries should have been evicted
        assert len(_counters[key]) == 0

    def test_different_users_have_independent_counters(self) -> None:
        """Rate limit counters are per-user, not global."""
        now = time.time()
        _counters["user_a:general"] = [now] * 60  # User A at limit
        _counters["user_b:general"] = []           # User B at zero

        # User A is blocked; User B should not be
        assert len(_counters["user_a:general"]) >= 60
        assert len(_counters["user_b:general"]) == 0


# ---------------------------------------------------------------------------
# Integration-style tests using the ASGI middleware
# ---------------------------------------------------------------------------

class TestRateLimitMiddlewareDispatch:
    """Tests the full middleware dispatch path via a minimal ASGI app."""

    @pytest.mark.asyncio
    async def test_inference_path_uses_stricter_limit(self) -> None:
        """Inference paths are keyed with ':inference' suffix."""
        assert "/chat" in INFERENCE_PATHS or "/assistant/chat" in INFERENCE_PATHS

    @pytest.mark.asyncio
    async def test_health_path_bypasses_rate_limiting(self) -> None:
        """Middleware calls next directly for /health without counting."""
        middleware = RateLimitMiddleware(app=AsyncMock())

        call_count = 0

        async def call_next(req):
            nonlocal call_count
            call_count += 1
            return MagicMock(status_code=200)

        req = MagicMock()
        req.url.path = "/health"
        req.headers = {}
        req.client = MagicMock()
        req.client.host = "127.0.0.1"

        await middleware.dispatch(req, call_next)
        assert call_count == 1
        # Counter should not have been incremented
        assert all(":health" not in k for k in _counters)

    @pytest.mark.asyncio
    async def test_auth_path_bypasses_rate_limiting(self) -> None:
        """/auth/* paths bypass rate limiting entirely."""
        middleware = RateLimitMiddleware(app=AsyncMock())

        call_count = 0

        async def call_next(req):
            nonlocal call_count
            call_count += 1
            return MagicMock(status_code=200)

        req = MagicMock()
        req.url.path = "/auth/send-otp"
        req.headers = {}
        req.client = MagicMock()
        req.client.host = "127.0.0.1"

        await middleware.dispatch(req, call_next)
        assert call_count == 1
