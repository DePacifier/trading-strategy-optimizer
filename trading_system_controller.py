import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TradingSystemController:
    def __init__(self, data_loader, strategy_manager, optimizer, result_analyzer):
        self.data_loader = data_loader
        self.strategy_manager = strategy_manager
        self.optimizer = optimizer
        self.result_analyzer = result_analyzer
        self.data = None
        self.current_strategy_class = None
        self.objectives = ['sharpe_ratio']
    
    def set_objectives(self, objectives):
        self.objectives = objectives

    def objective_function(self, params):
        strategy = self.current_strategy_class(*params)
        self.strategy_manager.reset(self.data)
        self.strategy_manager.execute_strategy(strategy)
        performance = self.result_analyzer.analyze(self.strategy_manager.trades)
        
        if len(self.objectives) == 1:
            return performance[self.objectives[0]]
        else:
            return [-performance[obj] for obj in self.objectives] 

    def run(self, symbol, interval, start_time, end_time, strategies, param_ranges, n_iterations):
        logging.info("Starting trading system optimization")

        # Load data
        logging.info(f"Loading historical data for {symbol}")
        self.data = self.data_loader.fetch_historical_data(symbol, interval, start_time, end_time)

        best_results = {}
        for strategy_class in strategies:
            logging.info(f"Optimizing {strategy_class.__name__}")
            self.current_strategy_class = strategy_class

            best_params = self.optimizer.optimize(
                self.objective_function,
                param_ranges[strategy_class.__name__],
                n_iterations
            )
            
            print("Identified best parameters are:")
            print(best_params)
            
            best_strategy = strategy_class(*best_params)

            self.strategy_manager.reset(self.data)
            self.strategy_manager.execute_strategy(best_strategy)

            performance = self.result_analyzer.analyze(self.strategy_manager.trades)
            best_params = {param["name"]:best_param for param, best_param in zip(param_ranges[strategy_class.__name__], best_params)}
            trades = [trade.get_data() for trade in self.strategy_manager.trades]
            best_results[strategy_class.__name__] = {
                'params': best_params,
                'performance': performance,
                'trades': trades
            }

        logging.info("Optimization completed")
        return best_results