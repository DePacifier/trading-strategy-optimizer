from data import DataLoader
from strategy_manager import StrategyManager
from optimization import GeneticAlgorithmOptimizer, ParticleSwarmOptimizer, BayesianOptimizer, ParallelHybridOptimizer, DifferentialEvolutionOptimizer
from evaluation import ResultAnalyzer
from reporting import ReportGenerator
from trading_system_controller import TradingSystemController
from strategies import VWAP_RSI_MACDStrategy
from binance.client import Client

def main():
    # Initialize components
    api_key = "Binance API KEY"
    api_secret = "Binance API Secret"
    data_loader = DataLoader(api_key, api_secret)
    strategy_manager = StrategyManager(None)
    ga_optimizer = GeneticAlgorithmOptimizer()
    pso_optimizer = ParticleSwarmOptimizer()
    bayesian_optimizer = BayesianOptimizer()
    differential_optimizer = DifferentialEvolutionOptimizer()
    parallel_hybrid_optimizer = ParallelHybridOptimizer(ga_optimizer, pso_optimizer, bayesian_optimizer, differential_optimizer, )
    result_analyzer = ResultAnalyzer()
    report_generator = ReportGenerator()

    # Create and run the controller
    controller = TradingSystemController(data_loader, strategy_manager, parallel_hybrid_optimizer, result_analyzer)
    
    # Set multiple objectives
    controller.set_objectives(['total_return'])
    
    best_results = controller.run(
        symbol='BTCUSDT',
        interval=Client.KLINE_INTERVAL_4HOUR,
        start_time="1 Jan, 2024",
        end_time="20 July, 2024",
        strategies=[VWAP_RSI_MACDStrategy],
        param_ranges={
            'MACD_RSIStrategy': [
                {'name': 'macd_short_window', 'type': 'int', 'low': 5, 'high': 20},
                {'name': 'macd_long_window', 'type': 'int', 'low': 20, 'high': 50},
                {'name': 'macd_signal_window', 'type': 'int', 'low': 5, 'high': 15},
                {'name': 'rsi_window', 'type': 'int', 'low': 10, 'high': 30},
                {'name': 'rsi_overbought', 'type': 'int', 'low': 70, 'high': 90},
                {'name': 'rsi_oversold', 'type': 'int', 'low': 10, 'high': 30},
                {'name': 'stop_loss_pct', 'type': 'int', 'low': 1, 'high': 2},
                {'name': 'take_profit_pct', 'type': 'int', 'low': 1, 'high': 4}
            ],
            'VWAP_RSI_MACDStrategy': [
                {'name': 'vwap_window', 'type': 'int', 'low': 5, 'high': 30},
                {'name': 'rsi_window', 'type': 'int', 'low': 10, 'high': 30},
                {'name': 'rsi_overbought', 'type': 'float', 'low': 70, 'high': 90},
                {'name': 'rsi_oversold', 'type': 'float', 'low': 10, 'high': 30},
                {'name': 'macd_short_window', 'type': 'int', 'low': 5, 'high': 20},
                {'name': 'macd_long_window', 'type': 'int', 'low': 20, 'high': 50},
                {'name': 'macd_signal_window', 'type': 'int', 'low': 5, 'high': 15},
                {'name': 'stop_loss_pct', 'type': 'float', 'low': 1, 'high': 2},
                {'name': 'take_profit_pct', 'type': 'float', 'low': 1, 'high': 4}
            ],
            'MovingAverageCrossover': [
                {'name': 'short_window', 'type': 'int', 'low': 5, 'high': 10},
                {'name': 'long_window', 'type': 'int', 'low': 5, 'high': 10},
                {'name': 'stop_loss_pct', 'type': 'int', 'low': 1, 'high': 2},
                {'name': 'take_profit_pct', 'type': 'int', 'low': 1, 'high': 4}
            ],
            'MACD_RSI_CMF_Strategy': [
                {'name': 'macd_short_window', 'type': 'int', 'low': 5, 'high': 20},
                {'name': 'macd_long_window', 'type': 'int', 'low': 20, 'high': 50},
                {'name': 'macd_signal_window', 'type': 'int', 'low': 5, 'high': 15},
                {'name': 'rsi_window', 'type': 'int', 'low': 10, 'high': 30},
                {'name': 'rsi_overbought', 'type': 'int', 'low': 70, 'high': 90},
                {'name': 'rsi_oversold', 'type': 'int', 'low': 10, 'high': 30},
                {'name': 'cmf_window', 'type': 'int', 'low': 10, 'high': 40},
                {'name': 'stop_loss_pct', 'type': 'int', 'low': 1, 'high': 2},
                {'name': 'take_profit_pct', 'type': 'int', 'low': 1, 'high': 4}
            ],
            'WilliamsFractals': [
                {'name': 'period', 'type': 'int', 'low': 2, 'high': 4},
                {'name': 'fractal_bars', 'type': 'int', 'low': 3, 'high': 5},
                {'name': 'stop_loss_pct', 'type': 'int', 'low': 1, 'high': 2},
                {'name': 'take_profit_pct', 'type': 'int', 'low': 1, 'high': 4}
            ]
        },
        n_iterations=100
    )

    # Generate the report
    report_generator.generate_report(best_results)

if __name__ == "__main__":
    main()