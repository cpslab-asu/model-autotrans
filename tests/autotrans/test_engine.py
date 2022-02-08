import os.path as path

import numpy as np
import numpy.testing
import scipy.io
from autotrans.engine import Engine


def test_engine_step():
    engine = Engine(time_step_ms=40, engine_propeller_inertia=1.0, initial_rpm=0.0)
    engine.step(throttle=0.35, impeller_torque=40.0)

    assert engine.rpm == 1.0


def trace_data():
    scipy.io.loadmat(path.join(path.dirname(__file__), "test_data.mat"))


def test_engine_steps():
    engine = Engine(time_step_ms=40, engine_propeller_inertia=1.0, initial_rpm=0.0)
    throttle_signal = np.array([])
    impeller_torque_signal = np.array([])
    expected_output = np.array([])
    output = []

    for throttle, impeller_torque in zip(throttle_signal, impeller_torque_signal):
        engine.step(throttle, impeller_torque)
        output.append(engine.rpm)

    assert np.testing.assert_equal(output, expected_output)
