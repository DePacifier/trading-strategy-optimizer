import os, sys
import pytest
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from trading_system_controller import TradingSystemController


def test_set_objectives_dict():
    controller = TradingSystemController(None, None, None, None)
    controller.set_objectives({'total_return': 70, 'sharpe_ratio': 30})
    assert controller.objectives == ['total_return', 'sharpe_ratio']
    assert abs(sum(controller.objective_weights.values()) - 1.0) < 1e-6
    assert controller.objective_weights['total_return'] == pytest.approx(0.7)
    assert controller.objective_weights['sharpe_ratio'] == pytest.approx(0.3)

