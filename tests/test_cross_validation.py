import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import pandas as pd
from trading_system_controller import TradingSystemController
from strategy_manager import StrategyManager
from evaluation.result_analyzer import ResultAnalyzer
from utils.enums import TradeAction

class DummyLoader:
    def fetch_historical_data(self, symbol, interval, start_time, end_time):
        dates = pd.date_range('2024-01-01', periods=4)
        return pd.DataFrame({
            'open': [1,1,1,1],
            'high': [1,1,1,1],
            'low': [1,1,1,1],
            'close': [1,1,1,1],
            'volume':[1,1,1,1]
        }, index=dates)

class DummyOptimizer:
    def optimize(self, obj, param_ranges, n_iterations):
        obj([1])
        return [1]

class DummyStrategy:
    def __init__(self, p):
        # store as decimal from percentage inputs
        self.stop_loss_pct = 10 / 100
        self.take_profit_pct = 20 / 100
    def generate_signals(self, data):
        return pd.Series({data.index[0]: TradeAction.ENTER_LONG.value,
                          data.index[-1]: TradeAction.EXIT.value})

def test_cross_validation_split():
    loader = DummyLoader()
    sm = StrategyManager(None)
    optimizer = DummyOptimizer()
    controller = TradingSystemController(loader, sm, optimizer, ResultAnalyzer())
    results = controller.run('SYM', '1h', None, None, [DummyStrategy],
                             {'DummyStrategy': [{'name': 'p', 'type': 'int', 'low':0, 'high':1}]},
                             n_iterations=1, train_ratio=0.5)
    assert len(controller.train_data) == 2
    assert len(controller.test_data) == 2
    assert 'train_performance' in results['DummyStrategy']
    assert 'test_performance' in results['DummyStrategy']
