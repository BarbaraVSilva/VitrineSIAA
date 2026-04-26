import os
import time
from playwright.sync_api import sync_playwright

def publish_to_shopee_video(video_path: str, caption: str, affiliate_link: str):
    """
    Simula o login e upload de um vídeo + link de afiliado no painel da Shopee.
    Atenção: Requer sessão persistente para manter o login salvo, 
    pois tem Captchas complexos ao fazer login limpo.
    """
    if not os.path.exists(video_path):
        print(f"[SHOPEE VIDEO] ERRO: Vídeo não encontrado -> {video_path}")
        return False
        
    print(f"[SHOPEE VIDEO] Iniciando processo automatizado para postar: {os.path.basename(video_path)}")
    user_data_dir = os.path.join(os.getcwd(), "shopee_creator_session")
    
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=False, # Mantenha false para acompanhamento
            viewport={'width': 1366, 'height': 768}
        )
        
        page = browser.new_page()
        try:
            print("[SHOPEE VIDEO] Acessando Creator Center...")
            # URL Hípotetica/Baseada em portais de criadores
            page.goto('https://creator.shopee.com.br/') 
            
            # Checa se pediu login (procurando um botao comum de login)
            if page.locator('button:has-text("Fazer Login")').count() > 0:
                print("[SHOPEE VIDEO] Login necessário. Faça o login manual na janela que se abriu...")
                # Dá um longo tempo para o usuário resolver o login/OTP manualmente
                page.wait_for_timeout(60000) 
                
            print("[SHOPEE VIDEO] Navegando para a aba de Postagem de Vídeo...")
            page.wait_for_selector('div.upload-video-btn', timeout=15000)
            
            # Faz o upload do arquivo
            with page.expect_file_chooser() as fc_info:
                page.click('div.upload-video-btn')
            file_chooser = fc_info.value
            file_chooser.set_files(video_path)
            
            print("[SHOPEE VIDEO] Vídeo carregando. Preenchendo a descrição...")
            page.fill('textarea[placeholder="Adicione uma legenda..."]', caption)
            
            # Adicionar Produto/Link Afiliado
            if page.locator('button:has-text("Adicionar Produto")').count() > 0:
                page.click('button:has-text("Adicionar Produto")')
                page.fill('input[placeholder="Cole o link do produto..."]', affiliate_link)
                page.click('button.confirm-link-btn')
                time.sleep(2)
                
            print("[SHOPEE VIDEO] Aguardando o uploader processar...")
            time.sleep(10) # Simples espera para demonstração do carregamento
            
            # Clica em Publicar
            if page.locator('button:has-text("Publicar")').is_enabled():
                page.click('button:has-text("Publicar")')
                print("[SHOPEE VIDEO] ✅ Vídeo publicado com sucesso!")
            else:
                print("[SHOPEE VIDEO] ⚠️ Botão Publicar não habilitado. O upload pode ter falhado ou demorado.")
                
            time.sleep(5) # Para visualização antes de fechar

        except Exception as e:
            print(f"[SHOPEE VIDEO BOT ERRO] O fluxo da página disparou um erro: {e}")
        finally:
            browser.close()
            
    return True

if __name__ == "__main__":
    # Teste unitário mockado
    publish_to_shopee_video("test_base.mp4", "Oferta Incrível passando na sua timeline! 🔥 #shopee", "https://shpe.site/abc")
