from abc import ABC, abstractmethod

class Strategy(ABC):
    def __init__(self, stop_loss_pct, take_profit_pct):
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct

    @abstractmethod
    def generate_signals(self, data):
        pass