import os
import pandas as pd
from strategy_manager import StrategyManager
from evaluation import ResultAnalyzer
from utils.enums import TradeAction, TradeMode
from reporting.report_generator import ReportGenerator
from strategy_tester import StrategyTester


class DummyLoader:
    def __init__(self):
        self.called_with = None

    def fetch_historical_data(self, symbol, interval, start, end):
        self.called_with = (symbol, interval, start, end)
        dates = pd.date_range('2024-01-01', periods=2)
        return pd.DataFrame(
            {
                'open': [1, 1],
                'high': [1, 1],
                'low': [1, 1],
                'close': [1, 1],
                'volume': [1, 1],
            },
            index=dates,
        )


class DummyStrategy:
    def __init__(self, p):
        self.p = p
        self.stop_loss_pct = 10 / 100
        self.take_profit_pct = 20 / 100

    def generate_signals(self, data):
        return pd.Series(
            [TradeAction.ENTER_LONG.value, TradeAction.EXIT.value], index=data.index
        )


class DummyReport(ReportGenerator):
    def __init__(self, path):
        super().__init__()
        self.path = path

    def generate_report(self, *args, **kwargs):
        filename = kwargs.get('filename') or self.path
        with open(filename, 'w') as f:
            f.write('x')
        self.generated = filename


def test_strategy_tester(tmp_path):
    loader = DummyLoader()
    sm = StrategyManager(None, trade_mode=TradeMode.LONG_ONLY)
    rg = DummyReport(tmp_path / 'report.pdf')
    tester = StrategyTester(loader, sm, ResultAnalyzer(), rg)
    params = {'p': 5}
    results = tester.run(
        DummyStrategy,
        params,
        'SYM',
        '1d',
        '2024-01-01',
        '2024-01-02',
        report_file=str(tmp_path / 'report.pdf'),
    )
    assert loader.called_with == ('SYM', '1d', '2024-01-01', '2024-01-02')
    assert results['DummyStrategy']['params'] == params
    assert os.path.exists(rg.generated)
