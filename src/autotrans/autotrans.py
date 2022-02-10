from collections.abc import Sequence as Seq
from dataclasses import dataclass

from .engine import Engine
from .shift_logic import ShiftLogic, Gear
from .transmission import Transmission
from .vehicle import Vehicle


@dataclass(frozen=True)
class AutotransState:
    impeller_torque: float
    output_torque: float
    vehicle_speed: float
    transmission_rpm: float
    engine_rpm: float
    gear: Gear


class Autotrans:
    def __init__(self, step_size_ms: int):
        assert isinstance(step_size_ms, int)
        assert step_size_ms > 0

        self._step_size = step_size_ms
        self._engine = Engine()
        self._shift_logic = ShiftLogic()
        self._transmission = Transmission()
        self._vehicle = Vehicle()

    def step(self, throttle: float, brake: float):
        assert 0.0 <= throttle <= 1.0
        assert brake >= 0.0

        self._engine.step(self._transmission.impeller_torque, throttle)
        self._shift_logic.step(throttle, self._vehicle.speed)
        self._transmission.step(
            self._engine.rpm,
            self._shift_logic.current_gear,
            self._vehicle.transmission_rpm
        )
        self._vehicle.step(self._transmission.output_torque, brake)

    @property
    def state(self) -> AutotransState:
        return AutotransState(
            self._transmission.impeller_torque,
            self._transmission.output_torque,
            self._vehicle.speed,
            self._vehicle.transmission_rpm,
            self._engine.rpm,
            self._shift_logic.current_gear
        )


TimedState = tuple[int, AutotransState]


def simulate(step_size_ms: int, throttle_signal: Seq[float], brake_signal: Seq[float]) -> list[TimedState]:
    assert len(throttle_signal) == len(brake_signal)

    current_time = 0
    model = Autotrans(step_size_ms)
    trajectory: list[TimedState] = []

    for (throttle_value, brake_value) in zip(throttle_signal, brake_signal):
        timed_state = (current_time, model.state)
        current_time = current_time + step_size_ms

        model.step(throttle_value, brake_value)
        trajectory.append(timed_state)

    return trajectory
