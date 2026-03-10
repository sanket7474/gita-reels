
# 📿 Gita Daily Wisdom — Automated Reel Generator

Automatically generate and publish **daily Bhagavad Gita / Krishna wisdom reels** using Python, GitHub Actions, and the Meta (Instagram) API.

Every day the system:

1. Picks a Bhagavad Gita quote for the current date  
2. Generates a **vertical reel video (1080x1920)**  
3. Adds **Sanskrit + English + Hindi translation**  
4. Adds **background music**  
5. Generates an engaging caption + hashtags  
6. Publishes the reel automatically to **Instagram (and optionally Facebook)**  

No manual work required.

---

# ✨ Features

✔ Fully automated daily posting  
✔ Dynamic reel generation  
✔ Sanskrit + English + Hindi text rendering  
✔ Gold styled typography for AMOLED backgrounds  
✔ Auto caption generation  
✔ Background music rotation  
✔ GitHub Pages hosting for reels  
✔ Instagram publishing via Meta API  
✔ Optional Facebook cross-posting  

---

# 🧠 How It Works

Automation pipeline:

GitHub Actions Scheduler  
        ↓  
Select Daily Quote (JSON dataset)  
        ↓  
Generate Reel Video (Python + MoviePy)  
        ↓  
Generate Caption + Hashtags  
        ↓  
Upload to GitHub Pages (public URL)  
        ↓  
Publish Reel via Instagram Graph API  
        ↓  
Optional: Auto-share to Facebook Page  

---

# 📂 Project Structure

```
gita-reels
│
├── assets
│   ├── music
│   └── bg_krishna_arjuna.png
│
├── fonts
│   ├── NotoSans-Regular.ttf
│   └── NotoSansDevanagari-Regular.ttf
│
├── data
│   ├── krishna_quotes_2026_01.json
│   ├── krishna_quotes_2026_02.json
│
├── output
│   ├── reel.mp4
│   ├── caption.txt
│   └── today_quote.json
│
├── scripts
│   ├── pick_today_quote.py
│   ├── make_reel_github_linux.py
│   ├── make_caption.py
│   └── post_to_instagram.py
│
└── .github/workflows
    └── daily-reel.yml
```

---

# ⚙️ Installation

Install Python dependencies:

```
pip install moviepy pillow numpy imageio imageio-ffmpeg requests
```

Linux system dependencies:

```
sudo apt install ffmpeg pango1.0-tools fonts-noto fonts-noto-core fonts-noto-extra
```

---

# 🛠 Running Locally

Pick today’s quote

```
python scripts/pick_today_quote.py
```

Generate caption

```
python scripts/make_caption.py
```

Generate reel

```
python scripts/make_reel_github_linux.py
```

Output:

```
output/reel.mp4
output/caption.txt
```

---

# 🤖 GitHub Automation

Workflow runs daily using **GitHub Actions**.

File:

```
.github/workflows/daily-reel.yml
```

Daily schedule:

```
01:00 UTC
06:30 IST
```

Tasks:

1. Install dependencies  
2. Generate reel  
3. Generate caption  
4. Deploy to GitHub Pages  
5. Upload to Instagram  

---

# 🔐 Required GitHub Secrets

Add inside:

```
Repository → Settings → Secrets → Actions
```

Secrets:

```
IG_USER_ID
IG_ACCESS_TOKEN
```

---

# 📡 Instagram Publishing

Uses **Meta Graph API**.

Create media container:

```
POST /{ig-user-id}/media
```

Publish media:

```
POST /{ig-user-id}/media_publish
```

---

# 🌐 GitHub Pages Hosting

Video is hosted at:

```
https://USERNAME.github.io/gita-reels/reels/reel.mp4
```

Instagram requires a **public video URL**.

---

# 🎵 Music

Music rotates randomly from:

```
assets/music/
```

Each reel:

- trimmed to 12 seconds
- fade in/out
- low volume

---

# 📅 Quote Dataset

Quotes stored month-wise:

```
krishna_quotes_YYYY_MM.json
```

Example:

```
{
  "date": "2026-02-01",
  "topic": "Right Mindset",
  "sanskrit": "योगस्थः कुरु कर्माणि",
  "english": "Stay steady in inner balance...",
  "hindi": "अंतर में संतुलन रखते हुए कर्म करो...",
  "reference": "Bhagavad Gita 2.48"
}
```

---

# 🧘 Purpose

This project spreads **Bhagavad Gita wisdom daily** using automation.

Ancient wisdom + modern technology.

---

# 📜 License

MIT License

Feel free to fork and share wisdom.
