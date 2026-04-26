import os
import uuid
import asyncio
import yt_dlp

from app.core.logger import log_event
from app.core.url_safety import assert_safe_download_url

class UniversalDownloader:
    """
    Serviço central de download de mídias para Reels, TikTok e Shopee.
    """
    def __init__(self, download_path: str = "downloads"):
        self.download_path = download_path
        if not os.path.exists(self.download_path):
            os.makedirs(self.download_path)

    async def download_social_video(self, url: str) -> str:
        """
        Usa yt-dlp para baixar vídeos do Instagram, TikTok, etc.
        """
        try:
            assert_safe_download_url(url)
        except ValueError:
            log_event(f"Download bloqueado (URL não permitida): {url[:80]}", component="Downloader", event="DL_BLOCKED", status="WARNING")
            return ""

        filename = f"social_{uuid.uuid4().hex[:8]}.mp4"
        filepath = os.path.join(self.download_path, filename)
        
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': filepath,
            'quiet': True,
            'no_warnings': True,
        }

        try:
            log_event(f"Iniciando download social via yt-dlp: {url}", component="Downloader", event="START_DL")
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, lambda: self._run_ytdlp(url, ydl_opts))
            
            if os.path.exists(filepath):
                log_event(f"Download concluído: {filepath}", component="Downloader", event="DL_SUCCESS")
                return filepath
            return ""
        except Exception as e:
            log_event(f"Erro no download yt-dlp: {e}", component="Downloader", event="DL_ERROR", status="ERROR")
            return ""

    def _run_ytdlp(self, url, opts):
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])

    async def scrape_shopee_video(self, url: str) -> str:
        """
        Versão aprimorada do scraper de vídeo Shopee.
        """
        from playwright.async_api import async_playwright
        
        try:
            assert_safe_download_url(url)
        except ValueError:
            log_event(f"Scrape Shopee bloqueado: {url[:80]}", component="Downloader", event="SHOPEE_BLOCKED", status="WARNING")
            return ""

        log_event(f"Iniciando scrape Shopee: {url}", component="Downloader", event="START_SHOPEE")
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            try:
                await page.goto(url, wait_until="networkidle", timeout=60000)
                video_el = await page.wait_for_selector("video", timeout=10000)
                if video_el:
                    src = await video_el.get_attribute("src")
                    if src:
                        try:
                            assert_safe_download_url(src)
                        except ValueError:
                            log_event("URL de vídeo Shopee rejeitada pela política de segurança", component="Downloader", event="SHOPEE_SRC_BLOCKED", status="WARNING")
                            return ""
                        return await self._download_raw(src, ".mp4")
            except Exception as e:
                log_event(f"Erro no scrape Shopee: {e}", component="Downloader", event="SHOPEE_ERROR", status="ERROR")
            finally:
                await browser.close()
        return ""

    async def _download_raw(self, url: str, ext: str) -> str:
        import aiohttp

        try:
            assert_safe_download_url(url)
        except ValueError:
            return ""

        filename = f"raw_{uuid.uuid4().hex[:8]}{ext}"
        filepath = os.path.join(self.download_path, filename)
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    with open(filepath, 'wb') as f:
                        f.write(await response.read())
                    return filepath
        return ""

downloader = UniversalDownloader()
