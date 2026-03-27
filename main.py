import os
import time
from dotenv import load_dotenv

import schedule

from app.publisher.auto_post import run_publisher
from app.core.health_check import verify_all_active_products
from app.publisher.update_vitrine import generate_html_vitrine
from app.core.database import init_db, get_connection
from app.social_interactions.instagram_bot import run_social_interactions
from app.publisher.shopee_video import publish_to_shopee_video

load_dotenv()

def job_postagem_pico():
    print(f"\n[CRON] {time.strftime('%H:%M:%S')} - Iniciando Job de Publicação! Olhando a fila de aprovados...")
    run_publisher()

def job_healthcheck():
    print(f"\n[CRON] {time.strftime('%H:%M:%S')} - Iniciando Check Médico de Estoque e Links Quebrados...")
    houve_modificacoes_vitrine = verify_all_active_products()
    if houve_modificacoes_vitrine:
        print("[CRON] Algum produto esgotou ou quebrou! Renderizando o HTML novo para proteger do Shadowban...")
        generate_html_vitrine()

def job_social():
    run_social_interactions()
    
def job_shopee_video():
    """Puxa do banco achados (itens aprovados, em formato de vídeo) e posta."""
    print(f"\n[CRON] {time.strftime('%H:%M:%S')} - Iniciando Auto-postagem Shopee Video...")
    
    conn = get_connection()
    c = conn.cursor()
    # Pega apenas 1 video q ainda não listado como POSTED_SHOPEE (status 'APPROVED' ou 'POSTED')
    try:
        c.execute('''
            SELECT a.id, a.texto_original, a.midia_path, p.link_afiliado 
            FROM achados a
            JOIN produtos p ON a.id = p.achado_id
            WHERE a.status IN ('APPROVED', 'POSTED') AND (a.midia_path LIKE '%.mp4' OR a.midia_path LIKE '%.mov')
            LIMIT 1
        ''')
        video = c.fetchone()
    except Exception as e:
        print(f"[SHOPEE VIDEO] Erro DB: {e}")
        video = None
        
    if not video:
        print("[SHOPEE VIDEO] Nenhum vídeo novo para postar agora.")
        conn.close()
        return
        
    v_id, legenda, video_path, link = video
    if not os.path.exists(video_path):
        print(f"[SHOPEE VIDEO] Arquivo físico não encontrado: {video_path}")
        # Marca como fail pra nao tentar de novo
        c.execute("UPDATE achados SET status = 'FAIL_FILE' WHERE id = ?", (v_id,))
        conn.commit()
        conn.close()
        return
        
    print(f"[SHOPEE VIDEO] Encontrado vídeo na fila DB: {video_path}")
    sucesso = publish_to_shopee_video(video_path, legenda, link)
    
    if sucesso:
        c.execute("UPDATE achados SET status = 'POSTED_SHOPEE' WHERE id = ?", (v_id,))
        conn.commit()
        print(f"[SHOPEE VIDEO] Produto {v_id} marcado como POSTED_SHOPEE.")
    conn.close()

def run_scheduler():
    if not os.path.exists("db_siaa.sqlite"):
        print("[SISTEMA] Banco não existe, criando do zero...")
        init_db()

    post_times = os.getenv("POST_SCHEDULE_TIMES", "12:00,18:00,21:00").split(",")
    
    # 1. Registra os horários de postagem das redes
    for t in post_times:
        schedule.every().day.at(t.strip()).do(job_postagem_pico)
        print(f"[*] Postagem Programada para Diariamente às: {t.strip()}")
        
    # 2. Registra o verificador da Shopee
    schedule.every(4).hours.do(job_healthcheck)
    print("[*] Verificador de Estoque Shopee (HealthCheck) programado a cada: 4 horas")
    
    # 3. Registra o Bot de Comentários do Instagram
    schedule.every(15).minutes.do(job_social)
    print("[*] Bot de Resposta Meta/Instagram programado a cada: 15 minutos")
    
    # 4. Registra Auto-postagem do Shopee Video (ex: a cada 2 horas)
    schedule.every(2).hours.do(job_shopee_video)
    print("[*] Bot de Upload p/ Shopee Video programado a cada: 2 horas")
    
    print("\n" + "="*50)
    print("🤖 O CÉREBRO SIAA-2026 ESTÁ ONLINE E ORQUESTRANDO TUDO 🤖")
    print("="*50)
    print("Nota: O Telegram Crawler e o Streamlit Dashboard rodam em processos separados!")
    print("\n[Inicialização] Gerando A Primeira Vitrine...")
    generate_html_vitrine()
    
    print("\nAguardando alarmes... (Pressione Ctrl+C para desligar o relógio)")
    
    try:
        # Loop real processando a fila do agendador
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nDesligando sistema Mestre...")

if __name__ == '__main__':
    run_scheduler()
