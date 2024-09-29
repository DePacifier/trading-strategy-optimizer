# Binance API credentials
BINANCE_API_KEY = 'your_binance_api_key'
BINANCE_API_SECRET = 'your_binance_api_secret'

# Telegram Bot credentials
TELEGRAM_BOT_TOKEN = "7399043948:AAGT4Y_cpZHDBTWU2RmxDUPEUu5HJAdpwQw"
TELEGRAM_CHAT_IDs = [300292003]

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
    'stop_loss_pct': 0.01,  # 2%
    'take_profit_pct': 0.0529  # 5.29%
}

# Risk management parameters
AVAILABLE_CAPITAL = 100  # Total capital in USD
RISK_PER_TRADE = 0.10  # Risk per trade as a fraction of capital (e.g., 0.01 for 1%)