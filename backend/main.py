import logging
import os
import sys
import time
import schedule
from dotenv import load_dotenv

# Força UTF-8 no terminal Windows para evitar 'charmap' errors
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Adiciona o diretório raiz ao path para encontrar o módulo app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import init_db, optimize_db
from app.core.logger import log_event
from app.core.firebase_sync import firebase_sync
from app.jobs.cron_jobs import (
    cleanup_downloads,
    job_healthcheck,
    job_postagem_pico,
    job_shopee_video,
)
from app.publisher.update_vitrine import generate_html_vitrine

# Carrega .env do diretório raiz (um nível acima de backend/)
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

def run_scheduler() -> None:
    init_db()
    optimize_db()
    log_event("Cérebro SIAA-2026 Inicializado", component="Main", event="SYSTEM_START", status="SUCCESS")
    
    # Atualiza status no Firebase para o Dashboard React
    firebase_sync.update_engine_status("main", "ATIVO")
    firebase_sync.update_engine_status("shopee", "ATIVO")
    firebase_sync.update_engine_status("social", "ATIVO")
    firebase_sync.update_engine_status("price", "SINC")

    post_times = os.getenv("POST_SCHEDULE_TIMES", "11:00,18:00").split(",")

    for t in post_times:
        schedule.every().day.at(t.strip()).do(job_postagem_pico)
        print(f"[*] Postagem Programada para Diariamente às: {t.strip()}")

    schedule.every(4).hours.do(job_healthcheck)
    schedule.every(2).hours.do(job_shopee_video)
    schedule.every().day.at("03:00").do(cleanup_downloads)

    print("\n" + "=" * 50)
    print("** O CÉREBRO SIAA-2026 ESTÁ ONLINE E ORQUESTRANDO TUDO **")
    print("=" * 50)
    
    print("\n[Inicialização] Gerando A Primeira Vitrine...")
    try:
        generate_html_vitrine()
    except Exception as e:
        print(f"[Aviso] Falha ao gerar vitrine inicial: {e}")

    print("\nAguardando alarmes... (Pressione Ctrl+C para desligar o relógio)")

    try:
        while True:
            schedule.run_pending()
            firebase_sync.heartbeat() # Heartbeat para o Dashboard
            time.sleep(1)
    except KeyboardInterrupt:
        firebase_sync.update_engine_status("main", "OFFLINE")
        print("\nDesligando sistema Mestre...")

if __name__ == "__main__":
    try:
        run_scheduler()
    except Exception as e:
        from app.core.logger import log_event
        import logging
        log_event(f"CRASH FATAL DO SISTEMA: {e}", component="Main", event="FATAL_ERROR", status="CRITICAL", level=logging.ERROR)
        print(f"\n[FATAL] O sistema parou inesperadamente: {e}")
        raise e
