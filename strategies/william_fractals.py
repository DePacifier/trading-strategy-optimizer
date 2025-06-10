import pandas as pd
from .base_strategy import Strategy
from utils.enums import TradeAction

class WilliamsFractals(Strategy):
    def __init__(self, period, fractal_bars, stop_loss_pct, take_profit_pct):
        super().__init__(stop_loss_pct, take_profit_pct)
        self.period = max(2, int(period))
        self.fractal_bars = fractal_bars if fractal_bars in [3, 5] else 3

    def generate_signals(self, data):
        signals = pd.Series(index=data.index, dtype=int)
        signals[:] = TradeAction.EXIT.value
        
        if self.fractal_bars == 5:
            dn_fractal = (
                (data['high'].shift(self.period - 2) < data['high'].shift(self.period)) &
                (data['high'].shift(self.period - 1) < data['high'].shift(self.period)) &
                (data['high'].shift(self.period + 1) < data['high'].shift(self.period)) &
                (data['high'].shift(self.period + 2) < data['high'].shift(self.period))
            )
            up_fractal = (
                (data['low'].shift(self.period - 2) > data['low'].shift(self.period)) &
                (data['low'].shift(self.period - 1) > data['low'].shift(self.period)) &
                (data['low'].shift(self.period + 1) > data['low'].shift(self.period)) &
                (data['low'].shift(self.period + 2) > data['low'].shift(self.period))
            )
        else:  # Default to 3-bar fractal
            dn_fractal = (
                (data['high'].shift(self.period - 1) < data['high'].shift(self.period)) &
                (data['high'].shift(self.period + 1) < data['high'].shift(self.period))
            )
            up_fractal = (
                (data['low'].shift(self.period - 1) > data['low'].shift(self.period)) &
                (data['low'].shift(self.period + 1) > data['low'].shift(self.period))
            )

        position = TradeAction.EXIT.value
        for i in range(len(data)):
            long_entry = bool(up_fractal.iloc[i])
            short_entry = bool(dn_fractal.iloc[i])
            long_exit = position == TradeAction.ENTER_LONG.value and short_entry
            short_exit = position == TradeAction.ENTER_SHORT.value and long_entry

            if position == TradeAction.EXIT.value:
                if long_entry:
                    position = TradeAction.ENTER_LONG.value
                elif short_entry:
                    position = TradeAction.ENTER_SHORT.value
            elif long_exit or short_exit:
                position = TradeAction.EXIT.value

            signals.iloc[i] = position

        return signals