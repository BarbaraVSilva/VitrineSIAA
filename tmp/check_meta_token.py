"""Diagnóstico Meta: token a partir de META_ACCESS_TOKEN no .env (não hardcode)."""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from dotenv import load_dotenv

load_dotenv()
TOKEN = (os.getenv("META_ACCESS_TOKEN") or "").strip()
if not TOKEN:
    sys.exit("Defina META_ACCESS_TOKEN no .env")

import requests


def check_token():
    url = f"https://graph.facebook.com/v20.0/me/accounts?access_token={TOKEN}"
    r = requests.get(url, timeout=30)
    print(r.status_code, r.text[:500])


if __name__ == "__main__":
    check_token()
