"""
LokMat API — Structured JSON logging for Cloud Logging.

Per GEMINI.md: all logs structured JSON, compatible with Cloud Logging.
"""

import json
import logging
import sys
from datetime import UTC, datetime
from typing import Any


class CloudLoggingFormatter(logging.Formatter):
    """
    JSON-structured log formatter compatible with Google Cloud Logging.

    Outputs logs in a format that Cloud Logging automatically parses
    into structured log entries with severity, labels, and metadata.
    """

    SEVERITY_MAP = {
        logging.DEBUG: "DEBUG",
        logging.INFO: "INFO",
        logging.WARNING: "WARNING",
        logging.ERROR: "ERROR",
        logging.CRITICAL: "CRITICAL",
    }

    # Standard LogRecord attributes to exclude from structured extras
    _STANDARD_ATTRS = {
        'name', 'msg', 'args', 'created', 'relativeCreated', 'exc_info',
        'exc_text', 'stack_info', 'lineno', 'funcName', 'pathname',
        'filename', 'module', 'levelno', 'levelname', 'thread',
        'threadName', 'process', 'processName', 'msecs', 'message',
        'taskName',
    }

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON for Cloud Logging."""
        log_entry: dict[str, Any] = {
            "severity": self.SEVERITY_MAP.get(record.levelno, "DEFAULT"),
            "message": record.getMessage(),
            "timestamp": datetime.now(UTC).isoformat(),
            "logger": record.name,
            "module": record.module,
        }

        # Add structured extras (intent, tokens, latency, etc.)
        extras = {
            k: v
            for k, v in record.__dict__.items()
            if k not in self._STANDARD_ATTRS
            and not k.startswith('_')
        }
        if extras:
            log_entry["labels"] = extras

        # Add exception info if present
        if record.exc_info and record.exc_info[1]:
            log_entry["error"] = {
                "type": type(record.exc_info[1]).__name__,
                "message": str(record.exc_info[1]),
            }

        return json.dumps(log_entry, default=str)


def setup_cloud_logging(debug: bool = False) -> None:
    """
    Configure structured JSON logging for the entire application.

    Args:
        debug: If True, use DEBUG level and add console output.
    """
    root = logging.getLogger()
    root.setLevel(logging.DEBUG if debug else logging.INFO)

    # Remove existing handlers
    root.handlers.clear()

    # JSON handler for Cloud Logging
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(CloudLoggingFormatter())
    root.addHandler(handler)

    # Suppress noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if debug else logging.WARNING
    )
