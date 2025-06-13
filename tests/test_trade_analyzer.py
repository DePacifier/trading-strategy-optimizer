import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from datetime import datetime
import pytest
from strategy_manager import Trade
from utils.enums import Position
from evaluation.result_analyzer import ResultAnalyzer

def make_trade(entry, exit_price, position):
    t = Trade(datetime(2024,1,1), entry, position, 0, 0, 1)
    t.exit_time = datetime(2024,1,2)
    t.exit_price = exit_price
    return t

def test_profit_loss_long():
    t = make_trade(100, 120, Position.LONG)
    assert t.profit_loss == 20

def test_profit_loss_short():
    t = make_trade(100, 90, Position.SHORT)
    assert t.profit_loss == 10


def test_profit_loss_with_costs():
    t = Trade(
        datetime(2024, 1, 1),
        100,
        Position.LONG,
        0,
        0,
        1,
        buy_fee=0.01,
        sell_fee=0.01,
        slippage=0.01,
    )
    t.exit_time = datetime(2024, 1, 2)
    t.exit_price = 110
    t.costs = 100 * 0.01 + 110 * 0.01 + (100 + 110) * 0.01
    assert t.profit_loss == pytest.approx(110 - 100 - t.costs, rel=1e-9)

def test_result_analyzer():
    trades = [
        make_trade(100, 110, Position.LONG),
        make_trade(100, 90, Position.SHORT),
        make_trade(100, 95, Position.LONG),
    ]
    ra = ResultAnalyzer()
    perf = ra.analyze(trades)
    assert perf['total_trades'] == 3
    assert perf['profitable_trades'] == 2
    assert perf['win_rate'] == pytest.approx(0.667, rel=1e-3)
    assert perf['total_return'] == pytest.approx(15.0, rel=1e-3)
    assert perf['total_costs'] == 0
    assert perf['sharpe_ratio'] == pytest.approx(13.509, rel=1e-3)
    assert perf['sortino_ratio'] == 0
    assert perf['max_drawdown'] == 0.25
    assert perf['win_loss_ratio'] == 2.0
