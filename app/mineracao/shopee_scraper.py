import os
import uuid
import requests
from urllib.parse import urlparse
from app.core.logger import log_event

def _download_file(url: str, ext: str) -> str:
    """Faz o download puro de uma URL e salva em downloads/"""
    if not os.path.exists("downloads"):
        os.makedirs("downloads")
        
    filename = f"shopee_scrape_{uuid.uuid4().hex[:8]}{ext}"
    filepath = os.path.join("downloads", filename)
    
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return filepath
    except Exception as e:
        log_event(f"Erro ao baixar mídia {url}: {e}", component="ShopeeScraper", event="MEDIA_DL_ERROR", status="ERROR", level=40)
        return ""

def scrape_shopee_media(shopee_url: str) -> str:
    """
    Acessa a URL da Shopee (lida com redirecionamentos) usando Playwright.
    Busca preferencialmente a tag <video> e depois a imagem de capa.
    Retorna o caminho local local_path do arquivo baixado (ou "" se falhar).
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        log_event("Playwright não instalado. Scraper falhou.", component="ShopeeScraper", status="ERROR")
        return ""

    local_path = ""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Contexto persistente na memoria para não carregar cookies toda vez
        context = browser.new_context(
             user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        try:
            log_event(f"Iniciando scrape na URL: {shopee_url}", component="ShopeeScraper", event="START_SCRAPE", status="INFO")
            page.goto(shopee_url, timeout=30000, wait_until="domcontentloaded")
            
            # Aguarda um pouco por conta da re-renderização pesada do React da Shopee
            page.wait_for_timeout(4000)
            
            # 1. Tentar achar VÍDEO
            video_element = page.query_selector("video")
            if video_element:
                video_src = video_element.get_attribute("src")
                if video_src and video_src.startswith("http"):
                    log_event("Vídeo encontrado!", component="ShopeeScraper", event="VIDEO_FOUND", status="SUCCESS")
                    local_path = _download_file(video_src, ".mp4")
                    
                    if local_path:
                        browser.close()
                        return local_path
            
            # 2. Tentar achar IMAGEM PRINCIPAL
            # A Shopee sempre usa classes reativas malucas, então tentaremos pegar a imagem maior do carrossel.
            images = page.query_selector_all("img")
            best_img_src = ""
            for img in images:
                src = img.get_attribute("src")
                # As imagens oficiais de capa da Shopee ficam no domínio susercontent
                if src and "susercontent.com" in src and "/file/" in src:
                    # Se tiver o _tn no final da capa (thumbnail), removemos para ter alta resolução
                    if src.endswith("_tn"):
                        src = src[:-3]
                    best_img_src = src
                    break
                    
            if best_img_src:
                log_event("Imagem de capa encontrada!", component="ShopeeScraper", event="IMG_FOUND", status="SUCCESS")
                local_path = _download_file(best_img_src, ".jpg")
            else:
                log_event("Nenhuma mídia de alta qualidade extraída.", component="ShopeeScraper", event="NO_MEDIA_FOUND", status="WARNING")
        
        except Exception as e:
             log_event(f"Erro ao navegar na página da Shopee: {e}", component="ShopeeScraper", event="NAV_ERROR", status="ERROR", level=40)
        
        finally:
            browser.close()
            
    return local_path

if __name__ == "__main__":
    # Test
    url_mock = "https://shopee.com.br/product/1254184335/20199608460"
    path = scrape_shopee_media(url_mock)
    print("Downloaded to:", path)
