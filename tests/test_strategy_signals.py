import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import pandas as pd
from utils.enums import TradeAction
import importlib.util, importlib.machinery

path = os.path.join(os.path.dirname(__file__), '..', 'strategies')
if 'strategies' not in sys.modules:
    pkg = importlib.util.module_from_spec(importlib.machinery.ModuleSpec('strategies', None))
    pkg.__path__ = [path]
    sys.modules['strategies'] = pkg

file_path = os.path.join(path, 'moving_average_crossover.py')
spec = importlib.util.spec_from_file_location('strategies.moving_average_crossover', file_path)
mac_module = importlib.util.module_from_spec(spec)
sys.modules['strategies.moving_average_crossover'] = mac_module
spec.loader.exec_module(mac_module)
MovingAverageCrossover = mac_module.MovingAverageCrossover
from strategies.macd_rsi import MACD_RSIStrategy
from strategies.macd_rsi_cmf import MACD_RSI_CMF_Strategy
from strategies.bollinger_bands_strategy import BollingerBandsStrategy
from strategies.rsi_strategy import RSIStrategy
from strategies.price_breakout_volume import PriceBreakoutVolumeStrategy
from strategies.hyper_scalper import HyperScalper


def test_moving_average_crossover_signals():
    dates = pd.date_range('2024-01-01', periods=5)
    data = pd.DataFrame({'close':[5,4,3,2,3],
                         'open':[5]*5,
                         'high':[5]*5,
                         'low':[2]*5,
                         'volume':[1]*5}, index=dates)
    strat = MovingAverageCrossover(short_window=1, long_window=3, stop_loss_pct=1, take_profit_pct=1)
    signals = strat.generate_signals(data)
    expected = [TradeAction.EXIT.value, TradeAction.EXIT.value,
                TradeAction.ENTER_SHORT.value, TradeAction.ENTER_SHORT.value,
                TradeAction.ENTER_LONG.value]
    assert list(signals) == expected


def test_macd_rsi_position_persistence():
    dates = pd.date_range('2024-01-01', periods=5)
    close = [1, 2, 3, 4, 5]
    data = pd.DataFrame({
        'open': close,
        'high': close,
        'low': close,
        'close': close,
        'volume': [1] * 5
    }, index=dates)

    strat = MACD_RSIStrategy(
        macd_short_window=1,
        macd_long_window=2,
        macd_signal_window=2,
        rsi_window=1,
        rsi_overbought=200,
        rsi_oversold=101,
        stop_loss_pct=1,
        take_profit_pct=1,
    )
    signals = strat.generate_signals(data)
    expected = [TradeAction.EXIT.value] + [TradeAction.ENTER_LONG.value] * 4
    assert list(signals) == expected


def test_macd_rsi_cmf_position_persistence():
    dates = pd.date_range('2024-01-01', periods=5)
    close = [1, 2, 3, 4, 5]
    data = pd.DataFrame({
        'open': close,
        'high': [c + 1 for c in close],
        'low': [c - 2 for c in close],
        'close': close,
        'volume': [1] * 5,
    }, index=dates)

    strat = MACD_RSI_CMF_Strategy(
        macd_short_window=1,
        macd_long_window=2,
        macd_signal_window=2,
        rsi_window=1,
        rsi_overbought=200,
        rsi_oversold=101,
        cmf_window=1,
        stop_loss_pct=1,
        take_profit_pct=1,
    )
    signals = strat.generate_signals(data)
    expected = [TradeAction.EXIT.value] + [TradeAction.ENTER_LONG.value] * 4
    assert list(signals) == expected


file_path_vwap = os.path.join(path, 'vwap_rsi_macd.py')
spec_vwap = importlib.util.spec_from_file_location('strategies.vwap_rsi_macd', file_path_vwap)
vwap_module = importlib.util.module_from_spec(spec_vwap)
sys.modules['strategies.vwap_rsi_macd'] = vwap_module
spec_vwap.loader.exec_module(vwap_module)
VWAP_RSI_MACDStrategy = vwap_module.VWAP_RSI_MACDStrategy


def test_vwap_window_influences_signals():
    dates = pd.date_range('2024-01-01', periods=10)
    close = [1,1,1,1,10,1,1,1,1,1]
    data = pd.DataFrame({
        'close': close,
        'open': close,
        'high': close,
        'low':  close,
        'volume':[1,1,1,1,100,1,1,1,1,1]
    }, index=dates)

    strat_short = VWAP_RSI_MACDStrategy(
        vwap_window=1,
        rsi_window=1,
        rsi_overbought=101,
        rsi_oversold=-1,
        macd_short_window=2,
        macd_long_window=3,
        macd_signal_window=3,
        stop_loss_pct=1,
        take_profit_pct=1
    )

    strat_long = VWAP_RSI_MACDStrategy(
        vwap_window=3,
        rsi_window=1,
        rsi_overbought=101,
        rsi_oversold=-1,
        macd_short_window=2,
        macd_long_window=3,
        macd_signal_window=3,
        stop_loss_pct=1,
        take_profit_pct=1
    )

    signals_short = strat_short.generate_signals(data)
    signals_long = strat_long.generate_signals(data)

    expected_short = [TradeAction.EXIT.value] * 10
    expected_long = [
        TradeAction.EXIT.value,
        TradeAction.EXIT.value,
        TradeAction.EXIT.value,
        TradeAction.EXIT.value,
        TradeAction.ENTER_LONG.value,
        TradeAction.EXIT.value,
        TradeAction.EXIT.value,
        TradeAction.EXIT.value,
        TradeAction.EXIT.value,
        TradeAction.EXIT.value,
    ]

    assert list(signals_short) == expected_short
    assert list(signals_long) == expected_long


def test_bollinger_bands_position_persistence():
    dates = pd.date_range('2024-01-01', periods=5)
    close = [1, 0, 0, 0, 0.1]
    data = pd.DataFrame({
        'close': close,
        'open': close,
        'high': close,
        'low': close,
        'volume': [1] * 5,
    }, index=dates)

    strat = BollingerBandsStrategy(window=2, num_std=0.5)
    signals = strat.generate_signals(data)
    expected = [TradeAction.EXIT.value, TradeAction.ENTER_LONG.value,
                TradeAction.ENTER_LONG.value, TradeAction.ENTER_LONG.value,
                TradeAction.EXIT.value]
    assert list(signals) == expected


def test_rsi_position_persistence():
    dates = pd.date_range('2024-01-01', periods=5)
    close = [10, 20, 30, 80, 90]
    data = pd.DataFrame({
        'close': close,
        'open': close,
        'high': close,
        'low': close,
        'volume': [1] * 5,
    }, index=dates)

    strat = RSIStrategy(rsi_period=2, oversold=30, overbought=70)
    signals = strat.generate_signals(data)
    expected = [TradeAction.EXIT.value] + [TradeAction.ENTER_SHORT.value] * 4
    assert list(signals) == expected

def test_price_breakout_volume_signals():
    dates = pd.date_range('2024-01-01', periods=5)
    close = [5, 4, 6, 3, 2]

    data = pd.DataFrame({
        'close': close,
        'open': close,
        'high': close,
        'low': close,
        'volume': [1, 1, 5, 5, 8],
    }, index=dates)

    strat = PriceBreakoutVolumeStrategy(
        lookback=2,
        volume_multiplier=1.5,
        stop_loss_pct=1,
        take_profit_pct=1,
    )
    signals = strat.generate_signals(data)
    expected = [
        TradeAction.EXIT.value,
        TradeAction.EXIT.value,
        TradeAction.ENTER_LONG.value,
        TradeAction.EXIT.value,
        TradeAction.ENTER_SHORT.value,
    ]
    assert list(signals) == expected


def test_hyper_scalper_signals():
    dates = pd.date_range('2024-01-01', periods=4)
    close = [10, 9, 11, 10]
    data = pd.DataFrame({
        'close': close,
        'open': close,
        'high': close,
        'low': close,
        'volume': [1] * 4,
    }, index=dates)

    strat = HyperScalper(
        ema_fast=2,
        ema_mid=3,
        ema_long=4,
        adx_window=1,
        adx_threshold=-1,
        pullback_window=1,
        stop_loss_pct=1,
        take_profit_pct=1,
    )
    signals = strat.generate_signals(data)
    expected = [
        TradeAction.EXIT.value,
        TradeAction.EXIT.value,
        TradeAction.ENTER_LONG.value,
        TradeAction.EXIT.value,
    ]
    assert list(signals) == expected