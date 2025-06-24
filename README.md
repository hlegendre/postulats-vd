# Téléchargeur de postulats VD

Une application Python qui télécharge automatiquement les fichiers PDF contenant "POS" dans leur nom depuis la page des rapports de commission du Grand Conseil vaudois.

## Fonctionnalités

- **Téléchargement automatique de PDF** : Extrait le site web du Grand Conseil vaudois et télécharge les fichiers PDF contenant des mots-clés spécifiés
- **Configurable** : Facile à modifier les critères de recherche, le dossier de sortie et les paramètres de téléchargement
- **Gestion d'erreurs** : Gestion robuste des erreurs avec journalisation détaillée
- **Reprise de téléchargement** : Ignore automatiquement les fichiers déjà téléchargés pour éviter les doublons
- **Extraction respectueuse** : Inclut des délais entre les téléchargements pour être respectueux du serveur

## Installation

### Prérequis

Assurez-vous d'avoir Python 3.8+ installé sur votre système.

### Installation avec uv

1. **Installer uv** (si pas déjà installé) :

   ```bash
   # Sur macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Ou en utilisant pip
   pip install uv
   ```

2. **Cloner ou télécharger les fichiers du projet**

3. **Installer les dépendances avec uv** :

   ```bash
   uv sync
   ```

4. **Activer l'environnement virtuel** :

   ```bash
   source .venv/bin/activate  # Sur macOS/Linux
   # ou
   .venv\Scripts\activate     # Sur Windows
   ```

## Utilisation

### Utilisation de base

Lancer l'application principale :

```bash
python downloader.py
```

Cela va :

- Extraire la page des rapports de commission du Grand Conseil vaudois
- Trouver tous les liens PDF contenant "POS" dans le nom de fichier
- Les télécharger dans le dossier `postulats`
- Afficher le progrès et les résultats

### Test

Avant de lancer l'application principale, vous pouvez tester si tout fonctionne :

```bash
python test_downloader.py
```

Cela va tester :

- L'accessibilité du site web
- L'extraction des liens PDF
- L'accessibilité des URLs PDF

### Configuration

Vous pouvez personnaliser l'application en modifiant `config.py` :

```python
# Critères de recherche
SEARCH_KEYWORDS = ["POS"]  # Mots-clés à rechercher dans les noms de fichiers
FILE_EXTENSIONS = [".pdf"]  # Extensions de fichiers à télécharger

# Paramètres de sortie
OUTPUT_FOLDER = "postulats"  # Dossier pour sauvegarder les PDFs téléchargés

# Paramètres de téléchargement
DOWNLOAD_TIMEOUT = 60  # secondes
REQUEST_TIMEOUT = 30   # secondes
CHUNK_SIZE = 8192      # bytes
DELAY_BETWEEN_DOWNLOADS = 1  # secondes

# Comportement de saut de fichiers
SKIP_EXISTING_FILES = True  # Ignorer les fichiers déjà présents dans le dossier de sortie
```

### Utilisation avancée

Vous pouvez aussi utiliser le téléchargeur programmatiquement :

```python
from downloader import TelechargeurPostulatsVD

# Initialiser avec des paramètres personnalisés
telechargeur = TelechargeurPostulatsVD(
    output_folder="mes_pdfs"
)

# Télécharger les PDFs depuis une URL spécifique
telechargements_reussis = telechargeur.scrape_and_download(
    "https://www.vd.ch/gc/objets-et-rapports-de-commissions/liste-des-rapports-de-commission"
)

print(f"{telechargements_reussis} fichiers PDF téléchargés")
```

## Structure des fichiers

```text
telechargeur_postulats_vd/
├── downloader.py              # Application principale
├── config.py                    # Fichier de configuration
├── test_downloader.py           # Script de test
├── pyproject.toml               # Configuration du projet (uv)
├── README.md                    # Ce fichier
├── setup.sh                     # Script de configuration (macOS/Linux)
├── setup.bat                    # Script de configuration (Windows)
├── .venv/                       # Environnement virtuel (créé par uv)
└── postulats/                    # PDFs téléchargés (créé automatiquement)
```

## Développement

### Utilisation de uv pour le développement

1. **Installer les dépendances de développement** :

   ```bash
   uv sync --extra dev
   ```

2. **Lancer les tests** :

   ```bash
   uv run pytest
   ```

3. **Formater le code** :

   ```bash
   uv run black .
   ```

4. **Linter le code** :

   ```bash
   uv run flake8 .
   ```

## Options de configuration

### Critères de recherche

- `SEARCH_KEYWORDS` : Liste des mots-clés à rechercher dans les noms de fichiers (défaut : `["POS"]`)
- `FILE_EXTENSIONS` : Liste des extensions de fichiers à télécharger (défaut : `[".pdf"]`)

### Paramètres de téléchargement

- `DOWNLOAD_TIMEOUT` : Timeout pour les téléchargements de PDF en secondes (défaut : `60`)
- `REQUEST_TIMEOUT` : Timeout pour les requêtes de pages en secondes (défaut : `30`)
- `CHUNK_SIZE` : Taille des chunks lors du téléchargement de fichiers (défaut : `8192`)
- `DELAY_BETWEEN_DOWNLOADS` : Délai entre les téléchargements en secondes (défaut : `1`)

### Comportement de saut de fichiers

- `SKIP_EXISTING_FILES` : Ignorer les fichiers déjà présents dans le dossier de sortie (défaut : `True`)

### Journalisation

- `VERBOSE` : Activer la journalisation verbeuse (défaut : `True`)

## Fonctionnalités techniques

### Détection automatique de l'URL de base

L'application détecte automatiquement l'URL de base à partir de l'URL cible fournie. Cela permet de :

- Traiter les liens relatifs et absolus
- Fonctionner avec n'importe quel site web sans configuration supplémentaire
- S'adapter automatiquement si l'URL cible change

### Exemple de détection

- **URL cible** : `https://www.vd.ch/gc/objets-et-rapports-de-commissions/liste-des-rapports-de-commission`
- **URL de base détectée** : `https://www.vd.ch`
- **Lien relatif trouvé** : `/fileadmin/user_upload/gc/25_POS_17.pdf`
- **URL complète générée** : `https://www.vd.ch/fileadmin/user_upload/gc/25_POS_17.pdf`

## Exemple de sortie

```text
Téléchargeur de postulats VD
==================================================
URL cible : https://www.vd.ch/gc/objets-et-rapports-de-commissions/liste-des-rapports-de-commission
Dossier de sortie : postulats
Mots-clés de recherche : ['POS']
Extensions de fichiers : ['.pdf']
Ignorer les fichiers existants : Oui

2024-01-15 10:30:15 - INFO - Téléchargeur de postulats initialisé avec le dossier de sortie : postulats
2024-01-15 10:30:15 - INFO - Début de l'extraction et du téléchargement depuis : https://www.vd.ch/...
2024-01-15 10:30:16 - INFO - Récupération de la page : https://www.vd.ch/...
2024-01-15 10:30:17 - INFO - Page récupérée avec succès
2024-01-15 10:30:17 - INFO - 5 liens PDF trouvés contenant les mots-clés ['POS'] :
2024-01-15 10:30:17 - INFO -   - https://www.vd.ch/fileadmin/user_upload/.../25_POS_17.pdf
2024-01-15 10:30:17 - INFO -   - https://www.vd.ch/fileadmin/user_upload/.../25_POS_1.pdf
2024-01-15 10:30:18 - INFO - Traitement 1/5 : https://www.vd.ch/fileadmin/user_upload/.../25_POS_17.pdf
2024-01-15 10:30:18 - INFO - Fichier déjà présent, ignoré : 25_POS_17.pdf
2024-01-15 10:30:19 - INFO - Traitement 2/5 : https://www.vd.ch/fileadmin/user_upload/.../25_POS_1.pdf
2024-01-15 10:30:20 - INFO - Téléchargement : https://www.vd.ch/fileadmin/user_upload/.../25_POS_1.pdf
2024-01-15 10:30:22 - INFO - Téléchargement réussi : 25_POS_1.pdf (245760 octets)
...
2024-01-15 10:30:25 - INFO - Résumé du téléchargement : 3 téléchargés, 2 ignorés, 0 échoués

==================================================
Téléchargement terminé !
3 fichiers PDF téléchargés avec succès
Les fichiers déjà présents dans 'postulats' ont été ignorés
Fichiers enregistrés dans : postulats
Durée : 0:00:10.234567
```

## Dépannage

### Problèmes courants

1. **Aucun PDF trouvé** : La structure du site web a peut-être changé. Vérifiez le contenu HTML manuellement.

2. **Échecs de téléchargement** :

   - Vérifiez votre connexion internet
   - Vérifiez que les URLs sont accessibles
   - Consultez le fichier de journal pour les messages d'erreur détaillés

3. **Erreurs de permission** : Assurez-vous d'avoir les permissions d'écriture dans le dossier de sortie.

4. **Problèmes d'installation uv** :
   - Assurez-vous d'avoir Python 3.8+ installé
   - Essayez d'installer uv avec pip : `pip install uv`

### Mode debug

Pour activer la journalisation debug, modifiez le niveau de journalisation dans le code :

```python
self.logger.setLevel(logging.DEBUG)
```

## Avis légal

Cette application est à des fins éducatives et de recherche. Veuillez respecter les conditions d'utilisation du site web et le fichier robots.txt. L'application inclut des délais entre les requêtes pour être respectueuse du serveur.

## Licence

Ce projet est open source et disponible sous la licence MIT.

## Contribution

N'hésitez pas à soumettre des problèmes, des demandes de fonctionnalités ou des pull requests pour améliorer cette application.
