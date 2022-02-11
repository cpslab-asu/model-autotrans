import h5py
import pytest

from autotrans.transmission import Transmission


def test_transmission_impeller_torque(test_data: h5py.File):
    transmission_rpm_trace = test_data["transmission_rpm"]
    engine_rpm_trace = test_data["engine_rpm"]
    gear_trace = test_data["gear"]
    impeller_torque_trace = test_data["impeller_torque"]

    model = Transmission()
    inputs = zip(engine_rpm_trace, gear_trace, transmission_rpm_trace)
    outputs = []

    for engine_rpm, gear, transmission_rpm in inputs:
        model.step(engine_rpm, gear, transmission_rpm)
        outputs.append(model.impeller_torque)

    assert outputs == pytest.approx(list(impeller_torque_trace), abs=1.0e-3)


def test_transmission_output_torque(test_data: h5py.File):
    transmission_rpm_trace = test_data["transmission_rpm"]
    engine_rpm_trace = test_data["engine_rpm"]
    gear_trace = test_data["gear"]
    output_torque_trace = test_data["output_torque"]

    model = Transmission()
    inputs = zip(engine_rpm_trace, gear_trace, transmission_rpm_trace)
    outputs = []

    for engine_rpm, gear, transmission_rpm in inputs:
        model.step(engine_rpm, gear, transmission_rpm)
        outputs.append(model.output_torque)

    assert outputs == pytest.approx(list(output_torque_trace), abs=1.0e-3)
