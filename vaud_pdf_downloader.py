#!/usr/bin/env python3
"""
Téléchargeur de postulats VD
Télécharge automatiquement les fichiers PDF contenant des mots-clés spécifiés depuis la page des rapports de commission.
"""

import os
import re
import requests
import logging
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import time
from pathlib import Path
from datetime import datetime
from config import *


class TelechargeurPostulatsVD:
    def __init__(self, output_folder=OUTPUT_FOLDER):
        """
        Initialise le téléchargeur de postulats.
        
        Args:
            output_folder (str): Dossier pour sauvegarder les PDFs téléchargés
        """
        self.output_folder = Path(output_folder)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': USER_AGENT
        })
        
        # Setup logging
        self.setup_logging()
        
        # Create output folder if it doesn't exist
        self.output_folder.mkdir(exist_ok=True)
        
        self.logger.info(f"Téléchargeur de postulats initialisé avec le dossier de sortie : {self.output_folder}")
    
    def _extract_base_url(self, target_url):
        """
        Extrait l'URL de base à partir de l'URL cible.
        
        Args:
            target_url (str): URL complète de la page cible
            
        Returns:
            str: URL de base (protocole + domaine)
        """
        parsed_url = urlparse(target_url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        self.logger.debug(f"URL de base détectée : {base_url}")
        return base_url
        
    def setup_logging(self):
        """Configuration de la journalisation."""
        self.logger = logging.getLogger('TelechargeurPostulatsVD')
        self.logger.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        
        # Console handler
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
    
    def extract_pdf_links(self, html_content, base_url):
        """
        Extrait les liens PDF du contenu HTML qui contiennent les mots-clés spécifiés.
        
        Args:
            html_content (str): Contenu HTML à analyser
            base_url (str): URL de base pour construire les URLs complètes
            
        Returns:
            list: Liste des URLs PDF contenant les mots-clés
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        pdf_links = []
        
        # Find all links
        links = soup.find_all('a', href=True)
        
        for link in links:
            href = link.get('href')
            if href:
                # Check if the link contains any of the search keywords
                href_upper = href.upper()
                if any(keyword.upper() in href_upper for keyword in SEARCH_KEYWORDS):
                    # Check if it's a PDF or has a PDF-like structure
                    if any(ext.lower() in href.lower() for ext in FILE_EXTENSIONS) or 'pdf' in href.lower():
                        full_url = urljoin(base_url, href)
                        pdf_links.append(full_url)
                        self.logger.debug(f"Lien PDF trouvé : {full_url}")
        
        return pdf_links
    
    def download_pdf(self, pdf_url, filename=None):
        """
        Télécharge un fichier PDF.
        
        Args:
            pdf_url (str): URL du PDF à télécharger
            filename (str): Nom de fichier personnalisé optionnel
            
        Returns:
            bool: True si le téléchargement réussit, False sinon
        """
        try:
            # Extract filename from URL if not provided
            if not filename:
                parsed_url = urlparse(pdf_url)
                filename = os.path.basename(parsed_url.path)
                if not filename.endswith('.pdf'):
                    filename += '.pdf'
            
            # Clean filename
            filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
            filepath = self.output_folder / filename
            
            # Check if file already exists (before making HTTP request)
            if SKIP_EXISTING_FILES and filepath.exists():
                self.logger.info(f"Fichier déjà présent, ignoré : {filename}")
                return True
            
            self.logger.info(f"Téléchargement : {pdf_url}")
            
            response = self.session.get(pdf_url, timeout=DOWNLOAD_TIMEOUT, stream=True)
            response.raise_for_status()
            
            # Check if response is actually a PDF
            content_type = response.headers.get('content-type', '').lower()
            if 'pdf' not in content_type and not pdf_url.lower().endswith('.pdf'):
                self.logger.warning(f"L'URL pourrait ne pas être un PDF : {pdf_url} (Content-Type : {content_type})")
            
            # Save the PDF
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                    f.write(chunk)
            
            file_size = filepath.stat().st_size
            self.logger.info(f"Téléchargement réussi : {filename} ({file_size} octets)")
            return True
            
        except requests.RequestException as e:
            self.logger.error(f"Erreur lors du téléchargement de {pdf_url} : {e}")
            return False
        except Exception as e:
            self.logger.error(f"Erreur inattendue lors du téléchargement de {pdf_url} : {e}")
            return False
    
    def scrape_and_download(self, target_url):
        """
        Méthode principale pour extraire la page et télécharger les PDFs contenant les mots-clés.
        
        Args:
            target_url (str): URL de la page à extraire
            
        Returns:
            int: Nombre de PDFs téléchargés avec succès
        """
        self.logger.info(f"Début de l'extraction et du téléchargement depuis : {target_url}")
        
        # Auto-detect base URL from target URL
        base_url = self._extract_base_url(target_url)
        self.logger.info(f"URL de base détectée : {base_url}")
        
        # Get the page content
        html_content = self.get_page_content(target_url)
        if not html_content:
            self.logger.error("Échec de la récupération du contenu de la page")
            return 0
        
        # Extract PDF links
        pdf_links = self.extract_pdf_links(html_content, base_url)
        
        if not pdf_links:
            self.logger.warning(f"Aucun lien PDF contenant les mots-clés {SEARCH_KEYWORDS} trouvé sur la page")
            return 0
        
        self.logger.info(f"{len(pdf_links)} liens PDF trouvés contenant les mots-clés {SEARCH_KEYWORDS} :")
        for link in pdf_links:
            self.logger.info(f"  - {link}")
        
        # Download each PDF
        successful_downloads = 0
        failed_downloads = 0
        skipped_files = 0
        
        for i, pdf_url in enumerate(pdf_links, 1):
            self.logger.info(f"Traitement {i}/{len(pdf_links)} : {pdf_url}")
            
            # Extract filename for checking if it exists
            parsed_url = urlparse(pdf_url)
            filename = os.path.basename(parsed_url.path)
            if not filename.endswith('.pdf'):
                filename += '.pdf'
            filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
            filepath = self.output_folder / filename
            
            # Check if file already exists before attempting download
            if SKIP_EXISTING_FILES and filepath.exists():
                self.logger.info(f"Fichier déjà présent, ignoré : {filename}")
                skipped_files += 1
                continue
            
            if self.download_pdf(pdf_url):
                successful_downloads += 1
            else:
                failed_downloads += 1
            
            # Add delay between downloads
            if i < len(pdf_links):
                time.sleep(DELAY_BETWEEN_DOWNLOADS)
        
        self.logger.info(f"Résumé du téléchargement : {successful_downloads} téléchargés, {skipped_files} ignorés, {failed_downloads} échoués")
        return successful_downloads


def main():
    """Fonction principale pour exécuter le téléchargeur de postulats."""
    print("Téléchargeur de postulats VD")
    print("=" * 50)
    print(f"URL cible : {TARGET_URL}")
    print(f"Dossier de sortie : {OUTPUT_FOLDER}")
    print(f"Mots-clés de recherche : {SEARCH_KEYWORDS}")
    print(f"Extensions de fichiers : {FILE_EXTENSIONS}")
    print(f"Ignorer les fichiers existants : {'Oui' if SKIP_EXISTING_FILES else 'Non'}")
    print()
    
    # Initialize downloader
    downloader = TelechargeurPostulatsVD(output_folder=OUTPUT_FOLDER)
    
    # Start downloading
    start_time = datetime.now()
    successful_downloads = downloader.scrape_and_download(TARGET_URL)
    end_time = datetime.now()
    
    # Print summary
    print()
    print("=" * 50)
    print(f"Téléchargement terminé !")
    print(f"{successful_downloads} fichiers PDF téléchargés avec succès")
    if SKIP_EXISTING_FILES:
        print(f"Les fichiers déjà présents dans '{OUTPUT_FOLDER}' ont été ignorés")
    print(f"Fichiers enregistrés dans : {OUTPUT_FOLDER}")
    print(f"Durée : {end_time - start_time}")


if __name__ == "__main__":
    main() 