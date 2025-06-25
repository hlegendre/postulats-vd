"""
Postulats VD - Téléchargeur de Séances du Conseil d'État VD

Ce package permet d'extraire automatiquement les informations des séances
du Conseil d'État du canton de Vaud depuis le site officiel.
"""

__version__ = "1.0.0"
__author__ = "Hugues Le Gendre"
__email__ = "hugues@ikivox.org"

from .core.session_lister import SessionLister
from .core.storage import Storage

__all__ = ["SessionLister", "Storage"]
