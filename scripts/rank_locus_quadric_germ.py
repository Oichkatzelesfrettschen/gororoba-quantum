"""Exact quadric germ of the A_5 nullity-12 rank locus at the nonzd-axis witnesses and the Proposition 8.2 points.

For y = (p, q) in A_5 with p, q in Im A_4 (y_0 = y_16 = 0) put z = p + i q = (u, mu, v) in
C^7 + C + C^7, where i is a scalar unit, u = z_1..z_7, mu = z_8 and v = z_9..z_15, and every dot
product is complex bilinear. V is the cone {u ^ v = 0, Q(z) = u.u + mu^2 + v.v = 0}: 22 complex
equations, which are 44 real quadrics in y.

V lies in the closed rank cone R_12 = {y : rank L_y <= 20}, by identities this script checks in
full over Z[z, t].
- C_z, the imaginary part of (L_z - R_z) / 2 on Im (A_4)_C, is skew with C_z z = 0, and
  E(z) = C_z^2 - z z^T + Q(z) I = sum over i < j of M_ij (u_i v_j - u_j v_i) with constant
  integer matrices M_ij.
- For xi = r + i conj(s), with conj the Cayley-Dickson conjugation, L_y sends (r, s) to the vector
  whose xi is A(z, t) applied to the scalar-coefficient conjugate of xi, where t = p - i q and
  A = [[0, -t^T], [t, C_z]]. So rank_R L_y = 2 rank_C A.
- On V, C_z^2 = z z^T has rank at most 1, so Sylvester's inequality gives rank C_z <= 8, rank A <= 10
  and nullity L_y >= 12.
- B = a C_z + z h^T - h z^T with a = z^T t and h = C_z t satisfies t^T B = 0 and
  C_z B = (E - Q I)(a I - t z^T) for independent z and t. On V the columns of B, realified as
  (0, Re b; 0, Im b) and (0, -Im b; 0, Re b), are cubic polynomial kernel vectors of L_y.

At a point x of V with u_r a unit, V near x is v = lambda u together with
F = mu^2 + (1 + lambda^2) w.w = 0 in the nine complex coordinates (w = u, lambda, mu). dF(x) != 0
makes V a complex manifold of dimension 8 there, which is real dimension 16. The right and left
kernels N_r, N_l of L_x give the tangent bound T(x) = {y : N_l^T L_y N_r = 0}. The map
y -> N_l^T L_y N_r is the differential of the Schur complement, so when its rank is 16 the
Schur-complement germ M of rank_locus_padic_lift is a smooth 16-manifold containing R_12 near x.
V lies in R_12, which lies in M, and both V and M are 16-manifolds, so V = R_12 = M as germs at x.
D_(5,12) = R_12 on the unit sphere therefore has local dimension 15 at x, and the excess
Schur-complement entries vanish on M there. The record holds this at the three nonzd-axis witnesses
and the seven Proposition 8.2 points of rank_locus_local_dimension.

Degree. The Hilbert function of C[z]/(u ^ v, Q) in degrees 0..5 is 1, 15, 98, 420, 1386, 3822, that of
(1 + 7t + 6t^2)/(1 - t)^8. Degree 2 puts Q outside the span of the minors, hence outside their prime
ideal, which gives that series exactly: V is a cone of dimension 8 and degree 14. The 44 real quadrics
have integer coefficients, so over C they cut V x V in (z, w) with w_k = y_k - i y_(16+k), of degree 196.

Controls. x0 = e1 + e18 is a smooth point of V where T(x0) has dimension 22 and R_12 contains B17
beside V; its cone is A15 union B17 (nullity_twelve_local_geometry.md). The four-parameter
slice of nullity_twelve_curves lies in V identically, and the 14 octonion derivations act on u and v
by one real skew matrix and fix mu, so the A15 family germ lies in V. The fixed-norm tangent of V at
x0 contains the A15 frame, and both have dimension 15. The exact path
y(alpha) = e1 - sc e10 + c e18 + sc e24 + s e25 (s = sin alpha, c = cos alpha) lies in V and keeps
rank 20 by two principal minors whose closed forms are positive on two arcs that together cover
[0, pi/2]. It joins x0 to the witness e1 + e25 and is a rescaled slice point for c > 0.
e1 - e10 + e18 + e25 lies on V where dF = 0, with nullity 16, so V lies in the closed locus R_12 and
reaches nullity above 12 at that singular point.

Falsifiers: an entry of E outside the span of the minors, a failed kernel or
transport identity, a scope point off V, with dF = 0, with nullity other than 12, or with a tangent
bound other than 16 refutes the argument at that point; a Hilbert value off the series refutes the
degree.

Usage:
    "$PYTHON" scripts/rank_locus_quadric_germ.py --out docs/evidence/rank_locus_quadric_germ/result.json
    "$PYTHON" scripts/rank_locus_quadric_germ.py --check docs/evidence/rank_locus_quadric_germ/result.json
    "$PYTHON" scripts/rank_locus_quadric_germ.py --self-test
"""

from __future__ import annotations

import argparse
import copy
import importlib.metadata
import itertools
import json
import math
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any

import flint
import sympy as sp
from sympy.polys.matrices import DomainMatrix

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))
from rank_locus_local_dimension import witnesses  # noqa: E402

import parallel  # noqa: E402
from cd_core import cd_sign  # noqa: E402

SCHEMA = "rank-locus-quadric-germ-v1"
DIM = 32
HALF = 16
OCTONION = 7
# z_8 = mu is index 7 of z_1..z_15 and v_j is index 8 + j - 1; e8 and e24 carry Re mu and Im mu.
MU = 7
V_OFFSET = 8
NULLITY = 12
GERM_DIMENSION = 16
# Sylvester on C_z^2 = z z^T over C^15: 2 rank C_z - 15 <= 1.
CROSS_RANK_BOUND = 8
DERIVATIONS = 14
ORBIT_RANK = 11
SCOPE = ("nonzd-axis", "proposition-8.2")
OTHER_GAP_FAMILIES = ("zd-nonzd-locus", "zd-nonzd-generic", "nonzd-nonzd-locus")
SIGNS = [[cd_sign(HALF, i, j) for j in range(HALF)] for i in range(HALF)]
SIGNS32 = [[cd_sign(DIM, i, j) for j in range(DIM)] for i in range(DIM)]
# A coordinate y_k with k in 1..15 is p_k, and y_(16+k) is q_k, so z_k = y_k + i y_(16+k).
POINTS: tuple[tuple[str, str, tuple[tuple[int, int], ...]], ...] = (
    ("nonzd-axis", "e1+e25", ((1, 1), (25, 1))),
    ("nonzd-axis", "e2+e26", ((2, 1), (26, 1))),
    ("nonzd-axis", "e3+e27", ((3, 1), (27, 1))),
    *(("proposition-8.2", f"e8+e{16 + j}", ((8, 1), (16 + j, 1))) for j in range(1, 8)),
    ("x0", "e1+e18", ((1, 1), (18, 1))),
    ("singular", "e1-e10+e18+e25", ((1, 1), (10, -1), (18, 1), (25, 1))),
)
# C[z]/(u ^ v, Q) has Hilbert series (1 + 7t + 6t^2)/(1 - t)^8: the rank-one cone of the 2 x 7 matrix
# [u; v] with mu adjoined has (1 + 6t)/(1 - t)^9, and Q, outside that prime ideal, multiplies by 1 - t^2.
HILBERT_NUMERATOR = (1, 7, 6)
HILBERT_DENOMINATOR = 8
HILBERT_TOP = 5
PATH_MINORS = {
    "0..19": "16*c**8*(1 + s**2*c**2)**2*(1 - s**2*c**2)**4",
    "0..17,24,25": "16*s**4*(1 + 2*c**2)**2*(1 + s**2*c**2)**2*(1 - s**2*c**2)**4",
}
PATH_MINOR_INDICES = {"0..19": list(range(20)), "0..17,24,25": [*range(18), 24, 25]}


def _require(ok: bool, message: str) -> None:
    if not ok:
        raise SystemExit(f"rank_locus_quadric_germ: {message}")


@dataclass(frozen=True)
class Gauss:
    """A Gaussian integer re + i im."""

    re: int
    im: int

    def __add__(self, other: Gauss) -> Gauss:
        return Gauss(self.re + other.re, self.im + other.im)

    def __sub__(self, other: Gauss) -> Gauss:
        return Gauss(self.re - other.re, self.im - other.im)

    def __neg__(self) -> Gauss:
        return Gauss(-self.re, -self.im)

    def __mul__(self, other: Gauss | int) -> Gauss:
        if isinstance(other, int):
            return Gauss(self.re * other, self.im * other)
        return Gauss(self.re * other.re - self.im * other.im, self.re * other.im + self.im * other.re)

    def conj(self) -> Gauss:
        return Gauss(self.re, -self.im)

    def pair(self) -> list[int]:
        return [self.re, self.im]


ZERO = Gauss(0, 0)
ONE = Gauss(1, 0)


def cross(z: Sequence[Any], zero: Any, signs: list[list[int]]) -> list[list[Any]]:
    """C_z on Im (A_4)_C: entry (a - 1, b - 1) is the e_a coefficient of (z e_b - e_b z) / 2, linear in z_1..z_15."""
    rows = []
    for a in range(1, HALF):
        row = []
        for b in range(1, HALF):
            k = a ^ b
            twice = signs[k][b] - signs[b][k] if k else 0
            _require(twice % 2 == 0, f"the commutator coefficient of e_{k} e_{b} is odd")
            row.append(z[k - 1] * (twice // 2) if twice else zero)
        rows.append(row)
    return rows


def matmul(a: list[list[Any]], b: list[list[Any]], zero: Any) -> list[list[Any]]:
    out = []
    for row in a:
        line = []
        for j in range(len(b[0])):
            total = zero
            for k, value in enumerate(row):
                total = total + value * b[k][j]
            line.append(total)
        out.append(line)
    return out


def minors(z: Sequence[Any]) -> list[Any]:
    """u_i v_j - u_j v_i for 1 <= i < j <= 7, in lexicographic order."""
    return [z[i] * z[V_OFFSET + j] - z[j] * z[V_OFFSET + i] for i in range(OCTONION) for j in range(i + 1, OCTONION)]


def isotropy(z: Sequence[Any], zero: Any) -> Any:
    total = zero
    for value in z:
        total = total + value * value
    return total


def _monomials(degree: int) -> list[tuple[int, ...]]:
    out = []
    for combination in itertools.combinations_with_replacement(range(HALF - 1), degree):
        exponent = [0] * (HALF - 1)
        for k in combination:
            exponent[k] += 1
        out.append(tuple(exponent))
    return out


def cone_generators(quadric: bool = True) -> list[dict[tuple[int, ...], int]]:
    """The 21 minors and Q as exponent maps over z_1..z_15; quadric=False puts a sum of two minors in Q's place."""
    ring = flint.fmpz_mpoly_ctx.get([f"z{k}" for k in range(1, HALF)], "lex")
    z = list(ring.gens())
    rank_one = minors(z)
    last = isotropy(z, ring.from_dict({})) if quadric else rank_one[0] + rank_one[1]
    return [
        {tuple(int(e) for e in exponents): int(value) for exponents, value in generator.to_dict().items()}
        for generator in [*rank_one, last]
    ]


def hilbert_value(item: tuple[list[dict[tuple[int, ...], int]], int]) -> int:
    """dim_C of the degree-d part of C[z]/(generators), for quadratic generators, by an exact fmpz rank."""
    generators, degree = item
    _require(all(sum(exponents) == 2 for g in generators for exponents in g), "a generator is not quadratic")
    basis = _monomials(degree)
    if degree < 2:
        return len(basis)
    index = {monomial: k for k, monomial in enumerate(basis)}
    shifts = _monomials(degree - 2)
    matrix = flint.fmpz_mat(len(generators) * len(shifts), len(basis))
    row = 0
    for generator in generators:
        for shift in shifts:
            for exponents, value in generator.items():
                column = index[tuple(a + b for a, b in zip(exponents, shift, strict=True))]
                matrix[row, column] += value
            row += 1
    return len(basis) - matrix.rank()


def hilbert(quadric: bool = True, top: int = HILBERT_TOP) -> dict[str, Any]:
    """The Hilbert function of C[z]/(u ^ v, Q) in degrees 0..top against (1 + 7t + 6t^2)/(1 - t)^8."""
    generators = cone_generators(quadric)
    values = parallel.ordered_map(hilbert_value, [(generators, d) for d in range(top + 1)], min_items=2)
    predicted = [
        sum(
            c * math.comb(d - s + HILBERT_DENOMINATOR - 1, HILBERT_DENOMINATOR - 1)
            for s, c in enumerate(HILBERT_NUMERATOR)
            if d >= s
        )
        for d in range(top + 1)
    ]
    return {
        "values": values,
        "predicted": predicted,
        "agrees": values == predicted,
        "numerator": list(HILBERT_NUMERATOR),
        "denominator_exponent": HILBERT_DENOMINATOR,
        "degree": sum(HILBERT_NUMERATOR),
        "real_presentation_degree": sum(HILBERT_NUMERATOR) ** 2,
    }


def identity(signs: list[list[int]]) -> dict[str, Any]:
    """The remainder of C_z^2 - z z^T + Q I in the minors and the two cubic-kernel identities over Z[z, t]."""
    ring = flint.fmpz_mpoly_ctx.get([f"z{k}" for k in range(1, HALF)] + [f"t{k}" for k in range(1, HALF)], "lex")
    generators = ring.gens()
    z, t = list(generators[: HALF - 1]), list(generators[HALF - 1 :])
    zero = ring.from_dict({})
    n = HALF - 1
    c = cross(z, zero, signs)
    skew = all(c[i][j] + c[j][i] == 0 for i in range(n) for j in range(n))
    annihilates = all(sum((c[i][j] * z[j] for j in range(n)), zero) == 0 for i in range(n))
    q = isotropy(z, zero)
    square = matmul(c, c, zero)
    e = [[square[i][j] - z[i] * z[j] + (q if i == j else zero) for j in range(n)] for i in range(n)]
    remainder: list[list[int]] = []
    in_span = True
    for row in range(n):
        for column in range(n):
            terms: dict[tuple[int, int], int] = {}
            for exponents, value in e[row][column].to_dict().items():
                factors = [k for k, power in enumerate(exponents) for _ in range(power)]
                first, second = factors if len(factors) == 2 else (-1, -1)
                if 0 <= first < OCTONION and V_OFFSET <= second < n and first != second - V_OFFSET:
                    terms[(first, second - V_OFFSET)] = int(value)
                else:
                    in_span = False
            for (i, j), value in sorted(terms.items()):
                if i < j:
                    in_span &= terms.get((j, i)) == -value
                    remainder.append([row + 1, column + 1, i + 1, j + 1, value])
                else:
                    in_span &= terms.get((j, i)) == -value
    a = sum((z[i] * t[i] for i in range(n)), zero)
    h = [sum((c[i][j] * t[j] for j in range(n)), zero) for i in range(n)]
    b = [[a * c[i][j] + z[i] * h[j] - h[i] * z[j] for j in range(n)] for i in range(n)]
    left = all(sum((t[i] * b[i][j] for i in range(n)), zero) == 0 for j in range(n))
    factor = [[e[i][j] - (q if i == j else zero) for j in range(n)] for i in range(n)]
    shift = [[(a if i == j else zero) - t[i] * z[j] for j in range(n)] for i in range(n)]
    right = matmul(c, b, zero) == matmul(factor, shift, zero)
    return {
        "cross_matrix_skew": skew,
        "cross_matrix_annihilates_z": annihilates,
        "remainder_in_minor_span": in_span,
        "remainder": remainder,
        "remainder_coefficients": sorted({entry[4] for entry in remainder}),
        "kernel_left_identity": left,
        "kernel_right_identity": right,
    }


def left_matrix(y: Sequence[int]) -> list[list[int]]:
    """L_y with (k, j) entry the coefficient of e_k in y e_j."""
    return [[y[k ^ j] * SIGNS32[k ^ j][j] for j in range(DIM)] for k in range(DIM)]


def coordinates(y: Sequence[int]) -> list[Gauss]:
    return [Gauss(y[k], y[HALF + k]) for k in range(1, HALF)]


def transport_case(item: tuple[int, bool]) -> bool:
    """Phi L_y = Real(A(z, t)) Conj Phi at the basis element y = e_k, with Phi(r, s) = (r, conj(s))."""
    k, conjugate_s = item
    phi = [1] * HALF + [1] + [-1 if conjugate_s else 1] * (HALF - 1)
    y = [int(index == k) for index in range(DIM)]
    z = coordinates(y)
    t = [value.conj() for value in z]
    c = cross(z, ZERO, SIGNS)
    a = [[ZERO] * HALF for _ in range(HALF)]
    for index in range(1, HALF):
        a[0][index] = -t[index - 1]
        a[index][0] = t[index - 1]
        for column in range(1, HALF):
            a[index][column] = c[index - 1][column - 1]
    real = [[a[r][col].re for col in range(HALF)] + [-a[r][col].im for col in range(HALF)] for r in range(HALF)]
    real += [[a[r][col].im for col in range(HALF)] + [a[r][col].re for col in range(HALF)] for r in range(HALF)]
    conjugated = [[real[r][col] * (1 if col < HALF else -1) for col in range(DIM)] for r in range(DIM)]
    lhs = [[phi[r] * value for value in row] for r, row in enumerate(left_matrix(y))]
    rhs = [[conjugated[r][col] * phi[col] for col in range(DIM)] for r in range(DIM)]
    return lhs == rhs


def transport(conjugate_s: bool = True) -> dict[str, Any]:
    """The transport identity on every imaginary basis element (Re xi, Im xi) = (r, conj(s))."""
    cases = [(k, conjugate_s) for k in range(DIM) if k not in (0, HALF)]
    return {"imaginary_basis_elements": DIM - 2, "agreeing": sum(parallel.ordered_map(transport_case, cases))}


def fmpz(rows: list[list[int]]) -> flint.fmpz_mat:
    return flint.fmpz_mat(rows)


def kernel(rows: list[list[int]]) -> list[list[int]]:
    """An integer basis of the right kernel, as columns listed row by row."""
    basis, nullity = fmpz(rows).nullspace()
    return [[int(basis[r, c]) for r in range(basis.nrows())] for c in range(nullity)]


def leading_columns(rows: list[list[int]]) -> list[int]:
    reduced, rank = flint.fmpq_mat(fmpz(rows)).rref()
    found: list[int] = []
    column = 0
    for row in range(rank):
        while reduced[row, column] == 0:
            column += 1
        found.append(column)
    return found


def jacobian(z: Sequence[Gauss]) -> list[list[int]]:
    """Real Jacobian in y_0..y_31 of y_0, y_16 and the real and imaginary parts of the 22 equations of V."""
    gradients: list[dict[int, Gauss]] = []
    for i in range(OCTONION):
        for j in range(i + 1, OCTONION):
            gradients.append({i: z[V_OFFSET + j], V_OFFSET + j: z[i], j: -z[V_OFFSET + i], V_OFFSET + i: -z[j]})
    gradients.append({k: z[k] * 2 for k in range(HALF - 1)})
    rows = [[int(col == 0) for col in range(DIM)], [int(col == HALF) for col in range(DIM)]]
    for gradient in gradients:
        real = [0] * DIM
        imaginary = [0] * DIM
        # dz_k = dy_(k+1) + i dy_(17+k); for holomorphic F, dF = sum g_k dz_k.
        for k, g in gradient.items():
            real[k + 1] += g.re
            real[HALF + k + 1] -= g.im
            imaginary[k + 1] += g.im
            imaginary[HALF + k + 1] += g.re
        rows += [real, imaginary]
    return rows


def chart(z: Sequence[Gauss]) -> dict[str, Any] | None:
    """The v = lambda u chart at a unit anchor u_r and the differential of F = mu^2 + (1 + lambda^2) w.w."""
    anchors = [k for k in range(OCTONION) if z[k] in (ONE, -ONE, Gauss(0, 1), Gauss(0, -1))]
    if not anchors:
        return None
    r = anchors[0]
    lam = z[V_OFFSET + r] * z[r].conj()
    w = list(z[:OCTONION])
    if any(z[V_OFFSET + k] != lam * w[k] for k in range(OCTONION)):
        return None
    mu = z[MU]
    squared = isotropy(w, ZERO)
    shift = ONE + lam * lam
    return {
        "anchor": r + 1,
        "lambda": lam.pair(),
        "mu": mu.pair(),
        "d_mu": (mu * 2).pair(),
        "d_lambda": (lam * squared * 2).pair(),
        "d_w": [(shift * value * 2).pair() for value in w],
        "residual": (mu * mu + shift * squared).pair(),
    }


def realify(columns: list[list[Gauss]]) -> list[list[int]]:
    """The 32 x 2m real kernel frame (0, Re b; 0, Im b), (0, -Im b; 0, Re b) of complex 15-vectors b."""
    frame = []
    for b in columns:
        for first, second in (([v.re for v in b], [v.im for v in b]), ([-v.im for v in b], [v.re for v in b])):
            frame.append([0, *first, 0, *second])
    return [list(row) for row in zip(*frame, strict=True)]


def complex_rank(rows: list[list[Gauss]]) -> int:
    real = [[v.re for v in row] + [-v.im for v in row] for row in rows]
    real += [[v.im for v in row] + [v.re for v in row] for row in rows]
    return int(fmpz(real).rank()) // 2


def certify_point(point: tuple[str, str, tuple[tuple[int, int], ...]]) -> dict[str, Any]:
    family, name, support = point
    y = [0] * DIM
    for index, value in support:
        y[index] = value
    z = coordinates(y)
    on_v = y[0] == y[HALF] == 0 and all(m == ZERO for m in minors(z)) and isotropy(z, ZERO) == ZERO
    jac = jacobian(z)
    tangent_v = kernel(jac)
    matrix = left_matrix(y)
    right_kernel = kernel(matrix)
    left_kernel = kernel([list(row) for row in zip(*matrix, strict=True)])
    constraints = []
    for k in range(DIM):
        unit = left_matrix([int(index == k) for index in range(DIM)])
        images = [[sum(unit[r][c] * v[c] for c in range(DIM)) for r in range(DIM)] for v in right_kernel]
        constraints.append([sum(u[r] * image[r] for r in range(DIM)) for u in left_kernel for image in images])
    bound = [list(row) for row in zip(*constraints, strict=True)]
    bound_rank = int(fmpz(bound).rank())
    contained = all(sum(row[k] * v[k] for k in range(DIM)) == 0 for row in bound for v in tangent_v)
    rows = leading_columns([list(row) for row in zip(*matrix, strict=True)])
    columns = leading_columns(matrix)
    c = cross(z, ZERO, SIGNS)
    t = [value.conj() for value in z]
    a = ZERO
    for left_value, right_value in zip(z, t, strict=True):
        a = a + left_value * right_value
    h = [sum((c[i][j] * t[j] for j in range(HALF - 1)), ZERO) for i in range(HALF - 1)]
    b = [[c[i][j] * a + z[i] * h[j] - h[i] * z[j] for j in range(HALF - 1)] for i in range(HALF - 1)]
    frame = realify([[b[i][j] for i in range(HALF - 1)] for j in range(HALF - 1)])
    image = [
        [sum(matrix[r][k] * frame[k][col] for k in range(DIM)) for col in range(len(frame[0]))] for r in range(DIM)
    ]
    e8, e24 = ([int(index == unit) for index in range(DIM)] for unit in (MU + 1, HALF + MU + 1))
    return {
        "family": family,
        "point": name,
        "support": [list(pair) for pair in support],
        "on_v": on_v,
        "chart": chart(z),
        "jacobian_rank": int(fmpz(jac).rank()),
        "tangent_v_dimension": len(tangent_v),
        "nullity": len(right_kernel),
        "pivot_rows": rows,
        "pivot_columns": columns,
        "pivot_determinant": int(fmpz([[matrix[r][col] for col in columns] for r in rows]).det()),
        "tangent_bound_dimension": DIM - bound_rank,
        "tangent_v_in_bound": contained,
        "e8_e24_tangent": all(sum(row[k] * v[k] for k in range(DIM)) == 0 for row in jac for v in (e8, e24)),
        "cross_rank": complex_rank(c),
        "cubic_kernel_rank": int(fmpz(frame).rank()),
        "cubic_kernel_annihilated": all(value == 0 for row in image for value in row),
    }


def admit(row: dict[str, Any]) -> None:
    """The conditions under which the germ argument holds at a point, by its role."""
    where = f"{row['family']} {row['point']}"
    _require(row["on_v"], f"{where} is off V")
    _require(row["cross_rank"] <= CROSS_RANK_BOUND, f"{where}: rank C_z exceeds the Sylvester bound on V")
    chart_row = row["chart"]
    _require(chart_row is not None and chart_row["residual"] == [0, 0], f"{where} has no unit-anchor chart on V")
    smooth = any(v != [0, 0] for v in (chart_row["d_mu"], chart_row["d_lambda"], *chart_row["d_w"]))
    if row["family"] == "singular":
        _require(not smooth and row["nullity"] > NULLITY, f"{where} is not a singular point of V of excess nullity")
        return
    _require(smooth, f"{where}: dF vanishes, so the chart gives no manifold")
    _require(
        row["jacobian_rank"] == DIM - GERM_DIMENSION and row["tangent_v_dimension"] == GERM_DIMENSION,
        f"{where}: V is not cut out with codimension {DIM - GERM_DIMENSION}",
    )
    _require(row["nullity"] == NULLITY and len(row["pivot_rows"]) == DIM - NULLITY, f"{where}: nullity is not 12")
    _require(row["pivot_determinant"] != 0, f"{where}: the pivot minor vanishes")
    _require(row["tangent_v_in_bound"], f"{where}: the tangent space of V leaves the tangent bound")
    _require(row["cubic_kernel_annihilated"], f"{where}: the cubic kernel frame leaves ker L_x")
    if row["family"] in SCOPE:
        _require(row["tangent_bound_dimension"] == GERM_DIMENSION, f"{where}: tangent bound is not 16")
        _require(row["cubic_kernel_rank"] == NULLITY, f"{where}: the cubic frame does not span ker L_x")
    if row["family"] == "nonzd-axis":
        _require(row["e8_e24_tangent"], f"{where}: e8 or e24 is not tangent to V")
    if row["family"] == "x0":
        _require(row["tangent_bound_dimension"] > GERM_DIMENSION, f"{where}: tangent bound does not exceed V")


def scope_matches_witnesses() -> bool:
    """POINTS lists the nonzd-axis and Proposition 8.2 witnesses of rank_locus_local_dimension, in order."""
    listed = [
        sorted((index, int(value)) for index, value in enumerate(row["x"]) if value)
        for row in witnesses()
        if row["family"] in SCOPE
    ]
    return listed == [sorted(support) for family, _, support in POINTS if family in SCOPE]


def rational_chart() -> dict[str, Any]:
    """(w, tau) -> u = w, v = lambda w, mu with lambda = i (q - tau^2) / (q + tau^2), mu = 2 i q tau / (q + tau^2).

    q = w.w; the map solves F = 0 identically and inverts by tau = mu / (lambda + i), so it parameterizes V by
    C^8 wherever q + tau^2 and lambda + i are nonzero, which holds at both kinds of scope point.
    """
    q, tau = sp.symbols("q tau")
    lam = sp.I * (q - tau**2) / (q + tau**2)
    mu = 2 * sp.I * q * tau / (q + tau**2)
    # (q, tau) at e_r + e_(24 + r) (w = e_r) and at e_8 + e_(16 + j) (w = i e_j), with the (lambda, mu) they must give.
    centers = {"nonzd-axis": ((1, 0), (sp.I, 0)), "proposition-8.2": ((-1, -sp.I), (0, 1))}
    reached = {
        family: [lam.subs({q: at[0], tau: at[1]}), mu.subs({q: at[0], tau: at[1]})] == list(want)
        and (at[0] + at[1] ** 2) != 0
        for family, (at, want) in centers.items()
    }
    return {
        "solves_f": sp.cancel(mu**2 + (1 + lam**2) * q) == 0,
        "inverse": sp.cancel(mu / (lam + sp.I) - tau) == 0,
        "regular_at_scope_points": reached,
    }


def on_rank_one_locus(x: list[Any]) -> bool:
    """u ^ v = 0 at the rational point x."""
    values = [Fraction(value) for value in x]
    # The minors are homogeneous, so clearing denominators keeps their zero set.
    scale = math.lcm(*(value.denominator for value in values))
    return all(m == ZERO for m in minors(coordinates([int(value * scale) for value in values])))


def other_gap_witnesses() -> dict[str, list[int]]:
    """The nullity-8 and nullity-4 gap witnesses of rank_locus_local_dimension, split by whether u ^ v vanishes."""
    rows = [row for row in witnesses() if row["family"] in OTHER_GAP_FAMILIES]
    flags = parallel.ordered_map(on_rank_one_locus, [row["x"] for row in rows])
    split: dict[str, list[int]] = {"on_rank_one_locus": [], "off_rank_one_locus": []}
    for row, on in zip(rows, flags, strict=True):
        split["on_rank_one_locus" if on else "off_rank_one_locus"].append(row["witness"])
    return split


def _path() -> tuple[sp.Symbol, sp.Symbol, sp.Expr, list[sp.Expr]]:
    s, c = sp.symbols("s c", real=True)
    y = [sp.Integer(0)] * DIM
    y[1], y[10], y[18], y[24], y[25] = sp.Integer(1), -s * c, c, s * c, s
    return s, c, s**2 + c**2 - 1, y


def path_minor(label: str) -> bool:
    """The principal minor of L_y(alpha) on the rows and columns PATH_MINOR_INDICES[label] equals its closed form."""
    s, c, circle, y = _path()
    indices = PATH_MINOR_INDICES[label]
    matrix = sp.Matrix([[y[row ^ column] * SIGNS32[row ^ column][column] for column in indices] for row in indices])
    ring = sp.ZZ[s, c]
    determinant = ring.to_sympy(DomainMatrix.from_Matrix(matrix).convert_to(ring).det())
    closed = sp.sympify(PATH_MINORS[label], locals={"s": s, "c": c})
    return bool(sp.rem(sp.expand(determinant - closed), circle, s) == 0)


def path_link() -> dict[str, Any]:
    """y(alpha) = e1 - sc e10 + c e18 + sc e24 + s e25 on V, its two rank-20 minors and its slice form."""
    from nullity_twelve_curves import _base_numerator, _phase_vector

    s, c, circle, y = _path()
    z = [y[k] + sp.I * y[HALF + k] for k in range(1, HALF)]
    on_v = all(sp.rem(sp.expand(value), circle, s) == 0 for value in [*minors(z), isotropy(z, sp.Integer(0))])
    minors_ok = dict(zip(PATH_MINORS, parallel.ordered_map(path_minor, list(PATH_MINORS), min_items=2), strict=True))
    numerator, denominator = _base_numerator(sp.Integer(0), 2 * s * c / (1 + c), s)
    slice_point = _phase_vector(numerator / denominator, sp.Integer(0))
    rescaled = all(
        sp.rem(sp.expand(sp.numer(sp.together((1 + c) / 2 * slice_point[k] - y[k]))), circle, s) == 0
        for k in range(DIM)
    )
    return {
        "on_v": on_v,
        "principal_minors": {
            label: {"closed_form": PATH_MINORS[label], "agrees": minors_ok[label]} for label in PATH_MINORS
        },
        "rescaled_slice": rescaled,
        "endpoints": ["e1+e18", "e1+e25"],
    }


def a15_link() -> dict[str, Any]:
    """The nullity_twelve_curves slice and orbit lie in V, and V's fixed-norm tangent at x0 is the A15 frame."""
    from nullity_twelve_curves import (
        BETA,
        DELTA,
        KAPPA,
        PHASE,
        _base_numerator,
        _phase_vector,
        certify_nullity_twelve_curves,
    )

    numerator, denominator = _base_numerator(BETA, DELTA, KAPPA)
    vector = _phase_vector(numerator / denominator, PHASE)
    z = [vector[k] + sp.I * vector[HALF + k] for k in range(1, HALF)]
    slice_on_v = all(
        sp.cancel(sp.together(sp.expand(value))) == 0 for value in [*minors(z), isotropy(z, sp.Integer(0))]
    )
    certificate = certify_nullity_twelve_curves()
    # A derivation D acts as diag(D, D, D, D) on the octonion blocks of A_5, so it sends u and v through the same
    # 7 x 7 block and fixes mu = y_8 + i y_24; a real skew block preserves u ^ v = 0 and Q.
    preserving = all(
        all(row[0] == 0 for row in matrix)
        and all(value == 0 for value in matrix[0])
        and all(matrix[i][j] == -matrix[j][i] for i in range(8) for j in range(8))
        for matrix in certificate.derivations
    )
    x0 = [int(index in (1, 18)) for index in range(DIM)]
    fixed_norm = [*jacobian(coordinates(x0)), x0]
    frame = certificate.a15_frame
    annihilated = all(
        sum((row[k] * frame[k][col] for k in range(DIM)), Fraction(0)) == 0
        for row in fixed_norm
        for col in range(len(frame[0]))
    )
    return {
        "slice_on_v": slice_on_v,
        "derivations": len(certificate.derivations),
        "derivations_preserve_v": preserving,
        "orbit_rank": len(certificate.orbit_span.pivot_columns),
        "slice_completes_a15": certificate.a15_determinant != 0,
        "fixed_norm_tangent_dimension": DIM - int(fmpz(fixed_norm).rank()),
        "a15_frame_rank": int(
            flint.fmpq_mat([[flint.fmpq(v.numerator, v.denominator) for v in row] for row in frame]).rank()
        ),
        "a15_frame_tangent_to_v": annihilated,
    }


def measure(full: bool = True) -> dict[str, Any]:
    algebra = identity(SIGNS)
    _require(
        all(
            algebra[key]
            for key in (
                "cross_matrix_skew",
                "cross_matrix_annihilates_z",
                "remainder_in_minor_span",
                "kernel_left_identity",
                "kernel_right_identity",
            )
        ),
        "a polynomial identity fails",
    )
    moved = transport()
    _require(moved["agreeing"] == moved["imaginary_basis_elements"], "the transport identity fails")
    _require(scope_matches_witnesses(), "the scope points differ from the certified witness list")
    rows = parallel.ordered_map(certify_point, POINTS, min_items=4)
    for row in rows:
        admit(row)
    others = other_gap_witnesses()
    _require(not others["on_rank_one_locus"], f"V passes through the gap witnesses {others['on_rank_one_locus']}")
    parameterization = rational_chart()
    _require(
        parameterization["solves_f"]
        and parameterization["inverse"]
        and all(parameterization["regular_at_scope_points"].values()),
        "the rational chart fails",
    )
    data: dict[str, Any] = {
        "schema": SCHEMA,
        "versions": {name: importlib.metadata.version(name) for name in ("python-flint", "sympy")},
        "identity": algebra,
        "transport": moved,
        "points": rows,
        "rational_chart": parameterization,
        "other_gap_witnesses": others,
    }
    if full:
        data["hilbert"] = hilbert()
        _require(data["hilbert"]["agrees"], "the Hilbert function of C[z]/(u ^ v, Q) leaves (1 + 7t + 6t^2)/(1 - t)^8")
        data["path"] = path_link()
        data["a15"] = a15_link()
        _require(
            data["path"]["on_v"]
            and data["path"]["rescaled_slice"]
            and all(m["agrees"] for m in data["path"]["principal_minors"].values()),
            "the x0 to e1 + e25 path fails",
        )
        a15 = data["a15"]
        _require(
            a15["slice_on_v"]
            and a15["derivations"] == DERIVATIONS
            and a15["orbit_rank"] == ORBIT_RANK
            and a15["derivations_preserve_v"]
            and a15["slice_completes_a15"]
            and a15["fixed_norm_tangent_dimension"] == a15["a15_frame_rank"] == GERM_DIMENSION - 1
            and a15["a15_frame_tangent_to_v"],
            "the A15 family is not the fixed-norm germ of V at x0",
        )
    return data


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


def _assign(data: dict[str, Any], path: tuple[Any, ...], value: Any) -> None:
    target: Any = data
    for key in path[:-1]:
        target = target[key]
    if value is _MISSING:
        del target[path[-1]]
    else:
        target[path[-1]] = value


def self_test() -> str:
    data = measure(full=False)
    algebra = data["identity"]
    _require(len(algebra["remainder"]) == 168 and algebra["remainder_coefficients"] == [-2, 2], "remainder shape moved")
    flipped = copy.deepcopy(SIGNS)
    flipped[3][12] = -flipped[3][12]
    broken = identity(flipped)
    _require(
        not broken["cross_matrix_skew"]
        and not broken["remainder_in_minor_span"]
        and not broken["kernel_left_identity"],
        "a flipped sign in the sedenion table leaves the skewness, minor-span or left-kernel identity intact",
    )
    _require(transport(conjugate_s=False)["agreeing"] < DIM - 2, "transport without conj(s) still agrees")
    _require(hilbert(top=3)["agrees"], "the Hilbert function of C[z]/(u ^ v, Q) moved")
    _require(not hilbert(quadric=False, top=3)["agrees"], "a minor combination in Q's place keeps the Hilbert series")
    controls = (
        ("e1+e8+e25", ((1, 1), (8, 1), (25, 1))),
        ("e1-e10+e18+e25", ((1, 1), (10, -1), (18, 1), (25, 1))),
        ("e1+e18", ((1, 1), (18, 1))),
    )
    rows = parallel.ordered_map(
        certify_point, [("nonzd-axis", name, support) for name, support in controls], min_items=2
    )
    for (name, _), row in zip(controls, rows, strict=True):
        _require(_refused(row), f"{name} is admitted as a nonzd-axis germ point")
    first = algebra["remainder"][0][4]
    # Each corruption must change the record; the ones on a point row must also fail admission.
    corruptions: tuple[tuple[str, tuple[Any, ...], Any, bool], ...] = (
        ("remainder coefficient", ("identity", "remainder", 0, 4), -first, False),
        ("pivot determinant", ("points", 0, "pivot_determinant"), 0, True),
        ("chart derivative", ("points", 0, "chart", "d_lambda"), [0, 0], True),
        ("nullity", ("points", 3, "nullity"), 8, True),
        ("tangent bound", ("points", 4, "tangent_bound_dimension"), 17, True),
        ("cubic frame", ("points", 5, "cubic_kernel_annihilated"), False, True),
        ("cross rank", ("points", 6, "cross_rank"), CROSS_RANK_BOUND + 1, True),
        ("missing field", ("points", 7, "e8_e24_tangent"), _MISSING, False),
        ("extra null field", ("points", 8, "extra"), None, False),
    )
    for label, path, value, row_level in corruptions:
        damaged = copy.deepcopy(data)
        _assign(damaged, path, value)
        _require(bool(differences(damaged, data)), f"a corrupted {label} passes the comparison")
        if row_level:
            row = damaged["points"][path[1]]
            _require(_refused(row), f"a corrupted {label} is admitted")
    return f"{len(corruptions)} record corruptions, 3 identity mutations and {len(controls)} point controls rejected"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--out", type=Path)
    mode.add_argument("--check", type=Path)
    mode.add_argument("--self-test", action="store_true")
    arguments = parser.parse_args()
    if arguments.self_test:
        print(f"rank_locus_quadric_germ self-test: {self_test()}")
        return 0
    data = measure()
    if arguments.check is not None:
        retained = json.loads(arguments.check.read_text())
        # The record states the library versions that wrote it; the mathematics is compared without them.
        differing = differences(
            {k: v for k, v in retained.items() if k != "versions"}, {k: v for k, v in data.items() if k != "versions"}
        )
        if differing:
            raise SystemExit(f"rank_locus_quadric_germ: {differing} differ from {arguments.check}")
    else:
        arguments.out.parent.mkdir(parents=True, exist_ok=True)
        arguments.out.write_text(json.dumps(data, indent=1, sort_keys=True) + "\n")
    algebra = data["identity"]
    print(f"remainder: {len(algebra['remainder'])} coefficients in {algebra['remainder_coefficients']}")
    for row in data["points"]:
        print(
            f"{row['family']:16s} {row['point']:16s} nullity {row['nullity']:2d} "
            f"dim T {row['tangent_bound_dimension']:2d} V rank {row['jacobian_rank']:2d} "
            f"dF(mu, lambda) {row['chart']['d_mu']} {row['chart']['d_lambda']} cubic frame {row['cubic_kernel_rank']}"
        )
    cone = data["hilbert"]
    print(
        f"hilbert: {cone['values']} agrees {cone['agrees']} "
        f"degree {cone['degree']} real presentation {cone['real_presentation_degree']}"
    )
    print(f"path: {data['path']}")
    print(f"a15: {data['a15']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
