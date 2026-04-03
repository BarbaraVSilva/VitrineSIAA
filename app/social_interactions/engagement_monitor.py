"""
SIAA 2026 — Monitor de Engajamento
Busca comentários e DMs recentes via Meta Graph API.
Atualização manual (disparada pelo painel Streamlit).
"""

import os
import requests

META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN", "")
META_PAGE_ID = os.getenv("META_PAGE_ID", "")
GRAPH_URL = "https://graph.instagram.com/v25.0"


def _headers():
    return {"Authorization": f"Bearer {META_ACCESS_TOKEN}"}


def fetch_recent_media() -> list[dict]:
    """Retorna as mídias (posts) recentes do usuário."""
    if not META_ACCESS_TOKEN or not META_PAGE_ID:
        return []
    try:
        url = f"{GRAPH_URL}/{META_PAGE_ID}/media"
        params = {"fields": "id,caption,media_type,timestamp,like_count,comments_count", "limit": 10}
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        return data.get("data", [])
    except Exception as e:
        print(f"[ENGAGEMENT] Erro ao buscar mídias: {e}")
        return []


def fetch_comments_for_media(media_id: str) -> list[dict]:
    """Retorna comentários de uma mídia específica."""
    if not META_ACCESS_TOKEN:
        return []
    try:
        url = f"{GRAPH_URL}/{media_id}/comments"
        params = {"fields": "id,text,username,timestamp", "limit": 20}
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        return data.get("data", [])
    except Exception as e:
        print(f"[ENGAGEMENT] Erro ao buscar comentários: {e}")
        return []


def fetch_recent_conversations() -> list[dict]:
    """Retorna conversas (DMs) recentes do Instagram."""
    if not META_ACCESS_TOKEN or not META_PAGE_ID:
        return []
    try:
        url = f"{GRAPH_URL}/{META_PAGE_ID}/conversations"
        params = {"fields": "id,updated_time,participants,messages{message,from,created_time}", "limit": 10}
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        return data.get("data", [])
    except Exception as e:
        print(f"[ENGAGEMENT] Erro ao buscar DMs: {e}")
        return []


def post_public_comment_reply(comment_id: str, text: str) -> bool:
    """
    Posta uma resposta PÚBLICA num comentário do Instagram.
    Requer permissão instagram_manage_comments.
    """
    if not META_ACCESS_TOKEN:
        print("[ENGAGEMENT] Token não configurado.")
        return False
    try:
        url = f"{GRAPH_URL}/{comment_id}/replies"
        payload = {"message": text, "access_token": META_ACCESS_TOKEN}
        r = requests.post(url, json=payload, timeout=10)
        result = r.json()
        if "id" in result:
            print(f"[ENGAGEMENT] ✅ Resposta pública postada no comentário {comment_id}")
            return True
        else:
            print(f"[ENGAGEMENT] ❌ Falha ao responder comentário: {result}")
            return False
    except Exception as e:
        print(f"[ENGAGEMENT] Erro ao responder comentário: {e}")
        return False


def get_api_status() -> dict:
    """Verifica se o token Meta está válido e retorna info básica."""
    if not META_ACCESS_TOKEN:
        return {"ok": False, "motivo": "META_ACCESS_TOKEN não configurado no .env"}
    try:
        r = requests.get(
            f"{GRAPH_URL}/me",
            params={"fields": "id,name,username", "access_token": META_ACCESS_TOKEN},
            timeout=8
        )
        data = r.json()
        if "error" in data:
            return {"ok": False, "motivo": data["error"].get("message", "Token inválido ou expirado")}
        return {"ok": True, "nome": data.get("name", ""), "username": data.get("username", ""), "id": data.get("id")}
    except Exception as e:
        return {"ok": False, "motivo": str(e)}
