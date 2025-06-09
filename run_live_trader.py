import asyncio
import pandas as pd

from strategies import EMACrossover
from strategy_manager import StrategyManager
from live_trading import LiveTrader, websocket_candle_feed, TradeRecorder


def build_trader(url: str) -> tuple[LiveTrader, TradeRecorder]:
    feed = websocket_candle_feed(url)
    strategy = EMACrossover(short_window=9, long_window=21,
                            stop_loss_pct=0.02, take_profit_pct=0.04)
    manager = StrategyManager(pd.DataFrame(columns=['open', 'high', 'low', 'close', 'volume']),
                              initial_capital=1000, risk_per_trade=0.01)
    trader = LiveTrader(feed, manager, strategy)
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
