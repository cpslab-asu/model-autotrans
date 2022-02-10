import h5py
import pytest

from autotrans.shift_logic import ShiftLogic, Gear, up_shift_threshold, down_shift_threshold


def test_upshift_threshold():
    threshold_0s = up_shift_threshold(Gear.FIRST, throttle=59.9463087248322)
    threshold_5s = up_shift_threshold(Gear.THIRD, throttle=53.2885906040268)

    assert threshold_0s == pytest.approx(27.2271812080537, abs=1e-3)
    assert threshold_5s == pytest.approx(63.2885906040268, abs=1e-3)


def test_downshift_threshold():
    threshold_0s = down_shift_threshold(Gear.FIRST, throttle=59.9463087248322)
    threshold_5s = down_shift_threshold(Gear.THIRD, throttle=53.2885906040268)

    assert threshold_0s == 0
    assert threshold_5s == pytest.approx(31.6442953020134, abs=1e-3)


def test_shift_logic(test_data: h5py.File):
    throttle_trace = test_data["throttle"]
    vehicle_speed_trace = test_data["vehicle_speed"]
    gear_trace = test_data["gear"]
    model = ShiftLogic(wait_ticks=2, initial_gear=Gear.FIRST)
    inputs = zip(throttle_trace[0:750], vehicle_speed_trace[0:750])
    outputs = []

    for throttle, vehicle_speed in inputs:
        model.step(throttle, vehicle_speed)
        outputs.append(model.current_gear)

    outputs.append(model.current_gear)

    assert outputs == list(gear_trace)
