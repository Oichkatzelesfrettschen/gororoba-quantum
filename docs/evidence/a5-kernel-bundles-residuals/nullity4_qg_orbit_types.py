"""Closes the orbit types of the real nullity-4 points of V(Q) n V(G) that the normal form z(s) leaves open.

The types are the type s = +-1, the point (beta, lambda) = (i, 0) of the conic, the lemma on dim C(P) = 5 and the types
with u.u = 0.

Setting. M(t), Q, Delta, G, K(z) = ker M(z), P = K n conj(z)-perp, C(P) = ker M(p1) n ker M(p2) and
dim L = 2 (dim C(P) - 2) are those of nullity4_qg_intersection.py (frame t = (u, mu, v), conj the entrywise
conjugate of the frame vector). A
point z of V(Q) n V(G) with rank M(z) = 12 lies in K(z); the vectors of K outside the cone J = {k: nullity M(k) > 3}
have kernel K, and the kernel plane of a point z' of K outside J is the Hermitian complement of z' in K. G_2(C) acts by
diag(g, 1, g) with M(g t) = g M(t) g^T, and the 120-degree rotation R of the planes (u_j, v_j) is a real orthogonal
automorphism of the same kind (nullity4_orbit_normal_forms.py).

1. Type s = +-1 (mu = 0 on K). The 14 derivations of the octonions give 14 matrices diag(D, 0, D) that satisfy
   M(D t) = D M(t) + M(t) D^T, are skew and have rank 14 (exact checks); they are the Lie algebra of G_2(C), which is
   connected, so G_2(C) preserves
   E_eps = {(a; 0; eps i a)}, eps = +-1, and so does R, which multiplies E_eps by a scalar. E_+ and E_- are Hermitian
   orthogonal (A5-550 records the same invariance for the polar line). At s = 1 (eps = 1) and s = -1 (eps = -1) the
   plane P_x = <k1, k2> lies in E_eps, K = P_x + C q with q
   in E_(-eps), q lies on the lines l_y and l_z (q in P_y and P_z) and has nullity 7, so q is in J, and q spans the
   Hermitian complement of P_x in K (the vector that the witness construction returns). For every g in G_2(C) and
   every scalar c, the point z' = c g z(+-1) has K(z') = g K, P_x(z') = g P_x in E_eps, and the Hermitian
   complement of g P_x in g K contains g q in E_(-eps), so it is C g q. The plane P(z') equals g P_x only when z'
   lies on C g q, which lies in g J, while z' has nullity 3. Hence no real point of the type s = +-1 has the kernel
   plane P_x, dim C(P) = 7 never meets a kernel plane, and dim L = 10 does not occur there.
2. The point (i, 0). With s = 1 / sigma the vectors z~ = sigma^2 z(1/sigma), k~0 = sigma^2 k0(1/sigma),
   k~1 = sigma k1(1/sigma), k~2 = sigma k2(1/sigma) are polynomial in sigma, and sigma = 0 is (beta, lambda) = (i, 0).
   The identities of qg for the chart s hold in sigma (the 12 x 12 Pfaffian of M(z~) is 8 (sigma^2 + 1)^6 and the
   Pfaffian of M on K~ is the substitution of the sextic of qg). At sigma = 0 the three vectors are independent,
   rank M(z~) = 12, the Pfaffian on K~ is 8 i c0^4 c1 c2, so J is the three planes P~x = <k~1, k~2>, P~y = <k~2, k~0>
   and P~z = <k~1, k~0>, with dim C = 5, 4, 4, and the Hermitian complements of the three planes in K~ are points of
   K~ outside J with dim L = 6, 4, 4 (exact witnesses). The point (-i, 0) is s = 0 of the chart s. On the pencil
   M(c1 k~1 + c2 k~2) the generic rank is 8 and the principal 8 x 8 Pfaffians have no common zero in either chart of
   the pencil, so every vector of P~x has nullity 7. Scaling by -1 sends (x; beta; lambda x + w) to
   (x'; -beta; lambda x' - w) with x' = -x, so lambda alone labels the type, s and 1 / s are the same orbit type and
   sigma = 0 is the type of s = 0 (argument; the equality of the facts below with the row s = 0 of qg is the exact
   cross-check).
3. The lemma on dim C(P) = 5. For s with s^2 + 1 nonzero, the rank of each plane stack over Q(i)[s] drops only at
   the roots of a nonzero maximal minor, which is computed here exactly and factored over Q(i): the minor of P_x is
   -512 s^2 (s - 1)^3 (s + 1)^3, of P_y is 64 i s^2 (s - 1)^2 (s + 1)^2 (s - i)^3 (s + i)^3 (s^2 - 4 i s - 1)^3 and of
   P_z the same with s^2 + 4 i s - 1. The exact values at s = 0, 1, -1 give dim C = (5, 4, 4), (7, 4, 4), (7, 4, 4); at
   a root of D2 = s^2 - 4 i s - 1 (resp. D1 = s^2 + 4 i s - 1) the plane P_y (resp. P_z) is P_x, because
   D2 k0 + N2 k1 = N2 k1 and D2, N2 have no common root, so its dimension is that of P_x, 5. Hence on the chart s
   the dimensions of the planes of J are (5, 4, 4) except (7, 4, 4) at s = +-1 and (5, 5, 4), (5, 4, 5) at the roots
   of D2, D1, and a plane of K outside J has C(P) = K (dimension 3). So a plane with dim C(P) = 5 is P_x, s^2 is
   other than 1, and every vector of P_x has nullity 7 (qg item 7), and at sigma = 0 the same holds. The statement is
   complex-algebraic: it concerns the plane, not the Hermitian form.
4. Types with u.u = 0. If mu = 0 and Q = Delta = 0 then (u.u)^2 + (u.v)^2 = 0. The rotated norms n_(+-) of u are
   u.u / 4 + 3 v.v / 4 -+ sqrt(3) u.v / 2, with n_+ n_- = ((u.u + 3 v.v)^2 - 12 (u.v)^2) / 16, n_+ - n_- = -sqrt(3)
   u.v and n_+ + n_- = (u.u + 3 v.v) / 2, so for u.u = 0 both vanish only when u.v = v.v = 0, which with Q = 0 gives
   mu = 0 and a totally isotropic pair (A5-359, A5-360: rank M at most 10, no nullity-4 point). Every other point
   with u.u = 0 is the image under R^(+-1) of a point with u.u nonzero, which is a conic point; on z(s) the product
   n_+ n_- is (D1 D2)^2 / 16 with D1 D2 = s^4 + 14 s^2 + 1, so the rank-12 points with u.u = 0 and mu, u, v not all
   isotropic are the images under R^(+-1) of the four chart points at the roots of D1 D2 (two orbit types, exchanged in
   pairs by s -> 1 / s) (a point with u.u nonzero
   is a conic point, and R preserves rank, nullity, C(P), the Hermitian form and P). No further orbit type of rank
   12 exists. The orbit types of Lopatin and Zubkov (arXiv 2208.08122, Theorem 4.4) with Delta = 0 and Q = 0 map to
   these clauses: pairs (u, v) with
   u.u nonzero and w = 0, a only, b only, a + b have rank 8, 10, 10, 12 (here at s and at sigma = 0), so only the type
   a + b (their F-barP) holds nullity-4 points; u = 0 with v non-null (EF-bar), u null with v non-null orthogonal to
   u (K1F, K1M-bar) have u.u = 0 and are R-images of conic points; the pairs with v proportional to u or both
   null (EE, EK1, K1E, K1L1, K1M1^T and K1M-bar at beta1 = 0) are totally isotropic or zero; K1L-bar^T has u.v nonzero
   and so Delta nonzero with Q = 0. This map is a reading of the published table (derived), not recomputed here.

Evidence. The identities are exact over Q(i) or Q(i)[s, sigma] (CHECKS); the minors, witnesses and facts are exact over
Q(i); no scan modulo a prime and no floating point enters the record.

--write writes nullity4-qg-orbit-types-result.json beside this file; --check recomputes and compares.

Run from the repository root: "$PYTHON" docs/evidence/a5-kernel-bundles-residuals/nullity4_qg_orbit_types.py --check
"""

from __future__ import annotations

import argparse
import copy
import functools
import hashlib
import itertools
import json
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import sympy as sp
from sympy import QQ_I, ring
from sympy.polys.matrices import DomainMatrix

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(HERE))

import nullity4_gauss_image as gauss  # noqa: E402
import nullity4_orbit_normal_forms as forms  # noqa: E402
import nullity4_qg_intersection as qg  # noqa: E402

import parallel  # noqa: E402

SCHEMA = "a5-kernel-bundles-residuals-nullity4-qg-orbit-types-v1"
RECORD = HERE / "nullity4-qg-orbit-types-result.json"
SOURCE_PATHS = (
    HERE / "nullity4_qg_orbit_types.py",
    HERE / "nullity4_qg_intersection.py",
    qg.RECORD,
    HERE / "nullity4_orbit_normal_forms.py",
    HERE / "nullity4_gauss_image.py",
    gauss.BUNDLES / "kernel_symmetry.py",
)
FIELD = "Q(i) for every identity, minor, witness and fact; Q(i)[s] and Q(i)[sigma] for the polynomial identities"
IU = sp.I
SIGMA = sp.Symbol("sg")
Vector = list[Any]
IDENTITIES = (
    "derivations_preserve_the_eigenlines",
    "eigenlines_are_hermitian_orthogonal",
    "rotation_acts_by_scalars_on_the_eigenlines",
    "rotated_norms",
    "isotropic_pair_relation",
    "chart_rotation_modulus",
    "plane_coincidence",
    "chart_in_the_intersection",
    "chart_kernel_basis",
    "chart_kernel_product",
    "chart_kernel_in_both_hypersurfaces",
    "chart_rank_twelve_pfaffian",
    "chart_kernel_sextic",
    "chart_planes_rescale_the_plane_vectors",
)
# Per s = +-1: eps with P_x in E_eps, P_x in E_eps, q in E_(-eps), q + P_x spans K, nullity M(q), nullity M(k1),
# q proportional to the witness vector, q in P_y, q in P_z.
EIGENLINE_FACTS: dict[str, list[Any]] = {
    "1": [1, True, True, True, 7, 9, True, True, True],
    "-1": [-1, True, True, True, 7, 9, True, True, True],
}
# At sigma = 0: rank M(z~), dim K~, dim C of the planes x, y, z, nullity of k~0, k~1, k~2.
SIGMA_FACTS = [12, 3, [5, 4, 4], [7, 7, 7]]
# The generic ranks 8, 10, 10, 12 of the types w = 0, a only, b only, a + b at sigma = 0.
SIGMA_ORBIT_RANKS = {"w = 0": 8, "a only": 10, "b only": 10, "a + b": 12}
SIGMA_PFAFFIAN = "8*I*c0**4*c1*c2"
# Per plane at sigma = 0: rank M(z'), dim K, dim C(P), dim L_z, dim L.
SIGMA_WITNESSES: dict[str, list[int]] = {
    "x": [12, 3, 5, 3, 6],
    "y": [12, 3, 4, 2, 4],
    "z": [12, 3, 4, 2, 4],
}
SIGMA_POINTS: dict[str, list[str]] = {
    "x": ["16", "8*I", "8", "8*I", "-8", "0", "0", "16*I", "0", "8*I", "8", "-8*I", "8", "0", "0"],
    "y": ["8", "-12*I", "-12", "4*I", "-4", "0", "0", "8*I", "0", "20*I", "20", "-4*I", "4", "0", "0"],
    "z": ["8", "4*I", "4", "-12*I", "12", "0", "0", "8*I", "0", "4*I", "4", "-20*I", "20", "0", "0"],
}
# Generic rank of M(c1 k~1 + c2 k~2) over Q(i)(c1, c2) at sigma = 0; whether the gcd of its principal 8 x 8 Pfaffians
# in the chart c2 = 1 is a nonzero constant; whether one of them is nonzero at (c1 : c2) = (1 : 0).
SIGMA_LINE_X = {"rank": 8, "gcd_is_a_nonzero_constant": True, "value_at_c2_zero_nonzero": True}
# Per plane: the rows and columns of a nonzero maximal minor of the stack over Q(i)[s] (pivots at s = 2), the
# constant and the irreducible factors over Q(i) with multiplicities.
STACK_MINORS: dict[str, dict[str, Any]] = {
    "x": {
        "rows": [0, 1, 3, 5, 7, 9, 11, 13, 16, 24],
        "columns": [0, 1, 3, 5, 6, 7, 9, 11, 13, 14],
        "constant": "-512",
        "factors": [["s", 2], ["s + 1", 3], ["s - 1", 3]],
    },
    "y": {
        "rows": [0, 1, 3, 5, 7, 9, 11, 13, 16, 18, 20],
        "columns": [0, 1, 2, 3, 4, 5, 6, 7, 9, 11, 13],
        "constant": "64*I",
        "factors": [["s", 2], ["s + 1", 2], ["s + I", 3], ["s - 1", 2], ["s - I", 3], ["s**2 - 4*I*s - 1", 3]],
    },
    "z": {
        "rows": [0, 1, 3, 5, 7, 9, 11, 13, 16, 18, 20],
        "columns": [0, 1, 2, 3, 4, 5, 6, 7, 9, 11, 13],
        "constant": "64*I",
        "factors": [["s", 2], ["s + 1", 2], ["s + I", 3], ["s - 1", 2], ["s - I", 3], ["s**2 + 4*I*s - 1", 3]],
    },
}
# Exact dim C of (P_x, P_y, P_z) at s = 0, 1, -1 (qg.SPECIAL_S without the nullity of k1).
SPECIAL_DIMENSIONS = {"0": [5, 4, 4], "1": [7, 4, 4], "-1": [7, 4, 4]}
DIMENSION_TABLE = {
    "generic s": [5, 4, 4],
    "s = 1 and s = -1": [7, 4, 4],
    "roots of D2 = s^2 - 4 i s - 1": [5, 5, 4],
    "roots of D1 = s^2 + 4 i s - 1": [5, 4, 5],
    "sigma = 0": [5, 4, 4],
}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _zero(entries: Sequence[Any]) -> bool:
    return all(sp.expand(entry) == 0 for entry in entries)


@functools.cache
def derivation_matrices() -> tuple[sp.Matrix, ...]:
    """The 14 derivations of the octonions as 15 x 15 matrices diag(D, 0, D)."""
    matrices = []
    for triple in gauss.symmetry._octonion_derivation_triples():
        table = triple[0]
        matrix = sp.zeros(15, 15)
        for row in range(7):
            for column in range(7):
                entry = table[row + 1][column + 1]
                matrix[row, column] = matrix[8 + row, 8 + column] = sp.Rational(entry.numerator, entry.denominator)
        matrices.append(matrix)
    return tuple(matrices)


def _eigenline_vector(first: Sequence[Any], middle: Any, sign: int) -> sp.Matrix:
    return sp.Matrix([*first, middle, *[sign * IU * entry for entry in first]])


def derivations_preserve_the_eigenlines() -> bool:
    """The 14 matrices are equivariant, skew, span 14 dimensions, vanish on e_8 and map E_eps into itself."""
    t = sp.Matrix(sp.symbols("t1:16"))
    a = sp.Matrix(sp.symbols("a1:8"))
    block = forms.block(list(t), forms.ALL, forms.ALL)
    matrices = derivation_matrices()
    for matrix in matrices:
        moved = forms.block(list(matrix * t), forms.ALL, forms.ALL)
        if not _zero(list(moved - matrix * block - block * matrix.T)) or matrix + matrix.T != sp.zeros(15, 15):
            return False
        if any(matrix[7, :]) or any(matrix[:, 7]):
            return False
        small = matrix[0:7, 0:7]
        for sign in (1, -1):
            image = matrix * _eigenline_vector(a, 0, sign)
            if not _zero(list(image - _eigenline_vector(small * a, 0, sign))):
                return False
    return len(matrices) == 14 and sp.Matrix([list(m) for m in matrices]).rank() == 14


def eigenlines_are_hermitian_orthogonal() -> bool:
    """E_+ = {(a; 0; i a)} and E_- = {(a; 0; -i a)} are Hermitian orthogonal, and E_+ holds nonzero vectors."""
    a = sp.Matrix(sp.symbols("a1:8"))
    b = sp.Matrix(sp.symbols("b1:8"))
    cross = (_eigenline_vector(a, 0, 1).H * _eigenline_vector(b, 0, -1))[0, 0]
    own = (_eigenline_vector(a, 0, 1).H * _eigenline_vector(a, 0, 1))[0, 0]
    return bool(sp.expand(cross) == 0 and sp.expand(own) != 0)


def rotation_acts_by_scalars_on_the_eigenlines() -> bool:
    """R maps E_eps to itself by the scalar cos + eps i sin, for both rotations."""
    a = sp.Matrix(sp.symbols("a1:8"))
    for sign in (1, -1):
        rotation = forms._rotation(sign)
        for eps in (1, -1):
            vector = _eigenline_vector(a, 0, eps)
            scalar = rotation[0, 0] + eps * IU * rotation[0, 8]
            if not _zero(list(rotation * vector - scalar * vector)):
                return False
    return True


def rotated_norms() -> bool:
    """n_(+-) = u.u / 4 + 3 v.v / 4 -+ sqrt(3) u.v / 2: product, difference and sum, and the vanishing at u.u = 0."""
    uu, uv, vv = sp.symbols("uu uv vv")
    plus = uu / 4 + 3 * vv / 4 - sp.sqrt(3) * uv / 2
    minus = uu / 4 + 3 * vv / 4 + sp.sqrt(3) * uv / 2
    product = sp.expand(plus * minus - ((uu + 3 * vv) ** 2 - 12 * uv**2) / 16)
    difference = sp.expand(plus - minus + sp.sqrt(3) * uv)
    total = sp.expand(plus + minus - (uu + 3 * vv) / 2)
    both = sp.solve([plus.subs(uu, 0), minus.subs(uu, 0)], [uv, vv], dict=True)
    return bool(product == 0 and difference == 0 and total == 0 and both == [{uv: 0, vv: 0}])


def isotropic_pair_relation() -> bool:
    """At mu = 0 and Q = 0 the vanishing of Delta is (u.u)^2 + (u.v)^2 = 0."""
    uu, uv, vv, mu = sp.symbols("uu uv vv mu")
    delta = uu * vv - uv**2
    reduced = delta.subs({vv: -uu - mu**2}).subs(mu, 0)
    return bool(sp.expand(reduced + uu**2 + uv**2) == 0)


def chart_rotation_modulus() -> bool:
    """On z(s), u.u = (1 + s^2)^2 and n_+ n_- = (s^4 + 14 s^2 + 1)^2 / 16 = (D1 D2)^2 / 16."""
    z = qg.normal_point(qg.S)
    uu = sum(entry**2 for entry in z[0:7])
    uv = sum(a * b for a, b in zip(z[0:7], z[8:15], strict=True))
    vv = sum(entry**2 for entry in z[8:15])
    d1, d2 = qg.S**2 + 4 * IU * qg.S - 1, qg.S**2 - 4 * IU * qg.S - 1
    product = ((uu + 3 * vv) ** 2 - 12 * uv**2) / 16
    return bool(
        sp.expand(uu - (1 + qg.S**2) ** 2) == 0
        and sp.expand(product - (d1 * d2) ** 2 / 16) == 0
        and sp.expand(d1 * d2 - (qg.S**4 + 14 * qg.S**2 + 1)) == 0
    )


def plane_coincidence() -> bool:
    """D2 and N2 have no common root, nor D1 and N1, nor D1 and D2, nor D1 D2 and s (s^2 - 1)."""
    s = qg.S
    d2, n2 = s**2 - 4 * IU * s - 1, 2 * s * (s + IU)
    d1, n1 = s**2 + 4 * IU * s - 1, -2 * s * (s - IU)
    pairs = ((d2, n2), (d1, n1), (d1, d2), (d1 * d2, s * (s**2 - 1) * (s**2 + 1)))
    return all(sp.gcd(sp.Poly(a, s, extension=IU), sp.Poly(b, s, extension=IU)).degree() == 0 for a, b in pairs)


def _rescaled(vector: Sequence[Any], scale: Any) -> Vector:
    return [
        sp.expand(sp.cancel(scale * entry.subs(qg.S, 1 / SIGMA))) if entry != 0 else sp.Integer(0) for entry in vector
    ]


def chart_vectors() -> tuple[Vector, list[Vector]]:
    """z~ and the vectors k~0, k~1, k~2 of the chart sigma = 1 / s, polynomial in sigma."""
    k0, k1, k2 = qg.kernel_vectors(qg.S)
    return _rescaled(qg.normal_point(qg.S), SIGMA**2), [
        _rescaled(k0, SIGMA**2),
        _rescaled(k1, SIGMA),
        _rescaled(k2, SIGMA),
    ]


def chart_in_the_intersection() -> bool:
    return _zero(forms._forms(chart_vectors()[0]))


def chart_kernel_basis() -> bool:
    z, kernel = chart_vectors()
    m = qg.msym(z)
    return all(_zero(list(m * sp.Matrix(k))) for k in kernel)


def chart_kernel_product() -> bool:
    kernel = chart_vectors()[1]
    return all(_zero(list(qg.msym(a) * sp.Matrix(b))) for a in kernel for b in kernel)


def chart_kernel_in_both_hypersurfaces() -> bool:
    kernel = chart_vectors()[1]
    combination = [qg.C0 * a + qg.C1 * b + qg.C2 * c for a, b, c in zip(*kernel, strict=True)]
    q, delta, _ = forms._forms(combination)
    return _zero([q, delta])


def chart_rank_twelve_pfaffian() -> bool:
    domain = ring("sg", QQ_I)[0]
    entries = qg._ring_matrix(qg.msym(chart_vectors()[0]), domain)
    indices = [index for index in range(15) if index not in (0, 1, 4)]
    found = qg._pfaffian_ring(entries, indices, domain)
    return bool(found == domain.from_expr(sp.expand(8 * (SIGMA**2 + 1) ** 6)))


def _chart_pfaffian() -> Any:
    kernel = chart_vectors()[1]
    combination = [sp.expand(qg.C0 * a + qg.C1 * b + qg.C2 * c) for a, b, c in zip(*kernel, strict=True)]
    domain = ring("sg,c0,c1,c2", QQ_I)[0]
    entries = qg._ring_matrix(qg.msym(combination), domain)
    indices = [index for index in range(15) if index not in (0, 1, 3)]
    return sp.expand(qg._pfaffian_ring(entries, indices, domain).as_expr())


def chart_kernel_sextic() -> bool:
    """The Pfaffian of M on K~ is the sextic of qg under s = 1 / sigma, c0 = sigma^2 c~0, c1 = sigma c~1, ..."""
    substitution = {qg.S: 1 / SIGMA, qg.C0: SIGMA**2 * qg.C0, qg.C1: SIGMA * qg.C1, qg.C2: SIGMA * qg.C2}
    expected = sp.expand(sp.cancel(sp.sympify(qg.SEXTIC).subs(substitution, simultaneous=True)))
    return bool(sp.expand(_chart_pfaffian() - expected) == 0)


def chart_planes_rescale_the_plane_vectors() -> bool:
    """The vectors of P~y and P~z at sigma are sigma^4 times the vectors of P_y and P_z at s = 1 / sigma."""
    k0, k1, k2 = qg.kernel_vectors(qg.S)
    k0t, k1t, k2t = chart_vectors()[1]
    d2, n2 = qg.S**2 - 4 * IU * qg.S - 1, 2 * qg.S * (qg.S + IU)
    d1, n1 = qg.S**2 + 4 * IU * qg.S - 1, -2 * qg.S * (qg.S - IU)
    y = _rescaled([d2 * a + n2 * b for a, b in zip(k0, k1, strict=True)], SIGMA**4)
    z = _rescaled([d1 * a + n1 * b for a, b in zip(k0, k2, strict=True)], SIGMA**4)
    y_chart = [
        (1 - 4 * IU * SIGMA - SIGMA**2) * a + 2 * SIGMA * (1 + IU * SIGMA) * b for a, b in zip(k0t, k1t, strict=True)
    ]
    z_chart = [
        (1 + 4 * IU * SIGMA - SIGMA**2) * a - 2 * SIGMA * (1 - IU * SIGMA) * c for a, c in zip(k0t, k2t, strict=True)
    ]
    return _zero([a - b for a, b in zip(y, y_chart, strict=True)]) and _zero(
        [a - b for a, b in zip(z, z_chart, strict=True)]
    )


CHECKS = {name: globals()[name] for name in IDENTITIES}


def identity(name: str) -> bool:
    return CHECKS[name]()


def _in_eigenline(vector: Sequence[Any], eps: int) -> bool:
    return bool(vector[7] == 0 and all(sp.expand(vector[8 + i] - eps * IU * vector[i]) == 0 for i in range(7)))


def eigenline_facts(s: int) -> list[Any]:
    """The facts of the type s = +-1 listed at EIGENLINE_FACTS."""
    kernel = qg.kernel_vectors(sp.Integer(s))
    k0, k1, k2 = kernel
    eps = 1 if _in_eigenline(k1, 1) else -1
    rows = [[k[8 + i] + eps * IU * k[i] for k in kernel] for i in range(7)] + [[k[7] for k in kernel]]
    solution = qg._nullspace(rows)
    _require(len(solution) == 1, "the vectors of K in E_(-eps) are not a line")
    q = qg._combination(solution[0], kernel)
    witness = qg.witness_point(sp.Integer(s), "x")
    planes = qg.plane_vectors(sp.Integer(s))
    return [
        eps,
        _in_eigenline(k1, eps),
        _in_eigenline(k2, eps),
        _in_eigenline(q, -eps) and qg._rank([k1, k2, q]) == 3,
        15 - qg._rank(qg.msym(q).tolist()),
        15 - qg._rank(qg.msym(k1).tolist()),
        qg._rank([q, witness]) == 1,
        qg._rank([*planes["y"], q]) == 2,
        qg._rank([*planes["z"], q]) == 2,
    ]


def eigenline_record() -> dict[str, list[Any]]:
    return dict(zip(("1", "-1"), parallel.ordered_map(eigenline_facts, [1, -1], min_items=2), strict=True))


def _sigma_zero() -> tuple[Vector, list[Vector]]:
    z, kernel = chart_vectors()
    return [sp.sympify(e).subs(SIGMA, 0) for e in z], [[sp.sympify(e).subs(SIGMA, 0) for e in k] for k in kernel]


def _sigma_planes() -> dict[str, tuple[Vector, Vector]]:
    k0, k1, k2 = _sigma_zero()[1]
    return {"x": (k1, k2), "y": (k2, k0), "z": (k1, k0)}


def _orbit_types_at_infinity() -> dict[str, Vector]:
    head: Vector = [sp.Integer(1), 0, 0, 0, 0, 0, 0, IU, 0]
    types = {
        "w = 0": [0, 0, 0, 0, 0, 0],
        "a only": [IU, 1, 0, 0, 0, 0],
        "b only": [0, 0, -IU, 1, 0, 0],
        "a + b": [IU, 1, -IU, 1, 0, 0],
    }
    return {name: head + list(w) for name, w in types.items()}


def sigma_common(plane: str) -> int:
    """dim C(P) of the plane x, y or z at sigma = 0."""
    p1, p2 = _sigma_planes()[plane]
    return 15 - qg._rank([*qg.msym(p1).tolist(), *qg.msym(p2).tolist()])


def sigma_nullity(index: int) -> int:
    """The nullity of M(k~_index) at sigma = 0."""
    return 15 - qg._rank(qg.msym(_sigma_zero()[1][index]).tolist())


def sigma_facts() -> list[Any]:
    """Rank M(z~), dim K~, dim C of the planes x, y, z and the nullities of k~0, k~1, k~2, all at sigma = 0."""
    z, kernel = _sigma_zero()
    commons = parallel.ordered_map(sigma_common, ["x", "y", "z"], min_items=2)
    nullities = parallel.ordered_map(sigma_nullity, [0, 1, 2], min_items=2)
    return [qg._rank(qg.msym(z).tolist()), qg._rank(kernel), commons, nullities]


def sigma_orbit_rank(name: str) -> int:
    """The rank of M at the point of the type w at sigma = 0."""
    return qg._rank(qg.msym(_orbit_types_at_infinity()[name]).tolist())


def sigma_orbit_ranks() -> dict[str, int]:
    names = list(_orbit_types_at_infinity())
    return dict(zip(names, parallel.ordered_map(sigma_orbit_rank, names, min_items=2), strict=True))


def sigma_pfaffian() -> str:
    return str(sp.factor(_chart_pfaffian().subs(SIGMA, 0), extension=IU))


def sigma_witness(plane: str) -> tuple[str, list[int], list[str]]:
    """The vector of K~ Hermitian-orthogonal to the plane at sigma = 0, its facts and its coordinates."""
    kernel = _sigma_zero()[1]
    rows = [[qg._hermitian(k, p) for k in kernel] for p in _sigma_planes()[plane]]
    solution = qg._nullspace(rows)
    _require(len(solution) == 1, "the orthogonal complement in K~ is not a line")
    point = qg._clear(qg._combination(solution[0], kernel))
    facts = qg.real_point_facts(point)
    row = [facts["rank"], facts["kernel"], facts["common"], facts["cut"], facts["fiber"]]
    return plane, row, [str(entry) for entry in point]


@functools.cache
def _pencil() -> tuple[Any, Any, Any]:
    domain = ring("c1,c2", QQ_I)[0]
    _, k1, k2 = _sigma_zero()[1]
    matrix = qg.msym([qg.C1 * a + qg.C2 * b for a, b in zip(k1, k2, strict=True)])
    return domain, qg._ring_matrix(matrix, domain), matrix.subs({qg.C1: 3, qg.C2: 5})


def pencil_pfaffian(indices: tuple[int, ...]) -> Any:
    """The Pfaffian of the principal 8 x 8 block of M(c1 k~1 + c2 k~2) on the indices, None where it is 0 at (3, 5)."""
    domain, entries, sample = _pencil()
    if sample.extract(list(indices), list(indices)).det() == 0:
        return None
    return sp.expand(qg._pfaffian_ring(entries, indices, domain).as_expr())


def sigma_line_x() -> dict[str, Any]:
    """The generic rank of the pencil and the gcd of its principal 8 x 8 Pfaffians in the chart c2 = 1."""
    _, k1, k2 = _sigma_zero()[1]
    matrix = qg.msym([qg.C1 * a + qg.C2 * b for a, b in zip(k1, k2, strict=True)]).applyfunc(sp.expand)
    rank = int(DomainMatrix.from_Matrix(matrix).convert_to(QQ_I.frac_field(qg.C1, qg.C2)).rank())
    subsets = list(itertools.combinations(range(15), 8))
    found = [p for p in parallel.ordered_map(pencil_pfaffian, subsets, min_items=2) if p is not None]
    common: Any = 0
    for poly in found:
        common = sp.gcd(common, sp.expand(poly.subs(qg.C2, 1)))
    at_infinity = any(sp.expand(poly.subs({qg.C1: 1, qg.C2: 0})) != 0 for poly in found)
    constant = bool(common != 0 and sp.Poly(common, qg.C1).degree() == 0)
    return {"rank": rank, "gcd_is_a_nonzero_constant": constant, "value_at_c2_zero_nonzero": at_infinity}


def stack_minor(plane: str) -> dict[str, Any]:
    """A nonzero maximal minor of the stack [M(p1); M(p2)] of the plane over Q(i)[s], pivots chosen at s = 2."""
    p1, p2 = qg.plane_vectors(qg.S)[plane]
    stack = sp.Matrix.vstack(qg.msym(p1), qg.msym(p2)).applyfunc(sp.expand)
    at_two = DomainMatrix.from_Matrix(stack.subs(qg.S, 2)).convert_to(QQ_I)
    columns = list(at_two.rref()[1])
    rows = list(at_two.transpose().rref()[1])
    _require(len(rows) == len(columns) == qg.STACK_RANKS[plane], "the pivots miss the generic rank")
    polynomials = QQ_I.poly_ring(qg.S)
    minor = DomainMatrix.from_Matrix(stack.extract(rows, columns)).convert_to(polynomials).det()
    constant, factors = sp.factor_list(sp.expand(polynomials.to_sympy(minor)), extension=IU)
    return {
        "rows": rows,
        "columns": columns,
        "constant": str(constant),
        "factors": sorted([str(factor), int(power)] for factor, power in factors),
    }


def stack_minor_record() -> dict[str, dict[str, Any]]:
    planes = list(qg.STACK_RANKS)
    return dict(zip(planes, parallel.ordered_map(stack_minor, planes, min_items=2), strict=True))


def special_row(s: int) -> list[int]:
    """Exact dim C of the planes x, y, z at the rational s."""
    return qg.special_facts(s)[:3]


def special_dimensions() -> dict[str, list[int]]:
    values = (0, 1, -1)
    return dict(zip(map(str, values), parallel.ordered_map(special_row, list(values), min_items=2), strict=True))


ALLOWED_FACTORS = {
    "x": ["s", "s + 1", "s - 1"],
    "y": ["s", "s + 1", "s + I", "s - 1", "s - I", "s**2 - 4*I*s - 1"],
    "z": ["s", "s + 1", "s + I", "s - 1", "s - I", "s**2 + 4*I*s - 1"],
}


def dimension_table(
    minors: dict[str, dict[str, Any]], special: dict[str, list[int]], sigma: list[int], coincidence: bool
) -> dict[str, list[int]]:
    """The dim C of the planes of J over the chart, derived from the minors, the exact values and the coincidence.

    The rank of a stack drops only at roots of its maximal minor: s = 0, s = +-1 (exact values), s = +-i (outside the
    chart) and the roots of D2 (resp. D1), where P_y (resp. P_z) is P_x. A different set of factors leaves the table
    empty of its key rows."""
    generic = [15 - qg.STACK_RANKS[plane] for plane in ("x", "y", "z")]
    factors_agree = all(
        sorted(f for f, _ in minors[plane]["factors"]) == sorted(ALLOWED_FACTORS[plane]) for plane in "xyz"
    )
    if not (factors_agree and coincidence and special["0"] == generic and special["1"] == special["-1"]):
        return {"inconsistent": []}
    return {
        "generic s": generic,
        "s = 1 and s = -1": special["1"],
        "roots of D2 = s^2 - 4 i s - 1": [generic[0], generic[0], generic[2]],
        "roots of D1 = s^2 + 4 i s - 1": [generic[0], generic[1], generic[0]],
        "sigma = 0": sigma,
    }


def _inputs() -> dict[str, str]:
    return {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in SOURCE_PATHS}


def compute() -> dict[str, Any]:
    names = list(IDENTITIES)
    identities = dict(zip(names, parallel.ordered_map(identity, names, min_items=2), strict=True))
    witnesses = parallel.ordered_map(sigma_witness, ["x", "y", "z"], min_items=2)
    minors, special, facts = stack_minor_record(), special_dimensions(), sigma_facts()
    record: dict[str, Any] = {
        "schema": SCHEMA,
        "field": FIELD,
        "inputs": _inputs(),
        "identities": identities,
        "eigenlines": eigenline_record(),
        "sigma_facts": facts,
        "sigma_orbit_ranks": sigma_orbit_ranks(),
        "sigma_pfaffian": sigma_pfaffian(),
        "sigma_witnesses": {plane: row for plane, row, _ in witnesses},
        "sigma_points": {plane: point for plane, _, point in witnesses},
        "sigma_line_x": sigma_line_x(),
        "stack_minors": minors,
        "special_dimensions": special,
        "dimension_table": dimension_table(minors, special, facts[2], identities["plane_coincidence"]),
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
        "eigenlines": copy.deepcopy(EIGENLINE_FACTS),
        "sigma_facts": copy.deepcopy(SIGMA_FACTS),
        "sigma_orbit_ranks": dict(SIGMA_ORBIT_RANKS),
        "sigma_pfaffian": SIGMA_PFAFFIAN,
        "sigma_witnesses": {plane: list(row) for plane, row in SIGMA_WITNESSES.items()},
        "sigma_points": {plane: list(row) for plane, row in SIGMA_POINTS.items()},
        "sigma_line_x": dict(SIGMA_LINE_X),
        "stack_minors": copy.deepcopy(STACK_MINORS),
        "special_dimensions": {s: list(row) for s, row in SPECIAL_DIMENSIONS.items()},
        "dimension_table": copy.deepcopy(DIMENSION_TABLE),
        "pass": True,
    }


def verdict(record: dict[str, Any]) -> list[str]:
    """The reasons the record fails its own rules; empty when it passes. The comparison is on serialized text."""
    expected = expected_record()
    problems = []
    messages = {
        "inputs": "the input digests differ from the files",
        "identities": "an exact identity fails",
        "eigenlines": "the type s = +-1 no longer has P_x in E_eps and q in E_(-eps) inside J",
        "sigma_facts": "the facts at sigma = 0 differ",
        "sigma_orbit_ranks": "a rank of the orbit types at sigma = 0 differs",
        "sigma_pfaffian": "the Pfaffian of M on the kernel at sigma = 0 differs",
        "sigma_witnesses": "a witness at sigma = 0 differs from its pinned facts (dim L is 6, 4, 4)",
        "sigma_points": "a witness point at sigma = 0 is missing or differs",
        "sigma_line_x": "the nullity of M on the plane x at sigma = 0 is not 7 everywhere",
        "stack_minors": "a maximal minor of a plane stack differs from its pinned factorization",
        "special_dimensions": "a dimension at s = 0, 1 or -1 differs",
        "dimension_table": "the table of dim C(P) over the chart differs",
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
    print(f"pass: {len(record['identities'])} identities, {len(record['sigma_witnesses'])} witnesses at sigma = 0")


if __name__ == "__main__":
    main()
