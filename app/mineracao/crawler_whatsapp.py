import os
import time
from playwright.sync_api import sync_playwright
import sys

# Ajusta o patch para ter acesso a app.core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from app.core.database import get_connection

def save_to_database(descricao, media_path=None):
    """Salva o item extraído do Whatsapp no banco do sistema (SIAA)."""
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO achados (texto_original, midia_path, status, categoria) VALUES (?, ?, 'PENDING', 'WhatsApp')",
        (descricao, media_path)
    )
    conn.commit()
    conn.close()
    print(f"[WHATSAPP BOT] Item salvo no banco de dados SIAA! -> {descricao[:50]}...")

def run_whatsapp_crawler():
    target_group_name = os.getenv("WHATSAPP_GROUP_NAME", "Ofertas Vips - Teste")
    """
    Inicia o navegador (Chrome), abre o WhatsApp Web e aguarda o escaneamento do QR Code.
    Depois, entra em um grupo específico e monitora as últimas mensagens enviadas.
    """
    user_data_dir = os.path.join(os.getcwd(), "whatsapp_auth_session")
    
    with sync_playwright() as p:
        # Usa contexto persistente para não precisar ler o QR code toda santa vez
        browser = p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=False, # Mantenha False pra conseguir ver o QR Code
            viewport={'width': 1280, 'height': 720}
        )
        
        page = browser.new_page()
        print("[WHATSAPP BOT] Abrindo WhatsApp Web...")
        page.goto('https://web.whatsapp.com/')
        
        print("[WHATSAPP BOT] Aguardando autenticação (Leia o QR Code se necessário)...")
        # Aguarda que a barra de pesquisa de contatos apareça, indicando login concluído
        page.wait_for_selector('div[contenteditable="true"][data-tab="3"]', timeout=120000)
        print("[WHATSAPP BOT] Autenticado com sucesso!")
        
        # Procura o grupo alvo
        search_box = page.locator('div[contenteditable="true"][data-tab="3"]')
        search_box.click()
        search_box.fill(target_group_name)
        time.sleep(2)
        
        # Clica no resultado (baseado no title do span)
        page.locator(f'span[title="{target_group_name}"]').click()
        print(f"[WHATSAPP BOT] Grupo '{target_group_name}' acessado. Iniciando monitoramento simples...")
        
        # Loop simples para pegar a última mensagem (Em um crawler real, usaria websockets ou hooks)
        last_msg_text = ""
        try:
            for _ in range(10): # Roda 10 vezes como demonstração
                time.sleep(5)
                # Seleciona as mensagens de texto
                messages = page.locator('div.message-in, div.message-out').all()
                if messages:
                    latest = messages[-1]
                    texto_loc = latest.locator('span.selectable-text')
                    if texto_loc.count() > 0:
                        texto = texto_loc.inner_text()
                        if texto != last_msg_text:
                            last_msg_text = texto
                            print(f"\n[WHATSAPP BOT] Nova Mensagem Detectada:\n{texto}")
                            save_to_database(texto, None)
                            
        except Exception as e:
            print(f"[WHATSAPP BOT ERRO] {e}")
            
        print("[WHATSAPP BOT] Encerrando sessão...")
        browser.close()

if __name__ == "__main__":
    run_whatsapp_crawler()
