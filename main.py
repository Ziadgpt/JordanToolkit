import tkinter as tk
from tkinter import scrolledtext
import requests
import pandas as pd
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands, AverageTrueRange
from ta.volume import OnBalanceVolumeIndicator

API_KEY = "b211d75764f3456488396ae092e1e79a"  # Replace with your actual key

def fetch_xauusd_data():
    url = f"https://api.twelvedata.com/time_series?symbol=XAU/USD&interval=30min&outputsize=100&apikey={API_KEY}"
    response = requests.get(url)
    data = response.json()
    if "values" not in data:
        return None, f"API Error: {data}"

    df = pd.DataFrame(data["values"])
    df = df.rename(columns={
        "datetime": "time",
        "open": "open",
        "high": "high",
        "low": "low",
        "close": "close"
    })

    # Convert columns to float
    for col in ["open", "high", "low", "close"]:
        df[col] = df[col].astype(float)

    # Volume may be missing, fill with zeros
    if "volume" in df.columns:
        df["volume"] = df["volume"].astype(float)
    else:
        df["volume"] = 0.0

    df["time"] = pd.to_datetime(df["time"])
    df = df.sort_values(by="time")
    return df, None

def compute_indicators(df):
    df['rsi_14'] = RSIIndicator(close=df['close'], window=14).rsi()
    bb = BollingerBands(close=df['close'], window=21, window_dev=2)
    df['bb_upper'] = bb.bollinger_hband()
    df['bb_lower'] = bb.bollinger_lband()
    df['bb_middle'] = bb.bollinger_mavg()
    df['obv'] = OnBalanceVolumeIndicator(close=df['close'], volume=df['volume']).on_balance_volume()
    df['atr'] = AverageTrueRange(high=df['high'], low=df['low'], close=df['close'], window=14).average_true_range()
    return df

def update_gui():
    output_text.delete(1.0, tk.END)

    df, error = fetch_xauusd_data()
    if error:
        output_text.insert(tk.END, f"❌ Error fetching price data:\n{error}")
        return

    df = compute_indicators(df)
    latest = df.iloc[-1]

    output_text.insert(tk.END, "📊 Technical Snapshot (XAU/USD - 30m):\n" + "="*40 + "\n")
    output_text.insert(tk.END, f"Time: {latest['time']}\n")
    output_text.insert(tk.END, f"Price: {latest['close']:.2f}\n")
    output_text.insert(tk.END, f"RSI (14): {latest['rsi_14']:.2f}\n")
    output_text.insert(tk.END, f"Bollinger Bands: {latest['bb_lower']:.2f} ⬅️ {latest['close']:.2f} ➡️ {latest['bb_upper']:.2f}\n")
    output_text.insert(tk.END, f"OBV: {latest['obv']:.2f}\n")
    output_text.insert(tk.END, f"ATR: {latest['atr']:.2f}\n")

# GUI Setup
window = tk.Tk()
window.title("Gold Technicals Terminal")
window.geometry("700x500")

title_label = tk.Label(window, text="📈 Gold Technicals Terminal", font=("Arial", 16, "bold"))
title_label.pack(pady=10)

refresh_button = tk.Button(window, text="Refresh Data", command=update_gui)
refresh_button.pack(pady=5)

output_text = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=80, height=25, font=("Courier", 10))
output_text.pack(padx=10, pady=10)

update_gui()  # Initial load
window.mainloop()
