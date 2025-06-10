import pandas as pd
import ta
from .base_strategy import Strategy
from utils.enums import TradeAction

class BollingerBandsStrategy(Strategy):
    def __init__(self, window, num_std):
        self.window = int(window)
        self.num_std = num_std

    def generate_signals(self, data):
        signals = pd.Series(index=data.index, dtype=int)
        signals[:] = TradeAction.EXIT.value

        bollinger = ta.volatility.BollingerBands(
            data['close'], window=self.window, window_dev=self.num_std
        )

        position = TradeAction.EXIT.value
        mid_band = bollinger.bollinger_mavg()
        lower_band = bollinger.bollinger_lband()
        upper_band = bollinger.bollinger_hband()

        for i in range(1, len(data)):
            long_entry = data['close'].iloc[i] < lower_band.iloc[i]
            short_entry = data['close'].iloc[i] > upper_band.iloc[i]
            long_exit = (
                position == TradeAction.ENTER_LONG.value
                and data['close'].iloc[i] > mid_band.iloc[i]
            )
            short_exit = (
                position == TradeAction.ENTER_SHORT.value
                and data['close'].iloc[i] < mid_band.iloc[i]
            )

            if position == TradeAction.EXIT.value:
                if long_entry:
                    position = TradeAction.ENTER_LONG.value
                elif short_entry:
                    position = TradeAction.ENTER_SHORT.value
            elif long_exit or short_exit:
                position = TradeAction.EXIT.value

            signals.iloc[i] = position

        return signals