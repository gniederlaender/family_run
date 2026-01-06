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
        if "Error handling request" in record.getMessage() and "no URI read" in record.getMessage():
            return False
        # Suppress SystemExit messages that occur during normal shutdown
        if "SystemExit: 0" in record.getMessage() or "SystemExit: 1" in record.getMessage():
            return False
        return True

def post_worker_init(worker):
    """Configure worker after initialization."""
    # Add filter to suppress benign shutdown errors
    for handler in logging.getLogger("gunicorn.error").handlers:
        handler.addFilter(ShutdownErrorFilter())
