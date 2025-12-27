import json
import os
from datetime import datetime
from src.scrapers.tiktok import TikTokScraper
from src.scrapers.instagram import InstagramScraper
from src.scrapers.reddit import RedditScraper
from src.scrapers.trends import TrendsScraper, AdvancedTrendsScraper
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

    CONFIG_FILE = "config.json"

    def __init__(self):
        self._load_config()
        self.tiktok = TikTokScraper()
        self.instagram = InstagramScraper()
        self.reddit = RedditScraper()
        self.twitter = TwitterScraper() 
        self.trends = TrendsScraper()
        self.advanced_trends = AdvancedTrendsScraper() # Advanced logic
        self.weather = WeatherScraper()
        self.verifier = NewsVerifier()
        self.analyst = AnalystVerifier()
        self.resolver = EntityResolver()
        self.sentiment = SentimentEngine()
        self.risk = RiskManager()
        self.bot_detector = BotDetector()
        
        # Helper for price
        try:
            import yfinance as yf
            self.yf = yf
        except ImportError:
            self.yf = None
        
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

        # 1.5 Instagram Layer (visual hype)
        # 1.5 Instagram Layer (visual hype)
        print("--- Phase 1.5: Instagram Layer ---")
        # Placeholder usernames; replace with real influencer accounts
        insta_config = self.config.get("scrapers", {}).get("instagram", {})
        insta_usernames = insta_config.get("usernames", ["financeinfluencer1", "financeinfluencer2"])
        insta_limit = insta_config.get("limit", 5)
        insta_posts = self.instagram.fetch_posts(insta_usernames, limit=insta_limit)
        for post in insta_posts:
            tickers = self.resolver.resolve(post.get('caption', ''))
            if tickers:
                for ticker in tickers:
                    sent = self.sentiment.analyze(post.get('caption', ''))
                    if sent['compound'] > 0.05 or sent['compound'] < -0.05:
                        signals.append({
                            "ticker": ticker,
                            "source": post.get('permalink', f"Instagram/{post.get('username', 'unknown')}"),
                            "raw_text": post.get('caption', ''),
                            "sentiment_score": sent['compound'],
                            "timestamp": post.get('timestamp')
                        })

                # 1.6 TikTok Layer (viral hype)
        print("--- Phase 1.6: TikTok Layer ---")
        tiktok_config = self.config.get("scrapers", {}).get("tiktok", {})
        tiktok_tags = tiktok_config.get("tags", ["finance", "stockmarket"])
        tiktok_limit = tiktok_config.get("limit", 5)
        for tag in tiktok_tags:
            posts = self.tiktok.fetch_tag(tag, limit=tiktok_limit)
            for post in posts:
                tickers = self.resolver.resolve(post.get('content', ''))
                if tickers:
                    for ticker in tickers:
                        sent = self.sentiment.analyze(post.get('content', ''))
                        if sent['compound'] > 0.05 or sent['compound'] < -0.05:
                            signals.append({
                                "ticker": ticker,
                                "source": post.get('link', f"TikTok/{tag}"),
                                "raw_text": post.get('content', ''),
                                "sentiment_score": sent['compound'],
                                "timestamp": post.get('timestamp')
                            })
        # 2. Fetch from Reddit (discursive)
        # 2. Reddit Layer (Expanded)
        print("--- Phase 2: Reddit Discussion Layer ---")
        # Define the 'investment universe' of subreddits
        subs = [
            "wallstreetbets", "stocks", "investing", "options", "pennystocks", 
            "stockmarket", "thetagang", "dividends", "SPACs", "smallstreetbets",
            "Daytrading", "SwingTrading", "ValueInvesting", "SecurityAnalysis",
            "shortsqueeze", "RobinHood"
        ]
        
        # We use the new batch fetcher
        reddit_posts = self.reddit.fetch_feed(subreddits=subs, limit=50)
        
        for post in reddit_posts:
            # 0. Bot Detection Filter
                if self.bot_detector.is_bot(post):
                    print(f"Skipping Bot Post: {post['title']}")
                    continue

                # Resolve entity from Title + Content
                text_to_scan = f"{post.get('title')} {post.get('content')}"
                tickers = self.resolver.resolve(text_to_scan)
                
                if tickers:
                    for ticker in tickers:
                        # Sentiment Check
                        sent = self.sentiment.analyze(text_to_scan)
                        
                        # Simplified appending (Crowd Wisdom disabled for speed/stability temporarily)
                        signals.append({
                            "ticker": ticker,
                            "source": f"Reddit: {post.get('subreddit')}", 
                            "raw_text": post.get('title'),
                            "sentiment_score": sent['compound'],
                            "timestamp": post['timestamp'],
                            "link": post.get('link')
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
        if self.config.get("scrapers", {}).get("twitter", {}).get("enabled", True):
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
        else:
            print("--- Phase 3b: Twitter Cross-Check (SKIPPED per config) ---")

        # 3c. Advanced Trends & Price Overlay
        print("--- Phase 3c: Trends & Price Context ---")
        for ticker, data in aggregated.items():
            if data['count'] >= 1:
                # 1. Google Trends Sentiment
                # checks Hype (Volume) and Sentiment (Bull/Bear ratio)
                print(f"Analyzing Trends for {ticker}...")
                trend_data = self.advanced_trends.get_sentiment_index(ticker)
                
                if trend_data:
                    data['trend_sentiment'] = float(trend_data.get('sentiment_ratio', 0))
                    data['bullish_vol'] = int(trend_data.get('total_bullish_volume', 0))
                    data['bearish_vol'] = int(trend_data.get('total_bearish_volume', 0))
                    
                    # Weight it into the main sentiment?
                    # For now keep separate for the dashboard
                
                # 2. Live Price (yfinance)
                if self.yf:
                    try:
                        t = self.yf.Ticker(ticker)
                        hist = t.history(period="1d")
                        if not hist.empty:
                            current_price = hist['Close'].iloc[-1]
                            data['current_price'] = float(current_price)
                            print(f"Price for {ticker}: ${current_price:.2f}")
                    except Exception as e:
                        print(f"Failed to fetch price for {ticker}: {e}")

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
                "est_position_shares": est_shares,
                "sources": list(set(data['sources'])), # unique sources
                "details": data,
                
                # New metrics for Dashboard
                "current_price": data.get("current_price", 0),
                "trend_sentiment": data.get("trend_sentiment", 0), # 0 means no data/neutral
                "bullish_search_vol": data.get("bullish_vol", 0),
                "bearish_search_vol": data.get("bearish_vol", 0)
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

    def _load_config(self):
        if os.path.exists(self.CONFIG_FILE):
             with open(self.CONFIG_FILE, 'r') as f:
                 self.config = json.load(f)
        else:
             print("Warning: config.json not found, using defaults.")
             self.config = {}

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
        web_data = {
            "metadata": {
                "last_scan": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            "signals": data
        }
        with open(web_path, "w") as f:
            json.dump(web_data, f, indent=2)
        print(f"Web Dashboard data saved to {web_path}")

if __name__ == "__main__":
    engine = SocialArbEngine()
    engine.run()
