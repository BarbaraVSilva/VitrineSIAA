import datetime
from app.core.database import get_connection

def agendar_produto(produto_id: int, data_hora_str: str, evento: str = 'COMUM'):
    """
    Atualiza o produto para SCHEDULED e seta a data/hora exata em que deve ir ao ar.
    """
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "UPDATE produtos SET status_publicacao = 'SCHEDULED', data_agendada = ?, evento = ? WHERE id = ?",
        (data_hora_str, evento, produto_id)
    )
    conn.commit()
    conn.close()

def obter_produtos_pendentes():
    """
    Lista produtos que foram aprovados na Triagem mas ainda não foram Agendados nem Postados.
    """
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        SELECT p.id, p.nome_produto, p.categoria, p.status_publicacao, a.midia_path, p.evento 
        FROM produtos p
        JOIN achados a ON p.achado_id = a.id
        WHERE p.status_publicacao = 'PENDING'
    ''')
    rows = c.fetchall()
    conn.close()
    return rows

def obter_produtos_agendados():
    """
    Lista a fila de produtos que estão aguardando a hora de postar.
    """
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        SELECT p.id, p.nome_produto, p.data_agendada, p.evento 
        FROM produtos p
        WHERE p.status_publicacao = 'SCHEDULED'
        ORDER BY p.data_agendada ASC
    ''')
    rows = c.fetchall()
    conn.close()
    return rows

def cancelar_agendamento(produto_id: int):
    """
    Devolve o produto para pendente.
    """
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "UPDATE produtos SET status_publicacao = 'PENDING', data_agendada = NULL WHERE id = ?",
        (produto_id,)
    )
    conn.commit()
    conn.close()

def obter_posts_prontos_para_agora():
    """
    O Motor de Cron Job (main.py) chama isso para saber o que postar AGORA.
    Retorna os posts SCHEDULED cuja data apontada já passou ou é igual ao momento atual.
    """
    agora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        SELECT p.id AS p_id, a.id AS a_id, a.texto_original, a.midia_path, p.link_afiliado, a.link_original 
        FROM produtos p
        JOIN achados a ON p.achado_id = a.id
        WHERE p.status_publicacao = 'SCHEDULED' 
          AND p.data_agendada IS NOT NULL
          AND p.data_agendada <= ?
    ''', (agora,))
    rows = c.fetchall()
    conn.close()
    return rows

def marcar_como_postado(produto_id: int, achado_id: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE produtos SET status_publicacao = 'POSTED' WHERE id = ?", (produto_id,))
    c.execute("UPDATE achados SET status = 'POSTED' WHERE id = ?", (achado_id,))
    conn.commit()
    conn.close()

def relatorio_campanha(evento: str):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM produtos WHERE evento = ?", (evento,))
    total = c.fetchone()[0]
    conn.close()
    return total
