from dataclasses import dataclass
from typing import TypeVar, Generic

import numpy as np
import scipy.interpolate as interpolate
from numpy.typing import NDArray


@dataclass
class LinearInterpolator:
    q1: tuple[float, float]
    q2: tuple[float, float]

    def interpolate(self, x: float) -> float:
        x1, y1 = self.q1
        x2, y2 = self.q2

        return y1 + (x - x1) / (x2 - x1) * (y2 - y1)


@dataclass
class BilinearInterpolator:
    q11: tuple[float, float, float]
    q21: tuple[float, float, float]
    q12: tuple[float, float, float]
    q22: tuple[float, float, float]

    def interpolate(self, x: float, y: float) -> float:
        x1, y1, f_q11 = self.q11
        x2, _, f_q21 = self.q21
        _, y2, f_q12 = self.q12
        _, _, f_q22 = self.q22
        fx_y1 = (x2 - x) / (x2 - x1) * f_q11 + (x - x1) / (x2 - x1) * f_q21
        fx_y2 = (x2 - x) / (x2 - x1) * f_q12 + (x - x1) / (x2 - x1) * f_q22

        return (y2 - y) / (y2 - y1) * fx_y1 + (y - y1) / (y2 - y1) * fx_y2


def _is_monotonic(seq: NDArray) -> bool:
    return np.all(np.diff(seq) > 0)


ValueT = TypeVar("ValueT", bound=np.generic)


def _index_bounds(seq: NDArray[ValueT], value: ValueT) -> tuple[int, int]:
    """Compute the index bounds for a value given the sequence.

    The purpose of this function is to produce indices that can be used to index the table of
    values. This function assumes that the provided sequence is monotonic. Because this sequence is
    assumed to be monotonic, the upper index can be assumed to be the next index after the last
    index less than the value.

    Example: seq=[1,3,5,7,9], value=4 ==> lower=1, upper=2 because seq[1] <= value <= seq[2]

    Args:
        seq: The sequence to search
        value: The value to compute the index bounds for

    Returns:
        The indices of the elements in the sequence that bound the value
    """

    lower_indices, = np.where(seq <= value)
    if lower_indices.size == 0:
        lower_bound = 0
    else:
        lower_bound = lower_indices[-1]

    upper_indices, = np.where(seq >= value)
    if upper_indices.size == 0:
        upper_bound = seq.size - 1
    else:
        upper_bound = upper_indices[0]

    if lower_bound == upper_bound:
        if upper_bound == seq.size - 1:
            lower_bound = lower_bound - 1
        else:
            upper_bound = upper_bound + 1

    return lower_bound, upper_bound


Dim1T = TypeVar("Dim1T", bound=np.generic)


@dataclass
class LookupTable1D(Generic[Dim1T]):
    _breakpoints: NDArray[Dim1T]
    _values: NDArray[np.float]

    def lookup(self, x: ValueT) -> float:
        x_lower_index, x_upper_index = _index_bounds(self._breakpoints, x)
        interpolator = interpolate.interp1d(
            x=[self._breakpoints[x_lower_index], self._breakpoints[x_upper_index]],
            y=[self._values[x_lower_index], self._values[x_upper_index]],
            kind="linear",
            fill_value="extrapolate"
        )
        result = interpolator(x)

        return result.item()


Dim2T = TypeVar("Dim2T", bound=np.generic)


@dataclass
class LookupTable2D(Generic[Dim1T, Dim2T]):
    _x1_breakpoints: NDArray[Dim1T]
    _x2_breakpoints: NDArray[Dim2T]
    _values: NDArray[np.float]

    def __post_init__(self):
        assert _is_monotonic(self._x1_breakpoints)
        assert _is_monotonic(self._x2_breakpoints)
        assert self._values.shape == (self._x1_breakpoints.size, self._x2_breakpoints.size)

    def lookup(self, x1: Dim1T, x2: Dim2T):
        x1_lower_index, x1_upper_index = _index_bounds(self._x1_breakpoints, x1)
        x2_lower_index, x2_upper_index = _index_bounds(self._x2_breakpoints, x2)

        x1_1 = self._x1_breakpoints[x1_lower_index]
        x1_2 = self._x1_breakpoints[x1_upper_index]
        x2_1 = self._x2_breakpoints[x2_lower_index]
        x2_2 = self._x2_breakpoints[x2_upper_index]

        interpolator = interpolate.interp2d(
            x=[x1_1, x1_1, x1_2, x1_2],
            y=[x2_1, x2_2, x2_1, x2_2],
            z=[
                self._values[x1_lower_index, x2_lower_index],
                self._values[x1_lower_index, x2_upper_index],
                self._values[x1_upper_index, x2_lower_index],
                self._values[x1_upper_index, x2_upper_index],
            ],
            kind="linear",
            fill_value="extrapolate",
        )
        result = interpolator(x1, x2)

        return result[0]
