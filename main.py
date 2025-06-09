from data import DataLoader
from strategy_manager import StrategyManager
from optimization import GeneticAlgorithmOptimizer, ParticleSwarmOptimizer, BayesianOptimizer, ParallelHybridOptimizer, DifferentialEvolutionOptimizer
from evaluation import ResultAnalyzer
from reporting import ReportGenerator
from trading_system_controller import TradingSystemController
from strategies import VWAP_RSI_MACDStrategy, VWAP_RSI_ZeroLagMACDStrategy, ZeroLagMACD_OBV_Strategy, EMACrossover
from binance.client import Client

def main():
    # Initialize components
    api_key = "Binance API KEY"
    api_secret = "Binance API Secret"
    data_loader = DataLoader(api_key, api_secret)
    strategy_manager = StrategyManager(None, initial_capital=100, risk_per_trade=0.10)
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
        symbol='NEIROUSDT',
        interval=Client.KLINE_INTERVAL_5MINUTE,
        start_time="1 Jan, 2024",
        end_time="8 Oct, 2024",
        strategies=[EMACrossover],
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
                {'name': 'rsi_overbought', 'type': 'int', 'low': 70, 'high': 90},
                {'name': 'rsi_oversold', 'type': 'int', 'low': 10, 'high': 30},
                {'name': 'macd_short_window', 'type': 'int', 'low': 5, 'high': 20},
                {'name': 'macd_long_window', 'type': 'int', 'low': 20, 'high': 50},
                {'name': 'macd_signal_window', 'type': 'int', 'low': 5, 'high': 15},
                {'name': 'stop_loss_pct', 'type': 'float', 'low': 1, 'high': 2},
                {'name': 'take_profit_pct', 'type': 'float', 'low': 1, 'high': 4}
            ],
            'VWAP_RSI_ZeroLagMACDStrategy1-4hr': [
                {'name': 'vwap_window', 'type': 'int', 'low': 5, 'high': 30},
                {'name': 'rsi_window', 'type': 'int', 'low': 7, 'high': 21},
                {'name': 'rsi_overbought', 'type': 'int', 'low': 65, 'high': 85},
                {'name': 'rsi_oversold', 'type': 'int', 'low': 15, 'high': 35},
                {'name': 'macd_fast_length', 'type': 'int', 'low': 5, 'high': 15},
                {'name': 'macd_slow_length', 'type': 'int', 'low': 10, 'high': 30},
                {'name': 'macd_signal_length', 'type': 'int', 'low': 3, 'high': 12},
                {'name': 'stop_loss_pct', 'type': 'float', 'low': 1, 'high': 3},
                {'name': 'take_profit_pct', 'type': 'float', 'low': 1, 'high': 6}
            ],
            'VWAP_RSI_ZeroLagMACDStrategy': [
                # {'name': 'vwap_window', 'type': 'int', 'low': 5, 'high': 30},
                {'name': 'rsi_window', 'type': 'int', 'low': 5, 'high': 14},
                {'name': 'rsi_overbought', 'type': 'int', 'low': 75, 'high': 95},
                {'name': 'rsi_oversold', 'type': 'int', 'low': 5, 'high': 25},
                {'name': 'macd_fast_length', 'type': 'int', 'low': 3, 'high': 12},
                {'name': 'macd_slow_length', 'type': 'int', 'low': 6, 'high': 26},
                {'name': 'macd_signal_length', 'type': 'int', 'low': 3, 'high': 9},
                {'name': 'stop_loss_pct', 'type': 'int', 'low': 1, 'high': 2},
                {'name': 'take_profit_pct', 'type': 'int', 'low': 2, 'high': 6}
            ],
            'ZeroLagMACD_OBV_Strategy': [
                {'name': 'macd_fast_length', 'type': 'int', 'low': 10, 'high': 30},
                {'name': 'macd_slow_length', 'type': 'int', 'low': 30, 'high': 60},
                {'name': 'macd_signal_length', 'type': 'int', 'low': 10, 'high': 25},
                {'name': 'obv_smoothing_length', 'type': 'int', 'low': 10, 'high': 30},
                {'name': 'stop_loss_pct', 'type': 'int', 'low': 1, 'high': 5},
                {'name': 'take_profit_pct', 'type': 'int', 'low': 2, 'high': 10}
            ],
            'MovingAverageCrossover': [
                {'name': 'short_window', 'type': 'int', 'low': 5, 'high': 10},
                {'name': 'long_window', 'type': 'int', 'low': 5, 'high': 10},
                {'name': 'stop_loss_pct', 'type': 'int', 'low': 1, 'high': 2},
                {'name': 'take_profit_pct', 'type': 'int', 'low': 1, 'high': 4}
            ],
            'EMACrossover': [
                {'name': 'short_window', 'type': 'int', 'low': 3, 'high': 15},
                {'name': 'long_window', 'type': 'int', 'low': 10, 'high': 50},
                {'name': 'stop_loss_pct', 'type': 'int', 'low': 1, 'high': 2},
                {'name': 'take_profit_pct', 'type': 'int', 'low': 1, 'high': 3}
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
        n_iterations=50
    )

    # Generate the report
    file_name = "NEIROUSDT-Jan-Oct-24-5M-EMACRS"
    report_generator.generate_report(best_results, filename=f"{file_name}.pdf")
    

if __name__ == "__main__":
    main()