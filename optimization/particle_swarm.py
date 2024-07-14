from pyswarm import pso
import numpy as np
from .optimizer import Optimizer

class ParticleSwarmOptimizer(Optimizer):
    def optimize(self, objective_function, param_ranges, n_iterations, initial_guess=None):
        lb = [low for low, _ in param_ranges]
        ub = [high for _, high in param_ranges]

        def pso_objective(x):
            return -objective_function(x)  # PSO minimizes, so we negate

        # Pre-process the initial population by setting one particle to the GA best result
        if initial_guess is not None:
            xopt, _ = pso(pso_objective, lb, ub, swarmsize=10, maxiter=n_iterations, debug=False)
            xopt = np.asarray(initial_guess)
        else:
            xopt, _ = pso(pso_objective, lb, ub, swarmsize=10, maxiter=n_iterations, debug=False)
            
        print("XOPT result\n", xopt)
        return xopt