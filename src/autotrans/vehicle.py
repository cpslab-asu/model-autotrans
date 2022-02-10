import math

from scipy import integrate


def _into_mph(speed: float) -> float:
    ...


class Vehicle:
    RLOAD0 = None
    RLOAD2 = None

    def __init__(
        self,
        final_drive_ratio: float,
        co_friction: float,
        co_drag: float,
        wheel_radius: float,
        inertia: float,
        initial_transmission_rpm: float,
        initial_vehicle_speed: float
    ):
        self._final_drive_ratio = final_drive_ratio
        self._co_friction = co_friction
        self._co_drag = co_drag
        self._wheel_radius = wheel_radius
        self._inertia = inertia
        self._transmission_rpm = initial_transmission_rpm
        self._speed = initial_vehicle_speed
        self._signed_load = 0.0

    def _compute_speed(self, wheel_speed: float) -> float:
        return _into_mph(wheel_speed * 2 * math.pi * self._wheel_radius)

    def _compute_signed_load(self, vehicle_speed: float, brake: float) -> float:
        load = vehicle_speed**2 * self._co_drag + self._co_friction
        sign = math.copysign(1.0, vehicle_speed)

        return (load + brake) * sign

    def step(self, output_torque: float, brake: float):
        final_drive_ratio = output_torque * self._final_drive_ratio
        vehicle_inertia = (final_drive_ratio * self._signed_load) / self._inertia
        # TODO: Implement integrator for vehicle inertia
        integration = integrate.solve_ivp()
        wheel_speed = integration["y"][-1]

        self._transmission_rpm = self._final_drive_ratio * wheel_speed
        self._speed = self._compute_speed(wheel_speed)
        self._signed_load = self._compute_signed_load(self._speed, brake)

    @property
    def transmission_rpm(self) -> float:
        return self._transmission_rpm

    @property
    def speed(self) -> float:
        return self._speed
