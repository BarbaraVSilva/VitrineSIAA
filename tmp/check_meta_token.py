import requests
import os

TOKEN = "EAARpqF7rfooBRLS3Tl33PNDK4ZB7EZClhiOguBQC4tviUC6bSc04bUvO9f4k1LPF9osINp92vuC00JfNZBTktrmtGCaQJAMY3GoJfHjDRr38IdS9ZBe9okZAkZBO7yQIIRIjS4hWQJxptybxXZCZBGlCCEy8jIDGlZBkvmWVgctEHwpRZCrbk3GEiq2T2u41aEUfotUiE2rBLdNRDHclszmwn4i9r5xyGS423DA5MufJfEUU6UNZAqFBCBEdGM7VtmkheRPkM3nXMcIC5dI2AmrjocNLAZDZD"

def check_token():
    # 1. Obter informações do usuário e páginas
    url = f"https://graph.facebook.com/v20.0/me/accounts?access_token={TOKEN}"
    try:
        res = requests.get(url)
        data = res.json()
        
        if "error" in data:
            print(f"Erro ao buscar páginas: {data['error']['message']}")
            return

        pages = data.get("data", [])
        if not pages:
            print("Nenhuma página encontrada para este token.")
            return

        print("\n--- Páginas Encontradas ---")
        for page in pages:
            page_id = page['id']
            page_name = page['name']
            page_token = page['access_token']
            print(f"Página: {page_name} (ID: {page_id})")
            print(f"Page Access Token: {page_token[:20]}...")
            
            # 2. Buscar conta do Instagram vinculada à página
            ig_url = f"https://graph.facebook.com/v20.0/{page_id}?fields=instagram_business_account&access_token={page_token}"
            ig_res = requests.get(ig_url)
            ig_data = ig_res.json()
            
            if "instagram_business_account" in ig_data:
                ig_id = ig_data["instagram_business_account"]["id"]
                print(f"  -> Instagram Business ID vinculado: {ig_id}")
            else:
                print("  -> Nenhuma conta Instagram Business vinculada a esta página.")
                
    except Exception as e:
        print(f"Erro de conexão: {e}")

if __name__ == "__main__":
    check_token()
