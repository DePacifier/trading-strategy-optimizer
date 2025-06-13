import argparse
import json
from datetime import datetime

from data import DataLoader
from strategy_manager import StrategyManager
from evaluation import ResultAnalyzer
from reporting import ReportGenerator
from utils.enums import TradeMode
import strategies
import config


class StrategyTester:
    def __init__(self, data_loader, strategy_manager, result_analyzer, report_generator):
        self.data_loader = data_loader
        self.strategy_manager = strategy_manager
        self.result_analyzer = result_analyzer
        self.report_generator = report_generator

    @classmethod
    def from_config(cls):
        loader = DataLoader(config.BINANCE_API_KEY, config.BINANCE_API_SECRET)
        manager = StrategyManager(
            None,
            initial_capital=100,
            risk_per_trade=0.10,
            trade_mode=TradeMode.LONG_ONLY,
            signal_exit=False,
            buy_fee=0.001,
            sell_fee=0.001,
        )
        return cls(loader, manager, ResultAnalyzer(), ReportGenerator())

    def run(self, strategy_class, params, symbol, interval, start_time, end_time, report_file=None):
        data = self.data_loader.fetch_historical_data(symbol, interval, start_time, end_time)
        self.strategy_manager.reset(data)
        strategy = strategy_class(**params)
        self.strategy_manager.execute_strategy(strategy)
        performance = self.result_analyzer.analyze(self.strategy_manager.trades, interval)
        trades = [t.get_data() for t in self.strategy_manager.trades]

        results = {
            strategy_class.__name__: {
                "params": params,
                "performance": performance,
                "trades": trades,
            }
        }

        self.report_generator.generate_report(
            results,
            filename=report_file,
            symbol=symbol,
            interval=interval,
            start_time=start_time,
            end_time=end_time,
        )
        return results


def parse_args():
    parser = argparse.ArgumentParser(description="Run a single strategy backtest")
    parser.add_argument("--strategy", required=True, help="Strategy class name")
    parser.add_argument("--params", required=True, help="JSON file with parameter values")
    parser.add_argument("--symbol", required=True, help="Trading pair symbol")
    parser.add_argument("--interval", required=True, help="Candle interval, e.g. 1d")
    parser.add_argument("--start", required=True, help="Start date YYYY-MM-DD")
    parser.add_argument("--end", required=True, help="End date YYYY-MM-DD")
    parser.add_argument("--report", default=None, help="Output PDF file")
    return parser.parse_args()


def main():
    args = parse_args()
    with open(args.params) as f:
        params = json.load(f)

    strategy_cls = getattr(strategies, args.strategy)

    # Binance expects dates like "1 Jan, 2020"
    def fmt(date_str):
        return datetime.strptime(date_str, "%Y-%m-%d").strftime("%d %b, %Y")

    tester = StrategyTester.from_config()
    tester.run(
        strategy_cls,
        params,
        args.symbol,
        args.interval,
        fmt(args.start),
        fmt(args.end),
        report_file=args.report,
    )


if __name__ == "__main__":
    main()
