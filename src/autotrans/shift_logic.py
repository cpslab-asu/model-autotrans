from enum import Enum, IntEnum, auto, unique
from typing import Protocol

import numpy as np
from transitions import Machine, EventData

from .lookup_table import LookupTable2D

GEAR_BREAKPOINTS = np.arange(1, 5)
UP_SHIFT_THROTTLE_BREAKPOINTS = np.array([0, 25, 35, 50, 90, 100], dtype=np.float64)
UP_SHIFT_VALUES = np.array([
    [10, 30, 50, 1000000],
    [10, 30, 50, 1000000],
    [15, 30, 50, 1000000],
    [23, 41, 60, 1000000],
    [40, 70, 100, 1000000],
    [40, 70, 100, 1000000],
], dtype=np.float64)
DOWN_SHIFT_THROTTLE_BREAKPOINTS = np.array([0, 5, 40, 50, 90, 100])
DOWN_SHIFT_VALUES = np.array([
    [0, 5, 20, 35],
    [0, 5, 20, 35],
    [0, 5, 25, 40],
    [0, 5, 30, 50],
    [0, 30, 50, 80],
    [0, 30, 50, 80],
])


@unique
class Gear(IntEnum):
    FIRST = 1
    SECOND = 2
    THIRD = 3
    FOURTH = 4


def up_shift_threshold(gear: Gear, throttle: float) -> float:
    table = LookupTable2D(UP_SHIFT_THROTTLE_BREAKPOINTS, GEAR_BREAKPOINTS, UP_SHIFT_VALUES)
    return table.lookup(throttle, gear)


def down_shift_threshold(gear: Gear, throttle: float) -> float:
    table = LookupTable2D(DOWN_SHIFT_THROTTLE_BREAKPOINTS, GEAR_BREAKPOINTS, DOWN_SHIFT_VALUES)
    return table.lookup(throttle, gear)


def should_shift_up(event: EventData) -> bool:
    throttle = event.kwargs.get("throttle")
    current_gear = event.kwargs.get("current_gear")
    threshold = up_shift_threshold(current_gear, throttle)

    return event.kwargs.get("vehicle_speed") >= threshold


def should_shift_down(event: EventData) -> bool:
    throttle = event.kwargs.get("throttle")
    current_gear = event.kwargs.get("current_gear")
    threshold = down_shift_threshold(current_gear, throttle)

    return event.kwargs.get("vehicle_speed") <= threshold


def should_not_shift(event: EventData) -> bool:
    throttle = event.kwargs.get("throttle")
    current_gear = event.kwargs.get("current_gear")
    lo_threshold = down_shift_threshold(current_gear, throttle)
    hi_threshold = up_shift_threshold(current_gear, throttle)

    return lo_threshold < event.kwargs.get("vehicle_speed") < hi_threshold


@unique
class SelectionState(Enum):
    STEADY_STATE = auto(),
    UP_SHIFTING = auto(),
    DOWN_SHIFTING = auto()


class StepMethod(Protocol):
    def __call__(self, *, throttle: float, vehicle_speed: float, current_gear: Gear):
        ...


class SelectionStateModel:
    step: StepMethod
    state: SelectionState

    def __init__(self, wait_ticks: int):
        self._counter = 0
        self._wait_ticks = wait_ticks

    def reset_counter(self, *_):
        self._counter = 0

    def increment_counter(self, *_):
        self._counter += 1

    def shift_duration_met(self, *_) -> bool:
        return self._counter >= self._wait_ticks

    def shift_duration_not_met(self, *_) -> bool:
        return self._counter < self._wait_ticks


class ShiftLogic:
    def __init__(self, wait_ticks: int, initial_gear: Gear):
        gear_state_states = [gear for gear in Gear]
        gear_state_transitions = [
            {"trigger": "shift_up", "source": Gear.FIRST, "dest": Gear.SECOND},
            {"trigger": "shift_up", "source": Gear.SECOND, "dest": Gear.THIRD},
            {"trigger": "shift_up", "source": Gear.THIRD, "dest": Gear.FOURTH},
            {"trigger": "shift_down", "source": Gear.FOURTH, "dest": Gear.THIRD},
            {"trigger": "shift_down", "source": Gear.THIRD, "dest": Gear.SECOND},
            {"trigger": "shift_down", "source": Gear.SECOND, "dest": Gear.FIRST},
        ]
        self._gear_state = Machine(
            states=gear_state_states,
            transitions=gear_state_transitions,
            initial=initial_gear
        )

        selection_state_model = SelectionStateModel(wait_ticks)
        selection_state_states = [state for state in SelectionState]
        selection_state_transitions = [
            {
                "trigger": "step",
                "source": SelectionState.STEADY_STATE,
                "dest": None,
                "conditions": [should_not_shift],
            },
            {
                "trigger": "step",
                "source": SelectionState.STEADY_STATE,
                "dest": SelectionState.UP_SHIFTING,
                "conditions": [should_shift_up],
                "after": [selection_state_model.increment_counter]
            },
            {
                "trigger": "step",
                "source": SelectionState.STEADY_STATE,
                "dest": SelectionState.DOWN_SHIFTING,
                "conditions": [should_shift_down],
                "after": [selection_state_model.increment_counter]
            },
            {
                "trigger": "step",
                "source": [SelectionState.UP_SHIFTING, SelectionState.DOWN_SHIFTING],
                "dest": SelectionState.STEADY_STATE,
                "conditions": [should_not_shift],
                "after": [selection_state_model.reset_counter]
            },
            {
                "trigger": "step",
                "source": SelectionState.UP_SHIFTING,
                "dest": None,
                "conditions": [should_shift_up, selection_state_model.shift_duration_not_met],
                "after": [selection_state_model.increment_counter]
            },
            {
                "trigger": "step",
                "source": SelectionState.DOWN_SHIFTING,
                "dest": None,
                "conditions": [should_shift_down, selection_state_model.shift_duration_not_met],
                "after": [selection_state_model.increment_counter],
            },
            {
                "trigger": "step",
                "source": SelectionState.UP_SHIFTING,
                "dest": SelectionState.STEADY_STATE,
                "conditions": [should_shift_up, selection_state_model.shift_duration_met],
                "after": [self._gear_state.shift_up, selection_state_model.reset_counter]
            },
            {
                "trigger": "step",
                "source": SelectionState.DOWN_SHIFTING,
                "dest": SelectionState.STEADY_STATE,
                "conditions": [should_shift_down, selection_state_model.shift_duration_met],
                "after": [self._gear_state.shift_down, selection_state_model.reset_counter]
            }
        ]
        self._selection_state = selection_state_model
        self._selection_state_machine = Machine(
            model=selection_state_model,
            states=selection_state_states,
            transitions=selection_state_transitions,
            initial=SelectionState.STEADY_STATE,
            send_event=True
        )

    @property
    def current_gear(self) -> Gear:
        return self._gear_state.state

    def step(self, throttle: float, vehicle_speed: float):
        self._selection_state.step(
            throttle=throttle,
            vehicle_speed=vehicle_speed,
            current_gear=self._gear_state.state
        )
