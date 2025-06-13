import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import pytest
from optimization.utils import clamp_value, sample_value


def test_clamp_value_invalid_step_zero():
    spec = {'low': 0, 'high': 10, 'type': 'int', 'step': 0}
    with pytest.raises(ValueError):
        clamp_value(5, spec)


def test_clamp_value_invalid_step_negative():
    spec = {'low': 0, 'high': 10, 'type': 'int', 'step': -1}
    with pytest.raises(ValueError):
        clamp_value(5, spec)


def test_sample_value_invalid_step_zero():
    spec = {'low': 0, 'high': 10, 'type': 'int', 'step': 0}
    with pytest.raises(ValueError):
        sample_value(spec)


def test_sample_value_invalid_step_negative():
    spec = {'low': 0, 'high': 10, 'type': 'int', 'step': -1}
    with pytest.raises(ValueError):
        sample_value(spec)


def test_float_rounding_in_clamp_and_sample():
    spec = {'low': 0.0, 'high': 1.0, 'type': 'float'}
    val = clamp_value(0.123456, spec)
    assert val == 0.12

    for _ in range(5):
        sv = sample_value(spec)
        assert abs(sv - round(sv, 2)) < 1e-9
