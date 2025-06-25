"""
Fichier de configuration pour le "Téléchargeur de séances du Conseil d'État VD"
"""

# Base configuration
TARGET_URL = "https://www.vd.ch/actualites/decisions-du-conseil-detat"
OUTPUT_FOLDER = "output"

# Request settings
REQUEST_TIMEOUT = 30  # seconds

# User agent for requests
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

# Logging
VERBOSE = True

# Pagination settings
MAX_SESSIONS = (
    1000  # Nombre maximum de sessions du Conseil d'État à parcourir (sécurité)
)
PAGE_DELAY = 1  # Délai en secondes entre les requêtes de pages

# Date limite d'arrêt (format: 'YYYY-MM-DD')
# Le script s'arrêtera quand il trouvera une séance antérieure à cette date
# None = pas de limite (scrape toutes les pages)
STOP_DATE = "2024-05-14"  # Exemple: s'arrêter au 14 mai 2024