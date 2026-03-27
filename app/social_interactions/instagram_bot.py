import os
import requests
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Variáveis Necessárias no .env:
# META_ACCESS_TOKEN
# IG_USER_ID

def check_intent_with_ai(comment_text: str) -> bool:
    """Usa IA para determinar se o comentário pede o link."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        # Fallback de palavras-chave
        keywords = ["link", "quero", "manda", "gostei", "amem", "eu", "passa", "qual"]
        return any(kw in comment_text.lower() for kw in keywords)

    client = OpenAI(api_key=api_key)
    prompt = f"O usuário comentou: '{comment_text}'. Ele está demonstrando interesse em comprar, pedindo link ou preço? Responda APENAS 'SIM' ou 'NAO'."
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_tokens=10
        )
        return "SIM" in response.choices[0].message.content.upper()
    except:
        return False

def reply_to_comment(comment_id: str, message: str, token: str):
    """Responde publicamente ao comentário no Instagram."""
    url = f"https://graph.facebook.com/v19.0/{comment_id}/replies"
    payload = {"message": message, "access_token": token}
    requests.post(url, json=payload)

def send_dm(ig_user_id: str, recipient_id: str, message: str, token: str):
    """Envia o link no privado."""
    url = f"https://graph.facebook.com/v19.0/{ig_user_id}/messages"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message},
        "access_token": token
    }
    requests.post(url, json=payload)

def run_social_interactions():
    """Varre comentários recentes, interpreta com IA e dispara DMs."""
    print("[IG BOT] 🤖 Iniciando verificação de novos comentários nas redes sociais...")
    token = os.getenv("META_ACCESS_TOKEN")
    ig_user_id = os.getenv("IG_USER_ID")
    
    if not token or not ig_user_id:
        print("[IG BOT] ⚠️ 'META_ACCESS_TOKEN' ou 'IG_USER_ID' não definidos no .env. Ignorando checagem.")
        return
        
    try:
        # Pega a lista das últimas mídias
        url_media = f"https://graph.facebook.com/v19.0/{ig_user_id}/media?fields=id,comments&access_token={token}"
        res = requests.get(url_media)
        
        if res.status_code == 200:
            data = res.json()
            for item in data.get('data', []):
                # Para cada mídia, olha os comentários
                comments = item.get('comments', {}).get('data', [])
                for comment in comments:
                    texto = comment['text']
                    if check_intent_with_ai(texto):
                        print(f"[IG BOT] Comentário de interesse detectado: '{texto}'. Enviando DM...")
                        # O ideal é salvar num banco q já respondeu esse 'comment_id' para não duplicar.
                        # send_dm(ig_user_id, comment['from']['id'], "Aqui está o seu link Vip: [LINK]", token)
                        # reply_to_comment(comment['id'], "Link enviado no direct! 🚀", token)
            print("[IG BOT] ✅ Verificação concluída com sucesso.")
        else:
            print(f"[IG BOT ERRO] {res.text}")
    except Exception as e:
        print(f"[IG BOT ERRO EXCEÇÃO] {e}")

if __name__ == "__main__":
    run_social_interactions()
