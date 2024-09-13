import pandas as pd
from .base_strategy import Strategy
from utils.enums import TradeAction

class MACD_RSIStrategy(Strategy):
    def __init__(self, macd_short_window, macd_long_window, macd_signal_window, rsi_window, rsi_overbought, rsi_oversold, stop_loss_pct, take_profit_pct):
        super().__init__(stop_loss_pct, take_profit_pct)
        self.macd_short_window = max(1, int(macd_short_window))
        self.macd_long_window = max(1, int(macd_long_window))
        self.macd_signal_window = max(1, int(macd_signal_window))
        self.rsi_window = max(1, int(rsi_window))
        self.rsi_overbought = float(rsi_overbought)
        self.rsi_oversold = float(rsi_oversold)

    def generate_signals(self, data):
        signals = pd.Series(index=data.index)
        signals[:] = TradeAction.EXIT.value

        # MACD calculation
        short_ema = data['close'].ewm(span=self.macd_short_window, adjust=False).mean()
        long_ema = data['close'].ewm(span=self.macd_long_window, adjust=False).mean()
        macd = short_ema - long_ema
        signal_line = macd.ewm(span=self.macd_signal_window, adjust=False).mean()

        # RSI calculation
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.rsi_window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.rsi_window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        # Generating signals
        for i in range(len(data)):
            if macd.iloc[i] > signal_line.iloc[i] and rsi.iloc[i] < self.rsi_oversold:
                signals.iloc[i] = TradeAction.ENTER_LONG.value
            # elif macd.iloc[i] < signal_line.iloc[i] and rsi.iloc[i] > self.rsi_overbought:
            #     signals.iloc[i] = TradeAction.ENTER_SHORT.value

        return signals
