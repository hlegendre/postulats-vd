"""
Fichier de configuration pour le "Téléchargeur de séances du Conseil d'État VD"
"""

# Configuration de base
OUTPUT_FOLDER = "output"
STORAGE_FILENAME = "storage.json"
MAX_SESSIONS = 1000  # Nombre maximum de sessions du CE à parcourir (sécurité)

# Date limite d'arrêt (format: 'YYYY-MM-DD')
# Le script s'arrêtera quand il trouvera une séance antérieure à cette date
# None = pas de limite (scrape toutes les pages)
STOP_DATE = "2025-06-11"

# Paramètres de requête
REQUEST_TIMEOUT = 30  # secondes
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
PAGE_DELAY = 1  # Délai en secondes entre les requêtes de pages
