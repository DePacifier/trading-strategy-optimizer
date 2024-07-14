from utils.enums import Position, TradeAction

class Trade:
    def __init__(self, entry_time, entry_price, position, stop_loss, take_profit):
        self.entry_time = entry_time
        self.entry_price = entry_price
        self.position = position
        self.exit_time = None
        self.exit_price = None
        self.stop_loss = stop_loss
        self.take_profit = take_profit

    @property
    def profit_loss(self):
        if self.exit_price is None:
            return None
        return (self.exit_price - self.entry_price) * self.position.value

class StrategyManager:
    def __init__(self, data):
        self.data = data
        self.current_position = Position.NEUTRAL
        self.trades = []

    def reset(self, data):
        self.data = data
        self.current_position = Position.NEUTRAL
        self.trades = []

    def execute_strategy(self, strategy):
        signals = strategy.generate_signals(self.data)
        for timestamp, signal in signals.items():
            current_price = self.data.loc[timestamp, 'close']
            
            # Check for stop-loss or take-profit
            if self.current_position != Position.NEUTRAL:
                current_trade = self.trades[-1]
                if self.current_position == Position.LONG:
                    if current_price <= current_trade.stop_loss or current_price >= current_trade.take_profit:
                        self.exit_trade(timestamp)
                elif self.current_position == Position.SHORT:
                    if current_price >= current_trade.stop_loss or current_price <= current_trade.take_profit:
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
        self.trades.append(Trade(timestamp, entry_price, position, stop_loss, take_profit))

    def exit_trade(self, timestamp):
        if self.current_position == Position.NEUTRAL:
            return
        exit_price = self.data.loc[timestamp, 'close']
        self.trades[-1].exit_time = timestamp
        self.trades[-1].exit_price = exit_price
        self.current_position = Position.NEUTRAL