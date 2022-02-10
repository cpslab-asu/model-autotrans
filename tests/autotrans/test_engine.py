import h5py

import autotrans.engine as engine

INERTIA = 0.021991488283555904


def test_engine(test_data: h5py.File):
    throttle_trace = test_data["throttle"]
    impeller_torque_trace = test_data["impeller_torque"]
    engine_rpm = test_data["engine_rpm"]
    model = engine.Engine(
        time_step_ms=40,
        engine_propeller_inertia=INERTIA,
        initial_rpm=engine_rpm[0],
    )
    inputs = zip(throttle_trace, impeller_torque_trace, engine_rpm)

    for throttle, impeller_torque, engine_rpm in inputs:
        assert model.rpm == engine_rpm

        model.step(throttle, impeller_torque)
