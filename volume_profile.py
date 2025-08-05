import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go


def get_data(ticker="GC=F", period="7d", interval="15m"):
    df = yf.download(ticker, period=period, interval=interval)
    if df.empty:
        print(f"[!] No data found for {ticker}.")
        return None
    return df.dropna()


def volume_profile(df, price_bin=2):
    df = df.copy()
    df['PriceBin'] = np.floor(df['Close'] / price_bin) * price_bin
    vp = df.groupby('PriceBin')['Volume'].sum().reset_index()
    vp = vp.sort_values('PriceBin')
    vp['VolNorm'] = vp['Volume'] / vp['Volume'].max()
    return vp


def plot_volume_profile_candles(df_15m, df_1d, vp_15m, vp_1d, price_bin=2):
    candle15 = go.Candlestick(
        x=df_15m.index,
        open=df_15m['Open'],
        high=df_15m['High'],
        low=df_15m['Low'],
        close=df_15m['Close'],
        name="15m Candles",
        increasing_line_color='green',
        decreasing_line_color='red',
        yaxis='y1'
    )

    candle1d = go.Candlestick(
        x=df_1d.index,
        open=df_1d['Open'],
        high=df_1d['High'],
        low=df_1d['Low'],
        close=df_1d['Close'],
        name="1D Candles",
        increasing_line_color='lightgreen',
        decreasing_line_color='lightcoral',
        yaxis='y1',
        opacity=0.3
    )

    vp15_bars = go.Bar(
        y=vp_15m['PriceBin'],
        x=vp_15m['VolNorm'],
        orientation='h',
        marker_color='blue',
        name='Volume Profile 15m',
        yaxis='y2',
        customdata=vp_15m['Volume'],
        hovertemplate='Price: %{y}<br>Vol: %{customdata}'
    )

    vp1d_bars = go.Bar(
        y=vp_1d['PriceBin'],
        x=vp_1d['VolNorm'],
        orientation='h',
        marker_color='orange',
        name='Volume Profile 1D',
        yaxis='y2',
        customdata=vp_1d['Volume'],
        hovertemplate='Price: %{y}<br>Vol: %{customdata}'
    )

    min_price = np.nanmin([df_15m['Low'].min(), df_1d['Low'].min()])
    max_price = np.nanmax([df_15m['High'].max(), df_1d['High'].max()])

    key_levels_25 = np.arange(np.floor(min_price / 25) * 25, np.ceil(max_price / 25) * 25 + 25, 25)
    key_levels_50 = np.arange(np.floor(min_price / 50) * 50, np.ceil(max_price / 50) * 50 + 50, 50)

    shapes = []
    for lvl in key_levels_25:
        shapes.append(dict(
            type="line",
            y0=lvl, y1=lvl,
            x0=0, x1=1,
            xref='paper', yref='y1',
            line=dict(color="blue", width=1, dash="dot"),
            opacity=0.3
        ))
    for lvl in key_levels_50:
        shapes.append(dict(
            type="line",
            y0=lvl, y1=lvl,
            x0=0, x1=1,
            xref='paper', yref='y1',
            line=dict(color="red", width=1.5, dash="dash"),
            opacity=0.5
        ))

    fig = go.Figure(data=[candle15, candle1d, vp15_bars, vp1d_bars])
    fig.update_layout(
        title="GC=F Volume Profile Map (15m & 1D)",
        yaxis=dict(domain=[0, 1], autorange='reversed', title="Price"),
        yaxis2=dict(domain=[0, 1], anchor='x2', autorange='reversed', overlaying='y1', side='right',
                    showticklabels=False),
        xaxis=dict(domain=[0, 0.85], title="Time"),
        xaxis2=dict(domain=[0.85, 1], showgrid=False, zeroline=False, showticklabels=False),
        barmode='overlay',
        shapes=shapes,
        legend=dict(y=0.99, x=0.01),
        height=700,
        hovermode="y unified",
    )

    fig.update_traces(yaxis='y2', selector=dict(type='bar'))
    fig.show()


# === MAIN ===
if __name__ == "__main__":
    df_15m = get_data("GC=F", period="7d", interval="15m")
    df_1d = get_data("GC=F", period="7d", interval="1d")

    if df_15m is None or df_1d is None:
        print("[x] Data unavailable. Exiting...")
    else:
        vp_15m = volume_profile(df_15m, price_bin=2)
        vp_1d = volume_profile(df_1d, price_bin=2)

        plot_volume_profile_candles(df_15m, df_1d, vp_15m, vp_1d, price_bin=2)
