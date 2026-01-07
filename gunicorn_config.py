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

# Custom error log filter to suppress benign shutdown errors
class ShutdownErrorFilter(logging.Filter):
    """Filter out benign 'Error handling request (no URI read)' messages during shutdown."""

    def __init__(self):
        super().__init__()
        self._suppressing_traceback = False
        self._last_error_was_no_uri = False

    def filter(self, record):
        # Suppress "Error handling request (no URI read)" errors
        # These occur during graceful shutdowns and are not actual errors
        message = record.getMessage()

        # Check if this is the specific error we want to suppress
        if "Error handling request" in message and "no URI read" in message:
            self._suppressing_traceback = True
            self._last_error_was_no_uri = True
            return False

        # If we just saw the "no URI read" error, suppress the traceback that follows
        if self._last_error_was_no_uri and "Traceback (most recent call last):" in message:
            # Continue suppressing
            return False

        # Continue suppressing traceback lines after the error
        if self._suppressing_traceback:
            # Check if this line is part of a traceback or SystemExit
            # Traceback lines typically contain "File", "line", or are indented
            is_traceback_line = (
                message.strip().startswith("File ") or
                "SystemExit:" in message or
                (message.startswith("  ") and len(message.strip()) > 0)
            )

            # Stop suppressing after Worker exiting message
            if "Worker exiting" in message:
                self._suppressing_traceback = False
                self._last_error_was_no_uri = False

            # If it's a traceback line or SystemExit, suppress it
            if is_traceback_line:
                return False

            # If we've moved past the traceback, stop suppressing
            if not is_traceback_line and "SystemExit:" not in message:
                self._suppressing_traceback = False
                self._last_error_was_no_uri = False

        # Suppress SystemExit messages that occur during normal shutdown
        if "SystemExit: 0" in message or "SystemExit: 1" in message:
            return False

        # Check exception info for SystemExit exceptions
        if record.exc_info:
            exc_type, exc_value, exc_tb = record.exc_info
            if exc_type is SystemExit:
                return False

        return True

def when_ready(server):
    """Configure logging when server is ready."""
    # Add filter to suppress benign shutdown errors
    error_logger = logging.getLogger("gunicorn.error")
    for handler in error_logger.handlers:
        handler.addFilter(ShutdownErrorFilter())

def post_worker_init(worker):
    """Configure worker after initialization."""
    # Add filter to suppress benign shutdown errors
    error_logger = logging.getLogger("gunicorn.error")
    for handler in error_logger.handlers:
        handler.addFilter(ShutdownErrorFilter())
