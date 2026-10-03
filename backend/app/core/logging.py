"""
Structured logging configuration for RESQ AGENT.
"""
import logging
import sys
from app.core.config import settings


def setup_logging():
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO
    log_format = (
        "%(asctime)s [%(levelname)s] [%(name)s] "
        "[request_id=%(request_id)s] %(message)s"
        if not settings.DEBUG
        else "%(asctime)s [%(levelname)s] [%(name)s]: %(message)s"
    )

    class ContextFilter(logging.Filter):
        def filter(self, record):
            if not hasattr(record, "request_id"):
                record.request_id = "-"
            return True

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(log_format))
    handler.addFilter(ContextFilter())

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers = [handler]

    # Silence overly verbose external libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


logger = logging.getLogger("resq_agent")
