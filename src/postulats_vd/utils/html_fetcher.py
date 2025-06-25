#!/usr/bin/env python3
"""
HTML Fetcher Utility

This module provides utility functions for fetching HTML content from web pages.
"""

import time
import requests
from bs4 import BeautifulSoup
from typing import Optional

from ..config import REQUEST_TIMEOUT, USER_AGENT, PAGE_DELAY
from .logging import LoggingUtils


class HtmlFetcher:
    """
    Utility class for fetching HTML content from web pages.
    Singleton pattern implementation with rate limiting.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(HtmlFetcher, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """
        Initialize the HTML fetcher with a session and headers.
        Only initializes once due to singleton pattern.
        """
        if self._initialized:
            return

        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})
        self.logger = LoggingUtils.setup_simple_logger("HtmlFetcher")
        self._last_request_time = 0  # Timestamp of the last request
        self._initialized = True

    def _apply_rate_limit(self):
        """
        Apply rate limiting by waiting if necessary before making a request.
        """
        if PAGE_DELAY <= 0:
            return

        time_since_last_request = time.time() - self._last_request_time

        if time_since_last_request < PAGE_DELAY:
            wait_time = PAGE_DELAY - time_since_last_request
            self.logger.debug(f"Attente de {wait_time:.2f} seconde(s) pour respecter le délai entre requêtes")
            time.sleep(wait_time)

        self._last_request_time = time.time()

    def string(self, url: str) -> Optional[str]:
        """
        Fetch HTML content as a string from a given URL.

        Args:
            url (str): URL to fetch

        Returns:
            str: HTML content as string, or None if failed
        """
        # Apply rate limiting before making the request
        self._apply_rate_limit()

        try:
            self.logger.debug(f"Récupération de la page : {url}")
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            self.logger.debug("Page récupérée avec succès")

            # Update the last request timestamp

            return response.text
        except requests.RequestException as e:
            self.logger.error(f"Erreur lors de la récupération de {url} : {e}")
            return None

    def soup(self, url: str) -> Optional[BeautifulSoup]:
        """
        Fetch HTML content and return it as a BeautifulSoup object.

        Args:
            url (str): URL to fetch

        Returns:
            BeautifulSoup: Parsed HTML content, or None if failed
        """
        html_content = self.string(url)
        if html_content:
            return BeautifulSoup(html_content, "html.parser")
        return None
