"""Centralized logging configuration with exception handling."""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Any, Type


def setup_logging(
    log_file: str = "memap.log",
    max_bytes: int = 10_000_000,
    backup_count: int = 5,
) -> None:
    """Configure centralized logging with file rotation.

    Args:
        log_file: Path to log file
        max_bytes: Max size before rotation (10MB default)
        backup_count: Number of backup files to keep

    Raises:
        ValueError: If max_bytes or backup_count are <= 0

    Example:
        >>> setup_logging()  # Uses defaults
        >>> setup_logging("custom.log", max_bytes=5_000_000)
    """
    # Validation
    if max_bytes < 1:
        raise ValueError("max_bytes must be >= 1")
    if backup_count < 1:
        raise ValueError("backup_count must be >= 1")

    # Convert string to Path (more robust)
    log_path = Path(log_file)

    # Create handler
    handler = logging.handlers.RotatingFileHandler(
        log_path,
        maxBytes=max_bytes,
        backupCount=backup_count,
    )

    # Format: date - module - level - message
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        handlers=[handler],
        force=True,  # Override existing config
    )


def setup_exception_hook() -> None:
    """Capture uncaught exceptions and log them.

    This ensures that even if the app crashes,
    the error is logged to file before exit.
    """

    def log_uncaught(
        exc_type: Type[BaseException],
        exc_value: BaseException,
        traceback: Any,
    ) -> None:
        """Log exception details before exit."""
        logging.critical(
            "Uncaught exception",
            exc_info=(exc_type, exc_value, traceback),
        )

    # Install the global hook
    sys.excepthook = log_uncaught
