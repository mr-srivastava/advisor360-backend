"""Structured Logging Implementation

Provides structured logging with configurable levels, JSON formatting,
and context management for better observability and debugging.
"""

import json
import logging
import sys
from contextvars import ContextVar
from datetime import datetime
from logging.handlers import RotatingFileHandler
from typing import Any, Optional

from ..config.app_config import get_config

# Context variables for request tracking
request_context: ContextVar[dict[str, Any]] = ContextVar("request_context", default={})


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging output.

    Formats log records as JSON with consistent structure including
    timestamp, level, message, and context information.
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON.

        Args:
            record: Log record to format

        Returns:
            str: JSON formatted log message
        """
        # Base log data
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add request context if available
        context = request_context.get({})
        if context:
            log_data["context"] = context

        # Add extra fields from record
        if hasattr(record, "extra_data"):
            log_data.update(record.extra_data)

        # Add structured data if available
        if hasattr(record, "structured_data"):
            try:
                structured = (
                    json.loads(record.structured_data)
                    if isinstance(record.structured_data, str)
                    else record.structured_data
                )
                log_data["structured"] = structured
            except (json.JSONDecodeError, TypeError):
                log_data["structured_raw"] = str(record.structured_data)

        # Add exception information if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": (
                    self.formatException(record.exc_info) if record.exc_info else None
                ),
            }

        return json.dumps(log_data, default=str, ensure_ascii=False)


class StructuredLogger:
    """Structured logger with configurable levels and output formats.

    Provides consistent structured logging across the application with
    support for both console and file output, JSON formatting, and
    context management.
    """

    def __init__(self, name: str, config: Optional[dict[str, Any]] = None):
        """Initialize structured logger.

        Args:
            name: Logger name
            config: Optional configuration override
        """
        self.name = name
        self.logger = logging.getLogger(name)
        self.config = config or get_config().logging
        self._setup_logger()

    def _setup_logger(self):
        """Set up logger with appropriate handlers and formatters."""
        # Clear existing handlers to avoid duplicates
        self.logger.handlers.clear()

        # Set log level
        level = getattr(logging, self.config.level.upper(), logging.INFO)
        self.logger.setLevel(level)

        # Console handler with JSON formatting
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(JSONFormatter())
        console_handler.setLevel(level)
        self.logger.addHandler(console_handler)

        # File handler if configured
        if self.config.file_path:
            file_handler = RotatingFileHandler(
                self.config.file_path,
                maxBytes=self.config.max_file_size,
                backupCount=self.config.backup_count,
            )
            file_handler.setFormatter(JSONFormatter())
            file_handler.setLevel(level)
            self.logger.addHandler(file_handler)

        # Prevent propagation to root logger
        self.logger.propagate = False

    def _log_with_context(
        self,
        level: int,
        message: str,
        extra_data: Optional[dict[str, Any]] = None,
        exc_info: Optional[bool] = None,
    ):
        """Log message with context and extra data.

        Args:
            level: Log level
            message: Log message
            extra_data: Additional data to include
            exc_info: Include exception information
        """
        extra = {}
        if extra_data:
            extra["extra_data"] = extra_data

        self.logger.log(level, message, extra=extra, exc_info=exc_info)

    def debug(self, message: str, extra_data: Optional[dict[str, Any]] = None):
        """Log debug message."""
        self._log_with_context(logging.DEBUG, message, extra_data)

    def info(self, message: str, extra_data: Optional[dict[str, Any]] = None):
        """Log info message."""
        self._log_with_context(logging.INFO, message, extra_data)

    def warning(self, message: str, extra_data: Optional[dict[str, Any]] = None):
        """Log warning message."""
        self._log_with_context(logging.WARNING, message, extra_data)

    def error(
        self,
        message: str,
        extra_data: Optional[dict[str, Any]] = None,
        exc_info: bool = False,
    ):
        """Log error message."""
        self._log_with_context(logging.ERROR, message, extra_data, exc_info)

    def critical(
        self,
        message: str,
        extra_data: Optional[dict[str, Any]] = None,
        exc_info: bool = False,
    ):
        """Log critical message."""
        self._log_with_context(logging.CRITICAL, message, extra_data, exc_info)

    def exception(self, message: str, extra_data: Optional[dict[str, Any]] = None):
        """Log exception with traceback."""
        self._log_with_context(logging.ERROR, message, extra_data, exc_info=True)

    def log_request_start(
        self,
        method: str,
        path: str,
        request_id: str,
        user_id: Optional[str] = None,
        user_agent: Optional[str] = None,
        remote_addr: Optional[str] = None,
    ):
        """Log request start with context."""
        extra_data = {
            "request_id": request_id,
            "method": method,
            "path": path,
            "user_id": user_id,
            "user_agent": user_agent,
            "remote_addr": remote_addr,
            "event_type": "request_start",
        }
        self.info(f"Request started: {method} {path}", extra_data)

    def log_request_end(
        self,
        method: str,
        path: str,
        request_id: str,
        status_code: int,
        duration_ms: float,
        user_id: Optional[str] = None,
        response_size: Optional[int] = None,
    ):
        """Log request completion with metrics."""
        extra_data = {
            "request_id": request_id,
            "method": method,
            "path": path,
            "status_code": status_code,
            "duration_ms": duration_ms,
            "user_id": user_id,
            "response_size": response_size,
            "event_type": "request_end",
        }

        # Use different log levels based on status code
        if status_code >= 500:
            self.error(f"Request failed: {method} {path} - {status_code}", extra_data)
        elif status_code >= 400:
            self.warning(f"Request error: {method} {path} - {status_code}", extra_data)
        else:
            self.info(f"Request completed: {method} {path} - {status_code}", extra_data)

    def log_database_operation(
        self,
        operation: str,
        table: str,
        duration_ms: float,
        success: bool = True,
        error: Optional[str] = None,
        affected_rows: Optional[int] = None,
    ):
        """Log database operation with metrics."""
        extra_data = {
            "operation": operation,
            "table": table,
            "duration_ms": duration_ms,
            "success": success,
            "affected_rows": affected_rows,
            "event_type": "database_operation",
        }

        if success:
            self.info(f"Database operation: {operation} on {table}", extra_data)
        else:
            extra_data["error"] = error
            self.error(f"Database operation failed: {operation} on {table}", extra_data)

    def log_business_event(
        self,
        event_name: str,
        entity_type: str,
        entity_id: str,
        details: Optional[dict[str, Any]] = None,
    ):
        """Log business domain events."""
        extra_data = {
            "event_name": event_name,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "event_type": "business_event",
        }

        if details:
            extra_data["details"] = details

        self.info(
            f"Business event: {event_name} for {entity_type}:{entity_id}", extra_data
        )


# Global logger instances
_loggers: dict[str, StructuredLogger] = {}


def get_logger(name: str) -> StructuredLogger:
    """Get or create a structured logger instance.

    Args:
        name: Logger name

    Returns:
        StructuredLogger: Logger instance
    """
    if name not in _loggers:
        _loggers[name] = StructuredLogger(name)
    return _loggers[name]


def set_request_context(context: dict[str, Any]):
    """Set request context for logging.

    Args:
        context: Context data to set
    """
    request_context.set(context)


def get_request_context() -> dict[str, Any]:
    """Get current request context.

    Returns:
        Dict[str, Any]: Current context data
    """
    return request_context.get({})


def clear_request_context():
    """Clear request context."""
    request_context.set({})
