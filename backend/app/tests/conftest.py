import os
import sqlite3
import pytest

from app.core.database import get_connection

@pytest.fixture(scope="function", autouse=True)
def test_db(tmp_path, monkeypatch):
    TEST_DB_PATH = str(tmp_path / "test_db_siaa.sqlite")
    # Patch the module's variable
    monkeypatch.setattr("app.core.database.DB_PATH", TEST_DB_PATH)
    
    from app.core.database import init_db
    init_db()
    
    yield TEST_DB_PATH

@pytest.fixture
def mock_db_connection(test_db):
    conn = get_connection()
    yield conn
    conn.close()
