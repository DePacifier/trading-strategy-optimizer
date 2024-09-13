from utils.enums import Position, TradeAction

class Trade:
    def __init__(self, entry_time, entry_price, position, stop_loss, take_profit, size):
        self.entry_time = entry_time
        self.entry_price = entry_price
        self.position = position
        self.exit_time = None
        self.exit_price = None
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.size = size

    @property
    def profit_loss(self):
        if self.exit_price is None:
            return None
        return (self.exit_price - self.entry_price) * self.position.value * self.size
    
    def get_data(self) -> dict:
        return {
            "entry_time": str(self.entry_time),
            "entry_price": self.entry_price,
            "position": self.position.value,
            "exit_time": str(self.exit_time),
            "exit_price": self.exit_price,
            "stop_loss": self.stop_loss,
            "take_profit": self.take_profit,
            "size": self.size
        }

class StrategyManager:
    def __init__(self, data, initial_capital=100000, risk_per_trade=0.02):
        self.data = data
        self.current_position = Position.NEUTRAL
        self.trades = []
        self.initial_capital = initial_capital
        self.available_capital = initial_capital
        self.risk_per_trade = risk_per_trade

    def reset(self, data):
        self.data = data
        self.current_position = Position.NEUTRAL
        self.trades = []
        self.available_capital = self.initial_capital

    def execute_strategy(self, strategy):
        signals = strategy.generate_signals(self.data)
        for timestamp, signal in signals.items():
            # current_price = self.data.loc[timestamp, 'close']
            high_price = self.data.loc[timestamp, 'high']
            low_price = self.data.loc[timestamp, 'low']
            
            # Check for stop-loss or take-profit
            if self.current_position != Position.NEUTRAL:
                current_trade = self.trades[-1]
                if self.current_position == Position.LONG:
                    if low_price <= current_trade.stop_loss or high_price >= current_trade.take_profit:
                        self.exit_trade(timestamp)
                elif self.current_position == Position.SHORT:
                    if high_price >= current_trade.stop_loss or low_price <= current_trade.take_profit:
                        self.exit_trade(timestamp)

            # Process signal
            if signal == TradeAction.ENTER_LONG and self.current_position != Position.LONG:
                self.enter_trade(timestamp, Position.LONG, strategy.stop_loss_pct, strategy.take_profit_pct)
            elif signal == TradeAction.ENTER_SHORT and self.current_position != Position.SHORT:
                self.enter_trade(timestamp, Position.SHORT, strategy.stop_loss_pct, strategy.take_profit_pct)
            elif signal == TradeAction.EXIT and self.current_position != Position.NEUTRAL:
                self.exit_trade(timestamp)

    def enter_trade(self, timestamp, position, stop_loss_pct, take_profit_pct):
        if self.current_position != Position.NEUTRAL:
            self.exit_trade(timestamp)
        self.current_position = position
        entry_price = self.data.loc[timestamp, 'close']
        stop_loss = entry_price * (1 - stop_loss_pct) if position == Position.LONG else entry_price * (1 + stop_loss_pct)
        take_profit = entry_price * (1 + take_profit_pct) if position == Position.LONG else entry_price * (1 - take_profit_pct)
        size = self.risk_based_position_sizing(entry_price, stop_loss)
        self.trades.append(Trade(timestamp, entry_price, position, stop_loss, take_profit, size))

    def exit_trade(self, timestamp):
        if self.current_position == Position.NEUTRAL:
            return
        exit_price = self.data.loc[timestamp, 'close']
        self.trades[-1].exit_time = timestamp
        self.trades[-1].exit_price = exit_price
        self.current_position = Position.NEUTRAL
        
    def risk_based_position_sizing(self, entry_price, stop_loss_pct):
        risk_amount = self.available_capital * self.risk_per_trade
        position_size = risk_amount / stop_loss_pct
        max_position_size = self.available_capital / entry_price
        return min(position_size, max_position_size)