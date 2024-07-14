from abc import ABC, abstractmethod

class Optimizer(ABC):
    @abstractmethod
    def optimize(self, objective_function, param_ranges, n_iterations):
        pass