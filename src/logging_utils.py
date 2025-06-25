#!/usr/bin/env python3
"""
Utilitaires de configuration du logging

Cette classe fournit des méthodes statiques pour configurer le logging
de manière cohérente dans toute l'application.

Auteur: Hugues Le Gendre
Date: 2024
"""

import logging
from typing import Optional


class LoggingUtils:
    """
    Classe utilitaire statique pour la configuration du logging.

    Fournit des méthodes pour configurer le logging de manière cohérente
    dans toute l'application.
    """

    @staticmethod
    def get_default_formatter() -> logging.Formatter:
        """
        Retourne le formateur par défaut utilisé dans l'application.

        Returns:
            logging.Formatter: Formateur par défaut
        """
        return logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    @staticmethod
    def setup_logger(
        name: str, formatter: Optional[logging.Formatter] = get_default_formatter()
    ) -> logging.Logger:
        """
        Configure et retourne un logger avec les paramètres spécifiés.

        Args:
            name (str): Nom du logger
            formatter (logging.Formatter, optional): Formateur personnalisé

        Returns:
            logging.Logger: Logger configuré
        """
        logger = logging.getLogger(name)

        # Éviter d'ajouter plusieurs handlers si le logger existe déjà
        if logger.handlers:
            return logger

        # Gestionnaire console
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        return logger

    @staticmethod
    def setup_simple_logger(name: str) -> logging.Logger:
        """
        Configure un logger simple avec le formateur par défaut.

        Args:
            name (str): Nom du logger

        Returns:
            logging.Logger: Logger configuré
        """
        return LoggingUtils.setup_logger(name, LoggingUtils.get_default_formatter())
