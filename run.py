from config import (
    MAX_SESSIONS,
    OUTPUT_FOLDER,
    PAGE_DELAY,
    STOP_DATE,
    VERBOSE,
)
from src.downloader import TelechargeurSeancesVD
import logging


def main():
    """Fonction principale."""
    downloader = TelechargeurSeancesVD()

    print("=== Téléchargeur de Séances du Conseil d'État VD ===")
    print(f"Dossier de sortie : {OUTPUT_FOLDER}")
    print(f"Fichier de stockage : {downloader.storage.get_file_path()}")
    print(f"Date limite d'arrêt : {STOP_DATE if STOP_DATE else 'Aucune'}")
    print(f"Nombre maximum de pages : {MAX_SESSIONS}")
    print(f"Délai entre les pages : {PAGE_DELAY} seconde(s)")
    print()

    if VERBOSE:
        logging.basicConfig(level=logging.DEBUG)

    result = downloader.scrape_seances()

    if result["success"]:
        print(f"✅ Extraction réussie !")
        print(f"📊 Total des séances stockées : {result['stored_seances']}")
        print(f"🆕 Nouvelles séances ajoutées : {result['new_seances_count']}")
        print(f"📄 Pages traitées : {result['pages_processed']}")

        if result.get("stop_reached"):
            print(f"🛑 Arrêt anticipé : date limite ({STOP_DATE}) atteinte")

        if result["new_seances_count"] > 0:
            print(f"\nℹ️  {result['new_seances_count']} nouvelles séances ont été ajoutées au stockage")
        else:
            print(f"\nℹ️  Aucune nouvelle séance ajoutée")
    else:
        print(f"❌ Échec de l'extraction : {result.get('error', 'Erreur inconnue')}")


if __name__ == "__main__":
    main()
