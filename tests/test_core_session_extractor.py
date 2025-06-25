#!/usr/bin/env python3
"""
Tests pour l'Extracteur de Contenu des Séances du Conseil d'État VD

Ce module contient les tests unitaires pour vérifier le bon fonctionnement
de l'extracteur de contenu des séances.
"""

import tempfile
from pathlib import Path
from datetime import datetime
from unittest.mock import patch
from bs4 import BeautifulSoup

from postulats_vd.core.session_extractor import SessionExtractor, _parse_partie, _parse_seance
from postulats_vd.core.storage import Storage, Seance


def test_session_extractor_initialization():
    """Test de l'initialisation de l'extracteur de sessions."""

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        print("=== Test d'initialisation de l'extracteur de sessions ===")
        print(f"Dossier temporaire : {temp_path}")
        print()

        # Créer un storage et un extracteur
        storage = Storage(output_folder=str(temp_path))
        extractor = SessionExtractor(storage)

        # Vérifier que l'extracteur a été initialisé correctement
        assert extractor.storage is not None, "Le storage n'a pas été initialisé"
        assert extractor.html_fetcher is not None, "Le html_fetcher n'a pas été initialisé"
        assert extractor.logger is not None, "Le logger n'a pas été initialisé"

        print("   ✅ Extracteur initialisé correctement")
        print()


def test_parse_partie_with_valid_data():
    """Test de l'extraction d'une partie avec des données valides."""

    print("=== Test d'extraction d'une partie avec des données valides ===")
    print()

    # Créer un HTML de test avec une partie valide
    test_html = """
    <div>
        <h2 class="heading">Titre de la partie</h2>
        <a href="https://sieldocs.vd.ch/ecm/app18/service/siel/getContent?ID=123">Document 1</a>
        <a href="https://sieldocs.vd.ch/ecm/app18/service/siel/getContent?ID=456">Document 2</a>
        <a href="/autre/lien">Lien ignoré</a>
    </div>
    """

    soup = BeautifulSoup(test_html, "html.parser")
    partie = _parse_partie(soup)

    # Vérifier que la partie a été extraite correctement
    assert partie is not None, "La partie devrait être extraite"
    assert partie["titre"] == "Titre de la partie", "Le titre devrait être correct"
    assert len(partie["fichiers"]) == 2, "Deux fichiers devraient être trouvés"

    # Vérifier les URLs des fichiers
    file_urls = [f["url"] for f in partie["fichiers"]]
    expected_urls = [
        "https://sieldocs.vd.ch/ecm/app18/service/siel/getContent?ID=123",
        "https://sieldocs.vd.ch/ecm/app18/service/siel/getContent?ID=456",
    ]
    for expected_url in expected_urls:
        assert expected_url in file_urls, f"URL attendue manquante : {expected_url}"

    print("   ✅ Partie extraite correctement")
    print()


def test_parse_partie_without_h2():
    """Test de l'extraction d'une partie sans titre h2."""

    print("=== Test d'extraction d'une partie sans titre h2 ===")
    print()

    # Créer un HTML de test sans h2
    test_html = """
    <div>
        <h3>Titre incorrect</h3>
        <a href="https://sieldocs.vd.ch/ecm/app18/service/siel/getContent?ID=123">Document 1</a>
    </div>
    """

    soup = BeautifulSoup(test_html, "html.parser")
    partie = _parse_partie(soup)

    # Vérifier que la partie n'est pas extraite
    assert partie is None, "La partie ne devrait pas être extraite sans h2"

    print("   ✅ Partie ignorée correctement (pas de h2)")
    print()


def test_parse_seance_with_multiple_parts():
    """Test de l'extraction d'une séance avec plusieurs parties."""

    print("=== Test d'extraction d'une séance avec plusieurs parties ===")
    print()

    # Créer un HTML de test avec plusieurs parties
    test_html = """
    <div id="main">
        <div class="col-md-12 pl-0 pr-0">
            <h2 class="heading">Partie 1</h2>
            <a href="https://sieldocs.vd.ch/ecm/app18/service/siel/getContent?ID=123">Document 1</a>
        </div>
        <div class="col-md-12 pl-0 pr-0">
            <h2 class="heading">Partie 2</h2>
            <a href="https://sieldocs.vd.ch/ecm/app18/service/siel/getContent?ID=456">Document 2</a>
            <a href="https://sieldocs.vd.ch/ecm/app18/service/siel/getContent?ID=789">Document 3</a>
        </div>
    </div>
    """

    soup = BeautifulSoup(test_html, "html.parser")
    parties = _parse_seance(soup)

    # Vérifier que toutes les parties ont été extraites
    assert len(parties) == 2, "Deux parties devraient être extraites"

    # Vérifier la première partie
    assert parties[0]["titre"] == "Partie 1", "Le titre de la première partie devrait être correct"
    assert len(parties[0]["fichiers"]) == 1, "La première partie devrait avoir 1 fichier"

    # Vérifier la deuxième partie
    assert parties[1]["titre"] == "Partie 2", "Le titre de la deuxième partie devrait être correct"
    assert len(parties[1]["fichiers"]) == 2, "La deuxième partie devrait avoir 2 fichiers"

    print("   ✅ Séance avec plusieurs parties extraite correctement")
    print()


def test_extract_seance_success():
    """Test de l'extraction réussie d'une séance."""

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        print("=== Test d'extraction réussie d'une séance ===")
        print(f"Dossier temporaire : {temp_path}")
        print()

        # Créer un storage et un extracteur
        storage = Storage(output_folder=str(temp_path))
        extractor = SessionExtractor(storage)

        # Créer une séance de test
        test_seance: Seance = {
            "url": "https://www.vd.ch/test/seance",
            "date": "2025-01-01",
            "date_originale": "1er janvier 2025",
            "date_decouverte": datetime.now().isoformat(),
            "titre": "Séance du Conseil d'Etat du 1er janvier 2025",
            "parties": [],
        }

        # Mock du HTML fetcher pour retourner du contenu valide
        test_html = """
        <div id="main">
            <div class="col-md-12 pl-0 pr-0">
                <h2 class="heading">Partie 1</h2>
                <a href="https://sieldocs.vd.ch/ecm/app18/service/siel/getContent?ID=123">Document 1</a>
            </div>
        </div>
        """

        with patch.object(extractor.html_fetcher, "string", return_value=test_html):
            success = extractor.extract_seance(test_seance)

        # Vérifier que l'extraction a réussi
        assert success, "L'extraction de la séance devrait réussir"
        assert len(test_seance["parties"]) == 1, "La séance devrait avoir 1 partie"
        assert test_seance["parties"][0]["titre"] == "Partie 1", "Le titre de la partie devrait être correct"

        # Vérifier que la séance a été sauvegardée dans le storage
        saved_seance = storage.seances_get()[0]
        assert saved_seance["date"] == "2025-01-01", "La séance devrait être sauvegardée"

        print("   ✅ Séance extraite et sauvegardée correctement")
        print()


def test_extract_all_seances_empty():
    """Test de l'extraction de toutes les séances (cas vide)."""

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        print("=== Test d'extraction de toutes les séances (cas vide) ===")
        print(f"Dossier temporaire : {temp_path}")
        print()

        # Créer un storage et un extracteur
        storage = Storage(output_folder=str(temp_path))
        extractor = SessionExtractor(storage)

        # Tester avec aucune séance
        result = extractor.extract_all_seances()

        # Vérifier le résultat
        assert result["success"], "L'extraction devrait réussir même sans séances"
        assert result["nb_extracted"] == 0, "Aucune séance ne devrait être extraite"
        assert result["nb_error"] == 0, "Aucune erreur ne devrait survenir"
        assert result["nb_ignored"] == 0, "Aucune séance ne devrait être ignorée"

        print("   ✅ Aucune séance à traiter (comportement attendu)")
        print()


if __name__ == "__main__":
    print("🧪 Démarrage des tests de l'extracteur de sessions...")
    print()

    try:
        test_session_extractor_initialization()
        test_parse_partie_with_valid_data()
        test_parse_partie_without_h2()
        test_parse_seance_with_multiple_parts()
        test_extract_seance_success()
        test_extract_all_seances_empty()

        print("🎉 Tous les tests de l'extracteur de sessions ont réussi !")

    except Exception as e:
        print(f"❌ Erreur lors des tests : {e}")
        raise
