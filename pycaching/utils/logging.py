"""Logging configuration for the caching library."""

import logging
from typing import Optional


def setup_logging(
    level: str = "INFO",
    format_string: Optional[str] = None,
    logger_name: str = "pycaching",
) -> logging.Logger:
    """
    Set up logging for the caching library.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_string: Custom format string for log messages
        logger_name: Name of the logger

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(logger_name)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            format_string
            or "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    return logger
