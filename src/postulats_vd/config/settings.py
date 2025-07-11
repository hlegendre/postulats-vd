"""
Fichier de configuration pour le "Téléchargeur de séances du Conseil d'État VD"
"""

# Configuration de base
OUTPUT_FOLDER: str = "output"
STORAGE_FILENAME: str = "storage.json"
MAX_LISTING_PAGES: int = 100  # Nombre maximum de pages de liste des séances du CE à parcourir (sécurité)

# Date limite d'arrêt de découverte des séances du Conseil d'État (format: 'YYYY-MM-DD' ou None)
STOP_DATE: str | None = "2024-01-14"

# Optimisation du listing : fait un scan partiel des séances les plus récentes si la date la plus ancienne est proche de la date d'arrêt
OPTIMIZATION_THRESHOLD_DAYS: int = 6

# Pattern de sélection des fichiers à télécharger
FILE_PATTERNS: list[str] = ["_POS_"]

# Paramètres de requête
REQUEST_TIMEOUT: int = 30  # secondes
USER_AGENT: str = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
PAGE_DELAY: int = 1  # Délai en secondes entre les requêtes de pages
