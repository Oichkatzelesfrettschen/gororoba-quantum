"""Fixed-output-mode marginals without enumerating the full Fock space.

For collision-free inputs, the probability generating polynomial is
Per(I + V), V_ij = sum_a (z_a - 1) conj(U[a,i]) U[a,j].
The low-rank coefficient recurrence below evaluates this identity in
n**O(k) arithmetic for fixed k measured modes. Complex128 evaluation is not
an exact-arithmetic certificate. Repeated input occupations are rejected.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike

import parallel
from photonic_permanents import ComplexMatrix, finite_complex, integer, matrix, occupation, positive, unitary

Index = tuple[int, ...]
Key = tuple[Index, Index]


@dataclass(frozen=True)
class CoefficientStep:
    """One row's independent contributions to the bivariate coefficient map."""

    left: np.ndarray
    right: np.ndarray

    def __call__(self, item: tuple[Key, complex]) -> list[tuple[Key, complex]]:
        (alpha, beta), value = item
        result = [((alpha, beta), value)]
        for a, x in enumerate(self.left):
            if x == 0:
                continue
            aa = tuple(v + int(i == a) for i, v in enumerate(alpha))
            for b, y in enumerate(self.right):
                if y != 0:
                    bb = tuple(v + int(i == b) for i, v in enumerate(beta))
                    result.append(((aa, bb), finite_complex(value * complex(x) * complex(y))))
        return result


def low_rank_coefficients(left: ArrayLike, right: ArrayLike, *, max_work: int = 2_000_000) -> dict[Index, complex]:
    """Diagonal coefficients of prod_i (1 + (L_i.x)(R_i.y)).

    Per(I + L R.T) = sum_alpha alpha! * returned[alpha].
    The transpose is algebraic, not conjugate transpose. The caller supplies
    any required conjugation. Both arrays are n-by-k.
    """
    x = matrix(left, square=False)
    y = matrix(right, square=False)
    if x.shape != y.shape:
        raise ValueError("low-rank factors must have the same n-by-k shape")
    n, k = x.shape
    limit = integer(max_work, "max_work", 1)
    if k == 0:
        return {(): 1 + 0j}
    # At degree d each side has C(d+k-1,k-1) monomials. This preflight
    # bounds both the sparse state count and all recurrence contributions.
    states = 0
    for degree in range(n + 1):
        states += math.comb(degree + k - 1, k - 1) ** 2
        if states * max(1, n) * (k * k + 1) > limit:
            raise ValueError("fixed-mode recurrence exceeds max_work; reduce photons or measured modes")
    origin = (0,) * k
    coefficients: dict[Key, complex] = {(origin, origin): 1 + 0j}
    # Rows depend on the previous coefficient map; terms within a row do not.
    for row in range(n):
        pieces = parallel.ordered_map(CoefficientStep(x[row], y[row]), list(coefficients.items()))
        following: dict[Key, complex] = {}
        for piece in pieces:
            for key, value in piece:
                following[key] = finite_complex(following.get(key, 0j) + value)
        coefficients = following
    return {alpha: value for (alpha, beta), value in coefficients.items() if alpha == beta}


@dataclass(frozen=True)
class BinomialExpansion:
    """Expand one coefficient times prod_a (z_a-1)**alpha_a."""

    def __call__(self, item: tuple[Index, complex]) -> dict[Index, complex]:
        alpha, coefficient = item
        polynomial: dict[Index, complex] = {(): coefficient * math.prod(math.factorial(v) for v in alpha)}
        for degree in alpha:
            following = {}
            for prefix, value in polynomial.items():
                for power in range(degree + 1):
                    following[(*prefix, power)] = value * math.comb(degree, power) * (-1) ** (degree - power)
            polynomial = following
        return polynomial


@dataclass(frozen=True)
class MarginalDistribution:
    """Numerical probabilities plus the measured roundoff diagnostics.

    Tiny negative real coefficients within `atol` are clipped, with their
    removed mass retained. No renormalisation is performed.
    """

    modes: tuple[int, ...]
    probabilities: dict[Index, float]
    raw_mass_error: float
    maximum_imaginary: float
    clipped_negative_mass: float


def collision_free_marginal(
    value: ArrayLike,
    inputs: Sequence[int],
    modes: Sequence[int],
    *,
    max_work: int = 2_000_000,
    atol: float = 1e-10,
) -> MarginalDistribution:
    """Joint number distribution in selected modes, marginalising every other mode.

    The input may occupy arbitrary distinct modes, not only the first n.
    Empty measured sets and vacuum return a point mass. Increasing k removes
    the fixed-k efficiency guarantee. Ill-conditioned evaluations raise.
    """
    tolerance = positive(atol, "atol")
    limit = integer(max_work, "max_work", 1)
    u: ComplexMatrix = unitary(value, tolerance)
    t = occupation(inputs, len(u), "inputs")
    selected = tuple(integer(mode, "mode") for mode in modes)
    if len(set(selected)) != len(selected) or any(mode >= len(u) for mode in selected):
        raise ValueError("measured modes must be distinct valid mode indices")
    if any(count > 1 for count in t):
        raise ValueError("this fixed-mode recurrence requires collision-free input")
    if not selected:
        return MarginalDistribution((), {(): 1.0}, 0.0, 0.0, 0.0)
    occupied = [i for i, count in enumerate(t) if count]
    block = u[np.ix_(selected, occupied)].T
    coefficients = low_rank_coefficients(block.conj(), block, max_work=limit)
    pieces = parallel.ordered_map(BinomialExpansion(), list(coefficients.items()))
    terms: dict[Index, list[complex]] = {}
    for piece in pieces:
        for key, contribution in piece.items():
            terms.setdefault(key, []).append(contribution)
    values = {
        key: complex(math.fsum(v.real for v in parts), math.fsum(v.imag for v in parts)) for key, parts in terms.items()
    }
    if not all(math.isfinite(v.real) and math.isfinite(v.imag) for v in values.values()):
        raise ArithmeticError("marginal coefficients overflow; use higher precision")
    mass_error = abs(math.fsum(v.real for v in values.values()) - 1.0)
    imaginary = max((abs(v.imag) for v in values.values()), default=0.0)
    if mass_error > tolerance or imaginary > tolerance or any(v.real < -tolerance for v in values.values()):
        raise ArithmeticError("marginal cancellation exceeds atol; use higher precision")
    clipped = -math.fsum(min(0.0, v.real) for v in values.values())
    if clipped > tolerance:
        raise ArithmeticError("aggregate negative marginal mass exceeds atol; use higher precision")
    return MarginalDistribution(
        selected, {key: max(0.0, v.real) for key, v in values.items()}, mass_error, imaginary, clipped
    )
