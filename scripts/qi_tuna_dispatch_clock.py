"""Offline clock contract for a future guarded Quantum Inspire dispatch.

The contract accepts observations; it neither reads provider state nor dispatches.
"""

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Observation:
    boot_id: str
    utc_seconds: float
    boot_seconds: float


def _finite_number(value: object) -> bool:
    if not isinstance(value, (int, float)) or type(value) not in (int, float):
        return False
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


class DispatchClock:
    """Check an initiation horizon for one serialized owner, in one process."""

    __slots__ = ("_initial", "_previous", "_utc_deadline", "_elapsed_limit", "_tolerance", "_refused")
    _initial: Observation
    _previous: Observation
    _utc_deadline: float
    _elapsed_limit: float
    _tolerance: float
    _refused: bool

    def __setattr__(self, name: str, value: object) -> None:
        raise AttributeError("dispatch clock state is read-only")

    def __delattr__(self, name: str) -> None:
        raise AttributeError("dispatch clock state is read-only")

    def __init__(self, initial: Observation, utc_deadline: float, elapsed_limit: float, tolerance: float) -> None:
        self._validate_observation(initial)
        for value in (utc_deadline, elapsed_limit, tolerance):
            if not _finite_number(value):
                raise ValueError("clock bounds must be finite numbers")
        if utc_deadline <= initial.utc_seconds or elapsed_limit <= 0 or tolerance < 0:
            raise ValueError("clock bounds must define a future horizon and nonnegative tolerance")
        object.__setattr__(self, "_initial", initial)
        object.__setattr__(self, "_previous", initial)
        object.__setattr__(self, "_utc_deadline", utc_deadline)
        object.__setattr__(self, "_elapsed_limit", elapsed_limit)
        object.__setattr__(self, "_tolerance", tolerance)
        object.__setattr__(self, "_refused", False)

    @staticmethod
    def _validate_observation(observation: Observation) -> None:
        if type(observation) is not Observation:
            raise ValueError("clock observation has an invalid type")
        if type(observation.boot_id) is not str or not observation.boot_id:
            raise ValueError("boot identity is required")
        for value in (observation.utc_seconds, observation.boot_seconds):
            if not _finite_number(value):
                raise ValueError("clock readings must be finite numbers")
        if observation.boot_seconds < 0:
            raise ValueError("boot time must be nonnegative")

    def check(self, observation: Observation) -> None:
        if self._refused:
            raise ValueError("clock already refused this attempt")
        try:
            self._check(observation)
        except (ValueError, TimeoutError):
            object.__setattr__(self, "_refused", True)
            raise

    def _check(self, observation: Observation) -> None:
        self._validate_observation(observation)
        if observation.boot_id != self._initial.boot_id:
            raise ValueError("boot identity changed")
        if (
            observation.utc_seconds < self._previous.utc_seconds
            or observation.boot_seconds < self._previous.boot_seconds
        ):
            raise ValueError("clock moved backwards")
        utc_elapsed = observation.utc_seconds - self._initial.utc_seconds
        boot_elapsed = observation.boot_seconds - self._initial.boot_seconds
        if abs(utc_elapsed - boot_elapsed) > self._tolerance:
            raise ValueError("UTC and boot clocks disagree")
        if observation.utc_seconds >= self._utc_deadline or (
            observation.boot_seconds - self._initial.boot_seconds >= self._elapsed_limit
        ):
            raise TimeoutError("dispatch initiation horizon expired")
        object.__setattr__(self, "_previous", observation)
