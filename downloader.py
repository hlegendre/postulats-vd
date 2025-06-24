#!/usr/bin/env python3
"""
Téléchargeur de Séances du Conseil d'État VD

Ce script permet d'extraire automatiquement les informations des séances du Conseil d'État
du canton de Vaud depuis le site officiel.

Auteur: Hugues Le Gendre
Date: 2024
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
import time
from config import (
    MAX_PAGES,
    OUTPUT_FOLDER,
    PAGE_DELAY,
    REQUEST_TIMEOUT,
    STOP_DATE,
    TARGET_URL,
    USER_AGENT,
    VERBOSE,
)
import logging


class TelechargeurSeancesVD:
    def __init__(self, output_folder=OUTPUT_FOLDER):
        """
        Initialise le téléchargeur de séances.
        
        Args:
            output_folder (str): Dossier pour sauvegarder les données extraites
        """
        self.output_folder = Path(output_folder)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': USER_AGENT
        })
        
        # Configuration de la journalisation
        self.setup_logging()
        
        # Créer le dossier de sortie s'il n'existe pas
        self.output_folder.mkdir(exist_ok=True)
        
        # Nom du fichier JSON unique pour toutes les séances
        self.seances_file = self.output_folder / "seances_conseil_etat.json"
        
        # Charger les séances existantes
        self.existing_seances = self.load_existing_seances()
        
        self.logger.info(f"Téléchargeur de séances initialisé avec le dossier de sortie : {self.output_folder}")
        self.logger.info(f"Fichier de séances : {self.seances_file}")
        self.logger.info(f"Séances existantes chargées : {len(self.existing_seances)}")
    
    def setup_logging(self):
        """Configuration de la journalisation."""
        self.logger = logging.getLogger('SeancesDownloader')
        self.logger.setLevel(logging.INFO)
        
        # Créer le formateur
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        
        # Gestionnaire console
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
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
        soup = BeautifulSoup(html_content, 'html.parser')
        seance_links = []
        
        # Pattern pour détecter les liens de séances
        # Format attendu: "Séance du Conseil d'Etat du [date]"
        seance_pattern = re.compile(r'Séance du Conseil d\'Etat du (\d{1,2}\s+\w+\s+\d{4})', re.IGNORECASE)
        
        # Trouver tous les liens
        links = soup.find_all('a', href=True)
        
        for link in links:
            link_text = link.get_text(strip=True)
            href = link.get('href')
            
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
                        formatted_date = date_obj.strftime('%Y-%m-%d')
                    except Exception as e:
                        self.logger.warning(f"Impossible de parser la date '{date_str}': {e}")
                        formatted_date = date_str
                    
                    seance_info = {
                        'url': full_url,
                        'date': formatted_date,
                        'date_originale': date_str,
                        'titre': link_text
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
            'janvier': 1, 'février': 2, 'mars': 3, 'avril': 4,
            'mai': 5, 'juin': 6, 'juillet': 7, 'août': 8,
            'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12
        }
        
        # Pattern pour extraire jour, mois et année
        pattern = r'(\d{1,2})\s+(\w+)\s+(\d{4})'
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
    
    def load_existing_seances(self):
        """
        Charge les séances existantes depuis le fichier JSON.
        
        Returns:
            dict: Dictionnaire des séances existantes avec l'URL comme clé
        """
        if not self.seances_file.exists():
            self.logger.info("Aucun fichier de séances existant trouvé")
            return {}
        
        try:
            with open(self.seances_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                seances = data.get('seances', [])
                
                # Créer un dictionnaire avec l'URL comme clé pour un accès rapide
                existing_seances = {}
                for seance in seances:
                    existing_seances[seance['url']] = seance
                
                self.logger.info(f"Chargement de {len(existing_seances)} séances existantes")
                return existing_seances
                
        except (json.JSONDecodeError, FileNotFoundError) as e:
            self.logger.warning(f"Erreur lors du chargement des séances existantes : {e}")
            return {}
    
    def save_seances_to_json(self, seances):
        """
        Sauvegarde les informations des séances dans le fichier JSON unique.
        
        Args:
            seances (list): Liste des informations des séances
            
        Returns:
            str: Chemin du fichier sauvegardé
        """
        # Trier les séances par date
        seances_sorted = sorted(seances, key=lambda x: x['date'], reverse=True)
        
        data = {
            'metadonnees': {
                'url_source': TARGET_URL,
                'derniere_mise_a_jour': datetime.now().isoformat(),
                'total_seances': len(seances_sorted)
            },
            'seances': seances_sorted
        }
        
        with open(self.seances_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"Données sauvegardées dans : {self.seances_file}")
        return str(self.seances_file)
    
    def merge_new_seances(self, seances, current_date):
        """
        Fusionne les nouvelles séances avec les existantes.
        
        Args:
            seances (list): Liste des nouvelles séances trouvées
            current_date (str): Date de découverte pour cette session
            
        Returns:
            list: Liste complète des séances (existantes + nouvelles)
        """
        merged_seances = list(self.existing_seances.values())
        new_count = 0
        
        for seance in seances:
            if seance['url'] not in self.existing_seances:
                # Ajouter la date de découverte
                seance['date_decouverte'] = current_date
                merged_seances.append(seance)
                new_count += 1
                self.logger.info(f"Nouvelle séance trouvée : {seance['date']} - {seance['titre']}")
            else:
                self.logger.debug(f"Séance déjà connue ignorée : {seance['date']} - {seance['titre']}")
        
        self.logger.info(f"Fusion terminée : {new_count} nouvelles séances ajoutées")
        return merged_seances

    def extract_pagination_links(self, html_content, base_url):
        """
        Extrait les liens de pagination pour naviguer vers les pages suivantes.
        
        Args:
            html_content (str): Contenu HTML à analyser
            base_url (str): URL de base pour construire les URLs complètes
            
        Returns:
            list: Liste des URLs des pages suivantes
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        pagination_links = []
        
        # Chercher la pagination
        pagination_nav = soup.find('nav', {'aria-label': 'Pagination'})
        if not pagination_nav:
            self.logger.debug("Aucune pagination trouvée")
            return pagination_links
        
        # Chercher les liens "Page suivante" avec la classe spécifique
        next_links = pagination_nav.find_all('a', class_='vd-pagination__link')
        
        for link in next_links:
            # Vérifier si c'est un lien "Page suivante"
            link_text = link.get_text(strip=True).lower()
            if 'suivante' in link_text or 'next' in link_text:
                href = link.get('href')
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
            current_page_match = re.search(r'page%5D=(\d+)', html_content)
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
            seance_dt = datetime.strptime(seance_date, '%Y-%m-%d')
            stop_dt = datetime.strptime(STOP_DATE, '%Y-%m-%d')
            return seance_dt < stop_dt
        except ValueError as e:
            self.logger.warning(f"Erreur lors de la comparaison des dates : {e}")
            return False

    def scrape_seances(self, target_url=None):
        """
        Méthode principale pour extraire les séances du Conseil d'État avec pagination.
        
        Args:
            target_url (str): URL de la page à extraire (utilise TARGET_URL par défaut)
            
        Returns:
            dict: Résumé de l'extraction
        """
        if target_url is None:
            target_url = TARGET_URL
            
        self.logger.info(f"Début de l'extraction des séances depuis : {target_url}")
        
        # Définir la date de découverte une seule fois pour toute la session
        current_date = datetime.now().isoformat()
        self.logger.info(f"Date de découverte pour cette session : {current_date}")
        
        # Détection automatique de l'URL de base depuis l'URL cible
        parsed_url = urlparse(target_url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        self.logger.info(f"URL de base détectée : {base_url}")
        
        all_seances = []
        pages_processed = 0
        stop_reached = False
        current_url = target_url
        visited_urls = set()  # Pour éviter les boucles infinies
        
        while current_url and pages_processed < MAX_PAGES and not stop_reached:
            # Vérifier si l'URL a déjà été visitée
            if current_url in visited_urls:
                self.logger.warning(f"URL déjà visitée, arrêt pour éviter la boucle infinie : {current_url}")
                break
                
            visited_urls.add(current_url)
            pages_processed += 1  # Incrémenter le compteur au début du traitement de chaque page
            self.logger.info(f"Traitement de la page {pages_processed} : {current_url}")
            
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
            
            # Vérifier si on doit s'arrêter basé sur la date
            page_seances_to_add = []
            for seance in page_seances:
                if self.should_stop_scraping(seance['date']):
                    self.logger.info(f"Date limite atteinte ({STOP_DATE}). Séance trouvée : {seance['date']}")
                    stop_reached = True
                    break
                page_seances_to_add.append(seance)
            
            # Ajouter les séances de cette page à la liste totale
            all_seances.extend(page_seances_to_add)
            
            # Sauvegarder le fichier JSON après chaque page
            if page_seances_to_add:
                merged_seances = self.merge_new_seances(all_seances, current_date)
                self.save_seances_to_json(merged_seances)
                self.logger.info(f"Fichier JSON sauvegardé après la page {pages_processed} ({len(merged_seances)} séances total)")
            
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
        
        if not all_seances:
            self.logger.warning("Aucune séance trouvée sur toutes les pages")
            return {'success': True, 'seances': [], 'message': 'Aucune séance trouvée'}
        
        self.logger.info(f"Total des séances trouvées sur {pages_processed} pages : {len(all_seances)}")
        
        # Fusionner avec les séances existantes (final)
        merged_seances = self.merge_new_seances(all_seances, current_date)
        
        # Sauvegarder dans le fichier JSON (final)
        json_file = self.save_seances_to_json(merged_seances)
        
        return {
            'success': True,
            'seances': merged_seances,  # Ensemble de toutes les séances (existantes + nouvelles)
            'new_seances': [s for s in all_seances if s['url'] not in self.existing_seances],  # Seulement les nouvelles
            'json_file': json_file,
            'total_count': len(merged_seances),
            'new_count': len([s for s in all_seances if s['url'] not in self.existing_seances]),
            'pages_processed': pages_processed,
            'stop_reached': stop_reached
        }


def main():
    """Fonction principale."""
    downloader = TelechargeurSeancesVD()
    
    print("=== Téléchargeur de Séances du Conseil d'État VD ===")
    print(f"URL cible : {TARGET_URL}")
    print(f"Dossier de sortie : {OUTPUT_FOLDER}")
    print(f"Fichier de séances : {downloader.seances_file}")
    print(f"Date limite d'arrêt : {STOP_DATE if STOP_DATE else 'Aucune'}")
    print(f"Nombre maximum de pages : {MAX_PAGES}")
    print(f"Délai entre les pages : {PAGE_DELAY} seconde(s)")
    print()
    
    result = downloader.scrape_seances()
    
    if result['success']:
        print(f"✅ Extraction réussie !")
        print(f"📊 Total des séances : {result['total_count']}")
        print(f"🆕 Nouvelles séances ajoutées : {result['new_count']}")
        print(f"📄 Pages traitées : {result['pages_processed']}")
        print(f"📁 Fichier JSON : {result['json_file']}")
        
        if result.get('stop_reached'):
            print(f"🛑 Arrêt anticipé : date limite ({STOP_DATE}) atteinte")
        
        if result['new_seances']:
            print("\n🆕 Nouvelles séances ajoutées :")
            for i, seance in enumerate(result['new_seances'][:5]):
                print(f"  {i+1}. {seance['date']} - {seance['titre']}")
            
            if len(result['new_seances']) > 5:
                print(f"  ... et {len(result['new_seances']) - 5} autres")
        else:
            print(f"\nℹ️  Aucune nouvelle séance ajoutée")
    else:
        print(f"❌ Échec de l'extraction : {result.get('error', 'Erreur inconnue')}")


if __name__ == "__main__":
    main() 