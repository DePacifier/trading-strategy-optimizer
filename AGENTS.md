# Repository Guide for trading-strategy-optimizer

This project is a toolkit for backtesting and optimising crypto trading strategies.  Historical data is fetched from Binance, multiple optimisation algorithms search the parameter space and PDF reports are produced summarising the results.  A live trading module is also included.

## Directory overview

- **data/** – Binance data loader utilities
- **evaluation/** – performance metrics (Sharpe, Sortino, etc.)
- **live_trading/** – modules for streaming candles and executing strategies live
- **optimization/** – optimisation algorithms (Genetic Algorithm, PSO, Differential Evolution, Bayesian and the hybrid optimiser)
- **reporting/** – PDF report generation helpers
- **strategies/** – individual trading strategy implementations
- **tests/** – pytest unit tests
- **main.py** – entry point for running an optimisation
- **run_live_trader.py** – example setup for live trading

## Development notes

- Follow standard PEP8 style (4 space indents, descriptive names).
- When adding a new strategy file, import it in `strategies/__init__.py` so it is discoverable by other modules.
- Do not store API keys or secrets in the repository.  `config.py` reads them from environment variables.

## Running tests

Install dependencies from `requirements.txt` and then run:

```bash
pytest -q
```

All modifications should keep the test suite passing.

