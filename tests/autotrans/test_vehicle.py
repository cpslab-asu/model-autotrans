import h5py
import pytest

from autotrans.vehicle import Vehicle


@pytest.fixture
def vehicle_model() -> Vehicle:
    return Vehicle(
        t_step_ms=40,
        final_drive_ratio=3.23,
        wheel_friction=40,
        co_drag=0.02,
        wheel_radius=1,
        inertia=12.0941,
        initial_speed=0,
    )


def test_vehicle_transmission_rpm(test_data: h5py.File, vehicle_model: Vehicle):
    transmission_rpm_trace = test_data["transmission_rpm"]
    brake_trace = test_data["brake_torque"]
    output_torque_trace = test_data["output_torque"]
    inputs = zip(output_torque_trace, brake_trace)
    output_rpm = []

    for output_torque, brake in inputs:
        output_rpm.append(vehicle_model.transmission_rpm)
        vehicle_model.step(output_torque, brake)

    assert output_rpm == list(transmission_rpm_trace)


def test_vehicle_output_speed(test_data: h5py.File, vehicle_model: Vehicle):
    vehicle_speed_trace = test_data["vehicle_speed"]
    brake_torque_trace = test_data["brake_torque"]
    output_torque_trace = test_data["output_torque"]
    inputs = zip(output_torque_trace, brake_torque_trace)
    output_mph = []

    for output_torque, brake_torque in inputs:
        output_mph.append(vehicle_model.speed)
        vehicle_model.step(output_torque, brake_torque)

    assert output_mph == list(vehicle_speed_trace)
