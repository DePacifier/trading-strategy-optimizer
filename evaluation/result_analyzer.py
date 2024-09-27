import numpy as np

class ResultAnalyzer:
    def calculate_sharpe_ratio(self, trades, risk_free_rate=0.02):
        returns = [trade.profit_loss for trade in trades if trade.profit_loss is not None]

        if len(returns) < 2:
            return -np.inf
        
        annual_factor = 365  # Assuming 365 trading days in a year
        returns_mean = np.mean(returns)
        returns_std = np.std(returns)
        
        if returns_std == 0:
            return 0
        
        sharpe_ratio = (returns_mean - (risk_free_rate / annual_factor)) / returns_std * np.sqrt(annual_factor)
        return sharpe_ratio

    def calculate_sortino_ratio(self, trades, risk_free_rate=0.02):
        returns = [trade.profit_loss for trade in trades if trade.profit_loss is not None]
        
        if len(returns) < 2:
            return -np.inf
        
        annual_factor = 365  # Assuming 365 trading days in a year
        returns_mean = np.mean(returns)
        downside_returns = [r for r in returns if r < 0]
        downside_std = np.std(downside_returns) if len(downside_returns) > 1 else 0
        
        if downside_std == 0:
            return 0
        
        sortino_ratio = (returns_mean - (risk_free_rate / annual_factor)) / downside_std * np.sqrt(annual_factor)
        return sortino_ratio

    def calculate_max_drawdown(self, trades):
        returns = [trade.profit_loss for trade in trades if trade.profit_loss is not None]
        if not returns:
            return 0
        
        cumulative_returns = np.cumsum(returns)
        max_drawdown = 0
        peak = cumulative_returns[0]
        
        for value in cumulative_returns[1:]:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        return max_drawdown
    
    def calculate_win_loss_ratio(self, trades):
        wins = sum(1 for trade in trades if trade.profit_loss is not None and trade.profit_loss > 0)
        losses = sum(1 for trade in trades if trade.profit_loss is not None and trade.profit_loss <= 0)
        return wins / losses if losses > 0 else float('inf')

    def analyze(self, trades):
        if not trades:
            return {
                'total_trades': 0,
                'profitable_trades': 0,
                'win_rate': 0,
                'total_return': 0,
                'sharpe_ratio': -np.inf,
                'sortino_ratio': -np.inf,
                'max_drawdown': 0,
                'win_loss_ratio': 0
            }

        total_trades = len(trades)
        profitable_trades = sum(1 for trade in trades if trade.profit_loss is not None and trade.profit_loss > 0)
        win_rate = profitable_trades / total_trades if total_trades > 0 else 0

        returns = [trade.profit_loss for trade in trades if trade.profit_loss is not None]
        total_return = sum(returns)
        
        performance = {
            'total_trades': total_trades,
            'profitable_trades': profitable_trades,
            'win_rate': round(win_rate, 3),
            'total_return': round(total_return, 2),
            'sharpe_ratio': round(self.calculate_sharpe_ratio(trades),3),
            'sortino_ratio': round(self.calculate_sortino_ratio(trades),3),
            'max_drawdown': round(self.calculate_max_drawdown(trades),3),
            'win_loss_ratio': round(self.calculate_win_loss_ratio(trades),3)
        }
        
        return performance
