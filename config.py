# Binance API credentials
import os

# Allow API credentials to be configured via environment variables.  This makes
# it easier to run the optimizer in different environments without modifying
# the source code.
BINANCE_API_KEY = os.getenv('BINANCE_API_KEY', 'your_binance_api_key')
BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET', 'your_binance_api_secret')

# Telegram Bot credentials
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'TELEGRAM_BOT_TOKEN')
chat_ids = os.getenv('TELEGRAM_CHAT_IDS', 'TELEGRAM_CHAT_ID_1,TELEGRAM_CHAT_ID_2')
TELEGRAM_CHAT_IDs = [cid.strip() for cid in chat_ids.split(',') if cid.strip()]

# Trading parameters
SYMBOL = 'BTCUSDT'
INTERVAL = '4h'  # Adjust as needed ('1m', '5m', '15m', '1h', '4h', etc.)
HISTORIC_MONTHS = 6

# Strategy parameters
STRATEGY_PARAMS = {
    'vwap_window': 30,
    'rsi_window': 8,
    'rsi_overbought': 67,
    'rsi_oversold': 35,
    'macd_fast_length': 9,
    'macd_slow_length': 16,
    'macd_signal_length': 3,
    # Stop-loss and take-profit expressed in percentages (1 = 1%)
    'stop_loss_pct': 1,
    'take_profit_pct': 5.29
}

# Risk management parameters
AVAILABLE_CAPITAL = 100  # Total capital in USD
RISK_PER_TRADE = 0.10  # Risk per trade as a fraction of capital (e.g., 0.01 for 1%)

# Default parameter ranges for the PriceBreakoutVolumeStrategy organised by timeframe
PRICE_BREAKOUT_VOLUME_RANGES = {
    '5m': [
        {'name': 'lookback', 'type': 'int', 'low': 10, 'high': 50},
        {'name': 'volume_multiplier', 'type': 'float', 'low': 1.0, 'high': 3.0},
        {'name': 'stop_loss_pct', 'type': 'float', 'low': 1, 'high': 2},
        {'name': 'take_profit_pct', 'type': 'float', 'low': 1, 'high': 4},
    ],
    '1h': [
        {'name': 'lookback', 'type': 'int', 'low': 20, 'high': 100},
        {'name': 'volume_multiplier', 'type': 'float', 'low': 1.0, 'high': 3.0},
        {'name': 'stop_loss_pct', 'type': 'float', 'low': 1, 'high': 2},
        {'name': 'take_profit_pct', 'type': 'float', 'low': 1, 'high': 6},
    ],
}

