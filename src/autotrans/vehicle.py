import math

import numpy as np
from scipy import integrate


def _into_mph(feet_per_min: float) -> float:
    return feet_per_min * 60 / 1609.34


class Vehicle:
    def __init__(
        self,
        t_step_ms: int,
        final_drive_ratio: float,
        wheel_friction: float,
        co_drag: float,
        wheel_radius: float,
        inertia: float,
        initial_speed: float
    ):
        # Parameters
        self._time_step = t_step_ms / 1000
        self._final_drive_ratio = final_drive_ratio
        self._wheel_friction = wheel_friction
        self._co_drag = co_drag
        self._wheel_radius = wheel_radius
        self._inertia = inertia

        # State variables
        self._wheel_speed = initial_speed / wheel_radius
        self._signed_load = 0.0

    def _compute_speed(self, wheel_speed: float) -> float:
        return

    def _compute_signed_load(self, vehicle_speed: float, brake: float) -> float:
        load = vehicle_speed**2 * self._co_drag + self._wheel_friction
        sign = math.copysign(1.0, vehicle_speed)

        return (load + brake) * sign

    def step(self, output_torque: float, brake: float):
        self._signed_load = self._compute_signed_load(self.speed, brake)

        drive_ratio = output_torque * self._final_drive_ratio
        vehicle_inertia = (drive_ratio - self._signed_load) / self._inertia
        integration = integrate.solve_ivp(
            fun=lambda t, o: vehicle_inertia,
            t_span=(0, self._time_step),
            y0=np.array([self._wheel_speed], dtype=np.float64)
        )

        self._wheel_speed = integration["y"][-1, -1]

    @property
    def transmission_rpm(self) -> float:
        return self._final_drive_ratio * self._wheel_speed

    @property
    def speed(self) -> float:
        return _into_mph(self._wheel_speed * 2 * math.pi * self._wheel_radius)
