#!/usr/bin/env python3
"""
Tests pour le Téléchargeur de Séances du Conseil d'État VD

Ce module contient les tests unitaires pour vérifier le bon fonctionnement
du téléchargeur de séances.
"""

import json
import tempfile
from pathlib import Path
from datetime import datetime
from postulats_vd.core.sessionfinder import CESessionFinder


def test_single_file_logging():
    """Test du nouveau système de logging avec un seul fichier JSON."""

    # Créer un dossier temporaire pour les tests
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        print("=== Test du système de logging avec un seul fichier JSON ===")
        print(f"Dossier temporaire : {temp_path}")
        print()

        # Premier lancement - devrait créer le fichier et ajouter toutes les séances
        print("1. Premier lancement...")
        downloader1 = CESessionFinder(output_folder=str(temp_path))
        result1 = downloader1.scrape_seances()

        assert result1["success"], f"Échec du premier lancement : {result1.get('error', 'Erreur inconnue')}"
        print(f"   ✅ Succès : {result1['stored_seances']} séances totales, {result1['new_seances_count']} nouvelles")

        # Vérifier que le fichier existe
        seances_file = temp_path / "storage.json"
        assert seances_file.exists(), "Le fichier storage.json n'a pas été créé"
        print(f"   📁 Fichier créé : {seances_file}")

        # Vérifier le contenu
        with open(seances_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            assert "seances" in data, "Le fichier storage.json doit contenir une clé 'seances'"
            seances = data.get("seances", [])
            assert isinstance(seances, list), "La valeur de 'seances' doit être une liste"
            assert len(seances) > 0, "Aucune séance trouvée dans le fichier"
            print(f"   📊 {len(seances)} séances dans le fichier")

            # Vérifier que toutes les séances ont une date de découverte
            seances_with_discovery = [s for s in seances if "date_decouverte" in s]
            assert len(seances_with_discovery) == len(
                seances
            ), "Toutes les séances doivent avoir une date de découverte"
            print(f"   🕒 {len(seances_with_discovery)} séances avec date de découverte")

        print()

        # Deuxième lancement - devrait ignorer les séances existantes
        print("2. Deuxième lancement (même données)...")
        downloader2 = CESessionFinder(output_folder=str(temp_path))
        result2 = downloader2.scrape_seances()

        assert result2["success"], f"Échec du deuxième lancement : {result2.get('error', 'Erreur inconnue')}"
        assert result2["stored_seances"] == result1["stored_seances"], "Le nombre de séances stockées doit être le même"
        assert result2["new_seances_count"] == 0, "Aucune nouvelle séance doit être ajoutée"
        print(f"   ✅ Succès : {result2['stored_seances']} séances totales, {result2['new_seances_count']} nouvelles")

        print()

        # Test avec ajout manuel d'une nouvelle séance
        print("3. Test avec ajout manuel d'une nouvelle séance...")

        # Lire le fichier existant
        with open(seances_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            assert "seances" in data, "Le fichier storage.json doit contenir une clé 'seances'"
            seances = data.get("seances", [])
            assert isinstance(seances, list), "La valeur de 'seances' doit être une liste"
            assert len(seances) > 0, "Aucune séance trouvée dans le fichier"

        # Ajouter une nouvelle séance manuellement
        new_seance = {
            "url": "https://www.vd.ch/test/nouvelle-seance",
            "date": "2025-06-25",
            "date_originale": "25 juin 2025",
            "titre": "Séance du Conseil d'Etat du 25 juin 2025",
            "date_decouverte": datetime.now().isoformat(),
        }
        seances.append(new_seance)

        # Sauvegarder le fichier modifié
        data["seances"] = seances
        data["metadonnees"]["stored_seances"] = len(seances)
        data["metadonnees"]["derniere_mise_a_jour"] = datetime.now().isoformat()

        with open(seances_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"   📝 Nouvelle séance ajoutée manuellement")

        # Troisième lancement - devrait détecter la nouvelle séance
        print("4. Troisième lancement (après ajout manuel)...")
        downloader3 = CESessionFinder(output_folder=str(temp_path))
        result3 = downloader3.scrape_seances()

        assert result3["success"], f"Échec du troisième lancement : {result3.get('error', 'Erreur inconnue')}"
        assert (
            result3["stored_seances"] == result1["stored_seances"] + 1
        ), "Le nombre de séances stockées doit avoir augmenté de 1"
        assert result3["new_seances_count"] == 0, "Aucune nouvelle séance doit être ajoutée"
        print(f"   ✅ Succès : {result3['stored_seances']} séances totales, {result3['new_seances_count']} nouvelles")

        print()
        print("=== Test terminé avec succès ===")


if __name__ == "__main__":
    success = test_single_file_logging()
    if success:
        print("🎉 Tous les tests ont réussi !")
    else:
        print("❌ Certains tests ont échoué.")
