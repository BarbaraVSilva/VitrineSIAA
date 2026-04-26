"""Endpoints usados pelo dashboard HTML /pro e integrações."""

from __future__ import annotations

import os
import re
import socket

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import verify_internal_api
from app.api.schemas import CopyRequest, DownloadRequest, WhatsAppRequest
from app.core.downloader import downloader
from app.core.repository import AchadosRepository
from app.core.url_safety import assert_safe_download_url
from app.mineracao.hook_generator import generate_hooks
from app.social_interactions.evolution_api import whatsapp

router = APIRouter(prefix="/api", tags=["pro-dashboard"], dependencies=[Depends(verify_internal_api)])


def _validate_whatsapp_target(number: str) -> None:
    n = (number or "").strip()
    if not n or len(n) > 120:
        raise HTTPException(status_code=400, detail="Número ou JID WhatsApp inválido")
    if re.search(r'[<>"\'\\\n\r\x00]', n):
        raise HTTPException(status_code=400, detail="Caracteres não permitidos no destino WhatsApp")
    if not re.match(r"^[\d+\s\-()@.a-zA-Z_:]+$", n):
        raise HTTPException(status_code=400, detail="Formato de destino WhatsApp inválido")


@router.get("/achados")
async def list_achados():
    repo = AchadosRepository()
    return repo.get_pending()


@router.post("/download")
async def api_download(req: DownloadRequest):
    try:
        assert_safe_download_url(req.url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    try:
        url = req.url.strip()
        if "shopee" in url.lower() or "shope.ee" in url.lower() or "shp.ee" in url.lower():
            path = await downloader.scrape_shopee_video(url)
        else:
            path = await downloader.download_social_video(url)

        if path:
            repo = AchadosRepository()
            repo.add_achado("Download Manual", path, url, status="PENDING", categoria="Manual")
            return {"status": "success", "path": path}
        return {"status": "error", "message": "Falha no download"}
    except HTTPException:
        raise
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/generate-copy")
async def api_copy(req: CopyRequest):
    try:
        hooks = generate_hooks(req.description, style=req.style)
        return {"status": "success", "hooks": hooks}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/whatsapp/send")
async def api_whatsapp_send(req: WhatsAppRequest):
    _validate_whatsapp_target(req.number)
    if req.media_url:
        try:
            assert_safe_download_url(req.media_url)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e

    try:
        if req.media_url:
            res = await whatsapp.send_media(req.number, req.media_url, req.text)
        else:
            res = await whatsapp.send_text(req.number, req.text)
        return {"status": "success", "response": res}
    except HTTPException:
        raise
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.get("/access-info")
async def get_access_info():
    """Retorna o IP da rede local e Tailscale para facilitar a conexão mobile."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_local = s.getsockname()[0]
        s.close()
    except OSError:
        ip_local = "localhost"

    return {
        "status": "success",
        "ip_local": ip_local,
        "tailscale_ip": os.getenv("TAILSCALE_IP", "Não Configurado"),
        "mobile_url": f"http://{ip_local}:8088/pro",
    }
