import pandas as pd
import ta
from .base_strategy import Strategy
from utils.enums import TradeAction

class RSIStrategy(Strategy):
    def __init__(self, rsi_period, oversold, overbought):
        self.rsi_period = int(rsi_period)
        self.oversold = oversold
        self.overbought = overbought

    def generate_signals(self, data):
        signals = pd.Series(index=data.index)
        signals[:] = TradeAction.EXIT.value

        rsi = ta.momentum.RSIIndicator(data['close'], window=self.rsi_period).rsi()
        
        signals[rsi < self.oversold] = TradeAction.ENTER_LONG.value
        signals[rsi > self.overbought] = TradeAction.ENTER_SHORT.value

        return signals