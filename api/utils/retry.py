"""
LokMat API — Retry utility with exponential backoff.

Required on all Gemini API calls per GEMINI.md efficiency rules.
"""

import asyncio
import logging
import random
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

logger = logging.getLogger(__name__)
T = TypeVar("T")


def with_exponential_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    multiplier: float = 2.0,
) -> Callable[..., Any]:
    """
    Decorator that retries an async function with exponential backoff + jitter.

    Args:
        max_retries: Maximum number of retry attempts.
        base_delay:  Initial delay in seconds before the first retry.
        multiplier:  Factor by which delay increases after each attempt.

    Returns:
        Decorated async function with retry logic.
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            delay = base_delay
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as exc:
                    if attempt == max_retries:
                        logger.error(
                            "Retry exhausted",
                            extra={
                                "function": func.__name__,
                                "attempts": max_retries,
                                "error": str(exc),
                            },
                        )
                        raise
                    jitter = random.uniform(0, delay * 0.1)
                    logger.warning(
                        "Retrying after error",
                        extra={
                            "attempt": attempt + 1,
                            "delay_s": round(delay + jitter, 2),
                            "error": str(exc),
                        },
                    )
                    await asyncio.sleep(delay + jitter)
                    delay *= multiplier

        return wrapper

    return decorator
