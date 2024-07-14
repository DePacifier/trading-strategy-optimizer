import pandas as pd
import ta
from .base_strategy import Strategy
from utils.enums import TradeAction

class BollingerBandsStrategy(Strategy):
    def __init__(self, window, num_std):
        self.window = int(window)
        self.num_std = num_std

    def generate_signals(self, data):
        signals = pd.Series(index=data.index)
        signals[:] = TradeAction.EXIT.value

        bollinger = ta.volatility.BollingerBands(data['close'], window=self.window, window_dev=self.num_std)
        
        signals[data['close'] < bollinger.lower_band] = TradeAction.ENTER_LONG.value
        signals[data['close'] > bollinger.upper_band] = TradeAction.ENTER_SHORT.value

        return signals