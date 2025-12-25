import requests
from typing import List, Dict, Any
from datetime import datetime

class WeatherScraper:
    """
    Fetches weather data to detect 'Physical Catalysts'.
    Focus: Hail/Severe Storms -> Roofing Stocks (e.g. OC, BECN).
    Source: Open-Meteo (Free, No API Key).
    """
    
    # Key Markets for Roofing (Hail Belt)
    LOCATIONS = {
        "Dallas_TX": {"lat": 32.7767, "lon": -96.7970},
        "Denver_CO": {"lat": 39.7392, "lon": -104.9903},
        "Minneapolis_MN": {"lat": 44.9778, "lon": -93.2650}
    }
    
    # WMO Weather Codes for Hail
    # 96: Thunderstorm with slight and heavy hail
    # 99: Thunderstorm with slight and heavy hail
    HAIL_CODES = [96, 99]

    def check_hail_events(self) -> List[Dict[str, Any]]:
        """
        Checks for recent or forecast hail in key markets.
        """
        signals = []
        
        for city, coords in self.LOCATIONS.items():
            print(f"Checking weather for {city}...")
            # Fetch forecast for today
            url = f"https://api.open-meteo.com/v1/forecast?latitude={coords['lat']}&longitude={coords['lon']}&daily=weathercode&timezone=auto"
            
            try:
                resp = requests.get(url, timeout=10)
                if resp.status_code != 200:
                    continue
                    
                data = resp.json()
                daily_codes = data.get("daily", {}).get("weathercode", [])
                
                # Check today and tomorrow
                for i, code in enumerate(daily_codes[:2]):
                    if code in self.HAIL_CODES:
                        signals.append({
                            "type": "PhysicalCatalyst",
                            "subtype": "HailStorm",
                            "location": city,
                            "severity": "High",
                            "timestamp": datetime.now().isoformat(),
                            "likely_tickers": ["OC", "BECN", "ROCK"] # Owens Corning, Beacon, Gibraltar
                        })
                        print(f"!!! HAIL DETECTED IN {city} !!!")
                        
            except Exception as e:
                print(f"Weather fetch failed for {city}: {e}")
                
        return signals

if __name__ == "__main__":
    ws = WeatherScraper()
    print(ws.check_hail_events())
