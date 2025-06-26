#!/usr/bin/env python3
"""
Utilitaires pour les URLs.
"""

from urllib.parse import urlparse


def extract_base_url(url: str) -> str:
    """
    Extrait l'URL de base depuis une URL complète.

    Args:
        url (str): URL complète à analyser (ex: https://www.vd.ch/actualites/decisions-du-conseil-detat)

    Returns:
        str: URL de base (ex: https://www.vd.ch)
    """
    parsed_url = urlparse(url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}"
