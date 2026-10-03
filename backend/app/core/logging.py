"""
Structured application logging for RESQ AGENT.
Formats logs with timestamp, level, service, request_id, and message.
Enforces strict sanitization to never log passwords, tokens, API keys, or sensitive personal data.
"""
from datetime import datetime, timezone
import json
import logging
import re
import sys
from typing import Any, Dict

from app.core.config import settings

# Sensitive keyword patterns that must never appear in raw logs
SENSITIVE_PATTERNS = [
    re.compile(r'(password["\']?\s*[:=]\s*["\']?)([^"\'\s,]+)', re.IGNORECASE),
    re.compile(r'(token["\']?\s*[:=]\s*["\']?)([^"\'\s,]+)', re.IGNORECASE),
    re.compile(r'(secret["\']?\s*[:=]\s*["\']?)([^"\'\s,]+)', re.IGNORECASE),
    re.compile(r'(authorization["\']?\s*[:=]\s*["\']?Bearer\s+)([^"\'\s,]+)', re.IGNORECASE),
    re.compile(r'(api[_-]?key["\']?\s*[:=]\s*["\']?)([^"\'\s,]+)', re.IGNORECASE),
]


def sanitize_log_message(msg: str) -> str:
    """Masks credentials, tokens, and secrets from log strings."""
    sanitized = msg
    for pattern in SENSITIVE_PATTERNS:
        sanitized = pattern.sub(r'\1[REDACTED]', sanitized)
    return sanitized


class StructuredJsonFormatter(logging.Formatter):
    """
    Outputs structured log records conforming to enterprise SIEM/observability requirements.
    Fields: timestamp, level, service, request_id, message.
    """
    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.now(timezone.utc).isoformat()
        request_id = getattr(record, "request_id", "-")
        message = sanitize_log_message(record.getMessage())

        log_data: Dict[str, Any] = {
            "timestamp": timestamp,
            "level": record.levelname,
            "service": "resq-agent",
            "request_id": request_id,
            "message": message,
        }

        if record.exc_info and settings.DEBUG:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


class ContextFilter(logging.Filter):
    """Ensures request_id is always present on the log record."""
    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "request_id"):
            record.request_id = "-"
        return True


def setup_logging():
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(StructuredJsonFormatter())
    handler.addFilter(ContextFilter())

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers = [handler]

    # Silence overly noisy third-party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


logger = logging.getLogger("resq_agent")
