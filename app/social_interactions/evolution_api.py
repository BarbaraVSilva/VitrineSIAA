import os
import aiohttp
import logging
from app.core.logger import log_event

class EvolutionAPI:
    """
    Integração profissional com WhatsApp via Evolution API.
    Acesse a documentação: https://doc.evolution-api.com/
    """
    def __init__(self):
        self.base_url = os.getenv("EVOLUTION_API_URL", "http://localhost:8080")
        self.api_key = (os.getenv("EVOLUTION_API_TOKEN") or os.getenv("EVOLUTION_API_KEY") or "").strip()
        self.instance_name = os.getenv("EVOLUTION_INSTANCE", "SIAA_BOT")

    async def _send_request(self, endpoint: str, method: str = "POST", data: dict = None):
        url = f"{self.base_url}/{endpoint}/{self.instance_name}"
        headers = {
            "apikey": self.api_key,
            "Content-Type": "application/json"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(method, url, json=data, headers=headers) as response:
                    res_json = await response.json()
                    if response.status in [200, 201]:
                        return res_json
                    else:
                        log_event(f"Erro Evolution API ({response.status}): {res_json}", component="EvolutionAPI", status="ERROR")
                        return None
        except Exception as e:
            log_event(f"Falha de conexão com Evolution API: {e}", component="EvolutionAPI", status="CRITICAL")
            return None

    async def send_text(self, number: str, text: str):
        """Envia mensagem de texto para um número ou grupo (JID)."""
        data = {
            "number": number,
            "text": text,
            "delay": 1200,
            "linkPreview": True
        }
        return await self._send_request("message/sendText", data=data)

    async def send_media(self, number: str, media_url: str, caption: str, type: str = "image"):
        """Envia imagem ou vídeo com legenda."""
        endpoint = "message/sendMedia"
        data = {
            "number": number,
            "media": media_url,
            "caption": caption,
            "mediaType": type,
            "delay": 1500
        }
        return await self._send_request(endpoint, data=data)

    async def get_groups(self):
        """Lista todos os grupos que a instância participa."""
        return await self._send_request("group/fetchAllGroups", method="GET")

whatsapp = EvolutionAPI()
