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

    def filter(self, record):
        # Suppress "Error handling request (no URI read)" errors
        # These occur during graceful shutdowns and are not actual errors
        message = record.getMessage()

        if "Error handling request" in message and "no URI read" in message:
            return False

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
