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
from pathlib import Path
from urllib.parse import urljoin

from typing import TypedDict
from bs4 import BeautifulSoup
import time
from ..config import (
    MAX_SESSIONS,
    OUTPUT_FOLDER,
    PAGE_DELAY,
    STOP_DATE,
)
from .storage import Storage, Seance
from ..utils.logging import LoggingUtils
from ..utils.html_fetcher import HtmlFetcher
from ..utils.date_parser import DateParser
from ..utils.url import extract_base_url


class CESessionFinderResult(TypedDict):
    success: bool
    pages_processed: int
    new_seances_count: int
    stored_seances: int
    stop_reached: bool


class CESessionFinder:
    def __init__(self, output_folder=OUTPUT_FOLDER):
        """
        Initialise le découvreur de séances du Conseil d'État.

        Args:
            output_folder (str): Dossier pour sauvegarder les données extraites
        """
        self.output_folder = Path(output_folder)

        self.logger = LoggingUtils.setup_simple_logger("ExtracteurSéances")
        self.storage = Storage(output_folder=output_folder)
        self.html_fetcher = HtmlFetcher()

        self.logger.info(f"Découvreur de séances initialisé avec le fichier de sortie : {self.storage.get_file_path()}")
        self.logger.info(f"Séances existantes chargées : {self.storage.get_seance_count()}")

    def ajoute_seances_de_la_page(self, html_content: str, base_url: str, current_date: str) -> tuple[int, int, bool]:
        """
        Ajoute les séances de la page au stockage.

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

        # Trouver tous les liens
        links = soup.find_all("a", href=True)

        for link in links:
            link_text = link.get_text(strip=True)
            href = link.get("href")

            if href and link_text:
                # Vérifier si le texte du lien correspond au pattern d'une séance
                match = seance_pattern.search(link_text)
                if match:
                    date_str = match.group(1)
                    full_url = urljoin(base_url, href)

                    # Parser la date
                    try:
                        # Convertir la date française en objet datetime
                        date_obj = DateParser.parse_french_date(date_str)
                        formatted_date = date_obj.strftime("%Y-%m-%d")
                    except Exception as e:
                        self.logger.error(f"Impossible de parser la date '{date_str}': {e}")
                        continue

                    seance: Seance = {
                        "url": full_url,
                        "date": formatted_date,
                        "date_originale": date_str,
                        "date_decouverte": current_date,
                        "titre": link_text,
                        "parties": [],
                    }

                    # Si la date est antérieure à la date limite, on arrête le scraping
                    if formatted_date < STOP_DATE:
                        self.logger.info(f"Date limite atteinte ({STOP_DATE}).")
                        return nb_nouvelles_seances, nb_seances_existantes, False

                    # Ajoute la séance au stockage si elle n'existe pas déjà
                    if self.storage.seance_ajoute(seance):
                        self.logger.debug(f"Séance trouvée et ajoutée au stockage : {date_str} -> {full_url}")
                        nb_nouvelles_seances += 1
                    else:
                        self.logger.debug(f"Séance déjà existante : {date_str} -> {full_url}")
                        nb_seances_existantes += 1

        return nb_nouvelles_seances, nb_seances_existantes, True

    def extract_next_page(self, html_content: str, base_url: str) -> str | None:
        """
        Extrait les liens de pagination pour naviguer vers les pages suivantes.

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
        next_links = pagination_nav.find_all("a", class_="vd-pagination__link")

        for link in next_links:
            # Vérifier si c'est un lien "Page suivante"
            link_text = link.get_text(strip=True).lower()
            if "suivante" in link_text or "next" in link_text:
                href = link.get("href")
                if href:
                    full_url = urljoin(base_url, href)
                    self.logger.debug(f"Lien de pagination trouvé : {full_url}")
                    return full_url

        return None

    def scrape_seances(self) -> CESessionFinderResult:
        """
        Méthode principale pour extraire les séances du Conseil d'État avec pagination.

        Args:
        Returns:
            dict: Résumé de l'extraction
        """
        current_date = datetime.now().isoformat()
        self.logger.debug(f"Date de découverte pour cette session : {current_date}")

        first_url = "https://www.vd.ch/actualites/decisions-du-conseil-detat"
        self.logger.info(f"Début de l'extraction des séances depuis : {first_url}")

        # Détection automatique de l'URL de base depuis l'URL cible
        base_url = extract_base_url(first_url)

        new_seances_count = 0
        stop_reached = False
        current_url = first_url
        visited_urls = set()  # Pour éviter les boucles infinies

        while current_url and len(visited_urls) < MAX_SESSIONS and not stop_reached:
            # Vérifier si l'URL a déjà été visitée
            if current_url in visited_urls:
                self.logger.debug(f"URL déjà visitée, arrêt pour éviter la boucle infinie : {current_url}")
                break

            visited_urls.add(current_url)
            self.logger.debug(f"Traitement de la page {len(visited_urls)} : {current_url}")

            # Récupérer le contenu de la page
            html_content = self.html_fetcher.fetch_html_string(current_url)
            if not html_content:
                self.logger.error(f"Échec de la récupération du contenu de la page {current_url}")
                break

            # Extraire les liens des séances
            nb_nouv, nb_exist, cont = self.ajoute_seances_de_la_page(html_content, base_url, current_date)

            self.logger.info(
                f"Séances trouvées sur la page {len(visited_urls)} : {nb_nouv} nouvelle(s), {nb_exist} existante(s)"
            )
            new_seances_count += nb_nouv

            if not cont:
                break

            # Extraire les liens de pagination pour la page suivante
            current_url = self.extract_next_page(html_content, base_url)

            # Délai entre les requêtes pour être respectueux
            if current_url and PAGE_DELAY > 0:
                self.logger.debug(f"Attente de {PAGE_DELAY} seconde(s) avant la prochaine requête")
                time.sleep(PAGE_DELAY)

        stored_seances = self.storage.get_seance_count()

        self.logger.info(f"Nombre de nouvelles séances trouvées sur {len(visited_urls)} pages : {new_seances_count}")
        self.logger.info(f"Nombre total de séances stockées : {stored_seances}")

        return {
            "success": True,
            "pages_processed": len(visited_urls),
            "new_seances_count": new_seances_count,
            "stored_seances": stored_seances,
            "stop_reached": stop_reached,
        }
