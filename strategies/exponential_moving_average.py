import pandas as pd
from .base_strategy import Strategy
from utils.enums import TradeAction

class EMACrossover(Strategy):
    def __init__(self, short_window, long_window, stop_loss_pct, take_profit_pct):
        super().__init__(stop_loss_pct, take_profit_pct)
        self.short_window = max(1, int(short_window))
        self.long_window = max(1, int(long_window))

    def generate_signals(self, data):
        signals = pd.Series(index=data.index)
        signals[:] = TradeAction.EXIT.value

        short_ema = data['close'].ewm(span=self.short_window, adjust=False).mean()
        long_ema = data['close'].ewm(span=self.long_window, adjust=False).mean()

        signals[short_ema > long_ema] = TradeAction.ENTER_LONG.value
        signals[short_ema < long_ema] = TradeAction.ENTER_SHORT.value

        return signals
