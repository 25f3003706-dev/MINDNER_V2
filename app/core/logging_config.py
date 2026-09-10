"""Centralized logging configuration for Mindner Backend."""

import logging
import sys


def setup_logging(level: str = "INFO") -> logging.Logger:
    """Configures structured console logging for the application."""
    log_level = getattr(logging, level.upper(), logging.INFO)

    log_format = "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # Reset root handlers
    logging.root.handlers = []
    
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(fmt=log_format, datefmt=date_format))
    
    root_logger = logging.getLogger("mindner")
    root_logger.setLevel(log_level)
    root_logger.addHandler(handler)
    root_logger.propagate = False

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """Get a named logger that inherits standard configuration."""
    return logging.getLogger(f"mindner.{name}")
