"""Gunicorn configuration for Family Run Tracker."""

import logging
import sys

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

# Global state for tracking shutdown tracebacks across filter instances
_in_shutdown_traceback = False

# Custom error log filter to suppress benign shutdown errors
class ShutdownErrorFilter(logging.Filter):
    """Filter out benign 'Error handling request (no URI read)' messages during shutdown."""

    def filter(self, record):
        global _in_shutdown_traceback

        # Suppress "Error handling request (no URI read)" errors
        # These occur during graceful shutdowns and are not actual errors
        message = record.getMessage()

        # Check if this is the specific error we want to suppress
        if "Error handling request" in message and "no URI read" in message:
            _in_shutdown_traceback = True
            return False

        # If we're in a shutdown traceback, suppress all lines until we hit the end
        if _in_shutdown_traceback:
            # Check if this is the end of the traceback (SystemExit or Worker exiting)
            if "SystemExit:" in message or "Worker exiting" in message:
                _in_shutdown_traceback = False
                return False
            # Suppress all traceback lines
            if any(pattern in message for pattern in [
                "Traceback (most recent call last)",
                "File \"/opt/family_run/venv/lib/python3.12/site-packages/gunicorn/",
                "    ",  # Indented traceback lines (code lines and file paths)
                "^^^^^",  # Python 3.12 error markers
            ]):
                return False

        # Suppress SystemExit messages that occur during normal shutdown
        if "SystemExit: 0" in message or "SystemExit: 1" in message:
            return False

        # Check exception info for SystemExit exceptions during shutdown
        if record.exc_info:
            exc_type, exc_value, exc_tb = record.exc_info
            if exc_type is SystemExit:
                return False
            # Also check if the exception chain contains SystemExit
            if exc_value and hasattr(exc_value, '__cause__'):
                cause = exc_value.__cause__
                if isinstance(cause, SystemExit):
                    return False

        return True

def when_ready(server):
    """Configure logging when server is ready."""
    # Add filter to suppress benign shutdown errors in multiple places
    for logger_name in ["gunicorn.error", "gunicorn"]:
        logger = logging.getLogger(logger_name)
        logger.addFilter(ShutdownErrorFilter())
        for handler in logger.handlers:
            handler.addFilter(ShutdownErrorFilter())

def post_worker_init(worker):
    """Configure worker after initialization."""
    # Add filter to suppress benign shutdown errors in multiple places
    for logger_name in ["gunicorn.error", "gunicorn"]:
        logger = logging.getLogger(logger_name)
        logger.addFilter(ShutdownErrorFilter())
        for handler in logger.handlers:
            handler.addFilter(ShutdownErrorFilter())

def pre_fork(server, worker):
    """Configure logging before forking worker."""
    # Add filter before worker fork to ensure it's active from the start
    for logger_name in ["gunicorn.error", "gunicorn"]:
        logger = logging.getLogger(logger_name)
        logger.addFilter(ShutdownErrorFilter())
        for handler in logger.handlers:
            handler.addFilter(ShutdownErrorFilter())
