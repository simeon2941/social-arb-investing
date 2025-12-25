from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from typing import Dict, Any

class SentimentEngine:
    """
    Wrapper for VADER Sentiment Analysis.
    Optimized for social media text (emojis, slang).
    """
    
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()

    def analyze(self, text: str) -> Dict[str, float]:
        """
        Returns the polarity scores: neg, neu, pos, compound.
        Compound score is the normalized metric (-1 to 1).
        """
        if not text:
            return {"compound": 0.0, "pos": 0.0, "neu": 0.0, "neg": 0.0}
            
        scores = self.analyzer.polarity_scores(text)
        return scores

    def analyze_batch(self, texts: list) -> float:
        """
        Returns average compound score for a list of texts.
        """
        if not texts:
            return 0.0
            
        total_compound = 0.0
        for text in texts:
            scores = self.analyze(text)
            total_compound += scores['compound']
            
        return total_compound / len(texts)

if __name__ == "__main__":
    engine = SentimentEngine()
    print(engine.analyze("I love this stock! 🚀"))
    print(engine.analyze("This company is garbage."))
