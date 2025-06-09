import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import random
import numpy as np
from optimization.genetic_algorithm import GeneticAlgorithmOptimizer
from optimization.differential_evolution import DifferentialEvolutionOptimizer

# Simple quadratic objective with maximum at x=3
param_ranges = [{'low': 0, 'high': 5, 'type': 'float'}]

def quadratic_objective(params):
    x = params[0]
    return -(x - 3) ** 2

def test_genetic_algorithm_optimizer():
    random.seed(0)
    np.random.seed(0)
    ga = GeneticAlgorithmOptimizer()
    result = ga.optimize(quadratic_objective, param_ranges, n_iterations=5)
    assert abs(result[0] - 3) < 1

def test_differential_evolution_optimizer():
    np.random.seed(0)
    de = DifferentialEvolutionOptimizer()
    result = de.optimize(lambda p: (p[0] - 3) ** 2, param_ranges, n_iterations=5)
    assert abs(result[0] - 3) < 1
