import h5py
import pytest

import autotrans.engine as engine

INERTIA = 0.021991488283555904


def test_engine_impeller_inertia(test_data: h5py.File):
    throttle_trace = test_data["throttle"]
    impeller_torque_trace = test_data["impeller_torque"]
    rpm_trace = test_data["engine_rpm"]
    engine_impeller_inertia = test_data["engine_impeller_inertia"]
    model = engine.Engine(
        time_step_ms=40,
        engine_propeller_inertia=INERTIA,
        initial_rpm=rpm_trace[0],
        initial_throttle=throttle_trace[0],
        initial_impeller_torque=impeller_torque_trace[0]
    )
    inputs = zip(throttle_trace, impeller_torque_trace, rpm_trace)
    outputs = []

    for throttle, impeller_torque, rpm in inputs:
        outputs.append(model.engine_impeller_inertia(throttle, impeller_torque, rpm))

    assert outputs == pytest.approx(list(engine_impeller_inertia), abs=0.0001)


def test_engine_rpm(test_data: h5py.File):
    throttle_trace = test_data["throttle"]
    impeller_torque_trace = test_data["impeller_torque"]
    engine_rpm = test_data["engine_rpm"]
    model = engine.Engine(
        time_step_ms=40,
        engine_propeller_inertia=INERTIA,
        initial_rpm=engine_rpm[0],
        initial_throttle=throttle_trace[0],
        initial_impeller_torque=impeller_torque_trace[0]
    )
    inputs = zip(throttle_trace[1:], impeller_torque_trace[1:])
    outputs = []

    for throttle, impeller_torque in inputs:
        outputs.append(model.rpm)
        model.step(throttle, impeller_torque)

    assert outputs == list(engine_rpm)
