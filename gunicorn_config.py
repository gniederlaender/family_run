"""Gunicorn configuration for Family Run Tracker."""

import logging
import sys
import io

# Server socket
bind = "0.0.0.0:5002"

# Worker processes
workers = 2
worker_class = "sync"
timeout = 300
graceful_timeout = 30
keepalive = 5

# Logging
loglevel = "error"
accesslog = "-"
errorlog = "-"

# Custom error log filter to suppress benign shutdown errors
class ShutdownErrorFilter(logging.Filter):
    """Filter out benign 'Error handling request (no URI read)' messages during shutdown.

    This error occurs when gunicorn workers are interrupted during request handling,
    typically during graceful shutdown. It's not a real error and can be safely suppressed.
    """

    # Class-level state to track if we're in a shutdown traceback
    # Note: This works within a single worker process
    _in_traceback = False

    def filter(self, record):
        message = record.getMessage()

        # First check if we're already in a traceback (from previous log records)
        if ShutdownErrorFilter._in_traceback:
            # Check for end of traceback patterns
            if "sys.exit" in message.lower() or "SystemExit" in message:
                ShutdownErrorFilter._in_traceback = False
                return False
            # Suppress this line (it's part of the traceback)
            return False

        # Suppress "Error handling request (no URI read)" - this is a benign shutdown error
        # This error ONLY occurs during shutdown when a worker is interrupted mid-request
        if "Error handling request" in message and "no URI read" in message:
            ShutdownErrorFilter._in_traceback = True
            return False

        # Suppress standalone SystemExit messages
        if "SystemExit: 0" in message or "SystemExit: 1" in message:
            return False

        # Suppress SystemExit exceptions in exception info
        if record.exc_info:
            exc_type, exc_value, exc_tb = record.exc_info
            if exc_type is SystemExit:
                return False

        return True

def _add_filters_to_logger(logger):
    """Add shutdown error filter to a logger and all its handlers."""
    logger.addFilter(ShutdownErrorFilter())
    for handler in logger.handlers:
        handler.addFilter(ShutdownErrorFilter())

def when_ready(server):
    """Configure logging when server is ready."""
    # Add filter to suppress benign shutdown errors in multiple places
    for logger_name in ["gunicorn.error", "gunicorn", ""]:  # "" is root logger
        logger = logging.getLogger(logger_name)
        _add_filters_to_logger(logger)

def post_worker_init(worker):
    """Configure worker after initialization."""
    # Add filter to suppress benign shutdown errors in multiple places
    for logger_name in ["gunicorn.error", "gunicorn", ""]:  # "" is root logger
        logger = logging.getLogger(logger_name)
        _add_filters_to_logger(logger)

def pre_fork(server, worker):
    """Configure logging before forking worker."""
    # Add filter before worker fork to ensure it's active from the start
    for logger_name in ["gunicorn.error", "gunicorn", ""]:  # "" is root logger
        logger = logging.getLogger(logger_name)
        _add_filters_to_logger(logger)

def on_starting(server):
    """Configure logging when gunicorn starts (before workers)."""
    # Add filter at the very beginning
    for logger_name in ["gunicorn.error", "gunicorn", ""]:  # "" is root logger
        logger = logging.getLogger(logger_name)
        _add_filters_to_logger(logger)
