"""Logging configuration for EduDocAI application.

This module sets up structured logging with appropriate formatters and handlers.
"""

import logging
import sys
from pathlib import Path
from typing import Optional

from src.config.settings import settings


def setup_logging(
    name: str = "edudicai",
    level: Optional[int] = None,
    log_file: Optional[str] = None
) -> logging.Logger:
    """Configure and return a logger instance.

    Args:
        name: Logger name (default: "edudicai")
        level: Logging level (default: DEBUG if settings.debug else INFO)
        log_file: Optional path to log file

    Returns:
        logging.Logger: Configured logger instance

    Example:
        >>> logger = setup_logging("my_module")
        >>> logger.info("Application started")
    """
    # Determine logging level
    if level is None:
        level = logging.DEBUG if settings.debug else logging.INFO

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Prevent propagation to root logger
    logger.propagate = False

    return logger


def get_logger(name: str) -> logging.Logger:
    """Get or create a logger instance with default configuration.

    Args:
        name: Logger name (typically __name__ of the module)

    Returns:
        logging.Logger: Logger instance

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.debug("Processing document...")
    """
    logger = logging.getLogger(name)

    # Only setup if logger has no handlers
    if not logger.handlers:
        return setup_logging(name)

    return logger


# Default application logger
default_logger = setup_logging()
