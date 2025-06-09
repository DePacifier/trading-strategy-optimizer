import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from datetime import datetime
import pandas as pd

from strategy_manager import StrategyManager
from utils.enums import TradeAction
import asyncio
import json
import websockets
from live_trading.live_trader import LiveTrader
from live_trading.websocket_feed import websocket_candle_feed
from live_trading.trade_recorder import TradeRecorder

class DummyStrategy:
    def __init__(self):
        self.stop_loss_pct = 0.1
        self.take_profit_pct = 0.2

    def generate_signals(self, data):
        signals = pd.Series(TradeAction.EXIT.value, index=data.index)
        if len(signals) > 0:
            signals.iloc[0] = TradeAction.ENTER_LONG.value
        if len(signals) > 1:
            signals.iloc[1] = TradeAction.EXIT.value
        return signals

def make_data():
    index = [datetime(2024,1,1), datetime(2024,1,2)]
    return pd.DataFrame({
        'open':[100,110],
        'high':[105,112],
        'low':[95,108],
        'close':[100,110],
        'volume':[1000,1000]
    }, index=index)


async def data_stream(df):
    for i in range(len(df)):
        yield df.iloc[i:i+1], True
        await asyncio.sleep(0)

def test_live_trader_matches_offline():
    data = make_data()
    offline_sm = StrategyManager(data, initial_capital=100, risk_per_trade=0.1)
    offline_sm.execute_strategy(DummyStrategy())
    expected = [(t.entry_time, t.exit_time, t.profit_loss) for t in offline_sm.trades]

    sm = StrategyManager(pd.DataFrame(columns=data.columns), initial_capital=100, risk_per_trade=0.1)
    trader = LiveTrader(data_stream(data), sm, DummyStrategy(), sleep_time=0)

    asyncio.run(trader.run())
    result = [(t.entry_time, t.exit_time, t.profit_loss) for t in sm.trades]

    assert result == expected


async def websocket_server(data, port):
    async def handler(ws):
        for ts, row in data.iterrows():
            msg = json.dumps({
                'timestamp': ts.isoformat(),
                'open': float(row.open),
                'high': float(row.high),
                'low': float(row.low),
                'close': float(row.close),
                'volume': int(row.volume),
            })
            await ws.send(msg)
        await ws.close()
    return await websockets.serve(handler, 'localhost', port)


def test_websocket_live_trader():
    data = make_data()
    offline_sm = StrategyManager(data, initial_capital=100, risk_per_trade=0.1)
    offline_sm.execute_strategy(DummyStrategy())
    expected = [(t.entry_time, t.exit_time, t.profit_loss) for t in offline_sm.trades]

    async def run_case():
        port = 8765
        server = await websocket_server(data, port)
        feed = websocket_candle_feed(f"ws://localhost:{port}")
        sm = StrategyManager(pd.DataFrame(columns=data.columns), initial_capital=100, risk_per_trade=0.1)
        trader = LiveTrader(feed, sm, DummyStrategy(), sleep_time=0)
        await trader.run()
        server.close()
        await server.wait_closed()
        result = [(t.entry_time, t.exit_time, t.profit_loss) for t in sm.trades]
        return result

    result = asyncio.run(run_case())
    assert result == expected


async def binance_server(data, port):
    async def handler(ws):
        for ts, row in data.iterrows():
            msg = json.dumps({
                "stream": "btcusdt@kline_4h",
                "data": {
                    "e": "kline",
                    "E": 0,
                    "s": "BTCUSDT",
                    "k": {
                        "t": int(ts.timestamp() * 1000),
                        "T": int(ts.timestamp() * 1000),
                        "s": "BTCUSDT",
                        "i": "4h",
                        "f": 0,
                        "L": 0,
                        "o": str(row.open),
                        "c": str(row.close),
                        "h": str(row.high),
                        "l": str(row.low),
                        "v": str(row.volume),
                        "n": 0,
                        "x": True,
                        "q": "0",
                        "V": "0",
                        "Q": "0",
                        "B": "0",
                    },
                },
            })
            await ws.send(msg)
        await ws.close()

    return await websockets.serve(handler, "localhost", port)


def test_websocket_feed_binance_format():
    data = make_data().iloc[:1]

    async def run_case():
        port = 8899
        server = await binance_server(data, port)
        feed = websocket_candle_feed(f"ws://localhost:{port}")
        candle, closed = await anext(feed)
        server.close()
        await server.wait_closed()
        return candle, closed

    candle, closed = asyncio.run(run_case())
    assert closed is True
    pd.testing.assert_frame_equal(candle, data.astype(float))


def test_trade_recorder():
    data = make_data()

    async def run_case():
        sm = StrategyManager(pd.DataFrame(columns=data.columns), initial_capital=100, risk_per_trade=0.1)
        recorder = TradeRecorder(":memory:")
        trader = LiveTrader(data_stream(data), sm, DummyStrategy(), sleep_time=0)
        while await trader.step():
            recorder.sync(sm.trades)
        cur = recorder.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM trades")
        count = cur.fetchone()[0]
        recorder.close()
        return count

    count = asyncio.run(run_case())
    assert count == 1


def test_partial_candle_exit():
    data = make_data()
    first = data.iloc[:1]
    partial = pd.DataFrame({
        'open': [110], 'high': [112], 'low': [89], 'close': [105], 'volume': [1000]
    }, index=[data.index[1]])
    final = data.iloc[1:2]

    async def feed():
        yield first, True
        yield partial, False
        yield final, True

    sm = StrategyManager(pd.DataFrame(columns=data.columns), initial_capital=100, risk_per_trade=0.1)
    trader = LiveTrader(feed(), sm, DummyStrategy(), sleep_time=0)

    async def run_case():
        await trader.step()  # entry candle
        await trader.step()  # partial triggers exit
        return sm.trades[0]

    trade = asyncio.run(run_case())
    assert trade.exit_price == 90
    assert trade.exit_time == data.index[1]

