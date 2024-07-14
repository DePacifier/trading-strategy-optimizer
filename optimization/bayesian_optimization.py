# from skopt import gp_minimize
# from .optimizer import Optimizer

# class BayesianOptimizer(Optimizer):
#     def optimize(self, objective_function, param_ranges, n_iterations, initial_point=None):
#         def sklearn_objective(x):
#             return -objective_function(x)  # sklearn minimizes, so we negate
        
#         # Convert param_ranges to the format expected by gp_minimize
#         space = [(low, high) for low, high in param_ranges]

#         # Ensure initial_point is a list, not a numpy array
#         if initial_point is not None:
#             initial_point = list(initial_point)

#         result = gp_minimize(sklearn_objective, space, n_calls=n_iterations, x0=initial_point)
#         return result.x.tolist()
from skopt import gp_minimize
from skopt.utils import use_named_args
from skopt.space import Real
from .optimizer import Optimizer
import numpy as np

class BayesianOptimizer(Optimizer):
    def optimize(self, objective_function, param_ranges, n_iterations, initial_point=None):
        def bounded_objective(x):
            try:
                result = -objective_function(x)  # sklearn minimizes, so we negate
                if np.isinf(result) or np.isnan(result):
                    return 1e10  # Return a large finite number instead of infinity
                return result
            except Exception:
                return 1e10  # Return a large finite number if there's an error

        # Convert param_ranges to the format expected by gp_minimize
        space = [Real(low, high, name=f'p{i}') for i, (low, high) in enumerate(param_ranges)]

        @use_named_args(space)
        def wrapper(**params):
            return bounded_objective(list(params.values()))

        # Ensure initial_point is a list, not a numpy array
        if initial_point is not None:
            initial_point = list(initial_point)

        result = gp_minimize(wrapper, space, n_calls=n_iterations, x0=initial_point,
                             noise=1e-10, n_random_starts=5, 
                             acq_func='EI')  # Expected Improvement
        return result.x