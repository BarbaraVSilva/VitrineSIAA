import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from dotenv import load_dotenv

load_dotenv()
TOKEN = (os.getenv("META_ACCESS_TOKEN") or "").strip()
IG_ID = (os.getenv("IG_USER_ID") or "").strip()
if not TOKEN or not IG_ID:
    sys.exit("Defina META_ACCESS_TOKEN e IG_USER_ID no .env")

import requests

r = requests.get(
    f"https://graph.facebook.com/v20.0/{IG_ID}",
    params={"fields": "username,name", "access_token": TOKEN},
    timeout=30,
)
print(r.status_code, r.text)
