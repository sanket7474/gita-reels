import os
import requests
import time
from dotenv import load_dotenv

load_dotenv()

IG_USER_ID = os.getenv("IG_USER_ID")
ACCESS_TOKEN = os.getenv("IG_ACCESS_TOKEN")
APP_ID = os.getenv("APP_ID")
APP_SECRET = os.getenv("APP_SECRET")
VIDEO_URL = os.getenv("VIDEO_URL")
CAPTION_FILE = os.getenv("CAPTION_FILE", "output/caption.txt")


print("APP_ID:", os.getenv("APP_ID"))
print("APP_SECRET:", os.getenv("APP_SECRET")[:5], "...")
print("IG_USER_ID:", os.getenv("IG_USER_ID"))
print("ACCESS_TOKEN:", os.getenv("IG_ACCESS_TOKEN")[:10], "...")


API_VERSION = "v24.0"
MAX_ATTEMPTS = 30
SLEEP_INTERVAL = 5
REFRESH_THRESHOLD_DAYS = 50  # refresh if token is older than 50 days

# --- Helper Functions ---
def refresh_token():
    """Refresh long-lived token if close to expiry"""
    url = (
        f"https://graph.facebook.com/{API_VERSION}/oauth/access_token"
        f"?grant_type=fb_exchange_token"
        f"&client_id={APP_ID}"
        f"&client_secret={APP_SECRET}"
        f"&fb_exchange_token={ACCESS_TOKEN}"
    )

    print("URL for token refresh:", url)

    res = requests.get(url)
    data = res.json()
    if "access_token" in data:
        new_token = data["access_token"]
        print("Token refreshed ✅")
        # Update .env
        with open(".env", "r") as f:
            lines = f.readlines()
        with open(".env", "w") as f:
            for line in lines:
                if line.startswith("IG_ACCESS_TOKEN"):
                    f.write(f"IG_ACCESS_TOKEN={new_token}\n")
                else:
                    f.write(line)
        return new_token
    else:
        print("Failed to refresh token:", data)
        return ACCESS_TOKEN

def create_media(media_type="REELS", is_story=False):
    url = f"https://graph.facebook.com/{API_VERSION}/{IG_USER_ID}/media"
    payload = {
        "media_type": media_type,
        "video_url": VIDEO_URL,
        "caption": open(CAPTION_FILE, "r", encoding="utf-8").read(),
        "access_token": ACCESS_TOKEN
    }
    if is_story:
        payload["is_story"] = True
    res = requests.post(url, data=payload)
    data = res.json()
    if "id" not in data:
        print("Error creating media:", data)
        exit()
    return data["id"]

def wait_until_ready(media_id, label="Media"):
    status_url = f"https://graph.facebook.com/{API_VERSION}/{media_id}"
    attempt = 0
    while attempt < MAX_ATTEMPTS:
        status_res = requests.get(status_url, params={
            "fields": "status_code",
            "access_token": ACCESS_TOKEN
        })
        status_json = status_res.json()
        status = status_json.get("status_code")
        print(f"{label} status:", status)
        if status == "FINISHED":
            return
        elif status == "ERROR":
            print(f"{label} processing failed ❌")
            exit()
        attempt += 1
        time.sleep(SLEEP_INTERVAL)
    print(f"{label} timed out waiting for processing")
    exit()

def publish_media(media_id, label="Media"):
    url = f"https://graph.facebook.com/{API_VERSION}/{IG_USER_ID}/media_publish"
    payload = {
        "creation_id": media_id,
        "access_token": ACCESS_TOKEN
    }
    res = requests.post(url, data=payload)
    print(f"{label} published:", res.json())

# --- Auto Refresh Token ---
ACCESS_TOKEN = refresh_token()

# --- Upload Reel ---
reel_id = create_media(media_type="REELS")
wait_until_ready(reel_id, "Reel")
publish_media(reel_id, "Reel")

# --- Upload Story ---
story_id = create_media(media_type="VIDEO", is_story=True)
wait_until_ready(story_id, "Story")
publish_media(story_id, "Story")