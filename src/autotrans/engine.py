import numpy as np
import scipy.integrate as integrate
import scipy.interpolate as interpolate


class Engine:
    THROTTLE_BREAKPOINTS = np.array([])
    RPM_BREAKPOINTS = np.array([])
    ENGINE_TORQUE_TABLE = np.array([[]])

    def __init__(self, time_step_ms: int, engine_propeller_inertia: float = 0.0, initial_rpm: float = 0.0):
        self._time_step = time_step_ms
        self._inertia = engine_propeller_inertia
        self._rpm = initial_rpm

    def _compute_engine_torque(self, throttle: float):
        rpm_dim_indices = np.linspace(0, self.RPM_BREAKPOINTS.size, num=self.RPM_BREAKPOINTS.size)
        rpm_interpolator = interpolate.interp1d(
            self.RPM_BREAKPOINTS,
            rpm_dim_indices,
            kind="zero",
            fill_value="extrapolate"
        )
        throttle_dim_indices = np.linspace(0, self.THROTTLE_BREAKPOINTS.size, num=self.THROTTLE_BREAKPOINTS.size)
        throttle_interpolator = interpolate.interp1d(
            self.THROTTLE_BREAKPOINTS,
            throttle_dim_indices,
            kind="zero",
            fill_value="extrapolate"
        )
        torque_table_index = (throttle_interpolator(throttle), rpm_interpolator(self._rpm))

        return self.ENGINE_TORQUE_TABLE[torque_table_index]

    def step(self, throttle: float, impeller_torque: float):
        """Integrate engine inertia over one time step to compute engine RPM with saturation limits at 600 & 6,000

        This method updates the state of this class so that the data can be fed forward into other components.

        Args:
            throttle: Throttle signal in the range [0, 1)
            impeller_torque: The torque of the impeller
        """

        engine_torque = self._compute_engine_torque(throttle)
        engine_propeller_inertia = (impeller_torque + engine_torque) / self._inertia
        result = integrate.solve_ivp(
            fun=lambda t_, y_: engine_propeller_inertia,
            t_span=(0, self._time_step),
            y0=np.array([self._rpm]),
            method="RK45",
        )
        y = result[1]

        self._rpm = max(600.0, min(6_000.0, y[-1]))

    @property
    def rpm(self) -> float:
        return self._rpm

