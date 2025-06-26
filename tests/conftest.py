"""
Shared pytest fixtures for the Postulats VD test suite.

This module contains common fixtures that can be used across all tests.
"""

import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_output_dir():
    """
    Create a temporary directory for test output files.

    Returns:
        Path: Path to the temporary directory
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def sample_seance_data():
    """
    Sample session data for testing.

    Returns:
        dict: Sample session data
    """
    return {
        "url": "https://www.vd.ch/test/sample-seance",
        "date": "2025-01-15",
        "date_originale": "15 janvier 2025",
        "titre": "Séance du Conseil d'Etat du 15 janvier 2025",
    }


@pytest.fixture
def sample_storage_data():
    """
    Sample storage data structure for testing.

    Returns:
        dict: Sample storage data structure
    """
    return {
        "metadonnees": {
            "url_source": "https://www.vd.ch/actualites/decisions-du-conseil-detat",
            "derniere_mise_a_jour": "2025-01-15T10:00:00",
            "total_seances": 1,
        },
        "seances": [
            {
                "url": "https://www.vd.ch/test/sample-seance",
                "date": "2025-01-15",
                "date_originale": "15 janvier 2025",
                "titre": "Séance du Conseil d'Etat du 15 janvier 2025",
                "date_decouverte": "2025-01-15T10:00:00",
            }
        ],
    }
