import numpy as np
from deap import base, creator, tools, algorithms
from .optimizer import Optimizer
from .utils import clamp_value, sample_value

# Ensure classes are created only once
if not hasattr(creator, "FitnessMax"):
    creator.create("FitnessMax", base.Fitness, weights=(1.0,))
if not hasattr(creator, "Individual"):
    creator.create("Individual", list, fitness=creator.FitnessMax)

class GeneticAlgorithmOptimizer(Optimizer):
    def optimize(self, objective_function, param_ranges, n_iterations):
        toolbox = base.Toolbox()
        for i, param in enumerate(param_ranges):
            toolbox.register(f"attr_{i}", sample_value, param)

        toolbox.register("individual", tools.initCycle, creator.Individual,
                         [getattr(toolbox, f"attr_{i}") for i in range(len(param_ranges))], n=1)
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)

        def evaluate(individual):
            params = [clamp_value(val, param) for val, param in zip(individual, param_ranges)]
            result = objective_function(params)
            return (result,)

        toolbox.register("evaluate", evaluate)
        toolbox.register("mate", tools.cxBlend, alpha=0.5)
        def mutate_and_bound(individual):
            tools.mutGaussian(individual, mu=0, sigma=1, indpb=0.2)
            for i, param in enumerate(param_ranges):
                individual[i] = clamp_value(individual[i], param)
            return (individual,)

        toolbox.register("mutate", mutate_and_bound)
        toolbox.register("select", tools.selTournament, tournsize=3)

        population = toolbox.population(n=50)
        result, _ = algorithms.eaSimple(population, toolbox, cxpb=0.7, mutpb=0.2, ngen=n_iterations, verbose=False)

        best_individual = tools.selBest(result, k=1)[0]
        return [clamp_value(val, param) for val, param in zip(best_individual, param_ranges)]
