import asyncio
import pandas as pd


class LiveTrader:
    """Simple live trading engine using incremental candles.

    The trader expects ``data_feed`` to be an **asynchronous** iterator
    yielding single-row ``pandas.DataFrame`` objects.  This allows it to be
    connected directly to a websocket feed.
    """

    def __init__(self, data_feed, strategy_manager, strategy, sleep_time=1.0):
        """Initialize the trader.

        Parameters
        ----------
        data_feed : async iterator
            Asynchronous iterator yielding ``pandas.DataFrame`` objects containing
            a single OHLCV row indexed by timestamp.  A convenient way to obtain
            such iterator is ``websocket_candle_feed`` from ``websocket_feed``.
        strategy_manager : StrategyManager
            Manager used to process trades.
        strategy : Strategy
            Strategy instance used to generate signals.
        sleep_time : float
            Seconds to wait between processing new candles when ``run`` is used.
        """
        self.data_feed = data_feed
        self.strategy_manager = strategy_manager
        self.strategy = strategy
        self.sleep_time = sleep_time
        self.data = pd.DataFrame(columns=['open', 'high', 'low', 'close', 'volume'])

    async def step(self):
        """Process the next candle from the feed.  Returns ``False`` when the
        feed is exhausted."""
        try:
            new_candle = await anext(self.data_feed)
        except StopAsyncIteration:
            return False

        self.data = pd.concat([self.data, new_candle])
        signals = self.strategy.generate_signals(self.data)
        new_signals = signals.loc[new_candle.index]
        self.strategy_manager.data = self.data
        self.strategy_manager.execute_signals(new_signals, self.strategy)
        return True

    async def run(self):
        """Continuously process candles until the feed is exhausted."""
        while await self.step():
            await asyncio.sleep(self.sleep_time)
