# BITGET
import requests
import csv
import os
from datetime import datetime
import time
import re
from urllib.parse import quote

API_URL = "https://api.bitget.com/api/v3/market/instruments"
TRADING_PAGE_BASE = "https://www.bitget.com/en/trade/{}_SPBL"
CSV_FILE = "ST_Bitget.csv"
RATE_LIMIT_DELAY = 1.0  # Increased delay for web scraping to avoid rate limits

def fetch_spot_instruments():
    """Fetch spot instruments from Bitget public API."""
    try:
        params = {"category": "SPOT"}
        resp = requests.get(API_URL, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") != "00000":
            raise Exception(f"API error: {data}")
        return data.get("data", [])
    except Exception as e:
        print(f"Error fetching instruments: {e}")
        return []

def check_st_tag(symbol):
    """Check if a symbol has symbolType: 'st' by scraping its trading page."""
    try:
        url = TRADING_PAGE_BASE.format(quote(symbol))
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        # Search for "symbolType":"st" in the response
        if re.search(r'"symbolType":"st"', resp.text):
            print(f"Found ST tag for {symbol}")
            return True
        return False
    except Exception as e:
        print(f"Error checking ST tag for {symbol}: {e}")
        return False

def filter_st_tokens(instruments):
    """Filter instruments with symbolType: 'st' by scraping trading pages."""
    st_items = []
    for inst in instruments:
        symbol = inst.get("symbol", "")
        if check_st_tag(symbol):
            st_items.append(inst)
        time.sleep(RATE_LIMIT_DELAY)  # Avoid rate limits
    return st_items

def read_existing_for_today():
    """Read CSV entries for today; returns set of 'pair's already logged."""
    today = datetime.utcnow().strftime("%Y-%m-%d")
    existing = set()
    if not os.path.isfile(CSV_FILE):
        return existing

    try:
        with open(CSV_FILE, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames or "date" not in reader.fieldnames or "pair" not in reader.fieldnames:
                return existing  # Skip if header mismatch
            for row in reader:
                if row["date"].startswith(today):
                    existing.add(row["pair"])
    except Exception as e:
        print(f"Error reading CSV: {e}")
    return existing

def append_to_csv(st_items):
    """Append ST-tagged tokens for today into the CSV."""
    file_exists = os.path.isfile(CSV_FILE)
    today_ts = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    existing = read_existing_for_today()

    try:
        with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists or os.path.getsize(CSV_FILE) == 0:
                writer.writerow(["pair", "base", "quote", "date"])

            for inst in st_items:
                base = inst.get("baseCoin", "")
                quote = inst.get("quoteCoin", "")
                pair = f"{base}/{quote}"
                if pair not in existing:
                    writer.writerow([pair, base, quote, today_ts])
                    print(f"✅ Added: {pair}")
                else:
                    print(f"⏩ Skipped duplicate today: {pair}")
    except Exception as e:
        print(f"Error writing to CSV: {e}")

def main():
    print("Fetching Bitget spot instruments...")
    instruments = fetch_spot_instruments()
    print(f"Fetched {len(instruments)} instruments.")

    print("Checking for ST-tagged tokens via trading page scraping...")
    st_items = filter_st_tokens(instruments)
    print(f"Found {len(st_items)} instruments with ST tag.")
    if st_items:
        append_to_csv(st_items)
    else:
        print("No ST-tagged instruments found. Check trading pages or announcements.")

if __name__ == "__main__":
    main()
