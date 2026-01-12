import json
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUTPUT = ROOT / "output"
OUTPUT.mkdir(exist_ok=True)

def load_month_file(year, month):
    filename = f"krishna_quotes_{year}_{month:02d}.json"
    path = DATA / filename
    if not path.exists():
        raise FileNotFoundError(f"Month file not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))

def main():
    today = datetime.now()
    year, month, day = today.year, today.month, today.day

    month_data = load_month_file(year, month)

    # find quote by date
    today_str = today.strftime("%Y-%m-%d")
    quote = next((q for q in month_data if q["date"] == today_str), None)

    if not quote:
        raise Exception(f"No quote found for date {today_str} in month file.")

    out_file = OUTPUT / "today_quote.json"
    out_file.write_text(json.dumps(quote, ensure_ascii=False, indent=2), encoding="utf-8")

    print("✅ Picked today's quote:", today_str)
    print("Topic:", quote["topic"])
    print("Saved to:", out_file)

if __name__ == "__main__":
    main()
