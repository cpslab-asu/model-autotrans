import math

import numpy as np

from .shift_logic import Gear
from .lookup_table import LookupTable1D

K_FACTOR_VALUES = np.array([
    137.465208993806,
    137.065019156852,
    135.864449645989,
    135.664354727512,
    137.565256453045,
    140.366585311725,
    145.268910814415,
    152.872517716547,
    162.977311099644,
    164.277928069745,
    166.178829795278,
    167.979684061573,
    170.080680705583,
    172.781962105024,
    175.383196045227,
    179.585189333248,
    183.587087702791,
    189.890077634821,
    197.693779455430,
    215.902417036852,
    244.515990379085,
])
SPEED_RATIO = np.array([
    0.00,
    0.10,
    0.20,
    0.30,
    0.40,
    0.50,
    0.60,
    0.70,
    0.80,
    0.81,
    0.82,
    0.83,
    0.84,
    0.85,
    0.86,
    0.87,
    0.88,
    0.89,
    0.90,
    0.92,
    0.94,
])
TORQUE_VALUES = np.array([
    2.232,
    2.075,
    1.975,
    1.846,
    1.720,
    1.564,
    1.409,
    1.254,
    1.096,
    1.080,
    1.061,
    1.043,
    1.028,
    1.012,
    1.002,
    1.002,
    1.001,
    0.998,
    0.999,
    1.001,
    1.002,
])


class Transmission:
    GEAR_RATIOS = {
        Gear.FIRST: 2.393,
        Gear.SECOND: 1.450,
        Gear.THIRD: 1.000,
        Gear.FOURTH: 0.667
    }
    K_FACTOR_TABLE = LookupTable1D(SPEED_RATIO, K_FACTOR_VALUES)
    TORQUE_RATIO_TABLE = LookupTable1D(SPEED_RATIO, TORQUE_VALUES)

    def __init__(self):
        self._impeller_torque = 0.0
        self._output_torque = 0.0

    def _torque_converter(self, engine_rpm: float, n_in: float) -> tuple[float, float]:
        speed_ratio = n_in / engine_rpm
        k_factor = self.K_FACTOR_TABLE.lookup(speed_ratio)
        impeller_torque = math.pow(engine_rpm / k_factor, 2)
        torque_ratio = self.TORQUE_RATIO_TABLE.lookup(speed_ratio)
        turbine_torque = impeller_torque * torque_ratio

        return impeller_torque, turbine_torque

    def _internal_rpm(self, gear: Gear, transmission_rpm: float) -> float:
        return self.GEAR_RATIOS[gear] * transmission_rpm

    def _transmission_ratio(self, turbine_torque: float, gear: Gear,) -> float:
        return self.GEAR_RATIOS[gear] * turbine_torque

    def step(self, engine_rpm: float, gear: Gear, transmission_rpm: float):
        internal_rpm = self._internal_rpm(gear, transmission_rpm)
        self._impeller_torque, turbine_torque = self._torque_converter(engine_rpm, internal_rpm)
        self._output_torque = self._transmission_ratio(turbine_torque, gear)

    @property
    def impeller_torque(self) -> float:
        return self._impeller_torque

    @property
    def output_torque(self) -> float:
        return self._output_torque
