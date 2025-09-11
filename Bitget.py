import requests
import pandas as pd
from datetime import datetime
import time

def fetch_bitget_grey_status_tokens():
    """
    Fetches tokens from Bitget API where status is 'grey'.
    """
    # Bitget public API endpoint for symbols
    url = "https://api.bitget.com/api/v2/spot/public/symbols"
    
    # Rate limiting: Small delay to be respectful
    time.sleep(0.1)
    
    print("📡 Fetching symbol data from Bitget API...")
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Check if API call was successful
        if data.get('code') == '00000':  # Bitget success code
            symbols = data.get('data', [])
            print(f"✅ Successfully fetched {len(symbols)} trading symbols")
            
            # Filter for tokens where status is 'grey'
            grey_status_tokens = []
            for symbol in symbols:
                status = symbol.get('status', '').lower()
                if status == 'grey':
                    grey_status_tokens.append({
                        'pair': symbol.get('symbol'),
                        'base': symbol.get('baseCoin'),
                        'quote': symbol.get('quoteCoin'),
                        'status': symbol.get('status'),
                        'min_trade_amount': symbol.get('minTradeAmount'),
                        'max_trade_amount': symbol.get('maxTradeAmount'),
                        'last_updated': datetime.now().strftime('%Y-%m-%d')
                    })
            
            return grey_status_tokens
        else:
            print(f"❌ API Error: {data.get('msg', 'Unknown error')}")
            return []
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return []
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return []

# Fetch grey status tokens
grey_tokens = fetch_bitget_grey_status_tokens()

if grey_tokens:
    # Create DataFrame
    df = pd.DataFrame(grey_tokens)
    
    print(f"\n⚠️ Found {len(grey_tokens)} tokens with grey status:")
    print(df[['pair', 'base', 'quote', 'status', 'last_updated']])
    
    # Save to CSV
    filename = f"ST_Bitget.csv"
    df.to_csv(filename, index=False)
    print(f"\n💾 Data saved to {filename}")
else:
    print("\n✅ No tokens found with grey status")
    # Create empty CSV with headers
    df = pd.DataFrame(columns=['pair', 'base', 'quote', 'status', 'min_trade_amount', 'max_trade_amount', 'last_updated'])
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"bitget_grey_status_{timestamp}.csv"
    df.to_csv(filename, index=False)
    print(f"📁 Empty file created: {filename}")
