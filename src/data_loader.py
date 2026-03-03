import ccxt
import pandas as pd
import os
import time

def fetch_historical_data_paginated(symbol, timeframe='15m', start_str='2020-01-01T00:00:00Z', end_str='2026-01-01T00:00:00Z'):
    # initialize the exchange with rate limiting enabled
    exchange = ccxt.binance({'enableRateLimit': True})

    # convert string dates to milliseconds for the binance api
    since = exchange.parse8601(start_str)
    end_time = exchange.parse8601(end_str)

    all_ohlcv = []
    limit = 1000

    print(f"fetching paginated data for {symbol} from 2020 to 2026...")

    while since < end_time:
        try:
            # fetch a chunk of 1000 candles
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since=since, limit=limit)

            # break the loop if no more data is returned
            if not ohlcv:
                break

            # append the new chunk to our master list
            all_ohlcv.extend(ohlcv)

            # update the since variable to the last candle timestamp plus one millisecond
            since = ohlcv[-1][0] + 1

            # print progress to the console so you know it is working
            if len(all_ohlcv) % 10000 == 0:
                print(f"downloaded {len(all_ohlcv)} candles for {symbol}...")

            # pause briefly to respect public rate limits and avoid ip bans
            time.sleep(0.5)

        except Exception as e:
            print(f"network error encountered: {e}")
            # wait 5 seconds before retrying if we hit a rate limit
            time.sleep(5)

    # convert the massive list into a pandas dataframe
    df = pd.DataFrame(all_ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)

    # strip the timezone awareness from the end string so it matches our naive index
    end_timestamp = pd.to_datetime(end_str).tz_localize(None)
    
    # slice off any trailing data that goes past our exact end date
    df = df[df.index <= end_timestamp]

    return df

def get_project_data():
    os.makedirs('data', exist_ok=True)
    
    # updated file names for the multi year dataset
    btc_path = 'data/btc_15m_full.csv'
    eth_path = 'data/eth_15m_full.csv'

    # define the massive multi year range
    start_date = '2020-01-01T00:00:00Z'
    end_date = '2026-01-01T00:00:00Z'

    # load or fetch btc data
    if os.path.exists(btc_path):
        print("loading full btc history from local cache...")
        btc_df = pd.read_csv(btc_path, index_col='timestamp', parse_dates=True)
    else:
        btc_df = fetch_historical_data_paginated('BTC/USDT', '15m', start_date, end_date)
        btc_df.to_csv(btc_path)

    # load or fetch eth data
    if os.path.exists(eth_path):
        print("loading full eth history from local cache...")
        eth_df = pd.read_csv(eth_path, index_col='timestamp', parse_dates=True)
    else:
        eth_df = fetch_historical_data_paginated('ETH/USDT', '15m', start_date, end_date)
        eth_df.to_csv(eth_path)

    # align data indexes to prevent mismatch errors
    eth_df, btc_df = eth_df.align(btc_df, join='inner')
    
    # map required columns into the final combined dataframe
    combined_df = pd.DataFrame(index=btc_df.index)
    combined_df['close'] = btc_df['close']
    combined_df['high'] = btc_df['high']
    combined_df['low'] = btc_df['low']
    
    # eth specific mappings
    combined_df['eth_close'] = eth_df['close']
    combined_df['eth_btc_ratio'] = eth_df['close'] / btc_df['close']

    return combined_df