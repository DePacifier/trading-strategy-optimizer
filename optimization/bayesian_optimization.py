from skopt import gp_minimize
from skopt.utils import use_named_args
from skopt.space import Real, Integer
from .optimizer import Optimizer
import numpy as np

class BayesianOptimizer(Optimizer):
    def optimize(self, objective_function, param_ranges, n_iterations, initial_point=None):
        def bounded_objective(x):
            try:
                params = [int(val) if param['type'] == 'int' else val for val, param in zip(x, param_ranges)]
                result = -objective_function(params)  # sklearn minimizes, so we negate
                if np.isinf(result) or np.isnan(result):
                    return 1e10  # Return a large finite number instead of infinity
                return result
            except Exception:
                return 1e10  # Return a large finite number if there's an error

        # Convert param_ranges to the format expected by gp_minimize
        space = []
        for i, param in enumerate(param_ranges):
            if param['type'] == 'int':
                space.append(Integer(param['low'], param['high'], name=f'p{i}'))
            else:
                space.append(Real(param['low'], param['high'], name=f'p{i}'))

        @use_named_args(space)
        def wrapper(**params):
            return bounded_objective(list(params.values()))

        # Ensure initial_point is a list, not a numpy array
        if initial_point is not None:
            initial_point = list(initial_point)

        result = gp_minimize(wrapper, space, n_calls=n_iterations, x0=initial_point,
                             noise=1e-10, n_random_starts=5, 
                             acq_func='EI')  # Expected Improvement
        
        return [int(val) if param['type'] == 'int' else val for val, param in zip(result.x, param_ranges)]