import json
import os
from datetime import datetime
from src.main_engine import SocialArbEngine

def verify_output():
    engine = SocialArbEngine()
    
    # robustly create dummy data
    dummy_data = [{
        "ticker": "TEST",
        "signal_strength": 10,
        "velocity": 5,
        "avg_sentiment": 0.8,
        "blind_spot": True,
        "analyst_rating": 0.5,
        "est_position_shares": 100,
        "sources": ["https://reddit.com/r/test/comments/123/test_post"],
        "details": {}
    }]
    
    # Save ledger
    print("Saving ledger...")
    engine.save_ledger(dummy_data)
    
    # Check web/data.json
    web_path = os.path.join("web", "data.json")
    if not os.path.exists(web_path):
        print("FAIL: web/data.json not created")
        return
        
    with open(web_path, "r") as f:
        data = json.load(f)
        
    print(f"Loaded {web_path}")
    
    if "metadata" not in data:
        print("FAIL: 'metadata' key missing")
    else:
        print(f"SUCCESS: 'metadata' found. last_scan: {data['metadata'].get('last_scan')}")
        
    if "signals" not in data:
        print("FAIL: 'signals' key missing")
    else:
        print(f"SUCCESS: 'signals' found with {len(data['signals'])} items")
        if data['signals'][0]['sources'][0].startswith("http"):
             print("SUCCESS: Source is a URL")
        else:
             print("FAIL: Source is not a URL")

if __name__ == "__main__":
    verify_output()
