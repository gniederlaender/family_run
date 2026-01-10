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

# Global state for tracking shutdown tracebacks across filter instances
_in_shutdown_traceback = False
_shutdown_in_progress = False

# Custom error log filter to suppress benign shutdown errors
class ShutdownErrorFilter(logging.Filter):
    """Filter out benign 'Error handling request (no URI read)' messages during shutdown."""

    def filter(self, record):
        global _in_shutdown_traceback, _shutdown_in_progress

        # Get the message
        message = record.getMessage()

        # Detect when shutdown is in progress
        if "Handling signal: int" in message or "Handling signal: term" in message:
            _shutdown_in_progress = True

        # Suppress "Error handling request (no URI read)" errors
        # These occur during graceful shutdowns and are not actual errors
        # Check if this is the specific error we want to suppress
        if "Error handling request" in message and "no URI read" in message:
            _in_shutdown_traceback = True
            return False

        # Detect the start of a traceback during shutdown - this appears before the error message
        if _shutdown_in_progress and "Traceback (most recent call last)" in message:
            _in_shutdown_traceback = True
            return False

        # If we're in a shutdown traceback, suppress all lines until we hit the end
        if _in_shutdown_traceback:
            # Check if this is the end of the traceback (SystemExit or Worker exiting)
            if "SystemExit:" in message or "Worker exiting" in message:
                _in_shutdown_traceback = False
                return False
            # Suppress all traceback lines - including those with various patterns
            # Check if the line (after removing potential timestamp prefix) is part of the traceback
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

        # Reset shutdown flag when workers are done exiting
        if _shutdown_in_progress and "Shutting down: Master" in message:
            _shutdown_in_progress = False

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
