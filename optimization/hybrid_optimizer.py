import multiprocessing as mp
from .optimizer import Optimizer

class ParallelHybridOptimizer(Optimizer):
    def __init__(self, ga_optimizer, pso_optimizer, bayesian_optimizer, differential_optimizer, n_processes=None):
        self.ga_optimizer = ga_optimizer
        self.pso_optimizer = pso_optimizer
        self.bayesian_optimizer = bayesian_optimizer
        self.de_optimizer = differential_optimizer
        self.n_processes = n_processes or mp.cpu_count()

    def _best(self, results, objective_function):
        """Return the best parameter set based on the objective function."""
        scored = [(objective_function(r), r) for r in results]
        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[0][1]

    def optimize(self, objective_function, param_ranges, n_iterations):
        with mp.Pool(processes=self.n_processes) as pool:
            phase_iters = max(1, n_iterations // 4)

            # ---- Genetic Algorithm ----
            ga_args = (objective_function, param_ranges, phase_iters)
            ga_results = pool.starmap(self.ga_optimizer.optimize, [ga_args] * self.n_processes)
            ga_best = self._best(ga_results, objective_function)

            # ---- Particle Swarm ----
            pso_args = (objective_function, param_ranges, phase_iters, ga_best)
            pso_results = pool.starmap(self.pso_optimizer.optimize, [pso_args] * self.n_processes)
            pso_best = self._best(pso_results, objective_function)

            # ---- Differential Evolution ----
            de_args = (objective_function, param_ranges, phase_iters, pso_best)
            de_results = pool.starmap(self.de_optimizer.optimize, [de_args] * self.n_processes)
            de_best = self._best(de_results, objective_function)

            # ---- Bayesian Optimization ----
            bayes_iters = max(6, phase_iters)
            bayes_args = (objective_function, param_ranges, bayes_iters, de_best)
            bayes_results = pool.starmap(self.bayesian_optimizer.optimize, [bayes_args] * self.n_processes)
            final_best = self._best(bayes_results, objective_function)

        # Select the overall best result from each phase
        all_best = [ga_best, pso_best, de_best, final_best]
        scored = [(objective_function(r), r) for r in all_best]
        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[0][1]
