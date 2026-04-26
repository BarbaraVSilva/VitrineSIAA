"""Servidor FastAPI: webhooks, API /pro e arquivos estáticos."""

from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles

from app.api import deps as api_deps
from app.api.routers import dashboard_api, webhooks
from app.core.logger import log_event


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not api_deps.SIAA_INTERNAL_API_KEY:
        print(
            "[SIAA SEGURANÇA] SIAA_INTERNAL_API_KEY vazia: /api/* só aceita pedidos de loopback. "
            "Defina a chave no .env e no hub /pro (localStorage) para uso na rede local."
        )
    if not api_deps.EVOLUTION_API_SECRET:
        print("[SIAA SEGURANÇA] EVOLUTION_API_SECRET vazia: POST /webhook/whatsapp responde 503.")
    if not (os.getenv("META_VERIFY_TOKEN") or "").strip():
        print("[SIAA SEGURANÇA] META_VERIFY_TOKEN vazia: verificação GET /webhook/meta indisponível.")
    yield


app = FastAPI(title="SIAA-2026 Webhooks Server", lifespan=lifespan)

# ── Dashboard estático & mídia ──
@app.get("/pro", include_in_schema=False)
async def serve_pro_dashboard():
    dashboard_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "dashboard", "pro_dashboard.html"))
    if os.path.exists(dashboard_path):
        return FileResponse(dashboard_path)
    return Response(content="Dashboard file not found at " + dashboard_path, status_code=404)


proj_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
media_path = os.path.join(proj_root, "media")
os.makedirs(media_path, exist_ok=True)
app.mount("/media", StaticFiles(directory=media_path), name="media")

_cors = (os.getenv("SIAA_CORS_ORIGINS") or "").strip()
_cors_list = [x.strip() for x in _cors.split(",") if x.strip()] if _cors else ["*"]
_hosts = (os.getenv("SIAA_ALLOWED_HOSTS") or "").strip()
_host_list = [x.strip() for x in _hosts.split(",") if x.strip()] if _hosts else ["*"]

app.add_middleware(TrustedHostMiddleware, allowed_hosts=_host_list)
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_list,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=[
        "Content-Type",
        "Authorization",
        "X-SIAA-API-Key",
        "apikey",
        "X-Evolution-API-Key",
    ],
)

app.include_router(webhooks.router)
app.include_router(dashboard_api.router)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    log_event(f"Request: {request.method} {request.url.path}", component="WebhookServer", event="HTTP_REQ")
    response = await call_next(request)
    log_event(f"Response: {response.status_code}", component="WebhookServer", event="HTTP_RES")
    return response


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8088, reload=False)
