import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from dotenv import load_dotenv

load_dotenv()
TOKEN = (os.getenv("META_ACCESS_TOKEN") or "").strip()
if not TOKEN:
    sys.exit("Defina META_ACCESS_TOKEN no .env")

import requests

id_to_check = (sys.argv[1] if len(sys.argv) > 1 else os.getenv("META_PAGE_ID", "")).strip()
if not id_to_check:
    sys.exit("Passe o ID como argumento ou defina META_PAGE_ID")

r = requests.get(
    f"https://graph.facebook.com/v20.0/{id_to_check}",
    params={"fields": "name,username,metadata{type}", "access_token": TOKEN},
    timeout=30,
)
print(r.status_code, r.text)
