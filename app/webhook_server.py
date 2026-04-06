import os
import re
import requests
from fastapi import FastAPI, Request, Response, Depends, HTTPException, status
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import uuid

# Corrige imports para ser executado da raiz do projeto
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.repository import AchadosRepository
from app.social_interactions.instagram_bot import detectar_gatilho, send_private_dm, post_public_reply
from app.core.logger import log_event
import logging

class WhatsAppMessage(BaseModel):
    event: str
    data: dict

app = FastAPI(title="SIAA-2026 Webhooks Server")

# Segurança de Mercado: Middleware e Headers
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"]) # Ajustar para o seu domínio em produção
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Ajustar para a URL da sua vitrine
    allow_methods=["*"],
    allow_headers=["*"],
)

EVOLUTION_API_SECRET = os.getenv("EVOLUTION_API_SECRET", "siaa_master_key_2026")

# ==========================================
# WEBHOOK GENÉRICO DE VERIFICAÇÃO META
# ==========================================
@app.get("/webhook")
async def verify_webhook(request: Request):
    """Endpoint de verificação genérico para webhooks da Meta."""
    # O 'Verify Token' que você definiu no painel da Meta
    verify_token = "SIAA_SECRET_2026"
    
    params = request.query_params
    if params.get("hub.verify_token") == verify_token:
        # Retorna apenas o challenge como texto puro (exigência da Meta)
        return Response(content=params.get("hub.challenge"), media_type="text/plain")
    return Response(content="Token de verificação inválido", status_code=403)

async def verify_api_key(request: Request):
    """Verifica se a requisição possui a chave secreta configurada no Evolution API."""
    api_key = request.headers.get("apikey") or request.headers.get("X-Evolution-API-Key")
    if api_key != EVOLUTION_API_SECRET:
        log_event(f"Tentativa de acesso não autorizado! IP: {request.client.host}", component="Security", event="AUTH_FAIL", status="CRITICAL", level=logging.WARNING)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: Evolution API Key missing or invalid"
        )
    return api_key

@app.middleware("http")
async def log_requests(request: Request, call_next):
    log_event(f"Request: {request.method} {request.url.path}", component="WebhookServer", event="HTTP_REQ")
    response = await call_next(request)
    log_event(f"Response: {response.status_code}", component="WebhookServer", event="HTTP_RES")
    return response

# ==========================================
# 1. WEBHOOK META (INSTAGRAM/FACEBOOK)
# ==========================================
META_VERIFY_TOKEN = os.getenv("META_VERIFY_TOKEN", "siaa2026_secreto")
META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN", "")
IG_USER_ID = os.getenv("IG_USER_ID", "")

@app.get("/webhook/meta")
async def verify_meta_webhook(request: Request):
    """Endpoint de verificação do Webhook (challenge da Meta)."""
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == META_VERIFY_TOKEN:
            print("[META WEBHOOK] Webhook verificado!")
            return Response(content=challenge, status_code=200)
    return Response(status_code=403)

@app.post("/webhook/meta")
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

# ==========================================
# 2. WEBHOOK WHATSAPP SCRAPER (EVOLUTION API)
# ==========================================
@app.post("/webhook/whatsapp", dependencies=[Depends(verify_api_key)])
async def process_whatsapp_scraper(payload: WhatsAppMessage):
    """Monitoramento de grupos do WhatsApp via Evolution API."""
    try:
        body = payload.dict()
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
                
            shopee_links = re.findall(r'(https?://shope\.ee/[a-zA-Z0-9]+|https?://shopee\.com\.br/[^\s]+)', caption)
            if shopee_links:
                file_path = f"app/mineracao/wa_media_{uuid.uuid4().hex[:8]}.jpg"
                texto_limpo = caption
                for lnk in shopee_links:
                    texto_limpo = texto_limpo.replace(lnk, "[LINK]")
                
                repo.add_achado(texto_limpo, file_path, shopee_links[0], categoria="WhatsApp")
                log_event(f"Oferta WhatsApp salva: {shopee_links[0]}", component="WebhookWhatsApp", event="MSG_CAPTURE", status="SUCCESS")
                print(f"[WHATSAPP SCRAPER] Oferta salva via Repository: {shopee_links[0]}")
                
        return {"status": "success"}
    except Exception as e:
        log_event(f"Erro no processamento do webhook WhatsApp: {str(e)}", component="WebhookWhatsApp", event="WEBHOOK_ERROR", status="ERROR", level=logging.ERROR)
        return Response(content='{"error": "Internal Server Error"}', status_code=500, media_type="application/json")

if __name__ == "__main__":
    uvicorn.run("webhook_server:app", host="0.0.0.0", port=6000, reload=True)
