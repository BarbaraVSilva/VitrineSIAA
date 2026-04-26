"""Validação de URLs para downloads (anti-SSRF e allowlist de domínios)."""

from __future__ import annotations

import ipaddress
import re
from urllib.parse import urlparse

_BLOCK_HOSTNAMES = frozenset(
    {
        "localhost",
        "0.0.0.0",
        "metadata.google.internal",
        "metadata",
        "169.254.169.254",
        "127.0.0.1",
        "::1",
    }
)

# Hostname deve coincidir com estes sufixos (domínios de redes sociais / Shopee).
_ALLOWED_SUFFIXES = (
    ".shopee.com.br",
    ".shopee.com",
    ".shopee.sg",
    ".shp.ee",
    ".instagram.com",
    ".cdninstagram.com",
    ".tiktok.com",
    ".tiktokcdn.com",
    ".youtube.com",
    ".googlevideo.com",
    ".googleusercontent.com",
    ".fbcdn.net",
    ".susercontent.com",
)

_ALLOWED_EXACT = frozenset(
    {
        "shope.ee",
        "shp.ee",
        "youtu.be",
        "www.youtu.be",
        "m.youtube.com",
        "www.youtube.com",
        "youtube.com",
    }
)

_SHOPEE_SUBDOMAIN = re.compile(
    r"^[a-z0-9][a-z0-9.-]*\.shopee\.(com\.br|com|sg|co\.id|com\.my|ph|tw|vn|th)$",
    re.IGNORECASE,
)


def _hostname_blocked(host: str) -> bool:
    h = (host or "").lower().rstrip(".")
    if not h:
        return True
    if h in _BLOCK_HOSTNAMES:
        return True
    if h.endswith(".local") or h.endswith(".internal"):
        return True
    try:
        addr = ipaddress.ip_address(h)
        return bool(
            addr.is_private
            or addr.is_loopback
            or addr.is_link_local
            or addr.is_multicast
            or addr.is_reserved
        )
    except ValueError:
        pass
    if h.startswith(("127.", "10.", "192.168.")):
        return True
    if re.match(r"^172\.(1[6-9]|2[0-9]|3[0-1])\.", h):
        return True
    return False


def is_safe_download_url(url: str) -> bool:
    """
    True se a URL for http(s) com host público na allowlist (Shopee, IG, TikTok, YouTube, etc.).
    """
    raw = (url or "").strip()
    if not raw.startswith(("http://", "https://")):
        return False
    try:
        parsed = urlparse(raw)
    except Exception:
        return False
    host = (parsed.hostname or "").lower()
    if not host or _hostname_blocked(host):
        return False
    if host in _ALLOWED_EXACT:
        return True
    if _SHOPEE_SUBDOMAIN.match(host):
        return True
    for suf in _ALLOWED_SUFFIXES:
        if host.endswith(suf):
            return True
    return False


def assert_safe_download_url(url: str) -> None:
    """Levanta ValueError se a URL não for permitida."""
    if not is_safe_download_url(url):
        raise ValueError("URL não permitida: use apenas links de Shopee, Instagram, TikTok ou YouTube.")
