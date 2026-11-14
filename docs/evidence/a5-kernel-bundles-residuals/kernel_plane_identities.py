"""Exact identities on the kernel plane K(z) of the nullity-4 points: one square, null slice, product on K.

V is the 15-dimensional space of imaginary elements of the sedenions S = O + O e_8 (the Cayley-Dickson double of the
octonions O), with coordinates t_1, ..., t_15 in the frame of `gauss_image_quadrics.py`. M(z) v = Im(z v) is the
skew block of the bordered matrix (`kernel_three_plane_zero_divisors._exact_block` at a point of Q(i)^15) and K(z) =
ker M(z). The doubling forms are N1 = t_1^2 + ... + t_7^2, N2 = t_8^2 and N3 = t_9^2 + ... + t_15^2 with polar
forms N1(u, v), N2(u, v), N3(u, v); Q = N1 + N2 + N3 and G = Q^2 - 4 (N1 N3 - p^2) with p = t_1 t_9 + ... + t_7 t_15.
At a nullity-4 point dim K(z) = 3, and the statements below concern these three-planes K(z).

The record holds four groups of exact computations.

1. Four families of points over function fields (`families`), each a polynomial parametrization of a slice of V(G),
   V(Q) or V(Q) n V(G). The frame point is z = (m e_1, beta + lambda e_1 + w) with t_1 = m, t_8 = beta and
   t_9, ..., t_15 the coordinates of lambda e_1 + w, where w = s e_2 for the first three families. A basis of K(z)
   comes from the nullspace of M(z) over the field Q(i)(generators):
   - `FG+`  (m, u): (beta, lambda, s - m) = (u^2 - 1, i (u^2 + 1), 2u), so Q = 2 m s and G = 0.
   - `FG-`  (m, u): the same with s + m in place of s - m, so Q = -2 m s and G = 0.
   - `FQ`   (A, B, C): m = A C + B, beta = A B - C, lambda = -i (A B + C), s = -i (A C - B), so Q = 0 and G =
     -4 m^2 s^2.
   - `FQG`  (u): m = 2u, beta = u^2 - 1, lambda = i (u^2 + 1) and w = x + xi, where x and xi are null eigenvectors
     of the left multiplication by e_1 with eigenvalues i and -i, so Q = G = 0.
   Every test is a zero test of an element of the field, which is a decision procedure for the rational functions.
   Per family the record holds the generators, Q and G factored, and the rank of M(z); on `FG+` and `FG-` whether
   N_i(z) N_j(k, k') = N_i(k, z) N_j(k', z) for all i, j and basis vectors k, k' of K(z) (`one_square_identity`),
   and for the slice K0 = K(z) n ker N1(., z), cut out by the first basis vector at which N1(., z) is nonzero, whether
   t_8 vanishes on K0, whether N1, N2, N3 vanish on pairs of K0, whether N1, N2, N3 pair K0 with z to zero and whether
   c d'' + c'' d' vanishes (octonion products) for vectors (c, d') and (c'', d'') of K0 with c = t_1..t_7 and
   d' = t_9..t_15; on `FQ`
   whether every product M(k) k' of basis vectors is a multiple of z, whether some product is not identically zero
   and whether z lies in K(z); on `FQG` whether every product M(k) k' vanishes.
2. The derivation algebra of the octonions solved from the `cd_core` product table over Q(i) (`derivations`):
   its dimension and the ranks of D -> (D e_1, D e_2) and D -> (D e_1, D w0), w0 = x + xi the null vector of `FQG`.
   In characteristic 0 a rank is the dimension of the orbit of the Lie algebra's group, so 11 is the dimension of
   the orbit of the pair (e_1, e_2) and of (e_1, w0) under Aut(O) = G2.
3. One exact point z of V(G) minus V(Q) with N1(z) = 0 (`counterexample`), the values of Q, G, N1, t_8 and N3 at z,
   dim K(z), whether z lies in K(z), whether N1(., z) vanishes on K(z) and whether the one-square identity holds
   there.
4. The 66 exact fixtures of `nullity4-kernel-gauss-result.json` (`fixtures`), per stratum: the count, the count
   with dim K(z) = 3, the count at which the one-square identity holds, the count at which every product M(k) k' of
   basis vectors is a multiple of z, the count at which every such product vanishes, the count at which the
   null-slice statement of `null_slice_statement` holds and the count with t_8(z) = 0.

`verdict` first compares the fields and value types of a record with those of the record that the constants of
this module determine and stops there on a difference, then applies the rules by name, and last compares the
serialized text of the two records; apart from the input digests a record passes exactly when it is that record.

The four families run through `parallel.ordered_map`, one family per item, and so do the fixtures.

`--write` writes kernel-plane-identities-result.json beside this file; `--check` recomputes and compares.

Run from the repository root:
"$PYTHON" docs/evidence/a5-kernel-bundles-residuals/kernel_plane_identities.py --check
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
from sympy import QQ_I, I
from sympy.polys.matrices import DomainMatrix

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BUNDLES = HERE.parent / "a5-kernel-bundles"
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(BUNDLES))

from kernel_three_plane_zero_divisors import _exact_block, _exact_kernel  # noqa: E402
from nullity4_gauss_image import FIXTURES, STRATA, _fixture_splits  # noqa: E402

import cd_core  # noqa: E402
import parallel  # noqa: E402

SCHEMA = "a5-kernel-bundles-residuals-kernel-plane-identities-v1"
RECORD = HERE / "kernel-plane-identities-result.json"
SOURCE_PATHS = (
    HERE / "kernel_plane_identities.py",
    HERE / "gauss_image_quadrics.py",
    HERE / "nullity4_gauss_image.py",
    HERE / "kernel_three_plane_zero_divisors.py",
    FIXTURES,
    ROOT / "gororoba_quantum" / "cd_core.py",
)
FIELD = "Q(i)"

IMAGINARY = 15
# N1, N2, N3 sum the products of coordinates 1 to 7, 8 and 9 to 15 (one-based, inclusive).
DOUBLING_RANGES = ((1, 7), (8, 8), (9, 15))
FAMILY_NAMES = ("FG+", "FG-", "FQ", "FQG")
GENERATORS = {"FG+": ["m", "u"], "FG-": ["m", "u"], "FQ": ["A", "B", "C"], "FQG": ["u"]}
# Q and G of each family, factored, and the rank of M(z) over the function field (dim K(z) = 3).
FAMILY_QUADRIC = {"FG+": "2*m*(m + 2*u)", "FG-": "-2*m*(-m + 2*u)", "FQ": "0", "FQG": "0"}
FAMILY_QUARTIC = {"FG+": "0", "FG-": "0", "FQ": "4*(A*C - B)**2*(A*C + B)**2", "FQG": "0"}
FAMILY_RANK = 12
# The statements that hold on each family, by field name, with the rule that reads them.
SLICE_STATEMENTS = (
    "one_square_identity",
    "slice_t8_zero",
    "slice_forms_zero",
    "slice_pairs_with_point_zero",
    "slice_octonion_product_zero",
)
FAMILY_STATEMENTS = {
    "FG+": SLICE_STATEMENTS,
    "FG-": SLICE_STATEMENTS,
    "FQ": ("product_is_multiple_of_point", "product_not_identically_zero", "point_in_kernel"),
    "FQG": ("product_zero",),
}
STATEMENT_RULES = {
    "one_square_identity": "the one-square identity fails on K",
    "slice_t8_zero": "t_8 does not vanish on the slice K0",
    "slice_forms_zero": "N1, N2 or N3 does not vanish on a pair of the slice K0",
    "slice_pairs_with_point_zero": "N1, N2 or N3 does not pair the slice K0 with z to zero",
    "slice_octonion_product_zero": "the octonion product c d'' + c'' d' does not vanish on the slice K0",
    "product_is_multiple_of_point": "a product M(k) k' on K is not a multiple of z",
    "product_not_identically_zero": "every product M(k) k' on K vanishes",
    "point_in_kernel": "z is not in K(z)",
    "product_zero": "a product M(k) k' on K does not vanish",
}
# Der(O) and the ranks of D -> (D e_1, D e_2) and D -> (D e_1, D w0).
DERIVATIONS = {"dimension": 14, "rank_e1_e2": 11, "rank_e1_w0": 11}
DERIVATION_RULES = {
    "dimension": "the derivation algebra of the octonions has another dimension than 14",
    "rank_e1_e2": "the orbit of (e_1, e_2) has another dimension than 11",
    "rank_e1_w0": "the orbit of (e_1, w0) has another dimension than 11",
}
# The point of V(G) minus V(Q) with N1(z) = 0, as sympy source over Q(i), and what holds there.
COUNTEREXAMPLE_POINT = ["0", "1", "I", "0", "0", "0", "0", "2*I", "-2", "0", "-2", "0", "0", "0", "0"]
COUNTEREXAMPLE: dict[str, Any] = {
    "point": COUNTEREXAMPLE_POINT,
    "Q": "4",
    "G": "0",
    "N1": "0",
    "N3": "8",
    "t8": "2*I",
    "kernel_dimension": 3,
    "point_in_kernel": True,
    "n1_pairing_zero_on_kernel": True,
    "one_square_identity": True,
}
COUNTEREXAMPLE_RULES = {
    "point": "the counterexample point differs",
    "Q": "Q does not equal 4 at the counterexample",
    "G": "G does not vanish at the counterexample",
    "N1": "N1 does not vanish at the counterexample",
    "N3": "N3 does not equal 8 at the counterexample",
    "t8": "t_8 does not equal 2 i at the counterexample",
    "kernel_dimension": "K(z) at the counterexample is not a three-plane",
    "point_in_kernel": "z is not in K(z) at the counterexample",
    "n1_pairing_zero_on_kernel": "N1(., z) does not vanish on K(z) at the counterexample",
    "one_square_identity": "the one-square identity fails at the counterexample",
}
# Per stratum: fixtures, those with dim K(z) = 3, with the one-square identity (all inside V(G), none on V(Q) minus
# V(G)), with every product M(k) k' a multiple of z (all of V(Q) minus V(G) and of V(Q) n V(G)), with every
# product zero, with the null-slice statement (all inside V(G), none on V(Q) minus V(G)) and with t_8(z) = 0.
FIXTURE_COUNTS = {
    STRATA[0]: {
        "fixtures": 12,
        "kernel_dimension_three": 12,
        "one_square_identity": 0,
        "product_multiple_of_point": 12,
        "product_zero": 0,
        "null_slice_statement": 0,
        "point_t8_zero": 3,
    },
    STRATA[1]: {
        "fixtures": 52,
        "kernel_dimension_three": 52,
        "one_square_identity": 52,
        "product_multiple_of_point": 0,
        "product_zero": 0,
        "null_slice_statement": 52,
        "point_t8_zero": 37,
    },
    STRATA[2]: {
        "fixtures": 2,
        "kernel_dimension_three": 2,
        "one_square_identity": 2,
        "product_multiple_of_point": 2,
        "product_zero": 2,
        "null_slice_statement": 2,
        "point_t8_zero": 2,
    },
}
FIXTURE_RULES = {
    "fixtures": "the fixtures of the stratum differ from the pinned count",
    "kernel_dimension_three": "a fixture has a kernel that is not a three-plane",
    "one_square_identity": "the one-square identity does not hold exactly at the fixtures inside V(G)",
    "product_multiple_of_point": "the products M(k) k' are not multiples of z at the pinned fixtures",
    "product_zero": "the products M(k) k' vanish at other fixtures than the pinned ones",
    "null_slice_statement": "the null-slice statement does not hold exactly at the fixtures inside V(G)",
    "point_t8_zero": "t_8 vanishes at the point of other fixtures than the pinned ones",
}

OCTONION = [[int(cd_core.cd_sign(8, i, j)) for j in range(8)] for i in range(8)]
SEDENION = [[int(cd_core.cd_sign(16, i, j)) for j in range(16)] for i in range(16)]


def _require(condition: bool, message: str) -> None:
    """Raise when an internal invariant fails; unlike `assert` it survives `python -O`."""
    if not condition:
        raise RuntimeError(message)


def block(point: Sequence[Any], zero: Any) -> list[list[Any]]:
    """M(z) over the ring that holds the coordinates, `zero` being its zero: the entry (r, c) is the sign of
    e_(r xor c) e_c times t_(r xor c) and the diagonal is zero, so M(z) v is the imaginary part of z v."""
    frame = [zero, *point]
    return [
        [zero if row == column else SEDENION[row ^ column][column] * frame[row ^ column] for column in range(1, 16)]
        for row in range(1, 16)
    ]


def apply(matrix: Sequence[Sequence[Any]], vector: Sequence[Any], zero: Any) -> list[Any]:
    """The product of a matrix and a vector over the ring of `zero`."""
    return [sum((entry * value for entry, value in zip(row, vector, strict=True)), zero) for row in matrix]


def form(index: int, first: Sequence[Any], second: Sequence[Any], zero: Any) -> Any:
    """The polar form N1(u, v), N2(u, v) or N3(u, v) of the doubling form `index`."""
    low, high = DOUBLING_RANGES[index]
    return sum((first[k] * second[k] for k in range(low - 1, high)), zero)


def octonion_product(first: Sequence[Any], second: Sequence[Any], zero: Any) -> list[Any]:
    """The octonion product of two lists of 8 coordinates over the ring of `zero`."""
    product = [zero] * 8
    for i in range(8):
        for j in range(8):
            product[i ^ j] = product[i ^ j] + OCTONION[i][j] * first[i] * second[j]
    return product


def one_square_identity(point: Sequence[Any], kernel: Sequence[Sequence[Any]], zero: Any) -> bool:
    """N_i(z) N_j(k, k') = N_i(k, z) N_j(k', z) for all i, j and all pairs of the basis vectors of K(z).

    Both sides are bilinear in (k, k'), so the identity on a basis is the identity on K(z).
    """
    return all(
        form(i, point, point, zero) * form(j, first, second, zero)
        == form(i, first, point, zero) * form(j, second, point, zero)
        for i in range(3)
        for j in range(3)
        for first in kernel
        for second in kernel
    )


def products_on_kernel(kernel: Sequence[Sequence[Any]], zero: Any) -> list[list[Any]]:
    """M(k) k' for every ordered pair of basis vectors of K(z)."""
    return [apply(block(first, zero), second, zero) for first in kernel for second in kernel]


def multiple_of_point(vectors: Sequence[Sequence[Any]], point: Sequence[Any]) -> bool:
    """Every vector is proportional to z: all 2 x 2 minors of the vector against z vanish."""
    return all(
        not (vector[r] * point[c] - vector[c] * point[r])
        for vector in vectors
        for r in range(IMAGINARY)
        for c in range(r + 1, IMAGINARY)
    )


def null_eigenvector(index: int, value: Any) -> list[Any]:
    """The null eigenvector e_j + c e_j' of the left multiplication by e_1 on span(e_j, e_j'), j' = j xor 1.

    With e_1 e_j = sigma e_j' the eigenvalue i takes c = -i sigma and the eigenvalue -i takes c = i sigma, and
    e_1 e_j' = -sigma e_j.
    """
    sigma, partner = OCTONION[1][index], 1 ^ index
    vector: list[Any] = [0] * 7
    vector[index - 1] = 1
    vector[partner - 1] = -I * sigma if value == I else I * sigma
    image = octonion_product([0, 1, 0, 0, 0, 0, 0, 0], [0, *vector], 0)[1:]
    _require(all(sp.expand(x - value * y) == 0 for x, y in zip(image, vector, strict=True)), "not an eigenvector")
    _require(sp.expand(sum(x * x for x in vector)) == 0, "the eigenvector is not null")
    return vector


def null_pair() -> list[Any]:
    """x + xi, the sum of the null eigenvectors of eigenvalues i (on e_2, e_3) and -i (on e_4, e_5)."""
    return [p + q for p, q in zip(null_eigenvector(2, I), null_eigenvector(4, -I), strict=True)]


def family_point(name: str) -> tuple[list[sp.Expr], tuple[sp.Symbol, ...]]:
    """The frame point of a family as polynomials in its generators, and the generators."""
    m, u, a, b, c = sp.symbols("m u A B C")

    def point(mm: Any, beta: Any, lam: Any, w: Sequence[Any]) -> list[sp.Expr]:
        return [mm, 0, 0, 0, 0, 0, 0, beta, sp.expand(lam + w[0]), *w[1:]]

    def e2(s: Any) -> list[Any]:
        return [0, s, 0, 0, 0, 0, 0]

    if name == "FG+":
        return point(m, u**2 - 1, I * (u**2 + 1), e2(m + 2 * u)), (m, u)
    if name == "FG-":
        return point(m, u**2 - 1, I * (u**2 + 1), e2(-m + 2 * u)), (m, u)
    if name == "FQ":
        # (beta + i lambda)(beta - i lambda) = -(m + i s)(m - i s) with beta + i lambda = A B, beta - i lambda =
        # -C, m + i s = A C and m - i s = B, scaled by 2 to clear denominators.
        return point(a * c + b, a * b - c, -I * (a * b + c), e2(-I * (a * c - b))), (a, b, c)
    _require(name == "FQG", "an unknown family")
    return point(2 * u, u**2 - 1, I * (u**2 + 1), null_pair()), (u,)


def null_slice(kernel: Sequence[Sequence[Any]], point: Sequence[Any], zero: Any) -> list[list[Any]]:
    """A basis of K0 = K(z) n ker N1(., z) from a basis of K(z).

    With l_i = N1(k_i, z) and the first index p of a nonzero l_p, the vectors k_i - (l_i / l_p) k_p, i != p, span K0.
    When every l_i vanishes the slice is K(z) itself.
    """
    pairings = [form(0, k, point, zero) for k in kernel]
    pivot = next((index for index, value in enumerate(pairings) if value), None)
    if pivot is None:
        return [list(k) for k in kernel]
    return [
        [x - pairings[i] / pairings[pivot] * y for x, y in zip(kernel[i], kernel[pivot], strict=True)]
        for i in range(len(kernel))
        if i != pivot
    ]


def octonion_pairs_vanish(basis: Sequence[Sequence[Any]], zero: Any) -> bool:
    """c d'' + c'' d' = 0 for all vectors (c, d') and (c'', d'') of the basis, c = t_1..t_7 and d' = t_9..t_15."""
    return all(
        not (x + y)
        for k in basis
        for kk in basis
        for x, y in zip(
            octonion_product([zero, *k[:7]], [zero, *kk[8:]], zero),
            octonion_product([zero, *kk[:7]], [zero, *k[8:]], zero),
            strict=True,
        )
    )


def null_slice_statement(point: Sequence[Any], kernel: Sequence[Sequence[Any]], zero: Any) -> bool:
    """The null-slice statement at a point z with the kernel basis of K(z), with l = N1(., z) the pairing with z.

    N1(z) is nonzero, l is nonzero on K(z), and N1 on K(z) is a multiple of l^2 (every row of the Gram matrix of N1
    is proportional to the vector of the values of l on the basis). On K0 = K(z) n ker l (`null_slice`) t_8 vanishes,
    N1 and N3 vanish on pairs, and c d'' + c'' d' vanishes (`octonion_pairs_vanish`). With N2 = t_8^2 the one-square
    identity reads N1(z) t_8(k) t_8(k') = N1(k, z) z_8 t_8(k'), so t_8 vanishes on all of K(z) exactly when z_8 = 0.
    """
    pairings = [form(0, k, point, zero) for k in kernel]
    if not (form(0, point, point, zero) and any(pairings)):
        return False
    gram = [[form(0, first, second, zero) for second in kernel] for first in kernel]
    count = range(len(kernel))
    if any(pairings[i] * row[j] - pairings[j] * row[i] for row in gram for i in count for j in count):
        return False
    if any(k[7] for k in kernel) != bool(point[7]):
        return False
    cut = null_slice(kernel, point, zero)
    return (
        all(not k[7] for k in cut)
        and all(not form(j, k, kk, zero) for k in cut for kk in cut for j in (0, 2))
        and octonion_pairs_vanish(cut, zero)
    )


def family_record(name: str) -> dict[str, Any]:
    """The exact record of one family over Q(i)(generators); see the module docstring."""
    polynomials, generators = family_point(name)
    field = QQ_I.frac_field(*generators)
    zero = field.zero
    point = [field.from_sympy(sp.expand(x)) for x in polynomials]
    sums = [sp.expand(sum(x * x for x in polynomials[low - 1 : high])) for low, high in DOUBLING_RANGES]
    pairing = sp.expand(sum(polynomials[k] * polynomials[k + 8] for k in range(7)))
    norm = sp.expand(sum(sums))
    quartic = sp.expand(norm**2 - 4 * (sums[0] * sums[2] - pairing**2))
    matrix = DomainMatrix([[field.convert(x) for x in row] for row in block(point, zero)], (15, 15), field)
    kernel = matrix.nullspace().to_list()
    record: dict[str, Any] = {
        "generators": [str(g) for g in generators],
        "Q": str(sp.factor(norm)),
        "G": str(sp.factor(quartic)),
        "rank": IMAGINARY - len(kernel),
    }
    if name in ("FG+", "FG-"):
        record["one_square_identity"] = one_square_identity(point, kernel, zero)
        slice_basis = null_slice(kernel, point, zero)
        record["slice_t8_zero"] = all(not k[7] for k in slice_basis)
        record["slice_forms_zero"] = all(
            not form(j, k, kk, zero) for k in slice_basis for kk in slice_basis for j in range(3)
        )
        record["slice_pairs_with_point_zero"] = all(not form(j, k, point, zero) for k in slice_basis for j in range(3))
        record["slice_octonion_product_zero"] = octonion_pairs_vanish(slice_basis, zero)
    else:
        products = products_on_kernel(kernel, zero)
        if name == "FQ":
            record["product_is_multiple_of_point"] = multiple_of_point(products, point)
            record["product_not_identically_zero"] = any(x for vector in products for x in vector)
            record["point_in_kernel"] = not any(apply(block(point, zero), point, zero))
        else:
            record["product_zero"] = not any(x for vector in products for x in vector)
    return record


def derivation_record() -> dict[str, int]:
    """The dimension of Der(O) over Q(i) from the cd_core table and the ranks of D -> (D e_1, D e_2) and (D e_1, D w0).

    The unknown D is an 8 x 8 matrix d[a][b] with D e_b = sum_a d[a][b] e_a. The equation D(e_i e_j) = (D e_i) e_j +
    e_i (D e_j) has, in coordinate r, the coefficients OCTONION[i][j] on d[r][i xor j], -OCTONION[r xor j][j] on
    d[r xor j][i] and -OCTONION[i][r xor i] on d[r xor i][j].
    """
    rows = []
    for i, j, r in itertools.product(range(8), repeat=3):
        row = [0] * 64
        row[r * 8 + (i ^ j)] += OCTONION[i][j]
        row[(r ^ j) * 8 + i] -= OCTONION[r ^ j][j]
        row[(r ^ i) * 8 + j] -= OCTONION[i][r ^ i]
        rows.append(row)
    system = DomainMatrix(rows, (len(rows), 64), QQ_I)
    basis = system.nullspace().to_list()
    w0 = [QQ_I.zero, *(QQ_I.from_sympy(sp.sympify(x)) for x in null_pair())]
    _require(sum((x * x for x in w0), QQ_I.zero) == QQ_I.zero and w0[1] == QQ_I.zero, "w0 is not null or meets e_1")

    def image_rank(vectors: Sequence[Sequence[Any]]) -> int:
        """Rank of D -> (D v_1, D v_2, ...) over the basis of the derivations."""
        images = []
        for d in basis:
            entries = [[d[a * 8 + b] for b in range(8)] for a in range(8)]
            images.append([x for v in vectors for x in apply(entries, v, QQ_I.zero)])
        return int(DomainMatrix(images, (len(images), 8 * len(vectors)), QQ_I).rank())

    unit = [[QQ_I.one if k == j else QQ_I.zero for k in range(8)] for j in range(8)]
    return {
        "dimension": len(basis),
        "rank_e1_e2": image_rank([unit[1], unit[2]]),
        "rank_e1_w0": image_rank([unit[1], w0]),
    }


def _text(value: Any) -> str:
    """The exact value of a Q(i) element as text."""
    return str(QQ_I.to_sympy(value))


def counterexample_record() -> dict[str, Any]:
    """The exact point z of V(G) minus V(Q) with N1(z) = 0 and the facts of the module docstring about it."""
    zero = QQ_I.zero
    point = [QQ_I.from_sympy(sp.sympify(x)) for x in COUNTEREXAMPLE_POINT]
    kernel = _exact_kernel(_exact_block(point))
    squares = [form(i, point, point, zero) for i in range(3)]
    pairing = sum((point[k] * point[k + 8] for k in range(7)), zero)
    norm = sum(squares, zero)
    return {
        "point": [_text(x) for x in point],
        "Q": _text(norm),
        "G": _text(norm * norm - 4 * (squares[0] * squares[2] - pairing * pairing)),
        "N1": _text(squares[0]),
        "N3": _text(squares[2]),
        "t8": _text(point[7]),
        "kernel_dimension": len(kernel),
        "point_in_kernel": not any(apply(_exact_block(point), point, zero)),
        "n1_pairing_zero_on_kernel": all(not form(0, k, point, zero) for k in kernel),
        "one_square_identity": one_square_identity(point, kernel, zero),
    }


def _frame(split: Sequence[int]) -> list[Any]:
    """The frame point t_k = i^popcount(k) t'_k of the split point t'."""
    unit = QQ_I.convert(I)
    return [unit ** (index + 1).bit_count() * QQ_I.convert(value) for index, value in enumerate(split)]


def fixture_row(job: tuple[int, str, list[int]]) -> list[Any]:
    """At one fixture: the stratum, dim K(z), and whether the one-square identity holds, whether every product
    M(k) k' of basis vectors is a multiple of z, whether every one vanishes, whether the null-slice statement holds
    (`null_slice_statement`) and whether z_8 = 0."""
    _, stratum, split = job
    zero = QQ_I.zero
    point = _frame(split)
    kernel = _exact_kernel(_exact_block(point))
    products = products_on_kernel(kernel, zero)
    return [
        stratum,
        len(kernel),
        one_square_identity(point, kernel, zero),
        multiple_of_point(products, point),
        not any(x for vector in products for x in vector),
        null_slice_statement(point, kernel, zero),
        not point[7],
    ]


def fixture_record() -> dict[str, dict[str, int]]:
    """Per stratum: the count of fixtures and of those with each property of `fixture_row`."""
    rows = parallel.ordered_map(fixture_row, _fixture_splits(), min_items=2)
    record = {}
    for stratum in STRATA:
        mine = [row for row in rows if row[0] == stratum]
        record[stratum] = {
            "fixtures": len(mine),
            "kernel_dimension_three": sum(row[1] == 3 for row in mine),
            "one_square_identity": sum(row[2] for row in mine),
            "product_multiple_of_point": sum(row[3] for row in mine),
            "product_zero": sum(row[4] for row in mine),
            "null_slice_statement": sum(row[5] for row in mine),
            "point_t8_zero": sum(row[6] for row in mine),
        }
    return record


def _inputs() -> dict[str, str]:
    """The sha256 of every file whose bytes define the points, the blocks or this computation."""
    return {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in SOURCE_PATHS}


def compute() -> dict[str, Any]:
    """The whole record: the four families, the derivations, the counterexample and the fixtures, with the verdict."""
    families = parallel.ordered_map(family_record, list(FAMILY_NAMES), min_items=2)
    record: dict[str, Any] = {
        "schema": SCHEMA,
        "field": FIELD,
        "inputs": _inputs(),
        "families": dict(zip(FAMILY_NAMES, families, strict=True)),
        "derivations": derivation_record(),
        "counterexample": counterexample_record(),
        "fixtures": fixture_record(),
        "pass": True,
    }
    record["pass"] = verdict(record) == []
    return record


def expected_record() -> dict[str, Any]:
    """The record that the constants of this module determine, with the digests of the files as they are."""
    families = {}
    for name in FAMILY_NAMES:
        families[name] = {
            "generators": list(GENERATORS[name]),
            "Q": FAMILY_QUADRIC[name],
            "G": FAMILY_QUARTIC[name],
            "rank": FAMILY_RANK,
            **dict.fromkeys(FAMILY_STATEMENTS[name], True),
        }
    return {
        "schema": SCHEMA,
        "field": FIELD,
        "inputs": _inputs(),
        "families": families,
        "derivations": dict(DERIVATIONS),
        "counterexample": {**COUNTEREXAMPLE, "point": list(COUNTEREXAMPLE_POINT)},
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


def _family_problems(name: str, found: dict[str, Any]) -> list[str]:
    """The rules on one family: its parametrization, Q, G, the rank of M(z) and the statements that hold on it."""
    problems = []
    if found["generators"] != GENERATORS[name]:
        problems.append(f"{name}: the generators differ")
    if found["Q"] != FAMILY_QUADRIC[name]:
        problems.append(f"{name}: Q differs from its factorization")
    if found["G"] != FAMILY_QUARTIC[name]:
        problems.append(f"{name}: G differs from its factorization")
    if found["rank"] != FAMILY_RANK:
        problems.append(f"{name}: M(z) has another rank than {FAMILY_RANK}")
    for field in FAMILY_STATEMENTS[name]:
        if found[field] is not True:
            problems.append(f"{name}: {STATEMENT_RULES[field]}")
    return problems


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
    if (record["schema"], record["field"]) != (SCHEMA, FIELD):
        problems.append("the record is headed otherwise")
    if record["inputs"] != _inputs():
        problems.append("the input digests differ from the files")
    if record["pass"] is not True:
        problems.append("the record states that it fails")
    for name in FAMILY_NAMES:
        problems.extend(_family_problems(name, record["families"][name]))
    for field, message in DERIVATION_RULES.items():
        if record["derivations"][field] != DERIVATIONS[field]:
            problems.append(message)
    for field, message in COUNTEREXAMPLE_RULES.items():
        if record["counterexample"][field] != COUNTEREXAMPLE[field]:
            problems.append(message)
    for stratum in STRATA:
        for field, message in FIXTURE_RULES.items():
            if record["fixtures"][stratum][field] != FIXTURE_COUNTS[stratum][field]:
                problems.append(f"{stratum}: {message}")
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
    print("pass", ", ".join(f"{name} rank {found['rank']}" for name, found in record["families"].items()))


if __name__ == "__main__":
    main()
