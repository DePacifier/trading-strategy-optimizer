import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import random
import math
import numpy as np
from optimization.genetic_algorithm import GeneticAlgorithmOptimizer
from optimization.differential_evolution import DifferentialEvolutionOptimizer
from optimization.particle_swarm import ParticleSwarmOptimizer
from optimization.bayesian_optimization import BayesianOptimizer
from optimization.hybrid_optimizer import ParallelHybridOptimizer
from optimization.utils import decode_value

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
    assert param_ranges[0]['low'] <= result[0] <= param_ranges[0]['high']

def test_differential_evolution_optimizer():
    np.random.seed(0)
    de = DifferentialEvolutionOptimizer()
    result = de.optimize(lambda p: (p[0] - 3) ** 2, param_ranges, n_iterations=5)
    assert abs(result[0] - 3) < 1
    assert param_ranges[0]['low'] <= result[0] <= param_ranges[0]['high']


def test_particle_swarm_optimizer():
    np.random.seed(0)
    pso = ParticleSwarmOptimizer()
    result = pso.optimize(quadratic_objective, param_ranges, n_iterations=5)
    assert abs(result[0] - 3) < 1
    assert param_ranges[0]['low'] <= result[0] <= param_ranges[0]['high']


def test_bayesian_optimizer():
    np.random.seed(0)
    bo = BayesianOptimizer()
    result = bo.optimize(quadratic_objective, param_ranges, n_iterations=5)
    assert abs(result[0] - 3) < 1
    assert param_ranges[0]['low'] <= result[0] <= param_ranges[0]['high']


def test_parallel_hybrid_optimizer():
    np.random.seed(0)
    ga = GeneticAlgorithmOptimizer()
    pso = ParticleSwarmOptimizer()
    bo = BayesianOptimizer()
    de = DifferentialEvolutionOptimizer()
    pho = ParallelHybridOptimizer(ga, pso, bo, de, n_processes=2)
    result = pho.optimize(quadratic_objective, param_ranges, n_iterations=8)
    assert abs(result[0] - 3) < 1.5
    assert param_ranges[0]['low'] <= result[0] <= param_ranges[0]['high']


def test_parameter_step_handling():
    np.random.seed(0)
    ga = GeneticAlgorithmOptimizer()
    step_ranges = [{'low': 0, 'high': 6, 'type': 'int', 'step': 2}]
    result = ga.optimize(lambda p: -(p[0] - 4) ** 2, step_ranges, n_iterations=4)
    assert (result[0] - step_ranges[0]['low']) % 2 == 0


def test_float_parameter_step_handling():
    np.random.seed(0)
    ga = GeneticAlgorithmOptimizer()
    step_ranges = [{'low': 0.0, 'high': 1.0, 'type': 'float', 'step': 0.25}]
    result = ga.optimize(lambda p: -(p[0] - 0.75) ** 2, step_ranges, n_iterations=4)
    mod = (result[0] - step_ranges[0]['low']) % 0.25
    assert math.isclose(mod, 0.0, abs_tol=1e-8)


def test_list_parameter_handling():
    np.random.seed(0)
    ga = GeneticAlgorithmOptimizer()
    spec = {'type': 'list', 'values': [0, 5, 10]}

    def obj(params):
        val = decode_value(params[0], spec)
        return -(val - 5) ** 2

    result = ga.optimize(obj, [spec], n_iterations=4)
    decoded = decode_value(result[0], spec)
    assert decoded in spec['values']

