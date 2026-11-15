"""Orbit normal forms of the nullity-4 strata: the kernel quartic, its lines and nodes, and the common kernel.

M(t) is the 15 x 15 skew lower block of the bordered matrix of `nullity4_gauss_image.py` in the frame t = (u, mu, v),
u = (t_1..t_7), mu = t_8, v = (t_9..t_15): M(t) k is the imaginary part of the product t k of imaginary elements of
the complexified 16-dimensional Cayley-Dickson algebra (ledger row A5-461). Q = u.u + mu^2 + v.v, Delta =
(u.u)(v.v) - (u.v)^2 and G = Q^2 - 4 Delta (A5-357). On V(Q) minus V(G) and on V(G) minus V(Q) Delta is nonzero:
G = -4 Delta on V(Q), and 4 Delta = Q^2 on V(G). The plane of u and v is then nondegenerate for the dot product.

Reduction. G_2(C) acts on (u, v) diagonally by automorphisms of the algebra, so M(g t) = g M(t) g^T and K(g t) =
g K(t) for K(t) = ker M(t), and it is transitive on the orthonormal pairs of C^7 (the stabilizer SL_3 of a unit
vector e acts on e-perp = C^3 + C^3* transitively on the pairs (x, xi) with a fixed nonzero pairing). A pair (u, v)
with nondegenerate Gram matrix is a fixed linear combination of an orthonormal pair of its plane, so G_2(C) carries
it into the span of e_1, e_2, and z = (u, mu, v) into the seven coordinates FIXED = (1, 2, 3, 8, 9, 10, 11): the
imaginary part of the octonion subalgebra O' on the units 0, 1, 2, 3, 8, 9, 10, 11. The stabilizer of e_1, e_2 in
G_2(C) is an SL_2 that fixes those seven coordinates and acts on the other eight, COMPLEMENT, as four copies of
its two-dimensional representation. The rotation of the plane (u_j, v_j) by 120 degrees in every j is a further
automorphism (item 2); when u.u = 0 one of the two rotations gives u.u nonzero, because both vanish only for
u.v = v.v = 0, where Delta = 0. SO_3(C) inside the stabilizer of O' in G_2(C) then puts u on e_1 and v in the span
of e_1, e_2, and the scaling gives u = e_1: every point of the two strata is equivalent, by automorphisms and the
scaling, to a point z = (e_1; mu; v_1 e_1 + rho e_2) with rho nonzero (Delta = rho^2).

This producer checks, exactly over Q (items 1 to 7) and modulo 32029 (item 8):

1. For t in the FIXED coordinates M(t) has no entry between FIXED and COMPLEMENT, and the Pfaffian of its
   COMPLEMENT block is G or -G. So at a normal-form point of V(Q) minus V(G) the COMPLEMENT block is invertible and
   K(z) lies in the imaginary part of O', and at one of V(G) minus V(Q) the COMPLEMENT block has rank 6 where
   rank M(z) = 12 (z is not null, so its commutant in the alternative algebra O' is C z): K(z) = C z + l_z with l_z
   the kernel of the COMPLEMENT block, an irreducible SL_2-module. The quadric Q is SL_2-invariant, so Q on K(z) is
   Q(z) s^2 in the coordinate s of z, and l_z is the polar line K(z) n z-perp.
2. The rotation u -> c u + s v, v -> -s u + c v with (c, s) = (-1/2, sqrt(3)/2) satisfies M(g t) = g M(t) g^T, and
   u.u becomes u.u / 4 + 3 v.v / 4 - sqrt(3) u.v / 2 (plus for the inverse rotation).
3. V(Q) minus V(G), z = (e_1; mu; v_1, rho, 0) with mu^2 = -(1 + v_1^2 + rho^2): the vectors
   k(c0, s, t) = (x; r; y), x = (c0, -t, s), r = mu c0 + rho s,
   y = (c0 v_1 - rho t, c0 rho - mu s + v_1 t, -mu t - v_1 s), form K(z) (k(1, 0, 0) = z); Q(k) = 0; the product
   M(k) k' is 2 (s t' - s' t) z; and with n = c0^2 + s^2 + t^2 and q = v_1 (c0^2 - s^2 - t^2) - 2 rho c0 t,
   Delta(k) = -(n (n + r^2) + q^2), so the kernel quartic is G restricted to K(z) = 4 (n (n + r^2) + q^2).
4. No line lies in that quartic. On a line the restrictions satisfy n (n + r^2) = -q^2 as binary quartics, and
   n is not identically zero because the conic n = 0 is smooth. If n and n + r^2 are coprime, both are constant
   multiples of squares A^2 and B^2 of linear forms, and r^2 = beta B^2 - alpha A^2 forces A proportional to B,
   against coprimality. Otherwise a linear form A divides n and r. Either r vanishes on the line, which is then
   the line r = 0, where q = +-i n would need the coefficient -2 rho^2 of q at the mixed monomial to vanish (n has
   none); or r = A up to a constant, n = A B, and B (B + A) is a square, which forces B proportional to A: n is a
   multiple of r^2 on the line, so the line is tangent to the conic n = 0 at a point p0 of r = 0, and q is a
   multiple of r^2 on it. When 1 + v_1^2 = 0 the line r = 0 is itself tangent at its one point of the conic, so
   the line is r = 0, excluded. Otherwise p0 = (rho, -mu, eps) with eps^2 = 1 + v_1^2, the tangent line is
   alpha p0 + lambda (mu, rho, 0), on it r = -eps^2 lambda and n = -eps^2 lambda^2, and the coefficient of
   alpha^2 in q is 2 rho^2 (v_1 - eps), nonzero because (v_1 - eps)(v_1 + eps) = -1.
5. Delta(k) is the squared length of x cross y, so the quartic is singular where x and y are proportional. The
   pencil y = lambda x is a 3 x 3 linear system in (c0, s, t) whose determinant is -chi(lambda),
   chi = lambda^3 + v_1 lambda^2 - (1 + 2 v_1^2 + 2 rho^2) lambda + v_1: the base points of the net of conics x cross
   y are the roots of chi, and the record holds its discriminant.
6. V(G) minus V(Q), z = (e_1; mu; v_1, rho, 0) with mu^2 = -(v_1^2 + (rho - sigma)^2), sigma = +-1: G(z) = 0 and
   Q(z) = 2 sigma rho. For a general t in FIXED and p = (x', y') in COMPLEMENT, the Hessian of G at t sends p to
   4 ((Q - 2 v.v) x' + 2 (u.v) y'; (Q - 2 u.u) y' + 2 (u.v) x'), with determinant 2 Q mu^2 - G of the 2 x 2
   coefficient matrix.
7. The common kernel C(P) = {z': P in K(z')} of a plane P of K(z) that avoids z and differs from l_z is C z at
   every rank-12 normal-form point of V(G) minus V(Q). SL_2 is transitive on the nonzero covectors of l_z, so P is
   spanned by z + p1 and p2 for a basis p1, p2 of l_z. Write z' = a + b with a in FIXED and b in COMPLEMENT. The
   COMPLEMENT components of M(z') p2 = 0 and M(z')(z + p1) = 0 give M(a) l_z = 0 (SL_2-equivariance) and
   b in l_z; the FIXED components give b proportional to p2 and M(z) a proportional to grad G(z), the direction of
   the product on K(z) (A5-491). If M(z) a = 0 then a is a multiple of z and b = 0. Otherwise a = -z cross
   grad G(z) / Q(z) + tau z, since z cross (z cross g) = -Q(z) g for g orthogonal to z, and M(a) l_z = 0 says that
   the COMPLEMENT block of M(h), h = M(z) grad G(z), kills the kernel of the COMPLEMENT block of M(z). That kernel
   is the column space of the Pfaffian adjoint Omega (M Omega = Pf(M) I), so the condition is the vanishing of
   the 8 x 8 matrix W = M_C(h) Omega. The record certifies, by three Groebner bases that equal (1), that the
   entries of W, the relation and 1 - y rho have no common zero with v_1, mu or rho - sigma nonzero: W vanishes
   only at (v_1, mu, rho) = (0, 0, sigma), the point N1 = N3, u.v = 0, mu = 0 of rank 10 (A5-493). The same
   computation with h replaced by z gives W = 0 identically, so the certificate rejects that input.
8. Modulo 32029, at SAMPLES normal-form points of V(G) minus V(Q) with mu nonzero, at SAMPLES with mu = 0 and at
   the 52 exact fixtures of the stratum (which are not in normal form): the rank of M on l_z, the dimension of
   C(l_z) and of its part in FIXED (normal-form points), the dimension of C(P) for a plane P off z other than l_z,
   and whether M(M(z) grad G(z)) is nonzero on l_z. Each fixture row also holds three exact facts: the orbit rank
   and dim L of the retained record `nullity4-gauss-image-result.json`, and whether the real and imaginary parts of
   u and v lie in the imaginary part of one quaternion subalgebra of the real octonions (their span has dimension at
   most 2, or dimension 3 and is closed under the cross product). At all 66 fixtures the orbit rank is 13 exactly
   where u and v are in that position.
9. Modulo 32029, the length of the singular scheme of the kernel quartic and its line certificate
   (`kernel_three_plane_zero_divisors.quadric_point`) at the normal-form points of V(Q) minus V(G) with v_1 and rho
   in 1..GENERAL_RANGE whose mu lies in the field, all off the discriminant of chi, and at the points with v_1 and
   rho in 1..DISCRIMINANT_RANGE on that discriminant. The LONG_POINTS grid points of the retained record whose
   singular scheme has length 5 satisfy u.v = 0 and u.u + 2 v.v = 0, which is v_1 = 0 and 2 rho^2 + 1 = 0 after the
   scaling to u.u = 1: the point where chi = lambda^3. The field holds no square root of 2, so the normal form with
   u = e_1 has no such point over it.

`--write` writes nullity4-orbit-normal-forms-result.json beside this file; `--check` recomputes and compares.

Run from the repository root:
"$PYTHON" docs/evidence/a5-kernel-bundles-residuals/nullity4_orbit_normal_forms.py --check
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(HERE))

import kernel_three_plane_zero_divisors as three_plane  # noqa: E402
import nullity4_gauss_image as gauss  # noqa: E402

import parallel  # noqa: E402

SCHEMA = "a5-kernel-bundles-residuals-nullity4-orbit-normal-forms-v1"
RECORD = HERE / "nullity4-orbit-normal-forms-result.json"
SOURCE_PATHS = (
    HERE / "nullity4_orbit_normal_forms.py",
    HERE / "nullity4_gauss_image.py",
    gauss.RECORD,
    HERE / "kernel_three_plane_zero_divisors.py",
    three_plane.RECORD,
    gauss.FIXTURES,
)
PRIME = gauss.PRIME
UNIT = gauss.ROOT_OF_MINUS_ONE
FIELD = f"Q for the identities and certificates; GF({PRIME}), i = {UNIT}, for the samples and fixtures"
FIXED = (1, 2, 3, 8, 9, 10, 11)
COMPLEMENT = (4, 5, 6, 7, 12, 13, 14, 15)
SAMPLES = 60
QUARTIC_STRATUM = gauss.STRATA[1]
IDENTITIES = (
    "fixed_and_complement_blocks_decouple",
    "complement_pfaffian_is_plus_or_minus_g",
    "rotation_by_120_degrees_is_an_automorphism",
    "rotation_moves_the_norm_of_u",
    "quadric_kernel_parametrization",
    "quadric_kernel_is_null",
    "quadric_kernel_product_is_central",
    "kernel_quartic_formula",
    "line_r_zero_has_mixed_term",
    "tangent_line_restrictions",
    "node_pencil_determinant",
    "quartic_normal_form_on_v_g",
    "hessian_on_the_complement",
    "pfaffian_adjoint",
    "double_cross_product",
)
NODE_CUBIC = "lambda**3 + lambda**2*v1 - lambda*(2*rho**2 + 2*v1**2 + 1) + v1"
NODE_DISCRIMINANT = (
    "4*(8*rho**6 + 25*rho**4*v1**2 + 12*rho**4 + 26*rho**2*v1**4 + 16*rho**2*v1**2 + 6*rho**2 + 9*v1**6 + 3*v1**4"
    " - 5*v1**2 + 1)"
)
KERNEL_PRODUCT = "2*(s*t1 - s1*t)"
# Per sign sigma: nonzero entries of W = M_C(h) Omega modulo the relation, the three Groebner bases that equal (1),
# and the nonzero entries of W when h is replaced by z.
CERTIFICATE = {"entries": 14, "unit_ideals": [True, True, True], "mutation_entries": 0}
# (mu = 0, rank of M on l_z, dim C(l_z), dim of its FIXED part, dim C(P) for P off z other than l_z, M(h) l_z != 0).
SAMPLE_TALLY = {"mu nonzero": [[False, 8, 3, 3, 1, True, SAMPLES]], "mu zero": [[True, 6, 6, 4, 1, True, SAMPLES]]}
# (mu = 0, rank of M on l_z, dim C(l_z), dim C(P) for P off z other than l_z, M(h) l_z != 0, exact orbit rank,
# u and v in one quaternion subalgebra, exact dim L) at the fixtures.
FIXTURE_TALLY = [
    [False, 8, 3, 1, True, 13, True, 6, 13],
    [False, 8, 3, 1, True, 16, False, 2, 2],
    [True, 6, 6, 1, True, 13, True, 12, 16],
    [True, 6, 6, 1, True, 16, False, 2, 21],
]
# (stratum, exact orbit rank, u and v in one quaternion subalgebra) at the 66 fixtures.
POSITION_TALLY = [
    [gauss.STRATA[1], 13, True, 29],
    [gauss.STRATA[1], 16, False, 23],
    [gauss.STRATA[2], 16, False, 2],
    [gauss.STRATA[0], 13, True, 9],
    [gauss.STRATA[0], 16, False, 3],
]
GENERAL_RANGE = 11
DISCRIMINANT_RANGE = 400
LONG_POINTS = 32
# (length of the singular scheme, Hilbert value of the trisecant ideal: 0 certifies that no line lies in the quartic).
SCHEME_TALLY = {"off the discriminant": [[3, 0, 68]], "on the discriminant": [[4, 0, 5]]}

V1, RHO, MU, EPS, Y, W = sp.symbols("v1 rho mu eps y w")
C0, S, T, C1, S1, T1 = sp.symbols("c0 s t c1 s1 t1")
Vector = list[Any]


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def block(vector: Sequence[Any], rows: Sequence[int], columns: Sequence[int]) -> sp.Matrix:
    """The entries of M(vector) in the given rows and columns, numbered 1 to 15."""
    return sp.Matrix(
        len(rows),
        len(columns),
        lambda a, b: (
            0 if rows[a] == columns[b] else gauss.SIGNS[rows[a]][columns[b]] * vector[(rows[a] ^ columns[b]) - 1]
        ),
    )


ALL = tuple(range(1, 16))


def frame(u: Sequence[Any], middle: Any, v: Sequence[Any]) -> Vector:
    """The frame vector (u; mu; v) with u and v in the span of e_1, e_2, e_3."""
    vector: Vector = [sp.Integer(0)] * 15
    vector[0:3], vector[7], vector[8:11] = list(u), middle, list(v)
    return vector


def pfaffian(matrix: sp.Matrix) -> Any:
    """The Pfaffian of a skew matrix of even order by expansion along the first row."""
    order = matrix.shape[0]
    if order == 0:
        return sp.Integer(1)
    total = sp.Integer(0)
    for column in range(1, order):
        if matrix[0, column] != 0:
            keep = [index for index in range(order) if index not in (0, column)]
            total += (-1) ** (column - 1) * matrix[0, column] * pfaffian(matrix.extract(keep, keep))
    return sp.expand(total)


def pfaffian_adjoint(matrix: sp.Matrix) -> sp.Matrix:
    """Omega with matrix * Omega = Pf(matrix) I: its (i, j) entry, i < j, is (-1)^(i + j) Pf without i and j."""
    order = matrix.shape[0]
    adjoint = sp.zeros(order, order)
    for row in range(order):
        for column in range(row + 1, order):
            keep = [index for index in range(order) if index not in (row, column)]
            value = (-1) ** (row + column) * pfaffian(matrix.extract(keep, keep))
            adjoint[row, column], adjoint[column, row] = value, -value
    return adjoint


def _forms(vector: Sequence[Any]) -> tuple[Any, Any, Any]:
    """Q, Delta and G at a frame vector."""
    u, v = vector[0:7], vector[8:15]
    uu, vv = sum(a * a for a in u), sum(a * a for a in v)
    uv = sum(a * b for a, b in zip(u, v, strict=True))
    q = uu + vector[7] ** 2 + vv
    delta = uu * vv - uv**2
    return q, delta, q**2 - 4 * delta


QUADRIC_RELATION = MU**2 + 1 + V1**2 + RHO**2


def _reduce(expression: Any, relation: Any = QUADRIC_RELATION) -> Any:
    return sp.rem(sp.expand(expression), relation, MU)


def _zero(expressions: Any, relation: Any = QUADRIC_RELATION) -> bool:
    return all(_reduce(expression, relation) == 0 for expression in expressions)


def quadric_point() -> Vector:
    return frame([1, 0, 0], MU, [V1, RHO, 0])


def kernel_vector(c0: Any, s: Any, t: Any) -> Vector:
    """k(c0, s, t) of item 3."""
    return frame(
        [c0, -t, s],
        MU * c0 + RHO * s,
        [c0 * V1 - RHO * t, c0 * RHO - MU * s + V1 * t, -MU * t - V1 * s],
    )


def _quartic_parts(c0: Any, s: Any, t: Any) -> tuple[Any, Any, Any]:
    return c0**2 + s**2 + t**2, MU * c0 + RHO * s, V1 * (c0**2 - s**2 - t**2) - 2 * RHO * c0 * t


def _general_fixed() -> tuple[tuple[Any, ...], Vector]:
    symbols = sp.symbols("a1 a2 a3 am b1 b2 b3")
    return symbols, frame(symbols[0:3], symbols[3], symbols[4:7])


def fixed_and_complement_blocks_decouple() -> bool:
    _, vector = _general_fixed()
    return all(entry == 0 for entry in block(vector, FIXED, COMPLEMENT))


def complement_pfaffian_sign() -> int:
    """The sign e with Pf(M_C(t)) = e G(t) for t in FIXED, or 0 when neither sign holds."""
    _, vector = _general_fixed()
    value, g = pfaffian(block(vector, COMPLEMENT, COMPLEMENT)), sp.expand(_forms(vector)[2])
    return next((sign for sign in (1, -1) if sp.expand(value - sign * g) == 0), 0)


def complement_pfaffian_is_plus_or_minus_g() -> bool:
    return complement_pfaffian_sign() != 0


def _rotation(sign: int) -> sp.Matrix:
    cosine, sine = -sp.Rational(1, 2), sign * sp.sqrt(3) / 2
    matrix = sp.zeros(15, 15)
    for index in range(7):
        matrix[index, index], matrix[index, 8 + index] = cosine, sine
        matrix[8 + index, index], matrix[8 + index, 8 + index] = -sine, cosine
    matrix[7, 7] = 1
    return matrix


def rotation_by_120_degrees_is_an_automorphism() -> bool:
    symbols = sp.symbols("t1:16")
    for sign in (1, -1):
        rotation = _rotation(sign)
        moved = list(rotation * sp.Matrix(symbols))
        difference = block(moved, ALL, ALL) - rotation * block(symbols, ALL, ALL) * rotation.T
        if any(sp.expand(entry) != 0 for entry in difference):
            return False
    return True


def rotation_moves_the_norm_of_u() -> bool:
    symbols = sp.symbols("t1:16")
    u, v = symbols[0:7], symbols[8:15]
    uu, vv = sum(a * a for a in u), sum(a * a for a in v)
    uv = sum(a * b for a, b in zip(u, v, strict=True))
    for sign in (1, -1):
        moved = list(_rotation(sign) * sp.Matrix(symbols))
        expected = uu / 4 + 3 * vv / 4 - sign * sp.sqrt(3) * uv / 2
        if sp.expand(sum(a * a for a in moved[0:7]) - expected) != 0:
            return False
    return True


def quadric_kernel_parametrization() -> bool:
    z, k = quadric_point(), kernel_vector(C0, S, T)
    at_one = [sp.expand(a - b) for a, b in zip(kernel_vector(1, 0, 0), z, strict=True)]
    return _zero(block(z, ALL, ALL) * sp.Matrix(k)) and all(entry == 0 for entry in at_one)


def quadric_kernel_is_null() -> bool:
    return _zero([_forms(kernel_vector(C0, S, T))[0]])


def kernel_product() -> str:
    """The factor f with M(k) k' = f z for k = k(c0, s, t), k' = k(c1, s1, t1); empty when no such f exists."""
    z = quadric_point()
    product = block(kernel_vector(C0, S, T), ALL, ALL) * sp.Matrix(kernel_vector(C1, S1, T1))
    factor = _reduce(product[0])
    if not _zero([entry - factor * coordinate for entry, coordinate in zip(product, z, strict=True)]):
        return ""
    return str(sp.factor(factor))


def quadric_kernel_product_is_central() -> bool:
    return kernel_product() != ""


def kernel_quartic_formula() -> bool:
    _, delta, g = _forms(kernel_vector(C0, S, T))
    n, r, q = _quartic_parts(C0, S, T)
    quartic = n * (n + r**2) + q**2
    at_z = _reduce(_forms(quadric_point())[1] - RHO**2)
    return _zero([delta + quartic, g - 4 * quartic]) and at_z == 0


def line_r_zero_has_mixed_term() -> bool:
    tau, theta = sp.symbols("tau theta")
    n, r, q = (sp.expand(part) for part in _quartic_parts(RHO * tau, -MU * tau, theta))
    mixed_q = sp.Poly(q, tau, theta).coeff_monomial(tau * theta)
    mixed_n = sp.Poly(n, tau, theta).coeff_monomial(tau * theta)
    return r == 0 and sp.expand(mixed_q + 2 * RHO**2) == 0 and mixed_n == 0


def tangent_line_restrictions() -> bool:
    alpha, lam = sp.symbols("alpha lambda")

    def reduce(expression: Any) -> Any:
        return sp.rem(_reduce(expression), EPS**2 - 1 - V1**2, EPS)

    point = (alpha * RHO + lam * MU, -alpha * MU + lam * RHO, alpha * EPS)
    n, r, q = _quartic_parts(*point)
    leading = sp.Poly(reduce(q), alpha, lam).coeff_monomial(alpha**2)
    return (
        reduce(r + EPS**2 * lam) == 0
        and reduce(n + EPS**2 * lam**2) == 0
        and reduce(leading - 2 * RHO**2 * (V1 - EPS)) == 0
        and reduce((V1 - EPS) * (V1 + EPS) + 1) == 0
    )


def node_cubic() -> Any:
    lam = sp.Symbol("lambda")
    return lam**3 + V1 * lam**2 - (1 + 2 * V1**2 + 2 * RHO**2) * lam + V1


def node_pencil_determinant() -> bool:
    lam = sp.Symbol("lambda")
    k = kernel_vector(C0, S, T)
    rows = [sp.expand(k[8 + index] - lam * k[index]) for index in range(3)]
    pencil = sp.Matrix(3, 3, lambda a, b: sp.Poly(rows[a], C0, S, T).coeff_monomial((C0, S, T)[b]))
    return _reduce(pencil.det() + node_cubic()) == 0


def _quartic_relation(sigma: int) -> Any:
    return MU**2 + V1**2 + (RHO - sigma) ** 2


def quartic_normal_form_on_v_g() -> bool:
    z = frame([1, 0, 0], MU, [V1, RHO, 0])
    q, delta, g = _forms(z)
    return all(_zero([g, q - 2 * sigma * RHO, delta - RHO**2], _quartic_relation(sigma)) for sigma in (1, -1))


def hessian_on_the_complement() -> bool:
    symbols, vector = _general_fixed()
    direction = sp.symbols("x4 x5 x6 x7 y4 y5 y6 y7")
    step = sp.Symbol("step")
    moved = list(vector)
    for index, value in zip(COMPLEMENT, direction, strict=True):
        moved[index - 1] = step * value
    all_symbols = sp.symbols("t1:16")
    g = sp.expand(_forms(all_symbols)[2])
    at = dict(zip(all_symbols, moved, strict=True))
    image = [sp.expand(sp.diff(sp.diff(g, symbol).subs(at), step).subs(step, 0)) for symbol in all_symbols]
    u, v = vector[0:7], vector[8:15]
    uu, vv = sum(a * a for a in u), sum(a * a for a in v)
    uv = sum(a * b for a, b in zip(u, v, strict=True))
    q, _, g_fixed = _forms(vector)
    expected: Vector = [sp.Integer(0)] * 15
    for offset in range(4):
        x, y = direction[offset], direction[4 + offset]
        expected[3 + offset] = 4 * ((q - 2 * vv) * x + 2 * uv * y)
        expected[11 + offset] = 4 * ((q - 2 * uu) * y + 2 * uv * x)
    determinant = (q - 2 * vv) * (q - 2 * uu) - 4 * uv**2
    return (
        all(sp.expand(a - b) == 0 for a, b in zip(image, expected, strict=True))
        and sp.expand(determinant - (2 * q * symbols[3] ** 2 - g_fixed)) == 0
    )


def pfaffian_adjoint_identity() -> bool:
    _, vector = _general_fixed()
    matrix = block(vector, COMPLEMENT, COMPLEMENT)
    product, value = matrix * pfaffian_adjoint(matrix), pfaffian(matrix)
    return all(
        sp.expand(product[row, column] - (value if row == column else 0)) == 0
        for row in range(8)
        for column in range(8)
    )


def double_cross_product() -> bool:
    """z cross (z cross g) = -Q(z) g + (z.g) z on the seven coordinates of O', with Q the sum of their squares."""
    symbols, vector = _general_fixed()
    other = sp.symbols("g1:8")
    matrix = block(vector, FIXED, FIXED)
    image = matrix * (matrix * sp.Matrix(other))
    norm = sum(a * a for a in symbols)
    pairing = sum(a * b for a, b in zip(symbols, other, strict=True))
    expected = [-norm * b + pairing * a for a, b in zip(symbols, other, strict=True)]
    return all(sp.expand(a - b) == 0 for a, b in zip(image, expected, strict=True))


CHECKS: dict[str, Callable[[], bool]] = {
    "fixed_and_complement_blocks_decouple": fixed_and_complement_blocks_decouple,
    "complement_pfaffian_is_plus_or_minus_g": complement_pfaffian_is_plus_or_minus_g,
    "rotation_by_120_degrees_is_an_automorphism": rotation_by_120_degrees_is_an_automorphism,
    "rotation_moves_the_norm_of_u": rotation_moves_the_norm_of_u,
    "quadric_kernel_parametrization": quadric_kernel_parametrization,
    "quadric_kernel_is_null": quadric_kernel_is_null,
    "quadric_kernel_product_is_central": quadric_kernel_product_is_central,
    "kernel_quartic_formula": kernel_quartic_formula,
    "line_r_zero_has_mixed_term": line_r_zero_has_mixed_term,
    "tangent_line_restrictions": tangent_line_restrictions,
    "node_pencil_determinant": node_pencil_determinant,
    "quartic_normal_form_on_v_g": quartic_normal_form_on_v_g,
    "hessian_on_the_complement": hessian_on_the_complement,
    "pfaffian_adjoint": pfaffian_adjoint_identity,
    "double_cross_product": double_cross_product,
}


def identity(name: str) -> bool:
    return CHECKS[name]()


def common_kernel_matrix(sigma: int, mutation: bool = False) -> list[Any]:
    """The nonzero entries of W = M_C(h) Omega modulo the relation of item 6; with `mutation`, h is z."""
    relation = _quartic_relation(sigma)
    z = frame([1, 0, 0], MU, [V1, RHO, 0])
    symbols, vector = _general_fixed()
    g = sp.expand(_forms(vector)[2])
    at = dict(zip(symbols, [1, 0, 0, MU, V1, RHO, 0], strict=True))
    gradient = [sp.diff(g, symbol).subs(at) for symbol in symbols]
    image = block(z, FIXED, FIXED) * sp.Matrix(gradient)
    h: Vector = [sp.Integer(0)] * 15
    for index, value in zip(FIXED, image, strict=True):
        h[index - 1] = sp.expand(value)
    adjoint = pfaffian_adjoint(block(z, COMPLEMENT, COMPLEMENT))
    product = block(z if mutation else h, COMPLEMENT, COMPLEMENT) * adjoint
    return sorted({_reduce(entry, relation) for entry in product} - {0}, key=str)


def common_kernel_certificate(sigma: int) -> dict[str, Any]:
    """Item 7 at the sign sigma: the entry count, the three unit ideals and the entry count of the mutation."""
    relation = _quartic_relation(sigma)
    entries = common_kernel_matrix(sigma)
    units = []
    for factor in (V1, MU, RHO - sigma):
        basis = sp.groebner([*entries, relation, 1 - Y * RHO, 1 - W * factor], Y, W, MU, V1, RHO, order="grevlex")
        units.append(list(basis.exprs) == [1])
    return {
        "entries": len(entries),
        "unit_ideals": units,
        "mutation_entries": len(common_kernel_matrix(sigma, mutation=True)),
    }


def _combine(coefficients: Sequence[int], vectors: Sequence[Sequence[int]]) -> list[int]:
    return [
        sum(c * vector[index] for c, vector in zip(coefficients, vectors, strict=True)) % PRIME for index in range(15)
    ]


def _gradient_g(z: Sequence[int]) -> list[int]:
    u, v = z[0:7], z[8:15]
    uu, vv = sum(a * a for a in u), sum(a * a for a in v)
    uv = sum(a * b for a, b in zip(u, v, strict=True))
    q = uu + z[7] ** 2 + vv
    first = [4 * q * a - 8 * (vv * a - uv * b) for a, b in zip(u, v, strict=True)]
    second = [4 * q * b - 8 * (uu * b - uv * a) for a, b in zip(u, v, strict=True)]
    return [value % PRIME for value in [*first, 4 * q * z[7], *second]]


def _common_kernel(vectors: Sequence[Sequence[int]]) -> gauss.Matrix:
    rows: gauss.Matrix = []
    for vector in vectors:
        rows += gauss._block(vector)
    return gauss._nullspace(rows)


def point_facts(z: Sequence[int]) -> list[Any] | None:
    """(mu = 0, rank on l_z, dim C(l_z), dim of its FIXED part, dim C(P), M(h) l_z != 0), or None off rank 12."""
    matrix = gauss._block(z)
    if gauss._rank(matrix) != 12:
        return None
    polar = gauss._nullspace([*matrix, [value % PRIME for value in z]])
    _require(len(polar) == 2, "the polar line is not a line")
    ranks = {gauss._rank(gauss._block(_combine(pair, polar))) for pair in ((1, 0), (0, 1), (1, 1), (2, 5))}
    _require(len(ranks) == 1, "the rank of M varies on the sampled vectors of the polar line")
    common = _common_kernel(polar)
    fixed = len(common) - gauss._rank([[vector[index - 1] for vector in common] for index in COMPLEMENT])
    plane = [_combine((1, 1, 0), [list(z), *polar]), polar[1]]
    h = [sum(a * b for a, b in zip(row, _gradient_g(z), strict=True)) % PRIME for row in matrix]
    image = [
        sum(a * b for a, b in zip(row, vector, strict=True)) % PRIME for vector in polar for row in gauss._block(h)
    ]
    return [z[7] % PRIME == 0, ranks.pop(), len(common), fixed, len(_common_kernel(plane)), any(image)]


def _normal_form(job: tuple[str, int]) -> list[int]:
    """A normal-form point (e_1; mu; v_1, rho, 0) of V(G) with sigma = 1, from sha256 of the label and counter."""
    label, counter = job
    points = gauss.Points(f"nullity4-orbit-normal-forms:{label}:{counter}")
    while True:
        a, c = points.value(), points.value()
        if a == 0 or c == 0:
            continue
        if label == "mu zero":
            rho = a
            v1, middle = UNIT * (rho - 1) % PRIME, 0
        else:
            quotient = c * c * pow(a, -1, PRIME) % PRIME
            v1 = (a - quotient) * pow(2, -1, PRIME) % PRIME
            rho = (1 + (a + quotient) * pow(2 * UNIT, -1, PRIME)) % PRIME
            middle = c
        if rho in (0, 1):
            continue
        z = [1, 0, 0, 0, 0, 0, 0, middle, v1, rho, 0, 0, 0, 0, 0]
        if gauss._rank(gauss._block(z)) == 12:
            return z


def sample_facts(job: tuple[str, int]) -> list[Any]:
    z = _normal_form(job)
    q = sum(value * value for value in z) % PRIME
    _require(q == 2 * z[9] % PRIME and q != 0, "a sampled point is off V(G) minus V(Q)")
    facts = point_facts(z)
    _require(facts is not None, "a sampled point has another rank")
    return list(facts or [])


def in_one_quaternion_subalgebra(split: Sequence[int]) -> bool:
    """Whether the real and imaginary parts of u and v at an integer split point lie in one associative 3-plane."""
    parts = [[0] * 7 for _ in range(4)]
    for index, value in enumerate(split):
        unit = index + 1
        if unit == 8:
            continue
        power = unit.bit_count() % 4
        row = (0 if unit < 8 else 2) + power % 2
        parts[row][(unit & 7) - 1] = -value if power >= 2 else value
    span = sp.Matrix(parts)
    rank = span.rank()
    if rank != 3:
        return bool(rank < 3)
    basis = [parts[index] for index in span.T.rref()[1]]
    for first, second in ((0, 1), (0, 2), (1, 2)):
        cross = [
            sum(
                gauss.SIGNS[row][column] * basis[first][(row ^ column) - 1] * basis[second][column - 1]
                for column in range(1, 8)
                if column != row
            )
            for row in range(1, 8)
        ]
        if sp.Matrix([*basis, cross]).rank() != 3:
            return False
    return True


def fixture_facts(job: tuple[int, str, list[int]]) -> list[Any]:
    """The modular facts of `point_facts` without the FIXED part, then orbit rank, quaternion position and dim L."""
    number, _, split = job
    facts = point_facts(gauss._twist(split, UNIT))
    _require(facts is not None, "a fixture has another rank")
    retained = json.loads(gauss.RECORD.read_text(encoding="utf-8"))
    return [
        *(value for index, value in enumerate(facts or []) if index != 3),
        retained["exact_fixture_orbit_ranks"][number],
        in_one_quaternion_subalgebra(split),
        retained["exact_fixture_invariants"][number]["fiber_dimension"],
    ]


def _square_root(value: int) -> int | None:
    value %= PRIME
    if value and pow(value, (PRIME - 1) // 2, PRIME) != 1:
        return None
    return next(root for root in range(PRIME) if root * root % PRIME == value)


def scheme_jobs() -> dict[str, list[tuple[int, int]]]:
    """The normal-form points (v_1, rho) of item 9 whose mu lies in the field, off and on the discriminant."""
    lam = sp.Symbol("lambda")
    polynomial = sp.Poly(sp.discriminant(node_cubic(), lam), V1, RHO)
    terms = [(int(coefficient), powers) for powers, coefficient in polynomial.terms()]

    def value(v1: int, rho: int) -> int:
        return sum(c * pow(v1, a, PRIME) * pow(rho, b, PRIME) for c, (a, b) in terms) % PRIME

    def in_field(v1: int, rho: int) -> bool:
        return _square_root(-(1 + v1 * v1 + rho * rho)) is not None

    small = range(1, GENERAL_RANGE + 1)
    wide = range(1, DISCRIMINANT_RANGE + 1)
    return {
        "off the discriminant": [(a, b) for a in small for b in small if value(a, b) and in_field(a, b)],
        "on the discriminant": [(a, b) for a in wide for b in wide if not value(a, b) and in_field(a, b)],
    }


def scheme_facts(job: tuple[int, int]) -> list[Any]:
    """(length of the singular scheme, trisecant Hilbert value) of the kernel quartic at (e_1; mu; v_1, rho, 0)."""
    v1, rho = job
    middle = _square_root(-(1 + v1 * v1 + rho * rho))
    _require(middle is not None, "mu is not in the field")
    z = [1, 0, 0, 0, 0, 0, 0, middle or 0, v1, rho, 0, 0, 0, 0, 0]
    _require(gauss._rank(gauss._block(z)) == 12, "a normal-form point of V(Q) has another rank")
    row = three_plane.quadric_point(three_plane._untwist(z))
    _require(row["quadric_gram_rank"] == 0 and row["quartic_nonzero"], "the point is off V(Q) minus V(G)")
    return [row["singular_scheme_length"], row["trisecant_hilbert_value"]]


def long_grid_points() -> list[int]:
    """The grid points of the retained record with singular scheme of length 5, and those with u.v = u.u + 2 v.v = 0."""
    points = json.loads(three_plane.RECORD.read_text(encoding="utf-8"))["grid"]["long_scheme_points"]
    special = 0
    for split in points:
        z = gauss._twist(split, UNIT)
        uu, vv = sum(a * a for a in z[0:7]), sum(a * a for a in z[8:15])
        uv = sum(a * b for a, b in zip(z[0:7], z[8:15], strict=True))
        special += uv % PRIME == 0 and (uu + 2 * vv) % PRIME == 0
    return [len(points), special]


def position_facts(job: tuple[int, str, list[int]]) -> list[Any]:
    """(stratum, exact orbit rank of the retained record, quaternion position) at one fixture."""
    number, stratum, split = job
    retained = json.loads(gauss.RECORD.read_text(encoding="utf-8"))
    return [stratum, retained["exact_fixture_orbit_ranks"][number], in_one_quaternion_subalgebra(split)]


def _tally(rows: Sequence[Sequence[Any]]) -> list[list[Any]]:
    counts = Counter(tuple(row) for row in rows)
    return [[*key, counts[key]] for key in sorted(counts)]


def _inputs() -> dict[str, str]:
    return {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in SOURCE_PATHS}


def compute() -> dict[str, Any]:
    names = list(IDENTITIES)
    identities = dict(zip(names, parallel.ordered_map(identity, names, min_items=2), strict=True))
    certificates = parallel.ordered_map(common_kernel_certificate, [1, -1], min_items=2)
    samples = {}
    for label in ("mu nonzero", "mu zero"):
        jobs = [(label, counter) for counter in range(SAMPLES)]
        samples[label] = _tally(parallel.ordered_map(sample_facts, jobs, min_items=2))
    fixtures = [job for job in gauss._fixture_splits() if job[1] == QUARTIC_STRATUM]
    record: dict[str, Any] = {
        "schema": SCHEMA,
        "field": FIELD,
        "inputs": _inputs(),
        "identities": identities,
        "complement_pfaffian_sign": complement_pfaffian_sign(),
        "kernel_product": kernel_product(),
        "node_cubic": str(node_cubic()),
        "node_discriminant": str(sp.factor(sp.discriminant(node_cubic(), sp.Symbol("lambda")))),
        "common_kernel_certificate": {"sigma = 1": certificates[0], "sigma = -1": certificates[1]},
        "samples": samples,
        "fixtures": _tally(parallel.ordered_map(fixture_facts, fixtures, min_items=2)),
        "quaternion_position": _tally(parallel.ordered_map(position_facts, gauss._fixture_splits(), min_items=2)),
        "singular_schemes": {
            label: _tally(parallel.ordered_map(scheme_facts, jobs, min_items=2))
            for label, jobs in scheme_jobs().items()
        },
        "long_grid_points": long_grid_points(),
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
        "identities": dict.fromkeys(IDENTITIES, True),
        "complement_pfaffian_sign": 1,
        "kernel_product": KERNEL_PRODUCT,
        "node_cubic": NODE_CUBIC,
        "node_discriminant": NODE_DISCRIMINANT,
        "common_kernel_certificate": {"sigma = 1": dict(CERTIFICATE), "sigma = -1": dict(CERTIFICATE)},
        "samples": {label: [list(row) for row in rows] for label, rows in SAMPLE_TALLY.items()},
        "fixtures": [list(row) for row in FIXTURE_TALLY],
        "quaternion_position": sorted(list(row) for row in POSITION_TALLY),
        "singular_schemes": {label: [list(row) for row in rows] for label, rows in SCHEME_TALLY.items()},
        "long_grid_points": [LONG_POINTS, LONG_POINTS],
        "pass": True,
    }


def verdict(record: dict[str, Any]) -> list[str]:
    """The reasons the record fails its own rules; empty when it passes. The comparison is on serialized text."""
    expected = expected_record()
    problems = []
    messages = {
        "inputs": "the input digests differ from the files",
        "identities": "an exact identity fails",
        "complement_pfaffian_sign": "the Pfaffian of the complement block is not G",
        "kernel_product": "the product on the kernel of the quadric normal form differs",
        "node_cubic": "the cubic of the base points differs",
        "node_discriminant": "the discriminant of the cubic of the base points differs",
        "common_kernel_certificate": "the common-kernel certificate fails, or it accepts the mutation",
        "samples": "the sampled normal-form points differ from their pinned tallies",
        "fixtures": "the fixtures differ from their pinned tallies",
        "quaternion_position": "a fixture has orbit rank 13 off the quaternion position, or the reverse",
        "singular_schemes": "the singular schemes of the sampled kernel quartics differ from their pinned tallies",
        "long_grid_points": "a grid point with a singular scheme of length 5 is off u.v = u.u + 2 v.v = 0",
    }
    for group, message in messages.items():
        if json.dumps(record.get(group), sort_keys=True) != json.dumps(expected[group], sort_keys=True):
            problems.append(message)
    if record.get("pass") is not True:
        problems.append("the record states that it fails")
    if not problems and _serialized(record) != _serialized(expected):
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
    print(f"pass: {len(record['identities'])} identities, 2 common-kernel certificates, {2 * SAMPLES} samples")


if __name__ == "__main__":
    main()
