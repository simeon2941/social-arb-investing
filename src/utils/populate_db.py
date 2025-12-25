import pandas as pd
import json
import os
import requests

def populate_sp500():
    print("Fetching S&P 500 data...")
    try:
        # Use Wikipedia as source
        url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        tables = pd.read_html(response.text)
        df = tables[0]
        
        # Standardize columns
        # Ticker column usually 'Symbol'
        # Name column usually 'Security'
        
        companies = []
        for index, row in df.iterrows():
            ticker = row.get('Symbol')
            name = row.get('Security')
            
            if not ticker or not name:
                continue
                
            # Create aliases based on common variations
            name_clean = name.lower()
            aliases = [name_clean]
            
            # Remove "Inc.", "Corp.", etc for aliases
            simple_name = name_clean.replace(" inc.", "").replace(" corp.", "").replace(" co.", "").replace(" plc", "").strip()
            if simple_name != name_clean:
                aliases.append(simple_name)
                
            # Handle special cases (e.g. GOOG/GOOGL -> Google)
            if "alphabet" in name_clean:
                aliases.append("google")
            if "meta platforms" in name_clean:
                aliases.append("facebook")
                aliases.append("meta")
            
            companies.append({
                "symbol": ticker,
                "name": name,
                "aliases": list(set(aliases))
            })
            
        # Save to data/sp500.json
        output_path = os.path.join("data", "sp500.json")
        with open(output_path, "w") as f:
            json.dump(companies, f, indent=2)
            
        print(f"Successfully saved {len(companies)} companies to {output_path}")
        return True
        
    except Exception as e:
        print(f"Failed to populate S&P 500: {e}")
        return False

if __name__ == "__main__":
    populate_sp500()
