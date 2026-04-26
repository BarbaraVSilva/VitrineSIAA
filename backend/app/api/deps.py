"""Dependências compartilhadas (auth, constantes)."""

from __future__ import annotations

import logging
import os

from fastapi import HTTPException, Request, status

from app.core.logger import log_event

# Sem default inseguro: configure no .env (mesmo valor que na Evolution API, webhook incoming).
EVOLUTION_API_SECRET = (os.getenv("EVOLUTION_API_SECRET") or "").strip()

# Chave para proteger /api/* (dashboard /pro). Se vazia, apenas aviso no arranque — ver webhook_server.
SIAA_INTERNAL_API_KEY = (os.getenv("SIAA_INTERNAL_API_KEY") or "").strip()


def _client_host(request: Request) -> str:
    if request.client:
        return request.client.host or ""
    return ""


async def verify_internal_api(request: Request) -> None:
    """
    Protege endpoints /api/*.
    - Se SIAA_INTERNAL_API_KEY estiver definida: exige header X-SIAA-API-Key idêntico.
    - Se não estiver definida: permite apenas loopback (desenvolvimento local).
    """
    if SIAA_INTERNAL_API_KEY:
        supplied = (
            request.headers.get("X-SIAA-API-Key")
            or request.headers.get("x-siaa-api-key")
            or ""
        ).strip()
        auth = request.headers.get("Authorization") or ""
        if auth.lower().startswith("bearer "):
            supplied = supplied or auth[7:].strip()
        if supplied != SIAA_INTERNAL_API_KEY:
            log_event(
                f"API interna: chave inválida ou ausente (IP: {_client_host(request)})",
                component="Security",
                event="API_AUTH_FAIL",
                status="WARNING",
                level=logging.WARNING,
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Chave de API inválida ou ausente (header X-SIAA-API-Key)",
            )
        return

    host = _client_host(request)
    if host not in ("127.0.0.1", "::1", "localhost"):
        log_event(
            f"API interna sem SIAA_INTERNAL_API_KEY: bloqueado IP {host}",
            component="Security",
            event="API_LOCAL_ONLY",
            status="WARNING",
            level=logging.WARNING,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Defina SIAA_INTERNAL_API_KEY no .env para aceder à API a partir da rede.",
        )


async def verify_evolution_api_key(request: Request) -> str:
    """Valida a chave enviada pelo Evolution API no webhook WhatsApp."""
    if not EVOLUTION_API_SECRET:
        log_event(
            "EVOLUTION_API_SECRET não configurada — webhook WhatsApp desativado",
            component="Security",
            event="EVOLUTION_NOT_CONFIGURED",
            status="CRITICAL",
            level=logging.ERROR,
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Webhook WhatsApp desativado: configure EVOLUTION_API_SECRET no .env",
        )

    api_key = request.headers.get("apikey") or request.headers.get("X-Evolution-API-Key")
    if (api_key or "").strip() != EVOLUTION_API_SECRET:
        log_event(
            f"Tentativa de acesso não autorizado ao webhook Evolution (IP: {_client_host(request)})",
            component="Security",
            event="AUTH_FAIL",
            status="CRITICAL",
            level=logging.WARNING,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: Evolution API Key missing or invalid",
        )
    return api_key
