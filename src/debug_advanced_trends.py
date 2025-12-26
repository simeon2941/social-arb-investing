import sys
import os
import time

# Ensure src is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.scrapers.trends import AdvancedTrendsScraper

def debug_advanced_trends():
    print("Initializing Advanced Trends Scraper...")
    scraper = AdvancedTrendsScraper()
    
    if not scraper.pytrends:
        print("Failed to init pytrends.")
        return

    # 1. Hype vs Value / Volatility Test
    # Check interest for a hot stock
    symbol = "NVDA"
    print(f"\n--- Test 1: Interest Over Time for {symbol} ---")
    df = scraper.get_interest_over_time([symbol, f"{symbol} stock"], timeframe='today 1-m')
    if isinstance(df, dict) and not df:
         print("No data returned.")
    else:
        print("Data fetched successfully:")
        print(df.tail())
        
    # Sleep to respect rate limits slightly
    time.sleep(2)

    # 2. Bullish vs Bearish Sentiment
    print(f"\n--- Test 2: Sentiment Index for {symbol} ---")
    sentiment = scraper.get_sentiment_index(symbol)
    if sentiment:
        print(f"Bullish Vol: {sentiment['total_bullish_volume']}")
        print(f"Bearish Vol: {sentiment['total_bearish_volume']}")
        print(f"Ratio: {sentiment['sentiment_ratio']:.2f}")
    else:
        print("Could not calculate sentiment.")

    # 3. Related Queries (Identifying early interest)
    # Let's try a sector term
    sector_term = "artificial intelligence"
    print(f"\n--- Test 3: Related Queries for '{sector_term}' ---")
    related = scraper.get_related_queries(sector_term)
    if related:
        if 'top' in related and related['top'] is not None:
            print("Top Related:")
            print(related['top'].head())
        if 'rising' in related and related['rising'] is not None:
            print("\nRising Related (Breakout terms):")
            print(related['rising'].head())
    else:
        print("No related queries found.")

if __name__ == "__main__":
    debug_advanced_trends()
