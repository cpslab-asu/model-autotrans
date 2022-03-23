from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Callable

import numpy as np


class FixedStepIntegrator(ABC):
    def __init__(self, step_size: float):
        self._step_size = step_size

    @abstractmethod
    def integrate(self, t0: float, y0: float, func: Callable[[float, float], float]):
        ...


class EulerIntegrator(FixedStepIntegrator):
    def integrate(self, t0: float, y0: float, func: Callable[[float, float], float]):
        return y0 + self._step_size * func(t0, y0)


class Dp5Integrator(FixedStepIntegrator):
    TABLEAU = [
        [],
        [1/5],
        [3/40, 9/40],
        [44/45, -56/15, 32/9],
        [19372/6561, -25360/2187, 64448/6561, -212/729],
        [9017/3168, -355/33, 46732/5247, 49/176, -5103/18656],
        [35/384, 0, 500/1113, 125/192, -2187/6784, 11/84],
    ]

    def integrate(self, t0: float, y0: float, func: Callable[[float, float], float]):
        def _dot(v1: Sequence[float], v2: Sequence[float]) -> float:
            return np.dot(v1, v2).item()

        k1 = self._step_size * func(t0, y0)
        k2 = self._step_size * func(t0 + self._step_size * 1 / 5, y0 + _dot([k1], self.TABLEAU[1]))
        k3 = self._step_size * func(t0 + self._step_size * 3 / 10, y0 + _dot([k1, k2], self.TABLEAU[2]))
        k4 = self._step_size * func(t0 + self._step_size * 4 / 5, y0 + _dot([k1, k2, k3], self.TABLEAU[3]))
        k5 = self._step_size * func(t0 + self._step_size * 8 / 9, y0 + _dot([k1, k2, k3, k4], self.TABLEAU[4]))
        k6 = self._step_size * func(t0 + self._step_size, y0 + _dot([k1, k2, k3, k4, k5], self.TABLEAU[5]))
        k7 = self._step_size * func(t0 + self._step_size, y0 + _dot([k1, k2, k3, k4, k5, k6], self.TABLEAU[6]))
        k = [k1, k2, k3, k4, k5, k6, k7]
        b = [35/384, 0, 500/1113, 125/192, -2187/6784, 11/84, 0]  # 5-th order accurate solution

        return y0 + _dot(k, b)
