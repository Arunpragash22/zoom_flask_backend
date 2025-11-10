# zoom_api.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def get_zoom_access_token():
    url = "https://zoom.us/oauth/token"
    data = {
        "grant_type": "account_credentials",
        "account_id": os.getenv("ZOOM_ACCOUNT_ID")
    }
    auth = (os.getenv("ZOOM_CLIENT_ID"), os.getenv("ZOOM_CLIENT_SECRET"))

    response = requests.post(url, data=data, auth=auth)
    token_info = response.json()
    print("🔑 Zoom Token Response:", token_info)
    return token_info.get("access_token")
