"""The nullity-4 kernel Gauss map factors through the planes of the three-planes ker M(z): ranks, fibers, image.

The bordered skew matrix A(z, w) of `kernel_frames._bordered_matrix` has first row -w and lower 15 x 15 block M(z),
linear in z; at a real point w is the conjugate of z. This producer treats z and w as independent, in split
coordinates z_k = i^popcount(k) z'_k, w_k = (-i)^popcount(k) w'_k, with i sent to 9115 modulo 32029, and measures at
deterministic points of the three nullity-4 strata V(Q) minus V(G), V(G) minus V(Q) and V(Q) n V(G):

- rank M(z) = 12 with z in ker M(z), and rank A(z, w) = 14 for every sampled w, on the stratum or off it;
- ker A(z, w) has first coordinate zero, lies in ker M(z) and is orthogonal to w: it is the plane ker M(z) n w-perp
  of the three-plane ker M(z);
- the rank of the differential of z -> ker M(z) on the stratum (the dimension of the family of three-planes), of
  the Gauss map (z, w) -> ker A(z, w) with w free and with w on the conjugate stratum, and of the pair (Gauss map,
  conjugate Gauss map) on stratum x conjugate stratum at an independent pair (z, w): the complexified ranks at a
  general pair;
- the dimension of the linear span of the Plucker vectors of 300 sampled kernel planes and the rank of the 5,565
  quadratic monomials in the 105 Plucker coordinates of Gr(2, 15) at 6,100 sampled planes, read also at 5,800.
  Monomials minus rank counts the quadrics that vanish on the sampled planes, an upper bound for the quadrics that
  vanish on the image.

Off the strata the control point has rank M = 14 with kernel spanned by z, and rank A = 16.

The retained fixture record `nullity4-kernel-gauss-result.json` (exact, characteristic 0) holds 66 real points with
integer split coordinates, where w' = z'. It is read for two facts. At each fixture the 15 Plucker coordinates
p_(0 j) vanish, the first-coordinate statement above. At each fixture reduced modulo 32029 the same differentials
are computed on the real locus: the rank of the pair there is the rank over the reals of the Gauss map
z -> ker A(z, conjugate(z)). A rank modulo 32029 is a lower bound for the rank in characteristic 0 (the pivot
block is invertible modulo the prime and the tangent space keeps its dimension), and the two scalings of z and w
bound the rank of the pair by 26, 26 and 24, so a fixture that reaches the bound has that real rank in
characteristic 0.

A(z, w) is linear in (z, w), so the pairs with a given kernel plane P and conjugate kernel plane P' form the
linear space L = {(z, w): A(z, w) P = 0 and A-bar(w, z) P' = 0}: the fiber of the pair of Gauss maps is linear, it
contains the two scalings, and the differential of the pair has rank at most the tangent dimension minus dim L.
dim L is computed exactly over Q(i) at each fixture; where the rank modulo 32029 equals that bound it is the rank
in characteristic 0.

Four exact facts are joined to those ranks fixture by fixture: dim L; the rank of the orbit of the 18-dimensional
kernel symmetry algebra of `kernel_symmetry.py` at the fixture (16 at a general point, 13 on a special sublocus);
the least nullity among six vectors of the real kernel of left multiplication by the fixture, each taken as an
element of the algebra; and the class of fixtures with the same normalized Plucker vector in the retained record,
that is, the same kernel plane. Two fixtures of one class have different three-planes ker M(z): the two kernels
span a 4-space modulo 32029, the largest span of two three-planes through one plane, so the Gauss image is the
projection to Gr(2, 15) of the bundle of pairs (K, P in K) and that projection is not injective.

A grid of 41,616 integer points e_1 + a e_2 + b e_3 + m e_8 + v, v with at most three nonzero coordinates among
e_9..e_15, is then filtered to its nullity-4 points and the same three invariants are computed modulo 32029 with
w' = z'. An orbit rank of 16 modulo the prime is exact, and so is a fiber of dimension 2; the grid points where
the fiber is larger at orbit rank 16, or the kernel vectors have higher nullity at fiber dimension 2, have their
fiber recomputed exactly.

The fiber is then read from the kernel plane itself. The signs of the lower block satisfy
SIGNS[r][r ^ c] = -SIGNS[r][c], so M(z) p = -M(p) z, and for a basis p1, p2 of the kernel plane P the z-part of L is
{z in ker M(p1) n ker M(p2): z orthogonal to the conjugate plane P'}. `kernel_form` computes modulo 32029 the
nullity of M(p) at the probe vector p1 + 7 p2 of P, the dimension of ker M(p1) n ker M(p2) and of its cut by P', and the
nullities of M(k) on a net of 342 vectors k of the three-plane ker M(z), at the 66 fixtures and at every nullity-4
grid point. One probe vector does not decide the nullity on the plane, so at the 9 grid points where the probe
has nullity 7 and dim L = 2 the nullity is recomputed over Q(i) at six further vectors of the plane and at the
probe: it is 7 at all seven at 8 points; at one point it is 3 at the six and 7 at the probe, where the plane meets
the higher zero divisors of ker M(z) in that single point.

Two further samples bear on the real points of V(Q) minus V(G): 469 real points of V(Q) with
Gaussian-integer split coordinates, where w' is the conjugate of z' and independent of it, obtained by projecting
V(Q) from its 12 fixtures along Gaussian directions; and, at 25 sampled points z0 of each stratum, 40 general
planes of ker M(z0) that avoid z0, with the dimension of {z: P in ker M(z)}.

The points come from sha256 of a label and a counter, reduced modulo 32029: a fixed list, with no seed.

`--write` writes nullity4-gauss-image-result.json beside this file; `--check` recomputes and compares.

Run from the repository root: "$PYTHON" docs/evidence/a5-kernel-bundles-residuals/nullity4_gauss_image.py --check
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import re
import sys
from collections.abc import Callable, Sequence
from fractions import Fraction
from pathlib import Path
from typing import Any

from flint import nmod_mat, nmod_poly
from sympy import QQ_I, I
from sympy.polys.matrices import DomainMatrix

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BUNDLES = HERE.parent / "a5-kernel-bundles"
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(BUNDLES))

import kernel_frames as frames  # noqa: E402
import kernel_symmetry as symmetry  # noqa: E402

import parallel  # noqa: E402
from cd_core import cd_sign  # noqa: E402

SCHEMA = "a5-kernel-bundles-residuals-nullity4-gauss-image-v1"
RECORD = HERE / "nullity4-gauss-image-result.json"
FIXTURES = HERE / "nullity4-kernel-gauss-result.json"
SOURCE_PATHS = (
    HERE / "nullity4_gauss_image.py",
    BUNDLES / "kernel_frames.py",
    BUNDLES / "kernel_symmetry.py",
    ROOT / "docs" / "evidence" / "a5-strata-regularity" / "strata_regularity.py",
    ROOT / "docs" / "evidence" / "a5-rank-strata-equations" / "rederive_strata_equations.py",
    ROOT / "gororoba_quantum" / "cd_core.py",
    FIXTURES,
)
PRIME, ROOT_OF_MINUS_ONE = 32029, 9115
FIELD = f"GF({PRIME}), i = {ROOT_OF_MINUS_ONE}"
IMAGINARY, BORDERED = 15, 16
STRATA = ("V(Q) minus V(G)", "V(G) minus V(Q)", "V(Q) intersect V(G)")
# Whether Q and whether G vanish on the stratum.
MEMBERSHIP = {STRATA[0]: (True, False), STRATA[1]: (False, True), STRATA[2]: (True, True)}
RANK_POINTS = 4
FREE_W_PER_POINT = 3
PLUCKER_PAIRS = tuple(itertools.combinations(range(1, BORDERED), 2))
QUADRIC_MONOMIALS = tuple(itertools.combinations_with_replacement(range(len(PLUCKER_PAIRS)), 2))
PLUCKER_QUADRICS = math.comb(IMAGINARY, 4)
LINEAR_SAMPLES = 300
QUADRIC_SAMPLES = (5800, 6100)
# Per stratum: rank of the three-plane map, of the Gauss map (w free, w on the conjugate stratum), of the pair
# (Gauss map, conjugate Gauss map), the dimension of the linear span of the sampled planes and the number of
# quadrics that vanish on them.
EXPECTED: dict[str, dict[str, int]] = {
    STRATA[0]: {
        "tangent_dimension": 14,
        "three_plane_map_rank": 13,
        "gauss_rank_w_free": 15,
        "conjugate_pair_rank": 26,
        "linear_span_dimension": 105,
        "quadrics_vanishing": 1678,
    },
    STRATA[1]: {
        "tangent_dimension": 14,
        "three_plane_map_rank": 13,
        "gauss_rank_w_free": 15,
        "conjugate_pair_rank": 26,
        "linear_span_dimension": 105,
        "quadrics_vanishing": 1543,
    },
    STRATA[2]: {
        "tangent_dimension": 13,
        "three_plane_map_rank": 10,
        "gauss_rank_w_free": 12,
        "conjugate_pair_rank": 24,
        "linear_span_dimension": 90,
        "quadrics_vanishing": 2940,
    },
}
SIGNS = tuple(
    tuple(cd_sign(BORDERED, row ^ column, column) if row and column and row != column else 0 for column in range(16))
    for row in range(16)
)
# Exact real fixtures by (stratum, exact rank of the symmetry orbit, rank of the three-plane map, rank of the Gauss
# map on the real locus, real rank), the last three modulo PRIME.
FIXTURE_RANKS: dict[tuple[str, int, int, int, int], int] = {
    (STRATA[0], 16, 13, 15, 26): 3,
    (STRATA[0], 13, 13, 15, 26): 9,
    (STRATA[1], 16, 13, 15, 26): 23,
    (STRATA[1], 13, 13, 13, 22): 13,
    (STRATA[1], 13, 13, 10, 16): 16,
    (STRATA[2], 16, 10, 12, 24): 2,
}
# Exact dim L at a fixture by (stratum, real rank): tangent dimension of stratum x conjugate stratum minus the rank.
FIBER_DIMENSIONS = {26: 2, 24: 2, 22: 6, 16: 12}
# Nullity-4 grid points by (stratum, orbit rank, dim L, least nullity of a sampled kernel vector), modulo PRIME.
GRID_CANDIDATES = 41616
GRID_CLASSES: dict[tuple[str, int, int, int], int] = {
    (STRATA[0], 13, 2, 4): 371,
    (STRATA[0], 16, 2, 4): 1725,
    (STRATA[1], 13, 6, 12): 61,
    (STRATA[1], 13, 12, 16): 78,
    (STRATA[1], 16, 2, 4): 1042,
    (STRATA[1], 16, 2, 12): 8,
    (STRATA[1], 16, 12, 16): 14,
    (STRATA[2], 16, 2, 4): 384,
    (STRATA[2], 16, 6, 12): 4,
}
# Classes that refute "dim L > 2 exactly at orbit rank 13" and "dim L > 2 exactly at kernel nullity above 4".
GRID_EXCEPTIONS = ((STRATA[1], 16, 2, 12), (STRATA[1], 16, 12, 16), (STRATA[2], 16, 6, 12))
KERNEL_COMBINATIONS = ((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1), (1, 2, 3, 5), (2, -1, 7, 3))
# Distinct kernel planes among the 66 exact fixtures, and the fixtures that share a plane with another one.
FIXTURE_PLANES, FIXTURES_ON_SHARED_PLANES = 54, 22
# Sizes of the ten shared classes, and the real ranks of the 22 fixtures in them.
SHARED_PLANE_SIZES = [2] * 8 + [3] * 2
SHARED_PLANE_REAL_RANKS = [16] * 12 + [22] * 10
# Exact fixtures by (stratum, dim L, nullity of M(p) at a general vector p of the kernel plane, dimension of
# ker M(p1) n ker M(p2), its dimension after the cut by the conjugate plane, nullities of M(k) on the net of
# ker M(z) as (nullity, vectors, projective points, span, span with the kernel plane) rows), modulo PRIME, each
# class with its fixture numbers. Vectors of one nullity lie on one projective line when their span is 2, and
# that line is the kernel plane when the span stays 2 with the plane added.
# The net has 342 vectors on 145 projective points; a line through it holds at most 48 vectors on 16 points, and
# a point holds 6 vectors when its coprime combination has entries -1..1 and 2 otherwise.
KERNEL_FORM_FIXTURES: dict[tuple[Any, ...], tuple[int, ...]] = {
    (STRATA[0], 2, 3, 1, 1, ((3, 336, 144, 3, 3), (5, 6, 1, 1, 2))): (43, 45),
    (STRATA[0], 2, 3, 1, 1, ((3, 336, 144, 3, 3), (7, 6, 1, 1, 2))): (13, 61),
    (STRATA[0], 2, 3, 1, 1, ((3, 338, 143, 3, 3), (5, 4, 2, 2, 3))): (65,),
    (STRATA[0], 2, 3, 1, 1, ((3, 342, 145, 3, 3),)): (14, 19, 24, 25, 42, 44, 62),
    (STRATA[1], 2, 3, 1, 1, ((3, 294, 129, 3, 3), (9, 48, 16, 2, 3))): (30, 34),
    (STRATA[1], 2, 3, 1, 1, ((3, 322, 137, 3, 3), (9, 20, 8, 2, 3))): (52, 55),
    (STRATA[1], 2, 3, 1, 1, ((3, 336, 144, 3, 3), (7, 6, 1, 1, 2))): (47,),
    (STRATA[1], 2, 3, 1, 1, ((3, 336, 144, 3, 3), (9, 6, 1, 1, 3))): (41, 63),
    (STRATA[1], 2, 3, 1, 1, ((3, 340, 144, 3, 3), (7, 2, 1, 1, 2))): (46,),
    (STRATA[1], 2, 3, 1, 1, ((3, 340, 144, 3, 3), (9, 2, 1, 1, 3))): (33, 37, 49, 54, 57, 58),
    (STRATA[1], 2, 3, 1, 1, ((3, 342, 145, 3, 3),)): (29, 32, 36, 39, 40, 50, 51, 59, 60),
    (STRATA[1], 6, 7, 3, 3, ((3, 294, 129, 3, 3), (7, 48, 16, 2, 2))): (
        0,
        15,
        16,
        17,
        18,
        20,
        21,
        22,
        23,
        26,
        27,
        48,
        64,
    ),
    (STRATA[1], 12, 9, 6, 6, ((3, 294, 129, 3, 3), (9, 48, 16, 2, 2))): (
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        31,
        35,
        53,
        56,
    ),
    (STRATA[2], 2, 3, 3, 1, ((3, 336, 144, 3, 3), (9, 6, 1, 1, 3))): (28, 38),
}
# Nullity-4 grid points by (stratum, dim L, plane nullity, common kernel, cut common kernel), modulo PRIME.
KERNEL_FORM_GRID: dict[tuple[str, int, int, int, int], int] = {
    (STRATA[0], 2, 3, 1, 1): 2096,
    (STRATA[1], 2, 3, 1, 1): 1041,
    (STRATA[1], 2, 7, 1, 1): 1,
    (STRATA[1], 2, 7, 3, 1): 8,
    (STRATA[1], 6, 7, 3, 3): 61,
    (STRATA[1], 12, 9, 6, 6): 92,
    (STRATA[2], 2, 3, 3, 1): 384,
    (STRATA[2], 6, 7, 5, 3): 4,
}
# Grid classes with nullity 7 at the probe vector modulo PRIME and dim L = 2, and the exact nullities of M(p) at
# six further vectors of the plane and at the probe, by the dimension of the common kernel: the 8 points of common
# kernel 3 refute "dim L > 2 exactly where every vector of the kernel plane has nullity above 3"; at the point of
# common kernel 1 the probe is the only vector of the plane, up to scale, among the seven with nullity above 3.
KERNEL_FORM_EXCEPTIONS = ((STRATA[1], 2, 7, 1, 1), (STRATA[1], 2, 7, 3, 1))
EXACT_PLANE_NULLITY = {1: [3, 3, 3, 3, 3, 3, 7], 3: [7] * 7}
# Multiplier of the probe vector p1 + PROBE p2 on the echelon basis p1, p2 of a kernel plane.
PROBE = 7
# The split points of those nine grid points, each with the dimension of its common kernel.
PLANE_EXCEPTION_POINTS: dict[tuple[int, ...], int] = {
    (1, 0, 1, 0, 0, 0, 0, 1, 0, 0, -1, -1, 1, 0, 0): 3,
    (1, 0, 1, 0, 0, 0, 0, 1, 0, 0, -1, 1, -1, 0, 0): 3,
    (1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, -1, -1, 0, 0): 3,
    (1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 0): 3,
    (1, 0, 1, 0, 0, 0, 0, 1, 0, 0, -1, 0, 0, -1, -1): 3,
    (1, 0, 1, 0, 0, 0, 0, 1, 0, 0, -1, 0, 0, 1, 1): 3,
    (1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, -1, 1): 3,
    (1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, -1): 3,
    (1, 0, 2, 0, 0, 0, 0, 2, 2, 0, 0, 0, 2, -1, 0): 1,
}
# Gaussian real points of V(Q): 40 directions at each of the 12 fixtures of V(Q) minus V(G); the pairs kept, all
# in the class (Q = 0, G != 0, dim L 2, plane nullity 3, common kernel 1, cut common kernel 1), and the rest: a
# real direction (2), a line inside V(Q) modulo PRIME (1), a tangent direction, which returns the fixture (8), a
# pair of another nullity (0).
GAUSSIAN_PER_FIXTURE = 40
GAUSSIAN_CLASSES, GAUSSIAN_REJECTED = [[1, 0, 2, 3, 1, 1, 469]], [2, 1, 8, 0]
# Sampled points per stratum, planes of ker M(z0) off z0 per point, and dim {z: P in ker M(z)} at every such plane.
PLANE_POINTS, PLANES_PER_POINT = 25, 40
GENERAL_PLANE_KERNELS = {STRATA[0]: [1], STRATA[1]: [1], STRATA[2]: [3]}
Vector = list[int]
Matrix = list[list[int]]


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _flint(rows: Matrix) -> nmod_mat:
    return nmod_mat(len(rows), len(rows[0]), [value % PRIME for row in rows for value in row], PRIME)


def _rank(rows: Matrix) -> int:
    return int(_flint(rows).rank())


def _nullspace(rows: Matrix) -> Matrix:
    basis, nullity = _flint(rows).nullspace()
    return [[int(basis[i, j]) for i in range(len(rows[0]))] for j in range(nullity)]


class Points:
    """Coordinates modulo PRIME from sha256 of a label and a counter."""

    def __init__(self, label: str) -> None:
        self.label, self.counter = label, 0

    def value(self) -> int:
        self.counter += 1
        digest = hashlib.sha256(f"{self.label}:{self.counter}".encode()).digest()
        return int.from_bytes(digest[:8], "big") % PRIME

    def vector(self) -> Vector:
        return [self.value() for _ in range(IMAGINARY)]


def _twist(split: Sequence[int], unit: int) -> Vector:
    return [pow(unit, (index + 1).bit_count(), PRIME) * value % PRIME for index, value in enumerate(split)]


def bordered(point: Sequence[int], conjugate: bool = False) -> Matrix:
    """A(z, w) at the split point (z', w') of length 30; with `conjugate`, its complex conjugate A-bar(w, z)."""
    first, second = (point[IMAGINARY:], point[:IMAGINARY]) if conjugate else (point[:IMAGINARY], point[IMAGINARY:])
    unit = PRIME - ROOT_OF_MINUS_ONE if conjugate else ROOT_OF_MINUS_ONE
    z, w = _twist(first, unit), _twist(second, PRIME - unit)
    matrix = [[0] * BORDERED for _ in range(BORDERED)]
    for index in range(1, BORDERED):
        matrix[0][index], matrix[index][0] = -w[index - 1] % PRIME, w[index - 1]
    for row in range(1, BORDERED):
        for column in range(1, BORDERED):
            if row != column:
                matrix[row][column] = SIGNS[row][column] * z[(row ^ column) - 1] % PRIME
    return matrix


def conjugate_bordered(point: Sequence[int]) -> Matrix:
    return bordered(point, conjugate=True)


def lower_block(split: Sequence[int]) -> Matrix:
    """M(z): A(z, 0) without its first row and column."""
    return [row[1:] for row in bordered([*split, *([0] * IMAGINARY)])[1:]]


def _polynomials() -> dict[str, Any]:
    ideals = frames.regularity.closure_ideals()
    return {"Q": ideals["VQ"][0], "G": ideals["VG"][0]}


def _value(polynomial: Any, point: Sequence[int]) -> int:
    return int(polynomial(*point)) % PRIME


def _gradient(polynomial: Any, point: Sequence[int]) -> Vector:
    return [int(polynomial.derivative(index)(*point)) % PRIME for index in range(IMAGINARY)]


def _roots(function: Callable[[int], int], degree: int) -> list[int]:
    """Roots modulo PRIME of a univariate polynomial of at most the given degree, known through its values."""
    nodes = list(range(1, degree + 2))
    coefficients = [0] * (degree + 1)
    for node in nodes:
        numerator, denominator = [1], 1
        for other in nodes:
            if other != node:
                numerator = [
                    (low - other * high) % PRIME for low, high in zip([0, *numerator], [*numerator, 0], strict=True)
                ]
                denominator = denominator * (node - other) % PRIME
        scale = function(node) * pow(denominator, -1, PRIME) % PRIME
        for position, value in enumerate(numerator):
            coefficients[position] = (coefficients[position] + scale * value) % PRIME
    if not any(coefficients):
        return []
    return sorted(int(root) for root, _ in nmod_poly(coefficients, PRIME).roots())


def _on_hypersurface(polynomial: Any, degree: int, points: Points) -> Vector:
    """A point of the hypersurface: 14 coordinates from the list, the last one a root."""
    while True:
        point = points.vector()

        def restricted(last: int, base: Vector = point) -> int:
            return _value(polynomial, [*base[:-1], last])

        roots = _roots(restricted, degree)
        if roots:
            return [*point[:-1], roots[points.value() % len(roots)]]


def _on_intersection(polynomials: dict[str, Any], points: Points) -> Vector:
    """A point of V(Q) n V(G): the conic through a point of V(Q) along a pencil of directions, cut by G."""
    quadric, quartic = polynomials["Q"], polynomials["G"]
    while True:
        base, first, second = _on_hypersurface(quadric, 2, points), points.vector(), points.vector()

        def on_quadric(parameter: int, base: Vector = base, first: Vector = first, second: Vector = second) -> Vector:
            direction = [(a + parameter * b) % PRIME for a, b in zip(first, second, strict=True)]
            norm = _value(quadric, direction)
            polar = (_value(quadric, [(a + b) % PRIME for a, b in zip(base, direction, strict=True)]) - norm) % PRIME
            return [(norm * a - polar * b) % PRIME for a, b in zip(base, direction, strict=True)]

        for root in _roots(lambda parameter: _value(quartic, on_quadric(parameter)), 8):
            point = on_quadric(root)
            if any(point) and _value(quadric, point) == 0 and _value(quartic, point) == 0:
                return point


def sample(stratum: str, points: Points, polynomials: dict[str, Any]) -> Vector:
    """A point of the stratum in split coordinates, off the other hypersurface where the stratum excludes it."""
    while True:
        if stratum == STRATA[0]:
            point = _on_hypersurface(polynomials["Q"], 2, points)
            accepted = _value(polynomials["G"], point) != 0
        elif stratum == STRATA[1]:
            point = _on_hypersurface(polynomials["G"], 4, points)
            accepted = _value(polynomials["Q"], point) != 0
        else:
            point = _on_intersection(polynomials, points)
            accepted = True
        if accepted:
            return point


def tangent_space(stratum: str, point: Sequence[int], polynomials: dict[str, Any]) -> Matrix:
    names = {STRATA[0]: ("Q",), STRATA[1]: ("G",), STRATA[2]: ("Q", "G")}[stratum]
    return _nullspace([_gradient(polynomials[name], point) for name in names])


def _principal_pivots(matrix: Matrix, rank: int) -> list[int]:
    """Indices of an invertible principal block of a skew matrix of the given rank, grown two indices at a time."""
    pivots: list[int] = []
    while len(pivots) < rank:
        rest = [index for index in range(len(matrix)) if index not in pivots]
        for pair in itertools.combinations(rest, 2):
            trial = sorted([*pivots, *pair])
            if _rank([[matrix[a][b] for b in trial] for a in trial]) == len(trial):
                pivots = trial
                break
        else:
            raise RuntimeError("no principal block of full rank")
    return pivots


def kernel_differential(
    matrix_of: Callable[[Sequence[int]], Matrix], point: Sequence[int], directions: Matrix, rank: int
) -> tuple[Matrix, Matrix]:
    """Chart coordinates of d ker(matrix_of) along each direction, and the Schur frame of the kernel.

    matrix_of is linear. With principal pivots P and free rows F the frame is K = [-A_PP^-1 A_PF; I], and along a
    direction v tangent to the rank locus dK = -A_PP^-1 (A(v) K)_P, zero on F. Callers pass directions from the
    kernel of the gradients of the stratum (`tangent_space`). K^T A(v) K = 0 is checked: every tangent direction
    satisfies it, and on V(Q) n V(G), where the rank locus is singular, other directions satisfy it too.
    """
    matrix = matrix_of(point)
    size = len(matrix)
    pivots = _principal_pivots(matrix, rank)
    free = [index for index in range(size) if index not in pivots]
    inverse = _flint([[matrix[a][b] for b in pivots] for a in pivots]).inv()
    upper = inverse * _flint([[-matrix[a][b] for b in free] for a in pivots])
    frame = [[0] * len(free) for _ in range(size)]
    for position, row in enumerate(pivots):
        frame[row] = [int(upper[position, column]) for column in range(len(free))]
    for position, row in enumerate(free):
        frame[row][position] = 1
    product = _flint(matrix) * _flint(frame)
    _require(product.rank() == 0, "the Schur frame leaves the kernel")
    rows = []
    for direction in directions:
        moved = _flint(matrix_of(direction)) * _flint(frame)
        _require((_flint(frame).transpose() * moved).rank() == 0, "a direction leaves the rank locus")
        change = inverse * _flint([[-int(moved[a, column]) for column in range(len(free))] for a in pivots])
        rows.append([int(change[i, j]) for i in range(len(pivots)) for j in range(len(free))])
    return rows, frame


def rank_point(job: tuple[str, int]) -> dict[str, Any]:
    """Every rank and kernel statement at one point of one stratum."""
    stratum, number = job
    polynomials = _polynomials()
    points = Points(f"rank:{stratum}:{number}")
    z, w_on = sample(stratum, points, polynomials), sample(stratum, points, polynomials)
    block = lower_block(z)
    block_kernel = _nullspace(block)
    twisted = _twist(z, ROOT_OF_MINUS_ONE)
    free_w = [points.vector() for _ in range(FREE_W_PER_POINT)]
    kernel_checks = []
    for w in [*free_w, w_on]:
        matrix = bordered([*z, *w])
        kernel = _nullspace(matrix)
        border = _twist(w, PRIME - ROOT_OF_MINUS_ONE)
        kernel_checks.append(
            {
                "rank_bordered": _rank(matrix),
                "first_coordinate_zero": all(vector[0] == 0 for vector in kernel),
                "inside_lower_kernel": _rank([*block_kernel, *(vector[1:] for vector in kernel)]) == len(block_kernel),
                "orthogonal_to_w": all(
                    sum(a * b for a, b in zip(border, vector[1:], strict=True)) % PRIME == 0 for vector in kernel
                ),
            }
        )
    tangent_z = tangent_space(stratum, z, polynomials)
    tangent_w = tangent_space(stratum, w_on, polynomials)
    zero = [0] * IMAGINARY
    along_z = [[*direction, *zero] for direction in tangent_z]
    every_w = [[*zero, *(int(i == k) for i in range(IMAGINARY))] for k in range(IMAGINARY)]
    along_w = [[*zero, *direction] for direction in tangent_w]
    three_planes, _ = kernel_differential(lower_block, z, tangent_z, IMAGINARY - len(block_kernel))
    free, _ = kernel_differential(bordered, [*z, *free_w[0]], [*along_z, *every_w], 14)
    on_stratum, _ = kernel_differential(bordered, [*z, *w_on], [*along_z, *along_w], 14)
    conjugate, _ = kernel_differential(conjugate_bordered, [*z, *w_on], [*along_z, *along_w], 14)
    return {
        "stratum": stratum,
        "point_sha256": hashlib.sha256(json.dumps([z, w_on, free_w]).encode()).hexdigest(),
        "rank_lower_block": _rank(block),
        "z_in_lower_kernel": _rank([*block_kernel, twisted]) == len(block_kernel),
        "kernels": kernel_checks,
        "tangent_dimension": len(tangent_z),
        "three_plane_map_rank": _rank(three_planes),
        "gauss_rank_w_free": _rank(free),
        "gauss_rank_w_on_conjugate_stratum": _rank(on_stratum),
        "conjugate_pair_rank": _rank([a + b for a, b in zip(on_stratum, conjugate, strict=True)]),
    }


def fixture_rank(job: tuple[int, str, list[int]]) -> dict[str, Any]:
    """The differentials on the real locus w' = z' at one exact fixture, reduced modulo PRIME."""
    number, stratum, split = job
    polynomials = _polynomials()
    zero = [0] * IMAGINARY
    z = [value % PRIME for value in split]
    membership = tuple(_value(polynomials[name], z) == 0 for name in ("Q", "G"))
    _require(membership == MEMBERSHIP[stratum], f"fixture {number} lies off its stratum modulo {PRIME}")
    tangent = tangent_space(stratum, z, polynomials)
    directions = [*([*v, *zero] for v in tangent), *([*zero, *v] for v in tangent)]
    three_planes, _ = kernel_differential(lower_block, z, tangent, 12)
    gauss, _ = kernel_differential(bordered, [*z, *z], directions, 14)
    conjugate, _ = kernel_differential(conjugate_bordered, [*z, *z], directions, 14)
    return {
        "fixture": number,
        "stratum": stratum,
        "tangent_dimension": len(tangent),
        "three_plane_map_rank": _rank(three_planes),
        "gauss_rank": _rank(gauss),
        "real_rank": _rank([a + b for a, b in zip(gauss, conjugate, strict=True)]),
    }


def _fixture_splits() -> list[tuple[int, str, list[int]]]:
    rows = json.loads(FIXTURES.read_text(encoding="utf-8"))["fixtures"]
    return [(number, row["stratum"], [int(value) for value in row["split_point"]]) for number, row in enumerate(rows)]


def fixture_ranks() -> list[dict[str, Any]]:
    return parallel.ordered_map(fixture_rank, _fixture_splits(), min_items=2)


def plucker(job: tuple[str, int]) -> Vector:
    """The 105 Plucker coordinates in Gr(2, 15) of ker A(z, w) at one point of the stratum with w free."""
    stratum, number = job
    points = Points(f"image:{stratum}:{number}")
    z = sample(stratum, points, _polynomials())
    kernel = _nullspace(bordered([*z, *points.vector()]))
    _require(len(kernel) == 2 and kernel[0][0] == 0 == kernel[1][0], "the kernel is not a plane in the last 15")
    return [(kernel[0][a] * kernel[1][b] - kernel[0][b] * kernel[1][a]) % PRIME for a, b in PLUCKER_PAIRS]


def fixture_orbit_rank(job: tuple[list[int], tuple[Any, ...]]) -> int:
    """The exact rank of the orbit of the kernel symmetry algebra, given by its base matrices, at one split point."""
    split, generators = job
    point = tuple(symmetry.equations.y_from_split([Fraction(value) for value in split]))
    return int(symmetry._rank([symmetry._rational_matrix_vector_product(matrix, point) for matrix in generators]))


def fixture_orbit_ranks() -> list[int]:
    triples, _, _ = symmetry._solve_lie_triples("")
    generators = tuple(triple[0] for triple in triples)
    return parallel.ordered_map(
        fixture_orbit_rank, [(split, generators) for _, _, split in _fixture_splits()], min_items=2
    )


def fixture_plane_classes() -> list[int]:
    """For each exact fixture, the first fixture with the same kernel plane; the points are projectively distinct."""
    rows = json.loads(FIXTURES.read_text(encoding="utf-8"))["fixtures"]
    points = [[Fraction(value) for value in row["split_point"]] for row in rows]
    for first, second in itertools.combinations(points, 2):
        minors = (first[a] * second[b] - first[b] * second[a] for a, b in itertools.combinations(range(IMAGINARY), 2))
        _require(any(minors), "two exact fixtures are one projective point")
    planes = [tuple(row["normalized_plucker_coordinates"]) for row in rows]
    return [planes.index(plane) for plane in planes]


def _split_basis() -> Matrix:
    return [[int(row == column) for column in range(2 * IMAGINARY)] for row in range(2 * IMAGINARY)]


def fiber_dimension(split: Sequence[int], conjugate_split: Sequence[int] | None = None) -> int:
    """dim L modulo PRIME at the pair (z', w'), w' = z' by default: the pairs whose matrices kill both planes."""
    point = [*split, *(split if conjugate_split is None else conjugate_split)]
    kernels = (_nullspace(bordered(point)), _nullspace(conjugate_bordered(point)))
    columns = []
    for unit in _split_basis():
        column: Vector = []
        for matrix, kernel in zip((bordered(unit), conjugate_bordered(unit)), kernels, strict=True):
            for vector in kernel:
                column += [sum(a * b for a, b in zip(row, vector, strict=True)) % PRIME for row in matrix]
        columns.append(column)
    return 2 * IMAGINARY - _rank([list(row) for row in zip(*columns, strict=True)])


def _exact_bordered(point: Sequence[int], conjugate: bool = False) -> list[list[Any]]:
    """`bordered` over the Gaussian rationals."""
    first, second = (point[IMAGINARY:], point[:IMAGINARY]) if conjugate else (point[:IMAGINARY], point[IMAGINARY:])
    unit = QQ_I.convert(-I if conjugate else I)
    z = [unit ** (index + 1).bit_count() * QQ_I.convert(value) for index, value in enumerate(first)]
    w = [(-unit) ** (index + 1).bit_count() * QQ_I.convert(value) for index, value in enumerate(second)]
    matrix = [[QQ_I.zero] * BORDERED for _ in range(BORDERED)]
    for index in range(1, BORDERED):
        matrix[0][index], matrix[index][0] = -w[index - 1], w[index - 1]
    for row in range(1, BORDERED):
        for column in range(1, BORDERED):
            if row != column:
                matrix[row][column] = SIGNS[row][column] * z[(row ^ column) - 1]
    return matrix


def exact_fiber_dimension(split: Sequence[int]) -> int:
    """dim L over Q(i) at the pair (z', z') of an integer split point."""
    point = [*split, *split]
    shape = (BORDERED, BORDERED)
    kernels = [
        DomainMatrix(_exact_bordered(point, conjugate), shape, QQ_I).nullspace().to_list()
        for conjugate in (False, True)
    ]
    _require([len(kernel) for kernel in kernels] == [2, 2], "an exact kernel is not a plane")
    columns = []
    for unit in _split_basis():
        column: list[Any] = []
        for conjugate, kernel in zip((False, True), kernels, strict=True):
            matrix = _exact_bordered(unit, conjugate)
            for vector in kernel:
                column += [sum((a * b for a, b in zip(row, vector, strict=True)), QQ_I.zero) for row in matrix]
        columns.append(column)
    system = DomainMatrix([list(row) for row in zip(*columns, strict=True)], (len(columns[0]), len(columns)), QQ_I)
    return 2 * IMAGINARY - int(system.rank())


def _block(vector: Sequence[int]) -> Matrix:
    """M(t) for a vector t of the frame in which `bordered` writes its lower block and its kernel vectors."""
    return [
        [0 if row == column else SIGNS[row][column] * vector[(row ^ column) - 1] % PRIME for column in range(1, 16)]
        for row in range(1, BORDERED)
    ]


def sign_identity() -> bool:
    """SIGNS[r][r ^ c] = -SIGNS[r][c] for r != c, the identity behind M(z) p = -M(p) z."""
    units = range(1, BORDERED)
    return all(SIGNS[row][row ^ column] == -SIGNS[row][column] for row in units for column in units if row != column)


def three_plane_net(frame: Vector, plane: Matrix) -> list[list[int]]:
    """The nullities of M(k) on the net of ker M(z): [nullity, vectors, projective points, span, span with P]."""
    three_plane = _nullspace(_block(frame))
    net: dict[int, list[int]] = {}
    members: dict[int, Matrix] = {}
    for coefficients in itertools.product(range(-3, 4), repeat=len(three_plane)):
        if any(coefficients):
            vector = [
                sum(c * v[index] for c, v in zip(coefficients, three_plane, strict=True)) % PRIME
                for index in range(IMAGINARY)
            ]
            nullity = IMAGINARY - _rank(_block(vector))
            members.setdefault(nullity, []).append(vector)
            counts = net.setdefault(nullity, [0, 0])
            counts[0] += 1
            counts[1] += math.gcd(*coefficients) == 1 and next(c for c in coefficients if c) > 0
    return [
        [nullity, *counts, _rank(members[nullity]), _rank([*members[nullity], *plane])]
        for nullity, counts in sorted(net.items())
    ]


def kernel_form(job: tuple[list[int], list[int]], net: bool = True) -> dict[str, Any]:
    """The fiber through the pair (z', w') modulo PRIME, read from the kernel plane P = ker A(z, w).

    M(z) p = -M(p) z, so the z-part of L is {z in ker M(p1) n ker M(p2): z orthogonal to the conjugate plane P'}
    for a basis p1, p2 of P. The row holds dim L, the nullity of M(p) at the probe vector p1 + PROBE p2, the dimension
    of ker M(p1) n ker M(p2), its dimension after the cut by P' (dim L_z, which is half of dim L at a real point,
    where w' is the conjugate of z'), whether M(z) p = -M(p) z at p1 and p2, and the nullities of M(k) at the 342
    nonzero combinations k, coefficients -3..3, of the echelon basis of ker M(z), as [nullity, vectors, projective
    points, dimension of the span of those vectors, dimension of that span with P added]: a projective point is
    counted at its coprime combination with a positive first nonzero coefficient, and the vectors of one nullity
    lie on one line of the projective plane exactly when their span has dimension 2. The grid and the Gaussian
    points read the other fields only and pass net false, which leaves the net out of the row.
    """
    split, conjugate_split = job
    point = [*split, *conjugate_split]
    frame = _twist(split, ROOT_OF_MINUS_ONE)
    plane = [vector[1:] for vector in _nullspace(bordered(point))]
    conjugate_plane = [vector[1:] for vector in _nullspace(conjugate_bordered(point))]
    _require(len(plane) == 2 and len(conjugate_plane) == 2, "a kernel modulo the prime is not a plane")
    general = [(a + PROBE * b) % PRIME for a, b in zip(*plane, strict=True)]
    common = [*_block(plane[0]), *_block(plane[1])]
    product = [[sum(a * b for a, b in zip(row, p, strict=True)) % PRIME for row in _block(frame)] for p in plane]
    swapped = [[-sum(a * b for a, b in zip(row, frame, strict=True)) % PRIME for row in _block(p)] for p in plane]
    form: dict[str, Any] = {
        "fiber_dimension": fiber_dimension(split, conjugate_split),
        "plane_nullity": IMAGINARY - _rank(_block(general)),
        "common_kernel": IMAGINARY - _rank(common),
        "common_kernel_cut": IMAGINARY - _rank([*common, *conjugate_plane]),
        "antisymmetric": product == swapped,
    }
    if net:
        form["three_plane_net"] = three_plane_net(frame, plane)
    return form


def fixture_kernel_forms() -> list[dict[str, Any]]:
    jobs = [([value % PRIME for value in split],) * 2 for _, _, split in _fixture_splits()]
    return parallel.ordered_map(kernel_form, jobs, min_items=2)


def _small(label: str, count: int, span: int) -> Vector:
    """`count` integers of -span..span from sha256 of the label and a counter."""
    return [hashlib.sha256(f"{label}:{n}".encode()).digest()[0] % (2 * span + 1) - span for n in range(count)]


def gaussian_block(job: tuple[int, list[int]]) -> list[list[int]]:
    """Real points of V(Q) with Gaussian-integer split coordinates near one fixture of V(Q) minus V(G).

    The line from the fixture in the direction a + i b meets the quadric V(Q) in a second point z' with
    coordinates in Z[i]; w' is its conjugate and the pair is reduced by i -> ROOT_OF_MINUS_ONE. A pair is kept when
    z' and w' are independent modulo PRIME, hence over Q(i), so [z'] is a non-real point. Odd samples keep
    about a third of the coordinates of a and of b. Each row is [Q and G vanish (0 or 1 each), dim L, plane
    nullity, common kernel, cut common kernel] at a pair of nullity 4; the first row counts the other pairs by
    reason: a real direction, a line inside V(Q) modulo PRIME (z' = 0), a direction tangent to V(Q) at the fixture
    (the second point is the fixture, so z' and w' are proportional), another nullity.
    """
    number, base = job
    polynomials = _polynomials()
    quadric = polynomials["Q"]
    rows: list[list[int]] = []
    rejected = [0, 0, 0, 0]
    for sample_number in range(GAUSSIAN_PER_FIXTURE):
        label = f"gaussian:{number}:{sample_number}"
        real, imaginary = _small(f"{label}:re", IMAGINARY, 3), _small(f"{label}:im", IMAGINARY, 3)
        if sample_number % 2:
            keep = _small(f"{label}:keep", IMAGINARY, 1)
            real = [value if kept == 1 else 0 for value, kept in zip(real, keep, strict=True)]
            imaginary = [value if kept == -1 else 0 for value, kept in zip(imaginary, keep, strict=True)]
        pair = []
        for sign in (1, -1):
            direction = [(a + sign * ROOT_OF_MINUS_ONE * b) % PRIME for a, b in zip(real, imaginary, strict=True)]
            norm = _value(quadric, direction)
            polar = (_value(quadric, [(a + b) % PRIME for a, b in zip(base, direction, strict=True)]) - norm) % PRIME
            pair.append([(norm * a - polar * b) % PRIME for a, b in zip(base, direction, strict=True)])
        z, w = pair
        reasons = (not any(imaginary), not any(z), _rank([z, w]) != 2)
        if any(reasons):
            rejected[reasons.index(True)] += 1
            continue
        _require(_value(quadric, z) == 0 and _value(quadric, w) == 0, "a projected point lies off V(Q)")
        if _rank(lower_block(z)) != 12 or _rank(bordered([*z, *w])) != 14:
            rejected[3] += 1
            continue
        form = kernel_form((z, w), net=False)
        _require(form["antisymmetric"], "M(z) p = -M(p) z fails at a Gaussian point")
        rows.append(
            [
                int(_value(quadric, z) == 0),
                int(_value(polynomials["G"], z) == 0),
                form["fiber_dimension"],
                form["plane_nullity"],
                form["common_kernel"],
                form["common_kernel_cut"],
            ]
        )
    return [rejected, *rows]


def gaussian_points() -> dict[str, Any]:
    """Classes of the Gaussian real points of V(Q) projected from the fixtures of V(Q) minus V(G)."""
    jobs = [
        (number, [value % PRIME for value in split])
        for number, stratum, split in _fixture_splits()
        if stratum == STRATA[0]
    ]
    blocks = parallel.ordered_map(gaussian_block, jobs, min_items=2)
    classes: dict[tuple[int, ...], int] = {}
    for block in blocks:
        for row in block[1:]:
            classes[tuple(row)] = classes.get(tuple(row), 0) + 1
    return {
        "fixtures": len(jobs),
        "samples_per_fixture": GAUSSIAN_PER_FIXTURE,
        "rejected": [sum(counts) for counts in zip(*(block[0] for block in blocks), strict=True)],
        "classes": [[*found, count] for found, count in sorted(classes.items())],
    }


def plane_block(job: tuple[str, int]) -> list[int]:
    """dim {z: P in ker M(z)} at PLANES_PER_POINT planes P of ker M(z0) off z0, z0 a sampled point of the stratum."""
    stratum, number = job
    points = Points(f"planes:{stratum}:{number}")
    frame = _twist(sample(stratum, points, _polynomials()), ROOT_OF_MINUS_ONE)
    three_plane = _nullspace(_block(frame))
    _require(len(three_plane) == 3, "ker M(z) is not a three-plane at a sampled point")
    found: list[int] = []
    while len(found) < PLANES_PER_POINT:
        plane = []
        for _ in range(2):
            coefficients = [points.value() for _ in range(3)]
            plane.append(
                [
                    sum(c * v[index] for c, v in zip(coefficients, three_plane, strict=True)) % PRIME
                    for index in range(IMAGINARY)
                ]
            )
        if _rank([*plane, frame]) == 3:
            found.append(IMAGINARY - _rank([*_block(plane[0]), *_block(plane[1])]))
    return found


def general_planes() -> list[dict[str, Any]]:
    """Per stratum, the common kernels of general planes of ker M(z0) at sampled points z0."""
    jobs = [(stratum, number) for stratum in STRATA for number in range(PLANE_POINTS)]
    blocks = parallel.ordered_map(plane_block, jobs, min_items=2)
    rows = []
    for index, stratum in enumerate(STRATA):
        values = [value for block in blocks[index * PLANE_POINTS : (index + 1) * PLANE_POINTS] for value in block]
        rows.append({"stratum": stratum, "planes": len(values), "common_kernels": sorted(set(values))})
    return rows


def exact_plane_nullities(split: list[int]) -> list[int]:
    """The nullity over Q(i) of M(p) at seven vectors p of the kernel plane at the pair (z', z').

    Six are p1 + t p2, t = 0..4, and p2 on a basis of the exact kernel. The matrices of rank at most 8 among the
    skew M(p) are cut out by the Pfaffians of the principal 10 x 10 blocks, forms of degree 5 on the plane, so
    nullity above 5 at six pairwise independent vectors holds on the whole plane. The seventh is the probe vector
    of `kernel_form`: the exact basis is normalized to the identity at the two pivot coordinates of the echelon
    basis modulo PRIME, which makes it the lift of that basis.
    """
    point = [*split, *split]
    plane = DomainMatrix(_exact_bordered(point), (BORDERED, BORDERED), QQ_I).nullspace().to_list()
    _require(len(plane) == 2 and not any(vector[0] for vector in plane), "the exact kernel is not a plane of the block")
    first, second = (vector[1:] for vector in plane)
    vectors = [*([a + t * b for a, b in zip(first, second, strict=True)] for t in range(5)), second]
    reduced = [value % PRIME for value in split]
    echelon = [vector[1:] for vector in _nullspace(bordered([*reduced, *reduced]))]
    pivots = [
        next(index for index in range(IMAGINARY) if [vector[index] for vector in echelon] == unit)
        for unit in ([1, 0], [0, 1])
    ]
    determinant = first[pivots[0]] * second[pivots[1]] - first[pivots[1]] * second[pivots[0]]
    _require(determinant != 0, "the exact kernel plane has no basis on the pivots of the modular one")
    lifted = [
        [(second[pivots[1]] * a - first[pivots[1]] * b) / determinant for a, b in zip(first, second, strict=True)],
        [(first[pivots[0]] * b - second[pivots[0]] * a) / determinant for a, b in zip(first, second, strict=True)],
    ]
    vectors.append([a + PROBE * b for a, b in zip(*lifted, strict=True)])
    found = []
    for vector in vectors:
        rows = [
            [QQ_I.zero if row == column else SIGNS[row][column] * vector[(row ^ column) - 1] for column in range(1, 16)]
            for row in range(1, BORDERED)
        ]
        found.append(IMAGINARY - int(DomainMatrix(rows, (IMAGINARY, IMAGINARY), QQ_I).rank()))
    return found


def _real_point(split: Sequence[int]) -> list[Fraction]:
    return list(symmetry.equations.y_from_split([Fraction(int(value)) for value in split]))


def kernel_vector_nullity(split: Sequence[int]) -> int:
    """The least nullity, exact, among six vectors of the kernel of left multiplication by the real point."""
    kernel = symmetry.equations.nullspace(symmetry.equations.l_matrix(_real_point(split)))
    _require(len(kernel) == 4, "the real kernel is not four-dimensional")
    vectors = [
        [
            sum((c * vector[index] for c, vector in zip(combination, kernel, strict=True)), Fraction(0))
            for index in range(32)
        ]
        for combination in KERNEL_COMBINATIONS
    ]
    return min(int(symmetry.equations.nullity(vector)) for vector in vectors)


def _left_multiplication(vector: Sequence[int]) -> Matrix:
    rows = symmetry.equations.l_matrix([Fraction(int(value)) for value in vector])
    return [[int(value) % PRIME for value in row] for row in rows]


def grid_block(job: tuple[int, int, int, tuple[tuple[tuple[int, ...], ...], ...]]) -> list[list[Any]]:
    """Nullity-4 points of one block of the grid: [split point, stratum, orbit rank, dim L, kernel nullity]."""
    second, third, eighth, generators = job
    polynomials = _polynomials()
    rows: list[list[Any]] = []
    candidates = 0
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
                real = [int(value) % PRIME for value in _real_point(split)]
                orbit = _rank(
                    [[sum(a * b for a, b in zip(row, real, strict=True)) % PRIME for row in g] for g in generators]
                )
                kernel = _nullspace(_left_multiplication(real))
                _require(len(kernel) == 4, "the real kernel modulo the prime is not four-dimensional")
                general = [
                    sum(c * v[i] for c, v in zip(KERNEL_COMBINATIONS[4], kernel, strict=True)) % PRIME
                    for i in range(32)
                ]
                nullity = 32 - _rank(_left_multiplication(general))
                form = kernel_form((reduced, reduced), net=False)
                _require(form["antisymmetric"], "M(z) p = -M(p) z fails at a grid point")
                plane = [form["plane_nullity"], form["common_kernel"], form["common_kernel_cut"]]
                rows.append([split, stratum, orbit, fiber_dimension(reduced), nullity, plane])
    return [[candidates], *rows]


def grid() -> dict[str, Any]:
    """The classes of the nullity-4 grid points and the exact fiber dimension at the exceptional ones."""
    triples, _, _ = symmetry._solve_lie_triples("")
    generators = tuple(
        tuple(
            tuple(Fraction(value).numerator * pow(Fraction(value).denominator, -1, PRIME) % PRIME for value in row)
            for row in triple[0]
        )
        for triple in triples
    )
    jobs = [(second, third, eighth, generators) for second in range(3) for third in range(3) for eighth in range(4)]
    blocks = parallel.ordered_map(grid_block, jobs, min_items=2)
    classes: dict[tuple[str, int, int, int], int] = {}
    planes: dict[tuple[str, int, int, int, int], int] = {}
    exceptions = []
    plane_exceptions: list[dict[str, Any]] = []
    for block in blocks:
        for split, stratum, orbit, fiber, nullity, plane in block[1:]:
            found = (stratum, orbit, fiber, nullity)
            classes[found] = classes.get(found, 0) + 1
            planes[(stratum, fiber, *plane)] = planes.get((stratum, fiber, *plane), 0) + 1
            if (stratum, fiber, *plane) in KERNEL_FORM_EXCEPTIONS:
                plane_exceptions.append({"split_point": split, "common_kernel": plane[1]})
            if found in GRID_EXCEPTIONS:
                exceptions.append(
                    {"split_point": split, "stratum": stratum, "orbit_rank": orbit, "fiber_dimension": fiber}
                )
    exact = parallel.ordered_map(exact_invariants, [row["split_point"] for row in exceptions], min_items=2)
    for row, invariant in zip(exceptions, exact, strict=True):
        row["kernel_vector_nullity"] = invariant["kernel_vector_nullity"]
        row["exact_fiber_dimension"] = invariant["fiber_dimension"]
    nullities = parallel.ordered_map(
        exact_plane_nullities, [row["split_point"] for row in plane_exceptions], min_items=2
    )
    for row, found_nullities in zip(plane_exceptions, nullities, strict=True):
        row["exact_plane_nullities"] = found_nullities
    return {
        "candidates": sum(block[0][0] for block in blocks),
        "classes": [[*found, count] for found, count in sorted(classes.items())],
        "kernel_form_classes": [[*found, count] for found, count in sorted(planes.items())],
        "exceptions": exceptions,
        "kernel_form_exceptions": plane_exceptions,
    }


def exact_invariants(split: list[int]) -> dict[str, int]:
    """Exact dim L and least sampled kernel-vector nullity at one integer split point."""
    return {"fiber_dimension": exact_fiber_dimension(split), "kernel_vector_nullity": kernel_vector_nullity(split)}


def fixture_invariants() -> list[dict[str, int]]:
    return parallel.ordered_map(exact_invariants, [split for _, _, split in _fixture_splits()], min_items=2)


def image_equations(job: tuple[str, list[Vector]]) -> dict[str, Any]:
    """Linear span of the sampled planes and the count of quadrics vanishing on them, at two sample sizes.

    The values of the quadratic monomials fill two flint matrices of machine words, one per sample size: 0.5 GiB
    for one stratum, so the three strata run at once inside the 8 GiB scope of the gate.
    """
    stratum, rows = job
    matrices = [nmod_mat(count, len(QUADRIC_MONOMIALS), PRIME) for count in QUADRIC_SAMPLES]
    for number, row in enumerate(rows):
        for column, (a, b) in enumerate(QUADRIC_MONOMIALS):
            value = row[a] * row[b] % PRIME
            for count, matrix in zip(QUADRIC_SAMPLES, matrices, strict=True):
                if number < count:
                    matrix[number, column] = value
    ranks = [int(matrix.rank()) for matrix in matrices]
    return {
        "stratum": stratum,
        "linear_samples": LINEAR_SAMPLES,
        "linear_span_dimension": _rank(rows[:LINEAR_SAMPLES]),
        "plucker_coordinates": len(PLUCKER_PAIRS),
        "quadric_samples": list(QUADRIC_SAMPLES),
        "quadric_ranks": ranks,
        "quadric_monomials": len(QUADRIC_MONOMIALS),
        "quadrics_vanishing": len(QUADRIC_MONOMIALS) - ranks[-1],
        "plucker_quadrics": PLUCKER_QUADRICS,
    }


def images() -> list[dict[str, Any]]:
    """`image_equations` on the three strata: the planes are sampled in the pool, then the three rank stages are."""
    samples = [(stratum, number) for stratum in STRATA for number in range(QUADRIC_SAMPLES[-1])]
    planes = parallel.ordered_map(plucker, samples, min_items=2)
    size = QUADRIC_SAMPLES[-1]
    jobs = [(stratum, planes[index * size : (index + 1) * size]) for index, stratum in enumerate(STRATA)]
    return parallel.ordered_map(image_equations, jobs, min_items=2)


def shared_plane_spans() -> list[int]:
    """For each exact fixture that shares its kernel plane with an earlier one: dim (ker M(z) + ker M(z'))."""
    splits = [[value % PRIME for value in split] for _, _, split in _fixture_splits()]
    spans = []
    for number, first in enumerate(fixture_plane_classes()):
        if first != number:
            spans.append(_rank([*_nullspace(lower_block(splits[first])), *_nullspace(lower_block(splits[number]))]))
    return spans


def control() -> dict[str, Any]:
    """A point off both hypersurfaces: M(z) has kernel z alone and A(z, w) is invertible."""
    polynomials = _polynomials()
    points = Points("control")
    while True:
        z = points.vector()
        if _value(polynomials["Q"], z) and _value(polynomials["G"], z):
            break
    block = lower_block(z)
    kernel = _nullspace(block)
    return {
        "rank_lower_block": _rank(block),
        "lower_kernel_is_z": len(kernel) == 1 and _rank([kernel[0], _twist(z, ROOT_OF_MINUS_ONE)]) == 1,
        "rank_bordered": _rank(bordered([*z, *points.vector()])),
    }


def fixtures() -> dict[str, int]:
    """In the retained exact record, the fixtures whose 15 coordinates p_(0 j) all vanish."""
    rows = json.loads(FIXTURES.read_text(encoding="utf-8"))["fixtures"]
    order = list(itertools.combinations(range(BORDERED), 2))
    first = [position for position, pair in enumerate(order) if pair[0] == 0]
    vanishing = sum(all(row["normalized_plucker_coordinates"][position] == "0" for position in first) for row in rows)
    return {"fixtures": len(rows), "first_coordinate_zero": vanishing}


def _inputs() -> dict[str, str]:
    return {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in SOURCE_PATHS}


def compute() -> dict[str, Any]:
    jobs = [(stratum, number) for stratum in STRATA for number in range(RANK_POINTS)]
    record: dict[str, Any] = {
        "schema": SCHEMA,
        "field": FIELD,
        "inputs": _inputs(),
        "points": parallel.ordered_map(rank_point, jobs, min_items=2),
        "image": images(),
        "control": control(),
        "exact_fixtures": fixtures(),
        "exact_fixture_ranks": fixture_ranks(),
        "exact_fixture_orbit_ranks": fixture_orbit_ranks(),
        "exact_fixture_plane_classes": fixture_plane_classes(),
        "shared_plane_three_plane_spans": shared_plane_spans(),
        "exact_fixture_invariants": fixture_invariants(),
        "grid": grid(),
        "sign_identity": sign_identity(),
        "exact_fixture_kernel_forms": fixture_kernel_forms(),
        "gaussian_points": gaussian_points(),
        "general_planes": general_planes(),
    }
    record["pass"] = verdict(record) == []
    return record


def verdict(record: dict[str, Any]) -> list[str]:
    """The reasons the record fails its own rules; empty when it passes."""
    problems = []
    if (record.get("schema"), record.get("field")) != (SCHEMA, FIELD):
        problems.append("the record is headed otherwise")
    if record.get("inputs") != _inputs():
        problems.append("the input digests differ from the files")
    if record.get("pass", True) is not True:
        problems.append("the record states that it fails")
    points = record["points"]
    if [row["stratum"] for row in points] != [stratum for stratum in STRATA for _ in range(RANK_POINTS)]:
        problems.append("the points differ from the sampled strata")
    digests = {row["point_sha256"] for row in points}
    if len(digests) != len(points):
        problems.append("two rank points coincide")
    if any(re.fullmatch("[0-9a-f]{64}", digest) is None for digest in digests):
        problems.append("a point digest is not a sha256 digest")
    for number, row in enumerate(points):
        name = f"{row['stratum']} point {number % RANK_POINTS}"
        expected = EXPECTED.get(row["stratum"], {})
        if row["rank_lower_block"] != 12 or row["z_in_lower_kernel"] is not True:
            problems.append(f"{name}: ker M(z) is not a three-plane through z")
        if len(row["kernels"]) != FREE_W_PER_POINT + 1:
            problems.append(f"{name}: {len(row['kernels'])} kernels")
        for kernel in row["kernels"]:
            if kernel != {
                "rank_bordered": 14,
                "first_coordinate_zero": True,
                "inside_lower_kernel": True,
                "orthogonal_to_w": True,
            }:
                problems.append(f"{name}: ker A(z, w) is not ker M(z) n w-perp")
        for key in ("tangent_dimension", "three_plane_map_rank", "gauss_rank_w_free", "conjugate_pair_rank"):
            if row[key] != expected.get(key):
                problems.append(f"{name}: {key} is {row[key]}, expected {expected.get(key)}")
        if row["gauss_rank_w_on_conjugate_stratum"] != row["gauss_rank_w_free"]:
            problems.append(f"{name}: the Gauss rank drops when w lies on the conjugate stratum")
    if [row["stratum"] for row in record["image"]] != list(STRATA):
        problems.append("the image rows differ from the three strata")
    for row in record["image"]:
        name, expected = row["stratum"], EXPECTED.get(row["stratum"], {})
        if row["quadric_samples"] != list(QUADRIC_SAMPLES) or row["quadric_samples"][0] <= row["quadric_monomials"]:
            problems.append(f"{name}: the quadric interpolation has too few samples")
        if row["linear_samples"] != LINEAR_SAMPLES:
            problems.append(f"{name}: the linear span is read at {row['linear_samples']} samples")
        if len(set(row["quadric_ranks"])) != 1:
            problems.append(f"{name}: the quadric rank still grows between the two sample sizes")
        if row["quadrics_vanishing"] != row["quadric_monomials"] - row["quadric_ranks"][-1]:
            problems.append(f"{name}: the count of vanishing quadrics is not monomials minus rank")
        for key in ("linear_span_dimension", "quadrics_vanishing"):
            if row[key] != expected.get(key):
                problems.append(f"{name}: {key} is {row[key]}, expected {expected.get(key)}")
        if (row["plucker_coordinates"], row["quadric_monomials"], row["plucker_quadrics"]) != (
            len(PLUCKER_PAIRS),
            len(QUADRIC_MONOMIALS),
            PLUCKER_QUADRICS,
        ):
            problems.append(f"{name}: the coordinate counts differ from Gr(2, 15)")
    if record["control"] != {"rank_lower_block": 14, "lower_kernel_is_z": True, "rank_bordered": 16}:
        problems.append("the control point off the strata does not have ker M(z) = z and A invertible")
    exact = record["exact_fixtures"]
    if exact["fixtures"] != 66 or exact["first_coordinate_zero"] != exact["fixtures"]:
        problems.append("an exact fixture has a kernel vector with nonzero first coordinate")
    ranks = record["exact_fixture_ranks"]
    if [row["fixture"] for row in ranks] != list(range(exact["fixtures"])):
        problems.append("the fixture ranks do not cover the exact fixtures in order")
    orbits, classes = record["exact_fixture_orbit_ranks"], record["exact_fixture_plane_classes"]
    if len(orbits) != len(ranks) or len(classes) != len(ranks):
        problems.append("the orbit ranks or the plane classes do not cover the exact fixtures")
        return problems
    found: dict[tuple[str, int, int, int, int], int] = {}
    for row, orbit in zip(ranks, orbits, strict=True):
        rank_class = (row["stratum"], orbit, row["three_plane_map_rank"], row["gauss_rank"], row["real_rank"])
        found[rank_class] = found.get(rank_class, 0) + 1
        if row["tangent_dimension"] != EXPECTED.get(row["stratum"], {}).get("tangent_dimension"):
            problems.append(f"fixture {row['fixture']}: the tangent space drops modulo {PRIME}")
    if found != FIXTURE_RANKS:
        problems.append("the ranks on the real locus at the exact fixtures differ from the expected table")
    for stratum in STRATA:
        bound = EXPECTED[stratum]["conjugate_pair_rank"]
        if not any(row["stratum"] == stratum and row["real_rank"] == bound for row in ranks):
            problems.append(f"{stratum}: no exact fixture has real rank {bound}")
    invariants = record["exact_fixture_invariants"]
    if len(invariants) != len(ranks):
        problems.append("the fiber dimensions do not cover the exact fixtures")
        return problems
    for row, invariant in zip(ranks, invariants, strict=True):
        fiber = invariant["fiber_dimension"]
        if FIBER_DIMENSIONS.get(row["real_rank"]) != fiber or row["real_rank"] != 2 * row["tangent_dimension"] - fiber:
            problems.append(f"fixture {row['fixture']}: the real rank is not the tangent dimension minus dim L")
        if invariant["kernel_vector_nullity"] != {2: 4, 6: 12, 12: 16}.get(fiber):
            problems.append(f"fixture {row['fixture']}: the kernel vectors have another nullity")
    lattice = record["grid"]
    if lattice["candidates"] != GRID_CANDIDATES:
        problems.append("the grid has another number of candidates")
    if {tuple(row[:4]): row[4] for row in lattice["classes"]} != GRID_CLASSES or len(lattice["classes"]) != len(
        GRID_CLASSES
    ):
        problems.append("the classes of the nullity-4 grid points differ from the expected table")
    expected_exceptions = [found for found in sorted(GRID_EXCEPTIONS) for _ in range(GRID_CLASSES[found])]
    found_exceptions = sorted(
        (row["stratum"], row["orbit_rank"], row["exact_fiber_dimension"], row["kernel_vector_nullity"])
        for row in lattice["exceptions"]
    )
    if found_exceptions != expected_exceptions:
        problems.append("an exceptional grid point has another exact fiber dimension or kernel nullity")
    if any(row["fiber_dimension"] != row["exact_fiber_dimension"] for row in lattice["exceptions"]):
        problems.append("an exceptional grid point has a fiber that changes modulo the prime")
    problems += _kernel_form_problems(record)
    shared = [number for number, first in enumerate(classes) if classes.count(first) > 1]
    if (len(set(classes)), len(shared)) != (FIXTURE_PLANES, FIXTURES_ON_SHARED_PLANES):
        problems.append("the count of kernel planes shared by two exact fixtures differs")
    if record["shared_plane_three_plane_spans"] != [4] * (FIXTURES_ON_SHARED_PLANES - len(SHARED_PLANE_SIZES)):
        problems.append("two fixtures with one kernel plane do not have two different three-planes ker M(z)")
    sizes = sorted(classes.count(first) for first in set(classes) if classes.count(first) > 1)
    by_rank = sorted(ranks[number]["real_rank"] for number in shared)
    if sizes != SHARED_PLANE_SIZES or by_rank != SHARED_PLANE_REAL_RANKS:
        problems.append("the kernel planes are shared in other class sizes or at other real ranks")
    if any(first > number or classes[first] != first for number, first in enumerate(classes)):
        problems.append("a plane class does not name its first fixture")
    for number in shared:
        row = ranks[number]
        full = EXPECTED.get(row["stratum"], {}).get("conjugate_pair_rank")
        if (row["stratum"], orbits[number]) != (STRATA[1], 13) or row["real_rank"] == full:
            problems.append(f"fixture {number} shares its kernel plane off the orbit-rank-13 locus of V(G) minus V(Q)")
    return problems


def _kernel_form_problems(record: dict[str, Any]) -> list[str]:
    """The rules on the kernel form of the fiber: fixtures, grid, Gaussian points and general planes."""
    problems = []
    if record.get("sign_identity") is not True:
        problems.append("the sign identity behind M(z) p = -M(p) z is not recorded as true")
    ranks, forms = record["exact_fixture_ranks"], record.get("exact_fixture_kernel_forms", [])
    if len(forms) != len(ranks):
        return [*problems, "the kernel forms do not cover the exact fixtures"]
    found: dict[tuple[Any, ...], list[int]] = {}
    for row, invariant, form in zip(ranks, record["exact_fixture_invariants"], forms, strict=True):
        name = f"fixture {row['fixture']}"
        if form["antisymmetric"] is not True:
            problems.append(f"{name}: M(z) p = -M(p) z fails on the kernel plane")
        if form["fiber_dimension"] != invariant["fiber_dimension"]:
            problems.append(f"{name}: dim L modulo {PRIME} differs from the exact dim L")
        if form["fiber_dimension"] != 2 * form["common_kernel_cut"]:
            problems.append(f"{name}: dim L is not twice the cut common kernel")
        net = tuple(tuple(pair) for pair in form["three_plane_net"])
        totals = [sum(column) for column in zip(*net, strict=True)][1:3]
        if any(len(entry) != 5 for entry in net) or totals != [342, 145]:
            problems.append(f"{name}: the net of ker M(z) does not have 342 vectors on 145 projective points")
        key = (row["stratum"], form["fiber_dimension"], form["plane_nullity"], form["common_kernel"])
        found.setdefault((*key, form["common_kernel_cut"], net), []).append(row["fixture"])
    if {key: tuple(members) for key, members in found.items()} != KERNEL_FORM_FIXTURES:
        problems.append("the kernel forms at the exact fixtures differ from the expected table")
    lattice = record["grid"].get("kernel_form_classes", [])
    grid_classes = {tuple(row[:5]): row[5] for row in lattice}
    if grid_classes != KERNEL_FORM_GRID or len(lattice) != len(KERNEL_FORM_GRID):
        problems.append("the kernel forms of the nullity-4 grid points differ from the expected table")
    if any(row[1] != 2 * row[4] for row in lattice):
        problems.append("a grid class has dim L other than twice the cut common kernel")
    if not all(grid_classes.get(found_class, 0) > 0 for found_class in KERNEL_FORM_EXCEPTIONS):
        problems.append("no grid point has a kernel plane of higher zero divisors and dim L = 2")
    exceptions = record["grid"].get("kernel_form_exceptions", [])
    if (
        len(exceptions) != len(PLANE_EXCEPTION_POINTS)
        or {tuple(row["split_point"]): row["common_kernel"] for row in exceptions} != PLANE_EXCEPTION_POINTS
    ):
        problems.append("the grid points with a kernel plane of nullity 7 and dim L = 2 are other points")
    if any(row["exact_plane_nullities"] != EXACT_PLANE_NULLITY.get(row["common_kernel"]) for row in exceptions):
        problems.append("a listed kernel plane has another exact nullity at its seven vectors")
    gaussian = record.get("gaussian_points", {})
    if gaussian != {
        "fixtures": sum(row["stratum"] == STRATA[0] for row in ranks),
        "samples_per_fixture": GAUSSIAN_PER_FIXTURE,
        "rejected": GAUSSIAN_REJECTED,
        "classes": GAUSSIAN_CLASSES,
    }:
        problems.append("the Gaussian real points of V(Q) fall in other classes")
    planes = record.get("general_planes", [])
    if [row.get("stratum") for row in planes] != list(STRATA):
        return [*problems, "the general planes do not cover the three strata"]
    for row in planes:
        if row["planes"] != PLANE_POINTS * PLANES_PER_POINT:
            problems.append(f"{row['stratum']}: {row['planes']} general planes")
        if row["common_kernels"] != GENERAL_PLANE_KERNELS[row["stratum"]]:
            problems.append(f"{row['stratum']}: a general plane of ker M(z) has another common kernel")
    return problems


def _serialized(record: dict[str, Any]) -> str:
    """The retained text of a record. The replay compares text, so true and 1, which compare equal, differ."""
    return json.dumps(record, indent=1, sort_keys=True) + "\n"


def main() -> None:
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
    for row in record["points"][::RANK_POINTS]:
        print(row["stratum"], row["three_plane_map_rank"], row["gauss_rank_w_free"], row["conjugate_pair_rank"])
    for row in record["image"]:
        print(row["stratum"], row["linear_span_dimension"], row["quadrics_vanishing"])


if __name__ == "__main__":
    main()
