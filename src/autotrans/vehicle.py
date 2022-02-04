class Vehicle:
    def __init__(
        self,
        final_drive_ratio: float = 0.0,
        co_friction: float = 0.0,
        co_drag: float = 0.0,
        wheel_radius: float = 0.0,
        inertia: float = 0.0,
        initial_transmission_rpm: float = 0.0
    ):
        self._final_drive_ration = final_drive_ratio
        self._co_friction = co_friction
        self._co_drag = co_drag
        self._wheel_radius = wheel_radius
        self._inertia = inertia
        self._transmission_rpm = initial_transmission_rpm
        self._vehicle_speed = 0.0

    def _compute_speed(self, output_torque: float, brake: float) -> float:
        ...

    def _compute_rpm(self, output_torque: float) -> float:
        ...

    def step(self, output_torque: float, brake: float):
        self._transmission_rpm = self._compute_rpm(output_torque)
        self._vehicle_speed = self._compute_speed(output_torque, brake)

    @property
    def transmission_rpm(self) -> float:
        return self._transmission_rpm

    @property
    def vehicle_speed(self) -> float:
        return self._vehicle_speed
