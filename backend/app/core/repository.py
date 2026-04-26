import sqlite3
from typing import List, Optional, Dict, Any
from app.core.database import get_connection, retry_on_lock

class BaseRepository:
    def __init__(self):
        self.db_name = "db_siaa.sqlite"

    def _execute_query(self, query: str, params: tuple = (), commit: bool = False):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            if commit:
                conn.commit()
                return cursor.lastrowid
            return cursor.fetchall()
        finally:
            conn.close()

class AchadosRepository(BaseRepository):
    @retry_on_lock()
    def add_achado(self, texto: str, midia: str, link: str, status: str = 'PENDING', categoria: str = 'Geral') -> int:
        query = """
            INSERT INTO achados (texto_original, midia_path, link_original, status, categoria) 
            VALUES (?, ?, ?, ?, ?)
        """
        return self._execute_query(query, (texto, midia, link, status, categoria), commit=True)

    def get_pending(self) -> List[Dict[str, Any]]:
        query = "SELECT * FROM achados WHERE status = 'PENDING'"
        rows = self._execute_query(query)
        # Convert to list of dicts for easier use in business logic
        return [self._row_to_dict(row) for row in rows]

    @retry_on_lock()
    def update_status(self, id: int, status: str):
        query = "UPDATE achados SET status = ? WHERE id = ?"
        self._execute_query(query, (status, id), commit=True)

    def _row_to_dict(self, row: tuple) -> Dict[str, Any]:
        # Helper to map sqlite row to dict based on schema
        # id, texto_original, midia_path, cover_path, link_original, link_backup_1, link_backup_2, categoria, status
        return {
            "id": row[0],
            "texto_original": row[1],
            "midia_path": row[2],
            "cover_path": row[3],
            "link_original": row[4],
            "categoria": row[7],
            "status": row[8]
        }

class ProdutosRepository(BaseRepository):
    @retry_on_lock()
    def add_produto(self, achado_id: int, link_afiliado: str, nome: str, categoria: str = 'Geral'):
        query = """
            INSERT INTO produtos (achado_id, link_afiliado, nome_produto, categoria) 
            VALUES (?, ?, ?, ?)
        """
        return self._execute_query(query, (achado_id, link_afiliado, nome, categoria), commit=True)

    def get_all(self) -> List[Dict[str, Any]]:
        query = "SELECT * FROM produtos ORDER BY data_criacao DESC"
        rows = self._execute_query(query)
        return [self._row_to_dict(row) for row in rows]

    def _row_to_dict(self, row: tuple) -> Dict[str, Any]:
        return {
            "id": row[0],
            "achado_id": row[1],
            "link_afiliado": row[2],
            "nome_produto": row[5],
            "categoria": row[6],
            "data_criacao": row[8]
        }
