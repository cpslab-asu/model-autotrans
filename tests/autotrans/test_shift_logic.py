from os import path
from pprint import pprint

import h5py
import numpy as np
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


def test_shift_logic():
    test_data = h5py.File(path.join(path.dirname(__file__), "test_data.h5"))
    throttle_trace = test_data["throttle"]
    vehicle_speed_trace = test_data["vehicle_speed"]
    gear_trace = test_data["gear"]
    model = ShiftLogic(
        wait_ticks=2,
        initial_gear=Gear.FIRST,
        initial_throttle=throttle_trace[0],
        initial_speed=vehicle_speed_trace[0]
    )
    inputs = zip(throttle_trace, vehicle_speed_trace, gear_trace)
    output_trace = []

    for throttle, vehicle_speed, gear in inputs:
        output_trace.append(model.current_gear)
        model.step(throttle, vehicle_speed)
        # assert model.current_gear == gear

    times = np.linspace(start=0, stop=30, num=len(output_trace), endpoint=True)
    print()
    pprint(list(zip(times, output_trace, gear_trace)), width=120)
