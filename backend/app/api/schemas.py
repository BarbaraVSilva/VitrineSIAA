"""Modelos Pydantic compartilhados pela API FastAPI."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class WhatsAppMessage(BaseModel):
    event: str
    data: dict


class DownloadRequest(BaseModel):
    url: str


class CopyRequest(BaseModel):
    description: str
    style: str = "Padrao"


class WhatsAppRequest(BaseModel):
    number: str
    text: str
    media_url: Optional[str] = None
