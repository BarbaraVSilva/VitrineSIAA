import os
import requests
import time
import hashlib
import hmac
from dotenv import load_dotenv

load_dotenv()

APP_ID = os.getenv("SHOPEE_APP_ID")
APP_SECRET = os.getenv("SHOPEE_APP_SECRET")

def get_affiliate_link(original_link):
    """
    Converte um link bruto no seu link de Afiliado da Shopee consumindo a API oficial (Open Platform).
    Faz o hash da chave HMAC SHA256 exigido nas requisições seguras da Shopee.
    """
    if not APP_ID or not APP_SECRET:
        print("[SHOPEE API] ALERTA: Credenciais AppID/AppSecret Ausentes.")
        print("[SHOPEE API] Entrando em Modo Seguro (Dummy Link) apenas para testes.")
        return f"{original_link}?aff_id=TESTE_LOCAL"
        
    print(f"Iniciando conversão via SHOPEE OPEN API para o link: {original_link}")
    
    host = "https://partner.shopeemobile.com"
    path = "/api/v2/affiliate/generate_short_link"
    timestamp = int(time.time())
    
    # Assinatura baseada no partner_id, path e timestamp
    base_string = f"{APP_ID}{path}{timestamp}"
    sign = hmac.new(APP_SECRET.encode(), base_string.encode(), hashlib.sha256).hexdigest()
    
    url = f"{host}{path}?partner_id={APP_ID}&timestamp={timestamp}&sign={sign}"
    
    payload = {
        "originUrl": original_link,
        "subIds": ["siaa_bot", "telegram_tracker"]
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        data = response.json()
        
        if data.get("error") == "":
            print("[SHOPEE API] Sucesso! Encurtador e Rastreador aplicados.")
            return data["response"]["shortLink"]
        else:
            print(f"[SHOPEE API] Erro fornecido pela Shopee: {data.get('error')} - {data.get('message')}")
            # Em caso de erro na resposta, mantemos o link sem rastreio para não quebrar a vitrine
            return original_link
    except Exception as e:
        print(f"[SHOPEE API] Timeout ou Erro Rest: {e}")
        return original_link


def buscar_backups_por_palavra_chave(keyword):
    """
    Rascunho de Busca por Palavras-Chave.
    Em um cenário real, aqui seria feita uma requisição GET para a API Oficial da Shopee
    buscando itens similares / mais vendidos do mesmo nicho.
    Como a Shopee exige tokens avançados para isso, retornaremos mock links para testes de Redundância.
    """
    print(f"[SHOPEE API - BUSCA] Procurando reservas em alta para a keyword: '{keyword}'...")
    
    # Simulação da resposta da API
    time.sleep(1)
    
    return [
        f"https://shopee.com.br/search?keyword={keyword.replace(' ', '+')}&backup=1",
        f"https://shopee.com.br/search?keyword={keyword.replace(' ', '+')}&backup=2"
    ]

if __name__ == "__main__":
    link_mock = "https://shopee.com.br/produto/exemplo"
    print(f"Tentando converter: {link_mock}")
    link_convertido = get_affiliate_link(link_mock)
    print(f"Resultado Final: {link_convertido}")
