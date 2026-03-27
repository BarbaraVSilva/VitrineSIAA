import os
import re
import requests
from fastapi import FastAPI, Request, Response
from pydantic import BaseModel
import uvicorn
import uuid

# Corrige imports para ser executado da raiz do projeto
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import get_connection
from app.social_interactions.instagram_bot import check_intent_with_ai, reply_to_comment, send_dm

app = FastAPI(title="SIAA-2026 Webhooks Server")

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
            print("[META WEBHOOK] Webhook verificado com sucesso!")
            return Response(content=challenge, status_code=200)
    return Response(status_code=403)

@app.post("/webhook/meta")
async def process_meta_webhook(request: Request):
    """Recebe os eventos (comentários) do Instagram em tempo real."""
    body = await request.json()
    
    if body.get("object") == "instagram":
        for entry in body.get("entry", []):
            for change in entry.get("changes", []):
                field = change.get("field")
                value = change.get("value", {})
                
                # Checar se é um comentário
                if field == "comments":
                    comment_text = value.get("text", "")
                    comment_id = value.get("id")
                    from_user = value.get("from", {}).get("id")
                    media_id = value.get("media", {}).get("id")
                    
                    if from_user == IG_USER_ID:
                        # Ignorar próprios comentários do bot
                        continue
                        
                    print(f"[META WEBHOOK] Novo comentário recebido: {comment_text}")
                    
                    # Verifica intenção de link usando IA
                    if check_intent_with_ai(comment_text):
                        print("[META WEBHOOK] Usuário quer link! Processando envio...")
                        # Idealmente, faria query no DB pra achar o link que corresponde a 'media_id'.
                        # Como não temos um mapeamento exato IG <-> Vitrine aqui, 
                        # podemos mandar o link da vitrine geral ou responder genérico na automação simples.
                        resposta = "Oii! O link especial deste produto está na minha Bio ou mandei no seu direct! 🛍️✨"
                        
                        # Responde o comentário e manda DM
                        if META_ACCESS_TOKEN:
                            reply_to_comment(comment_id, resposta, META_ACCESS_TOKEN)
                            send_dm(IG_USER_ID, from_user, "Aguarde, sua oferta chegou! Link da Vitrine: https://barbaravsilva.github.io/VitrineSIAA", META_ACCESS_TOKEN)
                            
    return {"status": "success"}

# ==========================================
# 2. WEBHOOK WHATSAPP SCRAPER (EVOLUTION API)
# ==========================================
@app.post("/webhook/whatsapp")
async def process_whatsapp_scraper(request: Request):
    """
    Recebe mensagens de instâncias do WhatsApp (Evolution API).
    Se for num grupo monitorado, extrai, baixa midia e joga em 'achados'.
    """
    body = await request.json()
    
    # Verifica tipo de evento da Evolution API (messages.insert)
    event_type = body.get("event")
    if event_type != "messages.upsert":
        return {"status": "ignored"}
        
    for msg_info in body.get("data", {}).get("message", {}).get("messages", []):
        msg_obj = msg_info.get("message", {})
        
        # Filtra grupos alvo (Opcional: checar remoteJid contra lista de grupos concorrentes no env)
        from_jid = msg_info.get("key", {}).get("remoteJid", "")
        if "@g.us" not in from_jid:
            continue # ignora dms
            
        # Pega a legenda (caption) de foto/video ou texto puro
        caption = ""
        media_url = "" # a Evolution pode fornecer CDN ou endpoint de dl, precisaria de uma call separada pra baixar
        
        if "imageMessage" in msg_obj:
            caption = msg_obj["imageMessage"].get("caption", "")
            has_media = True
        elif "videoMessage" in msg_obj:
            caption = msg_obj["videoMessage"].get("caption", "")
            has_media = True
        elif "conversation" in msg_obj:
            caption = msg_obj["conversation"]
            has_media = False
        else:
            continue
            
        if not caption:
            continue
            
        # Tenta achar link shopee na legenda
        shopee_links = re.findall(r'(https?://shope\.ee/[a-zA-Z0-9]+|https?://shopee\.com\.br/[^\s]+)', caption)
        if shopee_links:
            # Baixar midia (simulado para brevidade já q evolution precisa baixar via GET endpoint)
            # Na real usaria `EvolutionAPI/message/downloadMedia` e salvaria local
            file_path = f"app/mineracao/wa_media_{uuid.uuid4().hex[:8]}.jpg" if has_media else ""
            
            # Limpa o link do concorrente usando heurística básica
            texto_limpo = caption
            for lnk in shopee_links:
                texto_limpo = texto_limpo.replace(lnk, "[LINK]")
            
            # Adiciona ao banco como PENDING (para o human preencher o dashboard)
            conn = get_connection()
            c = conn.cursor()
            c.execute(
                "INSERT INTO achados (texto_original, midia_path, link_original, status, categoria) VALUES (?, ?, ?, ?, ?)",
                (texto_limpo, file_path, shopee_links[0], 'PENDING', 'Geral')
            )
            conn.commit()
            conn.close()
            print(f"[WHATSAPP SCRAPER] Oferta chupada e jogada pra base: {shopee_links[0]}")
            
    return {"status": "success"}

if __name__ == "__main__":
    print("🚀 Iniciando Servidor de Webhooks (Meta & WhatsApp)... na porta 8000")
    uvicorn.run("webhook_server:app", host="0.0.0.0", port=8000, reload=True)
