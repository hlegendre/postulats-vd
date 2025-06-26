#!/usr/bin/env python3
"""
Gestionnaire de stockage des données du projet

Cette classe gère la persistance des données dans un fichier JSON.
Initialement conçu pour les séances du Conseil d'État VD, mais extensible.

Auteur: Hugues Le Gendre
Date: 2024
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, TypedDict

from ..config import OUTPUT_FOLDER, STORAGE_FILENAME
from ..utils.logging import Logger, LoggingUtils

SeanceFichier = TypedDict("SeanceFichier", {"url": str, "nom": str, "alias": str})
def SeanceFichier_check_type(data: Any) -> bool:
    return (
        isinstance(data, dict)
        and "url" in data
        and isinstance(data["url"], str)
        and "nom" in data
        and isinstance(data["nom"], str)
        and "alias" in data
        and isinstance(data["alias"], str)
    )

SeancePartie = TypedDict("SeancePartie", {"titre": str, "fichiers": list[SeanceFichier]})
def SeancePartie_check_type(data: Any) -> bool:
    return (
        isinstance(data, dict)
        and "titre" in data
        and isinstance(data["titre"], str)
        and "fichiers" in data
        and isinstance(data["fichiers"], list)
        and all(SeanceFichier_check_type(fichier) for fichier in data["fichiers"])
    )

Seance = TypedDict("Seance", {"url": str, "date": str, "date_decouverte": str, "date_originale": str, "titre": str, "discussions": list[SeancePartie]})
def Seance_check_type(data: Any) -> bool:
    return (
        isinstance(data, dict)
        and "url" in data
        and isinstance(data["url"], str)
        and "date" in data
        and isinstance(data["date"], str)
        and "date_decouverte" in data
        and isinstance(data["date_decouverte"], str)
        and "date_originale" in data
        and isinstance(data["date_originale"], str)
        and "titre" in data
        and isinstance(data["titre"], str)
        and "discussions" in data
        and isinstance(data["discussions"], list)
        and all(SeancePartie_check_type(partie) for partie in data["discussions"])
    )

StorageMetadonnees = TypedDict("StorageMetadonnees", {"url_source": str, "derniere_mise_a_jour": str, "total_seances": int})
def StorageMetadonnees_check_type(data: Any) -> bool:
    return (
        isinstance(data, dict)
        and "url_source" in data
        and isinstance(data["url_source"], str)
        and "derniere_mise_a_jour" in data
        and isinstance(data["derniere_mise_a_jour"], str)
        and "total_seances" in data
        and isinstance(data["total_seances"], int)
    )

StorageData = TypedDict("StorageData", {"metadonnees": StorageMetadonnees, "seances": list[Seance]})
def StorageData_check_type(data: Any) -> bool:
    return (
        isinstance(data, dict)
        and "metadonnees" in data
        and StorageMetadonnees_check_type(data["metadonnees"])
        and "seances" in data
        and isinstance(data["seances"], list)
        and all(Seance_check_type(seance) for seance in data["seances"])
    )

def StorageData_load_from_json(data: Any) -> Optional["StorageData"]:
    storage_data = json.loads(data)
    if not StorageData_check_type(storage_data):
        LoggingUtils.setup_simple_logger("Storage").error(f"Données JSON invalides : {storage_data}")
        return None
    return storage_data


class Storage:
    """
    Gestionnaire de stockage des données du projet.

    Cette classe fournit une interface claire pour :
    - Vérifier si une séance a déjà été découverte
    - Ajouter ou mettre à jour une séance

    La classe sauvegarde automatiquement les données dans un fichier JSON.
    """

    output_folder: Path
    filename: str
    storage_file: Path
    logger: Logger
    _seances_cache: Dict[str, Seance]

    def __init__(self, output_folder: str = OUTPUT_FOLDER, filename: str = STORAGE_FILENAME):
        """
        Initialise le gestionnaire de stockage.

        Args:
            output_folder (str): Dossier de sortie pour les fichiers
            filename (str): Nom du fichier JSON
        """
        self.output_folder = Path(output_folder)
        self.filename = filename
        self.storage_file = self.output_folder / filename

        # Configuration de la journalisation
        self.logger = LoggingUtils.setup_simple_logger("Storage")

        # Créer le dossier de sortie s'il n'existe pas
        self.output_folder.mkdir(parents=True, exist_ok=True)

        # Charger les séances existantes
        self._seances_cache: Dict[str, Seance] = self._load()

        self.logger.debug(f"Storage initialisé avec le fichier : {self.storage_file}")
        self.logger.debug(f"Séances existantes chargées : {len(self._seances_cache)}")

    def _load(self) -> Dict[str, Seance]:
        """
        Charge les séances existantes depuis le fichier JSON.

        Returns:
            dict: Dictionnaire des séances existantes avec la date comme clé
        """
        if not self.storage_file.exists():
            self.logger.warning("Aucun fichier de stockage existant trouvé, il sera créé au premier ajout de données")
            return {}

        try:
            with open(self.storage_file, "r", encoding="utf-8") as f:
                data = StorageData_load_from_json(f.read())
                return {seance["date"]: seance for seance in data["seances"] } if data is not None else {}

        except (ValueError, json.JSONDecodeError, FileNotFoundError) as e:
            self.logger.warning(f"Erreur lors du chargement de la base de données : {e}")
            return {}

    def _save_to_file(self):
        """
        Sauvegarde toutes les séances dans le fichier JSON.
        """
        # Trier les séances par date (plus récentes en premier)
        seances_sorted = sorted(self._seances_cache.values(), key=lambda x: x.get("date", ""), reverse=True)

        data = {
            "metadonnees": {
                "url_source": "https://www.vd.ch/actualites/decisions-du-conseil-detat",
                "derniere_mise_a_jour": datetime.now().isoformat(),
                "total_seances": len(seances_sorted),
            },
            "seances": seances_sorted,
        }

        try:
            with open(self.storage_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.logger.debug(f"Base de données sauvegardée : {self.storage_file} ({len(seances_sorted)} éléments)")

        except Exception as e:
            self.logger.error(f"Erreur lors de la sauvegarde de la base de données : {e}")
            raise

    def seance_exists(self, date: str) -> bool:
        """
        Vérifie si une séance existe déjà

        Args:
            date (str): Date de la séance à vérifier (format: "YYYY-MM-DD")

        Returns:
            bool: True si la séance existe, False sinon
        """
        return date in self._seances_cache

    def seance_upsert(self, seance: Seance) -> bool:
        """
        Ajoute une nouvelle séance ou met à jour une séance existante.

        Args:
            seance (Seance): La séance à ajouter ou mettre à jour

        Returns:
            bool: True si la séance a été ajoutée, False si elle a été modifiée
        """
        exists = self.seance_exists(seance["date"])
        self._seances_cache[seance["date"]] = seance
        self._save_to_file()

        if exists:
            self.logger.debug(f"Séance modifiée : {seance['date']} - {seance['titre']}")
            return False
        else:
            self.logger.debug(f"Séance créée : {seance['date']} - {seance['titre']}")
            return True

    def seances_get(self) -> List[Seance]:
        """
        Récupère toutes les séances stockées.

        Returns:
            list: Liste de toutes les séances
        """
        return list(self._seances_cache.values())

    def seances_count(self) -> int:
        """
        Retourne le nombre total de séances stockées.

        Returns:
            int: Nombre de séances
        """
        return len(self._seances_cache)

    def get_file_path(self) -> str:
        """
        Retourne le chemin du fichier de stockage.

        Returns:
            str: Chemin du fichier JSON
        """
        return str(self.storage_file)
