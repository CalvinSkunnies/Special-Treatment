import requests
import pandas as pd
from datetime import datetime
import time

def fetch_okx_suspended_tokens():
    """
    Fetches only tokens with 'suspend' state from OKX API.
    """
    # OKX public API endpoint for instruments
    url = "https://www.okx.com/api/v5/public/instruments"
    params = {
        'instType': 'SPOT'  # Only fetch spot trading pairs
    }
    
    # Rate limiting: OKX allows 20 requests per 2 seconds
    time.sleep(0.1)  # Small delay to be safe
    
    print("📡 Fetching instrument data from OKX API...")
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Check if API call was successful
        if data.get('code') == '0':  # OKX success code
            instruments = data.get('data', [])
            print(f"✅ Successfully fetched {len(instruments)} spot instruments")
            
            # Filter for suspended tokens only
            suspended_tokens = []
            for inst in instruments:
                if inst.get('state') == 'suspend':
                    suspended_tokens.append({
                        'pair': inst.get('instId'),
                        'base': inst.get('baseCcy'),
                        'quote': inst.get('quoteCcy'),
                        'state': inst.get('state'),
                        'min_order_size': inst.get('minSz'),
                        'tick_size': inst.get('tickSz'),
                        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
            
            return suspended_tokens
        else:
            print(f"❌ API Error: {data.get('msg', 'Unknown error')}")
            return []
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return []
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return []

# Fetch suspended tokens
suspended_tokens = fetch_okx_suspended_tokens()

if suspended_tokens:
    # Create DataFrame
    df = pd.DataFrame(suspended_tokens)
    
    print(f"\n⚠️ Found {len(suspended_tokens)} suspended trading pairs:")
    print(df[['pair', 'base', 'quote']])
    
    # Save to CSV
    filename = f"ST_OKX.csv"
    df.to_csv(filename, index=False)
    print(f"\n💾 Data saved to {filename}")
else:
    print("\n✅ No trading pairs are currently suspended")
    # Create empty CSV with headers
    df = pd.DataFrame(columns=['pair', 'base', 'quote', 'state', 'min_order_size', 'tick_size', 'last_updated'])
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"ST_OKX.csv"
    df.to_csv(filename, index=False)
    print(f"📁 Empty file created: {filename}")
