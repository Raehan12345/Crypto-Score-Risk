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

def calculate_atr(high_prices, low_prices, close_prices, window=14):
    # calculate true range components
    tr1 = high_prices - low_prices
    tr2 = (high_prices - close_prices.shift()).abs()
    tr3 = (low_prices - close_prices.shift()).abs()
    
    # combine and calculate rolling mean
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = true_range.rolling(window=window).mean()
    
    # backward fill any nan values using the new pandas syntax
    return atr.bfill()

def calculate_macro_regime(close_prices, window_days=50):
    # 1 day equals 96 periods on a 15m chart
    periods = window_days * 96
    
    # use ema instead of sma for a much faster reaction to market crashes
    ema_fast = close_prices.ewm(span=periods, adjust=False).mean()
    
    # returns 1 for a bull market and 0 for a bear market
    regime = (close_prices > ema_fast).astype(int)
    
    # backward fill the first 50 days so the backtest does not return nan
    return regime.bfill()