import pytest
from unittest.mock import patch

def test_mock_telegram_crawler_logic():
    """Test simulated telegram string parsing logic without hitting telegram."""
    message = "🔥 Promoção Imperdível!\n👉 Link: https://shpe.site/abc\n🛍️ Cupom: TESTE10"
    
    # Simple logic to see how we'd extract
    lines = message.split('\n')
    link = None
    for line in lines:
        if "Link:" in line:
            link = line.split("Link:")[1].strip()
            
    assert link == "https://shpe.site/abc"
