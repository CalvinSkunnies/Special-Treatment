import requests
import pandas as pd
from datetime import datetime
import time

def fetch_binance_break_status_tokens():
    """
    Fetches tokens from Binance API that are in 'BREAK' status.
    Reference: https://developers.binance.com/docs/binance-spot-api-docs/enums#symbol-status-status
    """
    # Binance API endpoint
    url = "https://api.binance.com/api/v3/exchangeInfo"
    
    # Rate limiting: Binance allows 1200 requests per minute
    time.sleep(0.2)
    
    print("📡 Fetching exchange information from Binance API...")
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Filter for symbols with 'BREAK' status
        break_tokens = []
        for symbol in data.get('symbols', []):
            status = symbol.get('status', '')
            if status == "BREAK":
                break_tokens.append({
                    'pair': symbol.get('symbol'),
                    'base': symbol.get('baseAsset'),
                    'quote': symbol.get('quoteAsset'),
                    'status': status,
                    'last_updated': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                })
        
        print(f"✅ Found {len(break_tokens)} tokens with BREAK status")
        return break_tokens
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return []
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return []

# Fetch BREAK status tokens
break_tokens = fetch_binance_break_status_tokens()

if break_tokens:
    # Create DataFrame
    df = pd.DataFrame(break_tokens)
    
    # Save to CSV with timestamp
    filename = f"ST_Binance.csv"
    df.to_csv(filename, index=False)
    print(f"\n💾 Data saved to {filename}")
    
    # Show results
    print(f"\n⚠️ Tokens with BREAK status ({len(break_tokens)}):")
    print(df[['pair', 'base', 'quote']].to_string(index=False))
else:
    print("\n✅ No Binance trading pairs are currently in BREAK status")
    # Create empty CSV with headers
    df = pd.DataFrame(columns=['pair', 'base', 'quote', 'status', 'last_updated'])
    filename = f"ST_Binance.csv"
    df.to_csv(filename, index=False)
    print(f"📁 Empty file created: {filename}")

# Optional: Print documentation reference
print("\n📚 Reference:")
print("https://developers.binance.com/docs/binance-spot-api-docs/enums#symbol-status-status")
print("BREAK status: Trading is temporarily suspended for this symbol")
