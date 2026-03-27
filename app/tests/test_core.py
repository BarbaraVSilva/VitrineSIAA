import os
from app.core.database import get_connection

def test_database_initialization(test_db):
    """Test if tables are created correctly."""
    conn = get_connection()
    c = conn.cursor()
    
    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in c.fetchall()]
    
    assert "achados" in tables
    assert "produtos" in tables
    
    c.execute("PRAGMA table_info(achados);")
    columns_achados = [row[1] for row in c.fetchall()]
    assert "categoria" in columns_achados
    assert "cover_path" in columns_achados
    
    conn.close()
    
def test_insert_achado(mock_db_connection):
    """Test inserting a new item in the database."""
    c = mock_db_connection.cursor()
    c.execute(
        "INSERT INTO achados (texto_original, midia_path, link_original) VALUES (?, ?, ?)",
        ("Promoção de teste", "/tmp/video.mp4", "http://shopee.com/teste")
    )
    mock_db_connection.commit()
    
    c.execute("SELECT id, texto_original FROM achados ORDER BY id DESC LIMIT 1")
    row = c.fetchone()
    
    assert row is not None
    assert row[1] == "Promoção de teste"
