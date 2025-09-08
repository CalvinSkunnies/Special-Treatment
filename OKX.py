import requests
import pandas as pd
from datetime import datetime
import time

def fetch_okx_instrument_states():
    """
    Fetches the state/status of all spot trading pairs from OKX API.
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
            
            # Extract state information
            state_data = []
            for inst in instruments:
                state_data.append({
                    'pair': inst.get('instId'),
                    'base': inst.get('baseCcy'),
                    'quote': inst.get('quoteCcy'),
                    'state': inst.get('state'),
                    'min_order_size': inst.get('minSz'),
                    'tick_size': inst.get('tickSz'),
                    'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
            
            return state_data
        else:
            print(f"❌ API Error: {data.get('msg', 'Unknown error')}")
            return []
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return []
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return []

def filter_special_status(df):
    """
    Filter tokens with non-standard trading status.
    """
    # Define normal trading state
    normal_state = 'live'
    
    # Find tokens with special status
    special_status = df[df['state'] != normal_state]
    
    return special_status

# Fetch data
instrument_states = fetch_okx_instrument_states()

if instrument_states:
    # Create DataFrame
    df = pd.DataFrame(instrument_states)
    
    # Display summary
    print(f"\n📊 Status Summary:")
    print(df['state'].value_counts())
    
    # Show special status tokens
    special_tokens = filter_special_status(df)
    if not special_tokens.empty:
        print(f"\n⚠️ Tokens with special status ({len(special_tokens)}):")
        print(special_tokens[['pair', 'state', 'base', 'quote']])
    else:
        print("\n✅ All spot trading pairs are in normal 'live' status")
    
    # Save to CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"ST_OKX.csv"
    df.to_csv(filename, index=False)
    print(f"\n💾 Full data saved to {filename}")
else:
    print("❌ Failed to fetch instrument state data")
