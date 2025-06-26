import argparse
import logging
from src.postulats_vd.config import (
    OUTPUT_FOLDER,
    STOP_DATE,
)
from src.postulats_vd.core import SessionLister, SessionExtractor, Storage, FileDownloader


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
    setup_logging(args.verbose)
    storage = Storage()

    logging.debug(f"Dossier de sortie : {OUTPUT_FOLDER}")
    logging.info(f"Date limite d'arrêt : {STOP_DATE if STOP_DATE else 'Aucune'}")

    # Découverte des séances
    print("=== Découverte des Séances du Conseil d'État VD ===")
    sessionFinder = SessionLister(storage=storage)
    result = sessionFinder.list()
    if result["success"]:
        if result["stop_reached"]:
            print(f"> arrêt anticipé : date limite ({STOP_DATE}) atteinte)")

        print(
            f"✅ OK : nouvelles = {result['new_seances_count']} / totales = {result['stored_seances']} (pages = {result['pages_processed']})"
        )
    else:
        print(f"❌ Échec de la découverte : {result.get('error', 'Erreur inconnue')}")
        exit(1)

    # Extraction des séances
    print("=== Extraction des Séances du Conseil d'État VD ===")
    sessionExtractor = SessionExtractor(storage=storage)
    result = sessionExtractor.extract_all_seances()
    status = "✅ OK" if result["success"] else "❌ KO"
    print(
        f"{status} : nouvelles = {result['nb_extracted']} / ignorées = {result['nb_ignored']} / en erreur = {result['nb_error']}"
    )

    # Téléchargement des fichiers
    print("=== Téléchargement des Fichiers des Séances du Conseil d'État VD ===")
    fileDownloader = FileDownloader(storage=storage)
    result = fileDownloader.download_all_files()
    status = "✅ OK" if result["nb_error"] == 0 else "❌ KO"
    print(
        f"{status} : téléchargés = {result['nb_downloaded']} / ignorés = {result['nb_ignored']} / existants = {result['nb_existing']} / en erreur = {result['nb_error']}"
    )


if __name__ == "__main__":
    main()
