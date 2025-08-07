#!/usr/bin/env python3

import logging

from rich.console import Console
from rich.logging import RichHandler
from rich.text import Text

# --- Configuration ---
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
LOG_LEVEL = logging.INFO  # Change to logging.DEBUG for more verbose output

# --- Logging Setup ---
file_handler = logging.FileHandler("terraforge.log")
file_handler.setFormatter(logging.Formatter(LOG_FORMAT))

handlers = [RichHandler(), file_handler]

logging.basicConfig(level=LOG_LEVEL, handlers=handlers)

logger = logging.getLogger(__name__)  # Use __name__ for logger identification

# --- Console Setup ---
console = Console()


def setLoggingLevel(level: int):
    """Set the logging level."""
    logger.setLevel(level)
    for handler in logger.handlers:
        handler.setLevel(level)
    logger.info(f"Logging level set to {logging.getLevelName(level)}")


def green(message: str):
    """Returns a message styled in green color."""
    return Text(message, style="green")


def yellow(message: str):
    """Returns a message styled in yellow color."""
    return Text(message, style="yellow")


def red(message: str):
    """Returns a message styled in red color."""
    return Text(message, style="red")


def greenBack(message: str):
    """Returns a message with green background."""
    return Text(message, style="on green")
