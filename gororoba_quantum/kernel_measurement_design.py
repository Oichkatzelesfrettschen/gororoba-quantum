"""Kernel-sensitive quantum measurement design for Cayley-Dickson operators.

Implements coherent input probe synthesis, measurement basis cover optimization,
Neyman shot allocation, and exact bias decomposition across all nullity strata
of 32-dimensional pathion and sedenion operators.
"""

from __future__ import annotations

import itertools
import math
from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np

import cd_core
import pathion_kernel_map as pkm

DIM = 32

# Canonical operands spanning the five nullity strata of A_5
OPERANDS_BY_NULLITY: dict[int, tuple[tuple[int, int, int], ...]] = {
    0: ((1, 17, 1),),
    4: ((1, 26, 1), (2, 27, 1)),
    8: ((1, 10, 1),),
    12: ((1, 18, 1), (17, 2, -1), (1, 24, 1)),
}

# The basis-heralding-degenerate pair: e_1 + e_9 (nullity 0) vs e_1 + e_10 (nullity 8).
# For both operands, ||L_y e_k||^2 = 2 for every standard basis input k in {0,...,31}.
DEGENERATE_PAIR = ((1, 9, 1), (1, 10, 1))


def left_mult_matrix(operand: tuple[int, int, int], dim: int = DIM) -> np.ndarray:
    """Matrix of left multiplication L_(e_i + t e_j) in dimension dim."""
    i, j, t = operand
    mat = np.zeros((dim, dim), dtype=float)
    for col in range(dim):
        sign_i = cd_core.cd_sign(dim, i, col)
        sign_j = cd_core.cd_sign(dim, j, col)
        mat[i ^ col, col] += float(sign_i)
        mat[j ^ col, col] += float(t * sign_j)
    return mat


def basis_heralding_probabilities(operand: tuple[int, int, int], dim: int = DIM) -> np.ndarray:
    """Square norms ||L_y e_k||^2 for standard basis inputs k in {0,...,dim-1}."""
    mat = left_mult_matrix(operand, dim)
    return np.sum(mat**2, axis=0)


def verify_basis_degeneracy() -> bool:
    """Verify that e_1 + e_9 (nullity 0) and e_1 + e_10 (nullity 8) have identical basis heralding."""
    p0 = basis_heralding_probabilities(DEGENERATE_PAIR[0])
    p8 = basis_heralding_probabilities(DEGENERATE_PAIR[1])
    n0 = pkm.nullity(DEGENERATE_PAIR[0])
    n8 = pkm.nullity(DEGENERATE_PAIR[1])
    return n0 == 0 and n8 == 8 and bool(np.allclose(p0, p8)) and bool(np.allclose(p0, 2.0))


@dataclass(frozen=True)
class CoherentProbe:
    """A two-Flat superposition probe psi = (e_j + phase * e_k) / sqrt(2)."""

    j: int
    k: int
    phase: float  # +1.0 or -1.0

    def state_vector(self, dim: int = DIM) -> np.ndarray:
        vec = np.zeros(dim, dtype=float)
        vec[self.j] = 1.0 / math.sqrt(2.0)
        vec[self.k] = self.phase / math.sqrt(2.0)
        return vec

    def response_norm_sq(self, operand: tuple[int, int, int], dim: int = DIM) -> float:
        """||L_y psi||^2 under left multiplication."""
        mat = left_mult_matrix(operand, dim)
        vec = self.state_vector(dim)
        out = mat @ vec
        return float(np.dot(out, out))


def find_distinguishing_coherent_probes(
    op1: tuple[int, int, int], op2: tuple[int, int, int], dim: int = DIM
) -> list[tuple[CoherentProbe, float, float]]:
    """Find two-Flat coherent superposition probes that distinguish op1 and op2."""
    probes: list[tuple[CoherentProbe, float, float]] = []
    for j in range(dim):
        for k in range(j + 1, dim):
            for phase in (1.0, -1.0):
                probe = CoherentProbe(j, k, phase)
                norm1 = probe.response_norm_sq(op1, dim)
                norm2 = probe.response_norm_sq(op2, dim)
                if abs(norm1 - norm2) > 1e-6:
                    probes.append((probe, norm1, norm2))
    return probes


def sedenion_blade_pauli_words() -> list[str]:
    """The 28 distinct 4-qubit Pauli words in the readout bank of all 84 sedenion zero-divisor blades.

    Algebraically, these are Y_3 (x) Q where Q in {I,X,Y,Z}^3 has an odd number of Y factors (Q^T = -Q).
    """
    words: list[str] = []
    paulis = ["I", "X", "Y", "Z"]
    for q2, q1, q0 in itertools.product(paulis, repeat=3):
        y_count = (q2 == "Y") + (q1 == "Y") + (q0 == "Y")
        if y_count % 2 == 1:
            words.append(f"Y{q2}{q1}{q0}")
    return sorted(words)


def is_qwc(word1: str, word2: str) -> bool:
    """Whether two Pauli words qubit-wise commute."""
    for c1, c2 in zip(word1, word2, strict=True):
        if c1 != "I" and c2 != "I" and c1 != c2:
            return False
    return True


def greedy_qwc_clique_cover(words: Sequence[str]) -> list[list[str]]:
    """Greedy graph coloring / clique partitioning for Qubit-Wise Commutation."""
    groups: list[list[str]] = []
    for w in sorted(words):
        placed = False
        for g in groups:
            if all(is_qwc(w, member) for member in g):
                g.append(w)
                placed = True
                break
        if not placed:
            groups.append([w])
    return groups


@dataclass(frozen=True)
class BlockBiasSummary:
    """Exact bias decomposition of a sign-contrast nullity estimate."""

    nullity_true: int
    n_hat: float
    visibility: float
    v_plus: float
    v_minus: float
    bias_theoretical: float
    identity_error: float


def block_bias_decomposition(c_obs: np.ndarray, tau: np.ndarray) -> BlockBiasSummary:
    """Compute exact bias decomposition:

    N_hat - N = (|B_+||B_-| / |B|) * (V_+ - V_-) / V_hat.
    """
    n_bins = len(c_obs)
    b_plus = int(np.sum(tau > 0))
    b_minus = int(np.sum(tau < 0))
    n_true = (b_plus - b_minus) // 2

    v_hat = float(np.mean(tau * c_obs))
    if abs(v_hat) < 1e-12:
        return BlockBiasSummary(n_true, float("nan"), 0.0, 0.0, 0.0, float("nan"), float("nan"))

    n_hat = 0.5 * float(np.sum(c_obs)) / v_hat
    v_p = float(np.mean(c_obs[tau > 0])) if b_plus > 0 else 0.0
    v_m = float(np.mean(-c_obs[tau < 0])) if b_minus > 0 else 0.0

    thm_bias = (b_plus * b_minus / float(n_bins)) * (v_p - v_m) / v_hat
    id_err = abs((n_hat - n_true) - thm_bias)

    return BlockBiasSummary(
        nullity_true=n_true,
        n_hat=n_hat,
        visibility=v_hat,
        v_plus=v_p,
        v_minus=v_m,
        bias_theoretical=thm_bias,
        identity_error=id_err,
    )


def oracle_free_calibrated_nullity(
    c_obs_blocks: Sequence[np.ndarray], c_null_blocks: Sequence[np.ndarray]
) -> tuple[list[float], float]:
    """Compute oracle-free calibrated nullity across blocks using null calibration:

    N_cal,b = (sum(c_obs,b - delta_0,b) / 2) / V_null,b.
    """
    n_cal_b: list[float] = []
    for c_b, c_null in zip(c_obs_blocks, c_null_blocks, strict=True):
        delta_0 = float(np.mean(c_null))
        tau_null = np.array([1.0 if t % 2 == 0 else -1.0 for t in range(len(c_null))])
        v_null = float(np.mean(tau_null * c_null))
        if abs(v_null) < 1e-12:
            n_cal_b.append(float("nan"))
        else:
            n_cal_b.append(0.5 * float(np.sum(c_b - delta_0)) / v_null)
    return n_cal_b, sum(n_cal_b)


def neyman_optimal_shot_allocation(total_shots: int, block_variances: Sequence[float]) -> list[int]:
    """Neyman-optimal allocation of shots proportional to standard deviations."""
    sigmas = [math.sqrt(max(v, 1e-15)) for v in block_variances]
    sum_sigmas = sum(sigmas)
    if sum_sigmas < 1e-12:
        n_blocks = len(block_variances)
        return [total_shots // n_blocks] * n_blocks
    shots = [int(round(total_shots * s / sum_sigmas)) for s in sigmas]
    diff = total_shots - sum(shots)
    shots[0] += diff
    return shots
