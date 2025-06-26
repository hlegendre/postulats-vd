#!/usr/bin/env python3
"""
Téléchargeur de Séances du Conseil d'État VD

Ce script permet d'extraire automatiquement les informations des séances du Conseil d'État
du canton de Vaud depuis le site officiel.

Auteur: Hugues Le Gendre
Date: 2024
"""

import re
from datetime import datetime
from typing import TypedDict, cast
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

from ..config import (
    MAX_LISTING_PAGES,
    STOP_DATE,
)
from ..utils.date_parser import DateParser
from ..utils.logging import LoggingUtils
from ..utils.url import extract_base_url
from ..utils.web_fetcher import WebFetcher
from .storage import Seance, Storage

SessionListerResult = TypedDict(
    "SessionListerResult",
    {"success": bool, "pages_processed": int, "new_seances_count": int, "stored_seances": int, "stop_reached": bool},
)


class SessionLister:
    def __init__(self, storage: Storage):
        """
        Initialise le listeur de séances du Conseil d'État.

        Args:
            storage (Storage): Stockage des données
        """

        self.logger = LoggingUtils.setup_simple_logger("ExtracteurSéances")
        self.storage = storage

        self.logger.info(f"Découvreur de séances initialisé avec la base de données : {self.storage.get_file_path()}")
        self.logger.info(f"Séances existantes chargées : {self.storage.seances_count()}")

    def _extract_seances(self, html_content: str, base_url: str, current_date: str) -> tuple[int, int, bool]:
        """
        Extrait les séances de la page, sans détails.
        La base de donnée est mise à jour à la volée.

        Args:
            html_content (str): Contenu HTML à analyser
            base_url (str): URL de base pour construire les URLs complètes
            current_date (str): Date de découverte pour les séances

        Returns:
            int: Nombre de nouvelles séances trouvées
            int: Nombre de séances déjà existantes
            bool: True s'il faut continuer à extraire les séances de la page suivante
        """
        nb_nouvelles_seances = 0
        nb_seances_existantes = 0

        soup = BeautifulSoup(html_content, "html.parser")

        # Pattern pour détecter les liens de séances : "Séance du Conseil d'Etat du [date]"
        seance_pattern = re.compile(r"Séance du Conseil d\'Etat du (\d{1,2}\s+\w+\s+\d{4})", re.IGNORECASE)

        for link in soup.find_all("a", href=True):
            link_text = link.get_text(strip=True)
            href = str(link.get("href")) if isinstance(link, Tag) else None

            if href and link_text:
                match = seance_pattern.search(link_text)
                if match:
                    date_str = match.group(1)
                    full_url = urljoin(base_url, href)

                    try:
                        date_str = DateParser.parse_french_date(date_str).strftime("%Y-%m-%d")
                    except Exception as e:
                        self.logger.error(f"Impossible de parser la date '{date_str}': {e}")
                        continue

                    if date_str < STOP_DATE:
                        self.logger.info(f"Date limite atteinte ({STOP_DATE}).")
                        return nb_nouvelles_seances, nb_seances_existantes, False

                    if self.storage.seance_exists(date_str):
                        self.logger.debug(f"Séance déjà existante : {date_str} -> {full_url}")
                        nb_seances_existantes += 1
                        continue

                    seance: Seance = {
                        "url": full_url,
                        "date": date_str,
                        "date_originale": date_str,
                        "date_decouverte": current_date,
                        "titre": link_text,
                        "discussions": [],
                    }

                    self.storage.seance_upsert(seance)
                    self.logger.debug(f"Séance trouvée et ajoutée au stockage : {date_str} -> {full_url}")
                    nb_nouvelles_seances += 1

        return nb_nouvelles_seances, nb_seances_existantes, True

    def _extract_next_page(self, html_content: str, base_url: str) -> str | None:
        """
        Extrait le lien de la page suivante.

        Args:
            html_content (str): Contenu HTML à analyser
            base_url (str): URL de base pour construire les URLs complètes

        Returns:
            str | None: URL de la page suivante ou None si aucune page suivante n'est trouvée
        """
        soup = BeautifulSoup(html_content, "html.parser")

        # Chercher la pagination
        pagination_nav = soup.find("nav", {"aria-label": "Pagination"})
        if not pagination_nav:
            self.logger.debug("Aucune pagination trouvée")
            return None

        # Chercher les liens "Page suivante" avec la classe spécifique
        next_links = cast(Tag, pagination_nav).find_all("a", class_="vd-pagination__link")

        for link in next_links:
            # Vérifier si c'est un lien "Page suivante"
            link_text = link.get_text(strip=True).lower()
            if "suivante" in link_text or "next" in link_text:
                href = str(link.get("href")) if isinstance(link, Tag) else None
                if href:
                    full_url = urljoin(base_url, href)
                    self.logger.debug(f"Lien de pagination trouvé : {full_url}")
                    return full_url

        return None

    def list(self) -> SessionListerResult:
        """
        Méthode principale pour extraire les séances du Conseil d'État avec pagination, mais sans détails.

        Returns:
            SessionListerResult: Résumé de l'extraction
        """
        current_date = datetime.now().isoformat()
        self.logger.debug(f"Date de découverte pour cette session : {current_date}")

        first_url = "https://www.vd.ch/actualites/decisions-du-conseil-detat"
        self.logger.info(f"Début de l'extraction des séances depuis : {first_url}")

        # Détection automatique de l'URL de base depuis l'URL cible
        base_url = extract_base_url(first_url)

        new_seances_count = 0
        stop_reached = False
        current_url: str | None = first_url
        visited_urls: set[str] = set()  # Pour éviter les boucles infinies

        while current_url and len(visited_urls) < MAX_LISTING_PAGES and not stop_reached:
            # Vérifier si l'URL a déjà été visitée
            if current_url in visited_urls:
                self.logger.debug(f"URL déjà visitée, arrêt pour éviter la boucle infinie : {current_url}")
                break

            visited_urls.add(current_url)
            self.logger.debug(f"Traitement de la page {len(visited_urls)} : {current_url}")

            # Récupérer le contenu de la page
            html_content = WebFetcher().html_string(current_url)
            if not html_content:
                self.logger.error(f"Échec de la récupération du contenu de la page {current_url}")
                break

            # Extraire les liens des séances
            nb_nouv, nb_exist, cont = self._extract_seances(html_content, base_url, current_date)

            self.logger.info(
                f"Séances trouvées sur la page {len(visited_urls)} : {nb_nouv} nouvelle(s), {nb_exist} existante(s)"
            )
            new_seances_count += nb_nouv

            if not cont:
                break

            # Extraire les liens de pagination pour la page suivante
            current_url = self._extract_next_page(html_content, base_url)

        stored_seances = self.storage.seances_count()

        self.logger.info(f"Nombre de nouvelles séances trouvées sur {len(visited_urls)} pages : {new_seances_count}")
        self.logger.info(f"Nombre total de séances stockées : {stored_seances}")

        return {
            "success": True,
            "pages_processed": len(visited_urls),
            "new_seances_count": new_seances_count,
            "stored_seances": stored_seances,
            "stop_reached": stop_reached,
        }
