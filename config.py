"""
Fichier de configuration pour le "Téléchargeur de postulats VD"
"""

# Base configuration
TARGET_URL = "https://www.vd.ch/gc/objets-et-rapports-de-commissions/liste-des-rapports-de-commission"
OUTPUT_FOLDER = "postulats"

# Search criteria
SEARCH_KEYWORDS = ["POS"]  # Keywords to look for in filenames
FILE_EXTENSIONS = [".pdf"]  # File extensions to download

# Download settings
DOWNLOAD_TIMEOUT = 60  # seconds
REQUEST_TIMEOUT = 30   # seconds
CHUNK_SIZE = 8192      # bytes
DELAY_BETWEEN_DOWNLOADS = 1  # seconds

# File skipping behavior
SKIP_EXISTING_FILES = True  # Skip files that already exist in output folder

# User agent for requests
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

# Logging
VERBOSE = True 