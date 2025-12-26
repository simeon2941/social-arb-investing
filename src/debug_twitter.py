from src.scrapers.twitter import TwitterScraper

def debug_twitter():
    scraper = TwitterScraper()
    
    # Test with a popular ticker that definitely has tweets
    ticker = "SPY" 
    print(f"Testing Twitter Scraper for ${ticker}...")
    
    tweets = scraper.search_cashtag(ticker)
    
    print(f"Found {len(tweets)} tweets.")
    if tweets:
        print("Sample Tweet:")
        print(tweets[0])
    else:
        print("No tweets found. Checking instance health...")

if __name__ == "__main__":
    debug_twitter()
