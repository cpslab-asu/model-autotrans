from h5py import File as H5File

from autotrans.vehicle import Vehicle


def test_vehicle(test_data: H5File):
    vehicle_speed_trace = test_data["vehicle_speed"]
    transmission_rpm_trace = test_data["transmission_rpm"]
    brake_trace = test_data["brake_torque"]
    output_torque_trace = test_data["output_torque"]
    model = Vehicle(
        t_step_ms=40,
        final_drive_ratio=3.23,
        co_friction=40,
        co_drag=0.02,
        wheel_radius=1,
        inertia=12.0941,
        initial_speed=0,
    )
    inputs = zip(output_torque_trace, brake_trace)
    output_rpm = []
    output_mph = []

    for output_torque, brake in inputs:
        output_rpm.append(model.transmission_rpm)
        output_mph.append(model.speed)

        model.step(output_torque, brake)

    assert output_rpm == list(vehicle_speed_trace)
    assert output_mph == list(transmission_rpm_trace)
