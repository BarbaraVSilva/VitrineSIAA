"""Diagnóstico Meta usando apenas variáveis de ambiente."""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from dotenv import load_dotenv

load_dotenv()
TOKEN = (os.getenv("META_ACCESS_TOKEN") or "").strip()
if not TOKEN:
    sys.exit("Defina META_ACCESS_TOKEN no .env")

import requests

print("--- permissions ---")
r = requests.get(
    "https://graph.facebook.com/v20.0/me/permissions",
    params={"access_token": TOKEN},
    timeout=30,
)
print(r.status_code, r.text[:1200])

print("\n--- pages ---")
r2 = requests.get(
    "https://graph.facebook.com/v20.0/me/accounts",
    params={"access_token": TOKEN},
    timeout=30,
)
print(r2.status_code, r2.text[:1200])
