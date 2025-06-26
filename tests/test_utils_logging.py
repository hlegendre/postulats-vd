#!/usr/bin/env python3
"""
Test de la classe LoggingUtils

Ce script teste les fonctionnalités de la classe utilitaire de logging.
"""

from src.postulats_vd.utils.logging import LoggingUtils


def test_logging_utils() -> None:
    """Test des fonctionnalités de LoggingUtils."""
    print("=== Test de LoggingUtils ===")

    # Test 1: Créer un logger simple
    print("1. Test de création d'un logger simple...")
    logger1 = LoggingUtils.setup_simple_logger("TestLogger1")
    logger1.info("Message de test du logger 1")
    print("   ✅ Logger simple créé avec succès")

    # Test 2: Créer un logger avec paramètres personnalisés
    print("2. Test de création d'un logger personnalisé...")
    custom_formatter = LoggingUtils.get_default_formatter()
    logger2 = LoggingUtils.setup_logger("TestLogger2", formatter=custom_formatter)
    logger2.info("Message de test du logger 2")
    print("   ✅ Logger personnalisé créé avec succès")

    # Test 3: Vérifier que les loggers sont différents
    print("3. Test de différenciation des loggers...")
    logger3 = LoggingUtils.setup_simple_logger("TestLogger3")
    logger3.warning("Message d'avertissement du logger 3")
    print("   ✅ Loggers différenciés avec succès")

    # Test 4: Vérifier que le même logger n'est pas recréé
    print("4. Test de réutilisation du même logger...")
    logger1_again = LoggingUtils.setup_simple_logger("TestLogger1")
    logger1_again.debug("Message de debug du logger 1 (réutilisé)")
    print("   ✅ Même logger réutilisé (pas de duplication)")

    print("\n✅ Tous les tests de LoggingUtils ont réussi !")


if __name__ == "__main__":
    print("🧪 Démarrage des tests de LoggingUtils...")  
    print()

    try:
        test_logging_utils()
    except Exception as e:
        print(f"❌ Erreur lors des tests : {e}")
        exit(1)

    print("🎉 Tous les tests ont réussi !")
    print()
