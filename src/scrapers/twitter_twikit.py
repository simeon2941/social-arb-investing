from twikit import Client
import asyncio
import random
from typing import List, Dict, Any

class TwitterScraper:
    def __init__(self):
        self.client = Client('en-US')
        self.initialized = False
        # REPLACE THESE WITH A BURNER ACCOUNT CREDENTIALS
        self.username = "YOUR_USERNAME"
        self.email = "YOUR_EMAIL"
        self.password = "YOUR_PASSWORD"

    async def _init_client(self):
        if not self.initialized:
            try:
                # Login is required for search in 2025
                if self.username != "YOUR_USERNAME":
                    await self.client.login(
                        auth_info_1=self.username,
                        auth_info_2=self.email,
                        password=self.password
                    )
                    self.initialized = True
                    print("Logged in to Twitter successfully.")
                else:
                    print("Twitter Login Skipped: No credentials provided in src/scrapers/twitter_twikit.py")
            except Exception as e:
                print(f"Twitter Login Failed: {e}")

    async def search_tweets(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        await self._init_client()
        try:
            # 'Latest' search tab
            tweets = await self.client.search_tweet(query, product='Latest', count=limit)
            
            results = []
            if not tweets:
                return []
                
            for tweet in tweets:
                results.append({
                    "text": tweet.text,
                    "url": f"https://twitter.com/{tweet.user.screen_name}/status/{tweet.id}",
                    "author": tweet.user.name,
                    "screen_name": tweet.user.screen_name,
                    "created_at": str(tweet.created_at),
                    "favorite_count": tweet.favorite_count,
                    "retweet_count": tweet.retweet_count
                })
            return results
        except Exception as e:
            print(f"TwitterScraper Error for {query}: {e}")
            return []

    def get_tweets_sync(self, ticker: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Synchronous wrapper for the engine"""
        query = f"${ticker} OR #{ticker} stock"
        try:
            return asyncio.run(self.search_tweets(query, limit))
        except Exception as e:
            print(f"Async loop error: {e}")
            return []

if __name__ == "__main__":
    # Test
    scraper = TwitterScraper()
    print("Fetching NVIDA tweets...")
    print(scraper.get_tweets_sync("NVDA", 3))
