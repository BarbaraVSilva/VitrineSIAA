import sqlite3
import os

DB_PATH = os.getenv("DB_PATH", "db_siaa.sqlite")

def get_connection():
    """Retorna uma conexão bruta com o banco SQLite com otimizações de concorrência (WAL)."""
    conn = sqlite3.connect(DB_PATH)
    # Ativa o modo WAL (Write-Ahead Logging) para permitir leituras e escritas simultâneas
    conn.execute("PRAGMA journal_mode=WAL;")
    # Define um timeout de 10s para esperar caso o banco esteja ocupado (evita database is locked imediato)
    conn.execute("PRAGMA busy_timeout=10000;")
    return conn

def retry_on_lock(retries=5, delay=0.5):
    """Decorador para tentar novamente operações em caso de 'database is locked'."""
    def decorator(func):
        import time
        from functools import wraps
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for i in range(retries):
                try:
                    return func(*args, **kwargs)
                except sqlite3.OperationalError as e:
                    if "locked" in str(e).lower():
                        last_exception = e
                        time.sleep(delay * (2 ** i)) # Backoff exponencial
                        continue
                    raise
            raise last_exception
        return wrapper
    return decorator

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
            last_checked DATETIME,
            FOREIGN KEY(achado_id) REFERENCES achados(id)
        )
    ''')
    
    # Migração simples se a coluna não existir
    try:
        c.execute("ALTER TABLE produtos ADD COLUMN last_checked DATETIME")
    except sqlite3.OperationalError:
        pass # Coluna já existe
    
    conn.commit()
    conn.close()
    print("Base SIAA-2026 inicializada com sucesso!")

if __name__ == "__main__":
    init_db()
