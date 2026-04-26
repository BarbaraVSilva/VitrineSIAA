import os
import time
import requests
from app.core.logger import log_event

class MetaGraphPublisher:
    """
    Substitui a frágil automação de navegadores (Chrome/Selenium) pelas 
    chamadas nativas super-rápidas da API Graph da Meta.
    """
    def __init__(self):
        self.access_token = os.getenv("META_ACCESS_TOKEN", "")
        self.ig_user_id = os.getenv("META_IG_USER_ID", "") # ID conectada à sua Page
        self.fb_page_id = os.getenv("META_PAGE_ID", "")
        self.graph_url = "https://graph.facebook.com/v18.0"
        
    def _validate_config(self) -> bool:
        if not self.access_token or not self.ig_user_id:
            msg = "[META API] ERRO: Credenciais ausentes no .env (META_ACCESS_TOKEN e META_IG_USER_ID)."
            print(msg)
            log_event(msg, component="MetaPublisher", status="ERROR")
            return False
        return True

    def publish_to_instagram(self, media_url: str, caption: str, is_video: bool = False) -> bool:
        """
        Publica foto ou vídeo (Reels) no Instagram via Graph API nativo.
        A mídia deve ser servida via URL. Para arquivos locais temporários, você pode precisar 
        de um bucket S3, imgur temporário, ou expor o próprio localhost via ngrok.
        Por simplicidade, o SIAA pode usar o Link Original extraído pra a API consumir.
        """
        if not self._validate_config():
            return False
            
        print(f"[META API] 🚀 Preparando para criar contêiner de mídia no Instagram (Video: {is_video})...")
        
        # 1. Cria o contêiner (Sobe o arquivo pros servidores da Meta)
        container_url = f"{self.graph_url}/{self.ig_user_id}/media"
        
        payload = {
            "caption": caption,
            "access_token": self.access_token
        }
        
        if is_video:
            payload["media_type"] = "REELS"
            payload["video_url"] = media_url
        else:
            payload["image_url"] = media_url
            
        try:
            # Envia pedido de criação
            res = requests.post(container_url, data=payload)
            res_json = res.json()
            
            if "id" not in res_json:
                print(f"[META API] ❌ Falha ao criar contêiner: {res_json}")
                return False
                
            creation_id = res_json["id"]
            print(f"[META API] ✅ Contêiner criado [{creation_id}]. Status: aguardando prcessamento da Meta...")
            
            # Se for vídeo, a meta processa o encode, precisamos aguardar
            if is_video:
                time.sleep(15) 
                
            # 2. Publica o contêiner para ir ao ar no Feed/Reels
            publish_url = f"{self.graph_url}/{self.ig_user_id}/media_publish"
            pub_payload = {
                "creation_id": creation_id,
                "access_token": self.access_token
            }
            
            pub_res = requests.post(publish_url, data=pub_payload)
            pub_json = pub_res.json()
            
            if "id" in pub_json:
                post_id = pub_json["id"]
                print(f"[META API] 🌟 SUCESSO ABSOLUTO! Post no ar no Instagram. ID: {post_id}")
                log_event(f"Post Instagram bem-sucedido via Meta API: {post_id}", component="MetaPublisher", status="SUCCESS")
                return True
            else:
                print(f"[META API] ❌ Falha na publicação final: {pub_json}")
                return False
                
        except Exception as e:
            print(f"[META API] CRASH INESPERADO ao contatar Meta: {e}")
            return False
