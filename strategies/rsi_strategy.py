import pandas as pd
import ta
from .base_strategy import Strategy
from utils.enums import TradeAction

class RSIStrategy(Strategy):
    def __init__(self, rsi_period, oversold, overbought,
                 stop_loss_pct=0, take_profit_pct=0):
        super().__init__(stop_loss_pct, take_profit_pct)
        self.rsi_period = int(rsi_period)
        self.oversold = oversold
        self.overbought = overbought

    def generate_signals(self, data):
        signals = pd.Series(index=data.index, dtype=int)
        signals[:] = TradeAction.EXIT.value

        rsi = ta.momentum.RSIIndicator(data['close'], window=self.rsi_period).rsi()

        position = TradeAction.EXIT.value
        for i in range(1, len(data)):
            long_entry = rsi.iloc[i] < self.oversold
            short_entry = rsi.iloc[i] > self.overbought
            long_exit = position == TradeAction.ENTER_LONG.value and rsi.iloc[i] > self.overbought
            short_exit = position == TradeAction.ENTER_SHORT.value and rsi.iloc[i] < self.oversold

            if position == TradeAction.EXIT.value:
                if long_entry:
                    position = TradeAction.ENTER_LONG.value
                elif short_entry:
                    position = TradeAction.ENTER_SHORT.value
            elif long_exit or short_exit:
                position = TradeAction.EXIT.value

            signals.iloc[i] = position

        return signals
