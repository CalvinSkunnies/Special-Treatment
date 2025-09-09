import requests
import pandas as pd
from datetime import datetime
import time

def fetch_coinbase_special_status_tokens():
    """
    Fetches Coinbase products that are not in 'online' status.
    """
    # Coinbase API endpoint for products (trading pairs)
    url = "https://api.exchange.coinbase.com/products"
    
    # Headers to mimic a legitimate request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    # Rate limiting: Coinbase allows 3 requests per second
    time.sleep(0.34)
    
    print("📡 Fetching product data from Coinbase API...")
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Coinbase returns a list of product objects directly
        print(f"✅ Successfully fetched {len(data)} trading products")
        
        # Filter for products not in 'online' status
        special_status_tokens = []
        for product in data:
            status = product.get('status', '').lower()
            # Define normal trading status
            if status != 'online':
                special_status_tokens.append({
                    'pair': product.get('id'), # e.g., BTC-USD
                    'base': product.get('base_currency'),
                    'quote': product.get('quote_currency'),
                    'status': status,
                    'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
        
        return special_status_tokens
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return []
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return []

# Fetch special status tokens
special_tokens = fetch_coinbase_special_status_tokens()

if special_tokens:
    # Create DataFrame
    df = pd.DataFrame(special_tokens)
    
    print(f"\n⚠️ Found {len(special_tokens)} Coinbase products with special status:")
    print(df[['pair', 'base', 'quote', 'status']])
    
    # Save to CSV
    filename = f"ST_Coinbase.csv"
    df.to_csv(filename, index=False)
    print(f"\n💾 Data saved to {filename}")
else:
    print("\n✅ All Coinbase trading products are in normal 'online' status")
    # Create empty CSV with headers
    df = pd.DataFrame(columns=['pair', 'base', 'quote', 'status', 'last_updated'])
    filename = f"ST_Coinbase.csv"
    df.to_csv(filename, index=False)
    print(f"📁 Empty file created: {filename}")
