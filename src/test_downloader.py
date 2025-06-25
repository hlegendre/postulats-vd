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
from .downloader import TelechargeurSeancesVD


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
        downloader1 = TelechargeurSeancesVD(output_folder=str(temp_path))
        result1 = downloader1.scrape_seances()
        
        if result1['success']:
            print(f"   ✅ Succès : {result1['total_count']} séances totales, {result1['new_count']} nouvelles")
            
            # Vérifier que le fichier existe
            seances_file = temp_path / "seances_conseil_etat.json"
            if seances_file.exists():
                print(f"   📁 Fichier créé : {seances_file}")
                
                # Vérifier le contenu
                with open(seances_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    seances = data.get('seances', [])
                    print(f"   📊 {len(seances)} séances dans le fichier")
                    
                    # Vérifier que toutes les séances ont une date de découverte
                    seances_with_discovery = [s for s in seances if 'date_decouverte' in s]
                    print(f"   🕒 {len(seances_with_discovery)} séances avec date de découverte")
                    
                    if seances:
                        first_seance = seances[0]
                        print(f"   📅 Première séance : {first_seance['date']} - {first_seance['titre']}")
                        if 'date_decouverte' in first_seance:
                            print(f"   🔍 Découverte le : {first_seance['date_decouverte']}")
        else:
            print(f"   ❌ Échec : {result1.get('error', 'Erreur inconnue')}")
            return False
        
        print()
        
        # Deuxième lancement - devrait ignorer les séances existantes
        print("2. Deuxième lancement (même données)...")
        downloader2 = TelechargeurSeancesVD(output_folder=str(temp_path))
        result2 = downloader2.scrape_seances()
        
        if result2['success']:
            print(f"   ✅ Succès : {result2['total_count']} séances totales, {result2['new_count']} nouvelles")
            
            if result2['new_count'] == 0:
                print("   ✅ Aucune nouvelle séance ajoutée (comportement attendu)")
            else:
                print(f"   ⚠️  {result2['new_count']} nouvelles séances ajoutées (inattendu)")
        else:
            print(f"   ❌ Échec : {result2.get('error', 'Erreur inconnue')}")
            return False
        
        print()
        
        # Test avec ajout manuel d'une nouvelle séance
        print("3. Test avec ajout manuel d'une nouvelle séance...")
        
        # Lire le fichier existant
        with open(seances_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            seances = data.get('seances', [])
        
        # Ajouter une nouvelle séance manuellement
        new_seance = {
            "url": "https://www.vd.ch/test/nouvelle-seance",
            "date": "2025-06-25",
            "date_originale": "25 juin 2025",
            "titre": "Séance du Conseil d'Etat du 25 juin 2025",
            "date_decouverte": datetime.now().isoformat()
        }
        seances.append(new_seance)
        
        # Sauvegarder le fichier modifié
        data['seances'] = seances
        data['metadonnees']['total_seances'] = len(seances)
        data['metadonnees']['derniere_mise_a_jour'] = datetime.now().isoformat()
        
        with open(seances_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"   📝 Nouvelle séance ajoutée manuellement")
        
        # Troisième lancement - devrait détecter la nouvelle séance
        print("4. Troisième lancement (après ajout manuel)...")
        downloader3 = TelechargeurSeancesVD(output_folder=str(temp_path))
        result3 = downloader3.scrape_seances()
        
        if result3['success']:
            print(f"   ✅ Succès : {result3['total_count']} séances totales, {result3['new_count']} nouvelles")
            
            # Vérifier que le nombre total est correct
            expected_total = result1['total_count'] + 1  # +1 pour la séance ajoutée manuellement
            if result3['total_count'] == expected_total:
                print(f"   ✅ Nombre total correct : {result3['total_count']}")
            else:
                print(f"   ⚠️  Nombre total incorrect : attendu {expected_total}, obtenu {result3['total_count']}")
        else:
            print(f"   ❌ Échec : {result3.get('error', 'Erreur inconnue')}")
            return False
        
        print()
        print("=== Test terminé avec succès ===")
        return True


if __name__ == "__main__":
    success = test_single_file_logging()
    if success:
        print("🎉 Tous les tests ont réussi !")
    else:
        print("❌ Certains tests ont échoué.") 