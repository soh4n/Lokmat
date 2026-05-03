"""
LokMat API — Cache service (Redis / Memorystore).

Provides response caching, session memory, and rate limit counters.
Per GEMINI.md: cache repeated prompts in Redis with 5-min TTL.
"""

import hashlib
import logging
from typing import Any

logger = logging.getLogger(__name__)

# In-memory fallback cache (when Redis is unavailable)
_memory_cache: dict[str, tuple[Any, float]] = {}


class CacheService:
    """
    Redis-compatible cache service with in-memory fallback.

    In production, connects to Memorystore (Redis).
    For local dev, falls back to a simple dict cache.
    """

    def __init__(self, redis_url: str | None = None) -> None:
        self._redis = None
        self._redis_url = redis_url
        if redis_url:
            try:
                import redis.asyncio as aioredis
                self._redis = aioredis.from_url(redis_url, decode_responses=True)  # type: ignore[no-untyped-call]
                logger.info("Redis cache connected")
            except Exception as e:
                logger.warning(f"Redis unavailable, using memory cache: {e}")

    @staticmethod
    def _hash_key(prefix: str, *parts: str) -> str:
        """Generate a deterministic cache key."""
        raw = ":".join(parts)
        hashed = hashlib.sha256(raw.encode()).hexdigest()[:16]
        return f"lokmat:{prefix}:{hashed}"

    async def get_cached_response(self, prompt: str) -> str | None:
        """
        Get a cached AI response for a given prompt.

        Args:
            prompt: The user's message text.

        Returns:
            Cached response string, or None if not found.
        """
        key = self._hash_key("chat", prompt.strip().lower())

        if self._redis:
            try:
                cached = await self._redis.get(key)
                if cached:
                    logger.info("Cache HIT", extra={"key": key})
                    return cached
            except Exception as e:
                logger.warning(f"Redis GET failed: {e}")

        # Memory fallback
        import time
        entry = _memory_cache.get(key)
        if entry and time.time() < entry[1]:
            logger.info("Memory cache HIT", extra={"key": key})
            return entry[0]

        return None

    async def set_cached_response(self, prompt: str, response: str, ttl: int = 300) -> None:
        """
        Cache an AI response.

        Args:
            prompt: The user's message text.
            response: AI response to cache.
            ttl: Time-to-live in seconds (default 5 minutes per GEMINI.md).
        """
        key = self._hash_key("chat", prompt.strip().lower())

        if self._redis:
            try:
                await self._redis.setex(key, ttl, response)
                return
            except Exception as e:
                logger.warning(f"Redis SET failed: {e}")

        # Memory fallback
        import time
        _memory_cache[key] = (response, time.time() + ttl)

    async def check_rate_limit(self, user_id: str, limit: int = 60, window: int = 60) -> bool:
        """
        Check if user has exceeded rate limit.

        Args:
            user_id: User identifier (phone number).
            limit: Max requests per window.
            window: Window size in seconds.

        Returns:
            True if within limit, False if exceeded.
        """
        key = f"lokmat:rate:{user_id}"

        if self._redis:
            try:
                pipe = self._redis.pipeline()
                await pipe.incr(key)
                await pipe.expire(key, window)
                results = await pipe.execute()
                return int(results[0]) <= limit
            except Exception as e:
                logger.warning(f"Rate limit check failed: {e}")
                return True

        # Memory fallback — always allow
        return True

    async def health_check(self) -> bool:
        """Check Redis connectivity."""
        if self._redis:
            try:
                return await self._redis.ping()
            except Exception:
                return False
        return True  # Memory mode is always "healthy"


# Global singleton
cache_service = CacheService()
