#!/usr/bin/env python3
"""
Enhanced Structured Logging Configuration for AI Router
Provides JSON-formatted logs with trace ID support and secret filtering

Features:
- Structured JSON logging (JSONL format)
- Dual output (file JSON + console human-readable)
- Trace ID propagation for request correlation
- Context variable support
- Ready for ELK/Datadog/Prometheus integration

Usage:
    from logging_config_v2 import setup_structured_logging, set_trace_id

    logger = setup_structured_logging(models_dir)

    # At start of request/operation
    trace_id = set_trace_id()

    # Log with automatic trace ID
    logger.info("Processing request", extra={
        'request_id': request_id,
        'extra_fields': {'model': 'gpt-4', 'duration_ms': 1500}
    })
"""

import logging
import json
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import uuid
import contextvars

# Context variable for trace ID (thread-safe, async-safe)
trace_id_context = contextvars.ContextVar('trace_id', default=None)


class StructuredFormatter(logging.Formatter):
    """
    Convert logs to structured JSON format for machine parsing.

    Output fields:
    - timestamp: ISO 8601 timestamp
    - level: Log level (INFO, ERROR, etc.)
    - logger: Logger name
    - message: Log message
    - module: Source module name
    - function: Source function name
    - line: Source line number
    - trace_id: Request trace ID for correlation
    - request_id: Optional operation-level request ID
    - extra_fields: Additional context
    - exception: Stack trace if exception
    - exception_type: Exception class name
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON string"""

        # Build core log entry
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }

        # Add trace ID if present
        trace_id = trace_id_context.get()
        if trace_id:
            log_entry['trace_id'] = trace_id

        # Add request ID if provided via extra fields
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id

        # Add custom extra fields if provided
        if hasattr(record, 'extra_fields') and record.extra_fields:
            log_entry['extra_fields'] = record.extra_fields

        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
            log_entry['exception_type'] = record.exc_info[0].__name__
            log_entry['has_exception'] = True

        return json.dumps(log_entry, default=str)


class ConsoleFormatter(logging.Formatter):
    """
    Human-readable console formatter with color and trace ID.

    Format: TIMESTAMP [LEVEL] [TRACE_ID] LOGGER - MESSAGE
    """

    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m',       # Reset
    }

    def format(self, record: logging.LogRecord) -> str:
        """Format log record for console output"""

        # Get timestamp
        ct = self.formatTime(record, self.datefmt)

        # Get trace ID
        trace_id = trace_id_context.get()
        trace_str = f"[{trace_id[:12]}...]" if trace_id else "[no-trace]"

        # Get color for level
        color = self.COLORS.get(record.levelname, '')
        reset = self.COLORS['RESET']

        # Build format string
        log_line = (
            f"{ct} "
            f"{color}[{record.levelname:8}]{reset} "
            f"{trace_str:18} "
            f"{record.name} - "
            f"{record.getMessage()}"
        )

        # Add exception if present
        if record.exc_info:
            log_line += f"\n{self.formatException(record.exc_info)}"

        return log_line


class SecretFilter(logging.Filter):
    """
    Filter to mask sensitive data (API keys, passwords, tokens, PII) in logs.

    Patterns masked:
    - API keys (api_key=xxx, apikey: xxx)
    - Passwords (password=xxx, passwd: xxx)
    - Tokens (Bearer xxx, token=xxx)
    - OpenAI keys (sk-...)
    - AWS keys (AKIA...)
    - Email addresses
    - Phone numbers
    """

    # Patterns to detect secrets (case-insensitive where appropriate)
    SECRET_PATTERNS = {
        'api_key': (r'(?:api[_-]?key)["\']?\s*[:=]\s*["\']?([a-zA-Z0-9_\-]{20,})["\']?',
                    'API_KEY'),
        'password': (r'(?:password|passwd)["\']?\s*[:=]\s*["\']?([^\s"\';,]{6,})["\']?',
                     'PASSWORD'),
        'token': (r'(?:token|auth_token)["\']?\s*[:=]\s*["\']?([a-zA-Z0-9_\-\.]{20,})["\']?',
                  'TOKEN'),
        'bearer': (r'Bearer\s+([a-zA-Z0-9_\-\.]+)',
                   'BEARER_TOKEN'),
        'openai_key': (r'sk-[a-zA-Z0-9]{48}',
                       'OPENAI_KEY'),
        'aws_key': (r'AKIA[0-9A-Z]{16}',
                    'AWS_KEY'),
        'email': (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                  'EMAIL'),
        'phone': (r'\b(?:\d{3}[-.]?\d{3}[-.]?\d{4}|\+1\s?\d{10})\b',
                  'PHONE'),
        'json_api_key': (r'"api_key"\s*:\s*"([^"]{20,})"',
                         'JSON_API_KEY'),
        'url_password': (r'https?://[^:]+:([^@]+)@',
                         'URL_PASSWORD'),
    }

    def filter(self, record: logging.LogRecord) -> bool:
        """Filter log record to mask secrets"""

        # Process main message
        record.msg = self._mask_secrets(str(record.msg))

        # Process extra fields if present
        if hasattr(record, 'extra_fields') and record.extra_fields:
            record.extra_fields = self._mask_dict_secrets(record.extra_fields)

        return True

    def _mask_secrets(self, text: str) -> str:
        """Mask secrets in a text string"""
        if not text:
            return text

        masked = text
        for secret_type, (pattern, label) in self.SECRET_PATTERNS.items():
            try:
                import re
                masked = re.sub(
                    pattern,
                    f'***{label}_REDACTED***',
                    masked,
                    flags=re.IGNORECASE
                )
            except Exception:
                # Skip problematic patterns
                pass

        return masked

    def _mask_dict_secrets(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively mask secrets in dictionary"""
        if not isinstance(data, dict):
            return data

        masked = {}
        for key, value in data.items():
            # Check if key name suggests secret
            if any(secret in key.lower() for secret in ['key', 'password', 'token', 'secret', 'auth']):
                masked[key] = '***REDACTED***'
            elif isinstance(value, dict):
                masked[key] = self._mask_dict_secrets(value)
            elif isinstance(value, (list, tuple)):
                masked[key] = [self._mask_secrets(str(v)) if isinstance(v, str) else v for v in value]
            elif isinstance(value, str):
                masked[key] = self._mask_secrets(value)
            else:
                masked[key] = value

        return masked


def set_trace_id(trace_id: Optional[str] = None) -> str:
    """
    Set trace ID for current request context.

    Args:
        trace_id: Optional trace ID. If None, generates UUID4.

    Returns:
        The trace ID that was set.

    Example:
        >>> trace_id = set_trace_id()  # Auto-generate
        >>> logger.info("Processing request")  # trace_id included automatically
    """
    if trace_id is None:
        trace_id = f"req-{uuid.uuid4().hex[:12]}"

    trace_id_context.set(trace_id)
    return trace_id


def get_trace_id() -> Optional[str]:
    """Get current trace ID from context"""
    return trace_id_context.get()


def clear_trace_id():
    """Clear trace ID from context"""
    trace_id_context.set(None)


def setup_structured_logging(
    models_dir: Path,
    level: int = logging.INFO,
    console_output: bool = True,
    file_output: bool = True,
    json_file: bool = True
) -> logging.Logger:
    """
    Setup structured JSON logging for AI Router.

    Creates two log outputs:
    1. File: JSONL format (machine-parseable)
    2. Console: Human-readable with colors and trace IDs

    Args:
        models_dir: Base directory for logs
        level: Logging level (logging.INFO, logging.DEBUG, etc.)
        console_output: Enable console logging
        file_output: Enable file logging
        json_file: Use JSON format for files (vs plain text)

    Returns:
        Logger instance configured for AI Router

    Example:
        >>> from pathlib import Path
        >>> logger = setup_structured_logging(Path('/models'))
        >>> logger.info("Starting application")
        >>>
        >>> # With trace ID
        >>> trace_id = set_trace_id('session-123')
        >>> logger.info("Processing user request")  # trace_id included
    """

    # Create log directory
    log_dir = models_dir / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    # Generate log file name
    date_str = datetime.now().strftime('%Y%m%d')
    ext = '.jsonl' if json_file else '.log'
    log_file = log_dir / f"ai-router-{date_str}{ext}"

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove existing handlers to prevent duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Add file handler (JSON format)
    if file_output:
        file_handler = logging.FileHandler(
            str(log_file),
            encoding='utf-8'
        )
        file_handler.setLevel(level)

        if json_file:
            file_formatter = StructuredFormatter()
        else:
            file_formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )

        file_handler.setFormatter(file_formatter)
        file_handler.addFilter(SecretFilter())
        root_logger.addHandler(file_handler)

    # Add console handler (human-readable)
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_formatter = ConsoleFormatter(
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        console_handler.addFilter(SecretFilter())
        root_logger.addHandler(console_handler)

    # Return named logger for application use
    logger = logging.getLogger('ai-router')
    logger.setLevel(level)

    return logger


def create_trace_logger(trace_id: str) -> logging.LoggerAdapter:
    """
    Create a logger adapter that automatically includes trace ID.

    Args:
        trace_id: Trace ID for this operation

    Returns:
        LoggerAdapter that includes trace_id in all logs

    Example:
        >>> logger = create_trace_logger('session-123')
        >>> logger.info("Starting operation")  # trace_id auto-included
    """
    set_trace_id(trace_id)

    base_logger = logging.getLogger('ai-router')

    class TraceAdapter(logging.LoggerAdapter):
        def process(self, msg, kwargs):
            trace = get_trace_id()
            return f"[{trace}] {msg}", kwargs

    return TraceAdapter(base_logger, {'trace_id': trace_id})


# Convenience function for quick setup
def setup_basic_logging(level: int = logging.INFO) -> logging.Logger:
    """
    Quick setup with default configuration.

    Args:
        level: Logging level

    Returns:
        Configured logger

    Example:
        >>> logger = setup_basic_logging()
        >>> logger.info("Application started")
    """
    return setup_structured_logging(Path.cwd(), level=level)


if __name__ == "__main__":
    # Example usage
    import time

    logger = setup_basic_logging(logging.DEBUG)

    # Example: Start a session with trace ID
    trace_id = set_trace_id("session-demo")
    logger.info("Starting demo session")

    # Example: Log with extra fields
    logger.info("Processing model", extra={
        'extra_fields': {
            'model': 'qwen3-coder-30b',
            'duration_ms': 1500,
            'tokens': 250
        }
    })

    # Example: Test secret filtering
    logger.warning("Config loaded", extra={
        'extra_fields': {
            'api_key': 'sk-1234567890abcdefghijklmnopqrstuv',
            'user_email': 'user@example.com',
            'connection_string': 'postgresql://user:password@localhost/db'
        }
    })

    # Example: Error with context
    try:
        raise ValueError("Test error for demonstration")
    except ValueError as e:
        logger.error("An error occurred", exc_info=True, extra={
            'extra_fields': {
                'context': 'model_execution',
                'model_id': 'llama33-70b',
                'retry_attempt': 1
            }
        })

    logger.info("Demo complete")

    print("\n--- Check logs directory for output files ---")
    print(f"Log files created in: {Path.cwd() / 'logs'}")
