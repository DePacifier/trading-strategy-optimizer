from pyswarm import pso
import numpy as np
from .optimizer import Optimizer

class ParticleSwarmOptimizer(Optimizer):
    def optimize(self, objective_function, param_ranges, n_iterations, initial_guess=None):
        lb = [low for low, _ in param_ranges]
        ub = [high for _, high in param_ranges]

        def pso_objective(x):
            return -objective_function(
                [int(val) if param['type'] == 'int' else val for val, param in zip(x, param_ranges)]
            )  # PSO minimizes, so negate

        # NOTE: pyswarm's `pso` does not support setting an initial population.
        #       For now we simply ignore `initial_guess` if provided.
        xopt, _ = pso(pso_objective, lb, ub, swarmsize=10, maxiter=n_iterations, debug=False)

        print("XOPT result\n", xopt)
        return [int(val) if param['type'] == 'int' else val for val, param in zip(xopt, param_ranges)]
