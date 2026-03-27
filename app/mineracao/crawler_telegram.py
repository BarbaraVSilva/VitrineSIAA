import os
import re
import asyncio
from telethon import TelegramClient, events
from dotenv import load_dotenv

load_dotenv()

# Configurações buscando do ambiente
API_ID = os.getenv("TELEGRAM_API_ID", "")
API_HASH = os.getenv("TELEGRAM_API_HASH", "")
PHONE = os.getenv("TELEGRAM_PHONE_NUMBER", "")

# Agora suporta múltiplos canais divididos por vírgula no .env
CHANNELS_ENV = os.getenv("TELEGRAM_TARGET_CHANNELS", "@achadinhos_shopee")
TARGET_CHANNELS = [ch.strip() for ch in CHANNELS_ENV.split(',')]

# Regex simples para buscar links https
LINK_REGEX = re.compile(r'(https?://[^\s]+)')

# Inicializando o cliente com sessão local salva em "siaa_session.session"
client = TelegramClient('siaa_session', API_ID, API_HASH)

async def download_media(message, dest_folder="downloads"):
    """
    Baixa arquivo/mídia associada à mensagem.
    """
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)
        
    if message.media:
        print("Mídia encontrada, baixando...")
        path = await message.download_media(file=dest_folder)
        print(f"Salvo em: {path}")
        return path
    return None

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from app.core.database import get_connection

def extract_links(text):
    """
    Extrai todos os links shopee (shope.ee e links normais).
    """
    if not text:
        return []
    urls = LINK_REGEX.findall(text)
    # Retorna só se tiver relação com shopee
    return [l for l in urls if "shopee" in l.lower() or "shope.ee" in l.lower()]

@client.on(events.NewMessage(chats=TARGET_CHANNELS))
async def new_message_handler(event):
    message = event.message
    text = message.message
    
    # 1. Extrair os Links para a Shopee do corpo do texto
    shopee_links = extract_links(text)
    
    # 2. Baixar as Mídias
    media_path = await download_media(message)
    
    if shopee_links or media_path:
        # Pega apenas o primeiro link relevante para a vitrine
        primeiro_link = shopee_links[0] if shopee_links else ""
        
        # Extrai foto do vídeo (se for mp4 ou similar)
        import sys
        sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
        from app.mineracao.editor_ia import extract_frame_from_video
        
        frame_foto = None
        if media_path and media_path.lower().endswith(('.mp4', '.mov')):
            frame_foto = extract_frame_from_video(media_path)
            
        # Extrair uma keyword básica do texto para buscar reservas na shopee
        from app.core.shopee_api import buscar_backups_por_palavra_chave
        keyword_base = " ".join(text.split()[:3]) if text else "achadinho"
        backups = buscar_backups_por_palavra_chave(keyword_base)
        
        b1 = backups[0] if len(backups) > 0 else ""
        b2 = backups[1] if len(backups) > 1 else ""
        
        print("="*40)
        print(f"--- NOVO ACHADINHO ENCONTRADO ---")
        print(f"Texto: {text[:50]}...")
        print(f"Link Original: {primeiro_link}")
        print(f"Link Reserva 1 (Auto): {b1}")
        print(f"Link Reserva 2 (Auto): {b2}")
        print("="*40)
        
        # Salva no banco de dados para a triagem do app.py
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute(
                "INSERT INTO achados (texto_original, midia_path, cover_path, link_original, link_backup_1, link_backup_2, status) VALUES (?, ?, ?, ?, ?, ?, 'PENDING')",
                (text, media_path, frame_foto, primeiro_link, b1, b2)
            )
            conn.commit()
            conn.close()
            print("=> Salvo no banco de dados com sucesso! Aguardando aprovação no Streamlit.")
        except Exception as e:
            print(f"=> Erro ao salvar no banco: {e}")

async def main():
    print(f"Iniciando o Crawler. Monitorando os canais/grupos: {', '.join(TARGET_CHANNELS)}")
    # Irá pedir o código enviado pro celular apenas na primeira vez
    await client.start(phone=PHONE)
    print("Conectado! Aguardando novas publicações...")
    # Bloqueia a execução enquanto escuta o Telegram ativamente
    await client.run_until_disconnected()

if __name__ == '__main__':
    # Cria a pasta temporária de downloads se não existir
    if not os.path.exists("downloads"):
        os.makedirs("downloads")
    
    if not API_ID or not API_HASH:
        print("AVISO: TELEGRAM_API_ID e TELEGRAM_API_HASH não configurados no .env")
    else:
        asyncio.run(main())
