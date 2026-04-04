"""Test configuration and shared fixtures."""

import os
import tempfile
from collections.abc import Generator

import pytest

from edb.core.database import Database
from edb.core.engine import StorageEngine


@pytest.fixture
def tmp_db_path() -> Generator[str, None, None]:
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        path = f.name
    yield path
    if os.path.exists(path):
        os.unlink(path)


@pytest.fixture
def engine(tmp_db_path: str) -> Generator[StorageEngine, None, None]:
    eng = StorageEngine(tmp_db_path)
    yield eng
    eng.close()


@pytest.fixture
def db(tmp_db_path: str) -> Generator[Database, None, None]:
    database = Database(tmp_db_path)
    yield database
    database.close()


@pytest.fixture
def app_client():
    """FastAPI TestClient for integration tests."""
    import tempfile

    from fastapi.testclient import TestClient

    from edb.api.app import create_app
    from edb.api.dependencies import AppState
    from edb.config import EDBConfig

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    config = EDBConfig(db_path=db_path, create_admin=True, jwt_secret="test-secret")
    app = create_app(config)

    state = AppState(config)
    state.user_manager.ensure_admin_exists()
    app.state.edb = state

    client = TestClient(app)
    yield client

    state.database.close()
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture
def admin_token(app_client):
    """Get an admin JWT token for integration tests."""
    resp = app_client.post("/auth/login", json={"username": "admin", "password": "admin1234"})
    return resp.json()["access_token"]
