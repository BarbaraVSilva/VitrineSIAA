import os
import requests
import mimetypes

def publish_to_whatsapp_group(jid: str, text: str, media_path: str = None) -> bool:
    """
    Envia uma mensagem (com ou sem mídia) para um grupo de WhatsApp
    utilizando a Evolution API.
    """
    # Configurações da Evolution API
    base_url = os.getenv("EVOLUTION_API_URL", "http://localhost:8080")
    instance_name = os.getenv("EVOLUTION_INSTANCE_NAME", "siaa")
    api_key = (os.getenv("EVOLUTION_API_KEY") or os.getenv("EVOLUTION_API_TOKEN") or "").strip()
    if not api_key:
        print("[WHATSAPP PUBLISHER] EVOLUTION_API_KEY / EVOLUTION_API_TOKEN não configurados.")
        return False

    headers = {
        "apikey": api_key
    }

    try:
        if media_path and os.path.exists(media_path):
            # Endpoint para envio de mídia com legenda
            url = f"{base_url}/message/sendMedia/{instance_name}"
            
            # Detecta o mimetype
            mime_type, _ = mimetypes.guess_type(media_path)
            if not mime_type:
                mime_type = "application/octet-stream"

            caption_json = text.replace("\\", "\\\\").replace('"', '\\"')
            data = {
                "number": jid,
                "options": '{"delay": 1200, "presence": "composing"}',
                "mediaMessage": '{"mediaType": "'
                + ("video" if "video" in mime_type else "image")
                + '", "caption": "'
                + caption_json
                + '"}',
            }

            with open(media_path, "rb") as media_fp:
                files = {"file": (os.path.basename(media_path), media_fp, mime_type)}
                response = requests.post(url, headers=headers, data=data, files=files)
            
        else:
            # Endpoint para texto simples
            url = f"{base_url}/message/sendText/{instance_name}"
            payload = {
                "number": jid,
                "text": text,
                "options": {
                    "delay": 1200,
                    "presence": "composing"
                }
            }
            # Se não tem media, json puro
            headers_json = {"apikey": api_key, "Content-Type": "application/json"}
            response = requests.post(url, headers=headers_json, json=payload)

        if response.status_code in [200, 201]:
            print(f"[WHATSAPP PUBLISHER] ✅ Mensagem enviada para {jid}")
            return True
        else:
            print(f"[WHATSAPP PUBLISHER] ❌ Falha ao enviar para {jid}: {response.text}")
            return False

    except Exception as e:
        print(f"[WHATSAPP PUBLISHER ERRO] Falha na comunicação com o gateway: {e}")
        return False

if __name__ == "__main__":
    # Teste
    print("Testando envio para WhatsApp (Evolution API)...")
    # Coloque o JID do seu grupo aqui ex: 120363030303030303@g.us
    # publish_to_whatsapp_group("120363030303030303@g.us", "Teste de mensagem SIAA-2026", "test_base.mp4")
