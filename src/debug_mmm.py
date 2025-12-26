import sys
import os
from src.scrapers.trends import AdvancedTrendsScraper

def debug_mmm():
    scraper = AdvancedTrendsScraper()
    symbol = "MMM"
    
    print(f"--- Debugging {symbol} ---")
    
    # 1. Get raw sentiment index
    sentiment = scraper.get_sentiment_index(symbol)
    if sentiment:
        print(f"Ratio: {sentiment['sentiment_ratio']}")
        print(f"Bullish Vol (Sum): {sentiment['total_bullish_volume']}")
        print(f"Bearish Vol (Sum): {sentiment['total_bearish_volume']}")
        
        # 2. Inspect the dataframe to see daily values
        df = sentiment['data']
        print("\n--- Raw Data Head ---")
        print(df.head())
        print("\n--- Raw Data Tail ---")
        print(df.tail())
        
        # 3. Check for Zeroes
        bullish_zeros = (df[f"buy {symbol}"] == 0).sum()
        bearish_zeros = (df[f"sell {symbol}"] == 0).sum()
        print(f"\nDays with 0 Bullish Search: {bullish_zeros}")
        print(f"Days with 0 Bearish Search: {bearish_zeros}")

if __name__ == "__main__":
    debug_mmm()
