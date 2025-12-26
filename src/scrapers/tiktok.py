import feedparser
import re
from typing import List, Dict, Any
from datetime import datetime

class TikTokScraper:
    """
    Scrapes TikTok data via RSSHub to avoid direct scraping issues.
    """
    
    RSS_HUB_INSTANCES = [
        "https://rsshub.app",
        # Add mirrors if known, for now use main one
    ]

    def __init__(self):
        self.base_url = self.RSS_HUB_INSTANCES[0]

    def _clean_html(self, raw_html: str) -> str:
        """Removes HTML tags from description."""
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', raw_html)
        return cleantext

    def fetch_tag(self, tag: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Fetches latest videos for a hashtag.
        Route: /tiktok/tag/:tag
        """
        url = f"{self.base_url}/tiktok/tag/{tag}"
        print(f"Fetching TikTok tag: {tag} from {url}")
        feed = feedparser.parse(url)

        results = []
        if not feed.entries:
            print(f"No entries found for {tag}")
            return results

        for entry in feed.entries:
            # RSSHub maps TikTok fields to standard RSS fields
            # Description often contains the video caption + stats if available
            text_content = self._clean_html(entry.description)

            # Simple extraction of stats if embedded in text (depends on RSSHub implementation)
            # Usually RSSHub provides direct video links
            data_point = {
                "platform": "TikTok",
                "query": f"#{tag}",
                "guid": entry.id,
                "link": entry.link,
                "author": entry.get("author", "unknown"),
                "timestamp": entry.get("published", datetime.now().isoformat()),
                "content": text_content,
                "title": entry.title
            }
            results.append(data_point)
        # Limit results to requested number
        results = results[:limit]
        return results
        """
        Fetches latest videos for a hashtag.
        Route: /tiktok/tag/:tag
        """
        url = f"{self.base_url}/tiktok/tag/{tag}"
        print(f"Fetching TikTok tag: {tag} from {url}")
        feed = feedparser.parse(url)
        
        results = []
        if not feed.entries:
            print(f"No entries found for {tag}")
            return results

        for entry in feed.entries:
            # RSSHub maps TikTok fields to standard RSS fields
            # Description often contains the video caption + stats if available
            text_content = self._clean_html(entry.description)
            
            # Simple extraction of stats if embedded in text (depends on RSSHub implementation)
            # Usually RSSHub provides direct video links
            
            data_point = {
                "platform": "TikTok",
                "query": f"#{tag}",
                "guid": entry.id, # Video ID
                "link": entry.link,
                "author": entry.get("author", "unknown"),
                "timestamp": entry.get("published", datetime.now().isoformat()),
                "content": text_content,
                "title": entry.title
            }
            results.append(data_point)
            
        return results

    def fetch_user(self, username: str) -> List[Dict[str, Any]]:
        """
        Fetches latest videos for a user.
        Route: /tiktok/user/:username
        """
        url = f"{self.base_url}/tiktok/user/{username}"
        print(f"Fetching TikTok user: {username} from {url}")
        feed = feedparser.parse(url)
        
        results = []
        for entry in feed.entries:
            data_point = {
                "platform": "TikTok",
                "query": f"@{username}",
                "guid": entry.id,
                "link": entry.link,
                "author": username,
                "timestamp": entry.get("published", datetime.now().isoformat()),
                "content": self._clean_html(entry.description),
                "title": entry.title
            }
            results.append(data_point)
            
        return results

if __name__ == "__main__":
    # Test run
    scraper = TikTokScraper()
    # Test with a generic tag
    print(scraper.fetch_tag("finance")[:2])
