import pandas as pd
from .base_strategy import Strategy
from utils.enums import TradeAction


class PriceBreakoutVolumeStrategy(Strategy):
    """Simple breakout strategy that also requires a volume expansion."""

    def __init__(self, lookback, volume_multiplier, stop_loss_pct, take_profit_pct):
        super().__init__(stop_loss_pct, take_profit_pct)
        self.lookback = max(1, int(lookback))
        self.volume_multiplier = float(volume_multiplier)

    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        signals = pd.Series(index=data.index, dtype=int)
        signals[:] = TradeAction.EXIT.value

        highs = data['high'].shift(1).rolling(self.lookback).max()
        lows = data['low'].shift(1).rolling(self.lookback).min()
        avg_volume = data['volume'].shift(1).rolling(self.lookback).mean()

        position = TradeAction.EXIT.value
        for i in range(len(data)):
            long_entry = (
                data['close'].iloc[i] > highs.iloc[i]
                and data['volume'].iloc[i] > avg_volume.iloc[i] * self.volume_multiplier
            )
            short_entry = (
                data['close'].iloc[i] < lows.iloc[i]
                and data['volume'].iloc[i] > avg_volume.iloc[i] * self.volume_multiplier
            )

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
