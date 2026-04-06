"""Webhooks Meta e Evolution (WhatsApp)."""

from __future__ import annotations

import logging
import os
import re
import uuid

from fastapi import APIRouter, Depends, Request, Response

from app.api.deps import verify_evolution_api_key
from app.api.schemas import WhatsAppMessage
from app.core.logger import log_event
from app.core.repository import AchadosRepository
from app.social_interactions.instagram_bot import detectar_gatilho, post_public_reply, send_private_dm

router = APIRouter(tags=["webhooks"])

# Obrigatório no .env (sem defaults fracos). META_HUB_VERIFY_TOKEN para GET /webhook; se vazio, usa META_VERIFY_TOKEN.
META_VERIFY_TOKEN = (os.getenv("META_VERIFY_TOKEN") or "").strip()
META_HUB_VERIFY_TOKEN = (os.getenv("META_HUB_VERIFY_TOKEN") or META_VERIFY_TOKEN).strip()
META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN", "")
IG_USER_ID = os.getenv("IG_USER_ID", "")


def _model_to_dict(model: WhatsAppMessage) -> dict:
    if hasattr(model, "model_dump"):
        return model.model_dump()
    return model.dict()


@router.get("/webhook")
async def verify_webhook(request: Request):
    """Endpoint de verificação genérico para webhooks da Meta."""
    if not META_HUB_VERIFY_TOKEN:
        return Response(content="Servidor não configurado (META_HUB_VERIFY_TOKEN / META_VERIFY_TOKEN)", status_code=503)
    params = request.query_params
    if params.get("hub.verify_token") == META_HUB_VERIFY_TOKEN:
        return Response(content=params.get("hub.challenge") or "", media_type="text/plain")
    return Response(content="Token de verificação inválido", status_code=403)


@router.get("/webhook/meta")
async def verify_meta_webhook(request: Request):
    """Endpoint de verificação do Webhook (challenge da Meta)."""
    if not META_VERIFY_TOKEN:
        return Response(content="META_VERIFY_TOKEN não configurado", status_code=503)

    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == META_VERIFY_TOKEN:
            print("[META WEBHOOK] Webhook verificado!")
            return Response(content=challenge, status_code=200)
    return Response(status_code=403)


@router.post("/webhook/meta")
async def process_meta_webhook(request: Request):
    """Recebe eventos do Instagram."""
    body = await request.json()

    if body.get("object") == "instagram":
        for entry in body.get("entry", []):
            for change in entry.get("changes", []):
                field = change.get("field")
                value = change.get("value", {})

                if field == "comments":
                    comment_text = value.get("text", "")
                    comment_id = value.get("id")
                    from_user = value.get("from", {}).get("id")

                    if from_user == IG_USER_ID:
                        continue

                    gatilho = detectar_gatilho(comment_text)
                    if gatilho:
                        texto_dm = "Link da Vitrine: https://barbaravsilva.github.io/VitrineSIAA"
                        if META_ACCESS_TOKEN:
                            send_private_dm(comment_id, texto_dm)
                            post_public_reply(comment_id, "Oii! Te mandei no direct! 🛍️✨")

    return {"status": "success"}


@router.post("/webhook/whatsapp", dependencies=[Depends(verify_evolution_api_key)])
async def process_whatsapp_scraper(payload: WhatsAppMessage):
    """Monitoramento de grupos do WhatsApp via Evolution API."""
    try:
        body = _model_to_dict(payload)
        repo = AchadosRepository()

        event_type = body.get("event")
        if event_type != "messages.upsert":
            return {"status": "ignored"}

        messages = body.get("data", {}).get("message", {}).get("messages", [])
        for msg_info in messages:
            msg_obj = msg_info.get("message", {})
            from_jid = msg_info.get("key", {}).get("remoteJid", "")

            if "@g.us" not in from_jid:
                continue

            caption = ""
            if "imageMessage" in msg_obj:
                caption = msg_obj["imageMessage"].get("caption", "")
            elif "videoMessage" in msg_obj:
                caption = msg_obj["videoMessage"].get("caption", "")
            elif "conversation" in msg_obj:
                caption = msg_obj["conversation"]
            else:
                continue

            if not caption:
                continue

            shopee_links = re.findall(
                r"(https?://shope\.ee/[a-zA-Z0-9]+|https?://shopee\.com\.br/[^\s]+)", caption
            )
            if shopee_links:
                file_path = f"app/mineracao/wa_media_{uuid.uuid4().hex[:8]}.jpg"
                texto_limpo = caption
                for lnk in shopee_links:
                    texto_limpo = texto_limpo.replace(lnk, "[LINK]")

                repo.add_achado(texto_limpo, file_path, shopee_links[0], categoria="WhatsApp")
                log_event(
                    f"Oferta WhatsApp salva: {shopee_links[0]}",
                    component="WebhookWhatsApp",
                    event="MSG_CAPTURE",
                    status="SUCCESS",
                )
                print(f"[WHATSAPP SCRAPER] Oferta salva via Repository: {shopee_links[0]}")

        return {"status": "success"}
    except Exception as e:
        log_event(
            f"Erro no processamento do webhook WhatsApp: {str(e)}",
            component="WebhookWhatsApp",
            event="WEBHOOK_ERROR",
            status="ERROR",
            level=logging.ERROR,
        )
        return Response(
            content='{"error": "Internal Server Error"}',
            status_code=500,
            media_type="application/json",
        )
