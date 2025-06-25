# Téléchargeur de Séances du Conseil d'État VD

Ce script permet d'extraire automatiquement les informations détaillées des séances du Conseil d'État du canton de Vaud depuis le site officiel.

## Fonctionnalités

- **Extraction automatique** : Récupère les URLs, dates, titres et contenus détaillés des séances depuis le site officiel
- **Système de logging unifié** : Un seul fichier JSON récapitule toutes les séances
- **Détection des nouvelles séances** : Ignore automatiquement les séances déjà connues
- **Métadonnées de découverte** : Chaque séance inclut sa date de première découverte
- **Parsing des dates françaises** : Conversion automatique des dates françaises en format ISO
- **Pagination automatique** : Parcourt automatiquement toutes les pages disponibles
- **Arrêt conditionnel** : Possibilité de s'arrêter à une date limite configurée
- **Extraction des parties et fichiers** : Pour chaque séance, toutes les parties et fichiers associés sont extraits

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
      "parties": [
        {
          "titre": "Un nouveau bâtiment pour la Haute école pédagogique à Chavannes-près-Renens",
          "fichiers": [
            {
              "url": "https://sieldocs.vd.ch/ecm/app18/service/siel/getContent?ID=2310752",
              "nom": "EMPD accordant au Conseil d'État un crédit d'investissement..."
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
- `parties` : Liste des parties de la séance

### Champs des parties

- `titre` : Titre de la partie
- `fichiers` : Liste des fichiers associés à cette partie

### Champs des fichiers

- `url` : URL du fichier
- `nom` : Nom ou description du fichier

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

# Afficher l'aide
python run.py --help
```

### Options disponibles

- `-v, --verbose` : Niveau de verbosité
  - `-v` : Mode info (affiche les informations de base)
  - `-vv` : Mode debug (affiche tous les détails)
  - Par défaut : Mode silencieux

### Sortie

Le script affiche :

- Le nombre total de séances dans la base
- Le nombre de nouvelles séances trouvées
- Le chemin du fichier JSON
- Un résumé des nouvelles séances extraites

Exemple :

```
=== Découverte des Séances du Conseil d'État VD ===
✅ OK : nouvelles = 2 / totales = 10 (pages = 1)
=== Récupération des Séances du Conseil d'État VD ===
✅ OK : nouvelles = 2 / ignorées = 8 / en erreur = 0
```

Le fichier de sortie est : `output/storage.json`

## Qualité du Code

### Outils de qualité

Le projet utilise plusieurs outils pour maintenir la qualité du code :

- **Black** : Formateur de code automatique
- **Flake8** : Linter pour détecter les erreurs de style et de logique
- **Pre-commit hooks** : Vérifications automatiques avant chaque commit

### Installation des hooks pre-commit

Pour installer les hooks pre-commit automatiquement :

```bash
./setup.sh
```

Ou manuellement :

```bash
chmod +x .git/hooks/pre-commit
```

### Utilisation des outils de qualité

**Formater le code avec Black :**

```bash
uv run black .
```

**Vérifier le formatage sans modification :**

```bash
uv run black --check .
```

**Linter le code avec Flake8 :**

```bash
uv run flake8 .
```

**Tester manuellement le hook pre-commit :**

```bash
.git/hooks/pre-commit
```

### Comportement des hooks

Le hook pre-commit s'exécute automatiquement avant chaque commit et :

1. **Vérifie le formatage** : S'assure que le code respecte les standards Black
2. **Lance le linter** : Détecte les erreurs de style et de logique avec Flake8
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
- Extrait toutes les parties et fichiers associés à chaque séance

### Lancements suivants

- Charge les séances existantes depuis le fichier JSON
- Extrait les séances depuis le site web (avec pagination)
- Compare les URLs pour identifier les nouvelles séances
- Ajoute uniquement les nouvelles séances avec leur `date_decouverte`
- Met à jour le fichier JSON avec toutes les séances et leur contenu détaillé

### Avantages du système

1. **Pas de duplication** : Un seul fichier contient toutes les séances
2. **Traçabilité** : Chaque séance garde sa date de première découverte
3. **Efficacité** : Les séances déjà connues sont ignorées
4. **Historique** : Conservation de l'historique complet des découvertes
5. **Pagination automatique** : Parcourt toutes les pages sans intervention
6. **Arrêt intelligent** : S'arrête automatiquement à la date limite configurée
7. **Extraction complète** : Toutes les parties et fichiers sont extraits pour chaque séance

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
- L'extraction correcte des parties et fichiers

## Configuration

Le script utilise le fichier `settings.py` pour sa configuration :

- `OUTPUT_FOLDER` : Dossier de sortie pour les fichiers JSON (par défaut `output`)
- `MAX_SESSIONS` : Nombre maximum de pages à parcourir
- `STOP_DATE` : Date limite d'arrêt (format YYYY-MM-DD)
- `REQUEST_TIMEOUT` : Timeout des requêtes HTTP
- `PAGE_DELAY` : Délai entre les requêtes de pages

**Note** : Le niveau de verbosité est maintenant configuré via les arguments de ligne de commande (`-v`, `-vv`) et non plus dans le fichier de configuration.
