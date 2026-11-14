"""The kernel product as a polynomial tensor: T(z) = -grad(Q G)(z) (x) z on V(Q) u V(G), exact over Q(i).

V, M(z), K(z) = ker M(z), Q and G are those of `kernel_plane_identities.py`: V is the 15-dimensional space of
imaginary sedenions with coordinates t_1, ..., t_15, M(z) v = Im(z v) is skew, and G = Q^2 - 4 Delta with
Delta = N1 N3 - p^2.

For a triple I = (i_1 < i_2 < i_3) of indices, P_I(z) = eps(I) Pf(M(z) with the rows and columns of I removed),
eps(I) the sign of the permutation (I, complement of I in increasing order). P(z) = sum_I P_I(z) e_I is a
three-vector whose coordinates are integer polynomials of degree 6 in z. The twelve-form pi = sum_J Pf(M_J) t_J
over the 12-subsets J is the sixth divided power of the two-form of M(z), and it transforms by congruence with
integer polynomial coefficients: Pf((U^T M U)_J) = sum_J' Pf(M_J') det(U_(J', J)) for every matrix U. Over any
field an alternating matrix of rank 12 is congruent to six blocks ((0, 1), (-1, 0)) and a zero block of order 3
whose columns of U span K(z); in that basis pi is the product of the first twelve coordinates. So pi is nonzero
exactly when rank M(z) >= 12, and at rank 12 its dual P(z) under the volume form is a nonzero multiple of
k_1 ^ k_2 ^ k_3 for a basis of K(z). No step divides by an integer.

tau: Lambda^3 V -> V (x) V sends a ^ b ^ c to Im(a b) (x) c + Im(b c) (x) a + Im(c a) (x) b, and T(z) = tau(P(z)),
a 15 x 15 array of polynomials of degree 6 in z. At a rank-12 point z lies in K(z) and Im(z k) = 0 on K(z), so
with K(z) = C z + C k_1 + C k_2 and P(z) = c z ^ k_1 ^ k_2, c nonzero, T(z) = c M(k_1) k_2 (x) z: T(z) vanishes
exactly when the product on K(z) does.

The identity under test is T(z) = -grad(Q G)(z) (x) z on the zero-divisor variety V(Q G) = V(Q) u V(G), with
grad(Q G) = G grad Q + Q grad G, grad Q = 2 z and grad G = 4 Q z - 4 grad Delta. On V(Q) it reads
T = -2 G z (x) z and on V(G) it reads T = -Q grad G (x) z.

Each entry of T + grad(Q G) (x) z has degree 6 and vanishes on V(Q) u V(G); Q and G are distinct absolutely
irreducible polynomials (ledger row A5-357) and Q G has degree 6, so T + grad(Q G) (x) z = Q G L for a matrix L of
constants, and one point off the variety determines L: T(z) = -grad(Q G)(z) (x) z - Q(z) G(z) I at every point
of V, I the identity matrix.

The record holds six groups of exact computations over Q(i).

1. `calibration`: the Pfaffian routine on a 4 x 4 integer matrix against a_12 a_34 - a_13 a_24 + a_14 a_23, and
   Pf^2 = det on the first 12 x 12 principal block of M(z) with a nonzero Pfaffian at one grid point.
2. `grids`: the identity, all 225 entries, on a grid of each of the families `FQ`, `FG+` and `FG-` of
   `kernel_plane_identities.py`. Each entry of T + grad(Q G) (x) z is homogeneous of degree 6 in z.
   - `FQ` (a slice of V(Q)): each coordinate has degree at most 1 in each of A, B and C, so an entry has degree at
     most 6 in each; (B, C) -> (t B, t C) scales z by t, so an entry that vanishes at C = 1 vanishes for every
     nonzero C; a polynomial of degree at most 6 in A and in B that vanishes on a 7 x 7 grid is zero.
   - `FG+`, `FG-` (slices of V(G)): each coordinate has degree at most 1 in m and at most 2 in u, so an entry has
     degree at most 6 in m and at most 12 in u and vanishes when it vanishes on a 7 x 13 grid. The family is the
     section t = 1 of the cone (beta, lambda, s -+ m) = t (u^2 - 1, i (u^2 + 1), 2 u), and the entry is
     homogeneous, so it vanishes on the cone.
   The grids therefore decide the identity on the three families, as polynomials in the generators.
3. `special_points`: exact points with N1(z) = 0, two of V(Q) minus V(G) and one of V(G) minus V(Q), outside the
   orbits that the families meet, with Q, G, N1, dim K(z), whether the identity holds, whether T vanishes and
   whether P is a nonzero multiple of the three-vector of a basis of K(z).
4. `singular_points`: three exact points of {t_8 = 0, N1 = N3, p = 0} off V(Q), the singular locus of V(G) off
   V(Q), with Q, G, whether grad G vanishes and dim K(z).
5. `general_points`: two exact points off V(Q) u V(G) with Q, G, dim K(z) and whether
   T = -grad(Q G) (x) z - Q G I there.
6. `fixtures`: at the 66 exact fixtures of `nullity4-kernel-gauss-result.json`, counted per stratum: whether
   T = -2 G z (x) z, whether T = -grad(Q G) (x) z, whether T = 0, whether P is a nonzero multiple of the
   three-vector of K(z), whether every row of T is a multiple of z and whether the polar form of Q vanishes on
   K(z).

`verdict` compares the fields and value types of a record with those of the record that the constants of this
module determine, then the input digests, then each group by name, then the serialized text; a record passes
exactly when it is that record.

The grid points, the special points, the singular points, the general points and the fixtures run through
`parallel.ordered_map`, one point per item; the 455 Pfaffians of a point stay in its worker, since a pool
inside a pool worker would exceed the worker budget.

`--write` writes kernel-product-pfaffian-tensor-result.json beside this file; `--check` recomputes and compares.

Run from the repository root:
"$PYTHON" docs/evidence/a5-kernel-bundles-residuals/kernel_product_pfaffian_tensor.py --check
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import sympy as sp
from sympy import QQ_I
from sympy.polys.matrices import DomainMatrix

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BUNDLES = HERE.parent / "a5-kernel-bundles"
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(BUNDLES))

from kernel_plane_identities import (  # noqa: E402
    COUNTEREXAMPLE_POINT,
    SEDENION,
    _frame,
    block,
    family_point,
    form,
)
from kernel_three_plane_zero_divisors import _exact_block, _exact_kernel  # noqa: E402
from nullity4_gauss_image import FIXTURES, STRATA, _fixture_splits  # noqa: E402

import parallel  # noqa: E402

SCHEMA = "a5-kernel-bundles-residuals-kernel-product-pfaffian-tensor-v1"
RECORD = HERE / "kernel-product-pfaffian-tensor-result.json"
SOURCE_PATHS = (
    HERE / "kernel_product_pfaffian_tensor.py",
    HERE / "kernel_plane_identities.py",
    HERE / "nullity4_gauss_image.py",
    HERE / "kernel_three_plane_zero_divisors.py",
    FIXTURES,
    ROOT / "gororoba_quantum" / "cd_core.py",
)
FIELD = "Q(i)"

IMAGINARY = 15
TRIPLES = tuple(itertools.combinations(range(IMAGINARY), 3))
# T(z) = CONSTANT * G(z) * z (x) z on V(Q), under the sign eps(I) of the module docstring.
CONSTANT = -2
CALIBRATION_MATRIX = ((0, 1, 2, 3), (-1, 0, 4, 5), (-2, -4, 0, 6), (-3, -5, -6, 0))
CALIBRATION = {"pfaffian_4x4": "8", "pfaffian_squared_is_determinant": True}
# Grid values of the two generators of each family (FQ at C = 1). On FQ the diagonal A = B is the locus s = 0,
# where G = 0; on FG- the three points m = 2 u have s = 0 and Q = 0, and rank M(z) is below 12 there.
GRID_VALUES = {
    "FQ": (tuple(range(1, 8)), tuple(range(1, 8))),
    "FG+": (tuple(range(1, 8)), tuple(range(1, 14))),
    "FG-": (tuple(range(1, 8)), tuple(range(1, 14))),
}
GRID_FIELDS = ("gradient_identity_holds", "rank_twelve", "quadric_zero", "quartic_zero", "tensor_zero")
GRID_COUNTS = {
    "FQ": dict(zip(("points", *GRID_FIELDS), (49, 49, 42, 49, 7, 7), strict=True)),
    "FG+": dict(zip(("points", *GRID_FIELDS), (91, 91, 91, 0, 91, 0), strict=True)),
    "FG-": dict(zip(("points", *GRID_FIELDS), (91, 91, 88, 3, 91, 3), strict=True)),
}
# z = (a, beta, b). The first two points have a = e_1 + i e_2 null and N1(a, b) = 1 and lie on V(Q) minus V(G);
# the third is the point of V(G) minus V(Q) with N1(z) = 0 of `kernel_plane_identities.py`.
POINT_FIELDS = ("kernel_dimension", "gradient_identity_holds", "tensor_zero", "three_vector_spans_kernel")
SPECIAL_POINTS = (
    ["1", "I", "0", "0", "0", "0", "0", "I", "1", "0", "0", "0", "0", "0", "0"],
    ["1", "I", "0", "0", "0", "0", "0", "0", "1", "0", "0", "I", "0", "0", "0"],
    list(COUNTEREXAMPLE_POINT),
)
SPECIAL_POINT_FACTS = (
    {"Q": "0", "G": "4", "N1": "0"} | dict(zip(POINT_FIELDS, (3, True, False, True), strict=True)),
    {"Q": "0", "G": "4", "N1": "0"} | dict(zip(POINT_FIELDS, (3, True, False, True), strict=True)),
    {"Q": "4", "G": "0", "N1": "0"} | dict(zip(POINT_FIELDS, (3, True, False, True), strict=True)),
)
# (a, 0, b) with N1 = N3 and p = 0: (e_1, e_2), (e_1, e_3) and (2 e_1 + e_4, e_2 + 2 e_5).
SINGULAR_POINTS = (
    ["1", "0", "0", "0", "0", "0", "0", "0", "0", "1", "0", "0", "0", "0", "0"],
    ["1", "0", "0", "0", "0", "0", "0", "0", "0", "0", "1", "0", "0", "0", "0"],
    ["2", "0", "0", "1", "0", "0", "0", "0", "0", "1", "0", "0", "2", "0", "0"],
)
SINGULAR_POINT_FACTS = (
    {"Q": "2", "G": "0", "quartic_gradient_zero": True, "kernel_dimension": 5},
    {"Q": "2", "G": "0", "quartic_gradient_zero": True, "kernel_dimension": 5},
    {"Q": "10", "G": "0", "quartic_gradient_zero": True, "kernel_dimension": 5},
)
# Two points off V(Q) u V(G), where rank M(z) = 14 and K(z) = C z.
GENERAL_POINTS = (
    ["3", "-1", "4", "1", "-5", "9", "2", "6", "-5", "3", "5", "-8", "9", "7", "-9"],
    ["2", "7", "-1", "8", "2", "-8", "1", "8", "2", "-8", "4", "5", "-9", "I", "4"],
)
GENERAL_POINT_FACTS = (
    {"Q": "507", "G": "74161", "kernel_dimension": 1, "global_identity_holds": True},
    {"Q": "456", "G": "57940 + 1920*I", "kernel_dimension": 1, "global_identity_holds": True},
)
# Per stratum: fixtures, those at which T = -2 G z (x) z, those at which T = -grad(Q G) (x) z, those at which
# T = 0, those at which P is a nonzero multiple of the three-vector of K(z), those at which T = w (x) z and those
# at which Q vanishes on K(z).
FIXTURE_FIELDS = (
    "identity_holds",
    "gradient_identity_holds",
    "tensor_zero",
    "three_vector_spans_kernel",
    "right_factor_is_point",
    "kernel_is_null",
)
FIXTURE_COUNTS = {
    STRATA[0]: dict(zip(("fixtures", *FIXTURE_FIELDS), (12, 12, 12, 0, 12, 12, 12), strict=True)),
    STRATA[1]: dict(zip(("fixtures", *FIXTURE_FIELDS), (52, 0, 52, 0, 52, 52, 0), strict=True)),
    STRATA[2]: dict(zip(("fixtures", *FIXTURE_FIELDS), (2, 2, 2, 2, 2, 2, 2), strict=True)),
}


def _require(condition: bool, message: str) -> None:
    """Raise when an internal invariant fails; unlike `assert` it survives `python -O`."""
    if not condition:
        raise RuntimeError(message)


def pfaffian(matrix: Sequence[Sequence[Any]]) -> Any:
    """The Pfaffian of a skew matrix of even order over Q(i), by simultaneous row and column elimination.

    At step k the pivot a[k][k+1] is brought in by one simultaneous swap (the Pfaffian changes sign), and the
    congruence that adds a multiple of row and column k+1 to row and column i > k+1 clears a[k][i] and keeps the
    Pfaffian; the Pfaffian is the product of the pivots with the sign of the swaps.
    """
    a = [list(row) for row in matrix]
    size = len(a)
    _require(size % 2 == 0, "the Pfaffian needs an even order")
    _require(all(not (a[r][c] + a[c][r]) for r in range(size) for c in range(r, size)), "the matrix is not skew")
    result = QQ_I.one
    for k in range(0, size, 2):
        pivot = next((j for j in range(k + 1, size) if a[k][j]), None)
        if pivot is None:
            return QQ_I.zero
        if pivot != k + 1:
            a[k + 1], a[pivot] = a[pivot], a[k + 1]
            for row in a:
                row[k + 1], row[pivot] = row[pivot], row[k + 1]
            result = -result
        result = result * a[k][k + 1]
        for i in range(k + 2, size):
            if a[k][i]:
                factor = a[k][i] / a[k][k + 1]
                for c in range(k, size):
                    a[i][c] = a[i][c] - factor * a[k + 1][c]
                for r in range(k, size):
                    a[r][i] = a[r][i] - factor * a[r][k + 1]
    return result


def complement_sign(triple: Sequence[int]) -> int:
    """eps(I): the sign of the permutation that lists I and then its complement, each in increasing order.

    Moving i_1 < i_2 < i_3 (zero-based) to the front crosses i_1 + (i_2 - 1) + (i_3 - 2) smaller indices.
    """
    return -1 if (sum(triple) - 3) % 2 else 1


def three_vector(point: Sequence[Any]) -> dict[tuple[int, ...], Any]:
    """P_I(z) for every triple I: eps(I) times the Pfaffian of M(z) without the rows and columns of I."""
    matrix = block(point, QQ_I.zero)
    vector: dict[tuple[int, ...], Any] = {}
    for triple in TRIPLES:
        rest = [k for k in range(IMAGINARY) if k not in triple]
        vector[triple] = complement_sign(triple) * pfaffian([[matrix[r][c] for c in rest] for r in rest])
    return vector


def product_tensor(vector: dict[tuple[int, ...], Any]) -> list[list[Any]]:
    """T = tau(P): the entry (r, c) collects sign(e_i e_j) P_I over the cyclic splittings (i, j; c) of I with
    e_i e_j = sign e_r, since Im(e_i e_j) = sign e_(i xor j) for distinct imaginary units."""
    tensor = [[QQ_I.zero] * IMAGINARY for _ in range(IMAGINARY)]
    for triple, value in vector.items():
        if not value:
            continue
        for x, y, w in ((0, 1, 2), (1, 2, 0), (2, 0, 1)):
            i, j = triple[x] + 1, triple[y] + 1
            row = (i ^ j) - 1
            tensor[row][triple[w]] = tensor[row][triple[w]] + SEDENION[i][j] * value
    return tensor


def invariants(point: Sequence[Any]) -> tuple[Any, Any, Any]:
    """Q, G and N1 at a point."""
    zero = QQ_I.zero
    squares = [form(index, point, point, zero) for index in range(3)]
    pairing = sum((point[k] * point[k + 8] for k in range(7)), zero)
    norm = sum(squares, zero)
    return norm, norm * norm - 4 * (squares[0] * squares[2] - pairing * pairing), squares[0]


def quartic_gradient(point: Sequence[Any]) -> list[Any]:
    """grad G = 4 Q z - 4 grad Delta, with grad Delta = 2 (N3 a - p b, 0, N1 b - p a) at z = (a, t_8, b)."""
    zero = QQ_I.zero
    first, third = form(0, point, point, zero), form(2, point, point, zero)
    pairing = sum((point[k] * point[k + 8] for k in range(7)), zero)
    norm = invariants(point)[0]
    delta = [2 * (third * point[k] - pairing * point[k + 8]) for k in range(7)]
    delta += [zero, *(2 * (first * point[k + 8] - pairing * point[k]) for k in range(7))]
    return [4 * norm * x - 4 * y for x, y in zip(point, delta, strict=True)]


def product_gradient(point: Sequence[Any]) -> list[Any]:
    """grad(Q G) = 2 G z + Q grad G."""
    norm, quartic, _ = invariants(point)
    return [2 * quartic * x + norm * y for x, y in zip(point, quartic_gradient(point), strict=True)]


def spans_kernel(vector: dict[tuple[int, ...], Any], kernel: Sequence[Sequence[Any]]) -> bool:
    """P is a nonzero multiple of k_1 ^ k_2 ^ k_3 for the basis of a three-dimensional K(z)."""
    if len(kernel) != 3 or not any(vector.values()):
        return False
    minors = {
        triple: DomainMatrix([[k[index] for index in triple] for k in kernel], (3, 3), QQ_I).det() for triple in TRIPLES
    }
    anchor = next(triple for triple in TRIPLES if minors[triple])
    return all(vector[triple] * minors[anchor] == vector[anchor] * minors[triple] for triple in TRIPLES)


def point_facts(point: Sequence[Any]) -> dict[str, Any]:
    """Q, G, N1, dim K(z), the identities T = CONSTANT G z (x) z and T = -grad(Q G) (x) z, T = 0, `spans_kernel`,
    whether every row of T is a multiple of z and whether the polar form of Q vanishes on K(z), at one exact
    point."""
    norm, quartic, first = invariants(point)
    kernel = _exact_kernel(_exact_block(list(point)))
    vector = three_vector(point)
    tensor = product_tensor(vector)
    count = range(IMAGINARY)
    gradient = product_gradient(point)
    return {
        "Q": norm,
        "G": quartic,
        "N1": first,
        "kernel_dimension": len(kernel),
        "identity_holds": all(tensor[r][c] == CONSTANT * quartic * point[r] * point[c] for r in count for c in count),
        "gradient_identity_holds": all(tensor[r][c] == -gradient[r] * point[c] for r in count for c in count),
        "tensor_zero": not any(x for row in tensor for x in row),
        "three_vector_spans_kernel": spans_kernel(vector, kernel),
        "right_factor_is_point": all(
            not (row[c] * point[d] - row[d] * point[c])
            for row in tensor
            for c in count
            for d in range(c + 1, IMAGINARY)
        ),
        "kernel_is_null": all(
            not sum((x * y for x, y in zip(first, second, strict=True)), QQ_I.zero)
            for first in kernel
            for second in kernel
        ),
    }


def _text(value: Any) -> str:
    """The exact value of a Q(i) element as text."""
    return str(QQ_I.to_sympy(value))


def grid_point(job: tuple[str, int, int]) -> list[Any]:
    """The point of a family at the two grid values (and C = 1 on `FQ`) as elements of Q(i)."""
    name, first, second = job
    polynomials, generators = family_point(name)
    at = dict(zip(generators, (first, second, 1), strict=False))
    return [QQ_I.from_sympy(sp.expand(sp.sympify(x).subs(at))) for x in polynomials]


def grid_row(job: tuple[str, int, int]) -> list[bool]:
    """At one grid point: the statements of `GRID_FIELDS`."""
    facts = point_facts(grid_point(job))
    return [
        facts["gradient_identity_holds"],
        facts["kernel_dimension"] == 3,
        not facts["Q"],
        not facts["G"],
        facts["tensor_zero"],
    ]


def grid_jobs(name: str) -> list[tuple[str, int, int]]:
    """The grid of one family."""
    first, second = GRID_VALUES[name]
    return [(name, a, b) for a in first for b in second]


def grid_record() -> dict[str, dict[str, int]]:
    """Per family: the count of grid points and of those with each statement of `GRID_FIELDS`."""
    jobs = [job for name in GRID_VALUES for job in grid_jobs(name)]
    rows = parallel.ordered_map(grid_row, jobs, min_items=2)
    record = {}
    for name in GRID_VALUES:
        mine = [row for job, row in zip(jobs, rows, strict=True) if job[0] == name]
        record[name] = {"points": len(mine)} | {
            field: sum(row[index] for row in mine) for index, field in enumerate(GRID_FIELDS)
        }
    return record


def calibration_record() -> dict[str, Any]:
    """The Pfaffian of the 4 x 4 calibration matrix, and Pf^2 = det on the first 12 x 12 principal block of M(z)
    with a nonzero Pfaffian at the `FQ` grid point (A, B) = (1, 2)."""
    small = [[QQ_I.convert(x) for x in row] for row in CALIBRATION_MATRIX]
    matrix = block(grid_point(("FQ", 1, 2)), QQ_I.zero)
    squares = False
    for triple in TRIPLES:
        rest = [k for k in range(IMAGINARY) if k not in triple]
        minor = [[matrix[r][c] for c in rest] for r in rest]
        value = pfaffian(minor)
        if value:
            squares = value * value == DomainMatrix(minor, (12, 12), QQ_I).det()
            break
    return {"pfaffian_4x4": _text(pfaffian(small)), "pfaffian_squared_is_determinant": squares}


def special_point_record(strings: Sequence[str]) -> dict[str, Any]:
    """`point_facts` at one of `SPECIAL_POINTS`, with the exact values as text."""
    facts = point_facts([QQ_I.from_sympy(sp.sympify(x)) for x in strings])
    return (
        {"point": list(strings)}
        | {key: _text(facts[key]) for key in ("Q", "G", "N1")}
        | {key: facts[key] for key in POINT_FIELDS}
    )


def singular_point_record(strings: Sequence[str]) -> dict[str, Any]:
    """At one of `SINGULAR_POINTS`: Q, G, whether grad G vanishes and dim K(z)."""
    point = [QQ_I.from_sympy(sp.sympify(x)) for x in strings]
    norm, quartic, _ = invariants(point)
    return {
        "point": list(strings),
        "Q": _text(norm),
        "G": _text(quartic),
        "quartic_gradient_zero": not any(quartic_gradient(point)),
        "kernel_dimension": len(_exact_kernel(_exact_block(point))),
    }


def general_point_record(strings: Sequence[str]) -> dict[str, Any]:
    """At one of `GENERAL_POINTS`: Q, G, dim K(z) and whether T = -grad(Q G) (x) z - Q G I."""
    point = [QQ_I.from_sympy(sp.sympify(x)) for x in strings]
    norm, quartic, _ = invariants(point)
    gradient = product_gradient(point)
    tensor = product_tensor(three_vector(point))
    count = range(IMAGINARY)
    return {
        "point": list(strings),
        "Q": _text(norm),
        "G": _text(quartic),
        "kernel_dimension": len(_exact_kernel(_exact_block(point))),
        "global_identity_holds": all(
            tensor[r][c] == -gradient[r] * point[c] - (norm * quartic if r == c else QQ_I.zero)
            for r in count
            for c in count
        ),
    }


def fixture_row(job: tuple[int, str, list[int]]) -> list[Any]:
    """At one fixture: the stratum and the statements of `FIXTURE_FIELDS`."""
    _, stratum, split = job
    facts = point_facts(_frame(split))
    return [stratum, *(facts[field] for field in FIXTURE_FIELDS)]


def fixture_record() -> dict[str, dict[str, int]]:
    """Per stratum: the count of fixtures and of those with each property of `fixture_row`."""
    rows = parallel.ordered_map(fixture_row, _fixture_splits(), min_items=2)
    record = {}
    for stratum in STRATA:
        mine = [row for row in rows if row[0] == stratum]
        record[stratum] = {"fixtures": len(mine)} | {
            field: sum(row[index + 1] for row in mine) for index, field in enumerate(FIXTURE_FIELDS)
        }
    return record


def _inputs() -> dict[str, str]:
    """The sha256 of every file whose bytes define the points, the blocks or this computation."""
    return {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in SOURCE_PATHS}


def compute() -> dict[str, Any]:
    """The whole record: calibration, grids, special, singular and general points and fixtures, with the verdict."""
    record: dict[str, Any] = {
        "schema": SCHEMA,
        "field": FIELD,
        "inputs": _inputs(),
        "constant": CONSTANT,
        "calibration": calibration_record(),
        "grids": grid_record(),
        "special_points": parallel.ordered_map(special_point_record, list(SPECIAL_POINTS), min_items=2),
        "singular_points": parallel.ordered_map(singular_point_record, list(SINGULAR_POINTS), min_items=2),
        "general_points": parallel.ordered_map(general_point_record, list(GENERAL_POINTS), min_items=2),
        "fixtures": fixture_record(),
        "pass": True,
    }
    record["pass"] = verdict(record) == []
    return record


def expected_record() -> dict[str, Any]:
    """The record that the constants of this module determine, with the digests of the files as they are."""
    return {
        "schema": SCHEMA,
        "field": FIELD,
        "inputs": _inputs(),
        "constant": CONSTANT,
        "calibration": dict(CALIBRATION),
        "grids": {name: dict(counts) for name, counts in GRID_COUNTS.items()},
        "special_points": [
            {"point": list(strings), **facts}
            for strings, facts in zip(SPECIAL_POINTS, SPECIAL_POINT_FACTS, strict=True)
        ],
        "singular_points": [
            {"point": list(strings), **facts}
            for strings, facts in zip(SINGULAR_POINTS, SINGULAR_POINT_FACTS, strict=True)
        ],
        "general_points": [
            {"point": list(strings), **facts}
            for strings, facts in zip(GENERAL_POINTS, GENERAL_POINT_FACTS, strict=True)
        ],
        "fixtures": {stratum: dict(counts) for stratum, counts in FIXTURE_COUNTS.items()},
        "pass": True,
    }


def _shape(value: Any) -> Any:
    """The fields and value types of a record: keys of every mapping, lengths of every list, type names of leaves."""
    if isinstance(value, dict):
        return {str(key): _shape(item) for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))}
    if isinstance(value, list):
        return [_shape(item) for item in value]
    return type(value).__name__


def verdict(record: dict[str, Any]) -> list[str]:
    """The reasons the record fails its own rules; empty when it passes.

    The comparison of fields and value types comes first and ends the verdict on a difference, since `==` holds
    True equal to 1; past it each group is compared with the constants by name and last the serialized text.
    """
    expected = expected_record()
    if _shape(record) != _shape(expected):
        return ["the record has other fields or value types than the record the constants determine"]
    problems = []
    if record["inputs"] != expected["inputs"]:
        problems.append("the input digests differ from the files")
    if record["pass"] is not True:
        problems.append("the record states that it fails")
    messages = {
        "calibration": "the Pfaffian routine fails its calibration",
        "grids": "the identity T = -grad(Q G) (x) z does not hold on a whole grid, or the grid tallies differ",
        "special_points": "a point with N1(z) = 0 differs from its pinned facts",
        "singular_points": "a singular point of V(G) differs from its pinned facts",
        "general_points": "the identity T = -grad(Q G) (x) z - Q G I fails at a general point, or its facts differ",
        "fixtures": "the fixture tallies differ from the pinned counts",
    }
    for group, message in messages.items():
        if record[group] != expected[group]:
            problems.append(message)
    if _serialized(record) != _serialized(expected):
        problems.append("the record differs from the record the constants determine")
    return problems


def _serialized(record: dict[str, Any]) -> str:
    """The retained text of a record. The replay compares text, so true and 1, which compare equal, differ."""
    return json.dumps(record, indent=1, sort_keys=True) + "\n"


def main() -> None:
    """Write the record with --write, or recompute and compare its text with --check."""
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    record = compute()
    if args.write:
        RECORD.write_text(_serialized(record), encoding="utf-8")
    elif RECORD.read_text(encoding="utf-8") != _serialized(record):
        raise SystemExit(f"{RECORD.name} differs from the recomputation")
    problems = verdict(record)
    if problems:
        raise SystemExit("\n".join(problems))
    grids = record["grids"].values()
    held, points = sum(grid["gradient_identity_holds"] for grid in grids), sum(grid["points"] for grid in grids)
    print(f"pass: T = -grad(Q G) (x) z at {held} of {points} grid points")


if __name__ == "__main__":
    main()
