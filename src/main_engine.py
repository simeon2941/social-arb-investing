import json
import os
from datetime import datetime
from src.scrapers.tiktok import TikTokScraper
from src.scrapers.reddit import RedditScraper
from src.scrapers.trends import TrendsScraper
from src.scrapers.news import NewsVerifier
from src.analysis.entity_resolution import EntityResolver
from src.analysis.sentiment import SentimentEngine
from src.analysis.risk import RiskManager
from src.analysis.bot_detector import BotDetector

from src.scrapers.weather import WeatherScraper

from src.scrapers.analyst import AnalystVerifier

from src.scrapers.twitter import TwitterScraper

class SocialArbEngine:
    """
    The Core Engine that runs the daily routine.
    """
    
    DATA_FILE = os.path.join("data", "ledger.json")
    HISTORY_FILE = os.path.join("data", "history.json")

    def __init__(self):
        self.tiktok = TikTokScraper()
        self.reddit = RedditScraper()
        self.twitter = TwitterScraper() # Start Twitter Scraper
        self.trends = TrendsScraper()
        self.weather = WeatherScraper()
        self.verifier = NewsVerifier()
        self.analyst = AnalystVerifier()
        self.resolver = EntityResolver()
        self.sentiment = SentimentEngine()
        self.risk = RiskManager()
        self.bot_detector = BotDetector()
        
    def run(self):
        print("Starting Social Arb Engine...")
        signals = []

        # 0. Phase 0: Physical Layer (Weather)
        print("--- Phase 0: Event Layer ---")
        weather_events = self.weather.check_hail_events()
        for event in weather_events:
            for ticker in event['likely_tickers']:
                signals.append({
                    "ticker": ticker,
                    "source": "Weather/Hail",
                    "raw_text": f"Hail Storm in {event['location']}",
                    "sentiment_score": 0.5, # Positive for roofing co
                    "timestamp": event['timestamp']
                })

        # 1. Fetch from Google Trends (high intent)
        print("--- Phase 1: Intent Layer ---")
        trend_entries = self.trends.fetch_daily_trends()
        for entry in trend_entries:
            # Check for entities
            tickers = self.resolver.resolve(entry['query'] + " " + entry['content'])
            if tickers:
                print(f"Found Entity in Trends: {entry['query']} -> {tickers}")
                for ticker in tickers:
                    signals.append({
                        "ticker": ticker,
                        "source": "GoogleTrends",
                        "raw_text": entry['query'],
                        "sentiment_score": 0.1, # Implied interest
                        "timestamp": entry['timestamp']
                    })

        # 2. Fetch from Reddit (discursive)
        print("--- Phase 2: Discursive Layer ---")
        # In production, iterate through list of watched subreddits
        subreddits = ["wallstreetbets", "stocks", "investing", "skincareaddiction"] 
        for sub in subreddits:
            posts = self.reddit.fetch_subreddit_new(sub, limit=10)
            for post in posts:
                # 0. Bot Detection Filter
                if self.bot_detector.is_bot(post):
                    print(f"Skipping Bot Post: {post['title']}")
                    continue

                tickers = self.resolver.resolve(post['content'])
                if tickers:
                     for ticker in tickers:
                        # Sentiment Check
                        sent = self.sentiment.analyze(post['content'])
                        
                        # Phase 3: Comment Deep Dive (The Wisdom of Crowds)
                        additional_sentiment = 0.0
                        if post.get('score', 0) > 50 and post.get('comments', 0) > 5:
                            # Verify with comments
                            permalink = post.get('link', '').replace("https://reddit.com", "")
                            if permalink:
                                comments = self.reddit.fetch_comments(permalink, limit=5)
                                crowd_confirmation = self.bot_detector.verify_comments(comments)
                                print(f"Crowd Confirmation for {ticker}: {crowd_confirmation}")
                                
                                # If crowd disagrees strongly, penalize sentiment
                                if sent['compound'] > 0 and crowd_confirmation < -0.1:
                                    print(f"Signal KILLED: Crowd Disagrees on {ticker}")
                                    sent['compound'] = -0.1 # Flip it or neutralize
                                else:
                                    additional_sentiment = crowd_confirmation * 0.5

                        final_sentiment = sent['compound'] + additional_sentiment

                        if final_sentiment > 0.05 or final_sentiment < -0.05:
                            signals.append({
                                "ticker": ticker,
                                "source": f"Reddit/r/{sub}",
                                "raw_text": post['title'],
                                "sentiment_score": final_sentiment,
                                "timestamp": post['timestamp']
                            })

        # 3. Aggregate Signals & Calculate Velocity
        print("--- Phase 3: Aggregation & Velocity ---")
        
        # Load History
        history = self._load_history()
        
        aggregated = {}
        for s in signals:
            t = s['ticker']
            if t not in aggregated:
                aggregated[t] = {"count": 0, "sentiment_sum": 0, "sources": []}
            aggregated[t]["count"] += 1
            aggregated[t]["sentiment_sum"] += s.get("sentiment_score", 0)
            aggregated[t]["sources"].append(s['source'])
            
        # 3b. Twitter Verification (Phase 2)
        # For high signal items, cross-check Twitter (Nitter)
        # This is expensive/slow so we only do it for active signals
        print("--- Phase 3b: Twitter Cross-Check ---")
        for ticker, data in aggregated.items():
            if data['count'] >= 1: # Threshold to verify
                 tweets = self.twitter.search_cashtag(ticker)
                 if tweets:
                     print(f"Found {len(tweets)} tweets for {ticker}")
                     data["sources"].append("Twitter/Nitter")
                     # Simple sentiment addition
                     data["count"] += len(tweets)
                     # Assuming tweets neutral/positive for now as we didn't score them individually in scraper
                     # Ideally we should score them.
                     
                     # Quick score of tweets
                     tweet_sentiment = 0
                     for tw in tweets:
                         score = self.sentiment.analyze(tw['content'])
                         tweet_sentiment += score['compound']
                     
                     data["sentiment_sum"] += tweet_sentiment

        # 4. Verification, Velocity & Risk
        print("--- Phase 4: Verification & Execution ---")
        final_output = []
        
        for ticker, data in aggregated.items():
            # Filter noise
            if data['count'] < 1: # Low threshold for demo
                continue

            avg_sentiment = data['sentiment_sum'] / data['count']
            
            # Calculate Velocity (Change in Volume)
            prev_data = history.get(ticker, {"count": 0})
            prev_count = prev_data.get("count", 0)
            velocity = data['count'] - prev_count # Simple difference for now
            
            # Verify Blind Spot (News Volume)
            priced_in = self.verifier.is_priced_in(ticker)
            blind_spot = not priced_in
            
            # Verify Analyst Asymmetry
            asymmetry_rating = self.analyst.analyze_asymmetry(ticker, avg_sentiment)
            
            # Risk Sizing (Smart Sizing with Velocity)
            est_shares = 0
            if blind_spot:
                # Bonus multiplier for high velocity
                # If velocity is high, we might size up, OR verify deeper
                est_shares = self.risk.calculate_position_size(ticker, 100.0, velocity=velocity) # Assume $100 price for sizing check

            final_output.append({
                "ticker": ticker,
                "signal_strength": data['count'],
                "velocity": velocity,
                "avg_sentiment": avg_sentiment,
                "blind_spot": blind_spot,
                "analyst_rating": asymmetry_rating,
                "est_position_shares": est_shares,
                "sources": list(set(data['sources'])), # unique sources
                "details": data
            })
            
        # Update History with current run stats
        self._update_history(history, aggregated)
        
        self.save_ledger(final_output)
        print("Engine Run Complete.")

    def _load_history(self) -> dict:
        if not os.path.exists(self.HISTORY_FILE):
            return {}
        try:
            with open(self.HISTORY_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return {}

    def _update_history(self, old_history: dict, current_agg: dict):
        """
        Updates history file. 
        For a real system, we'd append time-series.
        For zero-cost simple version, we store 'last_run_stats' to calc immediate velocity.
        """
        # We can implement a rolling window later. For now, just save current as 'last'
        with open(self.HISTORY_FILE, 'w') as f:
            json.dump(current_agg, f, indent=2)

    def save_ledger(self, data: list):
        # We append to history or overwrite? 
        # For Git-Scraping, overwriting a "current.json" is good for dashboards, 
        # appending to "history.json" is good for time series.
        # Let's save 'current_signals.json'
        output_path = os.path.join("data", "current_signals.json")
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Signals saved to {output_path}")

        # Also save to web directory for Vercel
        web_path = os.path.join("web", "data.json")
        with open(web_path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Web Dashboard data saved to {web_path}")

if __name__ == "__main__":
    engine = SocialArbEngine()
    engine.run()
