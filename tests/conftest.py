"""
Shared pytest fixtures.
"""
import pytest

from app import create_app


@pytest.fixture(scope="session")
def flask_app():
    """Create the Flask application once per test session."""
    app = create_app()
    app.config["TESTING"] = True
    return app


@pytest.fixture(scope="session")
def client(flask_app):
    """Test client reused across the session."""
    return flask_app.test_client()


@pytest.fixture()
def empty_context():
    """A fresh per-record context dict."""
    return {}
