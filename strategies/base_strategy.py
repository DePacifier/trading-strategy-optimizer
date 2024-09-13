from abc import ABC, abstractmethod

class Strategy(ABC):
    def __init__(self, stop_loss_pct, take_profit_pct):
        self.stop_loss_pct = stop_loss_pct / 100
        self.take_profit_pct = take_profit_pct / 100

    @abstractmethod
    def generate_signals(self, data):
        pass