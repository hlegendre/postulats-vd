import argparse
import logging
from src.postulats_vd.config import (
    OUTPUT_FOLDER,
    STOP_DATE,
)
from src.postulats_vd.core.sessionfinder import CESessionFinder


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

    logging.debug(f"Dossier de sortie : {OUTPUT_FOLDER}")
    logging.info(f"Date limite d'arrêt : {STOP_DATE if STOP_DATE else 'Aucune'}")

    # Découverte des séances
    print("=== Découverte des Séances du Conseil d'État VD ===")
    sessionFinder = CESessionFinder()
    result = sessionFinder.scrape_seances()
    if result["success"]:
        if result["stop_reached"]:
            print(f"> arrêt anticipé : date limite ({STOP_DATE}) atteinte)")

        print(
            f"✅ OK : nouvelles = {result['new_seances_count']} / totales = {result['stored_seances']} (pages = {result['pages_processed']})"
        )
    else:
        print(f"❌ Échec de la découverte : {result.get('error', 'Erreur inconnue')}")
        exit(1)

    # Récupération des séances
    print("=== Récupération des Séances du Conseil d'État VD ===")


if __name__ == "__main__":
    main()
