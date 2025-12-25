import feedparser
import urllib.parse
from typing import List, Dict, Any
from datetime import datetime, timedelta

class NewsVerifier:
    """
    Checks Google News to verify if a trend is 'Priced In'.
    """
    
    BASE_RSS_URL = "https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"

    def fetch_news_volume(self, ticker: str, query: str = None, hours_lookback: int = 48) -> int:
        """
        Counts news articles in the last N hours for a ticker/query.
        """
        search_term = query if query else ticker
        encoded_query = urllib.parse.quote(search_term)
        url = self.BASE_RSS_URL.format(query=encoded_query)
        
        print(f"Verifying news volume for {search_term} from {url}")
        feed = feedparser.parse(url)
        
        if not feed.entries:
            return 0
            
        count = 0
        cutoff_time = datetime.now() - timedelta(hours=hours_lookback)
        
        for entry in feed.entries:
            # Parse published date
            # format usually: 'Tue, 24 Dec 2024 22:00:00 GMT'
            try:
                published_dt = datetime(*entry.published_parsed[:6])
                if published_dt > cutoff_time:
                    count += 1
            except Exception:
                # If parsing fails, assume it's recent enough or skip?
                # We'll skip to be safe/conservative (if we can't verify time, don't count it? Or count it as noise?)
                # Actually, counting it as noise (volume) means we assume it IS priced in.
                # So to return a high count (priced in), we should be generous.
                count += 1
                
        return count

    def is_priced_in(self, ticker: str, threshold: int = 10) -> bool:
        """
        Returns True if news volume exceeds threshold.
        """
        volume = self.fetch_news_volume(ticker)
        print(f"News Volume for {ticker}: {volume}")
        return volume > threshold

if __name__ == "__main__":
    verifier = NewsVerifier()
    print(f"Is AAPL priced in? {verifier.is_priced_in('AAPL')}")
