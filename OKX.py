import requests
import csv
import os
from datetime import datetime

API_URL = "https://www.okx.com/api/v5/public/instruments?instType=SPOT"
CSV_FILE = "ST_OKX.csv"

def fetch_instruments():
    resp = requests.get(API_URL, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return data.get("data", [])

def heuristic_risk_filter(instruments):
    """
    Example heuristic: flag instruments with unusual status or warning fields.
    Replace logic when OKX adds actual ST tagging.
    """
    risk_items = []
    for inst in instruments:
        # Example placeholder: if inst.get("state") == "warning": etc.
        if inst.get("instStatus") == "SUSPENDED":
            risk_items.append(inst)
    return risk_items

def save_to_csv(items):
    today = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["instId", "instType", "state", "timestamp"])
        for item in items:
            writer.writerow([item.get("instId"), item.get("instType"), item.get("instStatus"), today])

def main():
    instruments = fetch_instruments()
    risky = heuristic_risk_filter(instruments)
    print(f"Found {len(risky)} instruments matching heuristic risk filter.")
    if risky:
        save_to_csv(risky)

if __name__ == "__main__":
    main()
