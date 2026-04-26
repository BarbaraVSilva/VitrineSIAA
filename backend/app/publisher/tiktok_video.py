import os
import time
from playwright.sync_api import sync_playwright

def publish_to_tiktok(video_path: str, caption: str):
    """
    Simula o login e upload de um vídeo + legenda para o TikTok Creator Center.
    Requer primeira autenticação manual.
    """
    if not os.path.exists(video_path):
        print(f"[TIKTOK BOT] ERRO: Vídeo não encontrado -> {video_path}")
        return False
        
    print(f"[TIKTOK BOT] 🎵 Iniciando postagem de vídeo no TikTok: {os.path.basename(video_path)}")
    user_data_dir = os.path.join(os.getcwd(), "tiktok_creator_session")
    
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=False, # Mantenha falso para o TikTok não bloquear fácil (Anti-Bot)
            viewport={'width': 1366, 'height': 768}
        )
        
        page = browser.new_page()
        try:
            print("[TIKTOK BOT] Acessando Studio do TikTok...")
            page.goto('https://www.tiktok.com/creator-center/upload') 
            
            # Checa se pediu login (procurando um iframe/login)
            if page.locator('button:has-text("Log in")').count() > 0 or page.locator('div[data-e2e="login-modal"]').count() > 0:
                print("[TIKTOK BOT] 🚨 Login ou Captcha necessário. Use o celular para escanear o QR Code de login!")
                page.wait_for_timeout(60000) 
            
            print("[TIKTOK BOT] Aguardando o Container de Upload...")
            # Encontra o input de arquivo oculto no Tiktok
            iframe = page.frame_locator('iframe[data-tt="upload-iframe"]')
            file_input = page.locator('input[type="file"]')
            
            try:
                # O botão The Tiktok Upload File (Pode variar no DOM)
                file_input.set_files(video_path)
            except:
                with page.expect_file_chooser() as fc_info:
                    page.locator('button:has-text("Select video")').click()
                file_chooser = fc_info.value
                file_chooser.set_files(video_path)
            
            print("[TIKTOK BOT] Vídeo carregando. Digitando a cópia/hashtags...")
            time.sleep(5) # tempo para carregar o preview
            
            # TikTok usa um formato ContentEditable para legendas (Draft.js)
            caption_box = page.locator('.public-DraftEditor-content')
            caption_box.click()
            caption_box.fill(caption)
            
            print("[TIKTOK BOT] Aguardando botão de Postar...")
            time.sleep(10)
            
            # Clica em Postar
            post_button = page.locator('button:has-text("Post")')
            
            if post_button.is_enabled():
                post_button.click()
                print("[TIKTOK BOT] ✅ Vídeo estourado no TikTok com Sucesso!")
            else:
                print("[TIKTOK BOT] ⚠️ Botão Publicar não habilitado. Falha na conversão TikTok.")
                
            time.sleep(5) 

        except Exception as e:
            print(f"[TIKTOK BOT ERRO] Falha massiva no navegador: {e}")
            return False
        finally:
            browser.close()
            
    return True
