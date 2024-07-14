# import numpy as np
# from deap import base, creator, tools, algorithms
# from .optimizer import Optimizer

# class GeneticAlgorithmOptimizer(Optimizer):
#     def optimize(self, objective_function, param_ranges, n_iterations):
#         creator.create("FitnessMax", base.Fitness, weights=(1.0,))
#         creator.create("Individual", list, fitness=creator.FitnessMax)

#         toolbox = base.Toolbox()
#         for i, (low, high) in enumerate(param_ranges):
#             toolbox.register(f"attr_{i}", np.random.uniform, low, high)

#         toolbox.register("individual", tools.initCycle, creator.Individual,
#                          [getattr(toolbox, f"attr_{i}") for i in range(len(param_ranges))], n=1)
#         toolbox.register("population", tools.initRepeat, list, toolbox.individual)

#         toolbox.register("evaluate", objective_function)
#         toolbox.register("mate", tools.cxBlend, alpha=0.5)
#         toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=1, indpb=0.2)
#         toolbox.register("select", tools.selTournament, tournsize=3)

#         population = toolbox.population(n=50)
#         result, _ = algorithms.eaSimple(population, toolbox, cxpb=0.7, mutpb=0.2, ngen=n_iterations, verbose=False)

#         best_individual = tools.selBest(result, k=1)[0]
#         return best_individual
import numpy as np
from deap import base, creator, tools, algorithms
from .optimizer import Optimizer

# Ensure classes are created only once
if not hasattr(creator, "FitnessMax"):
    creator.create("FitnessMax", base.Fitness, weights=(1.0,))
if not hasattr(creator, "Individual"):
    creator.create("Individual", list, fitness=creator.FitnessMax)

class GeneticAlgorithmOptimizer(Optimizer):
    def optimize(self, objective_function, param_ranges, n_iterations):
        toolbox = base.Toolbox()
        for i, (low, high) in enumerate(param_ranges):
            toolbox.register(f"attr_{i}", np.random.uniform, low, high)

        toolbox.register("individual", tools.initCycle, creator.Individual,
                         [getattr(toolbox, f"attr_{i}") for i in range(len(param_ranges))], n=1)
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)

        # Ensure the objective function returns a tuple
        def evaluate(individual):
            individual = [int(param) if isinstance(param, float) else param for param in individual]
            result = objective_function(individual)
            return (result,)

        toolbox.register("evaluate", evaluate)
        toolbox.register("mate", tools.cxBlend, alpha=0.5)
        toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=1, indpb=0.2)
        toolbox.register("select", tools.selTournament, tournsize=3)

        population = toolbox.population(n=50)
        result, _ = algorithms.eaSimple(population, toolbox, cxpb=0.7, mutpb=0.2, ngen=n_iterations, verbose=False)

        best_individual = tools.selBest(result, k=1)[0]
        return best_individual