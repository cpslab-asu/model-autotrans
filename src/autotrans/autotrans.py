from collections.abc import Sequence as Seq
from dataclasses import dataclass

from .engine import Engine
from .shift_logic import ShiftLogic, Gear
from .transmission import Transmission
from .vehicle import Vehicle


@dataclass(frozen=True)
class EngineParameters:
    engine_propeller_inertia: float
    initial_rpm: float


@dataclass(frozen=True)
class ShiftLogicParameters:
    initial_gear: Gear
    wait_ticks: int


@dataclass(frozen=True)
class VehicleParameters:
    drag_coefficient: float
    final_drive_ratio: float
    inertia: float
    initial_speed: float
    wheel_friction: float
    wheel_radius: float


@dataclass(frozen=True)
class AutotransParameters:
    step_size_ms: int
    engine: EngineParameters
    shift_logic: ShiftLogicParameters
    vehicle: VehicleParameters

    def __post_init__(self):
        assert isinstance(self.step_size_ms, int)
        assert self.step_size_ms > 0


@dataclass(frozen=True)
class AutotransState:
    impeller_torque: float
    output_torque: float
    vehicle_speed: float
    transmission_rpm: float
    engine_rpm: float
    gear: Gear


class Autotrans:
    def __init__(self, parameters: AutotransParameters):
        self._time = 0
        self._step_size = parameters.step_size_ms
        self._engine = Engine(
            parameters.step_size_ms,
            parameters.engine.engine_propeller_inertia,
            parameters.engine.initial_rpm,
        )
        self._shift_logic = ShiftLogic(
            parameters.shift_logic.wait_ticks, parameters.shift_logic.initial_gear
        )
        self._transmission = Transmission()
        self._vehicle = Vehicle(
            parameters.step_size_ms,
            parameters.vehicle.drag_coefficient,
            parameters.vehicle.final_drive_ratio,
            parameters.vehicle.inertia,
            parameters.vehicle.initial_speed,
            parameters.vehicle.wheel_friction,
            parameters.vehicle.wheel_radius,
        )

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
        self._time = self._time + self._step_size

    @property
    def time_ms(self) -> int:
        return self._time

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


def simulate(throttle_signal: Seq[float], brake_signal: Seq[float], model: Autotrans) -> list[TimedState]:
    assert len(throttle_signal) == len(brake_signal)

    trajectory: list[TimedState] = []

    for (throttle_value, brake_value) in zip(throttle_signal, brake_signal):
        timed_state = (model.time_ms, model.state)
        trajectory.append(timed_state)
        model.step(throttle_value, brake_value)

    return trajectory
