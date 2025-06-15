import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import pandas as pd
from utils.enums import TradeAction
from strategies.markov_entropy import MarkovEntropyStrategy


def test_markov_entropy_long_signal():
    dates = pd.date_range('2024-01-01', periods=360, freq='h')
    close = [1.01 ** i for i in range(360)]
    data = pd.DataFrame({
        'open': close,
        'high': close,
        'low': close,
        'close': close,
        'volume': [1] * len(close),
    }, index=dates)
    strat = MarkovEntropyStrategy(
        lookback_days=10,
        edge_threshold=0.0,
        entropy_threshold=1.0,
        stationary_threshold=0.0,
        kl_threshold=1.0,
        bucket_level='hour',
        stop_loss_pct=1,
        take_profit_pct=1,
    )
    signals = strat.generate_signals(data)
    assert list(signals) == [TradeAction.ENTER_LONG.value] * len(data)


def test_markov_entropy_short_signal():
    dates = pd.date_range('2024-01-01', periods=360, freq='h')
    close = [1.01 ** i for i in reversed(range(360))]
    data = pd.DataFrame({
        'open': close,
        'high': close,
        'low': close,
        'close': close,
        'volume': [1] * len(close),
    }, index=dates)
    strat = MarkovEntropyStrategy(
        lookback_days=10,
        edge_threshold=0.0,
        entropy_threshold=1.0,
        stationary_threshold=0.0,
        kl_threshold=1.0,
        bucket_level='hour',
        stop_loss_pct=1,
        take_profit_pct=1,
    )
    signals = strat.generate_signals(data)
    assert list(signals) == [TradeAction.ENTER_SHORT.value] * len(data)
