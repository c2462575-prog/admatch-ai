"""Shared test fixtures."""
import os
import sys
import pytest
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.database import init_db, get_db


@pytest.fixture
def test_db(tmp_path):
    """Create a fresh test database."""
    db_path = str(tmp_path / "test.db")
    init_db(db_path)
    return db_path


@pytest.fixture
def test_conn(test_db):
    """Yield a connection to a fresh test database."""
    with get_db(test_db) as conn:
        yield conn


@pytest.fixture
def test_app(test_db):
    """Create a FastAPI test app with test database."""
    os.environ["DATABASE_PATH"] = test_db

    # Re-import to pick up new DATABASE_PATH
    import importlib
    import core.config
    importlib.reload(core.config)

    from api.app import create_app
    app = create_app()
    return app


@pytest.fixture
def client(test_app):
    """HTTP test client."""
    from fastapi.testclient import TestClient
    return TestClient(test_app)
