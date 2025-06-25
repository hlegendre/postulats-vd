#!/usr/bin/env python3
"""
Utilitaires pour le parsing de dates

Ce module contient des utilitaires pour parser différents formats de dates,
notamment les dates françaises utilisées dans les séances du Conseil d'État.
"""

import re
from datetime import datetime
from typing import Optional


class DateParser:
    """Classe utilitaire pour parser différents formats de dates."""

    # Mapping des mois français vers les numéros
    MOIS_MAPPING = {
        "janvier": 1,
        "février": 2,
        "mars": 3,
        "avril": 4,
        "mai": 5,
        "juin": 6,
        "juillet": 7,
        "août": 8,
        "septembre": 9,
        "octobre": 10,
        "novembre": 11,
        "décembre": 12,
    }

    @classmethod
    def parse_french_date(cls, date_str: str) -> datetime:
        """
        Parse une date française en objet datetime.

        Args:
            date_str (str): Date au format français (ex: "18 juin 2025")

        Returns:
            datetime: Objet datetime correspondant

        Raises:
            ValueError: Si le format de date n'est pas reconnu ou si le mois est invalide
        """
        # Pattern pour extraire jour, mois et année
        pattern = r"(\d{1,2})\s+(\w+)\s+(\d{4})"
        match = re.search(pattern, date_str.lower())

        if match:
            jour = int(match.group(1))
            mois_nom = match.group(2)
            annee = int(match.group(3))

            if mois_nom in cls.MOIS_MAPPING:
                mois = cls.MOIS_MAPPING[mois_nom]
                return datetime(annee, mois, jour)
            else:
                raise ValueError(f"Mois non reconnu: {mois_nom}")
        else:
            raise ValueError(f"Format de date non reconnu: {date_str}")

    @classmethod
    def parse_french_date_safe(cls, date_str: str) -> Optional[datetime]:
        """
        Parse une date française en objet datetime de manière sécurisée.
        Retourne None si le parsing échoue.

        Args:
            date_str (str): Date au format français (ex: "18 juin 2025")

        Returns:
            Optional[datetime]: Objet datetime correspondant ou None si échec
        """
        try:
            return cls.parse_french_date(date_str)
        except ValueError:
            return None
