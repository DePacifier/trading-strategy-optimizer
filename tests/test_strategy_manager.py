import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from datetime import datetime
import pandas as pd
from strategy_manager import StrategyManager
from utils.enums import TradeAction, TradeMode, Position

class DummyStrategy:
    def __init__(self):
        # inputs provided in percentages
        self.stop_loss_pct = 10 / 100
        self.take_profit_pct = 20 / 100
    def generate_signals(self, data):
        return pd.Series({data.index[0]: TradeAction.ENTER_LONG.value,
                           data.index[1]: TradeAction.EXIT.value})

class LongShortStrategy:
    def __init__(self):
        self.stop_loss_pct = 10 / 100
        self.take_profit_pct = 20 / 100

    def generate_signals(self, data):
        return pd.Series({
            data.index[0]: TradeAction.ENTER_LONG.value,
            data.index[1]: TradeAction.ENTER_SHORT.value,
            data.index[2]: TradeAction.EXIT.value
        })

def make_data():
    index = [datetime(2024,1,1), datetime(2024,1,2), datetime(2024,1,3)]
    return pd.DataFrame({
        'open':[100,110,120],
        'high':[105,112,125],
        'low':[95,98,118],
        'close':[100,110,120],
        'volume':[1000,1000,1000]
    }, index=index)


def test_risk_based_position_sizing():
    sm = StrategyManager(None, initial_capital=1000, risk_per_trade=0.1)
    size = sm.risk_based_position_sizing(100, 90)
    assert size == 10
    size = sm.risk_based_position_sizing(100, 99)
    assert size == 10


def test_execute_strategy_basic():
    data = make_data()
    sm = StrategyManager(data, initial_capital=100, risk_per_trade=0.1)
    sm.execute_strategy(DummyStrategy())
    assert len(sm.trades) == 1
    trade = sm.trades[0]
    assert trade.entry_time == data.index[0]
    assert trade.exit_time == data.index[1]
    assert trade.profit_loss == 10


def test_trade_mode_long_only():
    data = make_data()
    sm = StrategyManager(data, initial_capital=100, risk_per_trade=0.1, trade_mode=TradeMode.LONG_ONLY)
    sm.execute_strategy(LongShortStrategy())
    # Should ignore short entry
    assert len(sm.trades) == 1
    assert sm.trades[0].position == Position.LONG


def test_trade_mode_short_only():
    data = make_data()
    sm = StrategyManager(data, initial_capital=100, risk_per_trade=0.1, trade_mode=TradeMode.SHORT_ONLY)
    sm.execute_strategy(LongShortStrategy())
    assert len(sm.trades) == 1
    assert sm.trades[0].position == Position.SHORT
