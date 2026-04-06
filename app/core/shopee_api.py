import os
import requests
import time
import hashlib
import hmac
from dotenv import load_dotenv

load_dotenv()

APP_ID = os.getenv("SHOPEE_APP_ID")
APP_SECRET = os.getenv("SHOPEE_APP_SECRET")

def get_affiliate_link(original_link, sub_id=None):
    """
    Converte um link bruto no seu link de Afiliado da Shopee consumindo a API oficial (Open Platform).
    Adiciona Sub-ID para rastreio de Analytics.
    """
    if not APP_ID or not APP_SECRET:
        print("[SHOPEE API] ALERTA: Credenciais AppID/AppSecret Ausentes.")
        print("[SHOPEE API] Entrando em Modo Seguro (Dummy Link) apenas para testes.")
        s_id = f"&sub_id={sub_id}" if sub_id else ""
        return f"{original_link}?aff_id=TESTE_LOCAL{s_id}"
        
    print(f"Iniciando conversão via SHOPEE OPEN API para o link: {original_link}")
    
    host = "https://partner.shopeemobile.com"
    path = "/api/v2/affiliate/generate_short_link"
    timestamp = int(time.time())
    
    # Assinatura baseada no partner_id, path e timestamp
    base_string = f"{APP_ID}{path}{timestamp}"
    sign = hmac.new(APP_SECRET.encode(), base_string.encode(), hashlib.sha256).hexdigest()
    
    url = f"{host}{path}?partner_id={APP_ID}&timestamp={timestamp}&sign={sign}"
    
    # Injeta Sub-ID se disponível
    payload = {
        "originUrl": original_link,
        "subIds": [sub_id] if sub_id else ["siaa_bot"]
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        data = response.json()
        
        if data.get("error") == "":
            print(f"[SHOPEE API] Sucesso! Rastreador aplicado: {sub_id or 'padrão'}")
            return data["response"]["shortLink"]
        else:
            print(f"[SHOPEE API] Erro fornecido pela Shopee: {data.get('error')} - {data.get('message')}")
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
