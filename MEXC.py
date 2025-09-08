import requests
import csv
import os
import time
from datetime import datetime

API_URL = "https://api.mexc.com/api/v3/exchangeInfo"
CSV_FILE = "mexc_st_tokens.csv"
RATE_LIMIT_DELAY = 0.2  # delay to respect MEXC rate limits

def fetch_st_tokens():
    """
    Fetch only ST-tagged tokens from MEXC (st == true).
    """
    time.sleep(RATE_LIMIT_DELAY)
    resp = requests.get(API_URL, timeout=30)
    resp.raise_for_status()
    symbols = resp.json().get("symbols", [])
    # Filter immediately: only keep symbols where st = true
    return [s for s in symbols if s.get("st") is True]

def read_existing_for_today():
    """
    Read today's logged ST pairs from CSV to avoid duplicates.
    """
    today_str = datetime.utcnow().strftime("%Y-%m-%d")
    seen_pairs = set()

    if os.path.isfile(CSV_FILE):
        with open(CSV_FILE, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames and "date" in reader.fieldnames and "pair" in reader.fieldnames:
                for row in reader:
                    if row["date"].startswith(today_str):
                        seen_pairs.add(row["pair"])
    return seen_pairs

def append_to_csv(st_items):
    """
    Append only new ST pairs for today to the CSV.
    """
    file_exists = os.path.isfile(CSV_FILE)
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    seen_today = read_existing_for_today()

    with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["pair", "base", "quote", "date"])

        for item in st_items:
            base = item.get("baseAsset", "")
            quote = item.get("quoteAsset", "")
            pair = f"{base}/{quote}"
            if pair not in seen_today:
                writer.writerow([pair, base, quote, timestamp])
                print(f"✅ Logged: {pair}")
            else:
                print(f"⏩ Skipped (already logged today): {pair}")

def main():
    print("🔍 Fetching ST-tagged tokens from MEXC...")
    try:
        st_tokens = fetch_st_tokens()
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error fetching data: {e}")
        return

    if not st_tokens:
        print("✅ No ST-tagged tokens found.")
        return

    print(f"🚨 Found {len(st_tokens)} ST-tagged pairs.")
    append_to_csv(st_tokens)

if __name__ == "__main__":
    main()
