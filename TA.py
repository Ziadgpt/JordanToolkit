import requests
import pandas as pd
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands
from ta.volume import OnBalanceVolumeIndicator
from ta.volatility import AverageTrueRange

API_KEY = "b211d75764f3456488396ae092e1e79a"  # Replace this with your key
def fetch_xauusd_data():
    url = (
        f"https://api.twelvedata.com/time_series?symbol=XAU/USD&interval=30min&outputsize=100&apikey={API_KEY}"
    )
    response = requests.get(url)
    data = response.json()

    if "values" not in data:
        print("Error:", data)
        return None

    df = pd.DataFrame(data["values"])
    df = df.rename(columns={
        "datetime": "time",
        "open": "open",
        "high": "high",
        "low": "low",
        "close": "close",
        "volume": "volume"
    })

    # Convert types explicitly
    df["open"] = df["open"].astype(float)
    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)
    df["close"] = df["close"].astype(float)
    df["volume"] = df["volume"].astype(float)

    df["time"] = pd.to_datetime(df["time"])
    df = df.sort_values(by="time")  # Oldest to newest

    return df
