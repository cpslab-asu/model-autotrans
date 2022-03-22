import numpy as np
import scipy.interpolate as interpolate

from .integration import Dp5Integrator

THROTTLE_BREAKPOINTS = np.array([0, 20, 30, 40, 50, 60, 70, 80, 90, 100], dtype=np.float64)
RPM_BREAKPOINTS = np.array([
    799.99999999999989,
    1200,
    1599.9999999999998,
    1999.9999999999998,
    2400,
    2800.0000000000005,
    3199.9999999999995,
    3599.9999999999995,
    3999.9999999999995,
    4400,
    4800,
], dtype=np.float64)
ENGINE_TORQUE_TABLE_VALUES = np.array([
    [-40, -44, -49, -53, -57, -61, -65, -70, -74, -78, -82],
    [215, 117, 85, 66, 44, 29, 10, -2, -13, -22, -32],
    [245, 208, 178, 148, 122, 104, 85, 66, 48, 33, 18],
    [264, 260, 241, 219, 193, 167, 152, 133, 119, 96, 85],
    [264, 279, 282, 275, 260, 238, 223, 208, 189, 171, 152],
    [267, 290, 293, 297, 290, 275, 260, 256, 234, 212, 193],
    [267, 297, 305, 305, 305, 301, 293, 282, 267, 249, 226],
    [267, 301, 308, 312, 319, 323, 319, 316, 297, 279, 253],
    [267, 301, 312, 319, 327, 327, 327, 327, 312, 293, 267],
    [267, 301, 312, 319, 327, 334, 334, 334, 319, 305, 275],
], dtype=np.float64)


class Engine:
    def __init__(self, time_step_ms: int, engine_propeller_inertia: float, initial_rpm: float, initial_throttle: float, initial_impeller_torque: float):
        self._time_step = time_step_ms / 1000
        self._integrator = Dp5Integrator(self._time_step)
        self._rpm = initial_rpm
        self._inertia = engine_propeller_inertia
        self._last_throttle = initial_throttle
        self._last_impeller_torque = initial_impeller_torque

    def engine_impeller_inertia(self, throttle: float, impeller_torque: float, rpm: float) -> float:
        interpolator = interpolate.RectBivariateSpline(
            THROTTLE_BREAKPOINTS,
            RPM_BREAKPOINTS,
            ENGINE_TORQUE_TABLE_VALUES,
            kx=1,
            ky=1
        )
        engine_torque = interpolator(throttle, rpm)
        engine_impeller_inertia = (engine_torque.item() - impeller_torque) / self._inertia

        return engine_impeller_inertia

    def step(self, throttle: float, impeller_torque: float):
        """Integrate engine inertia over one time step to compute engine RPM

        Engine RPM value has saturation limits at 600 & 6,000. This method updates the state of this
        class so that the data can be fed forward into other components.

        Args:
            throttle: Throttle signal in the range [0, 100]
            impeller_torque: The torque of the impeller
        """
        assert 0 <= throttle <= 100

        throttle_interpolator = interpolate.interp1d(
            x=(0, self._time_step),
            y=(self._last_throttle, throttle),
            kind="slinear",
        )
        torque_interpolator = interpolate.interp1d(
            x=(0, self._time_step),
            y=(self._last_impeller_torque, impeller_torque),
            kind="slinear",
        )

        def integration_fn(t: float, rpm: float) -> float:
            return self.engine_impeller_inertia(
                throttle_interpolator(t),
                torque_interpolator(t),
                rpm
            )

        self._rpm = self._integrator.integrate(t0=0, y0=self._rpm, func=integration_fn)
        self._last_throttle = throttle
        self._last_impeller_torque = impeller_torque

    @property
    def rpm(self) -> float:
        return self._rpm
