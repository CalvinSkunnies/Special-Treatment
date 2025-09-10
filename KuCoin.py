import requests
import pandas as pd
from datetime import datetime
import time

def fetch_kucoin_st_tokens():
    """
    Fetches tokens from KuCoin API that have 'ST' in their tags (case-insensitive).
    """
    # KuCoin public API endpoint for symbols
    url = "https://api.kucoin.com/api/v2/symbols"
    
    # Rate limiting: Small delay to be respectful
    time.sleep(0.1)
    
    print("📡 Fetching symbol data from KuCoin API...")
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Check if API call was successful
        if data.get('code') == '200000':  # KuCoin success code
            symbols = data.get('data', [])
            print(f"✅ Successfully fetched {len(symbols)} trading symbols")
            
            # Filter for tokens with ST tag (case-insensitive)
            st_tokens = []
            for symbol in symbols:
                # Convert tags to uppercase and check for 'ST'
                st_value = symbol.get('st', 'false')
                if st_value == "true" : # This checks for 'ST', 'st', 'St', 'sT', etc.
                    st_tokens.append({
                        'pair': symbol.get('symbol'),
                        'base': symbol.get('baseCurrency'),
                        'quote': symbol.get('quoteCurrency'),
                        'st': st_value,
                        'status': symbol.get('enableTrading'),
                        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
            return st_tokens
        else:
            print(f"❌ API Error: {data.get('msg', 'Unknown error')}")
            return []
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return []
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return []

# Fetch ST-tagged tokens
st_tokens = fetch_kucoin_st_tokens()

if st_tokens:
    # Create DataFrame
    df = pd.DataFrame(st_tokens)
    
    print(f"\n⚠️ Found {len(st_tokens)} ST-tagged trading pairs:")
    print(df[['pair', 'base', 'quote', 'st']])
    
    # Save to CSV
    filename = f"ST_KuCoin.csv"
    df.to_csv(filename, index=False)
    print(f"\n💾 Data saved to {filename}")
else:
    print("\n✅ No trading pairs are currently ST-tagged")
    # Create empty CSV with headers
    df = pd.DataFrame(columns=['pair', 'base', 'quote', 'st', 'status', 'last_updated'])
    filename = f"ST_KuCoin.csv"
    df.to_csv(filename, index=False)
    print(f"📁 Empty file created: {filename}")
