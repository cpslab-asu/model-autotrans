from .shift_logic import Gear


class Transmission:
    GEAR_RATIOS = {
        Gear.FIRST: 2.393,
        Gear.SECOND: 1.450,
        Gear.THIRD: 1.000,
        Gear.FOURTH: 0.667
    }

    def __init__(self):
        self._impeller_torque = 0.0
        self._output_torque = 0.0
        self._n_in = 0.0

    def _torque_converter(self, engine_rpm: float, n_in: float) -> tuple[float, float]:
        ...

    def _transmission_ratio(self, turbine_torque: float, gear: Gear, transmission_rpm: float) -> tuple[float, float]:
        ...

    def step(self, engine_rpm: float, gear: Gear, transmission_rpm: float):
        self._impeller_torque, turbine_torque = self._torque_converter(engine_rpm, self._n_in)
        self._output_torque, self._n_in = self._transmission_ratio(turbine_torque, gear, transmission_rpm)

    @property
    def impeller_torque(self) -> float:
        return self._impeller_torque

    @property
    def output_torque(self) -> float:
        return self._output_torque
