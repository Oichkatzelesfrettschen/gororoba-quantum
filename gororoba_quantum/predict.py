"""Classical predictions for the circuits, computed from cd_sign and cd_multiply.

The circuit builders in designs.py and select_lcu.py never import this module,
so every statevector or operator comparison in designs.py sets an algebraic
prediction against a compiled circuit. Basis index x = sum_b x_b 2^b puts
qubit 0 at the least significant bit, the Qiskit convention.
"""

from __future__ import annotations

import numpy as np

from cd_core import cd_multiply, cd_sign


def left_mult_matrix(dim: int, m: int) -> np.ndarray:
    """Matrix of L_{e_m}: |e_q> -> cd_sign(dim,m,q) |e_{m XOR q}>."""
    mat = np.zeros((dim, dim))
    for q in range(dim):
        mat[m ^ q, q] = cd_sign(dim, m, q)
    return mat


def select_matrix(dim: int, i: int, j: int) -> np.ndarray:
    """SELECT|a,x> = cd_sign(dim,m_a,x)|a, m_a ^ x> with m_0 = i, m_1 = j.

    Index x + dim*a places the ancilla above the data qubits.
    """
    mat = np.zeros((2 * dim, 2 * dim))
    for a, m in ((0, i), (1, j)):
        mat[a * dim : (a + 1) * dim, a * dim : (a + 1) * dim] = left_mult_matrix(dim, m)
    return mat


def associator_phase(dim: int, i: int, j: int) -> list[int]:
    """omega(x) in W|x> = omega(x)|x>, W = L_{e_i e_j}^dagger L_{e_i} L_{e_j}.

    L_{e_j} sends |x> to cd_sign(j,x)|j^x>, L_{e_i} multiplies by
    cd_sign(i,j^x), and L_{e_i e_j}^dagger = cd_sign(i,j) L_{e_{i^j}}^T returns
    |i^j^x> to |x> with cd_sign(i^j,x).
    """
    return [
        cd_sign(dim, i, j) * cd_sign(dim, i ^ j, x) * cd_sign(dim, j, x) * cd_sign(dim, i, j ^ x) for x in range(dim)
    ]


def walsh_distribution(phase: list[int]) -> np.ndarray:
    """P(y) = |2^-n sum_x phase(x) (-1)^(x.y)|^2: H^n, diagonal phase, H^n, measure."""
    dim = len(phase)
    amp = np.array(phase, dtype=float)
    h = 1
    while h < dim:
        for start in range(0, dim, 2 * h):
            lo = amp[start : start + h].copy()
            hi = amp[start + h : start + 2 * h].copy()
            amp[start : start + h] = lo + hi
            amp[start + h : start + 2 * h] = lo - hi
        h *= 2
    return np.asarray((amp / dim) ** 2)


def anf_degree(bits: list[int]) -> int:
    """Algebraic degree of a Boolean function given as its truth table."""
    coeff = list(bits)
    n = len(bits).bit_length() - 1
    for b in range(n):
        for x in range(len(bits)):
            if x >> b & 1:
                coeff[x] ^= coeff[x ^ (1 << b)]
    return max((bin(m).count("1") for m in range(len(bits)) if coeff[m]), default=0)


def zero_divisor_p0(a_pair: tuple[int, int], b_pair: tuple[int, int], s: int) -> float:
    """P(ancilla = 0) = |a b|^2 / 8 from cd_multiply, a = e_i + e_j, b = e_k + s e_l.

    The post-selected data state is (L_{e_i} + L_{e_j})/2 applied to b/sqrt2.
    """
    a = [0.0] * 16
    b = [0.0] * 16
    a[a_pair[0]] = a[a_pair[1]] = 1.0
    b[b_pair[0]] = 1.0
    b[b_pair[1]] = float(s)
    return sum(v * v for v in cd_multiply(16, a, b)) / 8.0


def phase_sweep_p0(a_pair: tuple[int, int], b_pair: tuple[int, int], phase: float) -> float:
    """P(ancilla = 0) for b = (e_k + e^{i phase} e_l)/sqrt2 under the complex-linear L.

    Intermediate phases probe the complex-linear extension of the real sedenion
    multiplication matrices; phase 0 and pi are the real inputs e_k +/- e_l.
    """
    b = np.zeros(16, dtype=complex)
    b[b_pair[0]] = 1.0 / np.sqrt(2.0)
    b[b_pair[1]] = np.exp(1j * phase) / np.sqrt(2.0)
    out = (left_mult_matrix(16, a_pair[0]) + left_mult_matrix(16, a_pair[1])) @ b / 2.0
    return float(np.vdot(out, out).real)
