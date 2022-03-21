import numpy as np

from autotrans.modeling.lookup_table import LookupTable2D
from autotrans.modeling.integrator import Integrator, DormundPrince5Solver

THROTTLE_BREAKPOINTS = np.array([0, 20, 30, 40, 50, 60, 70, 80, 90, 100], dtype=np.float64)
RPM_BREAKPOINTS = np.array([
    799.99,
    1200.00,
    1599.99,
    1999.99,
    2400.00,
    2800.00,
    3199.99,
    3599.99,
    3999.99,
    4400.00,
    4800.00
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
    ENGINE_TORQUE_TABLE = LookupTable2D(
        THROTTLE_BREAKPOINTS,
        RPM_BREAKPOINTS,
        ENGINE_TORQUE_TABLE_VALUES
    )

    def __init__(self, time_step_ms: int, engine_propeller_inertia: float, initial_rpm: float):
        time_step = time_step_ms / 1000
        solver = DormundPrince5Solver(time_step)

        self._integrator = Integrator(
            t0=0,
            y0=initial_rpm,
            solver=solver,
            saturation_limits=(600, 6000)
        )
        self._inertia = engine_propeller_inertia

    def step(self, throttle: float, impeller_torque: float):
        """Integrate engine inertia over one time step to compute engine RPM

        Engine RPM value has saturation limits at 600 & 6,000. This method updates the state of this
        class so that the data can be fed forward into other components.

        Args:
            throttle: Throttle signal in the range [0, 100]
            impeller_torque: The torque of the impeller
        """
        assert 0 <= throttle <= 100

        self._integrator.integrate(
            lambda _, rpm: self.engine_impeller_inertia(throttle, impeller_torque, rpm)
        )
        y = result["y"].flatten()

    @property
    def rpm(self) -> float:
        return self._integrator.state
