from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable, Static
from textual.containers import Container
import json
import os

class SocialArbTUI(App):
    """
    The 'Hacker' Terminal Interface.
    """
    CSS = """
    Screen {
        layout: vertical;
    }
    DataTable {
        height: 100%;
        border: solid green;
    }
    """
    
    BINDINGS = [("q", "quit", "Quit"), ("r", "refresh_data", "Refresh")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield DataTable()
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("Ticker", "Signal Strength", "Sentiment", "Blind Spot?", "Position (Est Shares)", "Sources")
        self.load_data()

    def load_data(self):
        table = self.query_one(DataTable)
        table.clear()
        
        data_path = os.path.join("data", "current_signals.json")
        if not os.path.exists(data_path):
            return

        try:
            with open(data_path, "r") as f:
                data = json.load(f)
                
            for item in data:
                ticker = item.get("ticker")
                strength = str(item.get("signal_strength"))
                sentiment = f"{item.get('avg_sentiment'):.2f}"
                blind_spot = "✅ YES" if item.get("blind_spot") else "❌ NO"
                shares = str(item.get("est_position_shares", 0))
                sources = ", ".join(item.get("sources", []))
                
                table.add_row(ticker, strength, sentiment, blind_spot, shares, sources)
                
        except Exception as e:
            pass

    def action_refresh_data(self) -> None:
        self.load_data()

if __name__ == "__main__":
    app = SocialArbTUI()
    app.run()
