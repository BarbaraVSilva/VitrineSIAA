import requests
import sqlite3
from app.core.database import get_connection
from app.core.telegram_logs import send_admin_log

def check_link_health(link):
    """
    Simula uma visita na URL para garantir que não se trata de um produto apagado
    ou de uma loja banida. Evita frustração do seu público promovendo link quebrado!
    """
    if not link:
        return False
        
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/114.0.0.0 Safari/537.36"
        }
        res = requests.get(link, headers=headers, timeout=10)
        
        # Produto não encontrado ou Lojista Sumiu vão redirecionar pra Home ou dar 404
        if res.status_code == 404 or res.url == "https://shopee.com.br/":
            return False
            
        return True
    except Exception as e:
        print(f"[HEALTH-CHECK] Falha de comunicação com Shopee para checar estoque: {e}")
        return False

def verify_all_active_products():
    """
    Job que deve rodar uma vez ao dia para varrer todos os seus links sendo divulgados na Vitrine / Insta.
    Esgotou principal? Tenta o Backup. Ambos caíram? Tira de circulação.
    """
    conn = get_connection()
    c = conn.cursor()
    
    # Busca com fallback extra (link_backup_2) ou joga nulo se banco ainda nao migrou 100%
    try:
        c.execute("SELECT id, nome_produto, link_afiliado, link_backup, link_backup_2 FROM produtos WHERE estoque_ok = 1")
    except:
        c.execute("SELECT id, nome_produto, link_afiliado, link_backup, NULL as link_backup_2 FROM produtos WHERE estoque_ok = 1")
    
    produtos = c.fetchall()
    
    print(f"[HEALTH-CHECK] Iniciado: Checando a integridade de {len(produtos)} oferta(s).")
    modificou_base = False
    
    for prod_id, nome_produto, principal, backup_1, backup_2 in produtos:
        is_active = check_link_health(principal)
        if not is_active:
            print(f"[ALERTA] Link Primário quebrou -> Produto ID {prod_id}. Link atual: {principal}")
            
            # Hora de brilhar! Usar o banco de Dados para salvar uma venda e ativar redundância!
            if backup_1 and check_link_health(backup_1):
                c.execute("UPDATE produtos SET link_afiliado = ?, link_backup = NULL WHERE id = ?", (backup_1, prod_id))
                msg = f"⚠️ Link de **{nome_produto}** esgotado.\n🔄 Trocado silenciosamente na vitrine pelo Reserva 1."
                print(f"   [SUCESSO] Link promovido pro Reserva 1: {backup_1}")
                send_admin_log(msg)
                modificou_base = True
            elif backup_2 and check_link_health(backup_2):
                c.execute("UPDATE produtos SET link_afiliado = ?, link_backup_2 = NULL WHERE id = ?", (backup_2, prod_id))
                msg = f"⚠️ O produto **{nome_produto}** esgotou o Original E o Reserva 1!\n🔥 Trocado com sucesso na vitrine pelo Reserva 2."
                print(f"   [SUCESSO] Link promovido pro Reserva 2: {backup_2}")
                send_admin_log(msg)
                modificou_base = True
            else:
                c.execute("UPDATE produtos SET estoque_ok = 0 WHERE id = ?", (prod_id,))
                msg = f"🚨 **ALERTA MÁXIMO:**\nO produto **{nome_produto}** secou! Todos os links reserva falharam e ele foi retirado da Vitrine."
                print(f"   [FALHA] Todos Reservas falharam! Ocultando o Produto da Vitrine Definitivamente.")
                send_admin_log(msg)
                modificou_base = True
                
    conn.commit()
    conn.close()
    
    # Retorna True se tiver que dar o Trigger de UPDATE da bio do Github Pages
    return modificou_base

if __name__ == "__main__":
    # Ao ser instanciado diretamente, roda a varredura.
    from database import init_db
    import os
    if not os.path.exists("db_siaa.sqlite"):
        init_db()
    verify_all_active_products()
