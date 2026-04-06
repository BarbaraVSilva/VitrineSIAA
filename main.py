import logging
import os
import sys
import time

from dotenv import load_dotenv

# Força UTF-8 no terminal Windows para evitar erros de charmap com emojis
if sys.platform == "win32":
    import codecs

    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

import schedule

from app.core.database import init_db
from app.core.logger import log_event
from app.jobs.cron_jobs import (
    cleanup_downloads,
    job_healthcheck,
    job_postagem_pico,
    job_shopee_video,
)
from app.publisher.update_vitrine import generate_html_vitrine

load_dotenv()


def run_scheduler() -> None:
    init_db()
    log_event("Cérebro SIAA-2026 Inicializado", component="Main", event="SYSTEM_START", status="SUCCESS")

    post_times = os.getenv("POST_SCHEDULE_TIMES", "12:00,18:00,21:00").split(",")

    for t in post_times:
        schedule.every().day.at(t.strip()).do(job_postagem_pico)
        print(f"[*] Postagem Programada para Diariamente às: {t.strip()}")

    schedule.every(4).hours.do(job_healthcheck)
    print("[*] Verificador de Estoque Shopee (HealthCheck) programado a cada: 4 horas")

    schedule.every(2).hours.do(job_shopee_video)
    print("[*] Bot de Upload p/ Shopee Video programado a cada: 2 horas")

    schedule.every().day.at("03:00").do(cleanup_downloads)
    print("[*] Faxina do Sistema programada para Diariamente às: 03:00")

    print("\n" + "=" * 50)
    print("** O CÉREBRO SIAA-2026 ESTÁ ONLINE E ORQUESTRANDO TUDO **")
    print("=" * 50)
    print("Nota: O Telegram Crawler e o Streamlit Dashboard rodam em processos separados!")
    print("\n[Inicialização] Gerando A Primeira Vitrine...")
    generate_html_vitrine()

    print("\nAguardando alarmes... (Pressione Ctrl+C para desligar o relógio)")

    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nDesligando sistema Mestre...")


if __name__ == "__main__":
    run_scheduler()
