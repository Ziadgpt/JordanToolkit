import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta

# Download data with error handling
try:
    end_date = datetime.today().strftime('%Y-%m-%d')
    start_date = (datetime.today() - timedelta(days=365)).strftime('%Y-%m-%d')

    df = yf.download('GC=F', start=start_date, end=end_date)
    if df.empty:
        raise ValueError("No data downloaded")
except Exception as e:
    print(f"Error downloading data: {e}")
    exit()


def compute_ema(series, window):
    """Calculate Exponential Moving Average (EMA)"""
    return series.ewm(span=window, adjust=False).mean()


def compute_rsi(series, window=14):
    """Calculate Relative Strength Index (RSI)"""
    delta = series.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=window, min_periods=1).mean()
    avg_loss = loss.rolling(window=window, min_periods=1).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def compute_macd(series, fast=12, slow=26, signal=9):
    """Calculate MACD, Signal Line, and Histogram"""
    fast_ema = compute_ema(series, fast)
    slow_ema = compute_ema(series, slow)
    macd = fast_ema - slow_ema
    signal_line = compute_ema(macd, signal)
    histogram = macd - signal_line
    return macd, signal_line, histogram


def compute_trend_signals(df):
    df = df.copy()

    # Calculate moving averages
    df['SMA21'] = df['Close'].rolling(window=21, min_periods=1).mean()
    df['SMA50'] = df['Close'].rolling(window=50, min_periods=1).mean()

    # Calculate RSI manually
    df['RSI14'] = compute_rsi(df['Close'], 14)

    # Calculate MACD manually
    macd, signal, hist = compute_macd(df['Close'])
    df['MACD'] = macd
    df['MACD_Signal'] = signal
    df['MACD_Hist'] = hist

    # Volume moving average
    df['Vol_MA20'] = df['Volume'].rolling(window=20, min_periods=1).mean()

    # Initialize TrendScore as integer series
    df['TrendScore'] = 0

    # Create temporary columns to avoid alignment issues
    df['SMA21_diff'] = df['SMA21'].diff()
    df['Volume_cond_bull'] = (df['Volume'] > df['Vol_MA20']) & (df['Close'] > df['Open'])
    df['Volume_cond_bear'] = (df['Volume'] > df['Vol_MA20']) & (df['Close'] < df['Open'])
    df['MACD_cond_bull'] = (df['MACD'] > df['MACD_Signal']) & (df['MACD'] > 0)
    df['MACD_cond_bear'] = (df['MACD'] < df['MACD_Signal']) & (df['MACD'] < 0)

    # Bullish conditions using temporary columns
    df.loc[df['SMA21'] > df['SMA50'], 'TrendScore'] += 1
    df.loc[df['Close'] > df['SMA21'], 'TrendScore'] += 1
    df.loc[df['Volume_cond_bull'], 'TrendScore'] += 1
    df.loc[df['MACD_cond_bull'], 'TrendScore'] += 1
    df.loc[df['SMA21_diff'] > 0, 'TrendScore'] += 1
    df.loc[df['RSI14'] > 50, 'TrendScore'] += 1

    # Bearish conditions using temporary columns
    df.loc[df['SMA21'] < df['SMA50'], 'TrendScore'] -= 1
    df.loc[df['Close'] < df['SMA21'], 'TrendScore'] -= 1
    df.loc[df['Volume_cond_bear'], 'TrendScore'] -= 1
    df.loc[df['MACD_cond_bear'], 'TrendScore'] -= 1
    df.loc[df['SMA21_diff'] < 0, 'TrendScore'] -= 1
    df.loc[df['RSI14'] < 45, 'TrendScore'] -= 1

    # Interpretation
    df['Trend'] = 'Sideways'
    df.loc[df['TrendScore'] >= 4, 'Trend'] = 'Uptrend'
    df.loc[df['TrendScore'] <= -4, 'Trend'] = 'Downtrend'

    # Clean up temporary columns
    df.drop(['SMA21_diff', 'Volume_cond_bull', 'Volume_cond_bear',
             'MACD_cond_bull', 'MACD_cond_bear'], axis=1, inplace=True)

    # Fill any potential NaN values
    df.fillna(0, inplace=True)

    return df


df = compute_trend_signals(df)
print(df[['Close', 'TrendScore', 'Trend']].tail(20))

# Create visualization
fig = go.Figure()

# Price and moving averages
fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name='Price', line=dict(color='black', width=2)))
fig.add_trace(go.Scatter(x=df.index, y=df['SMA21'], name='SMA21', line=dict(color='blue', width=1.5)))
fig.add_trace(go.Scatter(x=df.index, y=df['SMA50'], name='SMA50', line=dict(color='orange', width=1.5)))

# Add trend signals as background colors
df['color'] = 'rgba(200, 200, 200, 0.1)'  # Default for sideways
df.loc[df['Trend'] == 'Uptrend', 'color'] = 'rgba(0, 255, 0, 0.2)'
df.loc[df['Trend'] == 'Downtrend', 'color'] = 'rgba(255, 0, 0, 0.2)'

# Add trend background
for i in range(1, len(df)):
    fig.add_vrect(
        x0=df.index[i - 1],
        x1=df.index[i],
        fillcolor=df['color'].iloc[i],
        layer="below",
        line_width=0
    )

# Trend Score
fig.add_trace(go.Scatter(
    x=df.index,
    y=df['TrendScore'],
    name='Trend Score',
    yaxis='y2',
    line=dict(color='green', width=2),
    fill='tozeroy'
))

# Add horizontal reference lines
fig.add_hline(y=4, line_dash="dot", line_color="green", yref="y2")
fig.add_hline(y=-4, line_dash="dot", line_color="red", yref="y2")

fig.update_layout(
    title=f"Gold Futures (GC=F) Trend Analysis - {datetime.today().strftime('%Y-%m-%d')}",
    yaxis=dict(title="Price"),
    yaxis2=dict(
        title="Trend Score",
        overlaying='y',
        side='right',
        range=[-6, 6]  # Fixed range for better visualization
    ),
    height=700,
    hovermode='x unified',
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    plot_bgcolor='white'
)

fig.show()

# Current trend analysis
latest = df.iloc[-1]
trend_strength = abs(latest['TrendScore'])
print("\n" + "=" * 60)
print("GOLD FUTURES (GC=F) - CURRENT TREND ANALYSIS")
print("=" * 60)

if latest['Trend'] == 'Uptrend':
    print(f"\n🔼 STRONG UPTREND CONFIRMED (Score: {trend_strength}/6)")
elif latest['Trend'] == 'Downtrend':
    print(f"\n🔽 STRONG DOWNTREND CONFIRMED (Score: {trend_strength}/6)")
else:
    print(f"\n⏸️ SIDEWAYS MARKET (Score: {latest['TrendScore']}/6)")
    if latest['TrendScore'] > 0:
        print("   Leaning slightly bullish")
    elif latest['TrendScore'] < 0:
        print("   Leaning slightly bearish")
    else:
        print("   Completely neutral")

# Additional technical analysis
print("\nTECHNICAL INDICATORS:")
print(f"- Price: ${latest['Close']:.2f}")
print(f"- SMA21: ${latest['SMA21']:.2f} ({'above' if latest['Close'] > latest['SMA21'] else 'below'} price)")
print(f"- SMA50: ${latest['SMA50']:.2f} ({'above' if latest['Close'] > latest['SMA50'] else 'below'} price)")
print(
    f"- RSI14: {latest['RSI14']:.2f} ({'overbought' if latest['RSI14'] > 70 else 'oversold' if latest['RSI14'] < 30 else 'neutral'})")
print(
    f"- Volume: {latest['Volume'] / 1000000:.2f}M ({'above' if latest['Volume'] > latest['Vol_MA20'] else 'below'} 20-day avg)")
print(f"- MACD: {latest['MACD']:.4f} ({'above' if latest['MACD'] > latest['MACD_Signal'] else 'below'} signal line)")
print("=" * 60)