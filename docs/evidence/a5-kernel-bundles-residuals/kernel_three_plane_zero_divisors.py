"""The higher zero divisors of the kernel three-plane K = ker M(z) at a nullity-4 point z, modulo 32029.

M(t) is the 15 x 15 skew lower block of the bordered matrix of `nullity4_gauss_image.py`, linear in t, in the frame
t_k = i^popcount(k) t'_k of the split coordinates t' (i sent to 9115). Its signs satisfy M(z) k = -M(k) z, so a vector
k of K = ker M(z) has M(k) z = 0 and M(k) k = 0: M(k) has nullity at least 3 for k independent of z, hence rank at
most 12. A higher zero divisor is a k with nullity of M(k) above 3 (an odd skew matrix has odd nullity). At a nullity-4
point, rank M(z) = 12 (so dim K = 3) and rank A(z, z) = 14, where A is the bordered matrix at the real pair w' = z'.
The quadric Q and the quartic G of `kernel_frames.regularity.closure_ideals` cut out the strata V(Q) minus V(G) and
V(G) minus V(Q) of the nullity-4 points; V(Q) n V(G) lies outside this record. P = ker A(z, z) is the kernel plane of
the bordered matrix, a 2-plane inside K, and dim L is `fiber_dimension` of `nullity4_gauss_image.py`.

The record holds, at the 66 exact fixtures of `nullity4-kernel-gauss-result.json` (12 on V(Q) minus V(G), 52 on
V(G) minus V(Q), 2 on V(Q) n V(G)) and at every nullity-4 point of the 41,616-candidate grid of
`nullity4_gauss_image.py` (rank M(z) = 12 and rank A(z, z) = 14), these facts, each modulo 32029 unless marked exact:

1. K lies in the hypersurface of z. The principal 14 x 14 Pfaffian of M(t) that deletes row and column j equals
   (-1)^j Q(t') G(t') t_j (t' the split coordinates of the frame vector t; ledger row A5-357 states the Pfaffian
   identity, and the test of this producer checks this form of it at three fixed points modulo 32029 for every j). A
   rank of M(k) at most 12 kills every such Pfaffian, so Q G vanishes on the linear space K, which is irreducible:
   Q|_K = 0 or G|_K = 0. On V(Q) minus V(G) the Gram matrix of the polar form of Q on a basis of K is zero, so Q
   vanishes on K (the characteristic is odd). On V(G) minus V(Q) the quartic G vanishes at 16 points of P(K) whose
   15 quartic monomials have independent values, and a plane quartic has 15 coefficients, so G vanishes on K.
2. On V(G) minus V(Q) the Gram matrix of Q on K has rank 1, so Q|_K = c l^2 for a linear form l with l(z) nonzero (z
   lies in K and Q(z) is nonzero), and the polar line l_z = K n ker dQ_z = {l = 0} has dimension 2. M(k) has one
   nullity, 7 or 9, at six pairwise independent vectors of l_z, and nullity 3 at a vector of K off l_z. A skew matrix
   of rank at most 8 (at most 6) is cut out by its principal 10 x 10 (8 x 8) Pfaffians, forms of degree 5 (4) on l_z,
   and a binary form of degree 5 that vanishes at six points is zero, so nullity above 5 (above 7) at six points
   holds on the whole line. At the 52 fixtures the 91 Pfaffians of item 3 span exactly (Q|_K)^2 times the six
   quadratic monomials, so there the locus of higher zero divisors in P(K) is exactly l_z modulo the prime.
   hypothesis: the same holds at every nullity-4 point of the stratum; at the grid points the record holds the
   containment of l_z and one vector off the line. The record also tells whether P = l_z (rank(P + l_z) = 2) and
   dim L. At the 52 fixtures the same line and its six ranks are computed exactly over Q(i), with the rank of M(k) at
   one vector off the line, and dim L is computed exactly (`exact_fiber_dimension`).
3. On V(Q) minus V(G) the plane quartic G|_K is nonzero, the length of its singular scheme is read, and a
   certificate shows that it contains no line over the algebraic closure of GF(32029). The record identifies the
   locus of higher zero divisors with this quartic at the 12 fixtures only (last paragraph of this item); at the grid
   points it holds the quartic and its certificate. The certificate is linear
   algebra on the Jacobian ideal J = (F_a, F_b, F_c) of F = G|_K in S = k[a, b, c], with HF(d) = dim (S/J)_d. J is
   generated in degree 3, and HF(d) = HF(d + 1) = h at a degree d >= max(3, h) is maximal growth (the Macaulay bound
   of h at degree d is h), so Gotzmann's persistence theorem gives HF(n) = h for all n >= d: the singular scheme Z of
   F is zero-dimensional of length h, and J_n is the saturated ideal of Z in degrees n >= d. For F = L C with L a
   linear form, either L divides C and Z contains the line L = 0, or V(L, C) is a scheme of length 3 (Bezout) inside Z
   (F_x = L_x C + L C_x lies in (L, C)) on the line L = 0. So F = L C leaves Z non-zero-dimensional or gives Z a line
   that meets it in length at least 3 (a trisecant line). When the line l = 0 meets Z in length m at least 3,
   the h x h matrix of multiplication by l from (S/J)_d to (S/J)_(d + 1) has rank at most h - 3: the cokernel of that
   multiplication is (S/(J_sat + l))_(d + 1), of dimension at least m for m <= h <= d. The (h - 2) x (h - 2) minors of
   that matrix are forms of degree h - 2 in the dual coordinates (u, v, w) of l, and a set of forms that spans all
   monomials of one degree has no common zero over the algebraic closure. `quartic_line_certificate` returns h and the
   Hilbert function of the minor ideal in degree TRISECANT_DEGREE; a quartic with that value 0 contains no line.
   The `calibration` section of the record and the tests run the certificate on a three-nodal quartic with no line
   (the image of a conic under the Cremona map (a, b, c) -> (b c, a c, a b)), on a product of two conics meeting in
   four points and on a product of two conics tangent at one point (singular scheme of length 5), which it passes,
   and on a linear form times a smooth cubic (three nodes on the line), two lines times a conic and a double line
   times a conic, which it rejects.
   At the 12 fixtures the 91 principal 12 x 12 Pfaffians of the restriction of M(k) to the hyperplane x_j = 0 with z_j
   nonzero, a 14 x 14 skew matrix of the rank of M(k) (M(k) z = 0 and z^T M(k) = 0 for k in K), are sextic forms on K
   fitted from 28 points and checked at 8 more. They span exactly G|_K times the six quadratic monomials, and rank at
   most 10 of M(k) is their common vanishing, so at those fixtures the locus of higher zero divisors in P(K) is the zero
   set of the quartic G|_K.
4. A line of higher zero divisors over Q(i) at a fixture of V(Q) minus V(G) is a line in P(K) on which the principal
   12 x 12 Pfaffians of item 3 vanish. At the prime of Z[i] above 32029 that sends i to 9115 it reduces to a line in
   P(K modulo 32029) (rank M(z) = 12 modulo the prime, so K keeps its dimension) on which the reduced Pfaffians vanish.
   By the span statement of item 3 their zero set is the zero set of G|_K modulo the prime, which contains no line.
   The statement needs no further computation.

The grid enumeration of `nullity4_gauss_image.grid_block` is repeated here point for point (same candidates, same
filters), and the loops over independent points run through `parallel.ordered_map`. The grid points are integer split
points, the sampled kernel vectors have fixed coefficients, and the probe points of every interpolation and of the
quartic test come from sha256 of a label and a counter: a fixed list, with no seed.

`--write` writes kernel-three-plane-zero-divisors-result.json beside this file; `--check` recomputes and compares.

Run from the repository root:
"$PYTHON" docs/evidence/a5-kernel-bundles-residuals/kernel_three_plane_zero_divisors.py --check
"""

from __future__ import annotations

import argparse
import functools
import hashlib
import itertools
import json
import math
import sys
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

from flint import nmod_mat
from sympy import QQ_I, I
from sympy.polys.matrices import DomainMatrix

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BUNDLES = HERE.parent / "a5-kernel-bundles"
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(BUNDLES))

from nullity4_gauss_image import (  # noqa: E402
    FIXTURES,
    IMAGINARY,
    MEMBERSHIP,
    PRIME,
    ROOT_OF_MINUS_ONE,
    SIGNS,
    STRATA,
    Matrix,
    Vector,
    _block,
    _fixture_splits,
    _nullspace,
    _polynomials,
    _rank,
    _twist,
    _value,
    bordered,
    exact_fiber_dimension,
    fiber_dimension,
    lower_block,
)

import parallel  # noqa: E402

SCHEMA = "a5-kernel-bundles-residuals-kernel-three-plane-zero-divisors-v1"
RECORD = HERE / "kernel-three-plane-zero-divisors-result.json"
SOURCE_PATHS = (
    HERE / "kernel_three_plane_zero_divisors.py",
    HERE / "nullity4_gauss_image.py",
    BUNDLES / "kernel_frames.py",
    ROOT / "docs" / "evidence" / "a5-strata-regularity" / "strata_regularity.py",
    ROOT / "gororoba_quantum" / "cd_core.py",
    FIXTURES,
)
FIELD = f"GF({PRIME}), i = {ROOT_OF_MINUS_ONE}"
BORDERED = IMAGINARY + 1
QUADRIC, QUARTIC = STRATA[0], STRATA[1]
# The fixtures and the grid points of the strata outside this record: V(Q) n V(G).
EXCLUDED_STRATUM = STRATA[2]

# Interpolation of a form on K: its value at len(monomials) + CHECK_POINTS probe points fixes the coefficients and
# checks the degree.
CHECK_POINTS = 3
# Points of P(K) at which G is evaluated to force G|_K = 0 (more than the 15 quartic coefficients).
QUARTIC_PROBES = 16
QUARTIC_COEFFICIENTS = 15
# Degree of the Hilbert function in the line certificate, with HF(d) = HF(d + 1) read at d.
HILBERT_DEGREE = 6
# Degree at which the ideal of the trisecant lines is read: zero there means that the ideal has no zero.
TRISECANT_DEGREE = 8
# Pairwise independent vectors s * line[0] + t * line[1] of the polar line, as (s, t), and the vectors of K tried for a
# vector off the line.
LINE_PARAMETERS = tuple((1, t) for t in range(5)) + ((0, 1),)
OFF_LINE_COEFFICIENTS = ((1, 2, 5), (1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 1))
# Sextic forms on K from the Pfaffians: interpolation points beyond the 28 sextic monomials, and the number of
# principal Pfaffians of the 14 x 14 restriction (12 x 12 minors).
SEXTIC_CHECK_POINTS = 8
PFAFFIAN_SUBSETS = math.comb(14, 2)
PFAFFIAN_SPAN_RANK = 6

# Nullities of M(k) on the polar line at the six vectors, and the nullity off the line.
LINE_NULLITIES = {7, 9}
OFF_LINE_NULLITY = 3
# Rank of M(k) over Q(i) at six vectors of the exact polar line for nullity 7 and 9, and at the vector off it.
EXACT_LINE_RANKS = {7: 8, 9: 6}
EXACT_OFF_LINE_RANK = 12

# Fixtures of V(G) minus V(Q) by (exact dim L, P = l_z, nullity of M(k) on l_z).
FIXTURE_CLASSES: dict[tuple[int, bool, int], tuple[int, ...]] = {
    (2, False, 7): (46, 47),
    (2, False, 9): (29, 30, 32, 33, 34, 36, 37, 39, 40, 41, 49, 50, 51, 52, 54, 55, 57, 58, 59, 60, 63),
    (6, True, 7): (0, 15, 16, 17, 18, 20, 21, 22, 23, 26, 27, 48, 64),
    (12, True, 9): (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 31, 35, 53, 56),
}
# Nullity-4 grid points of V(G) minus V(Q) by (nullity of M(k) on l_z, P = l_z, dim L).
GRID_CLASSES: dict[tuple[int, bool, int], int] = {
    (7, False, 2): 364,
    (7, True, 2): 8,
    (7, True, 6): 61,
    (9, False, 2): 678,
    (9, True, 12): 92,
}
# Points of V(G) minus V(Q) in the grid; each has the same Gram rank, probe count, polar line and off-line nullity.
GRID_QUARTIC_POINTS = 1203
# Nullity-4 grid points of V(Q) minus V(G) by (Gram rank of Q|_K, G|_K nonzero, singular scheme length, trisecant
# Hilbert value).
GRID_QUADRIC_CLASSES = {(0, True, 3, 0): 2064, (0, True, 5, 0): 32}
GRID_QUADRIC_POINTS = 2096
# The grid points of V(Q) minus V(G) whose singular scheme has a length other than 3: how many, and the sha256 of
# json.dumps of their split points in grid order.
LONG_SCHEME_POINTS = 32
LONG_SCHEME_SHA256 = "a9d42385fc48125d0078e75e41b6f98a2f07c2e6e8735705402feb8ee2e39d99"
GRID_CANDIDATES = 41616
# Grid points of V(G) minus V(Q) with P = l_z and dim L = 2: split points.
PLANE_ON_LINE_POINTS: tuple[tuple[int, ...], ...] = (
    (1, 0, 1, 0, 0, 0, 0, 1, 0, 0, -1, -1, 1, 0, 0),
    (1, 0, 1, 0, 0, 0, 0, 1, 0, 0, -1, 1, -1, 0, 0),
    (1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, -1, -1, 0, 0),
    (1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 0),
    (1, 0, 1, 0, 0, 0, 0, 1, 0, 0, -1, 0, 0, -1, -1),
    (1, 0, 1, 0, 0, 0, 0, 1, 0, 0, -1, 0, 0, 1, 1),
    (1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, -1, 1),
    (1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, -1),
)
EXCLUDED_GRID_POINTS = 388
FIXTURE_STRATUM_COUNTS = {QUADRIC: 12, QUARTIC: 52, EXCLUDED_STRATUM: 2}
# Fixture numbers of the record `nullity4-kernel-gauss-result.json` by stratum.
QUADRIC_FIXTURES = (13, 14, 19, 24, 25, 42, 43, 44, 45, 61, 62, 65)
EXCLUDED_FIXTURES = (28, 38)
QUARTIC_FIXTURES = tuple(number for number in range(66) if number not in (*QUADRIC_FIXTURES, *EXCLUDED_FIXTURES))
# The certificate on the calibration quartics: the two quartics with no line pass, the three with a line are rejected.
CALIBRATION: dict[str, dict[str, int | None]] = {
    "three_nodal_quartic": {"singular_scheme_length": 3, "trisecant_hilbert_value": 0},
    "conic_times_conic": {"singular_scheme_length": 4, "trisecant_hilbert_value": 0},
    "tangent_conics": {"singular_scheme_length": 5, "trisecant_hilbert_value": 0},
    "line_times_cubic": {"singular_scheme_length": 3, "trisecant_hilbert_value": 1},
    "two_lines_times_conic": {"singular_scheme_length": 5, "trisecant_hilbert_value": 2},
    "double_line_times_conic": {"singular_scheme_length": None, "trisecant_hilbert_value": None},
}
LINE_FREE_CALIBRATION = ("three_nodal_quartic", "conic_times_conic", "tangent_conics")


@functools.cache
def _hypersurfaces() -> dict[str, Any]:
    """The polynomials Q and G in the 15 split coordinates, built once per process."""
    return _polynomials()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


# Plane curves and the Jacobian ideal: forms in three variables as coefficient vectors over the monomials of a degree.
def _monomials(degree: int) -> list[tuple[int, int, int]]:
    """The monomials a^i b^j c^k of the degree, in the order of the coefficient vectors."""
    return [(i, j, degree - i - j) for i in range(degree + 1) for j in range(degree + 1 - i)]


def _probe_point(label: str, number: int) -> tuple[int, int, int]:
    """A point (a, b, c) modulo PRIME from sha256 of a label and a counter."""
    digest = hashlib.sha256(f"{label}:{number}".encode()).digest()
    a, b, c = (int.from_bytes(digest[8 * axis : 8 * axis + 8], "big") % PRIME for axis in range(3))
    return a, b, c


def _monomial_values(point: Sequence[int], degree: int) -> Vector:
    return [
        pow(point[0], i, PRIME) * pow(point[1], j, PRIME) * pow(point[2], k, PRIME) % PRIME
        for i, j, k in _monomials(degree)
    ]


@functools.cache
def _interpolation(label: str, degree: int, checks: int) -> tuple[tuple[tuple[int, int, int], ...], nmod_mat]:
    """The probe points of a degree and the inverse of the matrix of monomial values at the first ones."""
    count = len(_monomials(degree))
    points = tuple(_probe_point(f"locus:{label}:{degree}", number) for number in range(count + checks))
    values = nmod_mat(
        count, count, [value for point in points[:count] for value in _monomial_values(point, degree)], PRIME
    )
    return points, values.inv()


def interpolate_form(
    function: Callable[[Sequence[int]], int], degree: int, label: str, checks: int = CHECK_POINTS
) -> Vector:
    """Coefficients over `_monomials(degree)` of the form of that degree in (a, b, c) that function evaluates.

    The form is fixed by its values at as many points as it has monomials (the monomial matrix at the probe points is
    invertible, which `nmod_mat.inv` enforces) and the `checks` further points confirm the degree.
    """
    points, inverse = _interpolation(label, degree, checks)
    count = len(_monomials(degree))
    column = nmod_mat(count, 1, [function(point) for point in points[:count]], PRIME)
    coefficients = [int(entry) for entry in (inverse * column).entries()]
    for point in points[count : count + checks]:
        found = sum(c * m for c, m in zip(coefficients, _monomial_values(point, degree), strict=True)) % PRIME
        _require(found == function(point), f"the restriction to the three-plane is not a form of degree {degree}")
    return coefficients


def _fit_forms(values: Sequence[Sequence[int]], degree: int, label: str, checks: int) -> list[Vector]:
    """Coefficients of forms from their values at the probe points of (label, degree).

    values[n][f] is the value of form f at probe point n.
    """
    points, inverse = _interpolation(label, degree, checks)
    count = len(_monomials(degree))
    forms = []
    for index in range(len(values[0])):
        column = nmod_mat(count, 1, [values[number][index] for number in range(count)], PRIME)
        coefficients = [int(entry) for entry in (inverse * column).entries()]
        for number in range(count, count + checks):
            found = (
                sum(c * m for c, m in zip(coefficients, _monomial_values(points[number], degree), strict=True)) % PRIME
            )
            _require(found == values[number][index], f"a fitted form is not of degree {degree}")
        forms.append(coefficients)
    return forms


def _jacobian_ideal(quartic: Sequence[int]) -> list[dict[tuple[int, int, int], int]]:
    """The three partial derivatives of a quartic, each as {monomial: coefficient}."""
    partials: list[dict[tuple[int, int, int], int]] = [{}, {}, {}]
    for coefficient, monomial in zip(quartic, _monomials(4), strict=True):
        for axis in range(3):
            if coefficient and monomial[axis]:
                lowered = list(monomial)
                lowered[axis] -= 1
                partials[axis][(lowered[0], lowered[1], lowered[2])] = coefficient * monomial[axis] % PRIME
    return partials


def _ideal_rows(quartic: Sequence[int], degree: int) -> Matrix:
    """Spanning rows of J_degree over the monomials of the degree: each partial times each monomial of degree - 3."""
    position = {monomial: index for index, monomial in enumerate(_monomials(degree))}
    rows = []
    for partial in _jacobian_ideal(quartic):
        for factor in _monomials(degree - 3):
            row = [0] * len(position)
            for monomial, coefficient in partial.items():
                row[position[(monomial[0] + factor[0], monomial[1] + factor[1], monomial[2] + factor[2])]] = coefficient
            rows.append(row)
    return rows


def hilbert_function(quartic: Sequence[int], degree: int) -> int:
    """HF(d) = dim (S/J)_d for the Jacobian ideal J of the quartic."""
    return len(_monomials(degree)) - _rank(_ideal_rows(quartic, degree))


def _quotient_functionals(quartic: Sequence[int], degree: int) -> Matrix:
    """A basis of the functionals on S_d that vanish on J_d: they identify (S/J)_d with k^HF(d)."""
    return _nullspace(_ideal_rows(quartic, degree))


def _multiplication_matrices(quartic: Sequence[int], length: int) -> list[Matrix]:
    """The matrices of x, y, z from (S/J)_d to (S/J)_(d + 1), d = HILBERT_DEGREE, in the bases of the quotients.

    A basis of (S/J)_d is the images of the monomials at the pivot columns of the functionals of S_d, and the
    coordinates of an element of S_(d + 1) in (S/J)_(d + 1) are the values of the functionals of that degree.
    """
    low, high = (_quotient_functionals(quartic, degree) for degree in (HILBERT_DEGREE, HILBERT_DEGREE + 1))
    _require(len(low) == len(high) == length, "the quotients of S by the Jacobian ideal have another dimension")
    reduced, rank = nmod_mat(len(low), len(low[0]), [value for row in low for value in row], PRIME).rref()
    _require(rank == length, "the functionals of S_d are dependent")
    pivots = [next(column for column in range(len(low[0])) if int(reduced[row, column])) for row in range(length)]
    low_monomials = _monomials(HILBERT_DEGREE)
    high_position: dict[tuple[int, ...], int] = {m: n for n, m in enumerate(_monomials(HILBERT_DEGREE + 1))}
    matrices = []
    for axis in range(3):
        columns = []
        for pivot in pivots:
            monomial = list(low_monomials[pivot])
            monomial[axis] += 1
            columns.append([phi[high_position[tuple(monomial)]] for phi in high])
        matrices.append([list(row) for row in zip(*columns, strict=True)])
    return matrices


def _trisecant_forms(quartic: Sequence[int], length: int) -> list[Vector]:
    """Forms of degree length - 2 in the dual coordinates (u, v, w) of the lines, cutting out the trisecant lines of Z.

    When the line u x + v y + w z meets the singular scheme Z (of length h) in a scheme of length at least 3, the
    h x h matrix of multiplication by that linear form, from (S/J)_d to (S/J)_(d + 1), has rank at most h - 3, so
    its (h - 2) x (h - 2) minors vanish. Each minor is a form of degree h - 2 in (u, v, w).
    """
    size = length - 2
    matrices = _multiplication_matrices(quartic, length)
    subsets = list(itertools.combinations(range(length), size))
    points, _ = _interpolation("trisecant", size, CHECK_POINTS)
    values = []
    for point in points:
        total = [
            [sum(c * m[row][col] for c, m in zip(point, matrices, strict=True)) % PRIME for col in range(length)]
            for row in range(length)
        ]
        values.append(
            [
                int(nmod_mat(size, size, [total[row][col] for row in rows for col in columns], PRIME).det())
                for rows in subsets
                for columns in subsets
            ]
        )
    return _fit_forms(values, size, "trisecant", CHECK_POINTS)


def _form_multiples(forms: Sequence[Sequence[int]], form_degree: int, degree: int) -> Matrix:
    """Every product of a form with a monomial, as coefficient vectors of the target degree."""
    position = {monomial: index for index, monomial in enumerate(_monomials(degree))}
    rows = []
    for form in forms:
        for factor in _monomials(degree - form_degree):
            row = [0] * len(position)
            for coefficient, monomial in zip(form, _monomials(form_degree), strict=True):
                row[position[(monomial[0] + factor[0], monomial[1] + factor[1], monomial[2] + factor[2])]] = coefficient
            rows.append(row)
    return rows


def trisecant_hilbert_value(forms: Sequence[Sequence[int]], form_degree: int) -> int:
    """dim (k[u, v, w] / I)_D for the ideal I of the forms, D = TRISECANT_DEGREE; zero means I has no zero over k-bar.

    A form set that spans all monomials of degree D has no common zero in the projective plane over the algebraic
    closure. The forms are first reduced to a basis of their span, which keeps the products few.
    """
    reduced, rank = nmod_mat(len(forms), len(forms[0]), [value for form in forms for value in form], PRIME).rref()
    basis = [[int(reduced[row, column]) for column in range(len(forms[0]))] for row in range(rank)]
    return len(_monomials(TRISECANT_DEGREE)) - _rank(_form_multiples(basis, form_degree, TRISECANT_DEGREE))


def quartic_line_certificate(quartic: Sequence[int]) -> dict[str, int | None]:
    """The singular-scheme length h of a nonzero plane quartic F and the trisecant ideal of the scheme.

    HF(d) = HF(d + 1) = h at d = HILBERT_DEGREE >= max(3, h) is the persistence condition of Gotzmann's theorem, so
    the singular scheme Z has length h (None when HF does not stabilize between d and d + 1, or h exceeds d). For
    n >= d the saturation of J has HF(n) = h, the same as J, so (S/J)_n is the space of sections of O_Z(n), and a line
    l = 0 that meets Z in a scheme of length m >= 3 has dim (S/(J + l))_(d + 1) >= m, which is h minus the rank of
    multiplication by l from (S/J)_d to (S/J)_(d + 1). F = L C has Z containing V(L, C) of length 3 on the line L = 0,
    or Z containing the whole line (not zero-dimensional). So a quartic with Z zero-dimensional and without a line
    that meets it in length 3 contains no line. `trisecant_hilbert_value` is the Hilbert function in degree
    TRISECANT_DEGREE of the ideal of the (h - 2) x (h - 2) minors of that multiplication matrix; value 0 means no
    such line over the algebraic closure. h < 3 has no trisecant line, value 0 without a computation.
    """
    first, second = hilbert_function(quartic, HILBERT_DEGREE), hilbert_function(quartic, HILBERT_DEGREE + 1)
    if first != second or first > HILBERT_DEGREE:
        return {"singular_scheme_length": None, "trisecant_hilbert_value": None}
    if first < 3:
        return {"singular_scheme_length": first, "trisecant_hilbert_value": 0}
    value = trisecant_hilbert_value(_trisecant_forms(quartic, first), first - 2)
    return {"singular_scheme_length": first, "trisecant_hilbert_value": value}


def line_free(certificate: dict[str, int | None]) -> bool:
    """True when the certificate proves that the quartic contains no line."""
    return certificate.get("singular_scheme_length") is not None and certificate.get("trisecant_hilbert_value") == 0


def _form_product(left: Sequence[int], left_degree: int, right: Sequence[int], right_degree: int) -> Vector:
    """Coefficients of the product of two forms."""
    position = {monomial: index for index, monomial in enumerate(_monomials(left_degree + right_degree))}
    product = [0] * len(position)
    for a, first in zip(left, _monomials(left_degree), strict=True):
        for b, second in zip(right, _monomials(right_degree), strict=True):
            product[position[(first[0] + second[0], first[1] + second[1], first[2] + second[2])]] += a * b % PRIME
    return [value % PRIME for value in product]


def _form(terms: dict[tuple[int, int, int], int], degree: int) -> Vector:
    return [terms.get(monomial, 0) % PRIME for monomial in _monomials(degree)]


def calibration() -> dict[str, dict[str, int | None]]:
    """The certificate on three quartics with no line and on three quartics with a line.

    The first quartic is q(b c, a c, a b) for a conic q: the Cremona image, three-nodal with nodes at the coordinate
    points. The second is a product of two conics that meet in four points, no three collinear, and the third a
    product of the conic y z - x^2 with y z - x^2 + y (x + z), tangent to it at one point. The quartics with a
    line are a linear form times a smooth cubic (three nodes on the line), two lines times a conic (the point of the
    lines and the four points of the conic, three of them on each line) and a double line times a conic.
    """
    conic = _form({(2, 0, 0): 3, (0, 2, 0): 5, (0, 0, 2): 7, (1, 1, 0): 2, (1, 0, 1): 11, (0, 1, 1): 13}, 2)
    cremona = _form(
        {
            (0, 2, 2): conic[_monomials(2).index((2, 0, 0))],
            (2, 0, 2): conic[_monomials(2).index((0, 2, 0))],
            (2, 2, 0): conic[_monomials(2).index((0, 0, 2))],
            (1, 1, 2): conic[_monomials(2).index((1, 1, 0))],
            (1, 2, 1): conic[_monomials(2).index((1, 0, 1))],
            (2, 1, 1): conic[_monomials(2).index((0, 1, 1))],
        },
        4,
    )
    cubic = _form({(3, 0, 0): 1, (0, 3, 0): 1, (0, 0, 3): 1, (1, 1, 1): 3, (2, 1, 0): 2, (0, 2, 1): 5}, 3)
    linear = _form({(1, 0, 0): 1, (0, 1, 0): 2, (0, 0, 1): 3}, 1)
    other_linear = _form({(1, 0, 0): 2, (0, 1, 0): 1, (0, 0, 1): -1 % PRIME}, 1)
    other_conic = _form({(2, 0, 0): 1, (0, 2, 0): 1, (0, 0, 2): -1 % PRIME, (1, 1, 0): 4}, 2)
    parabola = _form({(0, 1, 1): 1, (2, 0, 0): -1 % PRIME}, 2)
    tangent = _form({(0, 1, 1): 2, (2, 0, 0): -1 % PRIME, (1, 1, 0): 1}, 2)
    return {
        "three_nodal_quartic": quartic_line_certificate(cremona),
        "conic_times_conic": quartic_line_certificate(_form_product(conic, 2, other_conic, 2)),
        "tangent_conics": quartic_line_certificate(_form_product(parabola, 2, tangent, 2)),
        "line_times_cubic": quartic_line_certificate(_form_product(linear, 1, cubic, 3)),
        "two_lines_times_conic": quartic_line_certificate(
            _form_product(_form_product(linear, 1, other_linear, 1), 2, conic, 2)
        ),
        "double_line_times_conic": quartic_line_certificate(
            _form_product(_form_product(linear, 1, linear, 1), 2, conic, 2)
        ),
    }


# The kernel three-plane and its restrictions.
def _untwist(frame: Sequence[int]) -> Vector:
    """Split coordinates of a frame vector: the inverse of `_twist` at ROOT_OF_MINUS_ONE."""
    return _twist(frame, pow(ROOT_OF_MINUS_ONE, -1, PRIME))


def _combination(vectors: Sequence[Sequence[int]], coefficients: Sequence[int]) -> Vector:
    return [sum(c * v[index] for c, v in zip(coefficients, vectors, strict=True)) % PRIME for index in range(IMAGINARY)]


def kernel_three_plane(split: Sequence[int]) -> tuple[Matrix, Matrix]:
    """A basis of ker M(z) in the frame, and the same vectors in split coordinates."""
    basis = _nullspace(_block(_twist(split, ROOT_OF_MINUS_ONE)))
    _require(len(basis) == 3, "ker M(z) is not a three-plane")
    return basis, [_untwist(vector) for vector in basis]


def restrict_to_kernel(polynomial: Any, split_basis: Matrix, degree: int) -> Vector:
    """The coefficients of polynomial restricted to a K of the given degree, in the coordinates of the basis."""
    return interpolate_form(lambda point: _value(polynomial, _combination(split_basis, point)), degree, "restriction")


def nullity(vector: Sequence[int]) -> int:
    """The nullity of M(vector) for a vector of the frame."""
    return IMAGINARY - _rank(_block(vector))


def quadric_gram_rank(quadric: Any, split_basis: Matrix) -> int:
    """The rank of the Gram matrix of the polar form of Q on the basis of K (zero exactly when Q vanishes on K)."""
    diagonal = [_value(quadric, vector) for vector in split_basis]
    gram = [[0] * 3 for _ in range(3)]
    for first, second in itertools.combinations(range(3), 2):
        total = _value(quadric, [(a + b) % PRIME for a, b in zip(split_basis[first], split_basis[second], strict=True)])
        gram[first][second] = gram[second][first] = (total - diagonal[first] - diagonal[second]) % PRIME
    for index in range(3):
        gram[index][index] = 2 * diagonal[index] % PRIME
    return _rank(gram)


def _quartic_vanishing(quartic: Any, split_basis: Matrix) -> int:
    """How many of the QUARTIC_PROBES fixed points of P(K) the quartic G vanishes at."""
    return sum(
        _value(quartic, _combination(split_basis, _probe_point("locus:quartic-probes", number))) == 0
        for number in range(QUARTIC_PROBES)
    )


def quartic_probe_rank() -> int:
    """The rank of the quartic monomials at the QUARTIC_PROBES points: 15 means G vanishing there gives G|_K = 0."""
    return _rank(
        [_monomial_values(_probe_point("locus:quartic-probes", number), 4) for number in range(QUARTIC_PROBES)]
    )


def polar_line(polynomial_gradient: Sequence[int], basis: Matrix, split_basis: Matrix) -> Matrix:
    """K n ker dQ_z in the frame: the vectors of K killed by the differential of Q at z, taken on split coordinates."""
    functional = [
        sum(g * s for g, s in zip(polynomial_gradient, vector, strict=True)) % PRIME for vector in split_basis
    ]
    return [_combination(basis, coefficients) for coefficients in _nullspace([functional])]


def _off_line_vector(basis: Matrix, line: Matrix) -> Vector:
    """A vector of K outside the polar line, from the fixed coefficients."""
    for coefficients in OFF_LINE_COEFFICIENTS:
        vector = _combination(basis, coefficients)
        if _rank([*line, vector]) == 3:
            return vector
    raise RuntimeError("every tried vector of K lies on the polar line")


def _line_points(line: Sequence[Sequence[int]]) -> Matrix:
    """The six pairwise independent vectors of a polar line."""
    return [[(s * a + t * b) % PRIME for a, b in zip(*line, strict=True)] for s, t in LINE_PARAMETERS]


def quartic_point(split: Sequence[int]) -> dict[str, Any]:
    """The facts of items 1 and 2 at one nullity-4 point of V(G) minus V(Q), modulo PRIME."""
    polynomials = _hypersurfaces()
    reduced = [value % PRIME for value in split]
    basis, split_basis = kernel_three_plane(reduced)
    gradient = [int(polynomials["Q"].derivative(index)(*reduced)) % PRIME for index in range(IMAGINARY)]
    line = polar_line(gradient, basis, split_basis)
    row: dict[str, Any] = {
        "quadric_gram_rank": quadric_gram_rank(polynomials["Q"], split_basis),
        "quartic_zero_probes": _quartic_vanishing(polynomials["G"], split_basis),
        "polar_line_dimension": len(line),
    }
    if len(line) == 2:
        plane = [vector[1:] for vector in _nullspace(bordered([*reduced, *reduced]))]
        row["line_nullities"] = [nullity(vector) for vector in _line_points(line)]
        row["off_line_nullity"] = nullity(_off_line_vector(basis, line))
        row["plane_equals_line"] = _rank([*plane, *line]) == 2
        row["fiber_dimension"] = fiber_dimension(reduced)
    return row


def quadric_point(split: Sequence[int]) -> dict[str, Any]:
    """The facts of item 3 at one nullity-4 point of V(Q) minus V(G), modulo PRIME."""
    polynomials = _hypersurfaces()
    reduced = [value % PRIME for value in split]
    _, split_basis = kernel_three_plane(reduced)
    row: dict[str, Any] = {"quadric_gram_rank": quadric_gram_rank(polynomials["Q"], split_basis)}
    quartic = restrict_to_kernel(polynomials["G"], split_basis, 4)
    row["quartic_nonzero"] = any(quartic)
    if any(quartic):
        row.update(quartic_line_certificate(quartic))
    return row


# Exact statements over Q(i) at the fixtures of V(G) minus V(Q).
def _exact_block(vector: Sequence[Any]) -> list[list[Any]]:
    """M(t) over Q(i) for a vector t in the frame."""
    return [
        [
            QQ_I.zero if row == column else SIGNS[row][column] * vector[(row ^ column) - 1]
            for column in range(1, BORDERED)
        ]
        for row in range(1, BORDERED)
    ]


def _exact_rank(rows: list[list[Any]]) -> int:
    return int(DomainMatrix(rows, (len(rows), len(rows[0])), QQ_I).rank())


def _exact_kernel(rows: list[list[Any]]) -> list[list[Any]]:
    return DomainMatrix(rows, (len(rows), len(rows[0])), QQ_I).nullspace().to_list()


def _exact_combination(vectors: Sequence[Sequence[Any]], coefficients: Sequence[Any]) -> list[Any]:
    return [
        sum((c * v[index] for c, v in zip(coefficients, vectors, strict=True)), QQ_I.zero) for index in range(IMAGINARY)
    ]


def exact_polar_line(split: Sequence[int]) -> dict[str, Any]:
    """Over Q(i) at an integer split point of V(G) minus V(Q): dim K, the polar line and the rank of M(k) on it.

    The frame is i^popcount(k) z'_k and split coordinates are recovered by (-i)^popcount(k), so the differential of Q at
    z' pairs with a basis vector k of K through those factors.
    """
    unit = QQ_I.convert(I)
    frame = [unit ** (index + 1).bit_count() * QQ_I.convert(int(value)) for index, value in enumerate(split)]
    block = _exact_block(frame)
    basis = _exact_kernel(block)
    gradient = [
        int(_hypersurfaces()["Q"].derivative(index)(*[int(value) for value in split])) for index in range(IMAGINARY)
    ]
    untwist = [(-unit) ** (index + 1).bit_count() for index in range(IMAGINARY)]
    functional = [
        sum((QQ_I.convert(gradient[index]) * untwist[index] * vector[index] for index in range(IMAGINARY)), QQ_I.zero)
        for vector in basis
    ]
    line = _exact_kernel([functional])
    _require(len(basis) == 3 and len(line) == 2, "the exact kernel or polar line has another dimension")
    on_line = [
        _exact_rank(_exact_block(_exact_combination(basis, [s * a + t * b for a, b in zip(*line, strict=True)])))
        for s, t in LINE_PARAMETERS
    ]
    off_coefficients = next(
        (c for c in OFF_LINE_COEFFICIENTS if _exact_rank([*line, [QQ_I.convert(value) for value in c]]) == 3), None
    )
    _require(off_coefficients is not None, "every tried vector of K lies on the exact polar line")
    off_line = _exact_rank(_exact_block(_exact_combination(basis, [QQ_I.convert(c) for c in off_coefficients or ()])))
    return {
        "rank_lower_block": _exact_rank(block),
        "kernel_dimension": len(basis),
        "polar_line_dimension": len(line),
        "line_ranks": on_line,
        "off_line_rank": off_line,
    }


def quartic_fixture(job: tuple[int, list[int]]) -> dict[str, Any]:
    """The facts at one fixture of V(G) minus V(Q): modulo PRIME, and exact over Q(i)."""
    number, split = job
    row = {"fixture": number, **quartic_point([value % PRIME for value in split])}
    row["exact_fiber_dimension"] = exact_fiber_dimension(split)
    row["exact_polar_line"] = exact_polar_line(split)
    reduced = [value % PRIME for value in split]
    _, split_basis = kernel_three_plane(reduced)
    quadric = restrict_to_kernel(_hypersurfaces()["Q"], split_basis, 2)
    multiples = _quadric_multiples(_form_product(quadric, 2, quadric, 2))
    forms = pfaffian_forms(reduced)
    row["pfaffian_forms"] = len(forms)
    row["pfaffian_span_rank"] = _rank(forms)
    row["polar_square_multiples_rank"] = _rank(multiples)
    row["union_rank"] = _rank([*forms, *multiples])
    return row


def _pfaffian(matrix: Matrix) -> int:
    """The Pfaffian of an even skew matrix modulo PRIME, by elimination with symmetric row and column swaps."""
    size = len(matrix)
    work = [row[:] for row in matrix]
    sign, result = 1, 1
    for start in range(0, size - 1, 2):
        pivot = next((index for index in range(start + 1, size) if work[index][start] % PRIME), None)
        if pivot is None:
            return 0
        if pivot != start + 1:
            work[start + 1], work[pivot] = work[pivot], work[start + 1]
            for line in work:
                line[start + 1], line[pivot] = line[pivot], line[start + 1]
            sign = -sign
        result = result * work[start][start + 1] % PRIME
        inverse = pow(work[start + 1][start], -1, PRIME)
        for index in range(start + 2, size):
            factor = work[index][start] * inverse % PRIME
            if factor:
                work[index] = [(a - factor * b) % PRIME for a, b in zip(work[index], work[start + 1], strict=True)]
                for line in work:
                    line[index] = (line[index] - factor * line[start + 1]) % PRIME
    return sign * result % PRIME


def pfaffian_forms(split: Sequence[int]) -> list[Vector]:
    """The 91 principal 12 x 12 Pfaffians of M(k) restricted to a hyperplane x_j = 0 with z_j nonzero, as sextics on K.

    M(k) z = 0 and z^T M(k) = 0 for k in K, so deleting row and column j of M(k) keeps its rank, and rank at most 10 of
    the remaining 14 x 14 skew matrix is the vanishing of all its principal 12 x 12 Pfaffians. Each is a sextic form
    in the coordinates of K, interpolated from 28 values and checked at SEXTIC_CHECK_POINTS more.
    """
    frame = _twist(split, ROOT_OF_MINUS_ONE)
    basis, _ = kernel_three_plane(split)
    removed = next(index for index, value in enumerate(frame) if value % PRIME)
    keep = [index for index in range(IMAGINARY) if index != removed]
    full = [_block(vector) for vector in basis]
    blocks = [[[matrix[a][b] for b in keep] for a in keep] for matrix in full]
    subsets = [tuple(x for x in range(14) if x not in pair) for pair in itertools.combinations(range(14), 2)]
    points, inverse = _interpolation("sextic", 6, SEXTIC_CHECK_POINTS)
    count = len(_monomials(6))
    values = []
    for point in points[: count + SEXTIC_CHECK_POINTS]:
        total = [
            [sum(c * m[a][b] for c, m in zip(point, blocks, strict=True)) % PRIME for b in range(14)] for a in range(14)
        ]
        values.append([_pfaffian([[total[a][b] for b in subset] for a in subset]) for subset in subsets])
    return _fit_forms(values, 6, "sextic", SEXTIC_CHECK_POINTS)


def _quadric_multiples(quartic: Sequence[int]) -> Matrix:
    """The quartic times each of the six quadratic monomials, as sextic coefficient vectors."""
    return [_form_product(quartic, 4, _form({monomial: 1}, 2), 2) for monomial in _monomials(2)]


def quadric_fixture(job: tuple[int, list[int]]) -> dict[str, Any]:
    """The facts at one fixture of V(Q) minus V(G), including the span of the Pfaffians."""
    number, split = job
    reduced = [value % PRIME for value in split]
    row = {"fixture": number, **quadric_point(reduced)}
    polynomials = _hypersurfaces()
    _, split_basis = kernel_three_plane(reduced)
    multiples = _quadric_multiples(restrict_to_kernel(polynomials["G"], split_basis, 4))
    forms = pfaffian_forms(reduced)
    row["pfaffian_forms"] = len(forms)
    row["pfaffian_span_rank"] = _rank(forms)
    row["quartic_multiples_rank"] = _rank(multiples)
    row["union_rank"] = _rank([*forms, *multiples])
    return row


# The grid.
def grid_block(job: tuple[int, int, int]) -> dict[str, Any]:
    """The nullity-4 points of one block of the grid of `nullity4_gauss_image.grid_block`, classified by stratum."""
    second, third, eighth = job
    polynomials = _hypersurfaces()
    candidates = excluded = 0
    quartic_classes: dict[tuple[Any, ...], int] = {}
    quadric_classes: dict[tuple[Any, ...], int] = {}
    invariants: dict[tuple[Any, ...], int] = {}
    on_line: list[dict[str, Any]] = []
    long_scheme: list[list[int]] = []
    for count in range(4):
        for support in itertools.combinations(range(7), count):
            for values in itertools.product((-1, 1, 2), repeat=count):
                split = [1, second, third, 0, 0, 0, 0, eighth, *([0] * 7)]
                for position, value in zip(support, values, strict=True):
                    split[8 + position] = value
                candidates += 1
                reduced = [value % PRIME for value in split]
                if _rank(lower_block(reduced)) != 12 or _rank(bordered([*reduced, *reduced])) != 14:
                    continue
                membership = tuple(_value(polynomials[name], reduced) == 0 for name in ("Q", "G"))
                stratum = next(name for name, pattern in MEMBERSHIP.items() if pattern == membership)
                if stratum == EXCLUDED_STRATUM:
                    excluded += 1
                elif stratum == QUARTIC:
                    row = quartic_point(split)
                    invariants_key = (
                        row["quadric_gram_rank"],
                        row["quartic_zero_probes"],
                        row["polar_line_dimension"],
                        row.get("off_line_nullity"),
                    )
                    invariants[invariants_key] = invariants.get(invariants_key, 0) + 1
                    nullities = sorted(set(row.get("line_nullities", [])))
                    key = (
                        nullities[0] if len(nullities) == 1 else None,
                        row.get("plane_equals_line"),
                        row.get("fiber_dimension"),
                    )
                    quartic_classes[key] = quartic_classes.get(key, 0) + 1
                    if row.get("plane_equals_line") and row["fiber_dimension"] == 2:
                        on_line.append({"split_point": split, "line_nullity": key[0]})
                else:
                    row = quadric_point(split)
                    key_quadric = (
                        row["quadric_gram_rank"],
                        row["quartic_nonzero"],
                        row.get("singular_scheme_length"),
                        row.get("trisecant_hilbert_value"),
                    )
                    quadric_classes[key_quadric] = quadric_classes.get(key_quadric, 0) + 1
                    if row.get("singular_scheme_length") != 3:
                        long_scheme.append(split)
    return {
        "candidates": candidates,
        "excluded": excluded,
        "quartic_classes": quartic_classes,
        "quartic_invariants": invariants,
        "quadric_classes": quadric_classes,
        "plane_on_line": on_line,
        "long_scheme_points": long_scheme,
    }


def _merged(blocks: Sequence[dict[str, Any]], name: str) -> dict[tuple[Any, ...], int]:
    merged: dict[tuple[Any, ...], int] = {}
    for block in blocks:
        for key, count in block[name].items():
            merged[key] = merged.get(key, 0) + count
    return merged


def grid() -> dict[str, Any]:
    """The classes of the nullity-4 grid points of V(Q) minus V(G) and V(G) minus V(Q)."""
    jobs = [(second, third, eighth) for second in range(3) for third in range(3) for eighth in range(4)]
    blocks = parallel.ordered_map(grid_block, jobs, min_items=2)
    return {
        "candidates": sum(block["candidates"] for block in blocks),
        "excluded_stratum_points": sum(block["excluded"] for block in blocks),
        "quartic_classes": [
            [*key, count] for key, count in sorted(_merged(blocks, "quartic_classes").items(), key=str)
        ],
        "quartic_invariants": [
            [*key, count] for key, count in sorted(_merged(blocks, "quartic_invariants").items(), key=str)
        ],
        "quadric_classes": [
            [*key, count] for key, count in sorted(_merged(blocks, "quadric_classes").items(), key=str)
        ],
        "plane_on_line": [point for block in blocks for point in block["plane_on_line"]],
        "long_scheme_points": [point for block in blocks for point in block["long_scheme_points"]],
    }


def fixtures() -> dict[str, Any]:
    """The facts at the exact fixtures of the two strata."""
    splits = _fixture_splits()
    counts = {stratum: sum(row[1] == stratum for row in splits) for stratum in STRATA}
    quartic = [(number, split) for number, stratum, split in splits if stratum == QUARTIC]
    quadric = [(number, split) for number, stratum, split in splits if stratum == QUADRIC]
    return {
        "stratum_counts": counts,
        "quartic_stratum": parallel.ordered_map(quartic_fixture, quartic, min_items=2),
        "quadric_stratum": parallel.ordered_map(quadric_fixture, quadric, min_items=2),
    }


def _inputs() -> dict[str, str]:
    return {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in SOURCE_PATHS}


def compute() -> dict[str, Any]:
    record: dict[str, Any] = {
        "schema": SCHEMA,
        "field": FIELD,
        "inputs": _inputs(),
        "quartic_probes": {
            "points": QUARTIC_PROBES,
            "coefficients": QUARTIC_COEFFICIENTS,
            "monomial_rank": quartic_probe_rank(),
        },
        "calibration": calibration(),
        "fixtures": fixtures(),
        "grid": grid(),
    }
    record["pass"] = verdict(record) == []
    return record


def _fixture_problems(record: dict[str, Any]) -> list[str]:
    """The rules on the rows at the exact fixtures of the two strata."""
    problems = []
    found = record["fixtures"]
    if found.get("stratum_counts") != FIXTURE_STRATUM_COUNTS:
        problems.append("the exact fixtures fall in other strata than 12, 52 and 2")
    rows = found["quadric_stratum"]
    if [row["fixture"] for row in rows] != list(QUADRIC_FIXTURES):
        problems.append("the rows of V(Q) minus V(G) are other fixtures")
    for row in rows:
        name = f"fixture {row['fixture']}"
        if row["quadric_gram_rank"] != 0:
            problems.append(f"{name}: Q does not vanish on ker M(z)")
        if row["quartic_nonzero"] is not True:
            problems.append(f"{name}: G vanishes on ker M(z)")
        if not line_free(row):
            problems.append(f"{name}: no certificate that the quartic G|_K contains no line")
        if row["singular_scheme_length"] != 3:
            problems.append(f"{name}: the singular scheme of the quartic G|_K does not have length 3")
        if (row["pfaffian_forms"], row["pfaffian_span_rank"], row["quartic_multiples_rank"], row["union_rank"]) != (
            PFAFFIAN_SUBSETS,
            PFAFFIAN_SPAN_RANK,
            PFAFFIAN_SPAN_RANK,
            PFAFFIAN_SPAN_RANK,
        ):
            problems.append(f"{name}: the Pfaffians do not span G|_K times the quadratic monomials")
    rows = found["quartic_stratum"]
    if [row["fixture"] for row in rows] != list(QUARTIC_FIXTURES):
        problems.append("the rows of V(G) minus V(Q) are other fixtures")
    classes: dict[tuple[int, bool, int], list[int]] = {}
    for row in rows:
        name = f"fixture {row['fixture']}"
        problems += _quartic_row_problems(row, name)
        spans = (row.get("pfaffian_span_rank"), row.get("polar_square_multiples_rank"), row.get("union_rank"))
        if (row.get("pfaffian_forms"), *spans) != (PFAFFIAN_SUBSETS, *([PFAFFIAN_SPAN_RANK] * 3)):
            problems.append(f"{name}: the Pfaffians do not span the square of Q|_K times the quadratic monomials")
        exact = row.get("exact_polar_line", {})
        nullity_on_line = sorted(set(row.get("line_nullities", [])))
        expected_rank = EXACT_LINE_RANKS.get(nullity_on_line[0]) if len(nullity_on_line) == 1 else None
        if exact != {
            "rank_lower_block": 12,
            "kernel_dimension": 3,
            "polar_line_dimension": 2,
            "line_ranks": [expected_rank] * len(LINE_PARAMETERS),
            "off_line_rank": EXACT_OFF_LINE_RANK,
        }:
            problems.append(f"{name}: the exact polar line has other ranks than the modular one")
        if row.get("fiber_dimension") != row.get("exact_fiber_dimension"):
            problems.append(f"{name}: dim L modulo {PRIME} differs from the exact dim L")
        if len(nullity_on_line) == 1:
            key = (row["exact_fiber_dimension"], row["plane_equals_line"], nullity_on_line[0])
            classes.setdefault(key, []).append(row["fixture"])
    if {key: tuple(members) for key, members in classes.items()} != FIXTURE_CLASSES:
        problems.append("the classes of the fixtures of V(G) minus V(Q) differ from the expected table")
    return problems


def _quartic_row_problems(row: dict[str, Any], name: str) -> list[str]:
    """The rules on one point of V(G) minus V(Q): G vanishes on K, Q has Gram rank 1, the polar line, the nullities."""
    problems = []
    if row.get("quadric_gram_rank") != 1:
        problems.append(f"{name}: the Gram matrix of Q on ker M(z) does not have rank 1")
    if row.get("quartic_zero_probes") != QUARTIC_PROBES:
        problems.append(f"{name}: G does not vanish at every probe point of ker M(z)")
    if row.get("polar_line_dimension") != 2:
        problems.append(f"{name}: the polar line K n ker dQ_z does not have dimension 2")
    nullities = row.get("line_nullities", [])
    if len(nullities) != len(LINE_PARAMETERS) or len(set(nullities)) != 1 or not set(nullities) <= LINE_NULLITIES:
        problems.append(f"{name}: M(k) does not have one nullity, 7 or 9, at the six vectors of the polar line")
    if row.get("off_line_nullity") != OFF_LINE_NULLITY:
        problems.append(f"{name}: M(k) does not have nullity 3 at a vector of ker M(z) off the polar line")
    return problems


def _grid_problems(lattice: dict[str, Any]) -> list[str]:
    """The rules on the nullity-4 grid points of the two strata."""
    problems = []
    if lattice.get("candidates") != GRID_CANDIDATES:
        problems.append("the grid has another number of candidates")
    if lattice.get("excluded_stratum_points") != EXCLUDED_GRID_POINTS:
        problems.append("the grid has another number of points on V(Q) n V(G)")
    classes = {tuple(row[:3]): row[3] for row in lattice["quartic_classes"]}
    if classes != GRID_CLASSES or len(lattice["quartic_classes"]) != len(GRID_CLASSES):
        problems.append("the classes of the grid points of V(G) minus V(Q) differ from the expected table")
    if any(fiber > 2 and not on_line for _, on_line, fiber in classes):
        problems.append("a grid point of V(G) minus V(Q) has dim L above 2 with a kernel plane off the polar line")
    invariants = [tuple(row) for row in lattice["quartic_invariants"]]
    if invariants != [(1, QUARTIC_PROBES, 2, OFF_LINE_NULLITY, GRID_QUARTIC_POINTS)]:
        problems.append(
            "a grid point of V(G) minus V(Q) differs in Gram rank, probe zeros, polar line or off-line nullity"
        )
    if sum(classes.values()) != GRID_QUARTIC_POINTS:
        problems.append("the grid has another number of points on V(G) minus V(Q)")
    quadric_classes = {tuple(row[:4]): row[4] for row in lattice["quadric_classes"]}
    if quadric_classes != GRID_QUADRIC_CLASSES or len(lattice["quadric_classes"]) != len(GRID_QUADRIC_CLASSES):
        problems.append("the classes of the grid points of V(Q) minus V(G) differ from the expected table")
    if any(
        gram != 0 or not nonzero or length is None or value != 0 for gram, nonzero, length, value in quadric_classes
    ):
        problems.append("a grid point of V(Q) minus V(G) has no certificate that G|_K is a quartic with no line")
    if sum(quadric_classes.values()) != GRID_QUADRIC_POINTS:
        problems.append("the grid has another number of points on V(Q) minus V(G)")
    long_scheme = lattice["long_scheme_points"]
    digest = hashlib.sha256(json.dumps(long_scheme).encode()).hexdigest()
    if len(long_scheme) != LONG_SCHEME_POINTS or digest != LONG_SCHEME_SHA256:
        problems.append(
            "the grid points of V(Q) minus V(G) with a singular scheme of another length than 3 are other points"
        )
    if len(long_scheme) != sum(count for (_, _, length, _), count in quadric_classes.items() if length != 3):
        problems.append("the grid classes and the points of a singular scheme of another length than 3 disagree")
    points = {tuple(row["split_point"]): row["line_nullity"] for row in lattice["plane_on_line"]}
    if len(lattice["plane_on_line"]) != len(PLANE_ON_LINE_POINTS) or points != {p: 7 for p in PLANE_ON_LINE_POINTS}:
        problems.append("the grid points with P = l_z and dim L = 2 are other points")
    return problems


def verdict(record: dict[str, Any]) -> list[str]:
    """The reasons the record fails its own rules; empty when it passes."""
    problems = []
    if (record.get("schema"), record.get("field")) != (SCHEMA, FIELD):
        problems.append("the record is headed otherwise")
    if record.get("inputs") != _inputs():
        problems.append("the input digests differ from the files")
    if record.get("pass", True) is not True:
        problems.append("the record states that it fails")
    if record.get("quartic_probes") != {
        "points": QUARTIC_PROBES,
        "coefficients": QUARTIC_COEFFICIENTS,
        "monomial_rank": QUARTIC_COEFFICIENTS,
    }:
        problems.append("the probe points do not fix a plane quartic")
    calibrated = record.get("calibration", {})
    if calibrated != CALIBRATION:
        problems.append("the line certificate differs from its calibration on known quartics")
    if not all(line_free(calibrated.get(name, {})) for name in LINE_FREE_CALIBRATION) or any(
        line_free(certificate) for name, certificate in calibrated.items() if name not in LINE_FREE_CALIBRATION
    ):
        problems.append("the line certificate does not separate the quartic without a line from the quartics with one")
    return [*problems, *_fixture_problems(record), *_grid_problems(record["grid"])]


def main() -> None:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    record = compute()
    if args.write:
        RECORD.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    elif json.loads(RECORD.read_text(encoding="utf-8")) != record:
        raise SystemExit(f"{RECORD.name} differs from the recomputation")
    problems = verdict(record)
    if problems:
        raise SystemExit("\n".join(problems))
    lattice = record["grid"]
    print(
        "fixtures",
        {
            stratum: len(record["fixtures"][name])
            for stratum, name in ((QUADRIC, "quadric_stratum"), (QUARTIC, "quartic_stratum"))
        },
    )
    print("grid V(G) minus V(Q) classes (nullity on l_z, P = l_z, dim L, count)", lattice["quartic_classes"])
    print(
        "grid V(Q) minus V(G) classes (Gram rank, G|_K nonzero, length, trisecant value, count)",
        lattice["quadric_classes"],
    )


if __name__ == "__main__":
    main()
