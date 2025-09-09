#Huobi
import requests
import pandas as pd
from datetime import datetime
import time

def fetch_htx_suspended_or_st_tokens():
    """
    Fetches tokens from HTX API that are either:
    1. In 'suspend' state, OR
    2. Have 'st' in their tags list
    """
    # HTX API endpoint
    url = "https://api.huobi.pro/v1/settings/common/symbols"
    
    # Rate limiting: Small delay to be respectful
    time.sleep(0.1)
    
    print("📡 Fetching symbol data from HTX API...")
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Check if API call was successful
        if data.get('status') == 'ok':
            symbols = data.get('data', [])
            print(f"✅ Successfully fetched {len(symbols)} trading symbols")
            
            # Filter for suspended tokens OR tokens with "st" tag
            special_tokens = []
            for symbol in symbols:
                state = symbol.get('state')
                # Ensure tags is always a list, even if the value is None
                tags = symbol.get('tags') or [] # This converts None to []
                
                # Check if state is suspended OR if "st" is in tags
                if state == 'suspend' or 'st' in tags:
                    special_tokens.append({
                        'pair': symbol.get('symbol'), # Use 'symbol' for the trading pair
                        'base': symbol.get('bc'),
                        'quote': symbol.get('qc'), # Use 'quote-currency'
                        'state': state,
                        'tags': symbol.get('tags'),
                        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
            
            return special_tokens
        else:
            print(f"❌ API Error: {data.get('err-msg', 'Unknown error')}")
            return []
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return []
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return []

# Fetch special tokens (suspended or with st tag)
special_tokens = fetch_htx_suspended_or_st_tokens()

if special_tokens:
    # Create DataFrame
    df = pd.DataFrame(special_tokens)
    
    # Separate counts
    suspended_count = len(df[df['state'] == 'suspend'])
    st_tag_count = len(df[df['tags'].str.contains('st', na=False)])
    
    print(f"\n🔍 Found {len(special_tokens)} special trading pairs:")
    print(f"  • {suspended_count} in 'suspend' state")
    print(f"  • {st_tag_count} with 'st' tag")
    
    # Show the results
    print("\nSpecial Tokens:")
    print(df[['pair', 'state', 'tags', 'base', 'quote']])
    
    # Save to CSV
    filename = f"ST_Huobi.csv"
    df.to_csv(filename, index=False)
    print(f"\n💾 Data saved to {filename}")
else:
    print("\n✅ No trading pairs are currently suspended or have 'st' tag")
    # Create empty CSV with headers
    df = pd.DataFrame(columns=['pair', 'base', 'quote', 'state', 'tags', 'last_updated'])
    filename = f"ST_Huobi.csv"
    df.to_csv(filename, index=False)
    print(f"📁 Empty file created: {filename}")
