import sqlite3
import os

DB_PATH = 'db_siaa.sqlite'

def cleanup():
    if not os.path.exists(DB_PATH):
        print("Banco de dados não encontrado.")
        return

    conn = sqlite3.connect(DB_PATH)
    try:
        c = conn.cursor()
        
        # 1. Limpa Achadinhos Pessoais/Encontrados (PENDING ou MISSING_LINK)
        # 2. Limpa o que já foi Postado (status_fluxo = 'Postado')
        c.execute("""
            DELETE FROM achados 
            WHERE status IN ('PENDING', 'MISSING_LINK') 
               OR status_fluxo = 'Postado'
        """)
        
        rows = c.rowcount
        conn.commit()
        print(f"Sucesso! {rows} registros removidos das filas de processamento.")
        
    except Exception as e:
        print(f"Erro na limpeza: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    cleanup()
