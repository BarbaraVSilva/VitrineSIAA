import os
import re
import sys
import asyncio
from telethon import TelegramClient, events
from dotenv import load_dotenv

# Força UTF-8 no terminal Windows para evitar erros de charmap com emojis
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

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

def parse_shopee_links(raw_text: str) -> list[dict]:
    """
    Extrai e classifica links do Shopee usando Regex (Módulo 1 de Decomposição).
    Retorna uma lista de dicionários: [{"url": "...", "tipo": "PRODUTO/COLECAO"}]
    """
    if not raw_text:
        return []
        
    padrao_urls = re.compile(r'(https?://(?:s\.shopee\.com\.br|shope\.ee|shopee\.com\.br)[^\s]+)')
    encontrados = padrao_urls.findall(raw_text)
    
    resultados = []
    for link in encontrados:
        link_limpo = link.rstrip('.,!?)')
        
        # Classificação básica baseada na URL
        if re.search(r'/collection/|/c/', link_limpo):
            tipo = "COLECAO"
        elif re.search(r'/product/|-i\.\d+\.\d+', link_limpo):
            tipo = "PRODUTO"
        else:
            tipo = "LINK_CURTO_MISTERIOSO" # Link curto padrão
            
        resultados.append({
            "url": link_limpo,
            "tipo": tipo
        })
        
    return resultados

@client.on(events.NewMessage(chats=TARGET_CHANNELS))
async def new_message_handler(event):
    await process_telegram_message(event.message)

async def process_telegram_message(message):
    # 1. Sanitize text (remove HTML and excess whitespace)
    import html
    raw_text = message.text or ""
    text = html.escape(raw_text).strip()
    
    # 2. Extrair e decompor Links para a Shopee do corpo do texto (Módulo 1)
    shopee_links_objs = parse_shopee_links(text)
    
    # 2. Baixar as Mídias
    media_path = await download_media(message)
    
    if shopee_links or media_path:        
        # Extrai foto do vídeo (se for mp4 ou similar)
        import sys
        sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
        from app.mineracao.editor_ia import extract_frame_from_video
        
        frame_foto = None
        if media_path and media_path.lower().endswith(('.mp4', '.mov')):
            frame_foto = extract_frame_from_video(media_path)
            
        # Se não tiver links mas tiver mídia
        if not shopee_links_objs:
             shopee_links_objs = [{"url": "", "tipo": "DESCONHECIDO"}] # forçamos um loop com link vazio para salvar como MISSING_LINK
             
        # Extrair uma keyword básica do texto para buscar reservas na shopee
        from app.core.shopee_api import buscar_backups_por_palavra_chave
        keyword_base = " ".join(text.split()[:3]) if text else "achadinho"
        backups = buscar_backups_por_palavra_chave(keyword_base)
        
        b1 = backups[0] if len(backups) > 0 else ""
        b2 = backups[1] if len(backups) > 1 else ""
        
        conn = get_connection()
        c = conn.cursor()
            
        # Avaliação de Risco com IA antes de salvar no banco
        from app.mineracao.compliance_checker import check_compliance
        compliance_result = check_compliance(text)
        comp_status = 'SEGURO' if compliance_result["is_safe"] else 'PROIBIDO'
        comp_reason = compliance_result["reason"]
        
        for idx, obj in enumerate(shopee_links_objs):
            link_original = obj["url"]
            tipo_link = obj["tipo"]
            status = 'PENDING' if link_original else 'MISSING_LINK'
            
            print("="*40)
            print(f"--- NOVO ACHADO ({idx+1}/{len(shopee_links_objs)}) | TIPO: {tipo_link} ---")
            print(f"Texto: {text[:50]}...")
            print(f"Link Original: {link_original}")
            print(f"Link Reserva 1 (Auto): {b1}")
            print("="*40)
            
            try:
                c.execute(
                    "INSERT INTO achados (texto_original, midia_path, cover_path, link_original, link_backup_1, link_backup_2, status, compliance_status, compliance_reason, tipo_link) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (text, media_path, frame_foto, link_original, b1, b2, status, comp_status, comp_reason, tipo_link)
                )
                from app.core.logger import log_event
                log_event(f"Novo achado capturado ({status}): {link_original}", component="CrawlerTelegram", event="MSG_CAPTURE", status="SUCCESS")
                print(f"=> Salvo no banco com status {status}! Aguardando aprovação no Streamlit.")
            except Exception as e:
                from app.core.logger import log_event
                log_event(f"Erro ao salvar no banco: {str(e)}", component="CrawlerTelegram", event="DB_INSERT", status="ERROR", level=40)
                print(f"=> Erro ao salvar no banco: {e}")
                
        conn.commit()
        conn.close()

async def fetch_history():
    history_hours = float(os.getenv("TELEGRAM_HISTORY_HOURS", "0"))
    if history_hours > 0:
        from datetime import datetime, timedelta, timezone
        limit_date = datetime.now(timezone.utc) - timedelta(hours=history_hours)
        limit_date_local = limit_date.astimezone()
        print(f"Puxando histórico de até {history_hours} horas atrás (desde {limit_date_local.strftime('%Y-%m-%d %H:%M')})...")
        for channel in TARGET_CHANNELS:
            print(f"Processando histórico do canal: {channel}")
            try:
                # O Telethon iter_messages vai puxando do mais recente pro mais antigo
                async for message in client.iter_messages(channel):
                    if message.date < limit_date:
                        break # já passou do limite estipulado
                    # Processamos apenas se tiver texto e/ou mídia
                    if message.text or message.media:
                        msg_date_local = message.date.astimezone()
                        print(f"Lendo mensagem de {msg_date_local.strftime('%Y-%m-%d %H:%M')} do histórico...")
                        await process_telegram_message(message)
            except Exception as e:
                from app.core.logger import log_event
                log_event(f"Erro ao ler histórico de {channel}: {str(e)}", component="CrawlerTelegram", event="HISTORY_FETCH_ERROR", status="ERROR")
                print(f"Erro ao ler histórico de {channel}: {e}")

async def watcher_loop():
    """Vigia o sistema de arquivos para comandos manuais vindos do Painel Streamlit"""
    trigger_file = ".trigger_scrape"
    while True:
        if os.path.exists(trigger_file):
            try:
                 os.remove(trigger_file)
            except:
                 pass
            print("\n" + "="*40)
            print("🔄 GATILHO MANUAL RECEBIDO: Re-Vasculhando as últimas 24h...")
            print("="*40)
            await fetch_history()
            print("=> Busca retroativa finalizada! Monitoramento em tempo real retomado.")
        await asyncio.sleep(5)

async def main():
    print(f"Iniciando o Crawler. Monitorando os canais/grupos: {', '.join(TARGET_CHANNELS)}")
    await client.start(phone=PHONE)
    print("Conectado! Verificando convites e acessos...")
    
    # Tenta entrar nos canais se forem hashes de convite
    from telethon.tl.functions.messages import ImportChatInviteRequest
    from telethon.errors import UserAlreadyParticipantError, InviteHashExpiredError
    
    for channel in TARGET_CHANNELS:
        # Se parecer um hash de convite (sem @ e sem ser número puro)
        if not channel.startswith('@') and not channel.replace('-','').isdigit() and len(channel) > 10:
            try:
                print(f"Tentando entrar no canal via convite: {channel}")
                await client(ImportChatInviteRequest(channel))
                print(f"✅ Sucesso ao entrar no canal: {channel}")
            except UserAlreadyParticipantError:
                print(f"ℹ️ Já participamos do canal: {channel}")
            except InviteHashExpiredError:
                print(f"⚠️ Convite expirado para o canal: {channel}")
            except Exception as e:
                print(f"❌ Erro ao processar convite {channel}: {e}")

    # 1. Recuperar histórico anterior inicial
    await fetch_history()
                
    print("Aguardando novas publicações ativamente e vigiando gatilhos do painel...")
    # Executa as duas tarefas simultaneamente: Escuta do Telegram (event loop) e Vigilância de Pasta
    await asyncio.gather(
        client.run_until_disconnected(),
        watcher_loop()
    )

if __name__ == '__main__':
    # Cria a pasta temporária de downloads se não existir
    if not os.path.exists("downloads"):
        os.makedirs("downloads")
    
    if not API_ID or not API_HASH:
        print("AVISO: TELEGRAM_API_ID e TELEGRAM_API_HASH não configurados no .env")
    else:
        asyncio.run(main())
