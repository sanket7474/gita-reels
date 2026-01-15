import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output"

INPUT_QUOTE = OUTPUT / "today_quote.json"
CAPTION_FILE = OUTPUT / "caption.txt"

# ✅ pool of hashtags (we will randomly pick only 5 daily)
HASHTAGS_POOL = [
    "#bhagavadgita", "#krishna", "#krishnavani", "#gita",
    "#spirituality", "#dharma", "#motivation", "#hindiquotes",
    "#sanskrit", "#lifequotes", "#innerpeace", "#mindset",
    "#dailywisdom", "#quotes", "#inspiration", "#peace",
    "#bhakti", "#sanatan", "#india", "#meditation"
]

# ✅ CTA lines (1 random per day)
CTA_LINES = [
    "✨ Save this for later.",
    "💛 Share this with someone who needs it.",
    "🙏 Comment ‘ॐ’ if this touched your heart.",
    "📌 Follow @dailywisdomgita for daily Gita wisdom.",
    "🌼 Pause. Breathe. Reflect."
]


def load_quote():
    if not INPUT_QUOTE.exists():
        raise FileNotFoundError(f"Missing file: {INPUT_QUOTE}")

    q = json.loads(INPUT_QUOTE.read_text(encoding="utf-8"))

    required = ["sanskrit", "english", "hindi", "reference"]
    missing = [k for k in required if k not in q or not str(q[k]).strip()]
    if missing:
        raise ValueError(f"today_quote.json missing keys: {missing}")

    return q


def pick_hashtags(n=5):
    n = min(n, len(HASHTAGS_POOL))
    return random.sample(HASHTAGS_POOL, n)


def build_caption(q: dict) -> str:
    topic = q.get("topic", "").strip()
    topic_line = f"🌿 {topic}\n\n" if topic else ""

    cta = random.choice(CTA_LINES)
    tags = " ".join(pick_hashtags(5))

    caption = f"""🕉️ Bhagavad Gita Wisdom

{topic_line}📜 Sanskrit:
{q["sanskrit"]}

✨ English:
{q["english"]}

🌼 Hindi:
{q["hindi"]}

📌 Reference: Bhagavad Gita {q["reference"]}

{cta}

{tags}
"""
    return caption.strip() + "\n"


def main():
    OUTPUT.mkdir(exist_ok=True)
    q = load_quote()
    caption = build_caption(q)

    CAPTION_FILE.write_text(caption, encoding="utf-8")
    print("✅ caption generated:", CAPTION_FILE)


if __name__ == "__main__":
    main()
