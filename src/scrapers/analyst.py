import yfinance as yf
from typing import Dict, Any, Optional

class AnalystVerifier:
    """
    Checks Wall Street Consensus via Yahoo Finance.
    Goal: Identify 'Contrarian' opportunities or confirm 'blind spots'.
    
    Logic:
    - If Social Sentiment is High AND Analyst Rating is 'Sell'/'Hold' -> High Asymmetry (Analysts are wrong/slow).
    - If Social Sentiment is High AND Analyst Rating is 'Strong Buy' -> Parity (Analysts know).
    """

    def get_consensus(self, ticker: str) -> Dict[str, Any]:
        """
        Fetches recommendations.
        Returns: {
            "recommendationMean": float (1.0 = Strong Buy, 5.0 = Sell),
            "numberOfAnalystOpinions": int,
            "targetMean": float
        }
        """
        print(f"Checking Analyst Consensus for {ticker}...")
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # yfinance info keys usually: 'recommendationMean', 'numberOfAnalystOpinions', 'targetMeanPrice'
            rec_mean = info.get('recommendationMean')
            num_opinions = info.get('numberOfAnalystOpinions', 0)
            target_price = info.get('targetMeanPrice')
            
            return {
                "rating_score": rec_mean, # 1=Buy, 5=Sell
                "analyst_count": num_opinions,
                "target_price": target_price
            }
        except Exception as e:
            print(f"Failed to fetch analyst data for {ticker}: {e}")
            return {}

    def analyze_asymmetry(self, ticker: str, social_sentiment: float) -> str:
        """
        Returns a classification: 'Contrarian Opportunity', 'Consensus Follow', 'Warning', or 'Unknown'.
        """
        data = self.get_consensus(ticker)
        score = data.get("rating_score")
        
        if score is None:
            return "Unknown"
            
        # social_sentiment is -1 to 1 (VADER)
        # score is 1 (Buy) to 5 (Sell)
        
        # Case 1: High Social Positive, Analysts Negative (>3)
        if social_sentiment > 0.3 and score > 2.5:
            return "CONTRARIAN BULL (Analysts Late)"
            
        # Case 2: High Social Positive, Analysts Positive (<2)
        if social_sentiment > 0.3 and score < 2.0:
            return "CONSENSUS BULL (Priced In?)"
            
        # Case 3: Social Negative, Analysts Positive
        if social_sentiment < -0.3 and score < 2.0:
            return "CONTRARIAN BEAR (Analysts Wrong)"
            
        return "Neutral"

if __name__ == "__main__":
    verifier = AnalystVerifier()
    print(verifier.get_consensus("TSLA"))
    print(verifier.analyze_asymmetry("TSLA", 0.8)) # Assume high social sentiment
