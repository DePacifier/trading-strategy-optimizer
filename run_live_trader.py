import asyncio
import pandas as pd

from strategies import EMACrossover
from strategy_manager import StrategyManager
from live_trading import LiveTrader, websocket_candle_feed, prepend_historical_data, TradeRecorder
from data import DataLoader
from config import BINANCE_API_KEY, BINANCE_API_SECRET
from binance.client import Client


def build_trader(url: str, history_limit: int = 50) -> tuple[LiveTrader, TradeRecorder]:
    loader = DataLoader(BINANCE_API_KEY, BINANCE_API_SECRET)
    historical = loader.fetch_recent_data("BTCUSDT", Client.KLINE_INTERVAL_4HOUR, history_limit)
    feed = prepend_historical_data(historical, websocket_candle_feed(url))
    strategy = EMACrossover(short_window=3, long_window=21,
                            stop_loss_pct=6, take_profit_pct=3)
    manager = StrategyManager(historical.copy(), initial_capital=1000, risk_per_trade=0.01)
    trader = LiveTrader(feed, manager, strategy, initial_data=historical)
    recorder = TradeRecorder("trades.db")
    return trader, recorder


async def main() -> None:
    url = "wss://fstream.binance.com/stream?streams=btcusdt@kline_4h"
    trader, recorder = build_trader(url)
    try:
        while await trader.step():
            recorder.sync(trader.strategy_manager.trades)
            await asyncio.sleep(trader.sleep_time)
    finally:
        recorder.close()


if __name__ == "__main__":
    asyncio.run(main())
