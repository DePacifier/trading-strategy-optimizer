import pandas as pd
from .base_strategy import Strategy
from utils.enums import TradeAction

class VWAP_RSI_ZeroLagMACDStrategy(Strategy):
    def __init__(
        self,
        vwap_window,
        rsi_window,
        rsi_overbought,
        rsi_oversold,
        macd_fast_length,
        macd_slow_length,
        macd_signal_length,
        stop_loss_pct,
        take_profit_pct
    ):
        super().__init__(stop_loss_pct, take_profit_pct)
        self.vwap_window = max(1, int(vwap_window))
        self.rsi_window = max(1, int(rsi_window))
        self.rsi_overbought = float(rsi_overbought)
        self.rsi_oversold = float(rsi_oversold)
        self.macd_fast_length = max(1, int(macd_fast_length))
        self.macd_slow_length = max(1, int(macd_slow_length))
        self.macd_signal_length = max(1, int(macd_signal_length))

    def zero_lag_ema(self, series, length):
        """
        Calculate the Zero-Lag Exponential Moving Average (ZLEMA) of a series.
        """
        ema1 = series.ewm(span=length, adjust=False).mean()
        ema2 = ema1.ewm(span=length, adjust=False).mean()
        zlema = 2 * ema1 - ema2
        return zlema

    def generate_signals(self, data, live: bool = False):
        signals = pd.Series(index=data.index, dtype=int)
        signals[:] = TradeAction.EXIT.value

        # VWAP calculation using a rolling window
        typical_price = (data['high'] + data['low'] + data['close']) / 3
        tp_vol = typical_price * data['volume']
        vwap = (
            tp_vol.rolling(window=self.vwap_window, min_periods=1).sum() /
            data['volume'].rolling(window=self.vwap_window, min_periods=1).sum()
        )

        # RSI calculation
        delta = data['close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=self.rsi_window).mean()
        avg_loss = loss.rolling(window=self.rsi_window).mean()
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        # Zero Lag MACD calculation
        zlema_fast = self.zero_lag_ema(data['close'], self.macd_fast_length)
        zlema_slow = self.zero_lag_ema(data['close'], self.macd_slow_length)
        zero_lag_macd = zlema_fast - zlema_slow

        # Signal line calculation (Zero Lag EMA of the MACD line)
        emasig1 = zero_lag_macd.ewm(span=self.macd_signal_length, adjust=False).mean()
        emasig2 = emasig1.ewm(span=self.macd_signal_length, adjust=False).mean()
        signal_line = 2 * emasig1 - emasig2

        # Generating signals
        position = TradeAction.EXIT.value
        check_from = (len(data) - 2) if live else 1

        for i in range(check_from, len(data)):
            long_entry = (
                data['close'].iloc[i] > vwap.iloc[i]
                and rsi.iloc[i] < self.rsi_oversold
                and zero_lag_macd.iloc[i] > signal_line.iloc[i]
                and zero_lag_macd.iloc[i - 1] <= signal_line.iloc[i - 1]
            )
            short_entry = (
                data['close'].iloc[i] < vwap.iloc[i]
                and rsi.iloc[i] > self.rsi_overbought
                and zero_lag_macd.iloc[i] < signal_line.iloc[i]
                and zero_lag_macd.iloc[i - 1] >= signal_line.iloc[i - 1]
            )

            long_exit = (
                position == TradeAction.ENTER_LONG.value
                and (
                    data['close'].iloc[i] < vwap.iloc[i]
                    or zero_lag_macd.iloc[i] < signal_line.iloc[i]
                    or rsi.iloc[i] > self.rsi_overbought
                )
            )
            short_exit = (
                position == TradeAction.ENTER_SHORT.value
                and (
                    data['close'].iloc[i] > vwap.iloc[i]
                    or zero_lag_macd.iloc[i] > signal_line.iloc[i]
                    or rsi.iloc[i] < self.rsi_oversold
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

        return signals
