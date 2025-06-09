import pandas as pd
from .base_strategy import Strategy
from utils.enums import TradeAction

class ZeroLagMACD_OBV_Strategy(Strategy):
    def __init__(
        self,
        macd_fast_length,
        macd_slow_length,
        macd_signal_length,
        obv_smoothing_length,
        stop_loss_pct,
        take_profit_pct
    ):
        super().__init__(stop_loss_pct, take_profit_pct)
        self.macd_fast_length = max(1, int(macd_fast_length))
        self.macd_slow_length = max(1, int(macd_slow_length))
        self.macd_signal_length = max(1, int(macd_signal_length))
        self.obv_smoothing_length = max(1, int(obv_smoothing_length))

    def zero_lag_ema(self, series, length):
        ema1 = series.ewm(span=length, adjust=False).mean()
        ema2 = ema1.ewm(span=length, adjust=False).mean()
        zlema = 2 * ema1 - ema2
        return zlema

    def generate_signals(self, data):
        signals = pd.Series(index=data.index)
        signals[:] = TradeAction.EXIT.value

        # Zero Lag MACD calculation
        zlema_fast = self.zero_lag_ema(data['close'], self.macd_fast_length)
        zlema_slow = self.zero_lag_ema(data['close'], self.macd_slow_length)
        zero_lag_macd = zlema_fast - zlema_slow

        # Signal line calculation (Zero Lag EMA of the MACD line)
        macd_signal = self.zero_lag_ema(zero_lag_macd, self.macd_signal_length)

        # OBV calculation
        obv = (data['close'].diff().apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0)) * data['volume']).cumsum()
        obv_smooth = obv.rolling(window=self.obv_smoothing_length).mean()

        for i in range(1, len(data)):
            # Long Entry Condition
            if (
                zero_lag_macd.iloc[i] > macd_signal.iloc[i] and
                zero_lag_macd.iloc[i - 1] <= macd_signal.iloc[i - 1] and
                obv_smooth.iloc[i] > obv_smooth.iloc[i - 1]  # OBV is increasing
            ):
                signals.iloc[i] = TradeAction.ENTER_LONG.value
            # # Short Entry Condition
            elif (
                zero_lag_macd.iloc[i] < macd_signal.iloc[i] and
                zero_lag_macd.iloc[i - 1] >= macd_signal.iloc[i - 1] and
                obv_smooth.iloc[i] < obv_smooth.iloc[i - 1]  # OBV is decreasing
            ):
                signals.iloc[i] = TradeAction.ENTER_SHORT.value

        return signals