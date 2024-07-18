import multiprocessing as mp
from .optimizer import Optimizer

class ParallelHybridOptimizer(Optimizer):
    def __init__(self, ga_optimizer, pso_optimizer, bayesian_optimizer, differential_optimizer, n_processes=None):
        self.ga_optimizer = ga_optimizer
        self.pso_optimizer = pso_optimizer
        self.bayesian_optimizer = bayesian_optimizer
        self.de_optimizer = differential_optimizer
        self.n_processes = n_processes or 20

    def optimize(self, objective_function, param_ranges, n_iterations):
        with mp.Pool(processes=self.n_processes) as pool:
            # Parallel GA optimization
            print("Started GA Optimization")
            ga_results = pool.starmap(self.ga_optimizer.optimize, 
                                      [(objective_function, param_ranges, n_iterations // 3)] * self.n_processes)
            ga_results.sort(key=objective_function, reverse=True)
            # ga_best = max(ga_results, key=objective_function)
            ga_best = ga_results[:5]
            print("Finished GA Optimization\nResult:\n", ga_best)

            # print("Finished GA Optimization\nResult:\n", ga_best)
            # # Convert the best GA result to an initial guess for PSO
            # initial_guess = [ga_best]
            
            # # Parallel PSO optimization
            # print("Started PSO Optimization")
            # pso_results = pool.starmap(self.pso_optimizer.optimize, 
            #                            [(objective_function, param_ranges, n_iterations // 3), initial_guess] * self.n_processes)
            # pso_best = max(pso_results, key=objective_function)
            # print("Finished PSO Optimization\nResult:\n", pso_best)
            
            # # Parallel Bayesian optimization
            # print("Started Bayesian Optimization")
            # bayesian_results = pool.starmap(self.bayesian_optimizer.optimize, 
            #                                 [(objective_function, param_ranges, n_iterations // 3, pso_best)] * self.n_processes)
            # final_best = max(bayesian_results, key=objective_function)
            # print("Finished Bayesian Optimization\nResult:\n", final_best)
            
            # Parallel DE optimization
            print("Started Differential Optimization")
            de_results = pool.starmap(self.de_optimizer.optimize, 
                                       [(objective_function, param_ranges, n_iterations // 3, ga_best)] * self.n_processes)
            de_best = max(de_results, key=objective_function)
            print("Finished Differential Optimization\nResult:\n", de_best)

            # Parallel Bayesian optimization
            print("Started Bayesian Optimization")
            bayesian_results = pool.starmap(self.bayesian_optimizer.optimize, 
                                            [(objective_function, param_ranges, n_iterations // 3, list(de_best))] * self.n_processes)
            final_best = max(bayesian_results, key=objective_function)
            print("Finished Bayesian Optimization\nResult:\n", final_best)

        return final_best