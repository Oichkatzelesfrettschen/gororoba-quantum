"""Connected two-qubit correlations of shot records, and their contrast between coupled and uncoupled pairs.

A shot record is a list of bit strings with qubit 0 at the rightmost character (the Quantum Inspire register order).
The connected correlation C_ij = <b_i b_j> - <b_i><b_j> is zero for independent qubits; its standard error comes from
the sample variance of the centered product, which holds for the large shot counts of one circuit and treats the
pairs as separate estimates, although pairs that share a qubit share its noise.
"""

from __future__ import annotations

import itertools
import math
from collections.abc import Iterable
from typing import Any

import numpy as np
from scipy import stats


def bit_array(shots: Iterable[str]) -> np.ndarray:
    """Shots by qubits array of 0 and 1, column q holding qubit q (the rightmost character is qubit 0)."""
    rows = list(shots)
    if not rows:
        raise ValueError("no shots")
    width = len(rows[0])
    joined = "".join(rows)
    if len(joined) != width * len(rows) or set(joined) - {"0", "1"}:
        raise ValueError("shots differ in width or hold a character other than 0 and 1")
    array = np.frombuffer(joined.encode("ascii"), dtype=np.uint8).reshape(len(rows), width) - ord("0")
    return array[:, ::-1].astype(float)


def connected_correlations(bits: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Connected correlation matrix and the standard error of each entry, from a shots by qubits array."""
    shots = bits.shape[0]
    centered = bits - bits.mean(axis=0)
    correlation = centered.T @ centered / shots
    squares = centered**2
    # var(z_ij) = <c_i^2 c_j^2> - C_ij^2 for the centered product z_ij = c_i c_j.
    second = squares.T @ squares / shots - correlation**2
    return correlation, np.sqrt(np.maximum(second, 0.0) / shots)


def overdispersion(bits: np.ndarray) -> float:
    """Variance of the number of ones per shot over the sum of the per-qubit binomial variances (1 for independence)."""
    totals = bits.sum(axis=1)
    return float(totals.var() / np.sum(bits.var(axis=0)))


def coupled_contrast(correlation: np.ndarray, error: np.ndarray, edges: Iterable[tuple[int, int]]) -> dict[str, Any]:
    """Mean connected correlation of coupled pairs against uncoupled pairs, with a Welch test and a pooled z score."""
    coupled = {tuple(sorted(edge)) for edge in edges}
    count = correlation.shape[0]
    pairs = list(itertools.combinations(range(count), 2))
    near = [pair for pair in pairs if pair in coupled]
    far = [pair for pair in pairs if pair not in coupled]
    if len(near) < 2 or len(far) < 2:
        raise ValueError("a contrast needs at least two coupled and two uncoupled pairs")
    near_values = np.array([correlation[i, j] for i, j in near])
    far_values = np.array([correlation[i, j] for i, j in far])
    near_error = np.array([error[i, j] for i, j in near])
    far_error = np.array([error[i, j] for i, j in far])
    difference = float(near_values.mean() - far_values.mean())
    pooled = math.sqrt(float(np.sum(near_error**2)) / len(near) ** 2 + float(np.sum(far_error**2)) / len(far) ** 2)
    welch = stats.ttest_ind(near_values, far_values, equal_var=False)
    return {
        "coupled_pairs": len(near),
        "uncoupled_pairs": len(far),
        "coupled_mean": float(near_values.mean()),
        "uncoupled_mean": float(far_values.mean()),
        "difference": difference,
        "difference_z_sampling": difference / pooled if pooled > 0 else None,
        "welch_t": float(welch.statistic),
        "welch_p": float(welch.pvalue),
    }
