"""
Configuration module for the Postulats VD package.

This module contains all configuration settings and constants used throughout the package.
"""

from .settings import (
    OUTPUT_FOLDER,
    MAX_SESSIONS,
    STOP_DATE,
    REQUEST_TIMEOUT,
    USER_AGENT,
    PAGE_DELAY,
)

__all__ = [
    "OUTPUT_FOLDER",
    "MAX_SESSIONS",
    "STOP_DATE",
    "REQUEST_TIMEOUT",
    "USER_AGENT",
    "PAGE_DELAY",
]
