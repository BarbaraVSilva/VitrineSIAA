import requests
import os
from dotenv import load_dotenv

# Carrega variáveis existentes para o script
load_dotenv(".env")

TOKEN = "EAARpqF7rfooBRFscEGgvbwIuTz5xsm3kIVmanw5vOpfr5qnL90ZBuWMnPzYXvEa1QWCHidZA5ZAva5VjGEzzs4SM22hjaSwc63CJL8KrveY1I3u90jObcpZBrgbf2AiQklKb6s5sZCi3yZAPCVZAR5VvxyplN8QAAkLg6jOFlyj2fcdVIsWsB564ZAR6OEu6MY9964TIvkFddNdt951qBeoBOVqCXvNwb7iyGMXrrd8ysEw6jILU35JHZCiC2SNS77IvLIgIFsp4sfyaorcrpFoUz"
APP_ID = os.getenv("META_APP_ID")
APP_SECRET = os.getenv("META_APP_SECRET")

def run_diagnostic():
    print("--- Diagnosticando Token Meta ---")
    
    # 1. Checar Permissões
    perm_url = f"https://graph.facebook.com/v20.0/me/permissions?access_token={TOKEN}"
    perms = requests.get(perm_url).json()
    print(f"Permissões: {[p['permission'] for p in perms.get('data', [])]}")
    
    # 2. Buscar Páginas e IDs de Instagram
    pages_url = f"https://graph.facebook.com/v20.0/me/accounts?access_token={TOKEN}"
    pages_data = requests.get(pages_url).json()
    
    found_any = False
    for page in pages_data.get("data", []):
        page_id = page['id']
        page_name = page['name']
        page_token = page['access_token']
        print(f"\n[Página Encontrada]: {page_name} (ID: {page_id})")
        
        # Buscar IG ligado
        ig_url = f"https://graph.facebook.com/v20.0/{page_id}?fields=instagram_business_account&access_token={page_token}"
        ig_data = requests.get(ig_url).json()
        
        if "instagram_business_account" in ig_data:
            ig_id = ig_data["instagram_business_account"]["id"]
            found_any = True
            print(f"  -> Instagram Business ID: {ig_id}")
            
            # 3. Gerar Long-lived Page Token
            if APP_ID and APP_SECRET:
                print(f"  -> Gerando Token de Longa Duração para a Página...")
                ll_url = f"https://graph.facebook.com/v20.0/oauth/access_token"
                params = {
                    "grant_type": "fb_exchange_token",
                    "client_id": APP_ID,
                    "client_secret": APP_SECRET,
                    "fb_exchange_token": page_token
                }
                ll_res = requests.get(ll_url, params=params).json()
                ll_token = ll_res.get("access_token")
                if ll_token:
                    print(f"  -> ✅ Token Vitalício/Longo gerado com sucesso!")
                    print(f"\n--- RECOMENDAÇÃO PARA O .env ---")
                    print(f"META_ACCESS_TOKEN={ll_token}")
                    print(f"META_PAGE_ID={page_id}")
                    print(f"IG_USER_ID={ig_id}")
                else:
                    print(f"  -> ❌ Erro ao gerar Long-lived: {ll_res}")
        else:
            print("  -> Nenhuma conta Instagram Business vinculada.")

    if not found_any:
        print("\n❌ Nenhuma conta de Instagram Business foi identificada. Verifique se a conta é Business e está ligada à página.")

if __name__ == "__main__":
    run_diagnostic()
