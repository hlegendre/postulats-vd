#!/usr/bin/env python3
"""
HTML Fetcher Utility

This module provides utility functions for fetching HTML content from web pages.
"""

from urllib.parse import urlparse


def extract_base_url(url: str) -> str:
    """
    Extrait l'URL de base depuis une URL complète.

    Args:
        url (str): URL complète à analyser

    Returns:
        str: URL de base (scheme + netloc)
    """
    parsed_url = urlparse(url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}"
