import logging
from optimization.utils import decode_value

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
        self.current_param_ranges = None
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
        if self.current_param_ranges:
            decoded = [
                decode_value(val, spec)
                for val, spec in zip(params, self.current_param_ranges)
            ]
        else:
            decoded = params
        strategy = self.current_strategy_class(*decoded)
        self.strategy_manager.reset(self.train_data)
        self.strategy_manager.execute_strategy(strategy)
        performance = self.result_analyzer.analyze(
            self.strategy_manager.trades, self.interval
        )
        
        score = 0.0
        for obj in self.objectives:
            value = performance.get(obj, 0)
            if obj == 'max_drawdown':
                value = -value  # smaller drawdown is better
            score += self.objective_weights.get(obj, 0) * value

        return score

    def _average_metrics(self, metrics_list):
        if not metrics_list:
            return {}
        keys = metrics_list[0].keys()
        averaged = {}
        for key in keys:
            averaged[key] = sum(m.get(key, 0) for m in metrics_list) / len(metrics_list)
        return averaged

    def _kfold_split(self, data, n_folds):
        fold_size = len(data) // n_folds
        if fold_size == 0:
            raise ValueError("Not enough data for the number of folds")
        splits = []
        for i in range(n_folds):
            start = i * fold_size
            end = start + fold_size if i < n_folds - 1 else len(data)
            test_data = data.iloc[start:end]
            train_data = data.drop(test_data.index)
            splits.append((train_data, test_data))
        return splits

    def run(
        self,
        symbol,
        interval,
        start_time,
        end_time,
        strategies,
        param_ranges,
        n_iterations,
        train_ratio=0.7,
        validation_mode="holdout",
        n_folds=2,
    ):
        logging.info("Starting trading system optimization")

        # Load data
        logging.info(f"Loading historical data for {symbol}")
        self.interval = interval
        self.data = self.data_loader.fetch_historical_data(
            symbol, interval, start_time, end_time
        )

        best_results = {}

        if validation_mode == "holdout":
            split_idx = int(len(self.data) * train_ratio)
            self.train_data = self.data.iloc[:split_idx]
            self.test_data = self.data.iloc[split_idx:]
            splits = [(self.train_data, self.test_data)]
        else:
            splits = self._kfold_split(self.data, n_folds)

        for strategy_class in strategies:
            logging.info(f"Optimizing {strategy_class.__name__}")
            self.current_strategy_class = strategy_class
            self.current_param_ranges = param_ranges[strategy_class.__name__]

            fold_train_metrics = []
            fold_test_metrics = []
            all_trades = []

            for train_data, test_data in splits:
                self.train_data = train_data
                self.test_data = test_data

                best_params = self.optimizer.optimize(
                    self.objective_function,
                    self.current_param_ranges,
                    n_iterations,
                )

                decoded_params = [
                    decode_value(val, spec)
                    for val, spec in zip(best_params, self.current_param_ranges)
                ]
                best_strategy = strategy_class(*decoded_params)

                self.strategy_manager.reset(train_data)
                self.strategy_manager.execute_strategy(best_strategy)
                train_perf = self.result_analyzer.analyze(
                    self.strategy_manager.trades, self.interval
                )
                train_trades = [trade.get_data() for trade in self.strategy_manager.trades]
                for t in train_trades:
                    t["dataset"] = "train"

                self.strategy_manager.reset(test_data)
                self.strategy_manager.execute_strategy(best_strategy)
                test_perf = self.result_analyzer.analyze(
                    self.strategy_manager.trades, self.interval
                )
                test_trades = [trade.get_data() for trade in self.strategy_manager.trades]
                for t in test_trades:
                    t["dataset"] = "test"

                all_trades.extend(train_trades)
                all_trades.extend(test_trades)

                fold_train_metrics.append(train_perf)
                fold_test_metrics.append(test_perf)

            avg_train = self._average_metrics(fold_train_metrics)
            avg_test = self._average_metrics(fold_test_metrics)
            if avg_train.get("total_trades", 0) == 0:
                avg_train["no_trades"] = True
            if avg_test.get("total_trades", 0) == 0:
                avg_test["no_trades"] = True

            best_params_map = {
                param["name"]: decode_value(val, param)
                for param, val in zip(self.current_param_ranges, best_params)
            }

            best_results[strategy_class.__name__] = {
                "params": best_params_map,
                "train_performance": avg_train,
                "test_performance": avg_test,
                "folds": {"train": fold_train_metrics, "test": fold_test_metrics},
                "trades": all_trades,
            }

        logging.info("Optimization completed")
        return best_results