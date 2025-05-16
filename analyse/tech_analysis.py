import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz

def analysiere_technik():
    # Zeit-Setup
    london = pytz.timezone("Europe/London")
    now = datetime.now(tz=london)
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # Abruf von 1-Tagesdaten im 5-Minuten-Takt
    ticker = yf.Ticker("ES=F")  # S&P 500 Futures
    df = ticker.history(interval="5m", period="1d")

    if df.empty or len(df) < 10:
        return "Nicht genug Daten", df

    df = df.tz_convert("Europe/London")
    df_today = df[df.index >= start_of_day]

    if df_today.empty:
        return "Keine Daten für heute", df_today

    # Trend bestimmen
    open_price = df_today.iloc[0]["Open"]
    last_price = df_today.iloc[-1]["Close"]
    delta = last_price - open_price
    trend = "Bullish" if delta > 5 else "Bearish" if delta < -5 else "Seitwärts"

    # Tagesrange in Ticks (1 Tick = 0.25 Punkte)
    high = df_today["High"].max()
    low = df_today["Low"].min()
    range_ticks = round((high - low) / 0.25)

    # Opening Gap (Vergleich mit Vortagesschluss)
    prev_day = ticker.history(interval="1d", period="2d")
    if len(prev_day) < 2:
        gap_type = "Unbekannt"
    else:
        prev_close = prev_day.iloc[-2]["Close"]
        gap_size = abs(open_price - prev_close)
        gap_type = "Opening Gap" if gap_size > 1 else "Kein Gap"

    # Signal-Logik
    if range_ticks < 100:
        signal = "No Trade (Range < 100 Ticks)"
    elif trend == "Seitwärts":
        signal = "No Trade (Kein klarer Trend)"
    else:
        signal = f"{trend}-Signal"

    # Daten zusammenstellen
    daten = pd.DataFrame({
        "Trend": [trend],
        "Tagesrange (Ticks)": [range_ticks],
        "Gap-Typ": [gap_type],
        "Signal": [signal]
    })

    return signal, daten
