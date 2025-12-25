import yfinance as yf
import numpy as np

class RiskManager:
    """
    Calculates position sizing based on Volatility Targeting.
    """
    
    def __init__(self, risk_bucket_size: float = 10000.0, target_risk_per_trade: float = 0.02):
        self.risk_bucket = risk_bucket_size
        self.target_risk = target_risk_per_trade # 2% of equity at risk

    def get_volatility(self, ticker: str, period: str = "1mo") -> float:
        """
        Fetches historical volatility (std dev of returns).
        """
        try:
            print(f"Fetching volatility for {ticker}...")
            # We use yfinance to get history
            # Ticker object might be slow, optimize if needed
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)
            
            if hist.empty:
                return 0.05 # Default assume 5% vol if no data
                
            # Calculate daily returns
            hist['pct_change'] = hist['Close'].pct_change()
            vol = hist['pct_change'].std() * np.sqrt(252) # Annualized Volatility
            
            # Use specific period volatility (e.g. 30 day) not annualized if intended timeframe is short?
            # Prompt says: "Ticker_Volatility (30-day Std Dev)" 
            # We will use the raw std dev across the period for sizing or annualized?
            # "Ticker_Volatility (30-day Std Dev) = 4%." -> suggesting period specific.
            # Let's return the std dev of the daily returns over the last month.
            
            period_vol = hist['pct_change'].std()
            if np.isnan(period_vol):
                return 0.05
                
            return period_vol
            
        except Exception as e:
            print(f"Error fetching volatility for {ticker}: {e}")
            return 0.05 # Default fallback

    def calculate_position_size(self, ticker: str, price: float, velocity: int = 0) -> int:
        """
        Returns number of shares to buy.
        Formula: Position_Size ($) = Risk_Bucket * (Target_Risk / Ticker_Volatility)
        
        Smart Sizing:
        - If Velocity > 0 (Accelerating Trend), increase Target Risk by 50%.
        - If Velocity < 0 (Decelerating), reduce Target Risk by 50%.
        """
        vol = self.get_volatility(ticker)
        if vol == 0: 
            vol = 0.01 
            
        # Adjust risk based on velocity
        adjusted_risk = self.target_risk
        if velocity > 0:
            adjusted_risk *= 1.5
        elif velocity < 0:
            adjusted_risk *= 0.5
            
        position_value = self.risk_bucket * (adjusted_risk / vol)
        
        # Cap position size at 10% of bucket (or 15% if high velocity high conviction)
        max_cap = 0.10
        if velocity > 2:
            max_cap = 0.15
            
        max_position = self.risk_bucket * max_cap
        if position_value > max_position:
            position_value = max_position
            
        shares = int(position_value / price)
        return shares

if __name__ == "__main__":
    rm = RiskManager()
    # Mock price for calculation
    shares = rm.calculate_position_size("AAPL", 150.0)
    print(f"Recommended Position Size for AAPL: {shares} shares")
