"""Ramsey phase helpers shared by the Ramsey campaigns and the coherence probes.

A quadrature expectation read through an asymmetric assignment channel is inverted before any phase is taken,
and phases along a ladder whose steps grow by at most four are unwrapped against the line through the shorter
points, as in robust phase estimation.
"""

from __future__ import annotations

import math

import numpy as np


def corrected_expectation(raw: float, e10: float, e01: float) -> float:
    return (raw - (e01 - e10)) / (1.0 - e10 - e01)


def unwrap(delays: tuple[int, ...], phases: list[float]) -> list[float]:
    """Unwrap each phase to the branch nearest its prediction from the shorter delays.

    The first increment is taken inside (-pi, pi]; every later phase is moved
    by whole turns toward the line fitted through the phases already placed.
    """
    out = [phases[0]]
    for index in range(1, len(phases)):
        if index == 1:
            predicted = out[0]
        else:
            slope, intercept = np.polyfit(np.asarray(delays[:index], dtype=float), np.asarray(out), 1)
            predicted = float(slope * delays[index] + intercept)
        turns = round((predicted - phases[index]) / (2.0 * math.pi))
        out.append(phases[index] + 2.0 * math.pi * turns)
    return out


def fit_rate(delays: tuple[int, ...], phases: list[float]) -> tuple[float, float]:
    """Least-squares slope (rad per dt) and intercept of unwrapped phase against delay."""
    unwrapped = unwrap(delays, phases)
    slope, intercept = np.polyfit(np.asarray(delays, dtype=float), np.asarray(unwrapped), 1)
    return float(slope), float(intercept)
