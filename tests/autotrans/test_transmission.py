import h5py
import pytest

from autotrans.transmission import Transmission


def test_transmission(test_data: h5py.File):
    transmission_rpm_trace = test_data["transmission_rpm"]
    engine_rpm_trace = test_data["engine_rpm"]
    gear_trace = test_data["gear"]
    output_torque_trace = test_data["output_torque"]
    impeller_torque_trace = test_data["impeller_torque"]

    model = Transmission()
    inputs = zip(
        engine_rpm_trace,
        gear_trace,
        transmission_rpm_trace,
        output_torque_trace,
        impeller_torque_trace
    )

    for engine_rpm, gear, transmission_rpm, output_torque, impeller_torque in inputs:
        model.step(engine_rpm, gear, transmission_rpm)

        assert model.output_torque == pytest.approx(output_torque, abs=1.0e-3)
        assert model.impeller_torque == pytest.approx(impeller_torque, abs=1.0e-3)
