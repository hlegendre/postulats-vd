#!/usr/bin/env python3
"""
Extracteur de Contenu des Séances du Conseil d'État VD

Ce script permet d'extraire automatiquement le contenu détaillé des séances du Conseil d'État
du canton de Vaud depuis les pages individuelles des séances.

Auteur: Hugues Le Gendre
Date: 2024
"""

from typing import List, TypedDict

from bs4 import BeautifulSoup


from .storage import Storage, Seance, SeancePartie
from ..utils.logging import LoggingUtils
from ..utils.web_fetcher import WebFetcher


def _parse_discussion(soup: BeautifulSoup, seance: Seance, id_discussion: int) -> SeancePartie:
    h2 = soup.select_one("h2.heading")
    if not h2:
        print("error: no h2 found")
        return None

    return {
        "titre": h2.get_text(strip=True),
        "fichiers": [
            {
                "url": file.get("href"),
                "nom": file.get_text(strip=True),
                "alias": seance["date"].replace("-", "")
                + "_"
                + str(id_discussion + 1)
                + "_"
                + str(id_file + 1)
                + ".pdf",
            }
            for id_file, file in enumerate(soup.find_all("a", href=True))
            if file.get("href").startswith("https://sieldocs.vd.ch/ecm/app18/service/siel/getContent?ID=")
        ],
    }


def _parse_seance(soup: BeautifulSoup, seance: Seance) -> List[SeancePartie]:
    """
    Extrait toutes les discussions d'une séance

    Args:
        soup: l'objet BeautifulSoup de la page de la séance

    Returns:
        Liste de discussions
    """
    parts = soup.select("#main .col-md-12.pl-0.pr-0")

    return [_parse_discussion(part, seance, id_discussion) for id_discussion, part in enumerate(parts)]


class SessionExtractorResult(TypedDict):
    success: bool
    nb_extracted: int
    nb_error: int
    nb_ignored: int


class SessionExtractor:
    def __init__(self, storage: Storage):
        """
        Initialize the session extractor.
        Bespoke to VD.ch Council of State session pages.

        Args:
            output_folder: Output folder path
        """
        self.logger = LoggingUtils.setup_simple_logger("ExtracteurSession")
        self.storage = storage

        self.logger.info(f"Extracteur de contenu initialisé avec le fichier de sortie : {self.storage.get_file_path()}")
        self.logger.info(f"Séances existantes chargées : {self.storage.seances_count()}")

    def extract_seance(self, seance: Seance) -> bool:
        """
        Extrait le contenu d'une séance.
        La base de donnée est mise à jour à la volée.

        Args:
            seance: Séance à extraire

        Returns:
            True si l'extraction a réussi, False sinon
        """
        html_content = WebFetcher().html_string(seance["url"])
        if not html_content:
            self.logger.error(f"Impossible de récupérer le contenu de la séance : {seance['url']}")
            return False

        try:
            soup = BeautifulSoup(html_content, "html.parser")
            seance["discussions"] = _parse_seance(soup, seance)

            self.storage.seance_upsert(seance)
            self.logger.info(f"Séance \"{seance["date"]}\" extraite : {len(seance['discussions'])} discussions")
            return True
        except Exception as e:
            self.logger.error(f"Erreur lors de l'extraction de la séance {seance['date']}: {e}")
            return False

    def extract_all_seances(self) -> SessionExtractorResult:
        """
        Extrait le contenu de toutes les séances non traitées encore.

        Returns:
            int: Nombre de séances extraites
            int: Nombre de séances en erreur
            int: Nombre de séances déjà traitées
        """
        all_seances = self.storage.seances_get()
        todo_seances = list(filter(lambda s: len(s.get("discussions", [])) == 0, all_seances))

        nb_extracted = 0
        nb_error = 0

        for seance in todo_seances:
            if self.extract_seance(seance):
                nb_extracted += 1
            else:
                nb_error += 1

        return {
            "success": nb_error == 0,
            "nb_extracted": nb_extracted,
            "nb_error": nb_error,
            "nb_ignored": len(all_seances) - nb_extracted - nb_error,
        }
