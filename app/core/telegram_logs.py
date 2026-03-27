import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Cria o próprio bot no BotFather e pega o Token. 
# Para saber o seu CHAT_ID, mande mensagem pro @userinfobot
BOT_TOKEN = os.getenv("TELEGRAM_ADMIN_BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("TELEGRAM_ADMIN_CHAT_ID")

def send_admin_log(message):
    """
    Manda um ping pro Telegram Privado da usuária quando uma ação crucial acontece
    (Ex: Produto foi postado no Insta, Vitrine foi atualizada).
    """
    if not BOT_TOKEN or not ADMIN_CHAT_ID:
        # Se ela não configurou ainda, printa no console silenciosamente.
        print(f"[LOG ADMIN] AVISO: {message}")
        return
        
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": ADMIN_CHAT_ID,
        "text": f"🤖 SIAA-2026 Informa:\n\n{message}"
    }
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Falha ao enviar log pro Telegram: {e}")
