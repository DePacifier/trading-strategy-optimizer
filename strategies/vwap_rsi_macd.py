import pandas as pd
from .base_strategy import Strategy
from utils.enums import TradeAction

class VWAP_RSI_MACDStrategy(Strategy):
    def __init__(
        self,
        vwap_window,
        rsi_window,
        rsi_overbought,
        rsi_oversold,
        macd_short_window,
        macd_long_window,
        macd_signal_window,
        stop_loss_pct,
        take_profit_pct
    ):
        super().__init__(stop_loss_pct, take_profit_pct)
        self.vwap_window = max(1, int(vwap_window))
        self.rsi_window = max(1, int(rsi_window))
        self.rsi_overbought = float(rsi_overbought)
        self.rsi_oversold = float(rsi_oversold)
        self.macd_short_window = max(1, int(macd_short_window))
        self.macd_long_window = max(1, int(macd_long_window))
        self.macd_signal_window = max(1, int(macd_signal_window))

    def generate_signals(self, data):
        signals = pd.Series(index=data.index)
        signals[:] = TradeAction.EXIT.value

        # VWAP calculation
        typical_price = (data['high'] + data['low'] + data['close']) / 3
        cumulative_tp_vol = (typical_price * data['volume']).cumsum()
        cumulative_vol = data['volume'].cumsum()
        vwap = cumulative_tp_vol / cumulative_vol

        # RSI calculation
        delta = data['close'].diff()
        gain = delta.where(delta > 0, 0).rolling(window=self.rsi_window).mean()
        loss = -delta.where(delta < 0, 0).rolling(window=self.rsi_window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        # MACD calculation
        short_ema = data['close'].ewm(span=self.macd_short_window, adjust=False).mean()
        long_ema = data['close'].ewm(span=self.macd_long_window, adjust=False).mean()
        macd = short_ema - long_ema
        signal_line = macd.ewm(span=self.macd_signal_window, adjust=False).mean()

        # Generating signals
        position = None
        for i in range(len(data)):
            if i == 0:
                continue  # Skip first data point due to lack of previous data
            # Long Entry Condition
            if (
                data['close'].iloc[i] > vwap.iloc[i] and
                rsi.iloc[i] > self.rsi_oversold and
                macd.iloc[i] > signal_line.iloc[i]
            ):
                if position != TradeAction.ENTER_LONG.value:
                    signals.iloc[i] = TradeAction.ENTER_LONG.value
                    position = TradeAction.ENTER_LONG.value
            # Short Entry Condition (optional)
            # Uncomment the following lines if short positions are allowed
            elif (
                data['close'].iloc[i] < vwap.iloc[i] and
                rsi.iloc[i] < self.rsi_overbought and
                macd.iloc[i] < signal_line.iloc[i]
            ):
                if position != TradeAction.ENTER_SHORT.value:
                    signals.iloc[i] = TradeAction.ENTER_SHORT.value
                    position = TradeAction.ENTER_SHORT.value
            # Exit Condition
            else:
                if position is not None:
                    # signals.iloc[i] = TradeAction.EXIT.value
                    position = None

        return signals