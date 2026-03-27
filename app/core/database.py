import sqlite3
import os

DB_PATH = os.getenv("DB_PATH", "db_siaa.sqlite")

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    """
    Cria as tabelas caso não existam:
    1. 'achados' armazena as capturas e mantém a pipeline (do crawler até a postagem)
    2. 'produtos' mapeia os links oficiais e os de backup pros mesmos itens, controlando a vitrine.
    """
    conn = get_connection()
    c = conn.cursor()
    
    # Tabela 1: Fluxo de mineração e postagem
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
            status TEXT DEFAULT 'PENDING' -- PENDING, EDITED, APPROVED, POSTED, REJECTED
        )
    ''')
    
    # Adicionar a coluna nas tabelas existentes (migration dummy)
    try:
        c.execute("ALTER TABLE achados ADD COLUMN cover_path TEXT")
        c.execute("ALTER TABLE achados ADD COLUMN link_backup_1 TEXT")
        c.execute("ALTER TABLE achados ADD COLUMN link_backup_2 TEXT")
        c.execute("ALTER TABLE achados ADD COLUMN categoria TEXT DEFAULT 'Geral'")
        print("Migração: Colunas na tabela 'achados' completas.")
    except Exception:
        pass
    
    # Tabela 2: Vitrine e controle de estoque de afiliados
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
    
    # Migração Tabela Produtos (30 dias rule)
    try:
        c.execute("ALTER TABLE produtos ADD COLUMN data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP")
        print("Migração: Coluna 'data_criacao' em Produtos adicionada com sucesso.")
    except Exception:
        pass
        
    # Migração Tabela Produtos (Fallback Múltiplo)
    try:
        c.execute("ALTER TABLE produtos ADD COLUMN link_backup_2 TEXT")
        print("Migração: Coluna 'link_backup_2' em Produtos adicionada com sucesso.")
    except Exception:
        pass
        
    # Migração Categorias
    try:
        c.execute("ALTER TABLE produtos ADD COLUMN categoria TEXT DEFAULT 'Geral'")
        print("Migração: Coluna 'categoria' adicionada com sucesso.")
    except Exception:
        pass
        
    conn.commit()
    conn.close()
    print("Banco de dados local (SQLite3) inicializado e tabelas criadas com sucesso!")

if __name__ == "__main__":
    # Quando inicializado manualmente, ele cria a base.
    init_db()
