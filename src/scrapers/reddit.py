import requests
import time
from typing import List, Dict, Any
from datetime import datetime

class RedditScraper:
    """
    Scrapes Reddit data using the public JSON endpoints.
    Note: Strict rate limits apply. 
    """
    
    BASE_URL = "https://www.reddit.com"
    
    def __init__(self, user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"):
        self.headers = {"User-Agent": user_agent}

    def fetch_subreddit_new(self, subreddit: str, limit: int = 25) -> List[Dict[str, Any]]:
        """
        Fetches new posts from a subreddit.
        """
        url = f"{self.BASE_URL}/r/{subreddit}/new.json?limit={limit}"
        print(f"Fetching Reddit: r/{subreddit} from {url}")
        
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code != 200:
                print(f"Error fetching {subreddit}: {response.status_code}")
                return []
                
            data = response.json()
            posts = data.get("data", {}).get("children", [])
            
            results = []
            for post in posts:
                p_data = post.get("data", {})
                results.append({
                    "platform": "Reddit",
                    "query": f"r/{subreddit}",
                    "guid": p_data.get("id"),
                    "link": f"https://reddit.com{p_data.get('permalink')}",
                    "author": p_data.get("author"),
                    "timestamp": datetime.fromtimestamp(p_data.get("created_utc", 0)).isoformat(),
                    "content": f"{p_data.get('title')} {p_data.get('selftext', '')}",
                    "title": p_data.get("title"),
                    "score": p_data.get("score"),
                    "comments": p_data.get("num_comments")
                })
            return results
            
        except Exception as e:
            print(f"Exception fetching {subreddit}: {e}")
            return []

    def search(self, query: str, limit: int = 25) -> List[Dict[str, Any]]:
        """
        Searches Reddit for a keyword.
        """
        url = f"{self.BASE_URL}/search.json?q={query}&sort=new&limit={limit}"
        print(f"Searching Reddit for: {query}")
        
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code != 200:
                print(f"Error searching {query}: {response.status_code}")
                return []
                
            data = response.json()
            posts = data.get("data", {}).get("children", [])
            
            results = []
            for post in posts:
                p_data = post.get("data", {})
                results.append({
                    "platform": "Reddit",
                    "query": query,
                    "guid": p_data.get("id"),
                    "link": f"https://reddit.com{p_data.get('permalink')}",
                    "author": p_data.get("author"),
                    "timestamp": datetime.fromtimestamp(p_data.get("created_utc", 0)).isoformat(),
                    "content": f"{p_data.get('title')} {p_data.get('selftext', '')}",
                    "title": p_data.get("title"),
                    "score": p_data.get("score"),
                    "comments": p_data.get("num_comments")
                })
            return results

        except Exception as e:
            print(f"Exception searching {query}: {e}")
            return []

if __name__ == "__main__":
    scraper = RedditScraper()
    print(scraper.fetch_subreddit_new("wallstreetbets", limit=2))
