import numpy as np
import scipy.integrate as integrate


class Engine:
    THROTTLE_BREAKPOINTS = np.array([])
    RPM_BREAKPOINTS = np.array([])
    ENGINE_TORQUE_TABLE = np.array([[]])

    def __init__(self, time_step_ms: int, engine_propeller_inertia: float = 0.0, initial_rpm: float = 0.0):
        self._time_step = time_step_ms
        self._inertia = engine_propeller_inertia
        self._engine_rpm = initial_rpm

    def _compute_engine_torque(self, throttle: float):
        throttle_interpolator = lambda x: x
        rpm_interpolator = lambda x: x
        table_index = (throttle_interpolator(throttle), rpm_interpolator(self._engine_rpm))

        return self.ENGINE_TORQUE_TABLE[table_index]

    def _compute_rpm(self, throttle: float, impeller_torque: float) -> float:
        # Integrate EnginePlusImpellerInertia over time with saturation 600-6000
        engine_torque = self._compute_engine_torque(throttle)
        engine_propeller_inertia = (impeller_torque + engine_torque) / self._inertia

        return integrate.RK45(lambda _: 1, 0, engine_propeller_inertia)

    def step(self, throttle: float, impeller_torque: float):
        self._engine_rpm = self._compute_rpm(throttle, impeller_torque)

    @property
    def engine_rpm(self) -> float:
        return self._engine_rpm

