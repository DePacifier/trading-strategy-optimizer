from datetime import datetime, timedelta
from binance.client import Client
from strategies import VWAP_RSI_ZeroLagMACDStrategy
from data import DataLoader
from notifiers import send_notifications, TextMessage
from config import (
    BINANCE_API_KEY,
    BINANCE_API_SECRET,
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_IDs,
    SYMBOL,
    INTERVAL,
    HISTORIC_MONTHS,
    STRATEGY_PARAMS,
    AVAILABLE_CAPITAL,
    RISK_PER_TRADE
)
from utils.enums import TradeAction

def main():
    # Calculate start and end dates
    end_time = datetime.now()
    interval_mapping = {
        '1m': Client.KLINE_INTERVAL_1MINUTE,
        '5m': Client.KLINE_INTERVAL_5MINUTE,
        '15m': Client.KLINE_INTERVAL_15MINUTE,
        '30m': Client.KLINE_INTERVAL_30MINUTE,
        '1h': Client.KLINE_INTERVAL_1HOUR,
        '4h': Client.KLINE_INTERVAL_4HOUR,
        '1d': Client.KLINE_INTERVAL_1DAY,
    }

    if INTERVAL not in interval_mapping:
        raise ValueError(f"Unsupported interval: {INTERVAL}")

    # Start date is the first day of the month, data_interval_months ago
    start_month = (end_time - timedelta(days=(30 * HISTORIC_MONTHS))).replace(day=1)
    start_time_str = start_month.strftime("%d %b %Y")
    end_time_str = end_time.strftime("%d %b %Y")

    # Initialize DataLoader
    data_loader = DataLoader(BINANCE_API_KEY, BINANCE_API_SECRET)
    data = data_loader.fetch_historical_data(SYMBOL, INTERVAL, start_time_str, end_time_str)

    # Ensure data is sufficient
    if data.empty:
        print("No data fetched.")
        return

    # Initialize strategy
    strategy = VWAP_RSI_ZeroLagMACDStrategy(
        vwap_window=STRATEGY_PARAMS['vwap_window'],
        rsi_window=STRATEGY_PARAMS['rsi_window'],
        rsi_overbought=STRATEGY_PARAMS['rsi_overbought'],
        rsi_oversold=STRATEGY_PARAMS['rsi_oversold'],
        macd_fast_length=STRATEGY_PARAMS['macd_fast_length'],
        macd_slow_length=STRATEGY_PARAMS['macd_slow_length'],
        macd_signal_length=STRATEGY_PARAMS['macd_signal_length'],
        stop_loss_pct=STRATEGY_PARAMS['stop_loss_pct'],
        take_profit_pct=STRATEGY_PARAMS['take_profit_pct']
    )

    # Generate signals
    signals = strategy.generate_signals(data, True)
    # Get the last signal
    current_signal = signals.iloc[-1]

    # Check if there's a new entry signal
    if current_signal in [TradeAction.ENTER_LONG.value, TradeAction.ENTER_SHORT.value]:
        entry_price = data['close'].iloc[-1]

        # Calculate stop loss and take profit prices
        if current_signal == TradeAction.ENTER_LONG.value:
            stop_loss_price = entry_price * (1 - STRATEGY_PARAMS['stop_loss_pct'])
            take_profit_price = entry_price * (1 + STRATEGY_PARAMS['take_profit_pct'])
        elif current_signal == TradeAction.ENTER_SHORT.value:
            stop_loss_price = entry_price * (1 + STRATEGY_PARAMS['stop_loss_pct'])
            take_profit_price = entry_price * (1 - STRATEGY_PARAMS['take_profit_pct'])

        # Calculate position size
        position_size = risk_based_position_sizing(
            AVAILABLE_CAPITAL,
            RISK_PER_TRADE,
            entry_price,
            stop_loss_price
        )

        # Prepare notification message
        if current_signal == TradeAction.ENTER_LONG.value:
            message = f"""
            🚀 **Enter LONG position for {SYMBOL}**
            Entry Price: {entry_price:.2f}
            Stop Loss Price: {stop_loss_price:.2f}
            Take Profit Price: {take_profit_price:.2f}
            Position Size: {position_size:.6f} {SYMBOL.replace('USDT', '')} per 100$
            """
        elif current_signal == TradeAction.ENTER_SHORT.value:
            message = f"""
            🔻 **Enter SHORT position for {SYMBOL}**
            Entry Price: {entry_price:.2f}
            Stop Loss Price: {stop_loss_price:.2f}
            Take Profit Price: {take_profit_price:.2f}
            Position Size: {position_size:.6f} {SYMBOL.replace('USDT', '')} per 100$
            """

        # Send notification
        strategy = TextMessage(message)
        send_notifications(strategy, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_IDs)
    else:
        print("No new entry signal.")
        print(len(signals))

def risk_based_position_sizing(available_capital, risk_per_trade, entry_price, stop_loss_price):
    """
    Calculate position size based on risk per trade.

    Parameters:
    - available_capital: Total capital available for trading.
    - risk_per_trade: Fraction of capital to risk per trade (e.g., 0.01 for 1%).
    - entry_price: The price at which the trade is entered.
    - stop_loss_price: The price at which the stop loss is set.

    Returns:
    - position_size: The size of the position (in units of the asset).
    """
    risk_amount = available_capital * risk_per_trade
    stop_loss_distance = abs(entry_price - stop_loss_price)
    position_size = risk_amount / stop_loss_distance
    max_position_size = available_capital / entry_price
    return min(position_size, max_position_size)

if __name__ == "__main__":
    main()