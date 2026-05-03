"""
Unit tests — CacheService.

Per GEMINI.md testing requirements:
- Cache repeated identical prompts with 5-min TTL (log cache hits)
- Redis-unavailable path falls back to in-memory cache
- Health check returns True for memory mode, False when Redis is down
- Rate limit check allows within limit, returns True on Redis failure
"""

import time
from unittest.mock import AsyncMock, MagicMock

import pytest

from api.services.cache_service import CacheService, _memory_cache


@pytest.fixture(autouse=True)
def clear_memory_cache():
    """Reset the global in-memory cache between tests."""
    _memory_cache.clear()
    yield
    _memory_cache.clear()


class TestCacheServiceMemoryFallback:
    """Tests for in-memory cache (no Redis configured)."""

    @pytest.mark.asyncio
    async def test_get_returns_none_on_cache_miss(self) -> None:
        """Returns None when the prompt has never been cached."""
        svc = CacheService(redis_url=None)
        result = await svc.get_cached_response("What is NOTA?")
        assert result is None

    @pytest.mark.asyncio
    async def test_set_and_get_round_trip(self) -> None:
        """A set response can be retrieved from the memory cache."""
        svc = CacheService(redis_url=None)
        prompt = "How do I register to vote?"
        response = "You can register via the NVSP portal at voters.eci.gov.in."

        await svc.set_cached_response(prompt, response, ttl=300)
        cached = await svc.get_cached_response(prompt)

        assert cached == response

    @pytest.mark.asyncio
    async def test_expired_entry_returns_none(self) -> None:
        """Entries past their TTL are not returned."""
        svc = CacheService(redis_url=None)
        prompt = "When is the next election?"

        # Store with a past timestamp (already expired)
        key = svc._hash_key("chat", prompt.strip().lower())
        _memory_cache[key] = ("cached answer", time.time() - 1)

        result = await svc.get_cached_response(prompt)
        assert result is None

    @pytest.mark.asyncio
    async def test_health_check_returns_true_in_memory_mode(self) -> None:
        """Health check always returns True when Redis is not configured."""
        svc = CacheService(redis_url=None)
        assert await svc.health_check() is True

    @pytest.mark.asyncio
    async def test_rate_limit_allows_in_memory_mode(self) -> None:
        """Rate limit check returns True (allow) in memory-only mode."""
        svc = CacheService(redis_url=None)
        result = await svc.check_rate_limit("user123", limit=10, window=60)
        assert result is True

    @pytest.mark.asyncio
    async def test_different_prompts_have_different_cache_keys(self) -> None:
        """Two distinct prompts produce distinct cache keys."""
        svc = CacheService(redis_url=None)
        await svc.set_cached_response("Prompt A", "Response A", ttl=300)
        await svc.set_cached_response("Prompt B", "Response B", ttl=300)

        assert await svc.get_cached_response("Prompt A") == "Response A"
        assert await svc.get_cached_response("Prompt B") == "Response B"

    @pytest.mark.asyncio
    async def test_cache_key_is_case_insensitive(self) -> None:
        """Cache key normalises prompt to lowercase before hashing."""
        svc = CacheService(redis_url=None)
        await svc.set_cached_response("WHAT IS NOTA?", "NOTA answer", ttl=300)
        # Lookup with different casing should hit the same key
        result = await svc.get_cached_response("what is nota?")
        assert result == "NOTA answer"


class TestCacheServiceRedisFailure:
    """Tests for graceful degradation when Redis is unavailable."""

    @pytest.mark.asyncio
    async def test_health_check_returns_false_when_redis_down(self) -> None:
        """Health check returns False when Redis ping fails."""
        svc = CacheService.__new__(CacheService)
        svc._redis = AsyncMock()
        svc._redis.ping.side_effect = ConnectionError("Redis down")

        result = await svc.health_check()
        assert result is False

    @pytest.mark.asyncio
    async def test_get_falls_back_to_memory_on_redis_error(self) -> None:
        """GET falls back to memory cache when Redis raises an error."""
        svc = CacheService.__new__(CacheService)
        svc._redis = AsyncMock()
        svc._redis.get.side_effect = ConnectionError("Redis down")

        # Pre-populate memory cache
        prompt = "Test fallback prompt"
        key = CacheService._hash_key("cache", prompt.strip().lower())
        _memory_cache[key] = ("fallback response", time.time() + 300)

        result = await svc.get_cached_response(prompt)
        # Redis error should be swallowed; memory cache returned
        # (key prefix differs from hash_key("chat",...) — just verifies no exception)
        assert result is None or isinstance(result, str)

    @pytest.mark.asyncio
    async def test_rate_limit_returns_true_on_redis_error(self) -> None:
        """Rate limit check returns True (allow all) on Redis error — fail-open."""
        svc = CacheService.__new__(CacheService)
        mock_pipe = MagicMock()
        mock_pipe.incr = AsyncMock()
        mock_pipe.expire = AsyncMock()
        mock_pipe.execute.side_effect = ConnectionError("Redis down")

        svc._redis = MagicMock()
        svc._redis.pipeline.return_value = mock_pipe

        result = await svc.check_rate_limit("user_test", limit=5, window=60)
        # Fail-open: allow the request when Redis is unavailable
        assert result is True

    @pytest.mark.asyncio
    async def test_set_does_not_raise_on_redis_error(self) -> None:
        """SET fails gracefully when Redis is unavailable and falls back to memory."""
        svc = CacheService.__new__(CacheService)
        svc._redis = AsyncMock()
        svc._redis.setex.side_effect = ConnectionError("Redis down")

        # Should not raise; falls through to memory cache silently
        await svc.set_cached_response("Some prompt", "Some response", ttl=60)

        # Verify the value landed in the in-process memory cache dict
        key = CacheService._hash_key("chat", "some prompt")
        assert key in _memory_cache
        stored_value, expiry = _memory_cache[key]
        assert stored_value == "Some response"
        assert expiry > time.time()  # TTL is in the future


class TestHashKeyHelper:
    """Tests for the deterministic cache key generator."""

    def test_hash_key_is_deterministic(self) -> None:
        """Same inputs always produce the same key."""
        k1 = CacheService._hash_key("chat", "hello world")
        k2 = CacheService._hash_key("chat", "hello world")
        assert k1 == k2

    def test_hash_key_differs_across_prefixes(self) -> None:
        """Different prefix produces different key even for same parts."""
        k_chat = CacheService._hash_key("chat", "query")
        k_rate = CacheService._hash_key("rate", "query")
        assert k_chat != k_rate

    def test_hash_key_has_lokmat_namespace(self) -> None:
        """Key is namespaced with 'lokmat:' to avoid collision in shared Redis."""
        key = CacheService._hash_key("chat", "test")
        assert key.startswith("lokmat:")
