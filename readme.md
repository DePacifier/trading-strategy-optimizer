# Trading Strategy Optimizer

![Python Version](https://img.shields.io/badge/Python-3.x-blue) ![License](https://img.shields.io/github/license/DePacifier/trading-strategy-optimizer)

## Overview

**Trading Strategy Optimizer** is a Python tool designed to optimize trading strategies by tuning their parameters to achieve specific performance objectives. It fetches candlestick data from Binance, runs one or more optimization algorithms, and generates a detailed PDF report.

The optimizer supports three types of optimizations, and you can choose to run one or all:
- **Genetic Optimization**
- **Differential Evolution Optimization**
- **Bayesian Optimization**

## Features

- **Real-time Binance data**: Fetches candlestick data from Binance.
- **Multi-stage Optimization**: Runs Genetic, Differential Evolution, and Bayesian optimizations sequentially (or individually) to find optimal strategy parameters.
- **Customizable Objectives**: Optimize towards objectives such as:
  - Total trades
  - Profitable trades
  - Win rate
  - Total return
  - Sharpe ratio
  - Sortino ratio
  - Max drawdown
  - Win/Loss ratio
- **Detailed Reports**: Generates a PDF report for each strategy, detailing the best parameters and performance analysis.

## Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/DePacifier/trading-strategy-optimizer.git
    cd trading-strategy-optimizer
    ```

2. **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3. **Set up Binance API keys** in `.env` file:

    ```bash
    BINANCE_API_KEY=your_binance_api_key
    BINANCE_SECRET_KEY=your_binance_secret_key
    ```

## Usage

### 1. Modify the `main.py` file

- **Define your trading strategies** and **set the objectives** you want to optimize (e.g., win_rate, total_return).
- **Choose the optimizers** you want to run. You can select one or run all three (Genetic, Differential Evolution, and Bayesian).

### 2. Run the optimizer

After modifying `main.py` according to your strategy and preferences, simply run it:

```bash
python main.py
```

This will fetch data from Binance, perform the optimization, and generate a PDF report in the `reports/` directory.

### Example

To optimize a strategy for win rate and total return using all three optimizers:

1. Set the objectives and optimization methods in `main.py`.
2. Run:

    ```bash
    python main.py
    ```

A PDF report with the results will be generated automatically.

## Project Structure

```bash
.
├── data/                     # Scripts to collect and manage trading data from Binance
├── evaluation/               # Scripts for evaluating and analyzing trading strategy performance
├── reporting/                # Scripts for generating PDF reports of optimization results
├── reports/                  # Directory to store the generated PDF reports
├── strategies/               # Sample trading strategies and their configurations
├── tests/                    # Sample test cases for validation and debugging
├── utils/                    # Utility scripts for common functionality (helpers, data processing, etc.)
├── main.py                   # Main script to configure and run the optimizer
├── optimization/             # Implementations of optimization algorithms (Genetic, Differential, Bayesian)
├── strategy_manager.py       # Script for managing and executing trading strategies
├── trading_system_controller.py # Controller script for running and managing the optimization process
├── requirements.txt          # List of Python dependencies to be installed
└── README.md                 # The main README file (project documentation)
```

## Contributing

Contributions are welcome! If you find a bug or have a feature request, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.