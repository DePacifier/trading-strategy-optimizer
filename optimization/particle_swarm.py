from pyswarm import pso
from .optimizer import Optimizer
from .utils import clamp_value

class ParticleSwarmOptimizer(Optimizer):
    def optimize(self, objective_function, param_ranges, n_iterations, initial_guess=None):
        lb = [p['low'] for p in param_ranges]
        ub = [p['high'] for p in param_ranges]

        def pso_objective(x):
            params = [clamp_value(val, spec) for val, spec in zip(x, param_ranges)]
            return -objective_function(params)  # PSO minimizes, so negate

        # NOTE: pyswarm's `pso` does not support setting an initial population.
        #       For now we simply ignore `initial_guess` if provided.
        xopt, _ = pso(pso_objective, lb, ub, swarmsize=10, maxiter=n_iterations, debug=False)

        print("XOPT result\n", xopt)
        return [clamp_value(val, spec) for val, spec in zip(xopt, param_ranges)]
