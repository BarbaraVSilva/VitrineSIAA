import pytest
import sqlite3
import threading
import time
import os
import json
import httpx

# Antes de carregar a app FastAPI (deps leem o ambiente na importação)
os.environ["DB_PATH"] = "test_resilience.sqlite"
os.environ["EVOLUTION_API_SECRET"] = "test_evolution_secret_for_pytest"
os.environ["SIAA_INTERNAL_API_KEY"] = "test_internal_api_key_pytest"

from app.webhook_server import app
from app.core.database import get_connection, init_db

@pytest.fixture(autouse=True)
def setup_db():
    if os.path.exists("test_resilience.sqlite"):
        os.remove("test_resilience.sqlite")
    init_db()
    yield
    if os.path.exists("test_resilience.sqlite"):
        os.remove("test_resilience.sqlite")

def test_webhook_unauthorized():
    """Valida se o webhook recusa requisições sem apikey."""
    with httpx.Client(transport=httpx.ASGITransport(app=app), base_url="http://testserver") as client:
        payload = {"event": "messages.upsert", "data": {}}
        response = client.post("/webhook/whatsapp", json=payload)
        assert response.status_code == 401
        assert "Unauthorized" in response.text

def test_webhook_authorized():
    """Valida se o webhook aceita requisições com apikey correta."""
    with httpx.Client(transport=httpx.ASGITransport(app=app), base_url="http://testserver") as client:
        payload = {
            "event": "messages.upsert",
            "data": {
                "message": {
                    "messages": [
                        {
                            "key": {"remoteJid": "123456@g.us"},
                            "message": {"conversation": "Oferta! https://shope.ee/testlink"}
                        }
                    ]
                }
            }
        }
        headers = {"apikey": "test_evolution_secret_for_pytest"}
        response = client.post("/webhook/whatsapp", json=payload, headers=headers)
        assert response.status_code == 200

def test_branding_format_support():
    """Valida se o motor de branding reconhece formatos modernos como .webp e .jfif."""
    from app.mineracao.branding import apply_branding_to_image
    
    # Formato suportado mas arquivo inexistente (deve apenas logar e retornar o path)
    res = apply_branding_to_image("test_image.webp")
    assert res == "test_image.webp"
    
    # Formato não suportado
    res = apply_branding_to_image("test_image.gif")
    assert res == "test_image.gif"

if __name__ == "__main__":
    # Roda os testes manualmente se chamado direto
    pytest.main([__file__])
    # Roda os testes manualmente se chamado direto
    pytest.main([__file__])
