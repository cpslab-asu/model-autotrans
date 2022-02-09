from enum import Enum, IntEnum, auto, unique

from transitions import Machine, EventData


@unique
class Gear(IntEnum):
    FIRST = 1
    SECOND = 2
    THIRD = 3
    FOURTH = 4


def _up_shift_threshold(gear: Gear, vehicle_speed: float) -> float:
    ...


def _down_shift_threshold(gear: Gear, vehicle_speed: float) -> float:
    ...


def should_shift_up(event: EventData) -> bool:
    throttle = event.kwargs.get("throttle")
    current_gear = event.kwargs.get("current_gear")
    threshold = _up_shift_threshold(current_gear, throttle)

    return event.kwargs.get("vehicle_speed") >= threshold


def should_shift_down(event: EventData) -> bool:
    throttle = event.kwargs.get("throttle")
    current_gear = event.kwargs.get("current_gear")
    threshold = _down_shift_threshold(current_gear, throttle)

    return event.kwargs.get("vehicle_speed") <= threshold


def should_not_shift(event: EventData) -> bool:
    throttle = event.kwargs.get("throttle")
    current_gear = event.kwargs.get("current_gear")
    lo_threshold = _down_shift_threshold(current_gear, throttle)
    hi_threshold = _up_shift_threshold(current_gear, throttle)

    return lo_threshold <= event.kwargs.get("vehicle_speed") <= hi_threshold


@unique
class SelectionState(Enum):
    STEADY_STATE = auto(),
    UP_SHIFTING = auto(),
    DOWN_SHIFTING = auto()


class SelectionStateModel:
    def __init__(self, t_step_ms: int, t_wait_ms: int):
        self.timer = 0
        self.t_step_ms = t_step_ms
        self.t_wait_ms = t_wait_ms

    def reset_timer(self, _: EventData):
        self.timer = 0

    def increment_timer(self, _: EventData):
        self.timer += self.t_step_ms

    def shift_duration_met(self, _: EventData) -> bool:
        return self.timer >= self.t_wait_ms


class ShiftLogic:
    def __init__(self, t_step_ms: int = 10, t_wait_ms: int = 50):
        gear_state_states = [gear for gear in Gear]
        gear_state_transitions = [
            {"trigger": "shift_up", "source": Gear.FIRST, "dest": Gear.SECOND},
            {"trigger": "shift_up", "source": Gear.SECOND, "dest": Gear.THIRD},
            {"trigger": "shift_up", "source": Gear.THIRD, "dest": Gear.FOURTH},
            {"trigger": "shift_down", "source": Gear.FOURTH, "dest": Gear.THIRD},
            {"trigger": "shift_down", "source": Gear.THIRD, "dest": Gear.SECOND},
            {"trigger": "shift_down", "source": Gear.SECOND, "dest": Gear.FIRST},
        ]
        self._gear_state = Machine(states=gear_state_states, transitions=gear_state_transitions, initial=Gear.FIRST)

        selection_state_model = SelectionStateModel(t_step_ms, t_wait_ms)
        selection_state_states = [state for state in SelectionState]
        selection_state_transitions = [
            {
                "trigger": "step",
                "source": SelectionState.STEADY_STATE,
                "dest": SelectionState.UP_SHIFTING,
                "condition": [should_shift_up],
                "after": [selection_state_model.reset_timer]
            },
            {
                "trigger": "step",
                "source": SelectionState.STEADY_STATE,
                "dest": SelectionState.DOWN_SHIFTING,
                "condition": [should_shift_down],
                "after": [selection_state_model.reset_timer]
            },
            {
                "trigger": "step",
                "source": [SelectionState.UP_SHIFTING, SelectionState.DOWN_SHIFTING],
                "dest": SelectionState.STEADY_STATE,
                "condition": [should_not_shift]
            },
            {
                "trigger": "step",
                "source": SelectionState.UP_SHIFTING,
                "dest": None,
                "condition": [should_shift_up],
                "after": [selection_state_model.increment_timer]
            },
            {
                "trigger": "step",
                "source": SelectionState.DOWN_SHIFTING,
                "dest": None,
                "condition": [should_shift_down],
                "after": [selection_state_model.increment_timer],
            },
            {
                "trigger": "step",
                "source": SelectionState.UP_SHIFTING,
                "dest": SelectionState.STEADY_STATE,
                "condition": [should_shift_up, selection_state_model.shift_duration_met],
                "after": [self._gear_state.shift_up]
            },
            {
                "trigger": "step",
                "source": SelectionState.DOWN_SHIFTING,
                "dest": SelectionState.STEADY_STATE,
                "condition": [should_shift_down, selection_state_model.shift_duration_met],
                "after": [self._gear_state.shift_down]
            }
        ]
        self._selection_state = Machine(
            model=selection_state_model,
            states=selection_state_states,
            transitions=selection_state_transitions,
            inital=SelectionState.STEADY_STATE,
            send_event=True
        )

    @property
    def current_gear(self) -> Gear:
        return self._gear_state.state

    def step(self, throttle: float, vehicle_speed: float):
        self._selection_state.step(throttle=throttle, vehicle_speed=vehicle_speed, current_gear=self.current_gear)
