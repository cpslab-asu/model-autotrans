class Engine:
    def __init__(self, engine_propeller_inertia: float = 0.0, initial_rpm: float = 0.0):
        self._inertia = engine_propeller_inertia
        self._engine_rpm = initial_rpm

    def _compute_rpm(self, throttle: float, impeller_torque: float) -> float:
        ...

    def step(self, throttle: float, impeller_torque: float):
        self._engine_rpm = self._compute_rpm(throttle, impeller_torque)

    @property
    def engine_rpm(self) -> float:
        return self._engine_rpm

