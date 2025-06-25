#!/usr/bin/env python3
"""
Test de la classe Storage

Ce script teste les fonctionnalités de base de la classe Storage.
"""

import tempfile
from pathlib import Path
from datetime import datetime
from postulats_vd.core.storage import Storage


def test_storage():
    """Test des fonctionnalités de base de Storage."""
    print("=== Test de Storage ===")

    # Créer un dossier temporaire pour les tests
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Initialiser le stockage
        storage = Storage(output_folder=str(temp_path))

        print(f"📁 Fichier de stockage : {storage.get_file_path()}")
        print(f"📊 Nombre de séances initial : {storage.seances_count()}")

        # Test 1: Vérifier qu'une séance n'existe pas
        test_date = "2025-01-15"
        print(f"\n🔍 Test 1: Vérifier si la séance existe")
        print(f"Date: {test_date}")
        existe = storage.seance_exists(test_date)
        print(f"Résultat: {existe}")

        # Test 2: Ajouter une nouvelle séance
        print(f"\n➕ Test 2: Ajouter une nouvelle séance")
        seance_details = {
            "url": "https://www.vd.ch/test-seance-1",
            "date": test_date,
            "date_originale": "15 janvier 2025",
            "date_decouverte": datetime.now().isoformat(),
            "titre": "Séance du Conseil d'Etat du 15 janvier 2025",
            "parties": [],
        }

        ajoutee = storage.seance_upsert(seance_details)
        print(f"Séance ajoutée: {ajoutee}")
        print(f"Nombre de séances après ajout: {storage.seances_count()}")

        # Test 3: Vérifier que la séance existe maintenant
        print(f"\n🔍 Test 3: Vérifier que la séance existe maintenant")
        existe = storage.seance_exists(test_date)
        print(f"Résultat: {existe}")

        # Test 4: Essayer d'ajouter la même séance (doit retourner False)
        print(f"\n🔄 Test 4: Essayer d'ajouter la même séance")
        ajoutee_encore = storage.seance_upsert(seance_details)
        print(f"Séance ajoutée à nouveau: {ajoutee_encore}")
        print(f"Nombre de séances: {storage.seances_count()}")

        # Test 5: Ajouter une deuxième séance
        print(f"\n➕ Test 5: Ajouter une deuxième séance")
        seance_details_2 = {
            "url": "https://www.vd.ch/test-seance-2",
            "date": "2025-01-22",
            "date_originale": "22 janvier 2025",
            "date_decouverte": datetime.now().isoformat(),
            "titre": "Séance du Conseil d'Etat du 22 janvier 2025",
            "parties": [],
        }

        ajoutee_2 = storage.seance_upsert(seance_details_2)
        print(f"Deuxième séance ajoutée: {ajoutee_2}")
        print(f"Nombre de séances: {storage.seances_count()}")

        # Test 6: Récupérer toutes les séances
        print(f"\n📋 Test 6: Récupérer toutes les séances")
        toutes_seances = storage.seances_get()
        print(f"Nombre de séances récupérées: {len(toutes_seances)}")
        for i, seance in enumerate(toutes_seances, 1):
            print(f"  {i}. {seance['date']} - {seance['titre']}")

        print(f"\n✅ Tests terminés avec succès!")
        print(f"📊 Total des séances stockées: {storage.seances_count()}")


if __name__ == "__main__":
    test_storage()
