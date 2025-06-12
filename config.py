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

# Default parameter ranges for the Different Strategies organized by timeframe
HYPER_SCALPER_RANGES = {
    '5m': [
        {'name': 'ema_fast', 'type': 'int', 'low': 10, 'high': 40},
        {'name': 'ema_mid', 'type': 'int', 'low': 60, 'high': 160},
        {'name': 'ema_long', 'type': 'int', 'low': 160, 'high': 400},
        {'name': 'adx_window', 'type': 'int', 'low': 6, 'high': 12},
        {'name': 'adx_threshold', 'type': 'int', 'low': 25, 'high': 35},
        {'name': 'pullback_window', 'type': 'int', 'low': 3, 'high': 7},
        {'name': 'stop_loss_pct', 'type': 'float', 'low': 0.3, 'high': 0.9},
        {'name': 'take_profit_pct', 'type': 'float', 'low': 0.5, 'high': 2}
    ],
    '15m': [
        {'name': 'ema_fast', 'type': 'int', 'low': 10, 'high': 40},
        {'name': 'ema_mid', 'type': 'int', 'low': 50, 'high': 150},
        {'name': 'ema_long', 'type': 'int', 'low': 150, 'high': 350},
        {'name': 'adx_window', 'type': 'int', 'low': 8, 'high': 14},
        {'name': 'adx_threshold', 'type': 'int', 'low': 24, 'high': 35},
        {'name': 'pullback_window', 'type': 'int', 'low': 3, 'high': 7},
        {'name': 'stop_loss_pct', 'type': 'float', 'low': 0.4, 'high': 1.2},
        {'name': 'take_profit_pct', 'type': 'float', 'low': 0.8, 'high': 3}
    ],
    '30m': [
        {'name': 'ema_fast', 'type': 'int', 'low': 12, 'high': 50},
        {'name': 'ema_mid', 'type': 'int', 'low': 60, 'high': 180},
        {'name': 'ema_long', 'type': 'int', 'low': 180, 'high': 400},
        {'name': 'adx_window', 'type': 'int', 'low': 8, 'high': 16},
        {'name': 'adx_threshold', 'type': 'int', 'low': 24, 'high': 35},
        {'name': 'pullback_window', 'type': 'int', 'low': 3, 'high': 8},
        {'name': 'stop_loss_pct', 'type': 'float', 'low': 0.5, 'high': 1.5},
        {'name': 'take_profit_pct', 'type': 'float', 'low': 1.0, 'high': 4}
    ],
    '1h': [
        {'name': 'ema_fast', 'type': 'int', 'low': 15, 'high': 60},
        {'name': 'ema_mid', 'type': 'int', 'low': 80, 'high': 200},
        {'name': 'ema_long', 'type': 'int', 'low': 200, 'high': 450},
        {'name': 'adx_window', 'type': 'int', 'low': 10, 'high': 18},
        {'name': 'adx_threshold', 'type': 'int', 'low': 22, 'high': 35},
        {'name': 'pullback_window', 'type': 'int', 'low': 4, 'high': 9},
        {'name': 'stop_loss_pct', 'type': 'float', 'low': 0.7, 'high': 2},
        {'name': 'take_profit_pct', 'type': 'float', 'low': 1.5, 'high': 6}
    ],
    '4h': [
        {'name': 'ema_fast', 'type': 'int', 'low': 18, 'high': 70},
        {'name': 'ema_mid', 'type': 'int', 'low': 100, 'high': 220},
        {'name': 'ema_long', 'type': 'int', 'low': 220, 'high': 500},
        {'name': 'adx_window', 'type': 'int', 'low': 10, 'high': 20},
        {'name': 'adx_threshold', 'type': 'int', 'low': 22, 'high': 34},
        {'name': 'pullback_window', 'type': 'int', 'low': 4, 'high': 9},
        {'name': 'stop_loss_pct', 'type': 'float', 'low': 1, 'high': 3},
        {'name': 'take_profit_pct', 'type': 'float', 'low': 2, 'high': 10}
    ],
    '1d': [
        {'name': 'ema_fast', 'type': 'int', 'low': 20, 'high': 80},
        {'name': 'ema_mid', 'type': 'int', 'low': 100, 'high': 250},
        {'name': 'ema_long', 'type': 'int', 'low': 250, 'high': 600},
        {'name': 'adx_window', 'type': 'int', 'low': 10, 'high': 20},
        {'name': 'adx_threshold', 'type': 'int', 'low': 20, 'high': 34},
        {'name': 'pullback_window', 'type': 'int', 'low': 5, 'high': 10},
        {'name': 'stop_loss_pct', 'type': 'float', 'low': 2, 'high': 6},
        {'name': 'take_profit_pct', 'type': 'float', 'low': 4, 'high': 18}
    ],
    '1w': [
        {'name': 'ema_fast', 'type': 'int', 'low': 4, 'high': 20},
        {'name': 'ema_mid', 'type': 'int', 'low': 20, 'high': 60},
        {'name': 'ema_long', 'type': 'int', 'low': 60, 'high': 120},
        {'name': 'adx_window', 'type': 'int', 'low': 10, 'high': 20},
        {'name': 'adx_threshold', 'type': 'int', 'low': 20, 'high': 34},
        {'name': 'pullback_window', 'type': 'int', 'low': 5, 'high': 10},
        {'name': 'stop_loss_pct', 'type': 'float', 'low': 4, 'high': 12},
        {'name': 'take_profit_pct', 'type': 'float', 'low': 8, 'high': 35}
    ]
}

PRICE_BREAKOUT_VOLUME_RANGES = {
    '5m': [
        {'name': 'lookback', 'type': 'int', 'low': 10, 'high': 50},
        {'name': 'volume_multiplier', 'type': 'float', 'low': 1.0, 'high': 3.0},
        {'name': 'stop_loss_pct', 'type': 'float', 'low': 0.4, 'high': 1},
        {'name': 'take_profit_pct', 'type': 'float', 'low': 0.8, 'high': 3},
    ],
    '15m': [
        {'name': 'lookback', 'type': 'int', 'low': 10, 'high': 50},
        {'name': 'volume_multiplier', 'type': 'float', 'low': 1.0, 'high': 3.0},
        {'name': 'stop_loss_pct', 'type': 'float', 'low': 0.6, 'high': 1.5},
        {'name': 'take_profit_pct', 'type': 'float', 'low': 1.2, 'high': 4},
    ],
    '30m': [
        {'name': 'lookback', 'type': 'int', 'low': 20, 'high': 100},
        {'name': 'volume_multiplier', 'type': 'float', 'low': 1.0, 'high': 3.0},
        {'name': 'stop_loss_pct', 'type': 'float', 'low': 0.6, 'high': 1.5},
        {'name': 'take_profit_pct', 'type': 'float', 'low': 1.2, 'high': 4},
    ],
    '1h': [
        {'name': 'lookback', 'type': 'int', 'low': 20, 'high': 100},
        {'name': 'volume_multiplier', 'type': 'float', 'low': 1.0, 'high': 3.0},
        {'name': 'stop_loss_pct', 'type': 'float', 'low': 0.8, 'high': 2},
        {'name': 'take_profit_pct', 'type': 'float', 'low': 2, 'high': 6},
    ],
    '4h': [
        {'name': 'lookback', 'type': 'int', 'low': 20, 'high': 120},
        {'name': 'volume_multiplier', 'type': 'float', 'low': 1.1, 'high': 2.0},
        {'name': 'stop_loss_pct', 'type': 'float', 'low': 1.2, 'high': 3},
        {'name': 'take_profit_pct', 'type': 'float', 'low': 3, 'high': 10},
    ],
    '1d': [
        {'name': 'lookback', 'type': 'int', 'low': 10, 'high': 90},
        {'name': 'volume_multiplier', 'type': 'float', 'low': 1.1, 'high': 1.8},
        {'name': 'stop_loss_pct', 'type': 'float', 'low': 2, 'high': 6},
        {'name': 'take_profit_pct', 'type': 'float', 'low': 5, 'high': 20},
    ],
    '1w': [
        {'name': 'lookback', 'type': 'int', 'low': 4, 'high': 26},
        {'name': 'volume_multiplier', 'type': 'float', 'low': 1.05, 'high': 1.4},
        {'name': 'stop_loss_pct', 'type': 'float', 'low': 4, 'high': 12},
        {'name': 'take_profit_pct', 'type': 'float', 'low': 10, 'high': 40},
    ]
}

