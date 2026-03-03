import pandas as pd
import numpy as np

def calculate_ath_score(close_prices):
    rolling_ath = close_prices.expanding().max()
    score = 100 * (1 - (close_prices / rolling_ath))
    return score.fillna(0)

def calculate_trend_score(close_prices):
    ema20 = close_prices.ewm(span=20, adjust=False).mean()
    ema50 = close_prices.ewm(span=50, adjust=False).mean()
    ema200 = close_prices.ewm(span=200, adjust=False).mean()
    
    conditions = [
        (ema20 > ema50) & (ema50 > ema200),
        (ema20 < ema50) & (ema50 < ema200)
    ]
    choices = [20, 80]
    score = np.select(conditions, choices, default=50)
    return pd.Series(score, index=close_prices.index)

def calculate_vol_score(close_prices):
    std = close_prices.rolling(window=30).std()
    rolling_max_std = std.expanding().max()
    score = 100 * (std / rolling_max_std)
    return score.fillna(50)

def calculate_ratio_score(ratio_prices):
    delta = ratio_prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    score = 100 - rsi
    return score.fillna(50)