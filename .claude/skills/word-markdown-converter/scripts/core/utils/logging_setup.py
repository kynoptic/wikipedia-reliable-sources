#!/usr/bin/env python3
"""
Logging setup utilities for the word-to-markdown converter.

Provides standardized logging configuration for all scripts and modules.
"""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logging(name: str, level: str = "INFO", log_to_file: bool = True) -> logging.Logger:
    """
    Setup standardized logging configuration.

    Args:
        name: Logger name (typically script name)
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_to_file: Whether to log to file in logs/ directory

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # Clear existing handlers
    logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (if requested)
    if log_to_file:
        # Create logs directory if it doesn't exist
        logs_dir = Path(__file__).parent.parent.parent / "logs"
        logs_dir.mkdir(exist_ok=True)

        log_file = logs_dir / f"{name}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
