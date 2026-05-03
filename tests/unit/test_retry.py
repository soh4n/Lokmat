"""
Unit tests — Retry decorator with exponential backoff.

Per GEMINI.md testing requirements:
- Retry decorator retries on transient errors and raises after exhaustion.
"""

import asyncio

import pytest

from api.utils.retry import with_exponential_backoff


class TransientError(Exception):
    """Simulated transient error."""
    pass


@pytest.mark.asyncio
async def test_retry_succeeds_on_first_attempt() -> None:
    """Function succeeds immediately — no retries needed."""
    call_count = 0

    @with_exponential_backoff(max_retries=3, base_delay=0.01)
    async def succeeds() -> None:
        nonlocal call_count
        call_count += 1
        return "ok"

    result = await succeeds()
    assert result == "ok"
    assert call_count == 1


@pytest.mark.asyncio
async def test_retry_succeeds_after_transient_failure() -> None:
    """Function fails twice then succeeds on third attempt."""
    call_count = 0

    @with_exponential_backoff(max_retries=3, base_delay=0.01)
    async def flaky() -> None:
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise TransientError("transient")
        return "recovered"  # type: ignore

    result = await flaky()
    assert result == "recovered"
    assert call_count == 3


@pytest.mark.asyncio
async def test_retry_raises_after_exhaustion() -> None:
    """Function fails on all attempts — raises the final exception."""
    call_count = 0

    @with_exponential_backoff(max_retries=2, base_delay=0.01)
    async def always_fails() -> None:
        nonlocal call_count
        call_count += 1
        raise TransientError(f"fail #{call_count}")

    with pytest.raises(TransientError, match="fail #3"):
        await always_fails()

    assert call_count == 3  # 1 initial + 2 retries


@pytest.mark.asyncio
async def test_retry_preserves_return_value() -> None:
    """Retry decorator preserves the function's return value."""
    @with_exponential_backoff(max_retries=1, base_delay=0.01)
    async def returns_dict() -> None:
        return {"status": "ok", "tokens": 42}  # type: ignore

    result = await returns_dict()
    assert result == {"status": "ok", "tokens": 42}


@pytest.mark.asyncio
async def test_retry_respects_max_retries_zero() -> None:
    """With max_retries=0, no retries — fails immediately."""
    call_count = 0

    @with_exponential_backoff(max_retries=0, base_delay=0.01)
    async def no_retry() -> None:
        nonlocal call_count
        call_count += 1
        raise TransientError("immediate fail")

    with pytest.raises(TransientError):
        await no_retry()

    assert call_count == 1
