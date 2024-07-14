from utils.enums import Position, TradeAction

class Trade:
    def __init__(self, entry_time, entry_price, position, exit_time=None, exit_price=None):
        self.entry_time = entry_time
        self.entry_price = entry_price
        self.position = position
        self.exit_time = exit_time
        self.exit_price = exit_price

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
            if signal == TradeAction.ENTER_LONG and self.current_position != Position.LONG:
                self.enter_trade(timestamp, Position.LONG)
            elif signal == TradeAction.ENTER_SHORT and self.current_position != Position.SHORT:
                self.enter_trade(timestamp, Position.SHORT)
            elif signal == TradeAction.EXIT and self.current_position != Position.NEUTRAL:
                self.exit_trade(timestamp)

    def enter_trade(self, timestamp, position):
        if self.current_position != Position.NEUTRAL:
            self.exit_trade(timestamp)
        self.current_position = position
        entry_price = self.data.loc[timestamp, 'close']
        self.trades.append(Trade(timestamp, entry_price, position))

    def exit_trade(self, timestamp):
        if self.current_position == Position.NEUTRAL:
            return
        exit_price = self.data.loc[timestamp, 'close']
        self.trades[-1].exit_time = timestamp
        self.trades[-1].exit_price = exit_price
        self.current_position = Position.NEUTRAL