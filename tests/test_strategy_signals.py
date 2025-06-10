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
