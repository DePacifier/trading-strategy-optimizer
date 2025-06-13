import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import pandas as pd
from trading_system_controller import TradingSystemController
from strategy_manager import StrategyManager
from evaluation.result_analyzer import ResultAnalyzer
from reporting.report_generator import ReportGenerator


class DummyLoader:
    def fetch_historical_data(self, symbol, interval, start_time, end_time):
        dates = pd.date_range('2024-01-01', periods=4)
        return pd.DataFrame({
            'open': [1]*4,
            'high': [1]*4,
            'low': [1]*4,
            'close': [1]*4,
            'volume': [1]*4
        }, index=dates)


class DummyOptimizer:
    def optimize(self, obj, param_ranges, n_iterations):
        obj([1])
        return [1]


class NoTradeStrategy:
    def __init__(self, p):
        self.stop_loss_pct = 0.1
        self.take_profit_pct = 0.2

    def generate_signals(self, data):
        return pd.Series(dtype=int)


def test_no_trades_flag_and_report(tmp_path):
    loader = DummyLoader()
    sm = StrategyManager(None)
    optimizer = DummyOptimizer()
    controller = TradingSystemController(loader, sm, optimizer, ResultAnalyzer())
    results = controller.run(
        'SYM',
        '1h',
        None,
        None,
        [NoTradeStrategy],
        {'NoTradeStrategy': [{'name': 'p', 'type': 'int', 'low': 0, 'high': 1}]},
        n_iterations=1,
        train_ratio=0.5,
    )
    perf_train = results['NoTradeStrategy']['train_performance']
    perf_test = results['NoTradeStrategy']['test_performance']
    assert perf_train.get('no_trades') is True
    assert perf_test.get('no_trades') is True

    out_file = tmp_path / 'report.pdf'
    ReportGenerator().generate_report(results, filename=str(out_file))
    from pdfminer.high_level import extract_text
    text = extract_text(str(out_file))
    assert 'No trades executed' in text
    data_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'trades.csv')
    if os.path.exists(data_file):
        os.remove(data_file)

