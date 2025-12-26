from src.scrapers.reddit import RedditScraper
import json

def debug_reddit():
    scraper = RedditScraper()
    print("--- Testing Enhanced Reddit Scraper ---")
    
    subs = ["stocks", "pennystocks", "thetagang"] # Test a subset to be fast
    print(f"Fetching from: {subs}")
    
    posts = scraper.fetch_feed(subreddits=subs, limit=10)
    
    print(f"\nTotal Posts Fetched: {len(posts)}")
    
    # Analyze diversity
    sub_counts = {}
    for p in posts:
        s = p.get('subreddit')
        sub_counts[s] = sub_counts.get(s, 0) + 1
        
    print("\nPosts per Subreddit:")
    for s, c in sub_counts.items():
        print(f"  r/{s}: {c}")
        
    # Show sample
    if posts:
        print("\n--- Sample Post ---")
        print(json.dumps(posts[0], indent=2))
    else:
        print("\nNO POSTS FOUND! Check connection or rate limits.")

if __name__ == "__main__":
    debug_reddit()
