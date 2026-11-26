"""Associator form, isotropic strata, associative envelope and the dimension tower of the Lorentzian slice of A_5.

The slice holds y = sum_a x_a e_a + t e_26 with a in S = {1, 3, 4, 5, 6, 7}, A_a = L_(e_a), J = L_(e_26) and the
Clifford defect K_a = -(A_a J + J A_a)/2 of the record a5-null-slice-boost-algebra. This record checks, exactly:

- the defect is the symmetrized left associator, 2 K_a = [e_a, e_tau, .] + [e_tau, e_a, .], for every pair of distinct
  imaginary units of dimensions 16, 32 and 64, and L_y^T L_y = N(y) I + [y, y, .] at fixed integer points;
- over F_p at p = 32009 and p = 32003 the slice meets three null strata: nullity 4 on r^2 = t^2, nullity 12 on
  r^2 + t^2 = 0 with t != 0 (where y^2 = 0 and rank L_y^2 = 8), and nullity 16 on r^2 = 0 with t = 0;
- the associative algebra the seven slice tables generate over Q has dimension 256, is closed under transposition,
  and has a commutant of dimension 4 whose trace form on traceless elements has signature (2, 1); the six A_a and J eta,
  eta = I - 2 P_T, anticommute pairwise and square to -I;
- the two families of the earlier record from dimension 256 to 4096: the so(m,1) relations by direct check at
  dimensions 256 and 512 and the disjoint-star criterion at every level, with every sign row used compared with cd_core.

Independent items run through parallel.ordered_map. No random draw enters.
"""

from __future__ import annotations

import argparse
import functools
import hashlib
import json
import sys
from collections import Counter
from itertools import combinations, product
from pathlib import Path
from typing import Any

import numpy as np
from flint import fmpz_mat, nmod_mat

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import cd_core  # noqa: E402
import parallel  # noqa: E402

DIMENSION = 32
TIME = 26
SPACE: tuple[int, ...] = (1, 3, 4, 5, 6, 7)
TIME_SUPPORT: tuple[int, ...] = (2, 8, 18, 24)
ASSOCIATOR_DIMENSIONS: tuple[int, ...] = (16, 32, 64)
PRIMES: tuple[int, ...] = (32009, 32003)
GRID = 3
NULL_SPACE_POINTS = 12
NULL_SPACE_BOUND = 400
FAMILY_LEVELS: tuple[int, ...] = (8, 9, 10, 11, 12)
TRIPLE_LEVEL_LIMIT = 9
GRAM_POINTS: tuple[tuple[int, ...], ...] = ((1, 2, 0, -3), (2, -1, 1, 1), (3, 0, -2, 5))
SOURCE_FILES = (
    "gororoba_quantum/cd_core.py",
    "gororoba_quantum/parallel.py",
    "scripts/a5_null_slice_associator_envelope.py",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sign_rows(dimension: int, rows: list[int]) -> Any:
    """cd_sign(dimension, p, q) for p in rows and every q: the loop of cd_core.cd_sign run on integer arrays."""
    p = np.repeat(np.asarray(rows, dtype=np.int64)[:, None], dimension, axis=1)
    q = np.repeat(np.arange(dimension, dtype=np.int64)[None, :], len(rows), axis=0)
    sign = np.ones_like(p)
    live = np.ones(p.shape, dtype=bool)
    half = dimension >> 1
    while half > 0:
        p_hi = p >= half
        q_hi = q >= half
        low_high = live & ~p_hi & q_hi
        high_low = live & p_hi & ~q_hi
        high_high = live & p_hi & q_hi
        next_p, next_q = p.copy(), q.copy()
        next_p[low_high] = q[low_high] - half
        next_q[low_high] = p[low_high]
        next_p[high_low] = p[high_low] - half
        sign[high_low & (q != 0)] *= -1
        stop = high_high & (q - half == 0)
        sign[stop] *= -1
        live &= ~stop
        cont = high_high & ~stop
        next_p[cont] = q[cont] - half
        next_q[cont] = p[cont] - half
        p, q = next_p, next_q
        half >>= 1
    return sign


def sign_agreement_item(item: tuple[int, tuple[int, ...]]) -> int:
    """Number of entries of the vectorized rows that differ from cd_core.cd_sign."""
    dimension, rows = item
    table = sign_rows(dimension, list(rows))
    return sum(
        int(table[i, q]) != cd_core.cd_sign(dimension, row, q) for i, row in enumerate(rows) for q in range(dimension)
    )


def sign_disagreements(dimension: int, rows: set[int]) -> int:
    ordered = sorted(rows)
    chunks = [(dimension, tuple(ordered[i : i + 8])) for i in range(0, len(ordered), 8)]
    return sum(parallel.ordered_map(sign_agreement_item, chunks, min_items=1))


def table(signs: Any, index: int) -> Any:
    dimension = signs.shape[1]
    matrix = np.zeros((dimension, dimension), dtype=np.int64)
    matrix[np.arange(dimension) ^ index, np.arange(dimension)] = signs[index]
    return matrix


def full_tables(dimension: int) -> list[Any]:
    signs = sign_rows(dimension, list(range(dimension)))
    return [table(signs, k) for k in range(dimension)]


def integer_rank(matrices: list[Any]) -> int:
    return int(fmpz_mat([[int(v) for v in m.flatten()] for m in matrices]).rank())


def nullity(matrix: Any) -> int:
    return int(matrix.shape[0] - fmpz_mat(matrix.tolist()).rank())


def nullity_mod(matrix: Any, prime: int) -> int:
    return int(matrix.shape[0] - nmod_mat([[int(v) % prime for v in row] for row in matrix.tolist()], prime).rank())


def associator_item(dimension: int) -> dict[str, Any]:
    """2 K_a = [e_a, e_t, .] + [e_t, e_a, .] for all distinct imaginary a, t, and L_y^T L_y = N(y) I + [y, y, .]."""
    signs = sign_rows(dimension, list(range(dimension)))
    tables = [table(signs, k) for k in range(dimension)]

    def assoc(p: int, q: int) -> Any:
        return int(signs[p, q]) * tables[p ^ q] - tables[p] @ tables[q]

    failures = 0
    pairs = 0
    for t in range(1, dimension):
        for a in range(1, dimension):
            if a == t:
                continue
            pairs += 1
            defect2 = -(tables[a] @ tables[t] + tables[t] @ tables[a])
            if not np.array_equal(defect2, assoc(a, t) + assoc(t, a)):
                failures += 1
    gram_failures = 0
    indices = (1, 3, dimension // 2 + 2, dimension - 1)
    for coefficients in GRAM_POINTS:
        operator: Any = sum(c * tables[k] for c, k in zip(coefficients, indices, strict=True))
        vector = np.zeros(dimension, dtype=np.int64)
        for c, k in zip(coefficients, indices, strict=True):
            vector[k] += c
        square = operator @ vector
        left_square: Any = sum(int(square[k]) * tables[k] for k in range(dimension) if square[k])
        norm = sum(c * c for c in coefficients)
        if not np.array_equal(
            operator.T @ operator, norm * np.eye(dimension, dtype=np.int64) + left_square - operator @ operator
        ):
            gram_failures += 1
    return {
        "dimension": dimension,
        "pairs": pairs,
        "associator_failures": failures,
        "gram_points": len(GRAM_POINTS),
        "gram_failures": gram_failures,
    }


def square_root(value: int, prime: int) -> int | None:
    """A square root modulo an odd prime by Tonelli-Shanks, or None for a non-residue."""
    value %= prime
    if value == 0:
        return 0
    if pow(value, (prime - 1) // 2, prime) != 1:
        return None
    q, s = prime - 1, 0
    while q % 2 == 0:
        q //= 2
        s += 1
    z = 2
    while pow(z, (prime - 1) // 2, prime) != prime - 1:
        z += 1
    m, c, t, root = s, pow(z, q, prime), pow(value, q, prime), pow(value, (q + 1) // 2, prime)
    while t != 1:
        i, probe = 0, t
        while probe != 1:
            probe = probe * probe % prime
            i += 1
        b = pow(c, 1 << (m - i - 1), prime)
        m, c, t, root = i, b * b % prime, t * b * b % prime, root * b % prime
    return root


def slice_operator(tables: list[Any], x: tuple[int, ...], t: int) -> Any:
    return sum(v * tables[a] for v, a in zip(x, SPACE, strict=True)) + t * tables[TIME]


def square_vanishes(signs: Any, x: tuple[int, ...], t: int, prime: int) -> bool:
    coefficients = dict(zip(SPACE, x, strict=True))
    coefficients[TIME] = t
    out = [0] * DIMENSION
    for p, u in coefficients.items():
        for q, v in coefficients.items():
            out[p ^ q] += int(signs[p, q]) * u * v
    return all(value % prime == 0 for value in out)


def strata_item(prime: int) -> dict[str, Any]:
    """Nullity histograms of slice points on the three cones over F_prime."""
    signs = sign_rows(DIMENSION, list(range(DIMENSION)))
    tables = [table(signs, k) for k in range(DIMENSION)]
    euclidean: Counter[str] = Counter()
    lorentz: Counter[str] = Counter()
    for x in product(range(GRID), repeat=len(SPACE)):
        if not any(x):
            continue
        r2 = sum(v * v for v in x)
        t = square_root(-r2, prime)
        if t is not None and t != 0:
            operator = slice_operator(tables, x, t)
            square_rank = DIMENSION - nullity_mod(operator @ operator, prime)
            vanishes = square_vanishes(signs, x, t, prime)
            key = f"nullity {nullity_mod(operator, prime)}, rank L^2 {square_rank}, y^2 = 0 {vanishes}"
            euclidean[key] += 1
        t_real = square_root(r2, prime)
        if t_real is not None and t_real != 0:
            lorentz[f"nullity {nullity_mod(slice_operator(tables, x, t_real), prime)}"] += 1
    null_space: Counter[str] = Counter()
    found = 0
    for a in range(1, NULL_SPACE_BOUND):
        for b in range(a, NULL_SPACE_BOUND):
            c = square_root(-(a * a + b * b), prime)
            if c is None or c == 0 or found >= NULL_SPACE_POINTS:
                continue
            x = (a, b, c, 0, 0, 0)
            operator = slice_operator(tables, x, 0)
            null_space[
                f"nullity {nullity_mod(operator, prime)}, L^2 = 0 {not np.any((operator @ operator) % prime)}"
            ] += 1
            found += 1
        if found >= NULL_SPACE_POINTS:
            break
    return {
        "prime": prime,
        "euclidean_cone": dict(sorted(euclidean.items())),
        "lorentz_cone": dict(sorted(lorentz.items())),
        "null_space": dict(sorted(null_space.items())),
    }


GAUSSIAN_POINTS: tuple[tuple[tuple[int, ...], int], ...] = (
    ((1, 0, 0, 0, 0, 0), 1),
    ((3, 4, 0, 0, 0, 0), 5),
    ((1, 2, 2, 0, 0, 0), 3),
)


def gaussian_nullities() -> list[dict[str, Any]]:
    """Nullity over Q(i) of L_y for y = x + i t e_26 with r = t, from the rank of the 64 x 64 realification."""
    tables = full_tables(DIMENSION)
    out = []
    for x, t in GAUSSIAN_POINTS:
        real: Any = sum(v * tables[a] for v, a in zip(x, SPACE, strict=True))
        imaginary: Any = t * tables[TIME]
        block = np.block([[real, -imaginary], [imaginary, real]])
        complex_nullity = (2 * DIMENSION - int(fmpz_mat(block.tolist()).rank())) // 2
        out.append({"x": list(x), "t": t, "nullity": complex_nullity})
    return out


COMPLEX_LEVELS: tuple[int, ...] = (4, 5, 6)
COMPLEX_PAIRS_PER_LEVEL = 3
SPECTRUM_POINTS: tuple[tuple[str, tuple[int, ...], tuple[int, ...]], ...] = (
    ("e_1 + e_26", (1, 26), (1, 1)),
    ("e_1 + i e_26", (1, 26), (1, 2)),
    ("e_1 + i e_3", (1, 3), (1, 2)),
    ("e_1 + e_3", (1, 3), (1, 1)),
)


def real_form(real: Any, imaginary: Any) -> Any:
    return np.block([[real, -imaginary], [imaginary, real]])


def complex_nullity(real: Any, imaginary: Any) -> int:
    """Nullity over C of real + i imaginary, from the rank of its real form."""
    return (2 * real.shape[0] - int(fmpz_mat(real_form(real, imaginary).tolist()).rank())) // 2


def joint_nullity(blocks: list[tuple[Any, Any]]) -> int:
    """Dimension over C of the common kernel of several complex matrices given as (real, imaginary) pairs."""
    stacked = np.vstack([real_form(real, imaginary) for real, imaginary in blocks])
    return (2 * blocks[0][0].shape[1] - int(fmpz_mat(stacked.tolist()).rank())) // 2


def gram_multiplicities(real: Any, imaginary: Any) -> dict[str, int]:
    """Multiplicities of the eigenvalues 0, 2, 4 of the Hermitian Gram operator of real + i imaginary, exactly."""
    gram_real = real.T @ real + imaginary.T @ imaginary
    gram_imaginary = real.T @ imaginary - imaginary.T @ real
    eye = np.eye(real.shape[0], dtype=np.int64)
    return {str(value): complex_nullity(gram_real - value * eye, gram_imaginary) for value in (0, 2, 4)}


def complex_two_term() -> dict[str, Any]:
    """Kernels of complex two-term operands as eigenspaces of Hermitian involutions.

    For anticommuting imaginary units e_a, e_b the Gram operator of L_(e_a + i e_b) is 2 (I - i L_a L_b): its kernel is
    the +1 eigenspace of the involution i L_a L_b and its nullity is half the dimension. On the slice,
    L_(e_1 + i e_26) has the kernel ker K_1 n ker(i L_1 J - I).
    """
    levels = []
    for level in COMPLEX_LEVELS:
        dimension = 1 << level
        tables = full_tables(dimension)
        eye = np.eye(dimension, dtype=np.int64)
        pairs = anticommuting = identity_failures = 0
        kernel_rows: list[dict[str, Any]] = []
        for a, b in combinations(range(1, dimension), 2):
            first, second = tables[a], tables[b]
            pairs += 1
            if np.any(first @ second + second @ first):
                continue
            anticommuting += 1
            real_ok = np.array_equal(first.T @ first + second.T @ second, 2 * eye)
            imaginary_ok = np.array_equal(first.T @ second - second.T @ first, -2 * (first @ second))
            identity_failures += not (real_ok and imaginary_ok)
            if len(kernel_rows) < COMPLEX_PAIRS_PER_LEVEL:
                involution = first @ second
                operator_nullity = complex_nullity(first, second)
                eigenspace = complex_nullity(-eye, involution)
                joint = joint_nullity([(first, second), (-eye, involution)])
                kernel_rows.append(
                    {"pair": [a, b], "nullity": operator_nullity, "eigenspace": eigenspace, "joint": joint}
                )
        levels.append(
            {
                "dimension": dimension,
                "pairs": pairs,
                "anticommuting_pairs": anticommuting,
                "gram_identity_failures": identity_failures,
                "kernels": kernel_rows,
            }
        )
    tables = full_tables(DIMENSION)
    eye = np.eye(DIMENSION, dtype=np.int64)
    first, clock = tables[1], tables[TIME]
    defect = -(first @ clock + clock @ first) // 2
    zero = 0 * eye
    slice_kernel = {
        "nullity": complex_nullity(first, clock),
        "defect_and_involution": joint_nullity([(defect, zero), (-eye, first @ clock)]),
        "joint": joint_nullity([(first, clock), (defect, zero), (-eye, first @ clock)]),
    }
    spectra = {}
    for name, (a, b), (_, kind) in SPECTRUM_POINTS:
        real = tables[a] + (tables[b] if kind == 1 else zero)
        imaginary = tables[b] if kind == 2 else zero
        spectra[name] = gram_multiplicities(real, imaginary)
    return {"levels": levels, "slice_kernel": slice_kernel, "spectra": spectra}


def commutant_basis(generators: list[Any]) -> list[Any]:
    size = generators[0].shape[0]
    eye = np.eye(size, dtype=np.int64)
    rows: list[list[int]] = []
    for g in generators:
        rows.extend((np.kron(eye, g.T) - np.kron(g, eye)).tolist())
    kernel, dimension = fmpz_mat(rows).nullspace()
    return [
        np.array([int(kernel[i, c]) for i in range(size * size)], dtype=object).reshape(size, size)
        for c in range(int(dimension))
    ]


def anticommutant_dimension(generators: list[Any]) -> int:
    size = generators[0].shape[0]
    eye = np.eye(size, dtype=np.int64)
    rows: list[list[int]] = []
    for g in generators:
        rows.extend((np.kron(eye, g.T) + np.kron(g, eye)).tolist())
    return int(size * size - fmpz_mat(rows).rank())


def signature(gram: list[list[int]]) -> tuple[int, int]:
    """Positive and negative inertia of a symmetric integer matrix, from the signs of its rational eigenvalues' product
    structure: computed by symmetric Gaussian elimination over Q."""
    from fractions import Fraction

    matrix = [[Fraction(v) for v in row] for row in gram]
    n = len(matrix)
    positive = negative = 0
    active = list(range(n))
    while active:
        pivot = next((i for i in active if matrix[i][i] != 0), None)
        if pivot is None:
            pair = next(((i, j) for i in active for j in active if i < j and matrix[i][j] != 0), None)
            if pair is None:
                break
            i, j = pair
            for k in range(n):
                matrix[i][k] += matrix[j][k]
            for k in range(n):
                matrix[k][i] += matrix[k][j]
            continue
        d = matrix[pivot][pivot]
        positive += d > 0
        negative += d < 0
        active.remove(pivot)
        for i in active:
            factor = matrix[i][pivot] / d
            for k in range(n):
                matrix[i][k] -= factor * matrix[pivot][k]
            for k in range(n):
                matrix[k][i] -= factor * matrix[k][pivot]
    return positive, negative


def envelope() -> dict[str, Any]:
    """The associative algebra generated by A_a (a in S) and J over Q, its commutant and seven anticommuting units."""
    tables = full_tables(DIMENSION)
    generators = [tables[a] for a in SPACE] + [tables[TIME]]
    basis = [np.eye(DIMENSION, dtype=np.int64)]
    frontier = list(basis)
    growth = [1]
    while frontier:
        new: list[Any] = []
        for m in frontier:
            for g in generators:
                candidate = g @ m
                if integer_rank(basis + new + [candidate]) > len(basis) + len(new):
                    new.append(candidate)
        basis += new
        frontier = new
        if new:
            growth.append(len(basis))
    closure_rank = integer_rank(basis + [g @ m for g in generators for m in basis])
    transpose_rank = integer_rank(basis + [m.T for m in basis])
    commutant = commutant_basis(generators)
    eye = np.eye(DIMENSION, dtype=object)
    traceless = [c * DIMENSION - sum(c[i, i] for i in range(DIMENSION)) * eye for c in commutant]
    gram = [[int(sum((x @ y)[i, i] for i in range(DIMENSION))) for y in traceless] for x in traceless]
    commutant_commutative = all(np.array_equal(x @ y, y @ x) for x, y in combinations(commutant, 2))
    commutant_closed = integer_rank(commutant + [x @ y for x in commutant for y in commutant]) == len(commutant)
    spatial_commutant = len(commutant_basis([tables[a] for a in SPACE]))
    full_commutant = len(commutant_basis(tables[1:]))
    eta: Any = np.eye(DIMENSION, dtype=np.int64)
    for index in TIME_SUPPORT:
        eta[index, index] = -1
    clock: Any = tables[TIME] @ eta
    units = [tables[a] for a in SPACE] + [clock]
    eye64 = np.eye(DIMENSION, dtype=np.int64)
    anticommuting = all(np.array_equal(u @ v + v @ u, 0 * eye64) for u, v in combinations(units, 2))
    squares = all(np.array_equal(u @ u, -eye64) for u in units)
    volume: Any = units[0]
    for u in units[1:]:
        volume = volume @ u
    eta_in_envelope = integer_rank(basis + [eta]) == len(basis)
    sign_d8: Any = np.diag([-1 if (i >> 3) & 1 else 1 for i in range(DIMENSION)]).astype(np.int64)
    eighth: Any = tables[2] @ sign_d8
    eight = [*units, eighth]
    eighth_anticommutes = all(np.array_equal(eighth @ u + u @ eighth, 0 * eye64) for u in units)
    monomials: list[Any] = []
    for mask in range(1 << len(eight)):
        product_matrix: Any = eye64.copy()
        for bit, unit in enumerate(eight):
            if (mask >> bit) & 1:
                product_matrix = product_matrix @ unit
        monomials.append(product_matrix)
    monomial_rank = integer_rank(monomials)
    clock_in_span = integer_rank([*monomials, tables[TIME]]) == monomial_rank
    eighth_in_envelope = integer_rank([*basis, eighth]) == len(basis)
    return {
        "dimension_by_word_length": growth,
        "dimension": len(basis),
        "closed_under_products": closure_rank == len(basis),
        "closed_under_transpose": transpose_rank == len(basis),
        "commutant_dimension": len(commutant),
        "commutant_closed_under_products": commutant_closed,
        "commutant_is_commutative": commutant_commutative,
        "commutant_trace_form_signature": list(signature(gram)),
        "commutant_traceless_rank": integer_rank(traceless),
        "spatial_commutant_dimension": spatial_commutant,
        "all_imaginary_tables_commutant_dimension": full_commutant,
        "eta_in_envelope": eta_in_envelope,
        "seven_units_anticommute": anticommuting,
        "seven_units_square_to_minus_one": squares,
        "volume_is_scalar": bool(np.array_equal(volume, eye64) or np.array_equal(volume, -eye64)),
        "volume_square_is_identity": bool(np.array_equal(volume @ volume, eye64)),
        "anticommutant_dimension_of_seven_units": anticommutant_dimension(units),
        "eighth_unit": "L_(e_2) D_8, D_8 = diag((-1)^(bit 3 of i))",
        "eighth_unit_anticommutes": eighth_anticommutes,
        "eighth_unit_square_is_minus_one": bool(np.array_equal(eighth @ eighth, -eye64)),
        "eighth_unit_in_envelope": eighth_in_envelope,
        "clifford_monomial_rank": monomial_rank,
        "clock_in_clifford_span": clock_in_span,
    }


def defect_weights(dimension: int, rows: dict[int, Any], a: int, tau: int) -> Any:
    """K_a e_q = c[q] e_(q ^ a ^ tau), c = -(s_tau(q) s_a(tau ^ q) + s_a(q) s_tau(a ^ q)) / 2."""
    q = np.arange(dimension)
    c = -(rows[tau][q] * rows[a][tau ^ q] + rows[a][q] * rows[tau][a ^ q])
    return c // 2


def compose(x: dict[int, Any], y: dict[int, Any], dimension: int) -> dict[int, Any]:
    index = np.arange(dimension)
    out: dict[int, Any] = {}
    for m2, w2 in y.items():
        for m1, w1 in x.items():
            out[m1 ^ m2] = out.get(m1 ^ m2, 0) + w2 * w1[index ^ m2]
    return {m: w for m, w in out.items() if np.any(w)}


def combine(x: dict[int, Any], y: dict[int, Any], scale: int) -> dict[int, Any]:
    out = {m: w.copy() for m, w in x.items()}
    for m, w in y.items():
        out[m] = out.get(m, 0) + scale * w
    return {m: w for m, w in out.items() if np.any(w)}


@functools.lru_cache(maxsize=4)
def cached_defects(dimension: int, tau: int, space: tuple[int, ...]) -> dict[int, dict[int, Any]]:
    used = sorted({*space, tau})
    rows = {k: v.astype(np.int64) for k, v in zip(used, sign_rows(dimension, used), strict=True)}
    return {c: {c ^ tau: defect_weights(dimension, rows, c, tau)} for c in space}


def triple_item(item: tuple[int, int, tuple[int, ...], int, int]) -> int:
    """Failures of [[K_a, K_b], K_c] = delta_bc K_a - delta_ac K_b over c in the space, for one pair a < b."""
    dimension, tau, space, a, b = item
    defects = cached_defects(dimension, tau, space)
    ab = combine(compose(defects[a], defects[b], dimension), compose(defects[b], defects[a], dimension), -1)
    failures = 0
    for c in space:
        lhs = combine(compose(ab, defects[c], dimension), compose(defects[c], ab, dimension), -1)
        rhs: dict[int, Any] = {}
        if b == c:
            rhs = combine(rhs, defects[a], 1)
        if a == c:
            rhs = combine(rhs, defects[b], -1)
        failures += bool(combine(lhs, rhs, -1))
    return failures


def stars(dimension: int, rows: dict[int, Any], tau: int, space: tuple[int, ...]) -> dict[str, Any]:
    supports: dict[int, set[int]] = {}
    images: dict[int, dict[int, int]] = {}
    for a in space:
        weights = defect_weights(dimension, rows, a, tau)
        nonzero = [int(q) for q in np.nonzero(weights)[0]]
        supports[a] = set(nonzero)
        images[a] = {q: q ^ a ^ tau for q in nonzero}
    common = set.intersection(*supports.values())
    leaves = {a: supports[a] - common for a in space}
    stars_ok = bool(common) and all({images[a][m] for m in common} == leaves[a] for a in space)
    disjoint = stars_ok and all(not (leaves[a] & leaves[b]) for a, b in combinations(space, 2))
    return {
        "disjoint_stars": disjoint,
        "common_support": len(common),
        "common_kernel": dimension - len(set().union(*supports.values())),
    }


def clifford_space(dimension: int, rows: dict[int, Any], space: tuple[int, ...]) -> bool:
    q = np.arange(dimension)
    return all(not np.any(rows[b][q] * rows[a][b ^ q] + rows[a][q] * rows[b][a ^ q]) for a, b in combinations(space, 2))


def block_nullity(dimension: int, rows: dict[int, Any], coefficients: dict[int, int]) -> int:
    """Nullity of L_y for y = sum c_k e_k: L_y preserves each coset of the XOR group of the support."""
    group = {0}
    for k in coefficients:
        group |= {g ^ k for g in group}
    seen: set[int] = set()
    total = 0
    for base in range(dimension):
        if base in seen:
            continue
        coset = sorted(base ^ g for g in group)
        seen |= set(coset)
        position = {v: i for i, v in enumerate(coset)}
        matrix = [[0] * len(coset) for _ in coset]
        for q in coset:
            for k, value in coefficients.items():
                matrix[position[k ^ q]][position[q]] += value * int(rows[k][q])
        total += len(coset) - int(fmpz_mat(matrix).rank())
    return total


def family_specs(levels: tuple[int, ...]) -> list[tuple[int, str, int, tuple[int, ...]]]:
    """(level, family, time index, space) of the two families at each level."""
    specs = []
    for level in levels:
        specs.append(
            (
                level,
                "time 7 * 2^(n-3)",
                7 << (level - 3),
                tuple(i for i in range(1, 1 << (level - 2)) if i != 1 << (level - 3)),
            )
        )
        specs.append((level, "octonion space", (1 << (level - 1)) + (1 << (level - 2)) + 8, tuple(range(1, 8))))
    return specs


def family_structure_item(spec: tuple[int, str, int, tuple[int, ...]]) -> dict[str, Any]:
    """Stars, the Clifford test of the space and the nullity at a null point of one family slice."""
    level, family, tau, space = spec
    dimension = 1 << level
    used = sorted({*space, tau})
    rows = {k: v.astype(np.int64) for k, v in zip(used, sign_rows(dimension, used), strict=True)}
    row: dict[str, Any] = {"family": family, "level": level, "dimension": dimension, "time": tau}
    row["space_size"] = len(space)
    row["sign_rows_checked"] = len(used)
    row.update(stars(dimension, rows, tau, space))
    row["space_clifford"] = clifford_space(dimension, rows, space)
    row["null_point_nullity"] = block_nullity(dimension, rows, {space[0]: 3, space[1]: 4, tau: 5})
    return row


def family_rows_for(levels: tuple[int, ...]) -> list[dict[str, Any]]:
    """Every family row of the levels, with structure, sign checks and relation checks each mapped as one flat pool."""
    specs = family_specs(levels)
    rows = parallel.ordered_map(family_structure_item, specs, min_items=1)
    sign_tasks: list[tuple[int, tuple[int, ...]]] = []
    sign_owner: list[int] = []
    triple_tasks: list[tuple[int, int, tuple[int, ...], int, int]] = []
    triple_owner: list[int] = []
    for index, (level, _family, tau, space) in enumerate(specs):
        dimension = 1 << level
        used = sorted({*space, tau})
        for start in range(0, len(used), 8):
            sign_tasks.append((dimension, tuple(used[start : start + 8])))
            sign_owner.append(index)
        if level <= TRIPLE_LEVEL_LIMIT or len(space) <= 8:
            for a, b in combinations(space, 2):
                triple_tasks.append((dimension, tau, space, a, b))
                triple_owner.append(index)
    sign_counts = parallel.ordered_map(sign_agreement_item, sign_tasks, min_items=1)
    triple_counts = parallel.ordered_map(triple_item, triple_tasks, min_items=1)
    for index, row in enumerate(rows):
        row["sign_disagreements"] = sum(c for c, owner in zip(sign_counts, sign_owner, strict=True) if owner == index)
        failures = [c for c, owner in zip(triple_counts, triple_owner, strict=True) if owner == index]
        row["triple_relations"] = [len(failures) * row["space_size"], sum(failures)] if failures else None
    return rows


def family_rows(level: int) -> list[dict[str, Any]]:
    return family_rows_for((level,))


def two_term_strata() -> dict[str, Any]:
    """Nullity of e_j + e_tau, 1 <= j < 16 <= tau, j ^ tau != 16, against the strut s = j ^ tau ^ 16."""
    tables = full_tables(DIMENSION)
    counts: Counter[int] = Counter()
    four_high = True
    strut_equals_low = 0
    criterion_agreements = 0
    for j in range(1, 16):
        for tau in range(16, 32):
            if j ^ tau == 16:
                continue
            n = nullity(tables[j] + tables[tau])
            counts[n] += 1
            k = tau - 16
            strut_equals_low += k == 0
            low, high = sorted((j, k))
            independent = 1 <= low <= 7 and 9 <= high <= 15 and high != low + 8
            criterion_agreements += (n == 4) == independent
            if n == 4:
                four_high &= (j ^ tau ^ 16) > 8
    slice_struts = {str(a): a ^ TIME ^ 16 for a in SPACE}
    return {
        "histogram": {str(k): v for k, v in sorted(counts.items())},
        "nullity_4_struts_above_8": four_high,
        "slice_struts": slice_struts,
        "strut_equals_low_index": strut_equals_low,
        "independence_criterion_agreements": criterion_agreements,
    }


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def section_item(task: tuple[str, int]) -> Any:
    """One independent section: an associator dimension, a prime, the envelope, the two-term strata or Q(i)."""
    name, parameter = task
    if name == "associator":
        return associator_item(parameter)
    if name == "strata":
        return strata_item(parameter)
    if name == "envelope":
        return envelope()
    if name == "two_term_strata":
        return two_term_strata()
    if name == "complex_two_term":
        return complex_two_term()
    return gaussian_nullities()


def compute() -> dict[str, Any]:
    tasks = [("associator", d) for d in ASSOCIATOR_DIMENSIONS] + [("strata", p) for p in PRIMES]
    tasks += [("envelope", 0), ("two_term_strata", 0), ("gaussian", 0), ("complex_two_term", 0)]
    results = parallel.ordered_map(section_item, tasks, min_items=1)
    count = len(ASSOCIATOR_DIMENSIONS)
    associator = results[:count]
    strata = results[count : count + len(PRIMES)]
    envelope_result, two_term, gaussian, complex_result = results[count + len(PRIMES) :]
    families = family_rows_for(FAMILY_LEVELS)
    return {
        "schema": "a5-null-slice-associator-envelope/1",
        "sources": {name: sha256(ROOT / name) for name in SOURCE_FILES},
        "slice": {"dimension": DIMENSION, "time": TIME, "space": list(SPACE), "time_support": list(TIME_SUPPORT)},
        "associator": associator,
        "strata": strata,
        "gaussian_euclidean_cone": gaussian,
        "complex_two_term": complex_result,
        "envelope": envelope_result,
        "two_term_strata": two_term,
        "families": families,
    }


def validate(result: dict[str, Any]) -> None:
    require([row["dimension"] for row in result["associator"]] == list(ASSOCIATOR_DIMENSIONS), "associator dimensions")
    for row in result["associator"]:
        dimension = row["dimension"]
        require(row["pairs"] == (dimension - 1) * (dimension - 2), f"associator pairs at {dimension}")
        require(row["gram_points"] == len(GRAM_POINTS), f"Gram points at {dimension}")
        require(
            row["associator_failures"] == 0 and row["gram_failures"] == 0, f"associator identity fails at {dimension}"
        )
    require([row["prime"] for row in result["strata"]] == list(PRIMES), "strata primes")
    expected_counts = {32009: (411, 411), 32003: (409, 319)}
    for row in result["strata"]:
        p = row["prime"]
        lorentz, euclidean = expected_counts[p]
        require(row["euclidean_cone"] == {"nullity 12, rank L^2 8, y^2 = 0 True": euclidean}, f"Euclidean cone at {p}")
        require(row["lorentz_cone"] == {"nullity 4": lorentz}, f"Lorentz cone at {p}")
        require(row["null_space"] == {"nullity 16, L^2 = 0 True": NULL_SPACE_POINTS}, f"null space at {p}")
    gaussian = result["gaussian_euclidean_cone"]
    require(len(gaussian) == len(GAUSSIAN_POINTS) and all(row["nullity"] == 12 for row in gaussian), "Q(i) cone")
    env = result["envelope"]
    require(env["dimension_by_word_length"] == [1, 8, 35, 111, 210, 255, 256], "envelope growth")
    require(env["dimension"] == 256 and env["closed_under_products"] and env["closed_under_transpose"], "envelope")
    require(env["commutant_dimension"] == 4 and env["commutant_trace_form_signature"] == [2, 1], "commutant type")
    require(env["commutant_traceless_rank"] == 3, "commutant traceless part")
    require(env["commutant_closed_under_products"] and not env["commutant_is_commutative"], "commutant is M_2(R)")
    require(
        env["spatial_commutant_dimension"] == 16 and env["all_imaginary_tables_commutant_dimension"] == 1, "commutants"
    )
    require(
        env["eta_in_envelope"] and env["seven_units_anticommute"] and env["seven_units_square_to_minus_one"], "units"
    )
    require(not env["volume_is_scalar"] and env["volume_square_is_identity"], "volume of the seven units")
    require(env["anticommutant_dimension_of_seven_units"] == 8, "anticommutant dimension")
    require(env["eighth_unit_anticommutes"] and env["eighth_unit_square_is_minus_one"], "eighth unit")
    require(env["eighth_unit_in_envelope"] and env["clifford_monomial_rank"] == 256, "Cl(0,8) monomials")
    require(env["clock_in_clifford_span"], "J in the Clifford span")
    strata = result["two_term_strata"]
    require(
        strata["histogram"] == {"0": 15, "4": 84, "12": 126} and strata["nullity_4_struts_above_8"], "two-term strata"
    )
    require(strata["slice_struts"] == {"1": 11, "3": 9, "4": 14, "5": 15, "6": 12, "7": 13}, "slice struts")
    require(strata["strut_equals_low_index"] == 15, "nullity-0 pairs")
    require(strata["independence_criterion_agreements"] == 225, "independence criterion")
    complex_result = result["complex_two_term"]
    require(
        [row["dimension"] for row in complex_result["levels"]] == [1 << n for n in COMPLEX_LEVELS], "complex levels"
    )
    for row in complex_result["levels"]:
        half = row["dimension"] // 2
        require(
            row["gram_identity_failures"] == 0 and row["anticommuting_pairs"] > 0, f"complex Gram at {row['dimension']}"
        )
        require(len(row["kernels"]) == COMPLEX_PAIRS_PER_LEVEL, f"complex kernels at {row['dimension']}")
        for kernel in row["kernels"]:
            require(kernel["nullity"] == kernel["eigenspace"] == kernel["joint"] == half, f"involution kernel {kernel}")
    require(complex_result["slice_kernel"] == {"nullity": 12, "defect_and_involution": 12, "joint": 12}, "slice kernel")
    require(
        complex_result["spectra"]
        == {
            "e_1 + e_26": {"0": 4, "2": 24, "4": 4},
            "e_1 + i e_26": {"0": 12, "2": 8, "4": 12},
            "e_1 + i e_3": {"0": 16, "2": 0, "4": 16},
            "e_1 + e_3": {"0": 0, "2": 32, "4": 0},
        },
        "Gram spectra",
    )
    families = result["families"]
    require(
        [(row["level"], row["family"]) for row in families]
        == [(n, f) for n in FAMILY_LEVELS for f in ("time 7 * 2^(n-3)", "octonion space")],
        "family rows",
    )
    expected_relations = {8: 117242, 9: 992250}
    for row in families:
        tag = f"{row['family']} level {row['level']}"
        require(row["sign_disagreements"] == 0 and row["disjoint_stars"] and row["common_support"] == 4, tag)
        require(row["sign_rows_checked"] == row["space_size"] + 1, tag)
        require(row["null_point_nullity"] == 4, tag)
        if row["family"] == "octonion space":
            require(row["space_clifford"] and row["triple_relations"] == [147, 0], tag)
            require(row["common_kernel"] == row["dimension"] - 32, tag)
        else:
            require(row["common_kernel"] == 4, tag)
            if row["level"] <= TRIPLE_LEVEL_LIMIT:
                require(row["triple_relations"] == [expected_relations[row["level"]], 0], tag)
            else:
                require(row["triple_relations"] is None, tag)


def control(holds: bool, fails: bool, name: str) -> None:
    require(holds and fails, f"self-test control {name}: holds {holds}, mutant fails {fails}")


def self_test() -> None:
    signs = sign_rows(DIMENSION, list(range(DIMENSION)))
    reference = np.array([[cd_core.cd_sign(DIMENSION, p, q) for q in range(DIMENSION)] for p in range(DIMENSION)])
    mutant_signs = signs.copy()
    mutant_signs[3, 5] *= -1
    control(np.array_equal(signs, reference), not np.array_equal(mutant_signs, reference), "vectorized signs")
    tables = [table(signs, k) for k in range(DIMENSION)]
    a, t = 1, TIME
    defect2 = -(tables[a] @ tables[t] + tables[t] @ tables[a])
    assoc = (int(signs[a, t]) + int(signs[t, a])) * tables[a ^ t] - tables[a] @ tables[t] - tables[t] @ tables[a]
    symmetric = int(signs[a, t]) - int(signs[t, a])
    assoc_mutant = symmetric * tables[a ^ t] - tables[a] @ tables[t] - tables[t] @ tables[a]
    control(
        np.array_equal(defect2, assoc),
        not np.array_equal(defect2, assoc_mutant),
        "associator form against e_a e_t = e_t e_a",
    )
    prime, i = 32009, 10754
    on_cone = slice_operator(tables, (1, 0, 0, 0, 0, 0), i)
    off_cone = slice_operator(tables, (1, 0, 0, 0, 0, 0), i + 1)
    control(
        nullity_mod(on_cone, prime) == 12, nullity_mod(off_cone, prime) == 0, "Euclidean cone point against t = i + 1"
    )
    null_x = (1, i, 0, 0, 0, 0)
    off_x = (1, i + 1, 0, 0, 0, 0)
    control(
        nullity_mod(slice_operator(tables, null_x, 0), prime) == 16,
        nullity_mod(slice_operator(tables, off_x, 0), prime) == 0,
        "null space point against x_3 = i + 1",
    )
    slice_commutant = len(commutant_basis([tables[k] for k in SPACE] + [tables[TIME]]))
    moved = len(commutant_basis([tables[k] for k in SPACE] + [tables[2]]))
    control(slice_commutant == 4, moved == 8, "commutant against time index 2")
    used = sorted({*SPACE, 9, TIME})
    rows = {k: v.astype(np.int64) for k, v in zip(used, sign_rows(DIMENSION, used), strict=True)}
    clean = stars(DIMENSION, rows, TIME, SPACE)
    widened = stars(DIMENSION, rows, TIME, (*SPACE, 9))
    control(
        clean["disjoint_stars"],
        widened["common_support"] == 4 and not widened["disjoint_stars"],
        "stars against e_9 added to the space, with the common support kept",
    )
    fine = sum(triple_item((DIMENSION, TIME, SPACE, a, b)) for a, b in combinations(SPACE, 2))
    moved_space = (1, 2, 3, 4, 5, 6)
    coarse = sum(triple_item((DIMENSION, TIME, moved_space, a, b)) for a, b in combinations(moved_space, 2))
    control(fine == 0, coarse > 0, "triple relations on S against e_2 in place of e_7")


def dumps(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=1, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--out", type=Path)
    mode.add_argument("--check", type=Path)
    mode.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        print("self-test: 7 paired controls pass")
        return 0
    result = compute()
    validate(result)
    text = dumps(result)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
        print(f"wrote {args.out}")
        return 0
    if args.check.read_text(encoding="utf-8") != text:
        print("record differs from its recomputation", file=sys.stderr)
        return 1
    print("record matches its recomputation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
