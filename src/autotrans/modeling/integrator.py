from abc import ABC, abstractmethod
from typing import Callable, Optional, TypeAlias

import numpy as np

FirstOrderOde = Callable[[float, float], float]


class Solver(ABC):
    """Generic interface for an ODE solver"""

    @abstractmethod
    def step(self, func: FirstOrderOde, time: float, state: float) -> tuple[float, float]:
        ...


class EulerSolver(Solver):
    def __init__(self, step_size: float):
        self.h = step_size

    def step(self, func: FirstOrderOde, time: float, state: float) -> tuple[float, float]:
        new_state = state + self.h * func(time, state)
        new_time = time + self.h

        return new_time, new_state


class DormundPrince5Solver(Solver):
    TABLEAU = [
        [],
        [1/5],
        [3/40, 9/40],
        [44/45, -56/15, 32/9],
        [19372/6561, -25360/2187, 64448/6561, -212/729],
        [9017/3168, -355/33, 46732/5247, 49/176, -5103/18656],
        [35/384, 0, 500/1113, 125/192, -2187/6784, 11/84],
    ]

    def __init__(self, step_size):
        self.h = step_size

    def step(self, func: FirstOrderOde, time: float, state: float) -> tuple[float, float]:
        k1 = func(time, state)
        k2 = func(time + self.h * 1 / 5, state + self.h * np.dot([k1], self.TABLEAU[1]))
        k3 = func(time + self.h * 3 / 10, state + self.h * np.dot([k1, k2], self.TABLEAU[2]))
        k4 = func(time + self.h * 4 / 5, state + self.h * np.dot([k1, k2, k3], self.TABLEAU[3]))
        k5 = func(time + self.h * 8 / 9, state + self.h * np.dot([k1, k2, k3, k4], self.TABLEAU[4]))
        k6 = func(time + self.h * 1, state + self.h * np.dot([k1, k2, k3, k4, k5], self.TABLEAU[5]))
        k7 = func(time + self.h * 1, state + self.h * np.dot([k1, k2, k3, k4, k5, k6], self.TABLEAU[6]))

        k = np.array([k1, k2, k3, k4, k5, k6, k7])
        b = np.array([35/384, 0, 500/1113, 125/192, -2187/6784, 11/84, 0])
        new_state = state + self.h * b.dot(k)
        new_time = time + self.h

        return new_time, new_state


SaturationLimits: TypeAlias = tuple[Optional[float], Optional[float]]


class Integrator:
    """Python representation of a SimuLink integrator block."""

    def __init__(self, t0: float, y0: float, solver: Solver, saturation_limits: SaturationLimits = (None, None)):
        self._time = t0
        self._state = y0
        self._solver = solver
        self._saturation_limits = saturation_limits

    @property
    def state(self):
        return self._state

    def integrate(self, func: FirstOrderOde):
        self._time, self._state = self._solver.step(func, self._time, self._state)

        if self._saturation_limits[0] is not None:
            self._state = max(self._state, self._saturation_limits[0])

        if self._saturation_limits[1] is not None:
            self._state = min(self._state, self._saturation_limits[1])
