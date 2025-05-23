import pandas as pd
import numpy as np
from tvdatafeed import TvDatafeed, Interval

def berechne_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def analysiere_technik(df=None):
    if df is None:
        tv = TvDatafeed()
        df = tv.get_hist("ES1!", exchange="CME", interval=Interval.in_15_minute, n_bars=96)
        df = df.reset_index()

    df["SMA_20"] = df["close"].rolling(window=20).mean()
    df["RSI_14"] = berechne_rsi(df["close"], period=14)

    trend = df["SMA_20"].iloc[-1] > df["SMA_20"].iloc[-5]
    rsi = df["RSI_14"].iloc[-1]
    df["date"] = df["datetime"].dt.date
    grouped = df.groupby("date")
    if len(grouped) < 2:
        return "No Trade", df

    heute, gestern = list(grouped)[-1][1], list(grouped)[-2][1]
    open_today = heute.iloc[0]["open"]
    close_yesterday = gestern.iloc[-1]["close"]
    gap = open_today - close_yesterday
    gap_typ = "Gap Up" if gap > 0 else "Gap Down" if gap < 0 else "Kein Gap"

    # Tagesrange
    tagesrange = heute["high"].max() - heute["low"].min()
    range_score = 2 if tagesrange > 35 else 0

    # Scoring
    trend_score = 3 if trend else 0
    rsi_score = 2 if rsi > 70 or rsi < 30 else 0
    gap_score = 1 if ((gap > 0 and rsi < 50) or (gap < 0 and rsi > 50)) else 0

    score = trend_score + rsi_score + gap_score + range_score
    min_score = 4

    if score >= min_score:
        signal = "Long" if gap >= 0 else "Short"
    else:
        signal = "No Trade"

    bewerte = pd.DataFrame({
        "Indikator": ["RSI", "Trend", "Gap", "Range"],
        "Wert": [round(rsi, 2), "Steigend" if trend else "Fallend", f"{gap:.2f} ({gap_typ})", round(tagesrange, 2)],
        "Score": [rsi_score, trend_score, gap_score, range_score]
    })
    bewerte.loc[len(bewerte.index)] = ["Gesamt", "", score]

    return signal, bewerte
