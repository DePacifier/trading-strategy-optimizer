# Trading Strategy Optimizer

![Python Version](https://img.shields.io/badge/Python-3.x-blue) ![License](https://img.shields.io/github/license/DePacifier/trading-strategy-optimizer)

## Overview

**Trading Strategy Optimizer** is a Python toolkit for backtesting and tuning trading strategies using real market data.  
Candlestick data is downloaded from Binance and fed through several optimisation algorithms to discover the most profitable parameter combination.  
After the search a detailed PDF report is produced summarising the best parameters, the performance metrics and every simulated trade.

The optimiser ships with multiple algorithms and can run them in isolation or as a parallel hybrid search:

- **Genetic Optimisation**
- **Particle Swarm Optimisation**
- **Differential Evolution Optimisation**
- **Bayesian Optimisation**
- **Parallel Hybrid Optimiser** – runs GA → PSO → Differential Evolution → Bayesian in separate processes

## Features

- **Real-time Binance data** – fetches historical candles directly from Binance.
- **Multi-stage optimisation** – combine the available optimisers or use them individually.
- **Objective weighting** – optimise for one or several metrics (total return, win rate, Sharpe ratio, etc.) with optional weights.
- **Risk based position sizing** – trades use a fixed risk percentage of the available capital.
- **Long/short modes** – strategies can run in long only, short only or both directions.
- **Detailed PDF reports** – parameter table, train/test performance metrics and a list of all trades.
- **Telegram notifications** – `trades_finder.py` can scan the latest data and push alerts when new entry signals appear.

## Installation

1. **Clone the repository**

```bash
git clone https://github.com/DePacifier/trading-strategy-optimizer.git
cd trading-strategy-optimizer
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Configure API keys** – either export environment variables or edit `config.py` (used by the notifier script):

```bash
export BINANCE_API_KEY=your_key
export BINANCE_API_SECRET=your_secret
```

## Using the optimiser

All configuration lives in `main.py`. The important steps are:

1. **Choose optimisation objectives** using `controller.set_objectives`. Pass a list for equal weighting or a dictionary of weights:

```python
controller.set_objectives({'total_return': 70, 'sharpe_ratio': 30})
```

2. **Specify strategies and parameter ranges.** Each entry in `param_ranges` describes a tunable parameter with `low`, `high` and `type` (`int` or `float`).
3. **Select the optimisers** you wish to use – GA, PSO, Differential Evolution, Bayesian, or the `ParallelHybridOptimizer` which chains them together.
4. **Run `main.py`** to start the optimisation.

```bash
python main.py
```

During execution historical data is downloaded, split into training and testing sets (70/30 by default) and each strategy is optimised.  
A report file will appear under `reports/` named after the symbol and date range.

### Interpreting the report

The generated PDF contains for each strategy:

- **Parameter table** – the best values found for each tunable parameter.
- **Training/Test performance** – metrics such as total trades, win rate, total return, Sharpe ratio, Sortino ratio, maximum drawdown and win/loss ratio.
- **Trades table** – every simulated trade with entry/exit times, prices, position size and remaining capital.

By reviewing the training vs test metrics you can quickly judge if a strategy is over‑fitting.  The trades list helps to visually inspect how positions were opened and closed.

## Writing a new strategy

Strategies live in the `strategies/` directory. To add your own:

1. Create a new file, e.g. `my_strategy.py`.
2. Subclass `Strategy` from `strategies/base_strategy.py` and implement `generate_signals` which returns a `pandas.Series` of `TradeAction` values indexed by timestamp.
3. Include any parameters you wish to optimise (e.g. moving average lengths) in the constructor and remember that `stop_loss_pct` and `take_profit_pct` are expected in percentages.
4. Import your class in `strategies/__init__.py` so that it can be referenced elsewhere.
5. Update `main.py` to include the strategy class and provide its parameter ranges.

Example skeleton:

```python
from .base_strategy import Strategy
from utils.enums import TradeAction
import pandas as pd

class MyStrategy(Strategy):
    def __init__(self, my_window, stop_loss_pct, take_profit_pct):
        super().__init__(stop_loss_pct, take_profit_pct)
        self.my_window = int(my_window)

    def generate_signals(self, data):
        signals = pd.Series(index=data.index)
        signals[:] = TradeAction.EXIT.value
        # implement your logic here
        return signals
```

Signals should represent the desired position **at each time step**. If a trade
remains open, emit the current position (``TradeAction.ENTER_LONG`` or
``TradeAction.ENTER_SHORT``) for subsequent bars until an exit condition occurs.
Only output ``TradeAction.EXIT`` when you explicitly want to close the position.

Once added you can optimise it like the provided examples.

## Additional tools

- `trades_finder.py` – scans recent candles for a given strategy and sends Telegram messages if a new entry signal is detected.
- `tests/` – a suite of unit tests covering the optimisers, strategies and reporting utilities. Run them with `pytest` to verify changes.

## Project structure

```bash
.
├── data/                     # Data loading utilities
├── evaluation/               # Performance metrics
├── reporting/                # PDF report generation
├── reports/                  # Generated reports
├── strategies/               # Trading strategy implementations
├── tests/                    # Unit tests
├── utils/                    # Enums and helpers
├── main.py                   # Entry point for optimisation
├── optimization/             # Optimisation algorithms
├── strategy_manager.py       # Trade management engine
├── trading_system_controller.py # High level orchestration
└── requirements.txt          # Python dependencies
```

## Contributing

Contributions are welcome! If you find a bug or have a feature request, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.
