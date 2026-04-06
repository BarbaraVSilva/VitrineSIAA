import requests

TOKEN = "EAARpqF7rfooBRLS3Tl33PNDK4ZB7EZClhiOguBQC4tviUC6bSc04bUvO9f4k1LPF9osINp92vuC00JfNZBTktrmtGCaQJAMY3GoJfHjDRr38IdS9ZBe9okZAkZBO7yQIIRIjS4hWQJxptybxXZCZBGlCCEy8jIDGlZBkvmWVgctEHwpRZCrbk3GEiq2T2u41aEUfotUiE2rBLdNRDHclszmwn4i9r5xyGS423DA5MufJfEUU6UNZAqFBCBEdGM7VtmkheRPkM3nXMcIC5dI2AmrjocNLAZDZD"
IG_ID = "17841440746815302"

def check_ig_id():
    url = f"https://graph.facebook.com/v20.0/{IG_ID}?fields=username,name&access_token={TOKEN}"
    res = requests.get(url)
    print(res.json())

if __name__ == "__main__":
    check_ig_id()
