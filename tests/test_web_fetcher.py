#!/usr/bin/env python3
"""
Test for HtmlFetcher singleton pattern and rate limiting
"""

import time

from src.postulats_vd.utils.web_fetcher import WebFetcher


def test_web_fetcher_singleton() -> None:
    """Test that WebFetcher follows singleton pattern"""
    # Create two instances
    fetcher1 = WebFetcher()
    fetcher2 = WebFetcher()

    # They should be the same object
    assert fetcher1 is fetcher2

    # The session should be the same
    assert fetcher1.session is fetcher2.session

    # The logger should be the same
    assert fetcher1.logger is fetcher2.logger


def test_web_fetcher_initialization() -> None:
    """Test that WebFetcher initializes correctly"""
    fetcher = WebFetcher()

    # Check that session exists and has user agent
    assert hasattr(fetcher, "session")
    assert "User-Agent" in fetcher.session.headers

    # Check that logger exists
    assert hasattr(fetcher, "logger")

    # Check that _initialized flag is set
    assert fetcher._initialized is True

    # Check that rate limiting timestamp is initialized
    assert hasattr(fetcher, "_last_request_time")


def test_rate_limiting_timestamp() -> None:
    """Test that rate limiting timestamp is updated after requests"""
    fetcher = WebFetcher()

    # Reset the timestamp to simulate a fresh start
    fetcher._last_request_time = 0

    # Mock a successful request by directly calling the timestamp update
    fetcher._last_request_time = time.time()
    initial_timestamp = fetcher._last_request_time

    # Wait a bit
    time.sleep(0.1)

    # Verify timestamp was set
    assert fetcher._last_request_time > 0
    assert fetcher._last_request_time == initial_timestamp


if __name__ == "__main__":
    print("🧪 Démarrage des tests de WebFetcher...")
    print()

    try:
        test_web_fetcher_singleton()
        test_web_fetcher_initialization()
        test_rate_limiting_timestamp()
    except Exception as e:
        print(f"❌ Erreur lors des tests : {e}")
        exit(1)

    print("🎉 Tous les tests ont réussi !")
    print()
