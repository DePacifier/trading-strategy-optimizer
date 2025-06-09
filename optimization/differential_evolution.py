from scipy.optimize import differential_evolution
from .optimizer import Optimizer
import numpy as np

class DifferentialEvolutionOptimizer(Optimizer):
    def optimize(self, objective_function, param_ranges, n_iterations, initial_guess=None):
        bounds = [(param['low'], param['high']) for param in param_ranges]

        def wrapper(x):
            params = [int(val) if param['type'] == 'int' else val for val, param in zip(x, param_ranges)]
            return objective_function(params)

        kwargs = {'maxiter': n_iterations, 'strategy': 'best1bin'}
        if initial_guess is not None:
            ig = np.atleast_2d(initial_guess)
            if ig.shape[0] < 5:
                ig = np.vstack([ig] * 5)
            kwargs['init'] = ig

        result = differential_evolution(wrapper, bounds, **kwargs)

        return [int(val) if param['type'] == 'int' else val for val, param in zip(result.x, param_ranges)]