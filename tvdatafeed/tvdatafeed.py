# tvdatafeed/tvdatafeed.py
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

class TvDatafeed:
    def __init__(self, username=None, password=None):
        print("📡 Verbunden mit TradingView (Demo-Modus)")

    def get_hist(self, symbol, exchange, interval, n_bars=100):
        daten = []
        now = datetime(2025, 5, 15, 18, 0)
        for i in range(n_bars):
            zeit = now - timedelta(minutes=15 * i)
            close = 5000 + np.random.randn() * 10
            daten.append([zeit, close, close + 5, close - 5, close, 1000])
        df = pd.DataFrame(daten, columns=["datetime", "close", "high", "low", "open", "volume"])
        df.set_index("datetime", inplace=True)
        return df

class Interval:
    in_15_minute = "15min"
