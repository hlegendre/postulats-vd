"""
Fichier de configuration pour le "Téléchargeur de séances du Conseil d'État VD"
"""

# Configuration de base
OUTPUT_FOLDER = "output"
STORAGE_FILENAME = "storage.json"
MAX_LISTING_PAGES = 100  # Nombre maximum de pages de liste des séances du CE à parcourir (sécurité)

# Date limite d'arrêt de découverte des séances du Conseil d'État (format: 'YYYY-MM-DD' ou None)
STOP_DATE = "2024-01-01"

# Pattern de sélection des fichiers à télécharger
FILE_PATTERNS = ["_POS_"]

# Paramètres de requête
REQUEST_TIMEOUT = 30  # secondes
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
PAGE_DELAY = 1  # Délai en secondes entre les requêtes de pages
