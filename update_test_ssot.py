# -*- coding: utf-8 -*-
import sys, os
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.services.master_signal import BASE_WEIGHTS
from app.services.backtester import DEFAULT_WEIGHTS

def test_backtester_shares_engine_weights():
    assert dict(DEFAULT_WEIGHTS) == BASE_WEIGHTS
    assert abs(sum(BASE_WEIGHTS.values()) - 1.0) < 1e-12

def test_backtester_weights_are_immutable():
    try:
        DEFAULT_WEIGHTS["technical"] = 0.50
        assert False, "DEFAULT_WEIGHTS should be immutable!"
    except TypeError:
        pass  # Expected MappingProxyType TypeError

if __name__ == "__main__":
    test_backtester_shares_engine_weights()
    test_backtester_weights_are_immutable()
    print("test_backtester_shares_engine_weights PASSED")
    print("test_backtester_weights_are_immutable (MappingProxyType immutability) PASSED")
    print("\nALL WEIGHT SSOT TESTS PASSED WITH RETURNCODE 0!")
