from src.scrapers.trends import TrendsScraper
from src.analysis.entity_resolution import EntityResolver

def debug_trends():
    scraper = TrendsScraper()
    resolver = EntityResolver()
    
    print("Fetching Trends with headers...")
    urls = [
        "https://trends.google.com/trends/trendingsearches/daily/rss?geo=US",
        "https://trends.google.com/trending/rss?geo=US"
    ]
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    import requests
    import feedparser
    
    trends = []
    
    for url in urls:
        print(f"Trying {url}...")
        resp = requests.get(url, headers=headers)
        print(f"Status Code: {resp.status_code}")
        
        if resp.status_code == 200:
            feed = feedparser.parse(resp.content)
            print(f"Feed Entries: {len(feed.entries)}")
            if feed.entries:
                first_entry = feed.entries[0]
                print(f"First Entry Keys: {first_entry.keys()}")
                print(f"First Entry Content: {first_entry}")
                trends = feed.entries
                break
    
    matches = 0
    for t in trends:
        query = t['query']
        content = t['content']
        text = f"{query} {content}"
        
        tickers = resolver.resolve(text)
        print(f"Checking: '{query}' -> Match: {tickers}")
        
        if tickers:
            matches += 1
            
    print(f"Total Matches: {matches}")

if __name__ == "__main__":
    debug_trends()
