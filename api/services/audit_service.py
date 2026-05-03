"""
LokMat API — Audit service for Cloud Logging.

Structured JSON audit logging for all significant actions.
Per GEMINI.md: intent, model, tokens, latency → Cloud Logging.
"""

import logging
import time
from typing import Any

logger = logging.getLogger("lokmat.audit")


class AuditService:
    """Structured audit logging service for Cloud Logging integration."""

    @staticmethod
    def log_chat_event(
        user_phone: str | None,
        intent: str,
        model: str,
        tokens: int,
        latency_ms: int,
        status: str = "success",
        detail: str = "",
    ) -> None:
        """
        Log a chat inference event.

        Per GEMINI.md: every inference must be audit logged with
        intent, model, tokens, and latency.
        """
        logger.info(
            "chat_inference",
            extra={
                "event_type": "chat_inference",
                "user_phone": user_phone or "anonymous",
                "intent": intent,
                "model": model,
                "tokens": tokens,
                "latency_ms": latency_ms,
                "status": status,
                "detail": detail,
            },
        )

    @staticmethod
    def log_auth_event(
        phone: str,
        action: str,
        status: str = "success",
        detail: str = "",
    ) -> None:
        """Log an authentication event (OTP send, verify, login)."""
        logger.info(
            "auth_event",
            extra={
                "event_type": "auth_event",
                "user_phone": phone,
                "action": action,
                "status": status,
                "detail": detail,
            },
        )

    @staticmethod
    def log_profile_event(
        phone: str,
        action: str,
        status: str = "success",
    ) -> None:
        """Log a profile create/update event."""
        logger.info(
            "profile_event",
            extra={
                "event_type": "profile_event",
                "user_phone": phone,
                "action": action,
                "status": status,
            },
        )

    @staticmethod
    def log_error(
        action: str,
        error: str,
        user_phone: str | None = None,
    ) -> None:
        """Log an error event."""
        logger.error(
            "error_event",
            extra={
                "event_type": "error",
                "user_phone": user_phone or "unknown",
                "action": action,
                "error": error,
            },
        )


class Timer:
    """Context manager for measuring latency in milliseconds."""

    def __init__(self) -> None:
        self.start: float = 0
        self.elapsed_ms: int = 0

    def __enter__(self) -> "Timer":
        self.start = time.perf_counter()
        return self

    def __exit__(self, *args: Any) -> None:
        self.elapsed_ms = int((time.perf_counter() - self.start) * 1000)


audit = AuditService()
