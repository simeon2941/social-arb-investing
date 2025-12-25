import requests
import feedparser
import random
import time
from typing import List, Dict, Any
from datetime import datetime
import urllib.parse

class TwitterScraper:
    """
    Scrapes Twitter via Nitter instances to avoid API costs.
    Implements instance rotation and failover.
    """
    
    # List of public Nitter instances (prone to change, need robust fallback)
    NITTER_INSTANCES = [
        "https://nitter.net",
        "https://nitter.cz",
        "https://nitter.privacydev.net",
        "https://nitter.projectsegfau.lt",
        "https://nitter.eu"
    ]

    def __init__(self):
        self.working_instances = self.NITTER_INSTANCES.copy()

    def _get_working_instance(self) -> str:
        """Returns a random instance from the working pool."""
        if not self.working_instances:
            print("Warning: All Nitter instances failed. Resetting pool.")
            self.working_instances = self.NITTER_INSTANCES.copy()
            
        return random.choice(self.working_instances)

    def search_cashtag(self, ticker: str) -> List[Dict[str, Any]]:
        """
        Searches for $TICKER on Twitter.
        """
        query = f"${ticker}"
        encoded_query = urllib.parse.quote(query)
        
        # Try up to 3 instances
        for _ in range(3):
            instance = self._get_working_instance()
            url = f"{instance}/search/rss?f=tweets&q={encoded_query}"
            
            print(f"Scraping Twitter {query} via {instance}...")
            
            try:
                # Set short timeout to fail fast
                feed = feedparser.parse(url)
                
                # Check for bozo bit (parsing error) or empty status if instance is down
                if feed.bozo and not feed.entries:
                    raise Exception("Parse Error or Empty Feed")
                    
                results = []
                for entry in feed.entries:
                    results.append({
                        "platform": "Twitter",
                        "query": query,
                        "guid": entry.id,
                        "link": entry.link,
                        "author": entry.author,
                        "timestamp": entry.get("published", datetime.now().isoformat()),
                        "content": entry.title, # Nitter RSS often puts content in title
                        "sentiment_score": 0 # To be filled by analyzer
                    })
                
                # If success, return immediately
                return results

            except Exception as e:
                print(f"Instance {instance} failed: {e}")
                if instance in self.working_instances:
                    self.working_instances.remove(instance)
                time.sleep(1)
                
        print(f"Failed to scrape Twitter for {ticker} after retries.")
        return []

if __name__ == "__main__":
    ts = TwitterScraper()
    print(ts.search_cashtag("AAPL"))
