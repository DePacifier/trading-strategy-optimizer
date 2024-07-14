from scipy.optimize import differential_evolution
from .optimizer import Optimizer

class DifferentialEvolutionOptimizer(Optimizer):
    def optimize(self, objective_function, param_ranges, n_iterations, initial_guess=None):
        bounds = [(low, high) for low, high in param_ranges]

        result = differential_evolution(
            objective_function, bounds, maxiter=n_iterations, init=initial_guess, strategy='best1bin'
        )

        return result.x