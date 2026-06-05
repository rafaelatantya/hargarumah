"""Structured logging setup using Rich for beautiful console output."""

from __future__ import annotations

import logging
import sys

from rich.console import Console
from rich.logging import RichHandler

from src.config.settings import settings


def setup_logging(level: str | None = None) -> None:
    """Configure structured logging with Rich handler.

    Args:
        level: Log level string (DEBUG, INFO, WARNING, ERROR).
               Defaults to settings.log_level.
    """
    log_level = level or settings.log_level

    console = Console(stderr=True)

    handler = RichHandler(
        console=console,
        show_time=True,
        show_path=True,
        markup=True,
        rich_tracebacks=True,
        tracebacks_show_locals=True,
    )

    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format="%(message)s",
        datefmt="[%X]",
        handlers=[handler],
        force=True,
    )

    # Suppress noisy third-party loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("nodriver").setLevel(logging.WARNING)

    logging.getLogger(__name__).info(
        "Logging initialized (level=%s)", log_level.upper()
    )


def get_logger(name: str) -> logging.Logger:
    """Get a named logger instance.

    Args:
        name: Logger name (typically __name__ of the calling module).

    Returns:
        Configured logging.Logger instance.
    """
    return logging.getLogger(name)
