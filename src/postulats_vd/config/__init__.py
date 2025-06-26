"""
Configuration module for the Postulats VD package.

This module contains all configuration settings and constants used throughout the package.
"""

from .settings import (
    FILE_PATTERNS,
    MAX_LISTING_PAGES,
    OUTPUT_FOLDER,
    PAGE_DELAY,
    REQUEST_TIMEOUT,
    STOP_DATE,
    STORAGE_FILENAME,
    USER_AGENT,
)

__all__ = [
    "OUTPUT_FOLDER",
    "STORAGE_FILENAME",
    "MAX_LISTING_PAGES",
    "STOP_DATE",
    "REQUEST_TIMEOUT",
    "USER_AGENT",
    "PAGE_DELAY",
    "FILE_PATTERNS",
]
