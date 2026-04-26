import os
import time
import hmac
import hashlib
import json
import requests
from app.core.logger import log_event

class ShopeeAffiliateAPI:
    """
    Cliente Oficial da Shopee Affiliate Open API v2.
    Substitui a dependência de scraping do Telegram e gera links limpos, 
    bem como faz pesquisas inteligentes de estoque (Anti-Esgotamento).
    """
    def __init__(self):
        self.app_id = os.getenv("SHOPEE_APP_ID", "")
        self.app_secret = os.getenv("SHOPEE_APP_SECRET", "")
        self.base_url = os.getenv("SHOPEE_API_URL", "https://partner.shopeemobile.com")
        self.is_configured = bool(self.app_id and self.app_secret)

    def _generate_signature(self, payload: str, timestamp: str) -> str:
        """
        Gera a assinatura JWT (HMAC-SHA256) exigida pelos servidores da Shopee.
        Geralmente a signature string é "AppID + Timestamp + Payload" assinada pela Secret.
        """
        base_string = f"{self.app_id}{timestamp}{payload}"
        signature = hmac.new(
            self.app_secret.encode('utf-8'),
            base_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature

    def request_api(self, endpoint: str, payload: dict):
        if not self.is_configured:
            print("[SHOPEE API] ERRO: Faltam chaves de autenticação no .env (SHOPEE_APP_ID / SHOPEE_APP_SECRET)")
            return None

        timestamp = str(int(time.time()))
        payload_str = json.dumps(payload, separators=(',', ':'))
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": self._generate_signature(payload_str, timestamp),
            "Timestamp": timestamp,
            "AppId": self.app_id
        }

        url = f"{self.base_url}{endpoint}"
        try:
            res = requests.post(url, headers=headers, json=payload, timeout=15)
            data = res.json()
            if res.status_code == 200 and data.get("code") == 1:
                return data.get("data")
            else:
                print(f"[SHOPEE API ERRO] {data.get('msg', 'Erro Oculto')}")
                return None
        except Exception as e:
            print(f"[SHOPEE API CRASH] {e}")
            return None

    def search_similar_product(self, keyword: str, min_commission: float = 10.0):
        """
        Pesquisa produtos na central de afiliados usando uma palavra chave.
        Útil para o Sistema Anti-Esgotamento encontrar substitutos com boa comissão.
        """
        endpoint = "/api/v2/affiliate/offer/search"
        payload = {
            "keyword": keyword,
            "limit": 5,
            "sort_type": "sales" # Pega os mais vendidos
        }
        
        result = self.request_api(endpoint, payload)
        if result and "item_list" in result:
            for item in result["item_list"]:
                # Pega o primeiro que tiver comissão alta
                if float(item.get("commission_rate", 0)) >= min_commission:
                    return {
                        "shopee_id": item.get("item_id"),
                        "name": item.get("item_name"),
                        "price": item.get("price"),
                        "link": item.get("item_url"),
                        "image": item.get("image_url")
                    }
        return None

    def generate_affiliate_link(self, target_url: str):
        """
        Converte uma URL bruta da shopee no seu Link de Afiliado Rastreável.
        """
        endpoint = "/api/v2/affiliate/generate_short_link"
        payload = {
            "origin_url": target_url,
            "sub_ids": ["siaa_autobot"]
        }
        res = self.request_api(endpoint, payload)
        if res and "short_link" in res:
            return res["short_link"]
        return target_url # Se falhar, devolve a original
