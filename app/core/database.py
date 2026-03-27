import sqlite3
import os

DB_PATH = os.getenv("DB_PATH", "db_siaa.sqlite")

def get_connection():
    """Retorna uma conexão bruta com o banco SQLite."""
    return sqlite3.connect(DB_PATH)

def init_db():
    """Inicializa as tabelas fundamentais da pipeline SIAA-2026."""
    conn = get_connection()
    c = conn.cursor()
    
    # Tabela 1: Fluxo de mineração (Achados)
    c.execute('''
        CREATE TABLE IF NOT EXISTS achados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            texto_original TEXT,
            midia_path TEXT,
            cover_path TEXT,
            link_original TEXT,
            link_backup_1 TEXT,
            link_backup_2 TEXT,
            categoria TEXT DEFAULT 'Geral',
            status TEXT DEFAULT 'PENDING'
        )
    ''')
    
    # Tabela 2: Vitrine de Afiliados (Produtos)
    c.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            achado_id INTEGER,
            link_afiliado TEXT,
            link_backup TEXT,
            link_backup_2 TEXT,
            nome_produto TEXT,
            categoria TEXT DEFAULT 'Geral',
            estoque_ok BOOLEAN DEFAULT 1,
            data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(achado_id) REFERENCES achados(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Base SIAA-2026 inicializada com sucesso!")

if __name__ == "__main__":
    init_db()
