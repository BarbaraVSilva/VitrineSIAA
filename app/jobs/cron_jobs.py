"""Tarefas periódicas do Cérebro SIAA (schedule)."""

from __future__ import annotations

import glob
import os
import time

from app.core.database import get_connection
from app.core.health_check import verify_all_active_products
from app.core.logger import log_event
from app.publisher.auto_post import run_publisher
from app.publisher.shopee_video import publish_to_shopee_video
from app.publisher.update_vitrine import generate_html_vitrine


def job_postagem_pico() -> None:
    print(f"\n[CRON] {time.strftime('%H:%M:%S')} - Iniciando Job de Publicação! Olhando a fila de aprovados...")
    run_publisher()


def cleanup_downloads() -> None:
    print(f"\n[CRON] {time.strftime('%H:%M:%S')} - Iniciando Limpeza de Mídias Antigas (> 3 dias)...")
    now = time.time()
    count = 0
    if os.path.exists("downloads"):
        for f in glob.glob("downloads/*"):
            if os.path.isfile(f) and os.stat(f).st_mtime < now - 3 * 86400:
                try:
                    os.remove(f)
                    count += 1
                except OSError:
                    pass
    print(f"[*] Limpeza concluída: {count} arquivos antigos deletados.")


def job_healthcheck() -> None:
    print(f"\n[CRON] {time.strftime('%H:%M:%S')} - Iniciando Check Médico de Estoque e Links Quebrados...")
    houve_modificacoes_vitrine = verify_all_active_products()
    if houve_modificacoes_vitrine:
        print("[CRON] Algum produto esgotou ou quebrou! Renderizando o HTML novo para proteger do Shadowban...")
        generate_html_vitrine()


def job_shopee_video() -> None:
    """Puxa do banco achados (itens aprovados, em formato de vídeo) e posta."""
    print(f"\n[CRON] {time.strftime('%H:%M:%S')} - Iniciando Auto-postagem Shopee Video...")

    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute(
            """
            SELECT a.id, a.texto_original, a.midia_path, p.link_afiliado
            FROM achados a
            JOIN produtos p ON a.id = p.achado_id
            WHERE a.status IN ('APPROVED', 'POSTED') AND (a.midia_path LIKE '%.mp4' OR a.midia_path LIKE '%.mov')
            LIMIT 1
            """
        )
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
