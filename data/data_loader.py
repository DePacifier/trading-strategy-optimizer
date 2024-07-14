from binance.client import Client
import pandas as pd

class DataLoader:
    def __init__(self, api_key, api_secret):
        self.client = Client(api_key, api_secret)

    def fetch_historical_data(self, symbol, interval, start_time, end_time):
        klines = self.client.get_historical_klines(symbol, interval, start_time, end_time)
        df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        return df[['open', 'high', 'low', 'close', 'volume']].astype("float")