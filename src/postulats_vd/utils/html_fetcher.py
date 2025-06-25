#!/usr/bin/env python3
"""
HTML Fetcher Utility

This module provides utility functions for fetching HTML content from web pages.
"""

import requests
from bs4 import BeautifulSoup
from typing import Optional

from ..config import REQUEST_TIMEOUT, USER_AGENT
from .logging import LoggingUtils


class HtmlFetcher:
    """
    Utility class for fetching HTML content from web pages.
    """

    def __init__(self):
        """
        Initialize the HTML fetcher with a session and headers.
        """
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})
        self.logger = LoggingUtils.setup_simple_logger("HtmlFetcher")

    def fetch_html_string(self, url: str) -> Optional[str]:
        """
        Fetch HTML content as a string from a given URL.

        Args:
            url (str): URL to fetch

        Returns:
            str: HTML content as string, or None if failed
        """
        try:
            self.logger.debug(f"Récupération de la page : {url}")
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            self.logger.debug("Page récupérée avec succès")
            return response.text
        except requests.RequestException as e:
            self.logger.error(f"Erreur lors de la récupération de {url} : {e}")
            return None

    def fetch_html_soup(self, url: str) -> Optional[BeautifulSoup]:
        """
        Fetch HTML content and return it as a BeautifulSoup object.

        Args:
            url (str): URL to fetch

        Returns:
            BeautifulSoup: Parsed HTML content, or None if failed
        """
        html_content = self.fetch_html_string(url)
        if html_content:
            return BeautifulSoup(html_content, "html.parser")
        return None
