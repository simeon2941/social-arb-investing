import feedparser
import requests
from typing import List, Dict, Any
from datetime import datetime
import xml.etree.ElementTree as ET

class TrendsScraper:
    """
    Fetches Google Trends Daily Data via RSS.
    """
    
    RSS_URL = "https://trends.google.com/trends/trendingsearches/daily/rss?geo=US"
    
    def fetch_daily_trends(self) -> List[Dict[str, Any]]:
        """
        Fetches the daily trending searches.
        """
        print(f"Fetching Google Trends from {self.RSS_URL}")
        feed = feedparser.parse(self.RSS_URL)
        
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
                "query": entry.title,
                "guid": entry.id,
                "link": entry.link,
                "timestamp": entry.get("published", datetime.now().isoformat()),
                "traffic": traffic,
                "content": entry.get("summary", "")
            })
            
        return results

if __name__ == "__main__":
    scraper = TrendsScraper()
    print(scraper.fetch_daily_trends()[:2])
