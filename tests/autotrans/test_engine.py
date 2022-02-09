import os.path as path

import h5py
import numpy as np
import numpy.testing
import pytest

import autotrans.engine as engine

INERTIA = 0.021991488283555904


@pytest.fixture
def trace_data() -> h5py.File:
    return h5py.File(path.join(path.dirname(__file__), "test_data.h5"))


def test_engine_step(trace_data: h5py.File):
    engine_rpm = trace_data["engine_rpm"]
    throttle = trace_data["throttle"]
    impeller_torque = trace_data["impeller_torque"]
    expected_output = engine_rpm[1]

    model = engine.Engine(
        time_step_ms=40,
        engine_propeller_inertia=INERTIA,
        initial_rpm=engine_rpm[0]
    )
    model.step(throttle=throttle[0], impeller_torque=impeller_torque[0])

    assert model.rpm == expected_output


def test_engine_steps(trace_data: h5py.File):
    throttle_trace: h5py.Dataset = trace_data["throttle"]
    impeller_torque_trace: h5py.Dataset = trace_data["impeller_torque"]
    engine_rpm: h5py.Dataset = trace_data["engine_rpm"]
    model = engine.Engine(
        time_step_ms=40,
        engine_propeller_inertia=INERTIA,
        initial_rpm=engine_rpm[0],
    )
    output = []

    for throttle, impeller_torque in zip(throttle_trace, impeller_torque_trace):
        output.append(model.rpm)
        model.step(throttle, impeller_torque)

    assert np.testing.assert_equal(output, engine_rpm)
