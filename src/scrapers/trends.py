import feedparser
import requests
from typing import List, Dict, Any
from datetime import datetime
import xml.etree.ElementTree as ET

class TrendsScraper:
    """
    Fetches Google Trends Daily Data via RSS.
    """
    
    RSS_URL = "https://trends.google.com/trending/rss?geo=US"
    
    def fetch_daily_trends(self) -> List[Dict[str, Any]]:
        """
        Fetches the daily trending searches.
        """
        print(f"Fetching Google Trends from {self.RSS_URL}")
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        try:
            response = requests.get(self.RSS_URL, headers=headers)
            response.raise_for_status()
            feed = feedparser.parse(response.content)
        except Exception as e:
            print(f"Error fetching Google Trends: {e}")
            return []
        
        results = []
        if not feed.entries:
            print("No entries found in Google Trends RSS.")
            return results

        for entry in feed.entries:
            # feedparser might hide some custom namespaces like ht:approx_traffic
            # but usually entry.content or summary has it.
            # For simplest implementation, we grab title and link.
            
            # Extract additional info if available
            traffic = "N/A"
            # feedparser usually puts custom tags in a dictionary.
            # 'ht_approx_traffic' might be the key.
            
            if 'ht_approx_traffic' in entry:
                traffic = entry['ht_approx_traffic']
            
            results.append({
                "platform": "GoogleTrends",
                "query": entry.get('title', 'Unknown'),
                "guid": entry.get('id') or entry.get('link') or entry.get('title'),
                "link": entry.get('link', ''),
                "timestamp": entry.get("published", datetime.now().isoformat()),
                "traffic": traffic,
                "content": entry.get("summary", "")
            })
            
        return results

class AdvancedTrendsScraper:
    """
    Advanced Google Trends analysis using pytrends (unofficial API).
    Supports:
    - Hype vs Value (Interest over time)
    - Sentiment Analysis (Bullish vs Bearish keywords)
    - Volatility correlations
    """
    
    def __init__(self):
        # delayed import to avoid hard dependency if not installed
        try:
            from pytrends.request import TrendReq
            # hl='en-US', tz=360 corresponds to US CST/central time mostly, or just standard US offset
            self.pytrends = TrendReq(hl='en-US', tz=360, timeout=(10,25))
        except ImportError:
            print("Error: pytrends not installed. Please run `pip install pytrends`.")
            self.pytrends = None

    def get_interest_over_time(self, keywords: List[str], timeframe: str = 'today 1-m') -> Dict[str, Any]:
        """
        Get interest over time for a list of keywords.
        timeframe examples: 'today 1-m', 'today 5-y', 'now 1-d'
        """
        if not self.pytrends:
            return {}
        
        try:
            print(f"Fetching interest over time for: {keywords} ({timeframe})")
            self.pytrends.build_payload(keywords, cat=0, timeframe=timeframe, geo='US', gprop='')
            data = self.pytrends.interest_over_time()
            if data.empty:
                return {}
            # Return as dict or raw dataframe wrapper
            return data
        except Exception as e:
            print(f"Error fetching interest over time: {e}")
            return {}

    def get_related_queries(self, keyword: str) -> Dict[str, Any]:
        """
        Get related queries (top and rising) for a specific keyword.
        """
        if not self.pytrends:
            return {}
        
        try:
            print(f"Fetching related queries for: {keyword}")
            self.pytrends.build_payload([keyword], cat=0, timeframe='today 1-m', geo='US', gprop='')
            related = self.pytrends.related_queries()
            return related.get(keyword, {})
        except Exception as e:
            print(f"Error fetching related queries: {e}")
            return {}

    def get_sentiment_index(self, symbol: str, bullish_terms: List[str] = None, bearish_terms: List[str] = None) -> Dict[str, Any]:
        """
        Construct a sentiment index by comparing search volume for Bullish vs Bearish terms.
        """
        if not bullish_terms:
            bullish_terms = [f"buy {symbol}", f"why is {symbol} up", f"{symbol} price target"]
        if not bearish_terms:
            bearish_terms = [f"sell {symbol}", f"why is {symbol} down", f"short {symbol}"]
            
        # Google Trends allows max 5 keywords per request. 
        # We might need to batch if lists are long, but here we assume small lists.
        # Let's pick the top 2 of each to compare in one graph if possible, or do separate requests.
        # For a simple ratio, let's take 1 representative term from each side or sum them up?
        # Safe approach: aggregate separately.
        
        # NOTE: Comparison implies relative volume. If we query them together, they are relative to each other.
        # If we query separate, they are normalized 0-100 independently (useless for comparison).
        # MUST query together.
        
        # Let's take the most potent term: "buy [symbol]" vs "sell [symbol]"
        kw_list = [bullish_terms[0], bearish_terms[0]] 
        
        data = self.get_interest_over_time(kw_list, timeframe='today 3-m')
        
        if data is None or data.empty:
            return None
            
        # Calculate simple ratio
        # Avoid division by zero
        # Sum of interest over the period
        total_bullish = data[kw_list[0]].sum()
        total_bearish = data[kw_list[1]].sum()
        
        return {
            "symbol": symbol,
            "total_bullish_volume": total_bullish,
            "total_bearish_volume": total_bearish,
            "sentiment_ratio": total_bullish / (total_bearish + 1), # +1 smoothing
            "timeframe": "today 3-m",
            "data": data  # Returns the dataframe for detailed plotting if needed
        }

if __name__ == "__main__":
    scraper = TrendsScraper()
    print(scraper.fetch_daily_trends()[:2])
