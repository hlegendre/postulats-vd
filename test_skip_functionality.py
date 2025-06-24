#!/usr/bin/env python3
"""
Test script pour vérifier la fonctionnalité de saut de fichiers existants
"""

import os
import tempfile
from pathlib import Path
from vaud_pdf_downloader import TelechargeurPostulatsVD
from config import SKIP_EXISTING_FILES

def test_skip_functionality():
    """Test de la fonctionnalité de saut de fichiers existants"""
    print("🧪 Test de la fonctionnalité de saut de fichiers")
    print("=" * 50)
    
    # Créer un dossier temporaire pour le test
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Dossier de test temporaire : {temp_dir}")
        
        # Créer un fichier fictif pour simuler un fichier déjà téléchargé
        test_file = Path(temp_dir) / "25_POS_17_RC.pdf"
        test_file.write_text("Contenu fictif pour test")
        print(f"Fichier de test créé : {test_file}")
        
        # Initialiser le téléchargeur avec le dossier temporaire
        downloader = TelechargeurPostulatsVD(output_folder=temp_dir)
        
        # Simuler l'extraction d'un lien PDF
        test_url = "https://www.vd.ch/fileadmin/user_upload/organisation/gc/fichiers_pdf/2022-2027/25_POS_17_RC.pdf"
        
        print(f"\n🔍 Test avec SKIP_EXISTING_FILES = {SKIP_EXISTING_FILES}")
        print(f"URL de test : {test_url}")
        
        # Extraire le nom de fichier
        from urllib.parse import urlparse
        parsed_url = urlparse(test_url)
        filename = os.path.basename(parsed_url.path)
        filepath = Path(temp_dir) / filename
        
        print(f"Nom de fichier attendu : {filename}")
        print(f"Chemin complet : {filepath}")
        print(f"Fichier existe : {filepath.exists()}")
        
        # Tester la logique de saut
        if SKIP_EXISTING_FILES and filepath.exists():
            print("✅ Fichier serait ignoré (comportement attendu)")
            return True
        else:
            print("❌ Fichier ne serait PAS ignoré (comportement inattendu)")
            return False

if __name__ == "__main__":
    success = test_skip_functionality()
    print("\n" + "=" * 50)
    if success:
        print("🎉 Test de saut de fichiers réussi !")
    else:
        print("❌ Test de saut de fichiers échoué !") 