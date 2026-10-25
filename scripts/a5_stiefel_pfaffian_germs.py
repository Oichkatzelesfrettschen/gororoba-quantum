"""Exact Pfaffian proof of the universal A_5 Stiefel inclusion and the tangent-bound germs at the twelve gap witnesses.

For y = (p, q) in A_5 with p, q in Im A_4 (y_0 = y_16 = 0) put z = p + i q in C^15 (z_k = y_k + i y_(16+k)), where
i is a scalar unit and every dot product is complex bilinear; u = z_1..z_7, mu = z_8, v = z_9..z_15. C_z is the
Im-block of left multiplication by z on Im (A_4)_C, U = u.u, V = v.v, W = u.v, Q = U + mu^2 + V, Delta = U V - W^2 and
G = Q^2 - 4 Delta.

Identities checked coefficient by coefficient over Z[z, t] from cd_core.cd_sign:
- C_z is skew and C_z z = 0;
- P_j = (-1)^(j-1) Pf(C_z with row and column j removed) equals Q G z_j for j = 1..15;
- Pf A(z, t) = -(z.t) Q G for the bordered matrix A = [[0, -t^T], [t, C_z]].
For xi = r + i conj(s), with conj the Cayley-Dickson conjugation, L_y sends (r, s) to the vector whose xi is
A(z, conj z) applied to the coefficientwise conjugate of xi; checked on every imaginary basis element y and every
basis vector, so rank_R L_y = 2 rank_C A(z, conj z). Where Q(z) G(z) = 0 the 16 x 16 skew matrix A has zero
Pfaffian, so rank_C A <= 14 and nullity L_y >= 4. Q = 0 is the Stiefel condition |p| = |q|, <p, q> = 0, so every
nonzero A_5 Stiefel element is a zero divisor.

Cross-check route: for x in {(h, 0), (0, h) : h in 1, u, v, uv} the identity z (z x) = -Q x holds over Z[z], so on
Q = 0 left multiplication by z squares to zero on an 8-dimensional space wherever those eight vectors are
independent, which they are at one exact point of the irreducible quadric Q = 0.

Witness germs. At each of the twelve rank-locus witnesses with a non-zero-divisor entry the record computes, in
exact rational arithmetic, the nullity k, the Schur differential h -> N_l^T L_h N_r, its kernel T(x), whether
e_8 and e_24 lie in T(x), and dim T(x) cap H_5^perp. A smooth piece P of dimension dim T(x) through x inside
R_k = {rank L_y <= 32 - k} gives P = R_k = S_k as germs, because R_k lies near x in the Schur manifold of that
dimension.
- nonzd-nonzd-locus (Q = 0) and zd-nonzd-generic (G = 0): P is {y_0 = y_16 = 0, F(z) = 0} with F = Q or G; the
  real Jacobian of y_0, y_16, Re F, Im F has rank 4 at x, and P lies in R_4 by the Pfaffian identity.
- zd-nonzd-locus: P is the image of (X, s, k) -> s exp(D_X) z(k), where D_X runs over the octonion derivations acting
  on both halves and z(k) = ((1 + U k^2) u, -2 lambda U k, lambda (1 - U k^2) u + (1 + U k^2) n) is a polynomial curve
  through x with lambda = u.v / U and n = v - lambda u. rank C_(z(k)) <= 10 at 13 integer k bounds every order-12
  principal Pfaffian, a polynomial of degree <= 12 in k, to zero; automorphisms and scalars keep rank C_z; and the
  map has complex rank 11 at x, so its image contains a real 22-dimensional submanifold through x inside R_8.
- nonzd-axis: the quadric germ of rank_locus_quadric_germ; the record repeats the tangent and e_8, e_24 checks.

Falsifiers: a cofactor off Q G z_j, a failed transport or square-zero identity, a witness off its piece, a
Jacobian or orbit rank below the tangent dimension, a curve point of rank C_z above 10, e_8 or e_24 outside T(x),
or a nullity other than the family's refutes the argument where it occurs.

Usage:
    "$PYTHON" scripts/a5_stiefel_pfaffian_germs.py --out docs/evidence/a5-stiefel-pfaffian-germs/result.json
    "$PYTHON" scripts/a5_stiefel_pfaffian_germs.py --check docs/evidence/a5-stiefel-pfaffian-germs/result.json
    "$PYTHON" scripts/a5_stiefel_pfaffian_germs.py --self-test
"""

from __future__ import annotations

import argparse
import copy
import functools
import importlib.metadata
import json
import sys
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from fractions import Fraction
from math import lcm
from pathlib import Path
from typing import Any

import flint

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))
from rank_locus_local_dimension import witnesses  # noqa: E402

import parallel  # noqa: E402
from cd_core import cd_sign  # noqa: E402

SCHEMA = "a5-stiefel-pfaffian-germs-v1"
DIM = 32
HALF = 16
OCTONION = 8
IMAGINARY = HALF - 1
SEVEN = OCTONION - 1
# z_8 = mu is index 7 of z_1..z_15; e_8 and e_24 carry Re mu and Im mu.
MU = 7
H5 = (0, 8, 16, 24)
SIGNS8 = [[cd_sign(OCTONION, i, j) for j in range(OCTONION)] for i in range(OCTONION)]
SIGNS16 = [[cd_sign(HALF, i, j) for j in range(HALF)] for i in range(HALF)]
SIGNS32 = [[cd_sign(DIM, i, j) for j in range(DIM)] for i in range(DIM)]
LOCAL_DIMENSION_RECORD = ROOT / "docs" / "evidence" / "rank_locus_local_dimension" / "result.json"
# family -> (nullity, piece, cone dimension of the piece)
GAP_FAMILIES = {
    "nonzd-axis": (12, "quadric", 16),
    "zd-nonzd-locus": (8, "orbit", 22),
    "zd-nonzd-generic": (4, "quartic", 28),
    "nonzd-nonzd-locus": (4, "stiefel", 28),
}
DERIVATIONS = 14
# Order-12 principal Pfaffians of C_(z(k)) are polynomials of degree <= 12 in k, since z(k) has degree 2.
CURVE_POINTS = 13
CURVE_CROSS_RANK = 10
ORBIT_COMPLEX_RANK = 11
STIEFEL_CROSS_RANK = 12


def _require(ok: bool, message: str) -> None:
    if not ok:
        raise SystemExit(f"a5_stiefel_pfaffian_germs: {message}")


@dataclass(frozen=True)
class GQ:
    """A Gaussian rational re + i im."""

    re: Fraction
    im: Fraction

    def __add__(self, other: GQ) -> GQ:
        return GQ(self.re + other.re, self.im + other.im)

    def __sub__(self, other: GQ) -> GQ:
        return GQ(self.re - other.re, self.im - other.im)

    def __neg__(self) -> GQ:
        return GQ(-self.re, -self.im)

    def __mul__(self, other: GQ | int | Fraction) -> GQ:
        if isinstance(other, GQ):
            return GQ(self.re * other.re - self.im * other.im, self.re * other.im + self.im * other.re)
        return GQ(self.re * other, self.im * other)

    def __truediv__(self, other: GQ) -> GQ:
        norm = other.re * other.re + other.im * other.im
        product = self * other.conj()
        return GQ(product.re / norm, product.im / norm)

    def conj(self) -> GQ:
        return GQ(self.re, -self.im)

    def pair(self) -> list[str]:
        return [str(self.re), str(self.im)]


ZERO = GQ(Fraction(0), Fraction(0))
ONE = GQ(Fraction(1), Fraction(0))
I_UNIT = GQ(Fraction(0), Fraction(1))


def gq(value: int | Fraction) -> GQ:
    return GQ(Fraction(value), Fraction(0))


def dot(a: Sequence[Any], b: Sequence[Any], zero: Any) -> Any:
    total = zero
    for left, right in zip(a, b, strict=True):
        total = total + left * right
    return total


def cross(z: Sequence[Any], zero: Any, signs: list[list[int]]) -> list[list[Any]]:
    """C_z: entry (a - 1, b - 1) is the e_a coefficient of z e_b for imaginary a != b, sign(k, b) z_k at k = a ^ b."""
    return [[z[(a ^ b) - 1] * signs[a ^ b][b] if a != b else zero for b in range(1, HALF)] for a in range(1, HALF)]


def pfaffian_function(matrix: list[list[Any]], zero: Any, one: Any) -> Callable[[int], Any]:
    """Pf of the principal submatrix on a bit mask of indices, by expansion along its first index, memoized."""
    memo: dict[int, Any] = {0: one}

    def pf(mask: int) -> Any:
        if mask in memo:
            return memo[mask]
        indices = [i for i in range(len(matrix)) if mask >> i & 1]
        value = zero
        if len(indices) % 2 == 0:
            first = indices[0]
            for position, j in enumerate(indices[1:], start=1):
                entry = matrix[first][j]
                if entry == zero:
                    continue
                term = entry * pf(mask & ~(1 << first) & ~(1 << j))
                value = value + term if position % 2 else value - term
        memo[mask] = value
        return value

    return pf


def invariants(z: Sequence[Any], zero: Any) -> dict[str, Any]:
    u, mu, v = z[:SEVEN], z[MU], z[OCTONION:]
    big_u, big_v, big_w = dot(u, u, zero), dot(v, v, zero), dot(u, v, zero)
    q = big_u + mu * mu + big_v
    delta = big_u * big_v - big_w * big_w
    return {"U": big_u, "V": big_v, "W": big_w, "Q": q, "Delta": delta, "G": q * q - delta * 4}


def factorization(signs: list[list[int]], flip: tuple[int, int] | None = None) -> dict[str, Any]:
    """Skewness, C_z z = 0, the 15 cofactor identities P_j = Q G z_j and Pf A(z, t) = -(z.t) Q G over Z[z, t].

    flip = (a, b) negates the entries (a, b) and (b, a) of C_z, a mutation that keeps C_z skew.
    """
    names = [f"z{k}" for k in range(1, HALF)] + [f"t{k}" for k in range(1, HALF)]
    ring = flint.fmpz_mpoly_ctx.get(names, "lex")
    generators = list(ring.gens())
    z, t = generators[:IMAGINARY], generators[IMAGINARY:]
    zero, one = ring.from_dict({}), ring.from_dict({(0,) * len(names): 1})
    c = cross(z, zero, signs)
    if flip is not None:
        a, b = flip
        c[a][b], c[b][a] = -c[a][b], -c[b][a]
    skew = all(c[i][j] + c[j][i] == 0 for i in range(IMAGINARY) for j in range(IMAGINARY))
    annihilates = all(dot(c[i], z, zero) == 0 for i in range(IMAGINARY))
    pf = pfaffian_function(c, zero, one)
    full = (1 << IMAGINARY) - 1
    cofactors = [pf(full & ~(1 << j)) * (1 if j % 2 == 0 else -1) for j in range(IMAGINARY)]
    inv = invariants(z, zero)
    q, g = inv["Q"], inv["G"]
    bordered = [[zero] + [-value for value in t]] + [[t[r]] + c[r] for r in range(IMAGINARY)]
    pf_a = pfaffian_function(bordered, zero, one)((1 << HALF) - 1)
    return {
        "cross_matrix_skew": skew,
        "cross_matrix_annihilates_z": annihilates,
        "cofactor_terms": [len(p) for p in cofactors],
        "cofactor_equals_qg_z": [p == q * g * z[j] for j, p in enumerate(cofactors)],
        "cofactor_equals_g_z": [p == g * z[j] for j, p in enumerate(cofactors)],
        "cofactor_equals_q_z": [p == q * z[j] for j, p in enumerate(cofactors)],
        "bordered_pfaffian_equals_minus_zt_qg": pf_a == -dot(z, t, zero) * q * g,
        "q_terms": len(q),
        "g_terms": len(g),
    }


def pfaffian_order_check(order: int) -> bool:
    """Pf^2 = det on one deterministic integer skew matrix of the given even order."""
    rows = [[0] * order for _ in range(order)]
    for i in range(order):
        for j in range(i + 1, order):
            rows[i][j] = (7 * i + 3 * j + i * j) % 11 - 5
            rows[j][i] = -rows[i][j]
    pf = pfaffian_function(rows, 0, 1)((1 << order) - 1)
    return bool(pf * pf == int(flint.fmpz_mat(rows).det()))


def pfaffian_self_test() -> dict[str, Any]:
    """Pf^2 = det on deterministic integer skew matrices of orders 2..10, and Pf [[0, 1], [-1, 0]] = 1."""
    orders = list(range(2, 12, 2))
    agreements = parallel.ordered_map(pfaffian_order_check, orders, min_items=2)
    standard = pfaffian_function([[0, 1], [-1, 0]], 0, 1)(3)
    return {"orders": orders, "pf_squared_equals_det": agreements, "standard_pfaffian": standard}


def left_matrix(y: Sequence[int]) -> list[list[int]]:
    """L_y with (r, c) entry the coefficient of e_r in y e_c."""
    return [[y[r ^ c] * SIGNS32[r ^ c][c] for c in range(DIM)] for r in range(DIM)]


def coordinates(y: Sequence[int | Fraction]) -> list[GQ]:
    return [GQ(Fraction(y[k]), Fraction(y[HALF + k])) for k in range(1, HALF)]


def bordered_matrix(z: Sequence[GQ], t: Sequence[GQ], signs: list[list[int]]) -> list[list[GQ]]:
    c = cross(z, ZERO, signs)
    return [[ZERO] + [-value for value in t]] + [[t[r]] + c[r] for r in range(IMAGINARY)]


def transport_case(item: tuple[int, bool]) -> bool:
    """phi(y e_j) = A(z, conj z) conj(phi(e_j)) for the basis element y = e_k and every j, phi(r, s) = r + i conj(s)."""
    k, conjugate_s = item
    y = [int(index == k) for index in range(DIM)]
    z = coordinates(y)
    a = bordered_matrix(z, [value.conj() for value in z], SIGNS16)

    def phi(vector: Sequence[int]) -> list[GQ]:
        s = [vector[HALF + m] * (1 if m == 0 or not conjugate_s else -1) for m in range(HALF)]
        return [GQ(Fraction(vector[m]), Fraction(s[m])) for m in range(HALF)]

    matrix = left_matrix(y)
    for j in range(DIM):
        image = [matrix[r][j] for r in range(DIM)]
        source = [value.conj() for value in phi([int(index == j) for index in range(DIM)])]
        if phi(image) != [dot(row, source, ZERO) for row in a]:
            return False
    return True


def transport(conjugate_s: bool = True) -> dict[str, Any]:
    cases = [(k, conjugate_s) for k in range(DIM) if k not in (0, HALF)]
    return {"imaginary_basis_elements": len(cases), "agreeing": sum(parallel.ordered_map(transport_case, cases))}


def multiply(a: Sequence[Any], b: Sequence[Any], signs: list[list[int]], zero: Any) -> list[Any]:
    out = [zero] * len(a)
    for p, left in enumerate(a):
        if left == zero:
            continue
        for q, right in enumerate(b):
            if right != zero:
                out[p ^ q] = out[p ^ q] + left * right * signs[p][q]
    return out


def square_zero_vectors(z: Sequence[Any], zero: Any, one: Any) -> list[list[Any]]:
    """(h, 0) and (0, h) for h in 1, u, v, uv, with z = (u, mu + v) and uv the octonion product."""
    u8 = [zero, *z[:SEVEN]]
    v8 = [zero, *z[OCTONION:]]
    generators = [[one] + [zero] * SEVEN, u8, v8, multiply(u8, v8, SIGNS8, zero)]
    return [h + [zero] * OCTONION for h in generators] + [[zero] * OCTONION + h for h in generators]


def square_zero_route() -> dict[str, Any]:
    """z (z x) + Q x = 0 over Z[z] on the eight vectors, its failure on basis vectors, their rank where Q = 0."""
    ring = flint.fmpz_mpoly_ctx.get([f"z{k}" for k in range(1, HALF)], "lex")
    z = list(ring.gens())
    zero, one = ring.from_dict({}), ring.from_dict({(0,) * IMAGINARY: 1})
    q = invariants(z, zero)["Q"]
    sedenion_z = [zero, *z]

    def residual_vanishes(x: list[Any]) -> bool:
        twice = multiply(sedenion_z, multiply(sedenion_z, x, SIGNS16, zero), SIGNS16, zero)
        return all(a + q * b == 0 for a, b in zip(twice, x, strict=True))

    vectors = square_zero_vectors(z, zero, one)
    basis_failures = [m for m in range(HALF) if not residual_vanishes([one if i == m else zero for i in range(HALF)])]
    # u = e1, v = 2 e1 + 2 e2, mu = 3i: Q = 1 - 9 + 8 = 0 and Delta = 8 - 4 = 4.
    point = [ZERO] * IMAGINARY
    point[0], point[MU], point[OCTONION], point[OCTONION + 1] = ONE, I_UNIT * 3, gq(2), gq(2)
    return {
        "identity_on_square_zero_vectors": [residual_vanishes(x) for x in vectors],
        "basis_vectors_failing_identity": basis_failures,
        "example_point": [value.pair() for value in point],
        "example_q": invariants(point, ZERO)["Q"].pair(),
        "example_rank": complex_rank(square_zero_vectors(point, ZERO, ONE)),
    }


def fmpq_rows(rows: Sequence[Sequence[Fraction]]) -> flint.fmpq_mat:
    return flint.fmpq_mat([[flint.fmpq(value.numerator, value.denominator) for value in row] for row in rows])


def rational_rank(rows: Sequence[Sequence[Fraction]]) -> int:
    if not rows or not rows[0]:
        return 0
    return int(fmpq_rows(rows).rank())


def complex_rank(rows: Sequence[Sequence[GQ]]) -> int:
    real = [[v.re for v in row] + [-v.im for v in row] for row in rows]
    real += [[v.im for v in row] + [v.re for v in row] for row in rows]
    return rational_rank(real) // 2


def integer_kernel(rows: list[list[int]]) -> list[list[int]]:
    basis, nullity = flint.fmpz_mat(rows).nullspace()
    return [[int(basis[r, c]) for r in range(basis.nrows())] for c in range(nullity)]


def evaluate(poly: Any, point: Sequence[GQ]) -> GQ:
    total = ZERO
    for exponents, coefficient in poly.to_dict().items():
        term = gq(int(coefficient))
        for k, power in enumerate(exponents):
            for _ in range(int(power)):
                term = term * point[k]
        total = total + term
    return total


def derivation_basis() -> list[list[list[int]]]:
    """An integer basis of the derivations D of the octonions, D[r][c] the e_r coefficient of D e_c."""
    equations = []
    for i in range(OCTONION):
        for j in range(OCTONION):
            for m in range(OCTONION):
                row = [0] * (OCTONION * OCTONION)
                row[m * OCTONION + (i ^ j)] += SIGNS8[i][j]
                row[(m ^ j) * OCTONION + i] -= SIGNS8[m ^ j][j]
                row[(i ^ m) * OCTONION + j] -= SIGNS8[i][i ^ m]
                equations.append(row)
    return [
        [vector[r * OCTONION : (r + 1) * OCTONION] for r in range(OCTONION)] for vector in integer_kernel(equations)
    ]


def doubled(d: list[list[int]]) -> list[list[int]]:
    """D acting on both octonion halves of A_4."""
    return [
        [d[r % OCTONION][c % OCTONION] if (r < OCTONION) == (c < OCTONION) else 0 for c in range(HALF)]
        for r in range(HALF)
    ]


def is_sedenion_derivation(d: list[list[int]]) -> bool:
    for i in range(HALF):
        for j in range(HALF):
            lhs = [SIGNS16[i][j] * d[m][i ^ j] for m in range(HALF)]
            rhs = [0] * HALF
            for r in range(HALF):
                rhs[r ^ j] += d[r][i] * SIGNS16[r][j]
                rhs[i ^ r] += d[r][j] * SIGNS16[i][r]
            if lhs != rhs:
                return False
    return True


def derivations() -> dict[str, Any]:
    basis = derivation_basis()
    extended = [doubled(d) for d in basis]
    return {
        "count": len(basis),
        "sedenion_derivations": all(parallel.ordered_map(is_sedenion_derivation, extended, min_items=2)),
        "skew": all(d[r][c] == -d[c][r] for d in extended for r in range(HALF) for c in range(HALF)),
        "kill_units": all(d[r][0] == 0 and d[r][OCTONION] == 0 for d in extended for r in range(HALF)),
        "matrices": extended,
    }


def curve(z: Sequence[GQ], k: int) -> list[GQ]:
    """((1 + U k^2) u, -2 lambda U k, lambda (1 - U k^2) u + (1 + U k^2) n) with lambda = u.v / U, n = v - lambda u."""
    u, v = list(z[:SEVEN]), list(z[OCTONION:])
    big_u = dot(u, u, ZERO)
    lam = dot(u, v, ZERO) / big_u
    n = [b - lam * a for a, b in zip(u, v, strict=True)]
    scale = ONE + big_u * (k * k)
    shrink = ONE - big_u * (k * k)
    return (
        [a * scale for a in u]
        + [lam * big_u * (-2 * k)]
        + [lam * shrink * a + scale * b for a, b in zip(u, n, strict=True)]
    )


def orbit_piece(z: Sequence[GQ], extended: list[list[list[int]]]) -> dict[str, Any]:
    """The curve ranks, the orbit differential rank and the incidence data of a zd-nonzd-locus witness."""
    u, mu, v = list(z[:SEVEN]), z[MU], list(z[OCTONION:])
    big_u = dot(u, u, ZERO)
    _require(big_u != ZERO, "u.u vanishes at a zd-nonzd-locus witness")
    lam = dot(u, v, ZERO) / big_u
    n = [b - lam * a for a, b in zip(u, v, strict=True)]
    points = [curve(z, k) for k in range(CURVE_POINTS)]
    ranks = [complex_rank(cross(point, ZERO, SIGNS16)) for point in points]
    sedenion = [ZERO, *z]
    columns = [[dot([gq(value) for value in row], sedenion, ZERO) for row in d][1:] for d in extended]
    velocity = [ZERO] * IMAGINARY
    velocity[MU] = lam * big_u * -2
    columns += [list(z), velocity]
    octonion_cross = cross([*u, *([ZERO] * OCTONION)], ZERO, SIGNS16)
    image = [dot(octonion_cross[r][:SEVEN], n, ZERO) for r in range(SEVEN)]
    rho = next((image[r] / n[r] for r in range(SEVEN) if n[r] != ZERO), ZERO)
    return {
        "U": big_u.pair(),
        "lambda": lam.pair(),
        "mu": mu.pair(),
        "lambda_squared_is_minus_one": lam * lam == -ONE,
        "curve_starts_at_witness": points[0] == list(z),
        "curve_on_quadric": all(invariants(point, ZERO)["Q"] == ZERO for point in points),
        "curve_cross_ranks": ranks,
        "orbit_complex_rank": complex_rank(columns),
        "n_isotropic": dot(n, n, ZERO) == ZERO,
        "n_orthogonal_to_u": dot(u, n, ZERO) == ZERO,
        "n_eigenvector": all(image[r] == rho * n[r] for r in range(SEVEN)),
        "rho": rho.pair(),
        "rho_squared_plus_u": (rho * rho + big_u).pair(),
    }


def real_jacobian(gradient: Sequence[GQ]) -> list[list[Fraction]]:
    """Rows y_0, y_16, d Re F, d Im F in y_0..y_31 for holomorphic F with dF = sum g_k dz_k."""
    rows = [[Fraction(int(c == 0)) for c in range(DIM)], [Fraction(int(c == HALF)) for c in range(DIM)]]
    real, imaginary = [Fraction(0)] * DIM, [Fraction(0)] * DIM
    for k, g in enumerate(gradient):
        real[k + 1] += g.re
        real[HALF + k + 1] -= g.im
        imaginary[k + 1] += g.im
        imaginary[HALF + k + 1] += g.re
    return [*rows, real, imaginary]


def scaled(x: Sequence[Fraction]) -> list[int]:
    scale = 1
    for value in x:
        scale = lcm(scale, value.denominator)
    return [int(value * scale) for value in x]


def tangent_data(y: Sequence[int]) -> dict[str, Any]:
    """Nullity, the exact Schur differential rank, e_8 and e_24 membership in T(x) and dim T(x) cap H_5^perp."""
    matrix = left_matrix(y)
    right = integer_kernel(matrix)
    left = integer_kernel([list(row) for row in zip(*matrix, strict=True)])
    constraints = []
    for m in range(DIM):
        column = [
            sum(left_vector[m ^ c] * SIGNS32[m][c] * right_vector[c] for c in range(DIM))
            for left_vector in left
            for right_vector in right
        ]
        constraints.append(column)
    rows = [list(row) for row in zip(*constraints, strict=True)]
    rank = int(flint.fmpz_mat(rows).rank())
    restricted = rows + [[int(c == h) for c in range(DIM)] for h in H5]
    return {
        "nullity": len(right),
        "rank": DIM - len(right),
        "tangent_cone_dimension": DIM - rank,
        "e8_in_tangent": all(value == 0 for value in constraints[8]),
        "e24_in_tangent": all(value == 0 for value in constraints[24]),
        "tangent_cap_h5_perp_dimension": DIM - int(flint.fmpz_mat(restricted).rank()),
    }


@dataclass(frozen=True)
class Context:
    """Q and G over Z[z_1..z_15]."""

    q: Any
    g: Any


@functools.cache
def context() -> Context:
    ring = flint.fmpz_mpoly_ctx.get([f"z{k}" for k in range(1, HALF)], "lex")
    z = list(ring.gens())
    inv = invariants(z, ring.from_dict({}))
    return Context(inv["Q"], inv["G"])


def certify_witness(item: tuple[dict[str, Any], list[list[list[int]]]]) -> dict[str, Any]:
    row, extended = item
    ctx = context()
    family = row["family"]
    nullity, piece, cone = GAP_FAMILIES[family]
    x = [Fraction(value) for value in row["x"]]
    y = scaled(x)
    z = coordinates(x)
    out: dict[str, Any] = {
        "witness": row["witness"],
        "family": family,
        "family_unit_dimension": row["dimension"],
        "expected_nullity": nullity,
        "piece": piece,
        "piece_cone_dimension": cone,
        "x": [str(value) for value in x],
        "in_h5_perp": all(x[h] == 0 for h in H5),
    }
    out.update(tangent_data(y))
    q, g = evaluate(ctx.q, z), evaluate(ctx.g, z)
    out["Q"], out["G"] = q.pair(), g.pair()
    if piece in ("stiefel", "quartic"):
        poly = ctx.q if piece == "stiefel" else ctx.g
        gradient = [evaluate(poly.derivative(k), z) for k in range(IMAGINARY)]
        out["piece_equation_vanishes"] = (q if piece == "stiefel" else g) == ZERO
        out["piece_jacobian_rank"] = rational_rank(real_jacobian(gradient))
    elif piece == "quadric":
        minors = [z[i] * z[OCTONION + j] - z[j] * z[OCTONION + i] for i in range(SEVEN) for j in range(i + 1, SEVEN)]
        out["on_quadric_cone"] = q == ZERO and all(m == ZERO for m in minors)
    else:
        out["orbit"] = orbit_piece(z, extended)
    return out


def admit(row: dict[str, Any]) -> None:
    where = f"witness {row['witness']} ({row['family']})"
    _require(row["in_h5_perp"], f"{where} lies outside H_5^perp")
    _require(row["nullity"] == row["expected_nullity"], f"{where}: nullity {row['nullity']} is not the family's")
    _require(row["tangent_cone_dimension"] == row["piece_cone_dimension"], f"{where}: T(x) differs from the piece")
    _require(
        row["tangent_cone_dimension"] - 1 == row["family_unit_dimension"] + 2,
        f"{where}: the unit tangent bound is not two above the family",
    )
    _require(row["e8_in_tangent"] and row["e24_in_tangent"], f"{where}: e_8 or e_24 lies outside T(x)")
    _require(
        row["tangent_cap_h5_perp_dimension"] == row["tangent_cone_dimension"] - 2,
        f"{where}: T(x) cap H_5^perp is not two below T(x)",
    )
    piece = row["piece"]
    if piece in ("stiefel", "quartic"):
        _require(row["piece_equation_vanishes"], f"{where} is off its {piece} piece")
        _require(row["piece_jacobian_rank"] == 4, f"{where}: the {piece} piece is not smooth of codimension 4")
    elif piece == "quadric":
        _require(row["on_quadric_cone"], f"{where} is off the quadric cone V")
    else:
        orbit = row["orbit"]
        _require(orbit["curve_starts_at_witness"], f"{where}: the curve misses the witness")
        _require(len(orbit["curve_cross_ranks"]) == CURVE_POINTS, f"{where}: the curve has too few points")
        _require(max(orbit["curve_cross_ranks"]) <= CURVE_CROSS_RANK, f"{where}: the curve leaves R_8")
        _require(orbit["orbit_complex_rank"] == ORBIT_COMPLEX_RANK, f"{where}: the orbit map rank is not 11")


CONTROL_POINTS: tuple[tuple[str, tuple[tuple[int, int], ...]], ...] = (
    ("stiefel e1+e18", ((1, 1), (18, 1))),
    ("unit e1", ((1, 1),)),
    ("non-isotropic e1+e2+e18", ((1, 1), (2, 1), (18, 1))),
    ("moreno e1+e10+2e24", ((1, 1), (10, 1), (24, 2))),
    ("incidence e1+e10+e25+e27", ((1, 1), (10, 1), (25, 1), (27, 1))),
    ("mixed e1+e10+e25+e28", ((1, 1), (10, 1), (25, 1), (28, 1))),
)


def control_point(item: tuple[str, tuple[tuple[int, int], ...]]) -> dict[str, Any]:
    """Nullity, Q, G and the ranks of A and C_z at one structured point; the curve test at the G.I9 pair."""
    name, support = item
    ctx = context()
    y = [0] * DIM
    for index, value in support:
        y[index] = value
    z = coordinates(y)
    q, g = evaluate(ctx.q, z), evaluate(ctx.g, z)
    a = bordered_matrix(z, [value.conj() for value in z], SIGNS16)
    record: dict[str, Any] = {
        "point": name,
        "nullity": DIM - int(flint.fmpz_mat(left_matrix(y)).rank()),
        "Q": q.pair(),
        "G": g.pair(),
        "bordered_complex_rank": complex_rank(a),
        "cross_rank": complex_rank(cross(z, ZERO, SIGNS16)),
    }
    if name.startswith(("incidence", "mixed")):
        record["curve_cross_ranks"] = [complex_rank(cross(curve(z, k), ZERO, SIGNS16)) for k in range(3)]
    return record


def controls() -> list[dict[str, Any]]:
    """Structured points: nullity against Q G, and the curve test at the G.I9 pair."""
    return parallel.ordered_map(control_point, list(CONTROL_POINTS), min_items=2)


def witness_rows() -> list[dict[str, Any]]:
    """The gap-family witnesses of rank_locus_local_dimension, checked against its retained record."""
    retained = {row["witness"]: row["x"] for row in json.loads(LOCAL_DIMENSION_RECORD.read_text())["rows"]}
    rows = [row for row in witnesses() if row["family"] in GAP_FAMILIES]
    _require(len(rows) == 12, f"{len(rows)} gap witnesses instead of 12")
    for row in rows:
        _require(
            [str(value) for value in row["x"]] == retained[row["witness"]],
            f"witness {row['witness']} differs from the retained local-dimension record",
        )
    return rows


def measure() -> dict[str, Any]:
    algebra = factorization(SIGNS16)
    _require(
        algebra["cross_matrix_skew"]
        and algebra["cross_matrix_annihilates_z"]
        and all(algebra["cofactor_equals_qg_z"])
        and algebra["bordered_pfaffian_equals_minus_zt_qg"],
        "a Pfaffian identity fails",
    )
    pfaffian_check = pfaffian_self_test()
    _require(all(pfaffian_check["pf_squared_equals_det"]) and pfaffian_check["standard_pfaffian"] == 1, "Pf is wrong")
    moved = transport()
    _require(moved["agreeing"] == moved["imaginary_basis_elements"], "the transport identity fails")
    route = square_zero_route()
    _require(
        all(route["identity_on_square_zero_vectors"])
        and route["example_q"] == ZERO.pair()
        and route["example_rank"] == OCTONION,
        "the square-zero cross-check fails",
    )
    algebra_derivations = derivations()
    _require(
        algebra_derivations["count"] == DERIVATIONS
        and algebra_derivations["sedenion_derivations"]
        and algebra_derivations["skew"]
        and algebra_derivations["kill_units"],
        "the doubled octonion derivations are not skew sedenion derivations fixing 1 and e_8",
    )
    extended = algebra_derivations["matrices"]
    rows = parallel.ordered_map(certify_witness, [(row, extended) for row in witness_rows()], min_items=2)
    for row in rows:
        admit(row)
    checks = controls()
    for record in checks:
        product_zero = record["Q"] == ZERO.pair() or record["G"] == ZERO.pair()
        _require((record["nullity"] > 0) == product_zero, f"{record['point']}: nullity disagrees with Q G")
        _require(record["nullity"] == 28 - 2 * record["cross_rank"], f"{record['point']}: nullity is not 28 - 2 rank C")
    return {
        "schema": SCHEMA,
        "versions": {"python-flint": importlib.metadata.version("python-flint")},
        "factorization": algebra,
        "pfaffian_self_test": pfaffian_check,
        "transport": moved,
        "square_zero_route": route,
        "derivations": {key: value for key, value in algebra_derivations.items() if key != "matrices"},
        "witnesses": rows,
        "controls": checks,
    }


_MISSING = object()


def differences(retained: Any, fresh: Any, path: str = "") -> list[str]:
    """Paths where the records differ; a key present on one side only, or a value of another type, differs."""
    if isinstance(retained, dict) and isinstance(fresh, dict):
        return [
            item
            for key in sorted(set(retained) | set(fresh))
            for item in differences(retained.get(key, _MISSING), fresh.get(key, _MISSING), f"{path}/{key}")
        ]
    if isinstance(retained, list) and isinstance(fresh, list) and len(retained) == len(fresh):
        return [
            item
            for index, pair in enumerate(zip(retained, fresh, strict=True))
            for item in differences(*pair, f"{path}[{index}]")
        ]
    return [] if type(retained) is type(fresh) and retained == fresh else [path or "/"]


def _refused(row: dict[str, Any]) -> bool:
    try:
        admit(row)
    except SystemExit:
        return True
    return False


def self_test() -> str:
    flipped = copy.deepcopy(SIGNS16)
    flipped[3][12] = -flipped[3][12]
    _require(not factorization(flipped)["cross_matrix_skew"], "a flipped e3 e12 structure constant keeps C_z skew")
    # Entry (2, 5) of C_z is sign(e5 e6) z_5, the e3 coefficient of z e6.
    broken = factorization(SIGNS16, flip=(2, 5))
    _require(
        broken["cross_matrix_skew"]
        and not all(broken["cofactor_equals_qg_z"])
        and not broken["bordered_pfaffian_equals_minus_zt_qg"],
        "a skew sign flip of C_z keeps the Pfaffian identity",
    )
    honest = factorization(SIGNS16)
    _require(
        not any(honest["cofactor_equals_g_z"]) and not any(honest["cofactor_equals_q_z"]),
        "a cofactor equals G z_j or Q z_j, so a factor is not needed",
    )
    _require(transport(conjugate_s=False)["agreeing"] < DIM - 2, "transport without conj(s) still agrees")
    route = square_zero_route()
    _require(route["basis_vectors_failing_identity"], "z (z e_m) = -Q e_m holds on every basis vector")
    checks = {record["point"]: record for record in controls()}
    _require(
        max(checks["mixed e1+e10+e25+e28"]["curve_cross_ranks"]) > CURVE_CROSS_RANK
        and max(checks["incidence e1+e10+e25+e27"]["curve_cross_ranks"]) <= CURVE_CROSS_RANK,
        "the curve test does not separate the eigenspace-mixed point from the incidence point",
    )
    extended = derivations()["matrices"]
    rows = parallel.ordered_map(certify_witness, [(row, extended) for row in witness_rows()], min_items=2)
    corruptions: tuple[tuple[str, int, tuple[str, ...], Any], ...] = (
        ("nullity", 0, ("nullity",), 13),
        ("tangent dimension", 1, ("tangent_cone_dimension",), 23),
        ("e24 membership", 2, ("e24_in_tangent",), False),
        ("piece equation", 3, ("piece_equation_vanishes",), False),
        ("piece jacobian", 2, ("piece_jacobian_rank",), 3),
        ("curve rank", 1, ("orbit", "curve_cross_ranks"), [12] * CURVE_POINTS),
        ("orbit rank", 1, ("orbit", "orbit_complex_rank"), 10),
        ("quadric membership", 0, ("on_quadric_cone",), False),
    )
    for label, index, path, value in corruptions:
        damaged = copy.deepcopy(rows[index])
        target = damaged
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        _require(_refused(damaged), f"a corrupted {label} is admitted")
    return f"{len(corruptions)} row corruptions, 5 identity mutations and the G.I9 curve control rejected"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--out", type=Path)
    mode.add_argument("--check", type=Path)
    mode.add_argument("--self-test", action="store_true")
    arguments = parser.parse_args()
    if arguments.self_test:
        print(f"a5_stiefel_pfaffian_germs self-test: {self_test()}")
        return 0
    data = measure()
    if arguments.check is not None:
        retained = json.loads(arguments.check.read_text())
        differing = differences(
            {k: v for k, v in retained.items() if k != "versions"}, {k: v for k, v in data.items() if k != "versions"}
        )
        if differing:
            raise SystemExit(f"a5_stiefel_pfaffian_germs: {differing} differ from {arguments.check}")
    else:
        arguments.out.parent.mkdir(parents=True, exist_ok=True)
        arguments.out.write_text(json.dumps(data, indent=1, sort_keys=True) + "\n")
    algebra = data["factorization"]
    print(f"cofactors P_j = Q G z_j: {sum(algebra['cofactor_equals_qg_z'])}/15, terms {algebra['cofactor_terms'][0]}")
    print(f"transport: {data['transport']}")
    for row in data["witnesses"]:
        print(
            f"witness {row['witness']:2d} {row['family']:18s} nullity {row['nullity']:2d} "
            f"T {row['tangent_cone_dimension']:2d} cap H5perp {row['tangent_cap_h5_perp_dimension']:2d} "
            f"e8 {row['e8_in_tangent']} e24 {row['e24_in_tangent']} piece {row['piece']}"
        )
    for record in data["controls"]:
        print(f"control {record['point']:26s} nullity {record['nullity']:2d} Q {record['Q']} G {record['G']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
