"""The real nullity-4 points of V(Q) n V(G): their kernel lines, the values 2, 4, 6 of dim L and the plane nullity.

M(t) is the 15 x 15 skew lower block of the bordered matrix of nullity4_gauss_image.py in the frame t = (u, mu, v),
Q = u.u + mu^2 + v.v, Delta = (u.u)(v.v) - (u.v)^2 and G = Q^2 - 4 Delta. At a nullity-4 point z of V(Q) n V(G) the
product of two vectors of K = ker M(z) vanishes (A5-479), so M(k) K = 0 for every k in K. A real point pairs z
with its conjugate; its kernel plane is P = K n conj(z)-perp, and dim L = 2 dim (C(P) n conj(P)-perp) with
C(P) = ker M(p1) n ker M(p2) (A5-435).

1. Reduction. K lies in C(P), the Hermitian form k.conj(k') is positive definite on K, and the two functionals
   k -> k.conj(p_j) have rank 2 on K, so dim (C(P) n conj(P)-perp) = dim C(P) - 2 and dim L = 2 (dim C(P) - 2). The
   retained rows agree: common kernel 3 with cut 1 (384 grid points) and 5 with cut 3 (4 points).
2. Lines. A vector p of K with nullity M(p) = 3 has ker M(p) = K, so C(P) = K for every plane P through such a p.
   Hence dim C(P) > 3 only for the planes P inside J = {k in K: nullity M(k) > 3}, a cone in K.
3. Normal form (argument). A point with u.u nonzero is, up to scale, (x, beta + lambda x + w) with x a unit vector,
   w null and orthogonal to x, beta^2 + lambda^2 = -1 (A5-479). The stabilizer SL_3 of x in G_2(C) acts on the
   null w in x-perp = C^3 + C^3* and is transitive on its pairs (a, b) with a.b = 0, a and b nonzero; w = 0 and the
   pure types a or b lie in other orbits. The rotation of the planes (u_j, v_j) by 120 degrees (item 2 of
   nullity4_orbit_normal_forms.py) moves u.u off zero unless mu = 0 and u, v span a totally isotropic space. The
   conic is parametrized by s: z(s) = (1 + s^2) (e_1; beta; lambda e_1 + i e_2 + e_3 - i e_4 + e_5) in the frame,
   with i beta = (1 - s^2) / (1 + s^2) and i lambda = 2 s / (1 + s^2).
4. Exact identities over Q(i)[s] (the functions of CHECKS): z(s) lies in V(Q) n V(Delta); the three vectors k0,
   k1, k2 lie in ker M(z(s)), are independent for every s, and satisfy M(k_a) k_b = 0 and Q = Delta = 0 on their
   span; a 12 x 12 principal Pfaffian of M(z(s)) is 8 (s^2 + 1)^6, so rank M = 12 and K = <k0, k1, k2> for every s
   with s^2 + 1 nonzero; the generic ranks of M(z) are 8, 10, 10, 12 for w = 0, a, b, a + b (the first three are
   nullities 7, 5, 5, never 3, at every s, since a specialization never raises a rank); the Pfaffian of M on K
   factors as -32 i c0^4 (s^2 + 1)^3 l_y l_z, so J is the union of the three lines l_x: c0 = 0, l_y and l_z; the
   planes P_x = <k1, k2>, P_y = <k2, D2 k0 + N2 k1> and P_z = <k1, D1 k0 + N1 k2> are those lines
   (D2 = s^2 - 4 i s - 1, N2 = 2 s (s + i), D1 = s^2 + 4 i s - 1, N1 = -2 s (s - i)).
5. Common kernels. The stacks [M(p1); M(p2)] of P_x, P_y, P_z have rank 10, 11, 11 over Q(i)(s): dim C(P) = 5, 4, 4
   at a general s, so dim L = 6, 4, 4 at a real point with P = P_x, P_y, P_z. A specialization never raises a
   rank, so each dimension is at least that value at every s; equality at a special s rests on the exact ranks at
   s = 0, 1, -1 and on the scan below. The exact values are (5, 4, 4) at s = 0 and (7, 4, 4) at s = 1 and s = -1,
   where nullity M(k1) = 9. A scan of all 32,027 values of s modulo the prime with s^2 + 1 nonzero finds (5, 4, 4)
   except at s = +-1 and at the four roots of D1 D2, where the plane P_z or P_y coincides with P_x (dimension 5).
6. Existence. For a fixed kernel K, every vector z' of K outside J has ker M(z') = K, so z' is a nullity-4 point
   of V(Q) n V(G) with the same K and the same lines. The vector z' of K orthogonal, for the Hermitian form, to
   a plane P_j has kernel plane P(z') = P_j: it solves two linear equations over Q(i). The producer builds
   z' for P_x, P_y, P_z at s = 2 and s = 0 and computes, exactly over Q(i), the rank of M(z'), K(z') = K, the
   plane P, dim C(P), the cut and dim L; the independent modular routine kernel_form of nullity4_gauss_image.py
   reproduces dim L, the common kernel and its cut. dim L = 4 occurs at a real point, so the "only 2 and 6" half
   of A5-541 fails. The values 2, 4 and 6 occur; the value 10 at s = +-1 is open (residual c).
7. Nullity on the plane. M(c1 k1 + c2 k2) has rank 8 over Q(i)(s, c1, c2), and its 56 distinct 8 x 8 principal
   Pfaffians have the common zero set s^2 = 1 in both charts of (c1 : c2), so at s^2 other than 1 every vector of
   P_x has rank M = 8 (nullity 7). At s = +-1 the vector k1 has nullity 9. The function mu is -c0 (s^2 - 1) on K
   and u.u is -c0^2 (s^2 + 1)^2, so mu^2 / u.u is constant on K and mu vanishes on all of K exactly when s = +-1.
   The four retained points with dim L = 6 have P = P_x, the only plane with dim C(P) = 5, and nullity 7 on the
   eight sampled vectors of P. In the algebra of 32 dimensions the retained kernel vectors have nullity
   2 (nullity M(p) - 1) at all three retained values (4, 12, 16); that identification is a pattern of the
   retained rows, not a derivation.

Residuals. (a) The totally isotropic pairs (u.u = u.v = v.v = mu = 0) have rank 10 at every sampled point (200
sampled pairs); the exact statement needs an orbit argument. (b) The chart s covers the conic except the point
(beta, lambda) = (i, 0). (c) A real point of the orbit type s = +-1 with P = P_x would have dim C(P) = 7, dim L = 10
and a nullity of at least 9 on P; for the kernel K(z(+-1)) in this frame the vector orthogonal to P_x lies in J,
so the witness construction yields no such point there, and whether another unitary frame yields one is not
decided.
(d) The dimension of the set of real points with dim L = 4 or 6 is not computed.

--write writes nullity4-qg-intersection-result.json beside this file; --check recomputes and compares.

Run from the repository root: "$PYTHON" docs/evidence/a5-kernel-bundles-residuals/nullity4_qg_intersection.py --check
"""

from __future__ import annotations

import argparse
import copy
import functools
import hashlib
import itertools
import json
import sys
from collections import Counter
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

import parallel  # noqa: E402

SCHEMA = "a5-kernel-bundles-residuals-nullity4-qg-intersection-v1"
RECORD = HERE / "nullity4-qg-intersection-result.json"
SOURCE_PATHS = (
    HERE / "nullity4_qg_intersection.py",
    HERE / "nullity4_gauss_image.py",
    gauss.RECORD,
    HERE / "nullity4_orbit_normal_forms.py",
)
PRIME = gauss.PRIME
UNIT = gauss.ROOT_OF_MINUS_ONE
FIELD = f"Q(i) for the identities, the witnesses and the retained points; GF({PRIME}), i = {UNIT}, for the scans"
STRATUM = gauss.STRATA[2]
S = sp.Symbol("s")
IU = sp.I
C0, C1, C2 = sp.symbols("c0 c1 c2")
Vector = list[Any]
IDENTITIES = (
    "normal_form_on_the_intersection",
    "kernel_basis_in_the_kernel",
    "kernel_product_vanishes",
    "kernel_in_both_hypersurfaces",
    "rank_twelve_pfaffian",
    "kernel_independence",
    "kernel_sextic",
    "lines_are_the_common_kernel_planes",
    "orbit_modulus_is_constant_on_the_kernel",
)
ORBIT_RANKS = {"w = 0": 8, "a only": 10, "b only": 10, "a + b": 12}
SEXTIC = "-32*I*c0**4*(s**2 + 1)**3*(2*c0*s*(s + I) - c1*(s**2 - 4*I*s - 1))*(2*c0*s*(s - I) + c2*(s**2 + 4*I*s - 1))/4"
# Generic ranks of the stacks [M(p1); M(p2)] over Q(i)(s) for the planes x, y, z.
STACK_RANKS = {"x": 10, "y": 11, "z": 11}
# Exact dim C(P) for P_x, P_y, P_z and the nullity of M(k1) at the rational s where a minor vanishes.
SPECIAL_S = {"0": [5, 4, 4, 7], "1": [7, 4, 4, 9], "-1": [7, 4, 4, 9]}
# Generic rank of M(c1 k1 + c2 k2) over Q(i)(s, c1, c2): nullity 7 on the whole line x.
LINE_X_RANK = 8
LINE_X_GROEBNER = {"c2 = 1": ["s**2 - 1"], "c1 = 1, c2 = 0": ["s**2 - 1"]}
WITNESS_S = (2, 0)
# Per (s, plane): exact rank M(z'), dim K, dim C(P), dim L_z, dim L, and the modular fiber, plane nullity, common kernel
# and cut.
WITNESS_FACTS: dict[str, list[int]] = {
    "s = 2, x": [12, 3, 5, 3, 6, 6, 7, 5, 3],
    "s = 2, y": [12, 3, 4, 2, 4, 4, 5, 4, 2],
    "s = 2, z": [12, 3, 4, 2, 4, 4, 5, 4, 2],
    "s = 0, x": [12, 3, 5, 3, 6, 6, 7, 5, 3],
    "s = 0, y": [12, 3, 4, 2, 4, 4, 5, 4, 2],
    "s = 0, z": [12, 3, 4, 2, 4, 4, 5, 4, 2],
}
# Exact Gaussian-integer frame points z' of K orthogonal to the plane, scaled to clear denominators.
WITNESS_POINTS: dict[str, list[str]] = {
    "s = 0, x": [
        "16*I",
        "8",
        "-8*I",
        "8",
        "8*I",
        "0",
        "0",
        "16",
        "0",
        "-8",
        "8*I",
        "8",
        "8*I",
        "0",
        "0",
    ],
    "s = 0, y": [
        "8*I",
        "-12",
        "12*I",
        "4",
        "4*I",
        "0",
        "0",
        "8",
        "0",
        "-20",
        "20*I",
        "4",
        "4*I",
        "0",
        "0",
    ],
    "s = 0, z": [
        "8*I",
        "4",
        "-4*I",
        "-12",
        "-12*I",
        "0",
        "0",
        "8",
        "0",
        "-4",
        "4*I",
        "20",
        "20*I",
        "0",
        "0",
    ],
    "s = 2, x": [
        "2000*I",
        "-600 - 800*I",
        "-800 + 600*I",
        "-600 + 800*I",
        "-800 - 600*I",
        "0",
        "0",
        "-1200",
        "1600",
        "-1000",
        "1000*I",
        "1000",
        "1000*I",
        "0",
        "0",
    ],
    "s = 2, y": [
        "3000 + 6000*I",
        "-7000 + 36500*I",
        "36500 + 7000*I",
        "-600 + 3300*I",
        "-3300 - 600*I",
        "0",
        "0",
        "-3600 + 1800*I",
        "4800 - 2400*I",
        "-31000 - 24500*I",
        "-24500 + 31000*I",
        "3000 - 1500*I",
        "1500 + 3000*I",
        "0",
        "0",
    ],
    "s = 2, z": [
        "-3000 + 6000*I",
        "-600 - 3300*I",
        "-3300 + 600*I",
        "-7000 - 36500*I",
        "36500 - 7000*I",
        "0",
        "0",
        "-3600 - 1800*I",
        "4800 + 2400*I",
        "-3000 - 1500*I",
        "-1500 + 3000*I",
        "31000 - 24500*I",
        "24500 + 31000*I",
        "0",
        "0",
    ],
}
# Scan of every s modulo the prime with s^2 + 1 nonzero: (rank M(z(s)), nullity M(k1), dim C(P_x), dim C(P_y),
# dim C(P_z)) with the number of s.
SCAN_TALLY = [
    [12, 7, 5, 4, 4, 32021],
    [12, 7, 5, 4, 5, 2],
    [12, 7, 5, 5, 4, 2],
    [12, 9, 7, 4, 4, 2],
]
ISOTROPIC_SAMPLES = 200
ISOTROPIC_TALLY = [[10, 2, ISOTROPIC_SAMPLES]]
# Retained points of dim L = 6: exact rank, dim K, dim C(P), dim L_z, and the nullities of M(p) at the net of P.
RETAINED_FACTS = [12, 3, 5, 3, [7]]
RETAINED_POINTS = 4
NET = ((1, 0), (0, 1), (1, 1), (1, -1), (1, 2), (2, -1), (1, 3), (3, 1))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def msym(vector: Sequence[Any]) -> sp.Matrix:
    """M(vector) for a frame vector of 15 entries."""
    return forms.block(vector, forms.ALL, forms.ALL)


def kernel_vectors(s: Any) -> list[Vector]:
    """The vectors k0, k1, k2 of the frame that span ker M(z(s)) (items 3 and 4)."""
    k0 = [IU * (s**2 + 1), -((s + IU) ** 2), IU * (s + IU) ** 2, -((s - IU) ** 2), -IU * (s - IU) ** 2, 0, 0]
    k0 += [-(s**2 - 1), 2 * s, 0, 0, 0, 0, 0, 0]
    k1 = [0, -IU * (s + IU), -(s + IU), 0, 0, 0, 0, 0, 0, IU * (s - IU), s - IU, 0, 0, 0, 0]
    k2 = [0, 0, 0, -IU * (s - IU), s - IU, 0, 0, 0, 0, 0, 0, -IU * (s + IU), s + IU, 0, 0]
    return [k0, k1, k2]


def normal_point(s: Any) -> Vector:
    """z(s) = (1 + s^2) (e_1; beta; lambda e_1 + i e_2 + e_3 - i e_4 + e_5) in the frame."""
    d = 1 + s**2
    return [d, 0, 0, 0, 0, 0, 0, -IU * (1 - s**2), -2 * IU * s, d * IU, d, -d * IU, d, 0, 0]


def plane_vectors(s: Any) -> dict[str, tuple[Vector, Vector]]:
    """The planes P_x, P_y, P_z of item 4 as pairs of vectors of the frame."""
    k0, k1, k2 = kernel_vectors(s)
    d2, n2 = s**2 - 4 * IU * s - 1, 2 * s * (s + IU)
    d1, n1 = s**2 + 4 * IU * s - 1, -2 * s * (s - IU)
    return {
        "x": (k1, k2),
        "y": (k2, [d2 * a + n2 * b for a, b in zip(k0, k1, strict=True)]),
        "z": (k1, [d1 * a + n1 * b for a, b in zip(k0, k2, strict=True)]),
    }


def _expanded(vector: Sequence[Any]) -> Vector:
    return [sp.expand(entry) for entry in vector]


def _zero(entries: Sequence[Any]) -> bool:
    return all(sp.expand(entry) == 0 for entry in entries)


def _ring_matrix(matrix: sp.Matrix, domain: Any) -> list[list[Any]]:
    return [
        [domain.zero if matrix[a, b] == 0 else domain.from_expr(sp.expand(matrix[a, b])) for b in range(15)]
        for a in range(15)
    ]


def _pfaffian_ring(entries: list[list[Any]], indices: Sequence[int], domain: Any) -> Any:
    """The Pfaffian of the principal submatrix on the indices, by recursion on subsets, in a polynomial ring."""
    order = len(indices)
    memo: dict[int, Any] = {}

    def recurse(mask: int) -> Any:
        if mask == 0:
            return domain.one
        if mask in memo:
            return memo[mask]
        bits = [b for b in range(order) if mask >> b & 1]
        first, total = bits[0], domain.zero
        for position, other in enumerate(bits[1:]):
            entry = entries[indices[first]][indices[other]]
            if entry == 0:
                continue
            term = entry * recurse(mask & ~(1 << first) & ~(1 << other))
            total = total + term if position % 2 == 0 else total - term
        memo[mask] = total
        return total

    return recurse((1 << order) - 1)


def _function_field_rank(matrix: sp.Matrix) -> int:
    return int(DomainMatrix.from_Matrix(matrix).convert_to(QQ_I.frac_field(S)).rank())


def normal_form_on_the_intersection() -> bool:
    q, delta, g = forms._forms(normal_point(S))
    return _zero([q, delta, g])


def kernel_basis_in_the_kernel() -> bool:
    m = msym(normal_point(S))
    return all(_zero(list(m * sp.Matrix(k))) for k in kernel_vectors(S))


def kernel_product_vanishes() -> bool:
    ks = kernel_vectors(S)
    return all(_zero(list(msym(a) * sp.Matrix(b))) for a in ks for b in ks)


def kernel_in_both_hypersurfaces() -> bool:
    k0, k1, k2 = kernel_vectors(S)
    combination = [C0 * a + C1 * b + C2 * c for a, b, c in zip(k0, k1, k2, strict=True)]
    q, delta, _ = forms._forms(combination)
    return _zero([q, delta])


def rank_twelve_pfaffian() -> bool:
    domain = ring("s", QQ_I)[0]
    entries = _ring_matrix(msym(normal_point(S)), domain)
    indices = [index for index in range(15) if index not in (0, 1, 4)]
    found = _pfaffian_ring(entries, indices, domain)
    return bool(found == domain.from_expr(sp.expand(8 * (S**2 + 1) ** 6)))


def kernel_independence() -> bool:
    k0, k1, k2 = kernel_vectors(S)
    matrix = sp.Matrix([k0, k1, k2]).T
    common: Any = None
    for rows in itertools.combinations(range(15), 3):
        minor = sp.expand(matrix.extract(list(rows), [0, 1, 2]).det())
        if minor != 0:
            common = minor if common is None else sp.gcd(common, minor)
    return common == 1


def kernel_sextic() -> bool:
    domain = ring("s,c0,c1,c2", QQ_I)[0]
    k0, k1, k2 = kernel_vectors(S)
    combination = [C0 * a + C1 * b + C2 * c for a, b, c in zip(k0, k1, k2, strict=True)]
    entries = _ring_matrix(msym(combination), domain)
    indices = [index for index in range(15) if index not in (0, 1, 3)]
    found = _pfaffian_ring(entries, indices, domain)
    return bool(found == domain.from_expr(sp.expand(sp.sympify(SEXTIC))))


def lines_are_the_common_kernel_planes() -> bool:
    """P_y and P_z are the points of the plane family through k2 and k1 where the stack drops to rank 11."""
    k0, k1, k2 = kernel_vectors(S)
    d2, n2 = S**2 - 4 * IU * S - 1, 2 * S * (S + IU)
    tau = sp.Symbol("tau")
    stack = sp.Matrix.vstack(msym(k2), msym([a + tau * b for a, b in zip(k0, k1, strict=True)])).subs(S, 2)
    root = sp.expand(n2.subs(S, 2) / d2.subs(S, 2))
    return bool(_rank(stack.subs(tau, root).tolist()) == 11 and _rank(stack.subs(tau, 1).tolist()) == 12)


def orbit_modulus_is_constant_on_the_kernel() -> bool:
    """On K, u.u = -c0^2 (s^2 + 1)^2 and mu = -c0 (s^2 - 1), so mu^2 (s^2 + 1)^2 + u.u (s^2 - 1)^2 = 0."""
    k0, k1, k2 = kernel_vectors(S)
    point = [C0 * a + C1 * b + C2 * c for a, b, c in zip(k0, k1, k2, strict=True)]
    uu = sum(entry**2 for entry in point[0:7])
    return _zero([uu + C0**2 * (S**2 + 1) ** 2, point[7] + C0 * (S**2 - 1)])


CHECKS = {
    "normal_form_on_the_intersection": normal_form_on_the_intersection,
    "kernel_basis_in_the_kernel": kernel_basis_in_the_kernel,
    "kernel_product_vanishes": kernel_product_vanishes,
    "kernel_in_both_hypersurfaces": kernel_in_both_hypersurfaces,
    "rank_twelve_pfaffian": rank_twelve_pfaffian,
    "kernel_independence": kernel_independence,
    "kernel_sextic": kernel_sextic,
    "lines_are_the_common_kernel_planes": lines_are_the_common_kernel_planes,
    "orbit_modulus_is_constant_on_the_kernel": orbit_modulus_is_constant_on_the_kernel,
}


def identity(name: str) -> bool:
    return CHECKS[name]()


def orbit_ranks() -> dict[str, int]:
    """The generic rank of M(z) over Q(i)(s) at the four types of w in x-perp."""
    d = 1 + S**2
    head = [d, 0, 0, 0, 0, 0, 0, -IU * (1 - S**2), -2 * IU * S]
    types = {
        "w = 0": [0, 0, 0, 0, 0, 0],
        "a only": [IU * d, d, 0, 0, 0, 0],
        "b only": [0, 0, -IU * d, d, 0, 0],
        "a + b": [IU * d, d, -IU * d, d, 0, 0],
    }
    return {name: _function_field_rank(msym(head + w).applyfunc(sp.expand)) for name, w in types.items()}


def _stack(plane: tuple[Vector, Vector]) -> sp.Matrix:
    return sp.Matrix.vstack(msym(plane[0]), msym(plane[1])).applyfunc(sp.expand)


def stack_ranks() -> dict[str, int]:
    return {name: _function_field_rank(_stack(plane)) for name, plane in plane_vectors(S).items()}


def line_x_rank() -> int:
    """The rank of M(c1 k1 + c2 k2) over the field of fractions of Q(i)[s, c1, c2]."""
    k1, k2 = kernel_vectors(S)[1:]
    matrix = msym([C1 * a + C2 * b for a, b in zip(k1, k2, strict=True)]).applyfunc(sp.expand)
    return int(DomainMatrix.from_Matrix(matrix).convert_to(QQ_I.frac_field(S, C1, C2)).rank())


@functools.cache
def _line_x_matrices() -> tuple[Any, Any, Any]:
    """The ring Q(i)[s, c1, c2], M(c1 k1 + c2 k2) over it, and its value at s = 2, c1 = 3, c2 = 5."""
    domain = ring("s,c1,c2", QQ_I)[0]
    k1, k2 = kernel_vectors(S)[1:]
    matrix = msym([C1 * a + C2 * b for a, b in zip(k1, k2, strict=True)])
    return domain, _ring_matrix(matrix, domain), matrix.subs({S: 2, C1: 3, C2: 5})


def line_x_pfaffian(indices: tuple[int, ...]) -> Any:
    """The Pfaffian of the principal 8 x 8 block on the indices, or None where its value at the sample point is 0."""
    domain, entries, sample = _line_x_matrices()
    if sample.extract(list(indices), list(indices)).det() == 0:
        return None
    return sp.expand(_pfaffian_ring(entries, indices, domain).as_expr())


def line_x_groebner() -> dict[str, list[str]]:
    """The 8 x 8 Pfaffians of M(c1 k1 + c2 k2) with their common zeros in the charts c2 = 1 and c1 = 1, c2 = 0."""
    subsets = list(itertools.combinations(range(15), 8))
    polynomials: dict[str, Any] = {}
    for found in parallel.ordered_map(line_x_pfaffian, subsets, min_items=2):
        if found is not None:
            polynomials[sp.srepr(found)] = found
    result = {}
    for label, values in (("c2 = 1", {C2: 1}), ("c1 = 1, c2 = 0", {C1: 1, C2: 0})):
        generators = [sp.expand(poly.subs(values)) for poly in polynomials.values()]
        variables = [v for v in (S, C1) if v not in values]
        basis = sp.groebner([g for g in generators if g != 0], *variables, order="grevlex", extension=IU)
        result[label] = [str(e) for e in basis.exprs]
    return result


def _numbers(rows: Sequence[Sequence[Any]]) -> DomainMatrix:
    return DomainMatrix.from_Matrix(sp.Matrix(rows).applyfunc(sp.expand)).convert_to(QQ_I)


def _rank(rows: Sequence[Sequence[Any]]) -> int:
    return int(_numbers(rows).rank())


def _nullspace(rows: Sequence[Sequence[Any]]) -> list[Vector]:
    basis = _numbers(rows).nullspace().to_Matrix()
    return [list(basis.row(index)) for index in range(basis.rows)]


def _conjugate(vector: Sequence[Any]) -> Vector:
    return [sp.conjugate(entry) for entry in vector]


def _hermitian(a: Sequence[Any], b: Sequence[Any]) -> Any:
    return sp.expand(sum(x * sp.conjugate(y) for x, y in zip(a, b, strict=True)))


def _combination(coefficients: Sequence[Any], vectors: Sequence[Sequence[Any]]) -> Vector:
    return [sp.expand(sum(c * v[index] for c, v in zip(coefficients, vectors, strict=True))) for index in range(15)]


def real_point_facts(frame_vector: Sequence[Any], net: bool = False) -> dict[str, Any]:
    """Exact facts at the real point z: rank M, dim K, the plane P, dim C(P), the cut and dim L.

    The cut is the dimension of {z'' in C(P): z''.conj(p) = 0 for p in P}, dim L_z of A5-435, and dim L = 2 dim L_z.
    """
    kernel = _nullspace(msym(frame_vector).tolist())
    _require(len(kernel) == 3, "the point is not a nullity-4 point")
    zc = _conjugate(frame_vector)
    cut_row = [sum(a * b for a, b in zip(zc, k, strict=True)) for k in kernel]
    coefficients = _nullspace([cut_row])
    _require(len(coefficients) == 2, "the kernel plane is not two-dimensional")
    plane = [_combination(c, kernel) for c in coefficients]
    stack = [*msym(plane[0]).tolist(), *msym(plane[1]).tolist()]
    common = len(stack[0]) - _rank(stack)
    cut = len(stack[0]) - _rank([*stack, *[_conjugate(p) for p in plane]])
    facts: dict[str, Any] = {
        "rank": 15 - len(kernel),
        "kernel": len(kernel),
        "common": common,
        "cut": cut,
        "fiber": 2 * cut,
    }
    if net:
        facts["nullities"] = sorted({15 - _rank(msym(_combination(pair, plane)).tolist()) for pair in NET})
    return facts


def _clear(vector: Sequence[Any]) -> Vector:
    """The vector times the least common multiple of the denominators of its real and imaginary parts."""
    parts = [sp.Rational(sp.re(entry)) for entry in vector] + [sp.Rational(sp.im(entry)) for entry in vector]
    scale = sp.ilcm(*[part.q for part in parts])
    return [sp.expand(entry * scale) for entry in vector]


def witness_point(s: Any, plane: str) -> Vector:
    """The vector of K = <k0, k1, k2> orthogonal for the Hermitian form to the plane P_plane."""
    kernel = kernel_vectors(s)
    p1, p2 = plane_vectors(s)[plane]
    rows = [[_hermitian(k, p) for k in kernel] for p in (p1, p2)]
    solution = _nullspace(rows)
    _require(len(solution) == 1, "the orthogonal complement in K is not a line")
    return _clear(_combination(solution[0], kernel))


def split_coordinates(frame_vector: Sequence[Any]) -> tuple[list[int], list[int]]:
    """The split coordinates z' = z / i^popcount and their conjugate modulo the prime."""
    exact = [sp.expand(entry * IU ** (-((index + 1).bit_count()))) for index, entry in enumerate(frame_vector)]

    def reduce(value: Any) -> int:
        number = sp.nsimplify(sp.expand(value))
        return (int(sp.re(number)) + int(sp.im(number)) * UNIT) % PRIME

    return [reduce(e) for e in exact], [reduce(sp.conjugate(e)) for e in exact]


def witness_facts(job: tuple[int, str]) -> tuple[str, list[int], list[str]]:
    s, plane = job
    point = witness_point(sp.Integer(s), plane)
    facts = real_point_facts(point)
    split, conjugate = split_coordinates(point)
    modular = gauss.kernel_form((split, conjugate), net=False)
    row = [
        facts["rank"],
        facts["kernel"],
        facts["common"],
        facts["cut"],
        facts["fiber"],
        modular["fiber_dimension"],
        modular["plane_nullity"],
        modular["common_kernel"],
        modular["common_kernel_cut"],
    ]
    return f"s = {s}, {plane}", row, [str(entry) for entry in point]


def special_facts(s: int) -> list[int]:
    """Exact dim C(P_x), dim C(P_y), dim C(P_z) and the nullity of M(k1) at the rational s."""
    planes = plane_vectors(sp.Integer(s))
    commons = [15 - _rank(_stack(plane).tolist()) for plane in planes.values()]
    return [*commons, 15 - _rank(msym(kernel_vectors(sp.Integer(s))[1]).tolist())]


def _evaluated(vector: Sequence[Any], s: int) -> list[int]:
    """A frame vector with entries in Z[i][s] at s, modulo the prime."""
    out = []
    for entry in vector:
        value = sp.expand(sp.sympify(entry).subs(S, s))
        out.append((int(sp.re(value)) + int(sp.im(value)) * UNIT) % PRIME)
    return out


_COEFFICIENTS: dict[str, list[Any]] = {}


def _kernel_polynomials() -> dict[str, list[Any]]:
    """The entries of k0, k1, k2, z(s) and the plane vectors as polynomials in s with modular coefficients."""
    if not _COEFFICIENTS:
        rows = {"z": normal_point(S), **{f"k{j}": k for j, k in enumerate(kernel_vectors(S))}}
        for name, plane in plane_vectors(S).items():
            rows[f"p{name}1"], rows[f"p{name}2"] = plane
        for name, vector in rows.items():
            polys = []
            for entry in vector:
                poly = sp.Poly(sp.expand(entry), S) if entry != 0 else sp.Poly(0, S)
                polys.append(
                    [
                        (int(sp.re(c)) + int(sp.im(c)) * UNIT) % PRIME
                        for c in reversed(poly.all_coeffs() if poly.all_coeffs() else [0])
                    ]
                )
            _COEFFICIENTS[name] = polys
    return _COEFFICIENTS


def _horner(coefficients: list[int], s: int) -> int:
    value = 0
    for c in reversed(coefficients):
        value = (value * s + c) % PRIME
    return value


def scan_block(job: tuple[int, int]) -> list[list[int]]:
    """For s in [first, last): (rank M(z(s)), nullity M(k1), dim C of the three planes) modulo the prime."""
    first, last = job
    polys = _kernel_polynomials()
    tally: Counter[tuple[int, ...]] = Counter()
    for s in range(first, last):
        if (1 + s * s) % PRIME == 0:
            continue
        v = {name: [_horner(c, s) for c in entries] for name, entries in polys.items()}
        rank_z = gauss._rank(gauss._block(v["z"]))
        nullity_k1 = 15 - gauss._rank(gauss._block(v["k1"]))
        commons = tuple(
            15 - gauss._rank([*gauss._block(v[f"p{name}1"]), *gauss._block(v[f"p{name}2"])]) for name in ("x", "y", "z")
        )
        tally[(rank_z, nullity_k1, *commons)] += 1
    return [[*key, count] for key, count in sorted(tally.items())]


def scan() -> list[list[int]]:
    step = 2000
    jobs = [(first, min(first + step, PRIME)) for first in range(0, PRIME, step)]
    total: Counter[tuple[int, ...]] = Counter()
    for block in parallel.ordered_map(scan_block, jobs, min_items=2):
        for *key, count in block:
            total[tuple(key)] += count
    return [[*key, count] for key, count in sorted(total.items())]


def _hashed(label: str, count: int) -> list[int]:
    return [int.from_bytes(hashlib.sha256(f"{label}:{n}".encode()).digest()[:8], "big") % PRIME for n in range(count)]


def _null_vector(label: str, orthogonal: Sequence[Sequence[int]]) -> list[int]:
    """A nonzero vector of F_PRIME^7 with v.v = 0, orthogonal to the given vectors, from sha256 of the label."""
    attempt = 0
    while True:
        attempt += 1
        rows = [list(row) for row in orthogonal] or [[0] * 7]
        basis = gauss._nullspace(rows)
        raw = _hashed(f"{label}:{attempt}", 2 * len(basis))
        first = [sum(c * e[i] for c, e in zip(raw[: len(basis)], basis, strict=True)) % PRIME for i in range(7)]
        second = [sum(c * e[i] for c, e in zip(raw[len(basis) :], basis, strict=True)) % PRIME for i in range(7)]
        quad = sum(x * x for x in second) % PRIME
        lin = 2 * sum(x * y for x, y in zip(first, second, strict=True)) % PRIME
        const = sum(x * x for x in first) % PRIME
        if quad == 0:
            continue
        disc = (lin * lin - 4 * quad * const) % PRIME
        root = sp.sqrt_mod(disc, PRIME)
        if root is None:
            continue
        t = (-lin + int(root)) * pow(2 * quad, -1, PRIME) % PRIME
        vector = [(x + t * y) % PRIME for x, y in zip(first, second, strict=True)]
        if any(vector):
            return vector


def isotropic_rank(counter: int) -> list[int]:
    """[rank M, dim span(u, v)] at a sampled point (u, 0, v) with u.u = u.v = v.v = 0."""
    u = _null_vector(f"qg-intersection:isotropic:u:{counter}", [])
    v = _null_vector(f"qg-intersection:isotropic:v:{counter}", [u])
    point = [*u, 0, *v]
    q, delta, _ = (int(x) % PRIME for x in _modular_forms(point))
    _require(q == 0 and delta == 0, "a sampled isotropic point leaves V(Q) n V(Delta)")
    return [gauss._rank(gauss._block(point)), gauss._rank([u, v])]


def _modular_forms(vector: Sequence[int]) -> tuple[int, int, int]:
    u, mu, v = vector[0:7], vector[7], vector[8:15]
    uu, vv = sum(a * a for a in u), sum(a * a for a in v)
    uv = sum(a * b for a, b in zip(u, v, strict=True))
    q = uu + mu * mu + vv
    delta = uu * vv - uv * uv
    return q % PRIME, delta % PRIME, (q * q - 4 * delta) % PRIME


def retained_points() -> list[dict[str, Any]]:
    record = json.loads(gauss.RECORD.read_text(encoding="utf-8"))
    rows = [row for row in record["grid"]["exceptions"] if row["stratum"] == STRATUM and row["fiber_dimension"] == 6]
    return rows


def retained_facts(row: dict[str, Any]) -> list[Any]:
    frame_vector = [
        sp.expand(value * IU ** ((index + 1).bit_count())) for index, value in enumerate(row["split_point"])
    ]
    facts = real_point_facts(frame_vector, net=True)
    return [facts["rank"], facts["kernel"], facts["common"], facts["cut"], facts["nullities"]]


def _inputs() -> dict[str, str]:
    return {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in SOURCE_PATHS}


def compute() -> dict[str, Any]:
    names = list(IDENTITIES)
    identities = dict(zip(names, parallel.ordered_map(identity, names, min_items=2), strict=True))
    jobs = [(s, plane) for s in WITNESS_S for plane in ("x", "y", "z")]
    witnesses = parallel.ordered_map(witness_facts, jobs, min_items=2)
    retained = retained_points()
    record: dict[str, Any] = {
        "schema": SCHEMA,
        "field": FIELD,
        "inputs": _inputs(),
        "identities": identities,
        "orbit_ranks": orbit_ranks(),
        "sextic": SEXTIC,
        "stack_ranks": stack_ranks(),
        "line_x_rank": line_x_rank(),
        "line_x_groebner": line_x_groebner(),
        "special_s": {str(s): special_facts(s) for s in (0, 1, -1)},
        "witnesses": {label: row for label, row, _ in witnesses},
        "witness_points": {label: point for label, _, point in witnesses},
        "scan": scan(),
        "isotropic": _tally(parallel.ordered_map(isotropic_rank, list(range(ISOTROPIC_SAMPLES)), min_items=2)),
        "retained_points": len(retained),
        "retained_facts": [retained_facts(row) for row in retained],
        "pass": True,
    }
    record["pass"] = verdict(record) == []
    return record


def _tally(rows: Sequence[Sequence[Any]]) -> list[list[Any]]:
    counts = Counter(tuple(row) for row in rows)
    return [[*key, counts[key]] for key in sorted(counts)]


def expected_record() -> dict[str, Any]:
    """The record that the constants of this module determine, with the digests of the files as they are."""
    return {
        "schema": SCHEMA,
        "field": FIELD,
        "inputs": _inputs(),
        "identities": dict.fromkeys(IDENTITIES, True),
        "orbit_ranks": dict(ORBIT_RANKS),
        "sextic": SEXTIC,
        "stack_ranks": dict(STACK_RANKS),
        "line_x_rank": LINE_X_RANK,
        "line_x_groebner": copy.deepcopy(LINE_X_GROEBNER),
        "special_s": {s: list(row) for s, row in SPECIAL_S.items()},
        "witnesses": {label: list(row) for label, row in WITNESS_FACTS.items()},
        "witness_points": {label: list(row) for label, row in WITNESS_POINTS.items()},
        "scan": [list(row) for row in SCAN_TALLY],
        "isotropic": [list(row) for row in ISOTROPIC_TALLY],
        "retained_points": RETAINED_POINTS,
        "retained_facts": [copy.deepcopy(RETAINED_FACTS) for _ in range(RETAINED_POINTS)],
        "pass": True,
    }


def verdict(record: dict[str, Any]) -> list[str]:
    """The reasons the record fails its own rules; empty when it passes. The comparison is on serialized text."""
    expected = expected_record()
    problems = []
    messages = {
        "inputs": "the input digests differ from the files",
        "identities": "an exact identity fails",
        "orbit_ranks": "a generic rank of the orbit types differs",
        "sextic": "the sextic of the kernel lines differs",
        "stack_ranks": "a generic rank of a common-kernel stack differs",
        "line_x_rank": "the generic rank of M on the line x differs",
        "line_x_groebner": "the common zeros of the 8 x 8 Pfaffians on the line x differ",
        "special_s": "a dimension at s = 0, 1 or -1 differs",
        "witnesses": "a witness differs from its pinned facts: dim L is 6, 4, 4 at the planes x, y, z",
        "witness_points": "a witness point is missing or differs",
        "scan": "the scan of s modulo the prime differs from its pinned tally",
        "isotropic": "a sampled totally isotropic pair has rank 12",
        "retained_points": "the retained record no longer holds four points with dim L = 6",
        "retained_facts": "a retained point differs from the facts of the plane x",
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
    scanned = sum(row[-1] for row in record["scan"])
    print(f"pass: {len(record['identities'])} identities, {len(record['witnesses'])} witnesses, {scanned} scanned s")


if __name__ == "__main__":
    main()
