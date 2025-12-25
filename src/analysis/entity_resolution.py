import json
import re
from typing import Optional, Dict, List
import os

class EntityResolver:
    """
    Maps text to financial tickers using a local JSON database.
    """
    
    DB_PATH = os.path.join("data", "companies.json")

    def __init__(self):
        self.companies = self._load_db()
        # Build inverted index for fast lookup: alias -> ticker
        self.alias_map = self._build_alias_map()

    def _load_db(self) -> List[Dict]:
        # Priority 1: S&P 500 full list
        sp500_path = os.path.join("data", "sp500.json")
        if os.path.exists(sp500_path):
            with open(sp500_path, 'r', encoding='utf-8') as f:
                return json.load(f)

        # Priority 2: Manual list
        if not os.path.exists(self.DB_PATH):
            print(f"Warning: {self.DB_PATH} not found. Returning empty DB.")
            return []
        try:
            with open(self.DB_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading companies DB: {e}")
            return []

    def _build_alias_map(self) -> Dict[str, str]:
        """
        Creates a dictionary mapping lowercased aliases to tickers.
        """
        mapping = {}
        for company in self.companies:
            ticker = company.get("symbol")
            if not ticker:
                continue
                
            # Add official name
            name = company.get("name", "").lower()
            if name:
                mapping[name] = ticker
                
            # Add aliases
            aliases = company.get("aliases", [])
            for alias in aliases:
                mapping[alias.lower()] = ticker
                
        return mapping

    def resolve(self, text: str) -> List[str]:
        """
        Finds mentioned tickers in the text.
        Returns a list of unique tickers found.
        """
        text_lower = text.lower()
        found_tickers = set()
        
        # 1. Direct Ticker search via Regex ($TICKER)
        # Note: This is simplistic. $AAPL is clear, but just AAPL might be noise if not careful.
        # We stick to $TICKER format or explicit name matching for this version.
        ticker_matches = re.findall(r'\$([A-Za-z]{1,5})', text)
        for t in ticker_matches:
            # Verify it's a known ticker if possible, or just accept it as a potential signal
            found_tickers.add(t.upper())

        # 2. Alias/Name search
        # This is O(N*M) where N is text words and M is aliases.
        # Optimized approach: Check if alias strings exist in text.
        for alias, ticker in self.alias_map.items():
            # word boundary check to avoid substring matches (e.g. "for" in "Ford")
            # Simple regex for the alias
            if re.search(r'\b' + re.escape(alias) + r'\b', text_lower):
                found_tickers.add(ticker)

        return list(found_tickers)

if __name__ == "__main__":
    # Create dummy DB for testing if not exists
    if not os.path.exists("data"):
        os.makedirs("data")
    
    dummy_db = [
        {"symbol": "AAPL", "name": "Apple Inc", "aliases": ["iphone", "macbook", "apple"]},
        {"symbol": "TSLA", "name": "Tesla", "aliases": ["cybertruck", "model 3"]},
        {"symbol": "NVO", "name": "Novo Nordisk", "aliases": ["ozempic", "wegovy"]}
    ]
    with open("data/companies.json", "w") as f:
        json.dump(dummy_db, f)

    resolver = EntityResolver()
    print(resolver.resolve("I just bought a new iPhone and it's amazing! $AAPL"))
    print(resolver.resolve("Ozempic is changing everything."))
