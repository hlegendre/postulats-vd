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
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
import time
from ..config import (
    MAX_SESSIONS,
    OUTPUT_FOLDER,
    PAGE_DELAY,
    REQUEST_TIMEOUT,
    STOP_DATE,
    USER_AGENT,
)
from .storage import Storage
from ..utils.logging import LoggingUtils


class TelechargeurSeancesVD:
    def __init__(self, output_folder=OUTPUT_FOLDER):
        """
        Initialise le téléchargeur de séances du Conseil d'État.

        Args:
            output_folder (str): Dossier pour sauvegarder les données extraites
        """
        self.output_folder = Path(output_folder)
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})

        # Configuration de la journalisation
        self.logger = LoggingUtils.setup_simple_logger("ExtracteurSéances")

        # Initialiser le gestionnaire de stockage
        self.storage = Storage(output_folder=output_folder)

        self.logger.info(f"Téléchargeur de séances initialisé avec le dossier de sortie : {self.output_folder}")
        self.logger.info(f"Fichier de séances : {self.storage.get_file_path()}")
        self.logger.info(f"Séances existantes chargées : {self.storage.get_seance_count()}")

    def get_page_content(self, url):
        """
        Récupère le contenu d'une page web.

        Args:
            url (str): URL à récupérer

        Returns:
            str: Contenu HTML de la page
        """
        try:
            self.logger.info(f"Récupération de la page : {url}")
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            self.logger.info("Page récupérée avec succès")
            return response.text
        except requests.RequestException as e:
            self.logger.error(f"Erreur lors de la récupération de {url} : {e}")
            return None

    def extract_seance_links(self, html_content, base_url):
        """
        Extrait les liens des séances du Conseil d'État avec leurs dates.

        Args:
            html_content (str): Contenu HTML à analyser
            base_url (str): URL de base pour construire les URLs complètes

        Returns:
            list: Liste des dictionnaires contenant l'URL et la date de chaque séance
        """
        soup = BeautifulSoup(html_content, "html.parser")
        seance_links = []

        # Pattern pour détecter les liens de séances
        # Format attendu: "Séance du Conseil d'Etat du [date]"
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
                        date_obj = self.parse_french_date(date_str)
                        formatted_date = date_obj.strftime("%Y-%m-%d")
                    except Exception as e:
                        self.logger.warning(f"Impossible de parser la date '{date_str}': {e}")
                        formatted_date = date_str

                    seance_info = {
                        "url": full_url,
                        "date": formatted_date,
                        "date_originale": date_str,
                        "titre": link_text,
                    }

                    seance_links.append(seance_info)
                    self.logger.debug(f"Séance trouvée : {date_str} -> {full_url}")

        return seance_links

    def parse_french_date(self, date_str):
        """
        Parse une date française en objet datetime.

        Args:
            date_str (str): Date au format français (ex: "18 juin 2025")

        Returns:
            datetime: Objet datetime correspondant
        """
        # Mapping des mois français vers les numéros
        mois_mapping = {
            "janvier": 1,
            "février": 2,
            "mars": 3,
            "avril": 4,
            "mai": 5,
            "juin": 6,
            "juillet": 7,
            "août": 8,
            "septembre": 9,
            "octobre": 10,
            "novembre": 11,
            "décembre": 12,
        }

        # Pattern pour extraire jour, mois et année
        pattern = r"(\d{1,2})\s+(\w+)\s+(\d{4})"
        match = re.search(pattern, date_str.lower())

        if match:
            jour = int(match.group(1))
            mois_nom = match.group(2)
            annee = int(match.group(3))

            if mois_nom in mois_mapping:
                mois = mois_mapping[mois_nom]
                return datetime(annee, mois, jour)
            else:
                raise ValueError(f"Mois non reconnu: {mois_nom}")
        else:
            raise ValueError(f"Format de date non reconnu: {date_str}")

    def extract_pagination_links(self, html_content, base_url):
        """
        Extrait les liens de pagination pour naviguer vers les pages suivantes.

        Args:
            html_content (str): Contenu HTML à analyser
            base_url (str): URL de base pour construire les URLs complètes

        Returns:
            list: Liste des URLs des pages suivantes
        """
        soup = BeautifulSoup(html_content, "html.parser")
        pagination_links = []

        # Chercher la pagination
        pagination_nav = soup.find("nav", {"aria-label": "Pagination"})
        if not pagination_nav:
            self.logger.debug("Aucune pagination trouvée")
            return pagination_links

        # Chercher les liens "Page suivante" avec la classe spécifique
        next_links = pagination_nav.find_all("a", class_="vd-pagination__link")

        for link in next_links:
            # Vérifier si c'est un lien "Page suivante"
            link_text = link.get_text(strip=True).lower()
            if "suivante" in link_text or "next" in link_text:
                href = link.get("href")
                if href:
                    full_url = urljoin(base_url, href)
                    # Éviter les doublons
                    if full_url not in pagination_links:
                        pagination_links.append(full_url)
                        self.logger.debug(f"Lien de pagination trouvé : {full_url}")

        # Si aucun lien "suivante" trouvé, essayer d'extraire le numéro de page actuel
        # et construire le lien vers la page suivante
        if not pagination_links:
            # Chercher le numéro de page actuel dans l'URL ou dans le contenu
            current_page_match = re.search(r"page%5D=(\d+)", html_content)
            if current_page_match:
                current_page = int(current_page_match.group(1))
                next_page = current_page + 1
                # Construire l'URL de la page suivante
                next_url = f"{base_url}/actualites/decisions-du-conseil-detat?tx_vdsafarinet_safarinet%5Bcontroller%5D=Meeting&tx_vdsafarinet_safarinet%5Bpage%5D={next_page}"
                pagination_links.append(next_url)
                self.logger.debug(f"Lien de pagination construit : {next_url}")

        return pagination_links

    def should_stop_scraping(self, seance_date):
        """
        Détermine si le scraping doit s'arrêter basé sur la date de la séance.

        Args:
            seance_date (str): Date de la séance au format 'YYYY-MM-DD'

        Returns:
            bool: True si le scraping doit s'arrêter
        """
        if STOP_DATE is None:
            return False

        try:
            seance_dt = datetime.strptime(seance_date, "%Y-%m-%d")
            stop_dt = datetime.strptime(STOP_DATE, "%Y-%m-%d")
            return seance_dt < stop_dt
        except ValueError as e:
            self.logger.warning(f"Erreur lors de la comparaison des dates : {e}")
            return False

    def scrape_seances(self, target_url="https://www.vd.ch/actualites/decisions-du-conseil-detat"):
        """
        Méthode principale pour extraire les séances du Conseil d'État avec pagination.

        Args:
            target_url (str): URL de la page à extraire (utilise TARGET_URL par défaut)

        Returns:
            dict: Résumé de l'extraction
        """
        self.logger.info(f"Début de l'extraction des séances depuis : {target_url}")

        # Définir la date de découverte une seule fois pour toute la session
        current_date = datetime.now().isoformat()
        self.logger.info(f"Date de découverte pour cette session : {current_date}")

        # Détection automatique de l'URL de base depuis l'URL cible
        parsed_url = urlparse(target_url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

        new_seances_count = 0
        pages_processed = 0
        stop_reached = False
        current_url = target_url
        visited_urls = set()  # Pour éviter les boucles infinies

        while current_url and pages_processed < MAX_SESSIONS and not stop_reached:
            # Vérifier si l'URL a déjà été visitée
            if current_url in visited_urls:
                self.logger.warning(f"URL déjà visitée, arrêt pour éviter la boucle infinie : {current_url}")
                break

            visited_urls.add(current_url)
            pages_processed += 1  # Incrémenter le compteur au début du traitement de chaque page
            self.logger.debug(f"Traitement de la page {pages_processed} : {current_url}")

            # Récupérer le contenu de la page
            html_content = self.get_page_content(current_url)
            if not html_content:
                self.logger.error(f"Échec de la récupération du contenu de la page {pages_processed}")
                break

            # Extraire les liens des séances
            page_seances = self.extract_seance_links(html_content, base_url)

            if not page_seances:
                self.logger.warning(f"Aucune séance trouvée sur la page {pages_processed}")
                break

            self.logger.info(f"Nombre de séances trouvées sur la page {pages_processed} : {len(page_seances)}")

            # Traiter chaque séance de la page
            page_new_seances = 0
            for seance in page_seances:
                # Vérifier si on doit s'arrêter basé sur la date
                if self.should_stop_scraping(seance["date"]):
                    self.logger.info(f"Date limite atteinte ({STOP_DATE}). Séance trouvée : {seance['date']}")
                    stop_reached = True
                    break

                # Ajouter la séance au stockage
                if self.storage.seance_ajoute(seance, current_date):
                    page_new_seances += 1
                    new_seances_count += 1

            if stop_reached:
                break

            # Extraire les liens de pagination pour la page suivante
            pagination_links = self.extract_pagination_links(html_content, base_url)

            if pagination_links:
                current_url = pagination_links[0]  # Prendre le premier lien de pagination

                # Délai entre les requêtes pour être respectueux
                if PAGE_DELAY > 0:
                    self.logger.debug(f"Attente de {PAGE_DELAY} seconde(s) avant la prochaine requête")
                    time.sleep(PAGE_DELAY)
            else:
                self.logger.info("Aucun lien de pagination trouvé, fin du scraping")
                break

        stored_seances = self.storage.get_seance_count()

        self.logger.info(f"Nombre de nouvelles séances trouvées sur {pages_processed} pages : {new_seances_count}")
        self.logger.info(f"Nombre total de séances stockées : {stored_seances}")

        return {
            "success": True,
            "pages_processed": pages_processed,
            "new_seances_count": new_seances_count,
            "stored_seances": stored_seances,
            "stop_reached": stop_reached,
        }
