import sqlite3
import os

DB_PATH = os.getenv("DB_PATH", "db_siaa.sqlite")

def get_connection():
    """Retorna uma conexão bruta com o banco SQLite com otimizações de concorrência (WAL)."""
    # Define o tempo de timeout global da conexão Python para 30s
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    # Ativa o modo WAL (Write-Ahead Logging) para permitir leituras e escritas simultâneas
    conn.execute("PRAGMA journal_mode=WAL;")
    # Define um timeout na engine SQLite de 30.000ms
    conn.execute("PRAGMA busy_timeout=30000;")
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
            status TEXT DEFAULT 'PENDING',
            compliance_status TEXT DEFAULT 'PENDENTE',
            compliance_reason TEXT,
            tipo_link TEXT DEFAULT 'PRODUTO',
            status_fluxo TEXT DEFAULT 'Ideia',
            legenda_instagram TEXT,
            legenda_tiktok TEXT,
            legenda_shopee TEXT
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
    
    # Tabela 3: Log de disparos do bot Auto-DM
    c.execute('''
        CREATE TABLE IF NOT EXISTS bot_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT DEFAULT 'DM',
            user_id TEXT,
            comment_id TEXT,
            produto_id INTEGER,
            palavra_gatilho TEXT,
            resposta_enviada TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela 4: Banco de Mídias (mídias disponíveis independentes)
    c.execute('''
        CREATE TABLE IF NOT EXISTS media_bank (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            arquivo_path TEXT UNIQUE,
            tipo TEXT DEFAULT 'imagem',
            origem TEXT DEFAULT 'upload',
            usado BOOLEAN DEFAULT 0,
            achado_id INTEGER,
            data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Migrações de colunas existentes
    colunas_achados = [
        ("cover_path", "TEXT"),
        ("link_backup_1", "TEXT"),
        ("link_backup_2", "TEXT"),
        ("categoria", "TEXT"),
        ("compliance_status", "TEXT"),
        ("compliance_reason", "TEXT"),
        ("tipo_link", "TEXT"),
        ("status_fluxo", "TEXT DEFAULT 'Ideia'"),
        ("legenda_instagram", "TEXT"),
        ("legenda_tiktok", "TEXT"),
        ("legenda_shopee", "TEXT"),
    ]
    for col, col_type in colunas_achados:
        try:
            c.execute(f"ALTER TABLE achados ADD COLUMN {col} {col_type}")
        except sqlite3.OperationalError:
            pass  # Coluna já existe

    colunas_produtos = ["link_backup", "link_backup_2", "categoria", "last_checked"]
    for col in colunas_produtos:
        try:
            c.execute(f"ALTER TABLE produtos ADD COLUMN {col} TEXT")
        except sqlite3.OperationalError:
            pass
    
    # Migração campanhas
    cols_camp = [("status_publicacao", "TEXT DEFAULT 'PENDING'"), ("data_agendada", "TEXT"), ("evento", "TEXT DEFAULT 'COMUM'")]
    for col, col_type in cols_camp:
        try:
            c.execute(f"ALTER TABLE produtos ADD COLUMN {col} {col_type}")
        except sqlite3.OperationalError:
            pass

    conn.commit()
    conn.close()
    print("Base SIAA-2026 inicializada com sucesso!")

if __name__ == "__main__":
    init_db()
