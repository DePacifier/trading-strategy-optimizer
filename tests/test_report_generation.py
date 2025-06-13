import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from reporting.report_generator import ReportGenerator


def test_report_generation(tmp_path):
    rg = ReportGenerator()
    results = {
        'Dummy': {
            'params': {'a': 1},
            'performance': {
                'total_trades': 1,
                'profitable_trades': 1,
                'win_rate': 1.0,
                'total_return': 1.0,
                'sharpe_ratio': 1.0,
                'sortino_ratio': 1.0,
                'max_drawdown': 0.0,
                'win_loss_ratio': 1.0
            },
            'trades': [
                {
                    'entry_time': '2024-01-01 00:00:00',
                    'entry_price': 100,
                    'position': 1,
                    'exit_time': '2024-01-02 00:00:00',
                    'exit_price': 110,
                    'profit_loss': 10,
                    'costs': 0,
                    'size': 1,
                    'remaining_capital': 110
                }
            ]
        }
    }
    out_file = tmp_path / 'report.pdf'
    rg.generate_report(results, filename=str(out_file))
    assert out_file.exists()
    data_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'trades.csv')
    if os.path.exists(data_file):
        os.remove(data_file)
