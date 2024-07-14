from data.data_loader import DataLoader
from strategy_manager import StrategyManager
from optimization.genetic_algorithm import GeneticAlgorithmOptimizer
from optimization.particle_swarm import ParticleSwarmOptimizer
from optimization.bayesian_optimization import BayesianOptimizer
from optimization.hybrid_optimizer import ParallelHybridOptimizer
from optimization.differential_evolution import DifferentialEvolutionOptimizer
from evaluation.result_analyzer import ResultAnalyzer
from reporting.report_generator import ReportGenerator
from trading_system_controller import TradingSystemController
from strategies.moving_average_crossover import MovingAverageCrossover
from strategies.rsi_strategy import RSIStrategy
from strategies.bollinger_bands_strategy import BollingerBandsStrategy
from binance.client import Client

def main():
    # Initialize components
    api_key = "J3xAHx96UXy2TbX1JqcMXEJwkLPujKI5akWHzYgZPTNKw1uPCHTD7qzrciQ3tQaD"
    api_secret = "b5NUms8Jus85y278SxtnFSDZbwjU6p8sLYrO1C866qaqcN8Rs4HcOBuzsf2Jfyng"
    data_loader = DataLoader(api_key, api_secret)
    strategy_manager = StrategyManager(None)
    ga_optimizer = GeneticAlgorithmOptimizer()
    pso_optimizer = ParticleSwarmOptimizer()
    bayesian_optimizer = BayesianOptimizer()
    differential_optimizer = DifferentialEvolutionOptimizer()
    parallel_hybrid_optimizer = ParallelHybridOptimizer(ga_optimizer, pso_optimizer, bayesian_optimizer, differential_optimizer)
    result_analyzer = ResultAnalyzer()
    report_generator = ReportGenerator()

    # Create and run the controller
    controller = TradingSystemController(data_loader, strategy_manager, parallel_hybrid_optimizer, result_analyzer)
    best_results = controller.run(
        symbol='BTCUSDT',
        interval=Client.KLINE_INTERVAL_4HOUR,
        start_time="1 Jan, 2020",
        end_time="1 Jan, 2021",
        # strategies=[MovingAverageCrossover, RSIStrategy, BollingerBandsStrategy],
        strategies=[MovingAverageCrossover],
        param_ranges={
            'MovingAverageCrossover': [
                {'name': 'short_window', 'type': 'int', 'low': 5, 'high': 50},
                {'name': 'long_window', 'type': 'int', 'low': 10, 'high': 200},
                {'name': 'stop_loss_pct', 'type': 'float', 'low': 0.01, 'high': 0.1},
                {'name': 'take_profit_pct', 'type': 'float', 'low': 0.01, 'high': 0.2}
            ],
            # 'RSIStrategy': [(5, 30), (20, 40), (60, 80)],
            # 'BollingerBandsStrategy': [(10, 50), (1, 3)]
        },
        n_iterations=100
    )

    # Generate the report
    report_generator.generate_report(best_results)

if __name__ == "__main__":
    main()