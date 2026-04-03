"""
SIAA 2026 — Auto-DM Bot (Clone ManyChat)
Webhook FastAPI que escuta comentários do Instagram e:
  1. Envia DM privado com o link afiliado quando detecta palavras-gatilho
  2. Responde PUBLICAMENTE no comentário com mensagem curta (opcional, por gatilho)
  3. Registra cada disparo na tabela bot_logs do SQLite
"""

from fastapi import FastAPI, Request
import uvicorn
import os
import requests
import re
import sqlite3
from app.core.database import get_connection

app = FastAPI(title="SIAA Auto-DM Bot (ManyChat Clone)")

META_VERIFY_TOKEN = os.getenv("META_VERIFY_TOKEN", "siaa_super_secret")
META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN", "")
META_PAGE_ID = os.getenv("META_PAGE_ID", "")
GRAPH_URL = "https://graph.instagram.com/v25.0"

# Palavras-gatilho padrão (podem ser sobrescritas via banco futuramente)
GATILHOS_PADRAO = ["quero", "link", "onde compra", "quanto custa", "manda o link", "eu quero"]


def log_bot_disparo(tipo: str, user_id: str, comment_id: str, produto_id,
                    palavra_gatilho: str, resposta: str):
    """Registra disparo do bot na tabela bot_logs."""
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("""
            INSERT INTO bot_logs (tipo, user_id, comment_id, produto_id, palavra_gatilho, resposta_enviada)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (tipo, user_id, comment_id, produto_id, palavra_gatilho, resposta))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[AUTO-DM LOG] Erro ao registrar disparo: {e}")


def get_gatilhos_do_banco() -> list[str]:
    """Busca palavras-gatilho configuradas no banco (futuro: tabela config)."""
    return GATILHOS_PADRAO


def detectar_gatilho(texto: str) -> str | None:
    """Retorna a palavra-gatilho encontrada no texto, ou None."""
    texto_lower = texto.lower().strip()
    for g in get_gatilhos_do_banco():
        if g in texto_lower:
            return g
    return None


def buscar_link_produto(prod_id: str | None) -> tuple[str, int | None]:
    """Retorna (link_afiliado, produto_id) encontrado para o ID informado."""
    vitrine_link = "https://barbaravsilva.github.io/VitrineSIAA"
    if prod_id:
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("SELECT id, link_afiliado FROM produtos WHERE id = ?", (prod_id,))
            row = c.fetchone()
            conn.close()
            if row:
                return row[1], row[0]
        except Exception:
            pass
    # Sem produto específico: devolve vitrine
    return vitrine_link, None


@app.get("/webhook")
async def verify_webhook(request: Request):
    """Validação obrigatória do Meta Developers."""
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == META_VERIFY_TOKEN:
        print("[AUTO-DM] ✅ Webhook Meta verificado!")
        return int(challenge)
    return {"status": "error", "message": "Token inválido"}, 403


@app.post("/webhook")
async def receive_webhook(request: Request):
    """
    Escuta eventos de comentário.
    Só dispara DM + resposta pública se detectar palavra-gatilho.
    """
    body = await request.json()

    if body.get("object") in ["page", "instagram"]:
        for entry in body.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})

                if change.get("field") == "comments" and value.get("item") == "comment":
                    comment_text = value.get("text", "")
                    comment_id = value.get("id", "")
                    user_id = value.get("from", {}).get("id", "")

                    gatilho = detectar_gatilho(comment_text)
                    if not gatilho:
                        continue  # Ignora comentário sem palavra-gatilho

                    print(f"[AUTO-DM] 🔥 Gatilho '{gatilho}' detectado: '{comment_text[:60]}'")

                    # Procura número de produto mencionado no comentário
                    match = re.search(r'\b(\d+)\b', comment_text)
                    prod_id_str = match.group(1) if match else None

                    link, prod_id = buscar_link_produto(prod_id_str)

                    # 1. Envia DM privado
                    if prod_id:
                        texto_dm = (
                            f"Oii! 💛 Aqui está o link do Achado #{prod_id} que você pediu:\n"
                            f"{link}\n\n"
                            f"Mais promos imperdíveis: https://barbaravsilva.github.io/VitrineSIAA"
                        )
                    else:
                        texto_dm = (
                            f"Oii! 💛 Pra não perder nenhuma promoção, dá uma olhada no nosso catálogo completo:\n"
                            f"https://barbaravsilva.github.io/VitrineSIAA"
                        )

                    sucesso_dm = send_private_dm(comment_id, texto_dm)

                    # 2. Resposta PÚBLICA curta no comentário (só gatilho)
                    texto_publico = "Te mandei no direct! 💌"
                    sucesso_pub = post_public_reply(comment_id, texto_publico)

                    # 3. Registra no banco
                    log_bot_disparo(
                        tipo="DM+PUBLICO" if sucesso_dm and sucesso_pub else "DM",
                        user_id=user_id,
                        comment_id=comment_id,
                        produto_id=prod_id,
                        palavra_gatilho=gatilho,
                        resposta=texto_dm[:200]
                    )

    return {"status": "EVENT_RECEIVED"}


def send_private_dm(comment_id: str, texto: str) -> bool:
    """Envia DM pelo endpoint de Private Replies da Meta."""
    if not META_ACCESS_TOKEN or not META_PAGE_ID:
        print("[AUTO-DM] ERRO: Token / Page ID ausentes.")
        return False
    try:
        url = f"{GRAPH_URL}/{META_PAGE_ID}/messages"
        payload = {
            "recipient": {"comment_id": comment_id},
            "message": {"text": texto},
            "access_token": META_ACCESS_TOKEN
        }
        res = requests.post(url, json=payload, timeout=10)
        data = res.json()
        if "message_id" in data:
            print(f"[AUTO-DM] ✅ DM enviado com sucesso!")
            return True
        print(f"[AUTO-DM] ❌ Meta rejeitou o DM: {data}")
        return False
    except Exception as e:
        print(f"[AUTO-DM] Falha de conexão: {e}")
        return False


def post_public_reply(comment_id: str, texto: str) -> bool:
    """Responde publicamente a um comentário no Instagram."""
    if not META_ACCESS_TOKEN:
        return False
    try:
        url = f"{GRAPH_URL}/{comment_id}/replies"
        payload = {"message": texto, "access_token": META_ACCESS_TOKEN}
        res = requests.post(url, json=payload, timeout=10)
        data = res.json()
        if "id" in data:
            print(f"[AUTO-DM] ✅ Resposta pública postada!")
            return True
        print(f"[AUTO-DM] ⚠️ Falha na resposta pública: {data}")
        return False
    except Exception as e:
        print(f"[AUTO-DM] Erro na resposta pública: {e}")
        return False


if __name__ == "__main__":
    print("🚀 [AUTO-DM] Bot de Comentários SIAA escutando na porta 8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
