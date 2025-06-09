import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TradingSystemController:
    def __init__(self, data_loader, strategy_manager, optimizer, result_analyzer):
        self.data_loader = data_loader
        self.strategy_manager = strategy_manager
        self.optimizer = optimizer
        self.result_analyzer = result_analyzer
        self.data = None
        self.train_data = None
        self.test_data = None
        self.current_strategy_class = None
        self.objectives = ['sharpe_ratio']
        self.objective_weights = {'sharpe_ratio': 1.0}
    
    def set_objectives(self, objectives):
        """Set optimization objectives with optional weighting.

        Parameters
        ----------
        objectives : list or dict
            If a list is provided, each objective is given equal weight.
            If a dict is provided, keys are objective names and values are
            weights (e.g. percentages) indicating their relative importance.
        """
        if isinstance(objectives, dict):
            self.objectives = list(objectives.keys())
            total = float(sum(objectives.values())) or 1.0
            self.objective_weights = {
                obj: weight / total for obj, weight in objectives.items()
            }
        else:
            self.objectives = list(objectives)
            if self.objectives:
                eq_weight = 1.0 / len(self.objectives)
            else:
                eq_weight = 1.0
            self.objective_weights = {obj: eq_weight for obj in self.objectives}

    def objective_function(self, params):
        strategy = self.current_strategy_class(*params)
        self.strategy_manager.reset(self.train_data)
        self.strategy_manager.execute_strategy(strategy)
        performance = self.result_analyzer.analyze(self.strategy_manager.trades)
        
        score = 0.0
        for obj in self.objectives:
            value = performance.get(obj, 0)
            if obj == 'max_drawdown':
                value = -value  # smaller drawdown is better
            score += self.objective_weights.get(obj, 0) * value

        return score

    def run(self, symbol, interval, start_time, end_time, strategies, param_ranges, n_iterations, train_ratio=0.7):
        logging.info("Starting trading system optimization")

        # Load data
        logging.info(f"Loading historical data for {symbol}")
        self.data = self.data_loader.fetch_historical_data(symbol, interval, start_time, end_time)
        split_idx = int(len(self.data) * train_ratio)
        self.train_data = self.data.iloc[:split_idx]
        self.test_data = self.data.iloc[split_idx:]

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

            # Evaluate on training data
            self.strategy_manager.reset(self.train_data)
            self.strategy_manager.execute_strategy(best_strategy)
            train_performance = self.result_analyzer.analyze(self.strategy_manager.trades)

            # Evaluate on test data
            self.strategy_manager.reset(self.test_data)
            self.strategy_manager.execute_strategy(best_strategy)
            test_performance = self.result_analyzer.analyze(self.strategy_manager.trades)

            best_params = {param["name"]:best_param for param, best_param in zip(param_ranges[strategy_class.__name__], best_params)}
            trades = [trade.get_data() for trade in self.strategy_manager.trades]
            best_results[strategy_class.__name__] = {
                'params': best_params,
                'train_performance': train_performance,
                'test_performance': test_performance,
                'trades': trades
            }

        logging.info("Optimization completed")
        return best_results