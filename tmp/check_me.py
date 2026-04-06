import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from dotenv import load_dotenv

load_dotenv()
TOKEN = (os.getenv("META_ACCESS_TOKEN") or "").strip()
if not TOKEN:
    sys.exit("Defina META_ACCESS_TOKEN no .env")

import requests

r = requests.get(
    "https://graph.facebook.com/v20.0/me?fields=name,id",
    params={"access_token": TOKEN},
    timeout=30,
)
print(r.status_code, r.text[:800])
