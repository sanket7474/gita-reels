import os
import requests
import time

IG_USER_ID = os.getenv("IG_USER_ID")
ACCESS_TOKEN = os.getenv("IG_ACCESS_TOKEN")

VIDEO_URL = "https://sanket7474.github.io/gita-reels/reels/reel.mp4"

with open("output/caption.txt", "r", encoding="utf-8") as f:
    CAPTION = f.read()

# Step 1: create container
url = f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media"

payload = {
    "media_type": "REELS",
    "video_url": VIDEO_URL,
    "caption": CAPTION,
    "access_token": ACCESS_TOKEN
}

res = requests.post(url, data=payload)
creation_id = res.json()["id"]

print("Container created:", creation_id)

# wait for processing
time.sleep(15)

# Step 2: publish reel
publish_url = "https://graph.facebook.com/v19.0/{IG_USER_ID}/media_publish"

publish_payload = {
    "creation_id": creation_id,
    "access_token": ACCESS_TOKEN
}

res = requests.post(publish_url, data=publish_payload)

print("Posted:", res.json())