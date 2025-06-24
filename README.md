# Téléchargeur de Séances du Conseil d'État VD

Ce script permet d'extraire automatiquement les informations des séances du Conseil d'État du canton de Vaud depuis le site officiel.

## Fonctionnalités

- **Extraction automatique** : Récupère les URLs et dates des séances depuis le site officiel
- **Système de logging unifié** : Un seul fichier JSON récapitule toutes les séances
- **Détection des nouvelles séances** : Ignore automatiquement les séances déjà connues
- **Métadonnées de découverte** : Chaque séance inclut sa date de première découverte
- **Parsing des dates françaises** : Conversion automatique des dates françaises en format ISO
- **Pagination automatique** : Parcourt automatiquement toutes les pages disponibles
- **Arrêt conditionnel** : Possibilité de s'arrêter à une date limite configurée

## Structure du fichier JSON

Le script génère un fichier unique `seances_conseil_etat.json` avec la structure suivante :

```json
{
  "metadonnees": {
    "url_source": "https://www.vd.ch/actualites/decisions-du-conseil-detat",
    "derniere_mise_a_jour": "2025-06-24T18:04:18.487168",
    "total_seances": 45
  },
  "seances": [
    {
      "url": "https://www.vd.ch/actualites/decisions-du-conseil-detat/seance-du-conseil-detat/seance/1029290",
      "date": "2025-06-18",
      "date_originale": "18 juin 2025",
      "titre": "Séance du Conseil d'Etat du 18 juin 2025",
      "date_decouverte": "2025-06-24T17:41:52.624964"
    }
  ]
}
```

### Champs des séances

- `url` : URL complète de la page de la séance
- `date` : Date au format ISO (YYYY-MM-DD)
- `date_originale` : Date originale en français
- `titre` : Titre de la séance
- `date_decouverte` : Date et heure de première découverte de cette séance

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
python downloader.py
```

### Sortie

Le script affiche :

- Le nombre total de séances dans la base
- Le nombre de nouvelles séances trouvées
- Le chemin du fichier JSON
- La liste des nouvelles séances (si applicable)

Exemple :

```
=== Téléchargeur de Séances du Conseil d'État VD ===
URL cible : https://www.vd.ch/actualites/decisions-du-conseil-detat
Dossier de sortie : seances
Fichier de séances : seances/seances_conseil_etat.json
Date limite d'arrêt : 2024-05-14
Nombre maximum de pages : 50
Délai entre les pages : 1 seconde(s)

✅ Extraction réussie !
📊 Total des séances : 45
🆕 Nouvelles séances ajoutées : 0
📄 Pages traitées : 3
📁 Fichier JSON : seances/seances_conseil_etat.json

ℹ️  Aucune nouvelle séance ajoutée
```

## Comportement

### Premier lancement

- Crée le fichier `seances_conseil_etat.json`
- Extrait toutes les séances disponibles depuis toutes les pages
- Ajoute la métadonnée `date_decouverte` à chaque séance

### Lancements suivants

- Charge les séances existantes depuis le fichier JSON
- Extrait les séances depuis le site web (avec pagination)
- Compare les URLs pour identifier les nouvelles séances
- Ajoute uniquement les nouvelles séances avec leur `date_decouverte`
- Met à jour le fichier JSON avec toutes les séances

### Avantages du nouveau système

1. **Pas de duplication** : Un seul fichier contient toutes les séances
2. **Traçabilité** : Chaque séance garde sa date de première découverte
3. **Efficacité** : Les séances déjà connues sont ignorées
4. **Historique** : Conservation de l'historique complet des découvertes
5. **Pagination automatique** : Parcourt toutes les pages sans intervention
6. **Arrêt intelligent** : S'arrête automatiquement à la date limite configurée

## Tests

Exécuter les tests :

```bash
python test_downloader.py
```

Les tests vérifient :

- La création initiale du fichier JSON
- L'ignorance des séances déjà connues
- La détection des nouvelles séances
- La conservation des métadonnées de découverte

## Configuration

Le script utilise le fichier `config.py` pour la configuration :

- `TARGET_URL` : URL de la page des décisions du Conseil d'État
- `OUTPUT_FOLDER` : Dossier de sortie pour les fichiers JSON
- `USER_AGENT` : User-Agent pour les requêtes HTTP
- `REQUEST_TIMEOUT` : Timeout des requêtes HTTP
- `MAX_PAGES` : Nombre maximum de pages à parcourir
- `PAGE_DELAY` : Délai entre les requêtes de pages
- `STOP_DATE` : Date limite d'arrêt (format YYYY-MM-DD)
