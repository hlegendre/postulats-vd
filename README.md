# Téléchargeur de postulats du Conseil d'État VD

Ce script permet d'extraire automatiquement les postulats des séances du Conseil d'État du canton de Vaud depuis le site officiel.

## Fonctionnalités

- **Extraction automatique** : Récupère les URLs, dates, titres et contenus détaillés des séances depuis le site officiel
- **Système de logging unifié** : Un seul fichier JSON récapitule toutes les séances
- **Détection des nouvelles séances** : Ignore automatiquement les séances déjà connues
- **Optimisation du listing** : Récupération des séances les plus récentes manquantes sauf si la date d'arrêt est éloignée de la séance la plus ancienne
- **Métadonnées de découverte** : Chaque séance inclut sa date de première découverte
- **Parsing des dates françaises** : Conversion automatique des dates françaises en format ISO
- **Pagination automatique** : Parcourt automatiquement toutes les pages disponibles
- **Arrêt conditionnel** : Possibilité de s'arrêter à une date limite configurée
- **Extraction des discussions et fichiers** : Pour chaque séance, toutes les discussions et fichiers associés sont extraits
- **Filtrage intelligent des fichiers** : Seuls les fichiers correspondant aux patterns configurés sont téléchargés

## Structure du fichier JSON

Le script génère un fichier unique `output/storage.json` avec la structure suivante :

```json
{
  "metadonnees": {
    "url_source": "https://www.vd.ch/actualites/decisions-du-conseil-detat",
    "derniere_mise_a_jour": "2025-06-25T15:52:30.031871",
    "total_seances": 2
  },
  "seances": [
    {
      "url": "https://www.vd.ch/actualites/decisions-du-conseil-detat/seance-du-conseil-detat/seance/1029290",
      "date": "2025-06-18",
      "date_originale": "2025-06-18",
      "date_decouverte": "2025-06-25T15:52:17.868910",
      "titre": "Séance du Conseil d'Etat du 18 juin 2025",
      "discussions": [
        {
          "titre": "Un nouveau bâtiment pour la Haute école pédagogique à Chavannes-près-Renens",
          "fichiers": [
            {
              "url": "https://sieldocs.vd.ch/ecm/app18/service/siel/getContent?ID=2310752",
              "nom": "EMPD accordant au Conseil d'État un crédit d'investissement...",
              "alias": "20250618_2310752.pdf"
            }
          ]
        },
        {
          "titre": "Crédit d'études pour le remplacement du Dossier patient informatisé",
          "fichiers": []
        }
      ]
    }
  ]
}
```

### Champs des séances

- `url` : URL complète de la page de la séance
- `date` : Date au format ISO (YYYY-MM-DD)
- `date_originale` : Date originale (format source)
- `date_decouverte` : Date et heure de première découverte de cette séance
- `titre` : Titre de la séance
- `discussions` : Liste des discussions de la séance

### Champs des discussions

- `titre` : Titre de la partie
- `fichiers` : Liste des fichiers associés à cette partie

### Champs des fichiers

- `url` : URL du fichier
- `nom` : Nom ou description du fichier
- `alias` : Nom du fichier dans le dossier de sortie (format : YYYYMMDD_ID.pdf)

## Utilisation

### Installation

1. Installer les dépendances avec uv (recommandé) :

```bash
uv sync
```

Ou avec pip :

```bash
pip install -e .
```

### Exécution

```bash
# Mode silencieux (par défaut)
python run.py

# Mode info (affiche les informations de base)
python run.py -v

# Mode debug (affiche tous les détails)
python run.py -vv

# Force le relistage des séances
python run.py --relist

# Afficher l'aide
python run.py --help
```

### Options disponibles

- `-v, --verbose` : Niveau de verbosité
  - `-v` : Mode info (affiche les informations de base)
  - `-vv` : Mode debug (affiche tous les détails)
  - Par défaut : Mode silencieux (affiche uniquement les résultats finaux)
- `--relist` : Force le relistage des séances

### Niveaux de verbosité

- **Mode silencieux** (par défaut) : Affiche uniquement les résultats finaux de chaque étape
- **Mode info** (`-v`) : Affiche les informations de base comme le dossier de sortie et la date limite d'arrêt
- **Mode debug** (`-vv`) : Affiche tous les détails, y compris les URLs traitées, les fichiers téléchargés, etc.

```bash
python run.py -v / -vv
```

### Mode relistage

Le mode relistage permet de récupérer toutes les séances depuis aujourd'hui jusqu'à la date d'arrêt.
Par défaut, on scanne uniquement les séances les plus récentes non existantes.

```bash
python run.py --relist
```

### Sortie

Le script affiche trois sections principales :

1. **Découverte des séances** : Nombre de nouvelles séances trouvées, total de séances stockées, et pages traitées (avec optimisation ou non)
2. **Extraction des séances** : Nombre de nouvelles séances extraites, séances existantes, et séances en erreur
3. **Téléchargement des fichiers** : Nombre de fichiers téléchargés, ignorés, existants, et en erreur

Exemple de sortie :

```text
=== Découverte des Séances du Conseil d'État VD ===
✅ OK : nouvelles = 2 / totales = 10 (pages = 1, optimisé)

=== Extraction des Séances du Conseil d'État VD ===
✅ OK : nouvelles = 2 / existantes = 8 / en erreur = 0

=== Téléchargement des Fichiers des Séances du Conseil d'État VD ===
✅ OK : téléchargés = 5 / ignorés = 3 / existants = 2 / en erreur = 0
```

Le fichier de base de données est : `output/storage.json`

## Qualité du Code

### Outils de qualité

Le projet utilise plusieurs outils pour maintenir la qualité du code :

- **Ruff** : Formateur + linter de code automatique
- **Pre-commit hooks** : Vérifications automatiques avant chaque commit

### Installation des hooks pre-commit

Pour installer les hooks pre-commit manuellement :

```bash
uv run pre-commit install
```

sinon, il suffit de lancer le script de configuration :

```bash
./setup.sh / setup.bat
```

### Utilisation des outils de qualité

**Vérifier le formatage / linter le code avec Ruff :**

```bash
uv run ruff check
```

**Exécuter le formatage / linter avec modification :**

```bash
uv run ruff format
```

**Tester manuellement le hook pre-commit :**

```bash
uv run pre-commit run --all-files
```

### Comportement des hooks

Le hook pre-commit s'exécute automatiquement avant chaque commit et :

1. **Vérifie le formatage** : S'assure que le code respecte les standards Ruff
2. **Lance le linter** : Détecte les erreurs de style et de logique avec Ruff
3. **Bloque le commit** : Si des erreurs sont trouvées, le commit est annulé

**Pour ignorer le hook (urgence uniquement) :**

```bash
git commit --no-verify -m "message d'urgence"
```

## Comportement

### Premier lancement

- Crée le fichier `output/storage.json`
- Extrait toutes les séances disponibles depuis toutes les pages
- Ajoute la métadonnée `date_decouverte` à chaque séance
- Extrait toutes les discussions et fichiers associés à chaque séance

### Lancements suivants

- Charge les séances existantes depuis le fichier JSON
- Extrait les séances depuis le site web (avec pagination)
- Compare les URLs pour identifier les nouvelles séances
- Ajoute uniquement les nouvelles séances avec leur `date_decouverte`
- Met à jour le fichier JSON avec toutes les séances et leur contenu détaillé

## Tests

Exécuter les tests :

```bash
uv run pytest
```

Les tests vérifient :

- La création initiale du fichier JSON
- L'ignorance des séances déjà connues
- La détection des nouvelles séances
- La conservation des métadonnées de découverte
- L'extraction correcte des discussions et fichiers

## Configuration

Le script utilise le fichier `src/postulats_vd/config/settings.py` pour sa configuration :

### Paramètres de base

- `OUTPUT_FOLDER` : Dossier de sortie pour les fichiers JSON et PDF (par défaut `output`)
- `STORAGE_FILENAME` : Nom du fichier JSON de stockage (par défaut `storage.json`)
- `MAX_SESSIONS` : Nombre maximum de pages à parcourir (par défaut `1000`)

### Paramètres de filtrage

- `STOP_DATE` : Date limite d'arrêt (format YYYY-MM-DD, par défaut `"2024-01-01"`)
- `FILE_PATTERNS` : Patterns pour filtrer les fichiers à télécharger (par défaut `["_POS_"]`)
- `OPTIMIZATION_THRESHOLD_DAYS` : Nombre de jours maximum entre la date d'arrêt et la date la plus ancienne pour activer l'optimisation (par défaut `6`)

### Paramètres de requête HTTP

- `REQUEST_TIMEOUT` : Timeout des requêtes HTTP en secondes (par défaut `30`)
- `USER_AGENT` : User agent pour les requêtes HTTP
- `PAGE_DELAY` : Délai en secondes entre les requêtes de pages (par défaut `1`)

**Note** : Le niveau de verbosité est configuré via les arguments de ligne de commande (`-v`, `-vv`) et non dans le fichier de configuration.

## Filtrage des fichiers

Le script utilise le paramètre `FILE_PATTERNS` pour déterminer quels fichiers télécharger. Par défaut, seuls les fichiers contenant `_POS_` dans leur nom sont téléchargés.

### Exemples de filtrage

- **Pattern par défaut** : `["_POS_"]` - Télécharge uniquement les fichiers contenant "_POS_" dans leur nom
- **Tous les fichiers** : `[]` - Télécharge tous les fichiers disponibles
- **Patterns multiples** : `["_POS_", "_EMP_"]` - Télécharge les fichiers contenant "_POS_" ou "_EMP_"

### Fichiers ignorés

Les fichiers qui ne correspondent à aucun pattern sont marqués comme "ignorés" dans les statistiques de téléchargement.
