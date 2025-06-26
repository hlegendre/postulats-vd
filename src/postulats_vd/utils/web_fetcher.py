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


class WebFetcher:
    """
    Classe utilitaire pour récupérer du contenu web.
    Implémentation du pattern singleton avec limitation de débit.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(WebFetcher, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """
        Initialise le fetcher web avec une session et des headers.
        Initialisation unique due au pattern singleton.
        """
        if self._initialized:
            return

        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})
        self.logger = LoggingUtils.setup_simple_logger("WebFetcher")
        self._last_request_time = 0  # Timestamp of the last request
        self._initialized = True

    def _apply_rate_limit(self):
        """
        Applique la limitation de débit en attendant si nécessaire avant de faire une requête.
        """
        if PAGE_DELAY <= 0:
            return

        time_since_last_request = time.time() - self._last_request_time

        if time_since_last_request < PAGE_DELAY:
            wait_time = PAGE_DELAY - time_since_last_request
            self.logger.debug(f"Attente de {wait_time:.2f} seconde(s) pour respecter le délai entre requêtes")
            time.sleep(wait_time)

        self._last_request_time = time.time()

    def html_string(self, url: str) -> Optional[str]:
        """
        Récupère le contenu HTML d'une URL et le retourne sous forme de chaîne de caractères.

        Args:
            url (str): URL à récupérer

        Returns:
            str: Contenu HTML, ou None en cas d'échec
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

    def html_soup(self, url: str) -> Optional[BeautifulSoup]:
        """
        Récupère le contenu HTML d'une URL et le retourne sous forme d'objet BeautifulSoup.

        Args:
            url (str): URL à récupérer

        Returns:
            BeautifulSoup: Contenu HTML parsé, ou None en cas d'échec
        """
        html_content = self.html_string(url)
        if html_content:
            return BeautifulSoup(html_content, "html.parser")
        return None

    def download_file(self, url: str, filepath: str) -> bool:
        """
        Télécharge un fichier depuis une URL et le sauvegarde dans un fichier.
        """
        self._apply_rate_limit()

        try:
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            with open(filepath, "wb") as f:
                f.write(response.content)
        except requests.RequestException as e:
            self.logger.error(f"Erreur lors du téléchargement de {url} : {e}")
            return False

        return True
