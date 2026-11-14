"""The quadrics on the Gauss image of the nullity-4 strata: the span of S^2(Lambda^2 K(z)) and its annihilator.

V is the 15-dimensional space on which the skew lower block M(t) of the bordered matrix of `nullity4_gauss_image.py`
acts, linear in t, in the frame t_k = i^popcount(k) t'_k of the split coordinates t' (i sent to 9115). K(z) = ker M(z)
is the kernel three-plane at a point z of a nullity-4 stratum V(Q) minus V(G), V(G) minus V(Q) or V(Q) n V(G); all
computation is modulo 32029. The kernel plane of the bordered matrix at (z, w) with w free is K(z) n w-perp
(`nullity4_gauss_image.py`), so the Gauss image with w free is the union over z of the projective planes
P(Lambda^2 K(z)), each linear in the Plucker space P(Lambda^2 V). A quadric vanishes on the image exactly when its
polar form vanishes on S^2(Lambda^2 K(z)) for every z. S^2(Lambda^2 V) has dimension 5,565 = 4,200 + 1,365, the 1,365
being the Plucker quadrics p_ab p_cd - p_ac p_bd + p_ad p_bc (one per 4-subset of the 15 coordinates), so the quadrics
on the image are the annihilator of the span of the six products b_i b_j of a basis b_1, b_2, b_3 of Lambda^2 K(z), over
all z.

Polarization. A quadric with coefficient vector c over the monomials x_a x_b (a <= b) has the polar form
B(x, y) = Q(x + y) - Q(x) - Q(y), which is c paired with the row x_a y_b + x_b y_a for a < b and 2 x_a y_a for a = b.
Every row, product vector and family below uses this one convention, and a quadric c vanishes on the symmetric
product x y exactly when that pairing is zero.

The product on K. mu: Lambda^2 V -> V, u ^ v -> M(u) v, is linear and well defined because M(u) v = -M(v) u
(`sign_identity` of `nullity4_gauss_image.py`). The entry (r, c) of M(t) is cd_sign(16, r xor c, c) t_(r xor c), so
M(t) v is the imaginary part of the product t v of two imaginary elements of the 16-dimensional Cayley-Dickson
algebra, whose real part is minus their inner product: mu(u ^ v) is half the commutator of u and v, and K(z) is the
space of imaginary elements that commute with z.

Sandwiches. For a bivector p write Pi(p) for its skew 15 x 15 matrix, Pi(u ^ v) = u v^T - v u^T. For a symmetric
form D, Pi(p) D Pi(p) expands to
(v^T D u) u v^T - (v^T D v) u u^T - (u^T D u) v v^T + (u^T D v) v u^T, so every coefficient is a value of D on the
plane of u and v. Two consequences hold for every three-plane K, whose bivectors are all decomposable:
- If D vanishes on K, then Pi(p) D Pi(p) = 0 for every p in Lambda^2 K, and the 120 entries of Pi(p) D Pi(p) are
  quadrics that vanish on the image whenever D vanishes on every K(z).
- The combination of the entries with a symmetric matrix c is trace(c Pi(p) D Pi(p)) = 2 c(u, v) D(u, v) -
  c(u, u) D(v, v) - c(v, v) D(u, u), minus the mixed discriminant of c and D on the plane of u and v. When D
  restricted to K has rank one, D = l^2 for a linear form l on K, the combination vanishes on all of Lambda^2 K
  exactly when c vanishes on the plane K n ker l. A form D that vanishes on no K(z) therefore still yields
  quadrics on the image when its restrictions to the K(z) are degenerate.
The doubling forms are the three diagonal forms N1 = t_1^2 + ... + t_7^2, N2 = t_8^2 and N3 = t_9^2 + ... + t_15^2 of
the decomposition O + R e_8 + O e_8 of the imaginary part of the algebra as the double of the octonions; their sum is
the norm, which is Q in the frame.

The record holds, per stratum, from PLANES three-planes K(z) at the points `sample(stratum, Points(label), ...)`:

1. The dimensions of the spans of the vectors of K, of S^2 K in S^2 V, of Lambda^2 K and of Lambda^3 K in
   Lambda^3 V over the sampled planes (`spans`).
2. The rank r of the 6 x PLANES product vectors, the annihilator 5,565 - r, and three agreements that bound the
   sample from the side of generality: the rank at floor(r / 6) three-planes equals 6 floor(r / 6) and the rank at one
   more three-plane equals r, so no sampled plane is a combination of the earlier ones before the span saturates; the
   squares of RETAINED_PLANES planes of the retained sampler `nullity4_gauss_image.plucker` (planes of ker A(z, w) with
   w free, drawn under another label) have rank r, their first r planes have rank r, and both samples stacked
   have rank r. The rank r must equal 5,565 minus `quadrics_vanishing` of `nullity4_gauss_image.EXPECTED`. Both
   draws come from the one sampler `nullity4_gauss_image.sample`, so they agree on anything that sampler misses; the
   exact fixtures of the stratum come from another construction, and their product vectors stacked with the sample
   leave the rank at r (`rank_with_fixtures`). A rank of sampled products bounds the dimension of their span over the
   stratum, over GF(32029), from below, so these agreements are evidence that the quadrics counted as vanishing on
   the sample vanish on the image, and no proof.
3. The class of the product k, k' -> M(k) k' on K, tallied over the planes as (dim mu(Lambda^2 K), dim K + mu(Lambda^2
   K), whether every M(k) M(k') k'' over basis vectors vanishes, the rank of the nonzero products together with z in
   the frame of the kernel vectors, `_twist(z, ROOT_OF_MINUS_ONE)`; 0 when mu vanishes on Lambda^2 K). A class
   (1, 3, yes, 1) says that K is closed under the product, that the product lands in the line of z and that M(k) z = 0
   holds for every k, so M(k) k' = omega(k, k') z with a skew form omega and K(z) is a Heisenberg algebra with
   center z; the class (0, 3, yes, 0) says that every product vanishes. Beside it, the ranks of the norm and of the
   three doubling forms restricted to K, tallied over the planes (`doubling_form_ranks`).
4. The number of linear forms on Lambda^2 V that vanish on every sampled Lambda^2 K, the rank of those forms stacked
   with the 15 rows of mu (equal to the rank of mu when the forms lie in the row space of mu), the number of
   symmetric forms on V that vanish on every sampled K, and the rank of those forms stacked with the polar form of Q
   in the frame (1 when each is a multiple of it). In the frame Q is the sum of the squares of the 15 coordinates
   (`quadric_is_norm`), so on the two strata inside V(Q) the one form is the norm and K(z) is a null three-plane.
5. Eight families of quadrics, in this order, each with its written count of quadrics, its rank, the dimension of its
   intersection with the annihilator ("vanishing on the sampled span") and the cumulative rank of everything that
   vanishes so far; the annihilator dimension minus the last cumulative rank is the count of quadrics that no
   family explains (`unexplained`), and `characters` splits the monomials, the annihilator, the first seven
   families and all eight by the 16 characters of the sign changes of the coordinates (`character_split`):
   plucker_quadrics, the Plucker relations;
   linear_forms_times_coordinates, l(p) p_n for each linear form l of item 4 and each of the 105 coordinates;
   bivector_wedge_product_image, the 455 coordinates of p ^ mu(p) in Lambda^3 V;
   product_image_pairs, mu(p)_a mu(p)_b (120);
   bivector_matrix_block_product_image, Pi(p) M(e_j) mu(p) for the 15 frame vectors e_j (225);
   bivector_matrix_block_bivector_matrix, the independent entries a < b of the skew matrices Pi(p) M(e_j) Pi(p)
   (1,575);
   bivector_matrix_form_bivector_matrix, Pi(p) beta Pi(p) for each symmetric form beta of item 4 (120 each);
   bivector_matrix_doubling_form_bivector_matrix, Pi(p) D Pi(p) for the three doubling forms (360).
   The coefficient vectors come from evaluating each family at the 105 unit bivectors and the 5,460 sums of two of
   them (`quadric_coefficients`), checked against the family at two further points.
6. A calibration: the squares of GENERAL_BIVECTORS decomposable bivectors have rank 4,200, so their annihilator has
   dimension 1,365; the Plucker relations annihilate those squares and have rank 1,365, so the annihilator of the
   general squares is exactly the Plucker quadrics, and the first family of every stratum lying in the stratum's
   annihilator says that annihilator contains them.
7. Two ranks of whole families, which depend on no stratum (`family_ranks`): the Plucker quadrics with the 120
   entries of Pi(p) N Pi(p), N the polar form of Q, have rank 1,485 = 1,365 + 120; with the 225 entries of
   Pi(p) M(e_j) mu(p) added the rank is 1,678 = 1,365 + 313. The coefficients are integers, so each rank modulo
   32029 is a lower bound for the rank in characteristic 0.
8. Exact over Q(i), at the 66 fixtures of `nullity4-kernel-gauss-result.json`: the dimension of K(z), the class of
   item 3 and the ranks of the norm and of the three doubling forms on K(z), tallied per stratum (`fixtures`).

`verdict` first compares the fields and value types of a record with those of the record that the constants of
this module determine and stops there on a difference, then applies the rules by name, and last compares the
serialized text of the two records; apart from the input digests a record passes exactly when it is that record.

The loops over independent items run through `parallel.ordered_map`. The three strata take its serial path because
each holds about 3.4 GiB of matrices at its peak, and every matrix product of residues goes through float64 BLAS only
where each sum stays below 2^53. Ranks of prefixes of a matrix come from one elimination of its transpose
(`independent_rows`). The points come from sha256 of a label and a counter: a fixed list, with no seed.

`--write` writes gauss-image-quadrics-result.json beside this file; `--check` recomputes and compares.

Run from the repository root:
"$PYTHON" docs/evidence/a5-kernel-bundles-residuals/gauss_image_quadrics.py --check
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from collections import Counter
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

import numpy as np
import numpy.typing as npt
from flint import nmod_mat
from sympy import QQ_I, I

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BUNDLES = HERE.parent / "a5-kernel-bundles"
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(BUNDLES))

from kernel_three_plane_zero_divisors import _exact_block, _exact_kernel, _exact_rank  # noqa: E402
from nullity4_gauss_image import (  # noqa: E402
    EXPECTED,
    FIXTURES,
    IMAGINARY,
    PLUCKER_PAIRS,
    PLUCKER_QUADRICS,
    PRIME,
    QUADRIC_MONOMIALS,
    ROOT_OF_MINUS_ONE,
    STRATA,
    Points,
    _block,
    _fixture_splits,
    _nullspace,
    _polynomials,
    _rank,
    _twist,
    _value,
    lower_block,
    plucker,
    sample,
    sign_identity,
)

import parallel  # noqa: E402

Array = npt.NDArray[np.int64]
FloatArray = npt.NDArray[np.float64]

SCHEMA = "a5-kernel-bundles-residuals-gauss-image-quadrics-v2"
RECORD = HERE / "gauss-image-quadrics-result.json"
SOURCE_PATHS = (
    HERE / "gauss_image_quadrics.py",
    HERE / "nullity4_gauss_image.py",
    HERE / "kernel_three_plane_zero_divisors.py",
    FIXTURES,
    BUNDLES / "kernel_frames.py",
    BUNDLES / "kernel_symmetry.py",
    ROOT / "docs" / "evidence" / "a5-strata-regularity" / "strata_regularity.py",
    ROOT / "docs" / "evidence" / "a5-rank-strata-equations" / "rederive_strata_equations.py",
    ROOT / "gororoba_quantum" / "cd_core.py",
)
FIELD = f"GF({PRIME}), i = {ROOT_OF_MINUS_ONE}"

PLANES = 760
GENERAL_BIVECTORS = 4400
RETAINED_PLANES = 4300
SAMPLE_LABEL = "quadrics"
GENERAL_LABEL = "quadrics:general"
CHECK_LABEL = "quadrics:check"
BIVECTORS = len(PLUCKER_PAIRS)
QUADRIC_COEFFICIENTS = len(QUADRIC_MONOMIALS)
SYMMETRIC_COEFFICIENTS = IMAGINARY * (IMAGINARY + 1) // 2
PRODUCT_PAIRS = ((0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2))
# A float64 matrix product of residues is exact below 2^53.
EXACT_FLOAT_BOUND = 2**53

# Per stratum: dimensions of the span of the vectors of K, of S^2 K in S^2 V, of Lambda^2 K and of Lambda^3 K.
SPANS: dict[str, dict[str, int]] = {
    STRATA[0]: {"vectors": 15, "symmetric_square": 119, "bivectors": 105, "trivectors": 356},
    STRATA[1]: {"vectors": 15, "symmetric_square": 120, "bivectors": 105, "trivectors": 439},
    STRATA[2]: {"vectors": 15, "symmetric_square": 119, "bivectors": 90, "trivectors": 237},
}
# Per stratum: the classes (dim mu(Lambda^2 K), dim K + mu(Lambda^2 K), every triple product vanishes, rank of the
# products with z) with their plane counts.
PRODUCT_CLASSES: dict[str, list[list[Any]]] = {
    STRATA[0]: [[1, 3, True, 1, PLANES]],
    STRATA[1]: [[1, 4, False, 2, PLANES]],
    STRATA[2]: [[0, 3, True, 0, PLANES]],
}
# Per stratum: the number of linear forms on Lambda^2 V that vanish on every Lambda^2 K, and of symmetric forms on V
# that vanish on every K.
FORM_COUNTS: dict[str, dict[str, int]] = {
    STRATA[0]: {"linear_forms": 0, "symmetric_forms": 1},
    STRATA[1]: {"linear_forms": 0, "symmetric_forms": 0},
    STRATA[2]: {"linear_forms": 15, "symmetric_forms": 1},
}
MU_RANK = 15
# Per stratum: the ranks of the norm and of the three doubling forms N1, N2, N3 on K, with their plane counts.
DOUBLING_FORM_RANKS: dict[str, list[list[int]]] = {
    STRATA[0]: [[0, 3, 1, 3, PLANES]],
    STRATA[1]: [[1, 1, 1, 1, PLANES]],
    STRATA[2]: [[0, 1, 1, 1, PLANES]],
}
# The exact fixtures per stratum, and their classes over Q(i): (stratum, dim K, dim mu(Lambda^2 K), dim K +
# mu(Lambda^2 K), every triple product vanishes, rank of the products with z, ranks of the norm, N1, N2, N3 on K,
# count of fixtures).
FIXTURE_PLANES = {STRATA[0]: 12, STRATA[1]: 52, STRATA[2]: 2}
FIXTURE_CLASSES: list[list[Any]] = [
    [STRATA[1], 3, 1, 4, False, 2, 1, 1, 0, 0, 4],
    [STRATA[1], 3, 1, 4, False, 2, 1, 1, 0, 1, 33],
    [STRATA[1], 3, 1, 4, False, 2, 1, 1, 1, 0, 6],
    [STRATA[1], 3, 1, 4, False, 2, 1, 1, 1, 1, 9],
    [STRATA[2], 3, 0, 3, True, 0, 0, 1, 0, 1, 2],
    [STRATA[0], 3, 1, 3, True, 1, 0, 3, 1, 3, 12],
]
# Ranks of whole families of quadrics: Plucker with Pi(p) N Pi(p), and with Pi(p) M(e_j) mu(p) added.
FAMILY_RANKS = {"plucker_with_norm_family": 1485, "plucker_with_block_product_and_norm_families": 1678}
# The rank of the symmetric forms that vanish on every K stacked with the polar form of Q in the frame: 1 when
# every such form is a multiple of that polar form, and where no form vanishes.
FORMS_WITH_QUADRIC_RANK = 1
# Per stratum, in family order: (written count, rank, dimension of its intersection with the annihilator,
# cumulative rank).
FAMILY_NAMES = (
    "plucker_quadrics",
    "linear_forms_times_coordinates",
    "bivector_wedge_product_image",
    "product_image_pairs",
    "bivector_matrix_block_product_image",
    "bivector_matrix_block_bivector_matrix",
    "bivector_matrix_form_bivector_matrix",
    "bivector_matrix_doubling_form_bivector_matrix",
)
FAMILY_TALLIES: dict[str, list[tuple[int, int, int, int]]] = {
    STRATA[0]: [
        (1365, 1365, 1365, 1365),
        (0, 0, 0, 1365),
        (455, 455, 99, 1463),
        (120, 120, 1, 1463),
        (225, 211, 211, 1582),
        (1575, 1470, 232, 1582),
        (120, 120, 120, 1678),
        (360, 342, 120, 1678),
    ],
    STRATA[1]: [
        (1365, 1365, 1365, 1365),
        (0, 0, 0, 1365),
        (455, 455, 4, 1368),
        (120, 120, 3, 1371),
        (225, 211, 18, 1385),
        (1575, 1470, 168, 1518),
        (0, 0, 0, 1518),
        (360, 342, 57, 1543),
    ],
    STRATA[2]: [
        (1365, 1365, 1365, 1365),
        (1575, 1470, 1470, 2820),
        (455, 455, 455, 2820),
        (120, 120, 120, 2820),
        (225, 211, 211, 2820),
        (1575, 1470, 1470, 2820),
        (120, 120, 120, 2916),
        (360, 342, 152, 2940),
    ],
}
# The families that vanish on every Lambda^2 K by construction: linear forms times coordinates, and Pi beta Pi.
ALWAYS_VANISHING = (1, 6)
# Per stratum: the annihilator dimension minus the last cumulative rank.
UNEXPLAINED = {STRATA[0]: 0, STRATA[1]: 0, STRATA[2]: 0}
# Per stratum and per character of the sign group, in the order of CHARACTERS (the trivial character, the characters
# 1 to 8, the characters 9 to 15): the monomials, the quadrics on the sampled span, those the first seven families
# supply and those all eight supply.
CHARACTER_TALLIES: dict[str, list[list[int]]] = {
    STRATA[0]: [
        [420, 133, 133, 133],
        *([[343, 102, 102, 102]] * 7),
        [343, 103, 103, 103],
        *([[343, 104, 104, 104]] * 7),
    ],
    STRATA[1]: [[420, 119, 116, 119], *([[343, 94, 93, 94]] * 8), *([[343, 96, 94, 96]] * 7)],
    STRATA[2]: [[420, 225, 223, 225], *([[343, 181, 180, 181]] * 8), *([[343, 181, 179, 181]] * 7)],
}
CALIBRATION = {
    "general_bivectors": GENERAL_BIVECTORS,
    "square_rank": QUADRIC_COEFFICIENTS - PLUCKER_QUADRICS,
    "annihilator": PLUCKER_QUADRICS,
    "plucker_family_rank": PLUCKER_QUADRICS,
    "plucker_family_annihilates": True,
}


def _require(condition: bool, message: str) -> None:
    """Raise when an internal invariant fails; unlike `assert` it survives `python -O`."""
    if not condition:
        raise RuntimeError(message)


def _matrix(rows: Array) -> nmod_mat:
    """The rows as a matrix over GF(PRIME)."""
    return nmod_mat(rows.shape[0], rows.shape[1], rows.ravel().tolist(), PRIME)


def matrix_rank(rows: Array) -> int:
    """The rank over GF(PRIME) of an integer matrix; the empty matrix has rank 0."""
    if rows.shape[0] == 0:
        return 0
    return int(_matrix(rows).rank())


def independent_rows(rows: Array) -> list[int]:
    """The indices of the rows that are independent of the rows before them, in order.

    The pivot columns of the reduced echelon form of the transpose are exactly the columns that are not in the span
    of the columns before them. A pivot of the row i of the echelon form is the first nonzero entry of that row and
    the pivots increase with i, so one scan along the columns finds all of them. The rank of the first t rows is the
    number of indices below t, which gives the rank of every prefix from one elimination.
    """
    if rows.shape[0] == 0:
        return []
    echelon, rank = _matrix(np.ascontiguousarray(rows.T)).rref()
    pivots: list[int] = []
    for column in range(rows.shape[0]):
        if len(pivots) < rank and int(echelon[len(pivots), column]):
            pivots.append(column)
    _require(len(pivots) == rank, "the pivot scan found another rank than the elimination")
    return pivots


def prefix_rank(pivots: Sequence[int], count: int) -> int:
    """The rank of the first `count` rows, from the independent rows of `independent_rows`."""
    return sum(1 for index in pivots if index < count)


def product_mod_prime(left: Array | FloatArray, right: Array | FloatArray) -> Array:
    """left @ right modulo PRIME through float64 BLAS, exact because every sum stays below 2^53.

    The entries are residues below PRIME, so each product is below PRIME^2 and a sum of the inner dimension of
    them stays below 2^53 for the sizes this module multiplies.
    """
    _require(left.shape[1] * (PRIME - 1) ** 2 < EXACT_FLOAT_BOUND, "the float64 product could round")
    for operand in (left, right):
        reduced = operand.size == 0 or bool(0 <= operand.min() and operand.max() < PRIME)
        _require(reduced, "an operand is not a reduced residue")
    return (left.astype(np.float64) @ right.astype(np.float64)).astype(np.int64) % PRIME


PAIR_FIRST = np.array([first - 1 for first, _ in PLUCKER_PAIRS])
PAIR_SECOND = np.array([second - 1 for _, second in PLUCKER_PAIRS])
MONOMIAL_FIRST = np.array([first for first, _ in QUADRIC_MONOMIALS])
MONOMIAL_SECOND = np.array([second for _, second in QUADRIC_MONOMIALS])
SYMMETRIC_MONOMIALS = tuple(itertools.combinations_with_replacement(range(IMAGINARY), 2))
SYMMETRIC_FIRST = np.array([first for first, _ in SYMMETRIC_MONOMIALS])
SYMMETRIC_SECOND = np.array([second for _, second in SYMMETRIC_MONOMIALS])
TRIPLES = tuple(itertools.combinations(range(IMAGINARY), 3))
TRIPLE_FIRST, TRIPLE_SECOND, TRIPLE_THIRD = (np.array([triple[index] for triple in TRIPLES]) for index in range(3))
PLUCKER_RELATIONS = tuple(itertools.combinations(range(IMAGINARY), 4))
PAIR_INDEX = {(first - 1, second - 1): index for index, (first, second) in enumerate(PLUCKER_PAIRS)}


# The sign changes e_k -> chi(k) e_k, chi a character of the group (Z/2)^4 of the four index bits, satisfy
# M(D t) = D M(t) D because the entry (r, c) of M(t) is a sign times t at the index r xor c, so K(D z) = D K(z) and
# the sign changes preserve the nullity-4 locus and the norm Q. The quadrics on the image of a stratum they preserve
# split by character, and `character_split` records the sums that hold exactly when they do. The monomial
# p_ab p_cd has the character a xor b xor c xor d of the 1-based indices.
CHARACTERS = tuple(range(16))
MONOMIAL_CHARACTER = np.array(
    [
        (PAIR_FIRST[first] + 1) ^ (PAIR_SECOND[first] + 1) ^ (PAIR_FIRST[second] + 1) ^ (PAIR_SECOND[second] + 1)
        for first, second in QUADRIC_MONOMIALS
    ]
)


def character_split(products: Array, vanishing: Sequence[Array]) -> list[list[int]]:
    """Per character: its monomials, the quadrics on the sampled span and the quadrics each family set supplies.

    A space of quadrics that the sign changes preserve is the direct sum of its parts supported on the monomials
    of one character. The part of the annihilator has dimension monomials minus the rank of the product vectors on
    those columns, and the part of a set of families has the rank of its rows on those columns; the sums over the
    characters equal 5,565, the annihilator dimension and the rank of each set exactly when the spaces split.
    """
    rows = []
    for character in CHARACTERS:
        columns = np.flatnonzero(MONOMIAL_CHARACTER == character)
        rows.append(
            [
                int(columns.size),
                int(columns.size) - matrix_rank(products[:, columns]),
                *(matrix_rank(block[:, columns]) for block in vanishing),
            ]
        )
    return rows


def wedge(first: Array, second: Array) -> Array:
    """The Plucker coordinates u_a v_b - u_b v_a of u ^ v for a < b, along the last axis."""
    return (
        first[..., PAIR_FIRST] * second[..., PAIR_SECOND] - first[..., PAIR_SECOND] * second[..., PAIR_FIRST]
    ) % PRIME


def polar_rows(first: Array, second: Array, left: Array, right: Array) -> Array:
    """The polar pairing rows of x and y over the monomials (left[n], right[n]) of the quadratic forms.

    A quadric sum c_ab x_a x_b over a <= b has polar form B(x, y) = Q(x + y) - Q(x) - Q(y), which equals the
    coefficient vector c paired with the row x_a y_b + x_b y_a for a < b and 2 x_a y_a for a = b. A quadric
    vanishes on the symmetric product of two vectors exactly when this pairing is zero.
    """
    rows = (first[..., left] * second[..., right] + first[..., right] * second[..., left]) % PRIME
    diagonal = left == right
    rows[..., diagonal] = 2 * first[..., left[diagonal]] * second[..., left[diagonal]] % PRIME
    return rows


def skew_matrices(bivectors: Array) -> Array:
    """Pi(p), the skew 15 x 15 matrices of the bivectors p (rows of the argument)."""
    matrices = np.zeros((bivectors.shape[0], IMAGINARY, IMAGINARY), dtype=np.int64)
    matrices[:, PAIR_FIRST, PAIR_SECOND] = bivectors
    matrices[:, PAIR_SECOND, PAIR_FIRST] = (-bivectors) % PRIME
    return matrices


def frame_blocks() -> list[Array]:
    """M(e_j) for the 15 frame vectors, the skew lower blocks linear in the frame vector."""
    identity = np.eye(IMAGINARY, dtype=np.int64)
    return [np.array(_block([int(value) for value in identity[index]]), dtype=np.int64) for index in range(IMAGINARY)]


def mu_matrix(blocks: Sequence[Array]) -> Array:
    """The 15 x 105 matrix of mu: Lambda^2 V -> V, e_a ^ e_b -> M(e_a) e_b.

    mu is well defined on the exterior square because M(u) v = -M(v) u, the identity `sign_identity` checks.
    """
    _require(sign_identity(), "the block signs do not satisfy M(u) v = -M(v) u")
    matrix = np.zeros((IMAGINARY, BIVECTORS), dtype=np.int64)
    for index, (first, second) in enumerate(zip(PAIR_FIRST, PAIR_SECOND, strict=True)):
        matrix[:, index] = blocks[first][:, second]
        _require(not ((blocks[first][:, second] + blocks[second][:, first]) % PRIME).any(), "mu is not skew")
    return matrix


BLOCKS = frame_blocks()
MU = mu_matrix(BLOCKS)


def product_class(split: Sequence[int], kernel: list[list[int]]) -> list[Any]:
    """The class of the product k, k' -> M(k) k' on K = ker M(z) at one point.

    The entries are dim mu(Lambda^2 K), dim of K + mu(Lambda^2 K), whether M(k) M(k') k'' vanishes for all basis
    vectors, and the rank of the nonzero products together with z in the frame of the kernel vectors (0 when mu
    vanishes on Lambda^2 K).
    """
    vectors = np.array(kernel, dtype=np.int64)
    blocks = [np.array(_block(vector), dtype=np.int64) for vector in kernel]
    products = [blocks[first] @ vectors[second] % PRIME for first, second in ((0, 1), (0, 2), (1, 2))]
    nonzero = [[int(value) for value in vector] for vector in products if vector.any()]
    triple_vanishes = not any(
        (blocks[first] @ (blocks[second] @ vectors[third] % PRIME) % PRIME).any()
        for first, second, third in itertools.product(range(3), repeat=3)
    )
    frame_point = _twist(split, ROOT_OF_MINUS_ONE)
    return [
        _rank(nonzero) if nonzero else 0,
        _rank([*kernel, *nonzero]),
        triple_vanishes,
        _rank([*nonzero, frame_point]) if nonzero else 0,
    ]


# The three diagonal forms of the decomposition O + R e_8 + O e_8 of the imaginary units, by 1-based index.
DOUBLING_RANGES = ((1, 7), (8, 8), (9, 15))
DOUBLING_FORMS = tuple(
    np.diag([int(low <= index <= high) for index in range(1, IMAGINARY + 1)]).astype(np.int64)
    for low, high in DOUBLING_RANGES
)


def doubling_form_ranks(kernel: list[list[int]]) -> list[int]:
    """The ranks of the norm and of the three doubling forms restricted to the span of the kernel vectors."""
    vectors = np.array(kernel, dtype=np.int64)
    forms = [np.eye(IMAGINARY, dtype=np.int64), *DOUBLING_FORMS]
    return [matrix_rank(vectors @ form @ vectors.T % PRIME) for form in forms]


def three_plane(job: tuple[str, int]) -> tuple[list[list[int]], list[Any], list[int]]:
    """A point z of the stratum, a basis of K(z) = ker M(z), the class of the product and the form ranks on K(z)."""
    stratum, number = job
    split = sample(stratum, Points(f"{SAMPLE_LABEL}:{stratum}:{number}"), _polynomials())
    kernel = _nullspace(lower_block(split))
    _require(len(kernel) == 3, "the kernel of the lower block is not a three-plane")
    return kernel, product_class(split, kernel), doubling_form_ranks(kernel)


def fixture_class(job: tuple[int, str, list[int]]) -> list[Any]:
    """Exact over Q(i) at one fixture: dim K(z), the class of the product on K(z) and the form ranks on K(z).

    The entries after the stratum are those of `product_class` and `doubling_form_ranks`, preceded by dim K(z), with
    the frame point t_k = i^popcount(k) t'_k of the split point t' and every rank taken over Q(i).
    """
    _, stratum, split = job
    unit = QQ_I.convert(I)
    frame_point = [unit ** (index + 1).bit_count() * QQ_I.convert(value) for index, value in enumerate(split)]
    kernel = _exact_kernel(_exact_block(frame_point))
    blocks = [_exact_block(vector) for vector in kernel]

    def apply(block: list[list[Any]], vector: list[Any]) -> list[Any]:
        return [sum((entry * value for entry, value in zip(row, vector, strict=True)), QQ_I.zero) for row in block]

    def rank(rows: list[list[Any]]) -> int:
        return _exact_rank(rows) if rows else 0

    pairs = list(itertools.combinations(range(len(kernel)), 2))
    nonzero = [vector for vector in (apply(blocks[a], kernel[b]) for a, b in pairs) if any(vector)]
    triple_vanishes = not any(
        any(apply(blocks[a], apply(blocks[b], kernel[c])))
        for a, b, c in itertools.product(range(len(kernel)), repeat=3)
    )
    grams = []
    for low, high in ((1, IMAGINARY), *DOUBLING_RANGES):
        grams.append(
            rank([[sum((u[k] * v[k] for k in range(low - 1, high)), QQ_I.zero) for v in kernel] for u in kernel])
        )
    return [
        stratum,
        len(kernel),
        rank(nonzero),
        rank([*kernel, *nonzero]),
        triple_vanishes,
        rank([*nonzero, frame_point]) if nonzero else 0,
        *grams,
    ]


def fixture_classes() -> list[list[Any]]:
    """The classes of `fixture_class` over the exact fixtures, each with its count of fixtures."""
    classes = Counter(json.dumps(row) for row in parallel.ordered_map(fixture_class, _fixture_splits(), min_items=2))
    return [[*json.loads(key), count] for key, count in sorted(classes.items())]


def fixture_kernels(stratum: str) -> Array:
    """Bases of K(z) modulo PRIME at the exact fixtures of one stratum."""
    kernels = []
    for _, name, split in _fixture_splits():
        if name == stratum:
            kernel = _nullspace(lower_block([value % PRIME for value in split]))
            _require(len(kernel) == 3, "the kernel at a fixture is not a three-plane modulo the prime")
            kernels.append(kernel)
    return np.array(kernels, dtype=np.int64)


def spans(kernels: Array) -> dict[str, int]:
    """The dimensions of the spans of K, S^2 K, Lambda^2 K and Lambda^3 K over every sampled three-plane."""
    first, second = np.array([a for a, _ in PRODUCT_PAIRS]), np.array([b for _, b in PRODUCT_PAIRS])
    symmetric = polar_rows(kernels[:, first], kernels[:, second], SYMMETRIC_FIRST, SYMMETRIC_SECOND)
    bivectors = wedge(kernels[:, [0, 0, 1]], kernels[:, [1, 2, 2]])
    trivectors = np.empty((kernels.shape[0], len(TRIPLES)), dtype=np.int64)
    for column, (a, b, c) in enumerate(TRIPLES):
        minor = (kernels[:, 1, b] * kernels[:, 2, c] - kernels[:, 1, c] * kernels[:, 2, b]) % PRIME * kernels[:, 0, a]
        minor += (kernels[:, 1, c] * kernels[:, 2, a] - kernels[:, 1, a] * kernels[:, 2, c]) % PRIME * kernels[:, 0, b]
        minor += (kernels[:, 1, a] * kernels[:, 2, b] - kernels[:, 1, b] * kernels[:, 2, a]) % PRIME * kernels[:, 0, c]
        trivectors[:, column] = minor % PRIME
    return {
        "vectors": matrix_rank(kernels.reshape(-1, IMAGINARY)),
        "symmetric_square": matrix_rank(symmetric.reshape(-1, SYMMETRIC_COEFFICIENTS)),
        "bivectors": matrix_rank(bivectors.reshape(-1, BIVECTORS)),
        "trivectors": matrix_rank(trivectors),
    }


def product_vectors(kernels: Array) -> Array:
    """The six products b_i b_j of a basis of Lambda^2 K(z), as polar rows in S^2(Lambda^2 V), plane by plane."""
    basis = wedge(kernels[:, [0, 0, 1]], kernels[:, [1, 2, 2]])
    first, second = np.array([a for a, _ in PRODUCT_PAIRS]), np.array([b for _, b in PRODUCT_PAIRS])
    rows = polar_rows(basis[:, first], basis[:, second], MONOMIAL_FIRST, MONOMIAL_SECOND)
    return rows.reshape(-1, QUADRIC_COEFFICIENTS)


def quadric_rank_record(stratum: str, kernels: Array) -> tuple[dict[str, Any], Array]:
    """The rank of the product vectors, its saturation and its agreement with the retained plane sampler.

    The rank r of the 6 x PLANES product vectors is read at floor(r / 6) three-planes (full rank 6 floor(r / 6)) and at
    one more (rank r), which shows the sample as general as six vectors per three-plane allow. The squares of
    RETAINED_PLANES planes of `nullity4_gauss_image.plucker`, each a plane of ker A(z, w) inside some K(z) with w free,
    have the same rank, their first r planes have rank r, and the two samples stacked have rank r. The product vectors
    of the exact fixtures of the stratum, points that no sampler drew, stacked with the sample leave the rank at r.
    """
    products = product_vectors(kernels)
    pivots = independent_rows(products)
    rank = len(pivots)
    below = rank // 6
    retained_planes = np.array(
        parallel.ordered_map(plucker, [(stratum, number) for number in range(RETAINED_PLANES)], min_items=2),
        dtype=np.int64,
    )
    retained = polar_rows(retained_planes, retained_planes, MONOMIAL_FIRST, MONOMIAL_SECOND)
    del retained_planes
    retained_pivots = independent_rows(retained)
    fixtures = fixture_kernels(stratum)
    record = {
        "vectors": int(products.shape[0]),
        "rank": rank,
        "annihilator": QUADRIC_COEFFICIENTS - rank,
        "planes_below": below,
        "rank_below": prefix_rank(pivots, 6 * below),
        "rank_above": prefix_rank(pivots, 6 * (below + 1)),
        "retained_planes": RETAINED_PLANES,
        "retained_rank": len(retained_pivots),
        "retained_rank_first": prefix_rank(retained_pivots, rank),
        "retained_rank_stacked": matrix_rank(np.concatenate([products, retained])),
        "fixture_planes": int(fixtures.shape[0]),
        "rank_with_fixtures": matrix_rank(np.concatenate([products, product_vectors(fixtures)])),
    }
    return record, products


def calibration() -> dict[str, Any]:
    """The squares of GENERAL_BIVECTORS decomposable bivectors, whose annihilator is the Plucker quadrics.

    The 1,365 Plucker relations p_ab p_cd - p_ac p_bd + p_ad p_bc vanish on every decomposable bivector, so their
    polar pairing with the squares is zero, and the rank of the squares fixes the dimension of the annihilator.
    """
    points = Points(GENERAL_LABEL)
    first = np.array([points.vector() for _ in range(GENERAL_BIVECTORS)], dtype=np.int64)
    second = np.array([points.vector() for _ in range(GENERAL_BIVECTORS)], dtype=np.int64)
    bivectors = wedge(first, second)
    squares = polar_rows(bivectors, bivectors, MONOMIAL_FIRST, MONOMIAL_SECOND)
    family = quadric_coefficients(plucker_relations, PLUCKER_QUADRICS)
    square_rank = matrix_rank(squares)
    return {
        "general_bivectors": GENERAL_BIVECTORS,
        "square_rank": square_rank,
        "annihilator": QUADRIC_COEFFICIENTS - square_rank,
        "plucker_family_rank": matrix_rank(family),
        "plucker_family_annihilates": not product_mod_prime(family, squares.T).any(),
    }


# Quadric families: vector-valued functions of the bivector p in the 105 Plucker coordinates, each coordinate a
# quadratic form in p, turned into coefficient vectors over QUADRIC_MONOMIALS by polarization.
def plucker_relations(bivectors: Array) -> Array:
    """The Plucker relations p_ab p_cd - p_ac p_bd + p_ad p_bc, one per 4-subset of the 15 coordinates."""
    columns = []
    for a, b, c, d in PLUCKER_RELATIONS:
        columns.append(
            bivectors[:, PAIR_INDEX[a, b]] * bivectors[:, PAIR_INDEX[c, d]]
            - bivectors[:, PAIR_INDEX[a, c]] * bivectors[:, PAIR_INDEX[b, d]]
            + bivectors[:, PAIR_INDEX[a, d]] * bivectors[:, PAIR_INDEX[b, c]]
        )
    return np.stack(columns, axis=1) % PRIME


def wedge_with_product_image(bivectors: Array) -> Array:
    """The coordinates of p ^ mu(p) in Lambda^3 V."""
    matrices = skew_matrices(bivectors)
    image = bivectors @ MU.T % PRIME
    return (
        matrices[:, TRIPLE_FIRST, TRIPLE_SECOND] * image[:, TRIPLE_THIRD]
        - matrices[:, TRIPLE_FIRST, TRIPLE_THIRD] * image[:, TRIPLE_SECOND]
        + matrices[:, TRIPLE_SECOND, TRIPLE_THIRD] * image[:, TRIPLE_FIRST]
    ) % PRIME


def product_image_pairs(bivectors: Array) -> Array:
    """The products mu(p)_a mu(p)_b of the coordinates of mu(p)."""
    image = bivectors @ MU.T % PRIME
    return image[:, SYMMETRIC_FIRST] * image[:, SYMMETRIC_SECOND] % PRIME


def bivector_matrix_block_product_image(bivectors: Array) -> Array:
    """Pi(p) M(e_j) mu(p) for each frame vector e_j, 15 coordinates each."""
    matrices = skew_matrices(bivectors)
    image = bivectors @ MU.T % PRIME
    columns = [np.einsum("nab,nb->na", matrices, image @ block.T % PRIME) % PRIME for block in BLOCKS]
    return np.concatenate(columns, axis=1)


def bivector_matrix_block_bivector_matrix(bivectors: Array) -> Array:
    """The independent entries of Pi(p) M(e_j) Pi(p), a skew matrix, for each frame vector e_j."""
    matrices = skew_matrices(bivectors)
    columns = [np.matmul(np.matmul(matrices, block) % PRIME, matrices) % PRIME for block in BLOCKS]
    return np.concatenate([column[:, PAIR_FIRST, PAIR_SECOND] for column in columns], axis=1)


def linear_forms_times_coordinates(forms: Array) -> Callable[[Array], Array]:
    """The products l(p) p_n of a linear form l on Lambda^2 V that vanishes on every Lambda^2 K with a coordinate."""

    def function(bivectors: Array) -> Array:
        values = bivectors @ forms.T % PRIME
        return (values[:, :, None] * bivectors[:, None, :] % PRIME).reshape(bivectors.shape[0], -1)

    return function


def bivector_matrix_form_bivector_matrix(betas: Sequence[Array]) -> Callable[[Array], Array]:
    """The independent entries of Pi(p) beta Pi(p), a symmetric matrix, for each symmetric form beta."""

    def function(bivectors: Array) -> Array:
        matrices = skew_matrices(bivectors)
        columns = [np.matmul(np.matmul(matrices, beta) % PRIME, matrices) % PRIME for beta in betas]
        return np.concatenate([column[:, SYMMETRIC_FIRST, SYMMETRIC_SECOND] for column in columns], axis=1)

    return function


def quadric_coefficients(function: Callable[[Array], Array], count: int) -> Array:
    """The coefficient vectors, over QUADRIC_MONOMIALS, of the `count` quadrics that `function` evaluates.

    A quadratic form f has coefficient f(e_a) on x_a^2 and f(e_a + e_b) - f(e_a) - f(e_b) on x_a x_b, so
    evaluating at the 105 unit vectors and the 5,460 sums of two of them recovers every coefficient. The result is
    checked against `function` at two further points.
    """
    unit = np.eye(BIVECTORS, dtype=np.int64)
    off_diagonal = MONOMIAL_FIRST != MONOMIAL_SECOND
    first, second = MONOMIAL_FIRST[off_diagonal], MONOMIAL_SECOND[off_diagonal]
    single = function(unit)
    mixed = function((unit[first] + unit[second]) % PRIME)
    _require(single.shape[1] == count, "a family has another size than stated")
    coefficients = np.empty((count, QUADRIC_COEFFICIENTS), dtype=np.int64)
    coefficients[:, ~off_diagonal] = single[MONOMIAL_FIRST[~off_diagonal]].T
    coefficients[:, off_diagonal] = ((mixed - single[first] - single[second]) % PRIME).T
    points = Points(CHECK_LABEL)
    for _ in range(2):
        point = np.array([[points.value() for _ in range(BIVECTORS)]], dtype=np.int64)
        monomials = point[0, MONOMIAL_FIRST] * point[0, MONOMIAL_SECOND] % PRIME
        _require(
            bool(((coefficients @ monomials) % PRIME == function(point)[0]).all()),
            "the coefficients do not reproduce the quadrics",
        )
    return coefficients


def family_ranks() -> dict[str, int]:
    """The ranks of the Plucker quadrics with Pi(p) N Pi(p), and with Pi(p) M(e_j) mu(p) added; N the polar form of Q.

    The coefficient vectors are integers, so a rank modulo PRIME is a lower bound for the rank in characteristic 0.
    Where mu(p) is a multiple of z and K(z) is null, every quadric of the three families vanishes on Lambda^2 K(z).
    """
    plucker_family = quadric_coefficients(plucker_relations, PLUCKER_QUADRICS)
    norm_family = quadric_coefficients(
        bivector_matrix_form_bivector_matrix([quadric_polar_form()]), SYMMETRIC_COEFFICIENTS
    )
    block_family = quadric_coefficients(bivector_matrix_block_product_image, IMAGINARY * IMAGINARY)
    return {
        "plucker_with_norm_family": matrix_rank(np.concatenate([plucker_family, norm_family])),
        "plucker_with_block_product_and_norm_families": matrix_rank(
            np.concatenate([plucker_family, block_family, norm_family])
        ),
    }


def linear_forms_vanishing(bivectors: Array) -> Array:
    """A basis of the linear forms on Lambda^2 V that vanish on every sampled Lambda^2 K, one per row."""
    rows = [[int(value) for value in row] for row in bivectors.reshape(-1, BIVECTORS)]
    return np.array(_nullspace(rows), dtype=np.int64).reshape(-1, BIVECTORS)


def symmetric_forms_vanishing(kernels: Array) -> list[Array]:
    """The symmetric matrices beta of the bilinear forms on V that vanish on every sampled K, as 15 x 15 arrays.

    A coefficient vector c with polar pairing zero against every pair of basis vectors of every K gives the form
    beta(u, v) = sum over a < b of c_ab (u_a v_b + u_b v_a) + 2 sum of c_aa u_a v_a.
    """
    first, second = np.array([a for a, _ in PRODUCT_PAIRS]), np.array([b for _, b in PRODUCT_PAIRS])
    rows = polar_rows(kernels[:, first], kernels[:, second], SYMMETRIC_FIRST, SYMMETRIC_SECOND)
    flat = [[int(value) for value in row] for row in rows.reshape(-1, SYMMETRIC_COEFFICIENTS)]
    betas = []
    for coefficients in _nullspace(flat):
        beta = np.zeros((IMAGINARY, IMAGINARY), dtype=np.int64)
        for value, (a, b) in zip(coefficients, SYMMETRIC_MONOMIALS, strict=True):
            beta[a, b] = beta[b, a] = 2 * value % PRIME if a == b else value
        betas.append(beta)
    for beta in betas:
        pairing = np.einsum("nia,ab,njb->nij", kernels, beta, kernels) % PRIME
        _require(not pairing.any(), "a symmetric form does not vanish on the three-planes")
    return betas


def quadric_polar_form() -> Array:
    """The polar form Q(u + v) - Q(u) - Q(v) of the quadric Q in the frame of the kernel vectors, as a 15 x 15 array.

    Q is a polynomial in the split coordinates t', and a frame vector t has t'_k = i^-popcount(k) t_k.
    """
    quadric = _polynomials()["Q"]
    inverse = pow(ROOT_OF_MINUS_ONE, -1, PRIME)
    unit = [[int(row == column) for column in range(IMAGINARY)] for row in range(IMAGINARY)]

    def value(vector: Sequence[int]) -> int:
        return _value(quadric, _twist(vector, inverse))

    single = [value(vector) for vector in unit]
    polar = np.zeros((IMAGINARY, IMAGINARY), dtype=np.int64)
    for row in range(IMAGINARY):
        for column in range(IMAGINARY):
            both = [first + second for first, second in zip(unit[row], unit[column], strict=True)]
            polar[row, column] = (value(both) - single[row] - single[column]) % PRIME
    return polar


def annihilating_combinations(family: Array, products_float: FloatArray) -> Array:
    """A basis of the combinations of the family rows that vanish on every product vector.

    A quadric c vanishes on the sampled span exactly when its polar pairing with every product vector is zero. The
    left kernel of the pairing matrix family x products^T gives the coefficients x with x F annihilating, and
    x F lists those quadrics, a spanning set of the intersection of the family with the annihilator.
    """
    if family.shape[0] == 0:
        return np.zeros((0, QUADRIC_COEFFICIENTS), dtype=np.int64)
    pairing = product_mod_prime(family, products_float.T)
    basis, nullity = _matrix(pairing.T.copy()).nullspace()
    size = family.shape[0]
    left = np.array([int(value) for value in basis.entries()], dtype=np.int64).reshape(size, size)[:, :nullity].T
    return product_mod_prime(left, family)


def family_tallies(
    products: Array, forms: Array, betas: Sequence[Array], annihilator: int
) -> tuple[list[dict[str, Any]], int, list[list[int]]]:
    """Per family its rank, the dimension of its intersection with the annihilator and the cumulative rank.

    The families run in the order of FAMILY_NAMES. The cumulative rank is the rank of every annihilating quadric the
    families so far supply, and the annihilator dimension minus the last one is the count of quadrics that no family
    explains.
    """
    products_float = products.astype(np.float64)
    functions: list[tuple[Callable[[Array], Array], int]] = [
        (plucker_relations, PLUCKER_QUADRICS),
        (linear_forms_times_coordinates(forms), forms.shape[0] * BIVECTORS),
        (wedge_with_product_image, len(TRIPLES)),
        (product_image_pairs, SYMMETRIC_COEFFICIENTS),
        (bivector_matrix_block_product_image, IMAGINARY * IMAGINARY),
        (bivector_matrix_block_bivector_matrix, IMAGINARY * BIVECTORS),
        (bivector_matrix_form_bivector_matrix(betas), len(betas) * SYMMETRIC_COEFFICIENTS),
        (bivector_matrix_form_bivector_matrix(DOUBLING_FORMS), len(DOUBLING_FORMS) * SYMMETRIC_COEFFICIENTS),
    ]
    rows: list[dict[str, Any]] = []
    vanishing: list[Array] = []
    for name, (function, count) in zip(FAMILY_NAMES, functions, strict=True):
        family = quadric_coefficients(function, count) if count else np.zeros((0, QUADRIC_COEFFICIENTS), dtype=np.int64)
        vanishing.append(annihilating_combinations(family, products_float))
        rows.append(
            {
                "name": name,
                "written": count,
                "rank": matrix_rank(family),
                "vanishing": matrix_rank(vanishing[-1]),
            }
        )
    stacked = np.concatenate(vanishing)
    pivots = independent_rows(stacked)
    stop = 0
    for row, block in zip(rows, vanishing, strict=True):
        stop += block.shape[0]
        row["cumulative"] = prefix_rank(pivots, stop)
    before_doubling = stacked[: stop - vanishing[-1].shape[0]]
    return rows, annihilator - len(pivots), character_split(products, [before_doubling, stacked])


def stratum_record(stratum: str) -> dict[str, Any]:
    """Every tally of one stratum: spans, quadric rank, product classes, forms and families."""
    planes = parallel.ordered_map(three_plane, [(stratum, number) for number in range(PLANES)], min_items=2)
    kernels = np.array([kernel for kernel, _, _ in planes], dtype=np.int64)
    classes = Counter(json.dumps(product) for _, product, _ in planes)
    form_ranks = Counter(json.dumps(ranks) for _, _, ranks in planes)
    forms = linear_forms_vanishing(wedge(kernels[:, [0, 0, 1]], kernels[:, [1, 2, 2]]))
    betas = symmetric_forms_vanishing(kernels)
    rank_record, products = quadric_rank_record(stratum, kernels)
    families, unexplained, characters = family_tallies(products, forms, betas, rank_record["annihilator"])
    return {
        "planes": PLANES,
        "spans": spans(kernels),
        "quadric_rank": rank_record,
        "product_classes": [[*json.loads(key), count] for key, count in sorted(classes.items())],
        "doubling_form_ranks": [[*json.loads(key), count] for key, count in sorted(form_ranks.items())],
        "linear_forms": int(forms.shape[0]),
        "forms_and_mu_rank": matrix_rank(np.concatenate([forms, MU])),
        "symmetric_forms": len(betas),
        "forms_with_quadric_rank": matrix_rank(np.array([beta.ravel() for beta in [*betas, quadric_polar_form()]])),
        "families": families,
        "unexplained": unexplained,
        "characters": characters,
    }


def _inputs() -> dict[str, str]:
    """The sha256 of every file whose bytes define the points, the blocks or this computation."""
    return {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in SOURCE_PATHS}


def compute() -> dict[str, Any]:
    """The whole record: calibration, the rank of mu and the rows of the three strata, with the verdict."""
    # Each stratum holds about 3.4 GiB of matrices at its peak, so min_items above the count of strata sends the loop
    # over them down the serial path of parallel.ordered_map; the loops over independent points inside a stratum
    # take its pool.
    strata = parallel.ordered_map(stratum_record, list(STRATA), min_items=len(STRATA) + 1)
    record: dict[str, Any] = {
        "schema": SCHEMA,
        "field": FIELD,
        "inputs": _inputs(),
        "mu_rank": matrix_rank(MU),
        "quadric_is_norm": bool((quadric_polar_form() == 2 * np.eye(IMAGINARY, dtype=np.int64)).all()),
        "calibration": calibration(),
        "family_ranks": family_ranks(),
        "fixtures": fixture_classes(),
        "strata": dict(zip(STRATA, strata, strict=True)),
        "pass": True,
    }
    record["pass"] = verdict(record) == []
    return record


def expected_record() -> dict[str, Any]:
    """The record that the constants of this module determine, with the digests of the files as they are."""
    strata = {}
    for stratum in STRATA:
        annihilator = EXPECTED[stratum]["quadrics_vanishing"]
        rank = QUADRIC_COEFFICIENTS - annihilator
        strata[stratum] = {
            "planes": PLANES,
            "spans": dict(SPANS[stratum]),
            "quadric_rank": {
                "vectors": 6 * PLANES,
                "rank": rank,
                "annihilator": annihilator,
                "planes_below": rank // 6,
                "rank_below": 6 * (rank // 6),
                "rank_above": rank,
                "retained_planes": RETAINED_PLANES,
                "retained_rank": rank,
                "retained_rank_first": rank,
                "retained_rank_stacked": rank,
                "fixture_planes": FIXTURE_PLANES[stratum],
                "rank_with_fixtures": rank,
            },
            "product_classes": [list(row) for row in PRODUCT_CLASSES[stratum]],
            "doubling_form_ranks": [list(row) for row in DOUBLING_FORM_RANKS[stratum]],
            "linear_forms": FORM_COUNTS[stratum]["linear_forms"],
            "forms_and_mu_rank": MU_RANK,
            "symmetric_forms": FORM_COUNTS[stratum]["symmetric_forms"],
            "forms_with_quadric_rank": FORMS_WITH_QUADRIC_RANK,
            "families": [
                {"name": name, "written": written, "rank": rank_, "vanishing": vanishing, "cumulative": cumulative}
                for name, (written, rank_, vanishing, cumulative) in zip(
                    FAMILY_NAMES, FAMILY_TALLIES[stratum], strict=True
                )
            ],
            "unexplained": UNEXPLAINED[stratum],
            "characters": [list(row) for row in CHARACTER_TALLIES[stratum]],
        }
    return {
        "schema": SCHEMA,
        "field": FIELD,
        "inputs": _inputs(),
        "mu_rank": MU_RANK,
        "quadric_is_norm": True,
        "calibration": dict(CALIBRATION),
        "family_ranks": dict(FAMILY_RANKS),
        "fixtures": [list(row) for row in FIXTURE_CLASSES],
        "strata": strata,
        "pass": True,
    }


def _shape(value: Any) -> Any:
    """The fields and value types of a record: keys of every mapping, lengths of every list, type names of leaves."""
    if isinstance(value, dict):
        return {str(key): _shape(item) for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))}
    if isinstance(value, list):
        return [_shape(item) for item in value]
    return type(value).__name__


def _rank_problems(stratum: str, found: dict[str, Any]) -> list[str]:
    """The rules on the rank of the product vectors, its saturation and the retained sampler."""
    problems = []
    rank = found.get("rank")
    if found.get("vectors") != 6 * PLANES:
        problems.append(f"{stratum}: the product vectors are not six per three-plane")
    if rank != QUADRIC_COEFFICIENTS - EXPECTED[stratum]["quadrics_vanishing"]:
        problems.append(f"{stratum}: the quadric rank differs from the retained producer's expected value")
    if found.get("annihilator") != EXPECTED[stratum]["quadrics_vanishing"]:
        problems.append(f"{stratum}: the annihilator dimension differs from the retained producer's expected value")
    if not isinstance(rank, int) or found.get("planes_below") != rank // 6:
        problems.append(f"{stratum}: the saturation reads at another count of three-planes")
    elif (found.get("rank_below"), found.get("rank_above")) != (6 * (rank // 6), rank):
        problems.append(f"{stratum}: the sample is less general than six vectors per three-plane allow")
    if found.get("retained_planes") != RETAINED_PLANES:
        problems.append(f"{stratum}: the retained sampler reads another count of planes")
    if (found.get("retained_rank"), found.get("retained_rank_first"), found.get("retained_rank_stacked")) != (
        rank,
    ) * 3:
        problems.append(f"{stratum}: the retained planes do not span the same quadrics as the three-planes")
    if (found.get("fixture_planes"), found.get("rank_with_fixtures")) != (FIXTURE_PLANES[stratum], rank):
        problems.append(f"{stratum}: the exact fixtures do not lie on the quadrics of the three-planes")
    return problems


def _family_problems(stratum: str, found: dict[str, Any]) -> list[str]:
    """The rules on the quadric families and the count of quadrics that none of them explains."""
    problems = []
    families = found.get("families", [])
    if [family.get("name") for family in families] != list(FAMILY_NAMES):
        problems.append(f"{stratum}: the families differ from the stated list")
    tallies = [
        (family.get("written"), family.get("rank"), family.get("vanishing"), family.get("cumulative"))
        for family in families
    ]
    if tallies != FAMILY_TALLIES[stratum]:
        problems.append(f"{stratum}: the family tallies differ")
    if any(vanishing > rank for _, rank, vanishing, _ in tallies):
        problems.append(f"{stratum}: a family meets the annihilator in more than its rank")
    cumulative = [tally[3] for tally in tallies]
    if cumulative != sorted(cumulative):
        problems.append(f"{stratum}: the cumulative rank decreases")
    if tallies and (tallies[0][1], tallies[0][2]) != (PLUCKER_QUADRICS, PLUCKER_QUADRICS):
        problems.append(f"{stratum}: the Plucker quadrics do not all vanish on the image")
    for index in ALWAYS_VANISHING:
        if index < len(tallies) and tallies[index][1] != tallies[index][2]:
            problems.append(f"{stratum}: a family that vanishes on every three-plane does not")
    annihilator = EXPECTED[stratum]["quadrics_vanishing"]
    if found.get("unexplained") != UNEXPLAINED[stratum] or (
        cumulative and cumulative[-1] != annihilator - UNEXPLAINED[stratum]
    ):
        problems.append(f"{stratum}: the count of unexplained quadrics differs")
    characters = found.get("characters", [])
    sums = [sum(row[index] for row in characters) for index in range(4)]
    if sums != [QUADRIC_COEFFICIENTS, annihilator, *cumulative[-2:]]:
        problems.append(f"{stratum}: the quadrics do not split by the characters of the sign group")
    if characters != CHARACTER_TALLIES[stratum]:
        problems.append(f"{stratum}: the quadrics fall in other characters")
    if cumulative and cumulative[-1] > annihilator:
        problems.append(f"{stratum}: the families explain more quadrics than the annihilator holds")
    return problems


def _stratum_problems(stratum: str, found: dict[str, Any]) -> list[str]:
    """The rules on the rows of one stratum."""
    problems = []
    if found.get("planes") != PLANES:
        problems.append(f"{stratum}: the sample is not {PLANES} three-planes")
    if found.get("spans") != SPANS[stratum]:
        problems.append(f"{stratum}: the spans of K, S^2 K, Lambda^2 K and Lambda^3 K differ")
    if found.get("product_classes") != PRODUCT_CLASSES[stratum]:
        problems.append(f"{stratum}: the classes of the product on K differ")
    if found.get("doubling_form_ranks") != DOUBLING_FORM_RANKS[stratum]:
        problems.append(f"{stratum}: the ranks of the norm and the doubling forms on K differ")
    if {name: found.get(name) for name in FORM_COUNTS[stratum]} != FORM_COUNTS[stratum]:
        problems.append(f"{stratum}: the counts of linear and symmetric forms differ")
    if found.get("forms_with_quadric_rank") != FORMS_WITH_QUADRIC_RANK:
        problems.append(f"{stratum}: a symmetric form vanishing on every K is not a multiple of the polar form of Q")
    if found.get("forms_and_mu_rank") != MU_RANK or found.get("linear_forms") not in (0, MU_RANK):
        problems.append(f"{stratum}: the linear forms do not span the rows of mu")
    return [*problems, *_rank_problems(stratum, found.get("quadric_rank", {})), *_family_problems(stratum, found)]


def verdict(record: dict[str, Any]) -> list[str]:
    """The reasons the record fails its own rules; empty when it passes.

    The rules below read fields by name and compare with `==`, under which True equals 1 and 15.0 equals 15, so the
    comparison of fields and value types with the expected record comes first and ends the verdict on a difference;
    past it every field exists with the type the rules assume.
    """
    expected = expected_record()
    if _shape(record) != _shape(expected):
        return ["the record has other fields or value types than the record the constants determine"]
    problems = []
    if (record.get("schema"), record.get("field")) != (SCHEMA, FIELD):
        problems.append("the record is headed otherwise")
    if record.get("inputs") != _inputs():
        problems.append("the input digests differ from the files")
    if record.get("pass") is not True:
        problems.append("the record states that it fails")
    if record.get("mu_rank") != MU_RANK:
        problems.append("mu has another rank than 15")
    if record.get("quadric_is_norm") is not True:
        problems.append("Q is not the sum of the squares of the frame coordinates")
    if record.get("calibration") != CALIBRATION:
        problems.append("the squares of general decomposable bivectors do not leave exactly the Plucker quadrics")
    if record.get("family_ranks") != FAMILY_RANKS:
        problems.append("the Plucker, block product and norm families have other ranks")
    if record.get("fixtures") != FIXTURE_CLASSES:
        problems.append("the exact fixtures have other classes of the product and the forms on K")
    for stratum in STRATA:
        problems.extend(_stratum_problems(stratum, record["strata"][stratum]))
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
    for stratum, found in record["strata"].items():
        print(stratum, "quadric rank", found["quadric_rank"]["rank"], "unexplained", found["unexplained"])


if __name__ == "__main__":
    main()
