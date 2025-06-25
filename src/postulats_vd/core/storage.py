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
from typing import Dict, List, Optional, Any
from ..utils.logging import LoggingUtils


class Storage:
    """
    Gestionnaire de stockage des données du projet.

    Cette classe fournit une interface claire pour :
    - Vérifier si une séance existe
    - Ajouter une nouvelle séance

    La classe sauvegarde automatiquement les données dans un fichier JSON.
    """

    def __init__(self, output_folder: str = "output", filename: str = "storage.json"):
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
        self._seances_cache = self._load_existing_seances()

        self.logger.debug(f"Storage initialisé avec le fichier : {self.storage_file}")
        self.logger.debug(f"Séances existantes chargées : {len(self._seances_cache)}")

    def _load_existing_seances(self) -> Dict[str, Dict[str, Any]]:
        """
        Charge les séances existantes depuis le fichier JSON.

        Returns:
            dict: Dictionnaire des séances existantes avec l'URL comme clé
        """
        if not self.storage_file.exists():
            self.logger.warning("Aucun fichier de stockage existant trouvé, il sera créé au premier ajout de données")
            return {}

        try:
            with open(self.storage_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                seances = data.get("seances", [])

                # Créer un dictionnaire avec l'URL comme clé pour un accès rapide
                existing_seances = {}
                for seance in seances:
                    existing_seances[seance["url"]] = seance

                return existing_seances

        except (json.JSONDecodeError, FileNotFoundError) as e:
            self.logger.warning(f"Erreur lors du chargement des séances existantes : {e}")
            return {}

    def seance_existe(self, url: str) -> bool:
        """
        Vérifie si une séance existe déjà.

        Args:
            url (str): URL de la séance à vérifier

        Returns:
            bool: True si la séance existe, False sinon
        """
        return url in self._seances_cache

    def seance_ajoute(self, details: Dict[str, Any], date_decouverte: str) -> bool:
        """
        Ajoute une nouvelle séance si elle n'existe pas déjà.

        Args:
            details (dict): Détails de la séance (url, date, titre, etc.)
            date_decouverte (str): Date de découverte de la séance

        Returns:
            bool: True si la séance a été ajoutée, False si elle existait déjà
        """
        url = details.get("url")
        if not url:
            self.logger.error("URL manquante dans les détails de la séance")
            return False

        if self.seance_existe(url):
            self.logger.debug(f"Séance déjà existante ignorée : {url}")
            return False

        # Ajouter la date de découverte
        seance_complete = details.copy()
        seance_complete["date_decouverte"] = date_decouverte

        # Ajouter au cache
        self._seances_cache[url] = seance_complete

        # Sauvegarder immédiatement
        self._save_to_file()

        self.logger.debug(
            f"Nouvelle séance sauvegardée : {seance_complete.get('date', 'N/A')} - {seance_complete.get('titre', 'N/A')}"
        )
        return True

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

            self.logger.debug(f"Fichier sauvegardé : {self.storage_file} ({len(seances_sorted)} séances)")

        except Exception as e:
            self.logger.error(f"Erreur lors de la sauvegarde : {e}")
            raise

    def get_all_seances(self) -> List[Dict[str, Any]]:
        """
        Récupère toutes les séances stockées.

        Returns:
            list: Liste de toutes les séances
        """
        return list(self._seances_cache.values())

    def get_seance_count(self) -> int:
        """
        Retourne le nombre total de séances stockées.

        Returns:
            int: Nombre de séances
        """
        return len(self._seances_cache)

    def get_seance_by_url(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Récupère une séance spécifique par son URL.

        Args:
            url (str): URL de la séance

        Returns:
            dict: Détails de la séance ou None si non trouvée
        """
        return self._seances_cache.get(url)

    def get_file_path(self) -> str:
        """
        Retourne le chemin du fichier de stockage.

        Returns:
            str: Chemin du fichier JSON
        """
        return str(self.storage_file)
