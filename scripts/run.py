import argparse
import logging
from postulats_vd.config import (
    MAX_SESSIONS,
    OUTPUT_FOLDER,
    PAGE_DELAY,
    STOP_DATE,
)
from postulats_vd.core.downloader import TelechargeurSeancesVD


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Téléchargeur de Séances du Conseil d'État VD",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python run.py              # Mode silencieux (par défaut)
  python run.py -v           # Mode info (affiche les informations de base)
  python run.py -vv          # Mode debug (affiche tous les détails)
        """,
    )

    parser.add_argument(
        "-v", "--verbose", action="count", default=0, help="Niveau de verbosité (-v pour info, -vv pour debug)"
    )

    return parser.parse_args()


def setup_logging(verbose_level):
    """Configure le niveau de logging selon le niveau de verbosité."""
    if verbose_level == 1:
        logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    elif verbose_level >= 2:
        logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")


def main():
    """Fonction principale."""
    args = parse_arguments()

    # Configuration du logging selon les arguments
    setup_logging(args.verbose)

    downloader = TelechargeurSeancesVD()

    print("=== Téléchargeur de Séances du Conseil d'État VD ===")
    print(f"Dossier de sortie : {OUTPUT_FOLDER}")
    print(f"Fichier de stockage : {downloader.storage.get_file_path()}")
    print(f"Date limite d'arrêt : {STOP_DATE if STOP_DATE else 'Aucune'}")
    print(f"Nombre maximum de pages : {MAX_SESSIONS}")
    print(f"Délai entre les pages : {PAGE_DELAY} seconde(s)")
    print()

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
