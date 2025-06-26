#!/usr/bin/env python3
"""
Téléchargeur de fichiers des séances du Conseil d'État VD

Ce script permet de télécharger automatiquement les fichiers des séances du Conseil d'État
du canton de Vaud qui sont valident certains critères.

Auteur: Hugues Le Gendre
Date: 2024
"""

import os
from enum import Enum
from typing import TypedDict

from ..config import FILE_PATTERNS, OUTPUT_FOLDER
from ..utils.logging import LoggingUtils
from ..utils.web_fetcher import WebFetcher
from .storage import Seance, SeanceFichier, Storage

FileDownloaderResult = TypedDict("FileDownloaderResult", {"nb_downloaded": int, "nb_error": int, "nb_ignored": int, "nb_existing": int})

class FileDownloadStatus(Enum):
    TO_DOWNLOAD = "TO_DOWNLOAD"
    DOWNLOADED = "DOWNLOADED"
    IGNORED = "IGNORED"
    EXISTING = "EXISTING"
    ERROR = "ERROR"


def _is_file_to_download(file: SeanceFichier) -> FileDownloadStatus:
    """
    Vérifie si un fichier doit être téléchargé.
    On teste son nom et s'il a déjà été téléchargé.

    Args:
        filename (str): Nom du fichier à vérifier

    Returns:
        bool: True si le fichier doit être téléchargé, False sinon
    """
    if not file or not file["alias"] or not file["nom"]:
        return FileDownloadStatus.ERROR
    if os.path.exists(os.path.join(OUTPUT_FOLDER, file["alias"])):
        return FileDownloadStatus.EXISTING
    for pattern in FILE_PATTERNS:
        if pattern in file["nom"]:
            return FileDownloadStatus.TO_DOWNLOAD
    return FileDownloadStatus.IGNORED


class FileDownloader:
    def __init__(self, storage: Storage):
        """
        Initialise le téléchargeur de fichiers.
        Spécifique aux pages des séances du Conseil d'État VD.ch.

        Args:
            storage: Objet de stockage
        """
        self.logger = LoggingUtils.setup_simple_logger("TéléchargeurFichiers")
        self.storage = storage

        self.logger.info(f"Téléchargeur de fichiers initialisé avec BDD : {self.storage.get_file_path()}")

    def download_files_of_seance(self, seance: Seance) -> FileDownloaderResult:
        """
        Télécharge les fichiers d'une séance.

        Args:
            seance: Séance à extraire

        Returns:
            True si l'extraction a réussi, False sinon
        """
        all_files = [file for discussion in seance["discussions"] for file in discussion["fichiers"]]

        nb_downloaded = 0
        nb_error = 0
        nb_ignored = 0
        nb_existing = 0

        for file in all_files:
            status = _is_file_to_download(file)
            match status:
                case FileDownloadStatus.TO_DOWNLOAD:
                    if WebFetcher().download_file(file["url"], os.path.join(OUTPUT_FOLDER, file["alias"])):
                        self.logger.info(f"Téléchargement de '{file['nom']}' vers '{file['alias']}' réussi")
                        nb_downloaded += 1
                    else:
                        self.logger.error(f"Erreur lors du téléchargement de '{file['nom']}' vers '{file['alias']}'")
                        nb_error += 1
                case FileDownloadStatus.ERROR:
                    self.logger.error(f"Erreur lors de la vérification du fichier '{file['nom']}'")
                    nb_error += 1
                case FileDownloadStatus.IGNORED:
                    self.logger.debug(f"Fichier '{file['nom']}' ignoré par nom")
                    nb_ignored += 1
                case FileDownloadStatus.EXISTING:
                    self.logger.debug(f"Fichier '{file['nom']}' déjà téléchargé vers '{file['alias']}'")
                    nb_existing += 1
                case _:
                    raise ValueError(f"Statut inconnu pour le fichier '{file['nom']}': {status}")

        return {
            "nb_downloaded": nb_downloaded,
            "nb_error": nb_error,
            "nb_ignored": nb_ignored,
            "nb_existing": nb_existing,
        }

    def download_all_files(self) -> FileDownloaderResult:
        """
        Télécharge tous les fichiers des séances.

        Returns:
            FileDownloaderResult: Résultat du téléchargement
        """
        all_seances = self.storage.seances_get()

        nb_downloaded = 0
        nb_error = 0
        nb_ignored = 0
        nb_existing = 0

        for seance in all_seances:
            result = self.download_files_of_seance(seance)
            nb_downloaded += result["nb_downloaded"]
            nb_error += result["nb_error"]
            nb_ignored += result["nb_ignored"]
            nb_existing += result["nb_existing"]

        return {
            "nb_downloaded": nb_downloaded,
            "nb_error": nb_error,
            "nb_ignored": nb_ignored,
            "nb_existing": nb_existing,
        }
