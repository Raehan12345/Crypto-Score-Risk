import ccxt
import pandas as pd
import os

def fetch_and_prep_data(symbol, timeframe='15m', limit=2000):
    # Initialize exchange purely for public data
    exchange = ccxt.binance({
        'enableRateLimit': True 
    })
    
    print(f"Fetching {limit} candles of {symbol} at {timeframe} timeframe...")
    
    # Binance allows fetching public data without keys
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
    
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    
    return df

def get_project_data():
    os.makedirs('data', exist_ok=True)
    btc_path = 'data/btc_15m.csv'
    eth_path = 'data/eth_15m.csv'

    if os.path.exists(btc_path):
        btc_df = pd.read_csv(btc_path, index_col='timestamp', parse_dates=True)
    else:
        btc_df = fetch_and_prep_data('BTC/USDT')
        btc_df.to_csv(btc_path)

    if os.path.exists(eth_path):
        eth_df = pd.read_csv(eth_path, index_col='timestamp', parse_dates=True)
    else:
        eth_df = fetch_and_prep_data('ETH/USDT')
        eth_df.to_csv(eth_path)

    eth_df, btc_df = eth_df.align(btc_df, join='inner')
    
    combined_df = pd.DataFrame(index=btc_df.index)
    combined_df['close'] = btc_df['close']
    combined_df['eth_close'] = eth_df['close']
    combined_df['eth_btc_ratio'] = eth_df['close'] / btc_df['close']

    return combined_df