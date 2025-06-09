import pandas as pd
from .base_strategy import Strategy
from utils.enums import TradeAction

class ADX_VWAP_ZeroLagEMAStrategy(Strategy):
    def __init__(
        self,
        adx_window,
        adx_threshold,
        vwap_window,
        macd_fast_length,
        macd_slow_length,
        macd_signal_length,
        stop_loss_pct,
        take_profit_pct
    ):
        super().__init__(stop_loss_pct, take_profit_pct)
        self.adx_window = max(1, int(adx_window))
        self.adx_threshold = float(adx_threshold)
        self.vwap_window = max(1, int(vwap_window))
        self.macd_fast_length = max(1, int(macd_fast_length))
        self.macd_slow_length = max(1, int(macd_slow_length))
        self.macd_signal_length = max(1, int(macd_signal_length))

    def zero_lag_ema(self, series, length):
        ema1 = series.ewm(span=length, adjust=False).mean()
        ema2 = ema1.ewm(span=length, adjust=False).mean()
        zlema = 2 * ema1 - ema2
        return zlema

    def calculate_adx(self, data, window):
        high = data['high']
        low = data['low']
        close = data['close']

        plus_dm = high.diff()
        minus_dm = low.diff()

        plus_dm = plus_dm.where((plus_dm > minus_dm) & (plus_dm > 0), 0.0)
        minus_dm = minus_dm.where((minus_dm > plus_dm) & (minus_dm > 0), 0.0)

        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

        atr = true_range.rolling(window=window).mean()

        plus_di = 100 * (plus_dm.ewm(alpha=1/window, adjust=False).mean() / atr)
        minus_di = 100 * (minus_dm.ewm(alpha=1/window, adjust=False).mean() / atr)
        dx = (abs(plus_di - minus_di) / (plus_di + minus_di)) * 100

        adx = dx.ewm(alpha=1/window, adjust=False).mean()
        return adx

    def generate_signals(self, data):
        signals = pd.Series(index=data.index)
        signals[:] = TradeAction.EXIT.value

        # VWAP calculation
        typical_price = (data['high'] + data['low'] + data['close']) / 3
        cumulative_tp_vol = (typical_price * data['volume']).cumsum()
        cumulative_vol = data['volume'].cumsum()
        vwap = cumulative_tp_vol / cumulative_vol

        # Zero Lag MACD calculation
        zlema_fast = self.zero_lag_ema(data['close'], self.macd_fast_length)
        zlema_slow = self.zero_lag_ema(data['close'], self.macd_slow_length)
        zero_lag_macd = zlema_fast - zlema_slow
        
        # Signal line calculation (Zero Lag EMA of the MACD line)
        emasig1 = zero_lag_macd.ewm(span=self.macd_signal_length, adjust=False).mean()
        emasig2 = emasig1.ewm(span=self.macd_signal_length, adjust=False).mean()
        signal_line = 2 * emasig1 - emasig2

        # ADX calculation
        adx = self.calculate_adx(data, self.adx_window)

        for i in range(1, len(data)):
            # Check if ADX is above the threshold, indicating a strong trend
            if adx.iloc[i] > self.adx_threshold:
                # Long Entry Condition
                if (
                    data['close'].iloc[i] > vwap.iloc[i] and
                    zero_lag_macd.iloc[i] > signal_line.iloc[i] and
                    zero_lag_macd.iloc[i - 1] <= signal_line.iloc[i - 1]
                ):
                    signals.iloc[i] = TradeAction.ENTER_LONG.value
                # Short Entry Condition
                elif (
                    data['close'].iloc[i] < vwap.iloc[i] and
                    zero_lag_macd.iloc[i] < signal_line.iloc[i] and
                    zero_lag_macd.iloc[i - 1] >= signal_line.iloc[i - 1]
                ):
                    signals.iloc[i] = TradeAction.ENTER_SHORT.value

        return signals