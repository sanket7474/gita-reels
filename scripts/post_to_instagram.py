import os
import requests
import time
import sys
from datetime import datetime

# --- Load environment variables ---
IG_USER_ID = os.getenv("IG_USER_ID")
ACCESS_TOKEN = os.getenv("IG_ACCESS_TOKEN")
VIDEO_URL = os.getenv("VIDEO_URL")
CAPTION_FILE = os.getenv("CAPTION_FILE", "output/caption.txt")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")  # optional

API_VERSION = "v24.0"
MAX_ATTEMPTS = 30
SLEEP_INTERVAL = 5

# --- Helper functions ---
def send_discord_notification(message: str):
    """Send a message to Discord webhook"""
    if not DISCORD_WEBHOOK:
        print("No Discord webhook set. Skipping notification.")
        return
    try:
        res = requests.post(DISCORD_WEBHOOK, json={"content": message})
        if res.status_code in [200, 204]:
            print("Discord notification sent ✅")
        else:
            print("Failed to send Discord notification:", res.text)
    except Exception as e:
        print("Error sending Discord notification:", e)

def validate_token():
    """Check if the access token is valid"""
    url = f"https://graph.facebook.com/{API_VERSION}/me"
    res = requests.get(url, params={"access_token": ACCESS_TOKEN})
    data = res.json()
    if "error" in data:
        message = f"❌ Access token invalid or expired: {data}"
        print(message)
        send_discord_notification(message)
        sys.exit(1)
    print("✅ Access token is valid.")

def create_media(media_type="REELS", is_story=False):
    """Create Instagram media container"""
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
        message = f"❌ Error creating media: {data}"
        print(message)
        send_discord_notification(message)
        sys.exit(1)
    return data["id"]

def wait_until_ready(media_id, label="Media"):
    """Wait until media is processed and ready to publish"""
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
            message = f"{label} processing failed ❌"
            print(message)
            send_discord_notification(message)
            sys.exit(1)
        attempt += 1
        time.sleep(SLEEP_INTERVAL)
    message = f"{label} timed out waiting for processing"
    print(message)
    send_discord_notification(message)
    sys.exit(1)

def publish_media(media_id, label="Media"):
    """Publish media to Instagram"""
    url = f"https://graph.facebook.com/{API_VERSION}/{IG_USER_ID}/media_publish"
    payload = {
        "creation_id": media_id,
        "access_token": ACCESS_TOKEN
    }
    res = requests.post(url, data=payload)
    data = res.json()
    if "error" in data:
        message = f"❌ Error publishing {label}: {data}"
        print(message)
        send_discord_notification(message)
        sys.exit(1)
    print(f"{label} published:", data)
    return data  # return data for summary

# --- Main workflow ---
validate_token()

# Upload Reel
reel_id = create_media(media_type="REELS")
wait_until_ready(reel_id, "Reel")
reel_data = publish_media(reel_id, "Reel")

# Upload Story
story_id = create_media(media_type="REELS", is_story=True)
wait_until_ready(story_id, "Story")
story_data = publish_media(story_id, "Story")

# --- Send daily summary to Discord ---
caption_snippet = open(CAPTION_FILE, "r", encoding="utf-8").read().strip()[:100]
summary_message = (
    f"📅 **Daily Instagram Post Summary**\n"
    f"🕒 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    f"🎬 Reel posted ✅ (ID: {reel_id})\n"
    f"📖 Caption preview: {caption_snippet}...\n"
    f"📹 Story posted ✅ (ID: {story_id})\n"
    f"🌐 Video URL: {VIDEO_URL}"
)

send_discord_notification(summary_message)