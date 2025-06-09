import json
import pandas as pd
import websockets

async def websocket_candle_feed(url):
    """Yield candle data from a websocket stream.

    The helper understands two JSON formats:

    1. Generic messages with ``timestamp``/``open``/``high``/``low``/``close``/
       ``volume`` fields.
    2. Binance kline messages as produced by futures or spot websocket streams
       (``data`` → ``k``).  Only closed candles (``x`` is ``True``) are yielded.
    """

    async with websockets.connect(url) as ws:
        async for message in ws:
            data = json.loads(message)

            # Binance kline format
            if isinstance(data, dict) and 'data' in data and 'k' in data['data']:
                kline = data['data']['k']
                closed = bool(kline.get('x'))
                timestamp = pd.to_datetime(kline['T'], unit='ms')
                df = pd.DataFrame({
                    'open': [float(kline['o'])],
                    'high': [float(kline['h'])],
                    'low': [float(kline['l'])],
                    'close': [float(kline['c'])],
                    'volume': [float(kline['v'])]
                }, index=[timestamp])
            else:
                closed = True
                timestamp = pd.to_datetime(data['timestamp'])
                df = pd.DataFrame({
                    'open': [data['open']],
                    'high': [data['high']],
                    'low': [data['low']],
                    'close': [data['close']],
                    'volume': [data['volume']]
                }, index=[timestamp])

            yield df, closed
