"""Exact simulation of the committed line-native Grover circuits with a coherent gate error, for the retention families.

A coherent error is one number per family, the same on every gate of the kind:

- cz_phase: every CZ applies the conditional phase pi + x instead of pi (x in radians);
- prx_amplitude: every PRX rotates by theta (1 + x) instead of theta (x a fraction).

The marked probability Q_k(x) after the k-iteration circuit of depth k, read at the outcome of the mark, gives the
factor R_k(x) = (Q_k(x) - 1/8) / (P_k - 1/8) with P_k the ideal marked probability, 1 at x = 0. The families of
grover_depth_families multiply R_k by a free depth-independent prefactor and a per-iteration rate.

The circuits come from iqm_grover_line.line_arm, the builder of the case, on the case's path; the factor tables on a
fine grid of x are computed once per process and cached.
"""

from __future__ import annotations

import functools
import math
from typing import Any

import numpy as np

PATH = ["QB20", "QB16", "QB17"]
MARKED = "101"
DEPTHS = (1, 2, 3, 4)
KINDS = ("cz_phase", "prx_amplitude")
# Symmetric bounds of the error in each family: a CZ conditional phase within 0.3 rad (17 degrees) of pi and a PRX
# amplitude within 10 % are far beyond the calibrated gates of the device, so a fit that ends there is out of domain.
X_BOUND = {"cz_phase": 0.3, "prx_amplitude": 0.10}
GRID_POINTS = 4001


def depth_circuit(k: int) -> dict[str, Any]:
    import iqm_grover_line as grover

    return dict(grover.line_arm(MARKED, k, PATH, "t")[1])


def outcome_of(key: str) -> int:
    return sum(int(c) << q for q, c in enumerate(key))


def simulate(circuit: dict[str, Any], cz_phase: np.ndarray, prx_scale: np.ndarray) -> np.ndarray:
    """Outcome probabilities (samples x 8) of the circuit with the CZ conditional phase pi + cz_phase[i] and every PRX
    angle scaled by prx_scale[i] (arrays of one length), by outcome index sum(bit_q << q) in the measured order."""
    n = len(PATH)
    samples = len(cz_phase)
    state = np.zeros((samples, 2**n), dtype=complex)
    state[:, 0] = 1
    measured: list[int] = []
    index = np.arange(2**n)
    for op in circuit["instructions"]:
        where = [PATH.index(q) for q in op["locus"]]
        if op["name"] == "prx":
            theta = op["args"]["angle"] * prx_scale
            phase = op["args"]["phase"]
            c, s = np.cos(theta / 2), np.sin(theta / 2)
            m01 = -1j * np.exp(-1j * phase) * s
            m10 = -1j * np.exp(1j * phase) * s
            low = index[((index >> where[0]) & 1) == 0]
            high = low | (1 << where[0])
            a, b = state[:, low].copy(), state[:, high].copy()
            state[:, low] = c[:, None] * a + m01[:, None] * b
            state[:, high] = m10[:, None] * a + c[:, None] * b
        elif op["name"] == "cz":
            both = index[(((index >> where[0]) & (index >> where[1])) & 1) == 1]
            state[:, both] *= (-np.exp(1j * cz_phase))[:, None]
        elif op["name"] == "measure":
            measured = where
    out = np.zeros((samples, 2**n))
    for i in range(2**n):
        out[:, sum(((i >> p) & 1) << q for q, p in enumerate(measured))] += np.abs(state[:, i]) ** 2
    return out


def ideal_marked(k: int) -> float:
    theta = math.asin(1 / math.sqrt(8))
    return math.sin((2 * k + 1) * theta) ** 2


def factor(kind: str, k: int, x: np.ndarray | float) -> np.ndarray:
    """R_k(x) of the family kind at depth k for an array (or scalar) x."""
    xs = np.atleast_1d(np.asarray(x, dtype=float))
    zeros, ones = np.zeros_like(xs), np.ones_like(xs)
    probabilities = simulate(
        depth_circuit_cached(k), xs if kind == "cz_phase" else zeros, ones + (xs if kind == "prx_amplitude" else zeros)
    )
    marked = probabilities[:, outcome_of(MARKED)]
    return np.asarray((marked - 1 / 8) / (ideal_marked(k) - 1 / 8))


@functools.lru_cache(maxsize=8)
def depth_circuit_cached(k: int) -> dict[str, Any]:
    return depth_circuit(k)


def grid(kind: str) -> np.ndarray:
    return np.linspace(-X_BOUND[kind], X_BOUND[kind], GRID_POINTS)


@functools.lru_cache(maxsize=4)
def factor_table(kind: str) -> np.ndarray:
    """R_k(x) on grid(kind), one column per depth 1 to 4: (GRID_POINTS, 4)."""
    xs = grid(kind)
    return np.stack([factor(kind, k, xs) for k in DEPTHS], axis=-1)
