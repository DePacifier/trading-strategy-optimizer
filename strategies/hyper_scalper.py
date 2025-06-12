import pandas as pd
from .base_strategy import Strategy
from utils.enums import TradeAction


class HyperScalper(Strategy):
    def __init__(
        self,
        ema_fast,
        ema_mid,
        ema_long,
        adx_window,
        adx_threshold,
        stop_loss_pct,
        take_profit_pct,
    ):
        super().__init__(stop_loss_pct, take_profit_pct)
        self.ema_fast = max(1, int(ema_fast))
        self.ema_mid = max(1, int(ema_mid))
        self.ema_long = max(1, int(ema_long))
        self.adx_window = max(1, int(adx_window))
        self.adx_threshold = float(adx_threshold)

    def calculate_adx(self, data, window):
        high = data["high"]
        low = data["low"]
        close = data["close"]

        plus_dm = high.diff()
        minus_dm = low.diff()

        plus_dm = plus_dm.where((plus_dm > minus_dm) & (plus_dm > 0), 0.0)
        minus_dm = minus_dm.where((minus_dm > plus_dm) & (minus_dm > 0), 0.0)

        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

        atr = true_range.rolling(window=window).mean()
        plus_di = 100 * (plus_dm.ewm(alpha=1 / window, adjust=False).mean() / atr)
        minus_di = 100 * (minus_dm.ewm(alpha=1 / window, adjust=False).mean() / atr)
        dx = (abs(plus_di - minus_di) / (plus_di + minus_di)) * 100
        adx = dx.ewm(alpha=1 / window, adjust=False).mean()
        return adx

    def generate_signals(self, data):
        signals = pd.Series(index=data.index, dtype=int)
        signals[:] = TradeAction.EXIT.value

        ema_fast = data["close"].ewm(span=self.ema_fast, adjust=False).mean()
        ema_mid = data["close"].ewm(span=self.ema_mid, adjust=False).mean()
        ema_long = data["close"].ewm(span=self.ema_long, adjust=False).mean()
        adx = self.calculate_adx(data, self.adx_window)

        position = TradeAction.EXIT.value
        last_dip_below = None
        last_dip_above = None

        if data["close"].iloc[0] < ema_fast.iloc[0]:
            last_dip_below = 0
        if data["close"].iloc[0] > ema_fast.iloc[0]:
            last_dip_above = 0

        for i in range(1, len(data)):
            long_entry = (
                data["close"].iloc[i] > ema_long.iloc[i]
                and ema_fast.iloc[i] > ema_mid.iloc[i] > ema_long.iloc[i]
                and adx.iloc[i] > self.adx_threshold
                and last_dip_below is not None
                and i - last_dip_below <= 5
                and data["close"].iloc[i - 1] <= ema_fast.iloc[i - 1]
                and data["close"].iloc[i] > ema_fast.iloc[i]
            )
            short_entry = (
                data["close"].iloc[i] < ema_long.iloc[i]
                and ema_fast.iloc[i] < ema_mid.iloc[i] < ema_long.iloc[i]
                and adx.iloc[i] > self.adx_threshold
                and last_dip_above is not None
                and i - last_dip_above <= 5
                and data["close"].iloc[i - 1] >= ema_fast.iloc[i - 1]
                and data["close"].iloc[i] < ema_fast.iloc[i]
            )
            long_exit = (
                position == TradeAction.ENTER_LONG.value
                and (
                    data["close"].iloc[i] < ema_fast.iloc[i]
                    or adx.iloc[i] < self.adx_threshold
                )
            )
            short_exit = (
                position == TradeAction.ENTER_SHORT.value
                and (
                    data["close"].iloc[i] > ema_fast.iloc[i]
                    or adx.iloc[i] < self.adx_threshold
                )
            )

            if position == TradeAction.EXIT.value:
                if long_entry:
                    position = TradeAction.ENTER_LONG.value
                elif short_entry:
                    position = TradeAction.ENTER_SHORT.value
            elif long_exit or short_exit:
                position = TradeAction.EXIT.value

            signals.iloc[i] = position

            if data["close"].iloc[i] < ema_fast.iloc[i]:
                last_dip_below = i
            if data["close"].iloc[i] > ema_fast.iloc[i]:
                last_dip_above = i

        return signals
