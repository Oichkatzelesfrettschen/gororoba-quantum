"""Independent verification of the compact-orbit and kernel-representation statements of the A_5 kernel bundles.

Every table comes from gororoba_quantum/cd_core.py: the real octonion signs from cd_sign(8, p, q) and L_y from
left_mult_matrix_exact(32, y). The compact g_2 (derivations of the real octonions), its lift to A_5, the phase lift,
the stabilizers, the kernel restrictions, the Casimir decompositions, the orbit invariants and the representation-ring
quotient are built here. From earlier records the script imports only the split-coordinate helpers of
docs/evidence/a5-strata-regularity/verify_regularity_independent.py (nilpotent split derivations, their exponentials,
the G_2 and boost actions on split points, the representatives REPS, the H-tangent vectors) and y_from_split, nullspace
from docs/evidence/a5-rank-strata-equations/rederive_strata_equations.py. Nothing comes from the kernel-bundle record's
own scripts.

Coordinates. z_k = y_k + i y_(16+k), k = 1..15; u = z_1..z_7, mu = z_8, v = z_9..z_15 (original coordinates). The
compact symmetry algebra is k = g_2 + u(1): a real derivation D of the octonions acts on y through the A_5 automorphism
that applies D to each of the four octonion blocks (indices 0-7, 8-15, 16-23, 24-31); the phase generator acts as
z -> i z. J = L_(e_16) is the complex structure on ker L_y.

Test points. Each recorded representative is moved by products of unipotent split G_2(C) elements exp(N) and the
boost (c, s) = (5/4, 3/4) or (13/12, 5/12), which are non-compact in original coordinates, so the moved points carry
generic values of the compact-orbit invariants. Every point is listed in the source; no random value enters.

Normalizations. Su(2) and su(3) decompositions use the Casimir of the Killing form, which takes the value
n (n + 2) / 8 on V_n (spin n/2) of su(2) and 4/9 on 3 and on conj(3) of su(3). A central generator Z is primitive
when the operator -Phi Z on the doubly pure space (Phi the phase generator, so Z = w Phi on the weight-w space) has
integer eigenvalues of greatest common divisor one; its sign makes the phase coefficient positive. The phase lift is
Y_Phi: x_0 -> 2 x_16, x_16 -> -2 x_0 on R^32 (zero elsewhere); the lift is unique up to adding a multiple of J,
which shifts every kernel weight by the same amount. A kernel weight w means Z = w J on that subspace.

Usage:
    GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 GOROROBA_WORKERS=4 "$PYTHON" -B -W error \
        docs/evidence/a5-kernel-bundles/verify_kernel_bundles_independent.py \
        --out docs/evidence/a5-kernel-bundles/verification.json
    ... verify_kernel_bundles_independent.py --self-test
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
import time
from collections import Counter
from collections.abc import Sequence
from fractions import Fraction
from math import gcd
from pathlib import Path
from typing import Any

import flint

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "docs" / "evidence" / "a5-strata-regularity"))
sys.path.insert(0, str(ROOT / "docs" / "evidence" / "a5-rank-strata-equations"))

import rederive_strata_equations as rd  # noqa: E402
import verify_regularity_independent as vr  # noqa: E402

import parallel  # noqa: E402
from cd_core import cd_multiply_exact, cd_sign, left_mult_matrix_exact  # noqa: E402

Mat = list[list[Fraction]]
Vec = list[Fraction]

# Mutation switches read by the self-test; the production run leaves every entry False.
MUTATION: dict[str, bool] = {
    "drop_leibniz_term": False,
    "zero_phase_lift": False,
    "no_phase_direction": False,
    "unmoved_points": False,
    "flip_j": False,
    "wrong_seven_restriction": False,
}

# ---------------------------------------------------------------------------------------------------------------------
# Exact linear algebra


def fm(rows: Sequence[Sequence[Any]]) -> Any:
    nr = len(rows)
    nc = len(rows[0]) if nr else 0
    return flint.fmpq_mat(nr, nc, [flint.fmpq(Fraction(x).numerator, Fraction(x).denominator) for r in rows for x in r])


def to_rows(m: Any) -> Mat:
    return [[Fraction(int(m[i, j].p), int(m[i, j].q)) for j in range(m.ncols())] for i in range(m.nrows())]


def rank(rows: Sequence[Sequence[Any]]) -> int:
    if not rows or not rows[0]:
        return 0
    return int(fm(rows).rank())


def kernel(rows: Sequence[Sequence[Any]]) -> list[Vec]:
    """Right nullspace basis (python-flint fmpz nullspace via rederive_strata_equations.nullspace)."""
    return rd.nullspace(rows)


def identity(n: int) -> Mat:
    return [[Fraction(int(i == j)) for j in range(n)] for i in range(n)]


def matmul(a: Mat, b: Mat) -> Mat:
    return to_rows(fm(a) * fm(b))


def transpose(a: Sequence[Sequence[Any]]) -> Mat:
    return [[Fraction(a[i][j]) for i in range(len(a))] for j in range(len(a[0]))]


def comm(a: Mat, b: Mat) -> Mat:
    fa, fb = fm(a), fm(b)
    return to_rows(fa * fb - fb * fa)


def lin(coeffs: Sequence[Fraction], mats: Sequence[Mat]) -> Mat:
    n, m = len(mats[0]), len(mats[0][0])
    out = [[Fraction(0)] * m for _ in range(n)]
    for c, mat in zip(coeffs, mats, strict=True):
        if c:
            for i in range(n):
                for j in range(m):
                    if mat[i][j]:
                        out[i][j] += c * mat[i][j]
    return out


def matvec(a: Sequence[Sequence[Fraction]], x: Sequence[Fraction]) -> Vec:
    return [sum((a[i][j] * x[j] for j in range(len(x)) if a[i][j]), Fraction(0)) for i in range(len(a))]


def coords_in_span(basis: Sequence[Vec], target: Vec) -> Vec | None:
    """Coefficients c with sum c_i basis_i = target, or None when target lies outside the span."""
    a = fm(transpose(basis))
    gram = a.transpose() * a
    rhs = a.transpose() * fm([[x] for x in target])
    sol = gram.solve(rhs)
    c = [Fraction(int(sol[i, 0].p), int(sol[i, 0].q)) for i in range(len(basis))]
    back = [sum((c[i] * basis[i][k] for i in range(len(basis))), Fraction(0)) for k in range(len(target))]
    return c if back == list(target) else None


def restrict(op: Mat, basis: Sequence[Vec]) -> Mat:
    """Matrix M with op B = B M for the column basis B of an op-invariant subspace; raises if not invariant."""
    b = fm(transpose(basis))
    ob = fm(op) * b
    m = (b.transpose() * b).solve(b.transpose() * ob)
    if b * m != ob:
        raise RuntimeError("subspace is not invariant under the operator")
    return to_rows(m)


def eigenspace_dims(mat: Mat, values: Sequence[Fraction]) -> dict[str, int]:
    n = len(mat)
    out = {}
    for lam in values:
        shifted = [[mat[i][j] - (lam if i == j else 0) for j in range(n)] for i in range(n)]
        out[str(lam)] = n - rank(shifted)
    return out


def rational_roots(mat: Mat) -> list[Fraction]:
    """Rational eigenvalues with algebraic multiplicity; raises if the characteristic polynomial has other factors."""
    poly = fm(mat).charpoly()
    _content, factors = poly.factor()
    roots: list[Fraction] = []
    for fac, mult in factors:
        if fac.degree() != 1:
            raise RuntimeError(f"non-rational eigenvalue factor {fac}")
        r = -fac[0] / fac[1]
        roots += [Fraction(int(r.p), int(r.q))] * int(mult)
    return sorted(roots)


# ---------------------------------------------------------------------------------------------------------------------
# Real octonions, compact g_2 and its lift to A_5


def oct_sign(p: int, q: int) -> int:
    return cd_sign(8, p, q)


def compact_derivations() -> list[Mat]:
    """Derivations D of the cd_core octonions (8 x 8, D e_0 = 0): D(e_p e_q) = D(e_p) e_q + e_p D(e_q)."""
    rows: list[list[int]] = []
    for p in range(8):
        for q in range(8):
            for k in range(8):
                r = [0] * 64
                r[k * 8 + (p ^ q)] += oct_sign(p, q)
                r[(k ^ q) * 8 + p] -= oct_sign(k ^ q, q)
                if not MUTATION["drop_leibniz_term"]:
                    r[(p ^ k) * 8 + q] -= oct_sign(p, p ^ k)
                rows.append(r)
    basis = kernel(rows)
    return [[[v[i * 8 + j] for j in range(8)] for i in range(8)] for v in basis]


def lift32(d: Mat) -> Mat:
    out = [[Fraction(0)] * 32 for _ in range(32)]
    for blk in range(4):
        for i in range(8):
            for j in range(8):
                out[8 * blk + i][8 * blk + j] = d[i][j]
    return out


def unit(n: int, k: int) -> Vec:
    return [Fraction(int(i == k)) for i in range(n)]


def lmat(y: Sequence[Fraction]) -> Mat:
    return [list(r) for r in left_mult_matrix_exact(32, list(y))]


L_BASIS = [lmat(unit(32, j)) for j in range(32)]
DOUBLY_PURE = [j for j in range(32) if j not in (0, 16)]


def l_of(y: Sequence[Fraction]) -> Mat:
    return lin(list(y), L_BASIS)


def derivation_lift_failures(d32: Mat) -> int:
    """Basis j where L_(D e_j) != [D, L_j] in A_5."""
    bad = 0
    for j in range(32):
        col = [d32[i][j] for i in range(32)]
        if l_of(col) != comm(d32, L_BASIS[j]):
            bad += 1
    return bad


PHASE = [[Fraction(0)] * 32 for _ in range(32)]  # z -> i z on doubly pure y
for _k in range(1, 16):
    PHASE[_k][16 + _k] = Fraction(-1)
    PHASE[16 + _k][_k] = Fraction(1)


def phase_lift() -> Mat:
    y = [[Fraction(0)] * 32 for _ in range(32)]
    if not MUTATION["zero_phase_lift"]:
        y[0][16] = Fraction(2)
        y[16][0] = Fraction(-2)
    return y


J32 = L_BASIS[16]


def check_algebra() -> dict[str, Any]:
    """Compact g_2, its A_5 lift, the phase lift, and the ambiguity of lifts."""
    ders = compact_derivations()
    if len(ders) != 14:
        raise RuntimeError(f"compact derivation space has dimension {len(ders)}")
    skew = all(d[i][j] == -d[j][i] for d in ders for i in range(8) for j in range(8))
    d32s = [lift32(d) for d in ders]
    lift_bad = sum(parallel.ordered_map(derivation_lift_failures, d32s, min_items=1))
    commutes_j = all(comm(d, J32) == [[0] * 32 for _ in range(32)] for d in d32s)
    # cd_multiply_exact cross-check of the table on every octonion pair
    table_bad = sum(
        1
        for p in range(8)
        for q in range(8)
        if list(cd_multiply_exact(8, unit(8, p), unit(8, q))) != [oct_sign(p, q) * x for x in unit(8, p ^ q)]
    )
    yphi = phase_lift()
    # Y' from j = 1, then L_(Phi e_j) = Y' L_j - L_j Y_Phi for every doubly pure j
    l1 = fm(L_BASIS[1])
    yprime = (fm(l_of([PHASE[i][1] for i in range(32)])) + l1 * fm(yphi)) * l1.inv()
    yprime_rows = to_rows(yprime)
    phase_bad = sum(
        not ok for ok in parallel.ordered_map(_phase_identity_ok, [(j, yphi, yprime_rows) for j in DOUBLY_PURE])
    )
    zero = [[Fraction(0)] * 32 for _ in range(32)]
    phase_commutes = comm(yphi, J32) == zero and all(comm(yphi, d) == zero for d in d32s)
    homog = homogeneous_lifts()
    # R_(e_16) (x -> x e_16) lifts the base generator L_(e_16) = -Phi; it equals -(Y_Phi + J), which fixes the
    # convention change between this script's weights and weights read with that lift.
    r16 = [[Fraction(0)] * 32 for _ in range(32)]
    for c in range(32):
        r16[c ^ 16][c] = Fraction(cd_sign(32, c, 16))
    right_lift = r16 == [[-yphi[i][j] - J32[i][j] for j in range(32)] for i in range(32)]
    base_minus_phase = all(J32[i][j] == -PHASE[i][j] for i in DOUBLY_PURE for j in DOUBLY_PURE)
    ok = (
        skew and lift_bad == 0 and commutes_j and table_bad == 0 and phase_bad == 0 and phase_commutes and homog["pass"]
    )
    return {
        "compact_g2_dimension": len(ders),
        "derivations_skew": skew,
        "octonion_table_vs_cd_multiply_exact_failures": table_bad,
        "a5_derivation_lift_failures": lift_bad,
        "lifts_commute_with_J": commutes_j,
        "phase_lift_identity_failures": phase_bad,
        "phase_lift_central": phase_commutes,
        "lift_ambiguity": homog,
        "R_e16_equals_-(Y_Phi+J)": right_lift,
        "L_e16_on_base_equals_-Phi": base_minus_phase,
        "pass": ok,
    }


def _phase_identity_ok(item: tuple[int, Mat, Mat]) -> bool:
    """L_(Phi e_j) = Y' L_j - L_j Y_Phi at one doubly pure basis index j."""
    j, yphi, yprime = item
    lhs = fm(l_of([PHASE[i][j] for i in range(32)]))
    return bool(lhs == fm(yprime) * fm(L_BASIS[j]) - fm(L_BASIS[j]) * fm(yphi))


def homogeneous_lifts() -> dict[str, Any]:
    """All (Y, Y') with L_j Y = Y' L_j for every doubly pure j: a sign-graph on the 2048 unknowns.

    Equation (j, a, b): Y'[a, j^b] sign(j, b) = sign(j, a^j) Y[a^j, b]. Each component of the graph is one free
    parameter unless a cycle forces a sign contradiction, which forces zero.
    """
    n = 2048
    parent = list(range(n))
    par_sign = [1] * n  # value(x) = par_sign[x] * value(parent[x])

    def find(x: int) -> tuple[int, int]:
        s = 1
        path = []
        while parent[x] != x:
            path.append(x)
            s *= par_sign[x]
            x = parent[x]
        root = x
        # path compression
        acc = s
        for node in path:
            sn = par_sign[node]
            parent[node] = root
            par_sign[node] = acc
            acc *= sn
        return root, s

    zero_roots: set[int] = set()
    for j in DOUBLY_PURE:
        for a in range(32):
            for b in range(32):
                p_var = 1024 + a * 32 + (j ^ b)
                y_var = (a ^ j) * 32 + b
                ratio = cd_sign(32, j, a ^ j) * cd_sign(32, j, b)  # Y' = ratio * Y
                rp, sp = find(p_var)
                ry, sy = find(y_var)
                if rp == ry:
                    if sp != ratio * sy:
                        zero_roots.add(rp)
                else:
                    parent[rp] = ry
                    par_sign[rp] = sp * ratio * sy
                    if rp in zero_roots:
                        zero_roots.add(ry)
    roots: dict[int, list[tuple[int, int]]] = {}
    for x in range(n):
        r, s = find(x)
        roots.setdefault(r, []).append((x, s))
    free = [r for r in roots if find(r)[0] not in {find(z)[0] for z in zero_roots}]
    sols = []
    for r in free:
        yv = [[Fraction(0)] * 32 for _ in range(32)]
        pv = [[Fraction(0)] * 32 for _ in range(32)]
        for x, s in roots[r]:
            if x < 1024:
                yv[x // 32][x % 32] = Fraction(s)
            else:
                pv[(x - 1024) // 32][(x - 1024) % 32] = Fraction(s)
        sols.append(flat_pair(yv, pv))
    ident = flat_pair(identity(32), identity(32))
    jpair = flat_pair(J32, [[-x for x in r] for r in J32])
    span_ok = len(sols) == 2 and rank([*sols, ident, jpair]) == 2
    return {"dimension": len(sols), "spanned_by_(I,I)_and_(J,-J)": span_ok, "pass": span_ok}


def flat_pair(a: Mat, b: Mat) -> Vec:
    return [x for r in a for x in r] + [x for r in b for x in r]


DERS = compact_derivations()
D7 = [[[d[i][j] for j in range(1, 8)] for i in range(1, 8)] for d in DERS]
D32 = [lift32(d) for d in DERS]
YPHI = phase_lift()


def structure_constants() -> list[list[Vec]]:
    """f_ab^k with [D_a, D_b] = sum_k f_ab^k D_k, from one normal-equation solve with all 196 right-hand sides."""
    basis = fm(transpose([[x for r in d for x in r] for d in D7]))  # 49 x 14
    rhs = fm(transpose([[x for r in comm(D7[a], D7[b]) for x in r] for a in range(14) for b in range(14)]))
    sol = (basis.transpose() * basis).solve(basis.transpose() * rhs)
    if basis * sol != rhs:
        raise RuntimeError("g_2 not closed under brackets")
    cols = to_rows(sol.transpose())  # 196 x 14
    return [[cols[14 * a + b] for b in range(14)] for a in range(14)]


STRUCT = structure_constants()


def bracket(x: Vec, y: Vec) -> Vec:
    """Bracket in k = g_2 + u(1), coordinates (c_1..c_14, t); the phase is central."""
    out = [Fraction(0)] * 15
    for a in range(14):
        if x[a]:
            for b in range(14):
                if y[b]:
                    w = x[a] * y[b]
                    for k in range(14):
                        if STRUCT[a][b][k]:
                            out[k] += w * STRUCT[a][b][k]
    return out


def y_action(x: Vec) -> Mat:
    """Action of k-element x on R^32 (doubly pure y)."""
    return lin(list(x), [*D32, PHASE])


def kernel_lift(x: Vec) -> Mat:
    return lin(list(x), [*D32, YPHI])


# ---------------------------------------------------------------------------------------------------------------------
# Test points

NILS = vr.nilpotent_derivations()


def scaled(m: Sequence[Sequence[Fraction]], c: Any) -> list[list[Any]]:
    return [[c * x for x in r] for r in m]


def move(z: Sequence[Any], ops: Sequence[tuple[Any, ...]]) -> list[Any]:
    """Apply unipotent split G_2(C) elements exp(c N) (c rational or Gaussian rational) and real boosts."""
    out = list(z)
    for op in ops:
        if op[0] == "u":
            out = vr.act_g2(vr.expm_nilpotent(scaled(NILS[op[1]], op[2])), out)
        elif op[0] == "b":
            out = vr.act_boost(op[1], op[2], out)
        else:
            raise ValueError(op)
    return out


B1 = ("b", Fraction(5, 4), Fraction(3, 4))
B2 = ("b", Fraction(13, 12), Fraction(5, 12))
# complex boost c = (w + 1/w)/2, s = (w - 1/w)/2 at w = 1 + i: c^2 - s^2 = 1, moves lambda off the imaginary axis
B3 = ("b", vr.Gq(Fraction(3, 4), Fraction(1, 4)), vr.Gq(Fraction(1, 4), Fraction(3, 4)))
MOVES: dict[str, list[tuple[Any, ...]]] = {
    "m1": [("u", 0, 1), ("u", 20, Fraction(1, 2)), B1],
    "m2": [("u", 28, -1), ("u", 6, 1), ("u", 38, Fraction(1, 3)), B2],
    "m3": [("u", 14, 2), ("u", 33, 1), B1, ("u", 10, -1)],
    # Gaussian-rational unipotents reach moduli off the slice that real split points stay on
    "m4": [("u", 0, vr.Gq(1, 1)), ("u", 20, vr.Gq(0, Fraction(1, 2))), B3, ("u", 14, vr.Gq(2, -1))],
    "m5": [("u", 28, vr.Gq(Fraction(1, 2), 1)), ("u", 6, 1), ("u", 38, vr.Gq(0, 1)), B3, B2, ("u", 33, vr.Gq(1, -2))],
}


def original_to_split(z: Sequence[vr.Gq]) -> list[vr.Gq]:
    return [vr.i_pow(-vr.popcount(k + 1)) * z[k] for k in range(15)]


def original_point(u: Sequence[Any], mu: Any, v: Sequence[Any]) -> list[vr.Gq]:
    return original_to_split([vr.Gq.of(x) for x in [*u, mu, *v]])


_E7 = [1, 0, 0, 0, 0, 0, 0]
_ONE3 = [1, 1, 1, 0, 0, 0, 0]
EXTRA: dict[tuple[str, str], list[Any]] = {
    # rho = 1 points away from the recorded representatives
    ("Va+", "c1"): [Fraction(x) for x in [3, 4, 0, 0, 0, 0, 0, 0, 3, 4, 0, 0, 0, 0, 0]],
    ("Va-", "c1"): [Fraction(x) for x in [3, 4, 0, 0, 0, 0, 0, 0, -3, -4, 0, 0, 0, 0, 0]],
    # V at rho = 1: z = (u, mu, lambda u), mu^2 = -(1 + lambda^2) u.u, lambda = 0 and lambda = 2i
    ("V", "c1"): original_point(_E7, vr.Gq(0, 1), [0] * 7),
    ("V", "c2"): original_point(_ONE3, 3, [vr.Gq(0, 2) * x for x in _ONE3]),
}


def split_point(name: str, move_key: str) -> list[Any]:
    if (name, move_key) in EXTRA:
        return list(EXTRA[(name, move_key)])
    base = list(vr.REPS[name])
    if move_key == "rep" or MUTATION["unmoved_points"]:
        return base
    return move(base, MOVES[move_key])


def y_of(zs: Sequence[Any]) -> Vec:
    """y in A_5 from split coordinates: z_k = i^popcount(k) z'_k, y_k = Re z_k, y_(16+k) = Im z_k."""
    y = [Fraction(0)] * 32
    for k in range(15):
        zk = vr.i_pow(vr.popcount(k + 1)) * vr.Gq.of(zs[k])
        y[k + 1] = zk.re
        y[16 + k + 1] = zk.im
    if all(not isinstance(x, vr.Gq) for x in zs) and y != [Fraction(x) for x in rd.y_from_split(list(zs))]:
        raise RuntimeError("y_of disagrees with rederive_strata_equations.y_from_split")
    return y


def fmt(x: Any) -> str:
    g = vr.Gq.of(x)
    return str(g.re) if not g.im else f"{g.re}+{g.im}i"


def z_parts(y: Sequence[Fraction]) -> tuple[list[vr.Gq], vr.Gq, list[vr.Gq]]:
    z = [vr.Gq(y[k], y[16 + k]) for k in range(1, 16)]
    return z[0:7], z[7], z[8:15]


# ---------------------------------------------------------------------------------------------------------------------
# Lie algebra analysis of a stabilizer


def stabilizer(y: Vec) -> list[Vec]:
    cols = [matvec(D32[a], y) for a in range(14)] + [matvec(PHASE, y)]
    if MUTATION["no_phase_direction"]:
        cols[14] = [Fraction(0)] * 32
    sols = kernel(transpose(cols))
    if MUTATION["no_phase_direction"]:
        sols = [s for s in sols if s[14] == 0]
    return sols


def ad_matrices(basis: Sequence[Vec]) -> list[Mat]:
    mats = []
    for x in basis:
        cols = []
        for y in basis:
            c = coords_in_span(list(basis), bracket(x, y))
            if c is None:
                raise RuntimeError("stabilizer not closed under brackets")
            cols.append(c)
        mats.append(transpose(cols))
    return mats


def killing(basis: Sequence[Vec]) -> Mat:
    ads = ad_matrices(basis)
    return [[sum((matmul(a, b)[i][i] for i in range(len(basis))), Fraction(0)) for b in ads] for a in ads]


def negative_definite(m: Mat) -> bool:
    n = len(m)
    for k in range(1, n + 1):
        det = fm([r[:k] for r in m[:k]]).det()
        if (det < 0) != (k % 2 == 1) or det == 0:
            return False
    return True


def derived(basis: Sequence[Vec]) -> list[Vec]:
    brs = [bracket(a, b) for i, a in enumerate(basis) for b in basis[i + 1 :]]
    brs = [b for b in brs if any(b)]
    if not brs:
        return []
    return kernel_complement_basis(brs)


def kernel_complement_basis(vecs: Sequence[Vec]) -> list[Vec]:
    """A basis of span(vecs) chosen among the vectors."""
    out: list[Vec] = []
    for v in vecs:
        if rank([*out, v]) > len(out):
            out.append(v)
    return out


def center(basis: Sequence[Vec]) -> list[Vec]:
    n = len(basis)
    rows = []
    for y in basis:
        cols = [bracket(x, y) for x in basis]
        for k in range(15):
            rows.append([cols[i][k] for i in range(n)])
    sols = kernel(rows)
    return [[sum((s[i] * basis[i][k] for i in range(n)), Fraction(0)) for k in range(15)] for s in sols]


def casimir(basis: Sequence[Vec], rep: Sequence[Mat]) -> Mat:
    kinv = to_rows(fm(killing(basis)).inv())
    n = len(rep[0])
    out = [[Fraction(0)] * n for _ in range(n)]
    for a in range(len(basis)):
        for b in range(len(basis)):
            if kinv[a][b]:
                prod = matmul(rep[a], rep[b])
                for i in range(n):
                    for j in range(n):
                        out[i][j] += kinv[a][b] * prod[i][j]
    return out


def su2_multiplicities(basis: Sequence[Vec], rep: Sequence[Mat], complex_dim_factor: int) -> dict[str, int]:
    """Multiplicity of V_n from the Killing Casimir, value n(n+2)/8, eigenspace real dimension / (factor (n+1))."""
    om = casimir(basis, rep)
    size = len(om)
    out: dict[str, int] = {}
    total = 0
    for nn in range(0, 9):
        lam = Fraction(nn * (nn + 2), 8)
        dim = size - rank([[om[i][j] - (lam if i == j else 0) for j in range(size)] for i in range(size)])
        if dim:
            if dim % (complex_dim_factor * (nn + 1)):
                raise RuntimeError("eigenspace dimension not a multiple of the irreducible dimension")
            out[f"V_{nn}"] = dim // (complex_dim_factor * (nn + 1))
            total += dim
    if total != size:
        raise RuntimeError("Casimir has eigenvalues outside n(n+2)/8")
    return out


def primitive_central(z: Vec) -> tuple[Vec, list[Fraction]]:
    """Scale the central element to the primitive generator; returns it and its weights on the doubly pure space."""
    act = y_action(z)
    weight_op = [[-x for x in r] for r in matmul(PHASE, act)]
    sub = [r for i, r in enumerate(weight_op) if i in DOUBLY_PURE]
    sub = [[r[j] for j in DOUBLY_PURE] for r in sub]
    roots = rational_roots(sub)
    nonzero = [r for r in roots if r]
    den = 1
    for r in nonzero:
        den = den * r.denominator // gcd(den, r.denominator)
    ints = [int(r * den) for r in nonzero]
    g = 0
    for v in ints:
        g = gcd(g, abs(v))
    scale = Fraction(den, g)
    zz = [scale * x for x in z]
    if zz[14] < 0:
        zz = [-x for x in zz]
        scale = -scale
    return zz, sorted(r * scale for r in roots)


def kernel_weights(zgen: Vec, kb: Sequence[Vec]) -> list[Fraction]:
    mz = restrict(kernel_lift(zgen), kb)
    jj = J32 if not MUTATION["flip_j"] else [[-x for x in r] for r in J32]
    mj = restrict(jj, kb)
    w = [[-x for x in r] for r in matmul(mj, mz)]
    roots = rational_roots(w)
    # each complex weight appears twice in the real 2m-dimensional operator
    cnt = Counter(roots)
    if any(c % 2 for c in cnt.values()):
        raise RuntimeError("odd real multiplicity of a kernel weight")
    return sorted(Fraction(r) for r, c in cnt.items() for _ in range(c // 2))


def joint_decomposition(su2: Sequence[Vec], zgen: Vec, kb: Sequence[Vec]) -> dict[str, int]:
    """Multiplicities of V_(n, w): su(2) highest weight n and central weight w on the complex kernel."""
    rep = [restrict(kernel_lift(x), kb) for x in su2]
    om = casimir(su2, rep)
    mz = restrict(kernel_lift(zgen), kb)
    jj = J32 if not MUTATION["flip_j"] else [[-x for x in r] for r in J32]
    mj = restrict(jj, kb)
    w = [[-x for x in r] for r in matmul(mj, mz)]
    size = len(om)
    out: dict[str, int] = {}
    for nn in range(0, 5):
        lam = Fraction(nn * (nn + 2), 8)
        es = kernel([[om[i][j] - (lam if i == j else 0) for j in range(size)] for i in range(size)])
        if not es:
            continue
        wr = restrict(w, es)
        for val, c in Counter(rational_roots(wr)).items():
            key = f"V_({nn},{val})"
            out[key] = c // (2 * (nn + 1))
    return out


def commutant_center_structure(rep: Sequence[Mat]) -> Mat:
    """A non-scalar element of the center of the commutant of rep (for 2 x realified 3 of su(3) it is the complex
    structure I0 of the realified 3, under which the module is 3 + 3 or conj(3) + conj(3))."""
    n = len(rep[0])
    rows = []
    for m in rep:
        for i in range(n):
            for j in range(n):
                row = [Fraction(0)] * (n * n)
                for k in range(n):
                    row[i * n + k] += m[k][j]  # (T M)_ij
                    row[k * n + j] -= m[i][k]  # (M T)_ij
                rows.append(row)
    comm_basis = [[[v[i * n + j] for j in range(n)] for i in range(n)] for v in kernel(rows)]
    rows = []
    for t in comm_basis:
        for i in range(n):
            for j in range(n):
                rows.append(
                    [sum((c[i][k] * t[k][j] - t[i][k] * c[k][j] for k in range(n)), Fraction(0)) for c in comm_basis]
                )
    cent = kernel(rows)
    for coeffs in cent:
        s_mat = lin(coeffs, comm_basis)
        if any(s_mat[i][j] != (s_mat[0][0] if i == j else 0) for i in range(n) for j in range(n)):
            trace = sum((s_mat[i][i] for i in range(n)), Fraction(0)) / n
            return [[s_mat[i][j] - (trace if i == j else 0) for j in range(n)] for i in range(n)]
    raise RuntimeError("commutant center is scalar")


# ---------------------------------------------------------------------------------------------------------------------
# Per-point analysis


PIECES = {
    "B9": ("B9", 12),
    "V": ("V", 12),
    "VB": ("VB", 12),
    "Va+": ("Va+", 12),
    "Va-": ("Va-", 12),
    "N+": ("N+", 16),
    "N-": ("N-", 16),
}


def gdot(x: Sequence[vr.Gq], y: Sequence[vr.Gq]) -> vr.Gq:
    acc = vr.Gq(0)
    for a, b in zip(x, y, strict=True):
        acc = acc + a * b
    return acc


def hdot(x: Sequence[vr.Gq], y: Sequence[vr.Gq]) -> vr.Gq:
    acc = vr.Gq(0)
    for a, b in zip(x, y, strict=True):
        acc = acc + a.conj() * b
    return acc


def gcross(x: Sequence[vr.Gq], y: Sequence[vr.Gq]) -> list[vr.Gq]:
    """Imaginary part of the octonion product of imaginary x, y (complex-bilinear), from cd_sign(8, ., .)."""
    out = [vr.Gq(0)] * 7
    for p in range(1, 8):
        for q in range(1, 8):
            k = p ^ q
            if k:
                out[k - 1] = out[k - 1] + oct_sign(p, q) * x[p - 1] * y[q - 1]
    return out


def invariants(name: str, y: Vec) -> dict[str, Any]:
    u, mu, v = z_parts(y)
    out: dict[str, Any] = {}
    uu = gdot(u, u)
    nu = hdot(u, u).re
    if name in ("Va+", "Va-", "N+", "N-"):
        sgn = 1 if name.endswith("+") else -1
        out["form_(u,0,+-iu)"] = mu == 0 and all(b == vr.Gq(0, sgn) * a for a, b in zip(u, v, strict=True))
        out["rho_squared"] = str((uu.re**2 + uu.im**2) / nu**2)
    if name == "V":
        idx = next(k for k in range(7) if u[k])
        lam = v[idx] / u[idx]
        out["collinear_v=lambda_u"] = all(b == lam * a for a, b in zip(u, v, strict=True))
        out["lambda"] = [str(lam.re), str(lam.im)]
        out["rho_squared"] = str((uu.re**2 + uu.im**2) / nu**2)
        out["mu^2+(1+lambda^2)u.u=0"] = mu * mu + (1 + lam * lam) * uu == vr.Gq(0)
        out["mu_nonzero"] = bool(mu)
    if name in ("B9", "VB"):
        g11, g12, g22 = hdot(u, u), hdot(u, v), hdot(v, v)
        tr = g11.re + g22.re
        out["mu_zero"] = mu == vr.Gq(0)
        out["null"] = uu == vr.Gq(0) and gdot(u, v) == vr.Gq(0) and gdot(v, v) == vr.Gq(0)
        out["cross_zero"] = all(c == vr.Gq(0) for c in gcross(u, v))
        out["gram_normalized"] = [str(g11.re / tr), str(g12.re / tr), str(g12.im / tr)]
        out["gram_rank"] = 2 if (g11 * g22 - g12 * g12.conj()) else 1
    return out


def piece_tangent(zs: Sequence[Fraction]) -> list[Vec]:
    """Real tangent vectors (in y coordinates) of the complex H-orbit through the split point zs."""
    vecs = []
    for w in vr.h_tangent(list(zs)):
        wz = [vr.i_pow(vr.popcount(k + 1)) * vr.Gq.of(w[k]) for k in range(15)]
        for mult in (vr.Gq(1), vr.Gq(0, 1)):
            yv = [Fraction(0)] * 32
            for k in range(15):
                c = mult * wz[k]
                yv[k + 1] = c.re
                yv[16 + k + 1] = c.im
            vecs.append(yv)
    return kernel_complement_basis(vecs)


class Dual:
    """a + b eps with eps^2 = 0 over the rationals, for exact directional derivatives."""

    __slots__ = ("a", "b")

    def __init__(self, a: Any, b: Any = 0) -> None:
        self.a = Fraction(a)
        self.b = Fraction(b)

    @staticmethod
    def of(x: Any) -> Dual:
        return x if isinstance(x, Dual) else Dual(x)

    def __add__(self, o: Any) -> Dual:
        o = Dual.of(o)
        return Dual(self.a + o.a, self.b + o.b)

    __radd__ = __add__

    def __sub__(self, o: Any) -> Dual:
        o = Dual.of(o)
        return Dual(self.a - o.a, self.b - o.b)

    def __rsub__(self, o: Any) -> Dual:
        return Dual.of(o) - self

    def __mul__(self, o: Any) -> Dual:
        o = Dual.of(o)
        return Dual(self.a * o.a, self.a * o.b + self.b * o.a)

    __rmul__ = __mul__

    def __truediv__(self, o: Any) -> Dual:
        o = Dual.of(o)
        return Dual(self.a / o.a, (self.b * o.a - self.a * o.b) / (o.a * o.a))


def rdot(x: Sequence[Any], y: Sequence[Any]) -> Any:
    acc: Any = 0
    for a, b in zip(x, y, strict=True):
        acc = acc + a * b
    return acc


def real_invariants(name: str, y: Sequence[Any]) -> list[Any]:
    """The stated compact-orbit invariants as real rational functions of y (generic arithmetic)."""
    a, b = list(y[1:8]), list(y[17:24])  # u = a + i b
    c, d = list(y[9:16]), list(y[25:32])  # v = c + i d
    aa, bb, ab = rdot(a, a), rdot(b, b), rdot(a, b)
    nu = aa + bb
    rho2 = ((aa - bb) * (aa - bb) + 4 * ab * ab) / (nu * nu)
    if name in ("Va+", "Va-"):
        return [rho2]
    uv_re = rdot(a, c) + rdot(b, d)  # u^* v
    uv_im = rdot(a, d) - rdot(b, c)
    if name == "V":
        return [uv_re / nu, uv_im / nu, rho2]
    vv = rdot(c, c) + rdot(d, d)
    tr = nu + vv
    return [nu / tr, uv_re / tr, uv_im / tr]


def level_set_rank(name: str, y: Vec, zs: Sequence[Fraction]) -> dict[str, int]:
    tan = piece_tangent(zs)
    # unit-section tangent: combinations orthogonal to y
    coeffs = kernel([[rdot(t, y) for t in tan]])
    unit_tan = [[sum((cf[i] * tan[i][k] for i in range(len(tan))), Fraction(0)) for k in range(32)] for cf in coeffs]
    rows = []
    for t in unit_tan:
        dual = [Dual(y[k], t[k]) for k in range(32)]
        rows.append([f.b for f in real_invariants(name, dual)])
    r = rank(transpose(rows)) if rows else 0
    return {"piece_real_dim": len(tan), "unit_section_dim": len(unit_tan), "invariant_rank": r}


def analyze_point(job: tuple[str, str]) -> dict[str, Any]:
    name, mkey = job
    zs = split_point(name, mkey)
    y = y_of(zs)
    ly = l_of(y)
    nul = 32 - rank(ly)
    kb = kernel(ly)
    stab = stabilizer(y)
    res: dict[str, Any] = {"piece": name, "move": mkey, "split_point": [fmt(x) for x in zs], "nullity": nul}
    res["H_orbit_complex_dim"] = vr.orbit_dim(zs)
    res["compact_orbit_dim_unit_section"] = 15 - len(stab)
    res["stabilizer_dim"] = len(stab)
    res["invariants"] = invariants(name, y)
    # J and every stabilizer lift preserve the kernel (restrict raises otherwise)
    restrict(J32, kb)
    dstab = derived(stab) if stab else []
    cent = center(stab) if stab else []
    res["derived_dim"] = len(dstab)
    res["center_dim"] = len(cent)
    if dstab:
        res["derived_killing_negative_definite"] = negative_definite(killing(dstab))
    if len(stab) == 8:
        res["stabilizer_type"] = "su(3)" if (len(dstab) == 8 and res["derived_killing_negative_definite"]) else "?"
        rep = [restrict(kernel_lift(x), kb) for x in stab]
        om = casimir(stab, rep)
        res["su3_casimir_eigenspaces"] = eigenspace_dims(om, [Fraction(4, 9), Fraction(10, 9), Fraction(1)])
        mj = restrict(J32 if not MUTATION["flip_j"] else [[-x for x in r] for r in J32], kb)
        i0 = commutant_center_structure(rep)
        xs = [
            [sum((Fraction((i + 1) ** e) * stab[i][k] for i in range(8)), Fraction(0)) for k in range(15)]
            for e in (0, 1, 2)
        ]
        cubic, control = [], []
        for x in xs:
            m = restrict(kernel_lift(x), kb)
            m3 = matmul(m, matmul(m, m))
            cubic.append(str(sum(matmul(mj, m3)[i][i] for i in range(len(kb)))))
            control.append(str(sum(matmul(i0, m3)[i][i] for i in range(len(kb)))))
        res["cubic_trace_tr(J rho(X)^3)"] = cubic
        res["cubic_trace_control_tr(I0 rho(X)^3)"] = control
        res["kernel_is_3_plus_conj3"] = (
            res["su3_casimir_eigenspaces"]["4/9"] == len(kb)
            and all(c == "0" for c in cubic)
            and all(c != "0" for c in control)
            and len(kb) == 12
        )
    elif len(dstab) == 3 and res.get("derived_killing_negative_definite"):
        rep = [restrict(kernel_lift(x), kb) for x in dstab]
        res["su2_on_kernel"] = su2_multiplicities(dstab, rep, 2)
        res["stabilizer_type"] = "u(2)" if len(stab) == 4 and len(cent) == 1 else ("su(2)" if len(stab) == 3 else "?")
        if len(cent) == 1:
            zgen, yw = primitive_central(cent[0])
            res["central_generator"] = [str(x) for x in zgen]
            res["central_weights_on_y"] = [str(w) for w in yw]
            res["joint_kernel_decomposition"] = joint_decomposition(dstab, zgen, kb)
        if name in ("N+", "N-"):
            rep7 = [x[:14] for x in dstab]
            seven_rep = [lin(c, D7) for c in rep7]
            if MUTATION["wrong_seven_restriction"]:
                seven_rep = [[[Fraction(0)] * 7 for _ in range(7)] for _ in rep7]
            res["su2_on_7"] = su2_multiplicities(dstab, seven_rep, 1)
            ads = []
            for x in dstab:
                cols = [bracket(x, [*unit(14, b), Fraction(0)])[:14] for b in range(14)]
                ads.append(transpose(cols))
            res["su2_on_14"] = su2_multiplicities(dstab, ads, 1)
    elif len(stab) == 1:
        res["stabilizer_type"] = "u(1)"
        zgen, yw = primitive_central(stab[0])
        res["central_generator"] = [str(x) for x in zgen]
        res["central_weights_on_y"] = [str(w) for w in yw]
        res["kernel_weights"] = [str(w) for w in kernel_weights(zgen, kb)]
    if name != "N+" and name != "N-" and mkey != "rep":
        res["level_set"] = level_set_rank(name, y, zs)
    return res


# ---------------------------------------------------------------------------------------------------------------------
# G_2 transitivity inputs, orbit-joining involution, B9 plane stabilizers


def g2_orbit_dim(vecs: Sequence[Sequence[Fraction]]) -> int:
    """Rank of D -> (D a_1, ..., D a_r) on compact g_2 for real 7-vectors a_i."""
    rows = [[x for a in vecs for x in matvec(d, list(a))] for d in D7]
    return rank(rows)


def subalgebra_dim(gens: Sequence[Vec]) -> int:
    """Real dimension of the octonion subalgebra (with 1) generated by imaginary 7-vectors."""
    basis: list[Vec] = [unit(8, 0)]
    cur = [[Fraction(0), *g] for g in gens]
    for v in cur:
        if rank([*basis, v]) > len(basis):
            basis.append(v)
    changed = True
    while changed:
        changed = False
        for a in list(basis):
            for b in list(basis):
                prod = list(cd_multiply_exact(8, a, b))
                if rank([*basis, prod]) > len(basis):
                    basis.append(prod)
                    changed = True
    return len(basis)


def plane_stabilizer(u: Sequence[vr.Gq], v: Sequence[vr.Gq]) -> dict[str, int]:
    """Compact g_2 elements D with D u, D v in span_C(u, v): unknowns c (14 real) and alpha..delta (8 real)."""
    rows: list[list[Fraction]] = []
    du = [[vr.Gq(0)] * 7 for _ in range(14)]
    dv = [[vr.Gq(0)] * 7 for _ in range(14)]
    for a in range(14):
        for i in range(7):
            du[a][i] = sum((D7[a][i][j] * u[j] for j in range(7)), vr.Gq(0))
            dv[a][i] = sum((D7[a][i][j] * v[j] for j in range(7)), vr.Gq(0))
    # D u = alpha u + beta v, D v = gamma u + delta v; alpha = ar + i ai etc.
    for target, dmat in ((0, du), (1, dv)):
        for i in range(7):
            for part in ("re", "im"):
                row = [getattr(dmat[a][i], part) for a in range(14)]
                coef = [Fraction(0)] * 8
                for slot, vec in ((0, u), (1, v)):
                    base = 4 * target + 2 * slot
                    x = vec[i]
                    if part == "re":
                        coef[base], coef[base + 1] = -x.re, x.im
                    else:
                        coef[base], coef[base + 1] = -x.im, -x.re
                rows.append(row + coef)
    sols = kernel(rows)
    image = rank([s[14:] for s in sols]) if sols else 0
    return {"stabilizer_dim": len(sols), "image_in_gl_P_dim": image, "orbit_dim_of_plane": 14 - len(sols)}


def _orbit_tool_row(job: tuple[str, str]) -> dict[str, Any]:
    """Plane stabilizer and generated subalgebra at a B9 point; null-vector orbit and subalgebra at a VB point."""
    piece, mkey = job
    u, _mu, v = z_parts(y_of(split_point(piece, mkey)))
    row: dict[str, Any] = {"piece": piece, "move": mkey}
    if piece == "B9":
        row.update(plane_stabilizer(u, v))
        gens = [[x.re for x in u], [x.im for x in u], [x.re for x in v], [x.im for x in v]]
        row["generated_subalgebra_dim"] = subalgebra_dim(gens)
    else:
        w = u if any(u) else v
        row["null_vector_g2_orbit_dim"] = g2_orbit_dim([[x.re for x in w], [x.im for x in w]])
        row["generated_subalgebra_dim"] = subalgebra_dim([[x.re for x in w], [x.im for x in w]])
    return row


def check_orbit_tools(points: Sequence[dict[str, Any]]) -> dict[str, Any]:
    e = [unit(7, k) for k in range(7)]
    pair = g2_orbit_dim([e[0], e[1]])
    single = g2_orbit_dim([e[0]])
    # involution: +1 on e_0, e_3, e_4, e_7 (a subgroup of (Z/2)^3 under XOR), -1 elsewhere
    plus = {0, 3, 4, 7}
    closed = all((p ^ q) in plus for p in plus for q in plus)
    eps = [1 if k in plus else -1 for k in range(8)]
    auto = all(eps[p ^ q] == eps[p] * eps[q] for p in range(8) for q in range(8))
    fixes = eps[1] == -1 and eps[2] == -1
    jobs = [(pt["piece"], pt["move"]) for pt in points if pt["piece"] in ("B9", "VB") and pt["move"] != "rep"]
    b9 = parallel.ordered_map(_orbit_tool_row, jobs)
    ok = pair == 11 and single == 6 and closed and auto and fixes
    ok = ok and all(
        r.get("stabilizer_dim", 4) == 4
        and r.get("image_in_gl_P_dim", 4) == 4
        and r.get("orbit_dim_of_plane", 10) == 10
        and r["generated_subalgebra_dim"] == (8 if r["piece"] == "B9" else 4)
        and r.get("null_vector_g2_orbit_dim", 11) == 11
        for r in b9
    )
    return {
        "g2_orbit_dim_orthonormal_pair": pair,
        "g2_orbit_dim_unit_vector": single,
        "involution_fix_{0,3,4,7}_is_automorphism": closed and auto,
        "involution_negates_e1_e2": fixes,
        "plane_and_null_vector_checks": b9,
        "pass": ok,
    }


# ---------------------------------------------------------------------------------------------------------------------
# Representation ring quotient for K^0(G_2 / SU(2))


def ring_quotient(seven: dict[int, int], adjoint: dict[int, int]) -> dict[str, Any]:
    """Z[V_1]/(rho_7 - 7, rho_14 - 14) with rho restricted through V_n characters; Smith form up to degree 8.

    V_n is expressed in V_1 by the Chebyshev recursion V_(n+1) = V_1 V_n - V_(n-1). Polynomials are integer
    coefficient lists in x = V_1 - 2.
    """

    def padd(p: list[int], q: list[int]) -> list[int]:
        n = max(len(p), len(q))
        return [(p[i] if i < len(p) else 0) + (q[i] if i < len(q) else 0) for i in range(n)]

    def pmul(p: list[int], q: list[int]) -> list[int]:
        out = [0] * (len(p) + len(q) - 1)
        for i, a in enumerate(p):
            for j, b in enumerate(q):
                out[i + j] += a * b
        return out

    v1 = [2, 1]  # V_1 = x + 2
    vs = [[1], v1]
    for _n in range(2, 6):
        vs.append(padd(pmul(v1, vs[-1]), [-c for c in vs[-2]]))

    def restrict_char(mult: dict[int, int], dim: int) -> list[int]:
        acc = [-dim]
        for nn, m in mult.items():
            acc = padd(acc, [m * c for c in vs[nn]])
        while len(acc) > 1 and acc[-1] == 0:
            acc.pop()
        return acc

    f7 = restrict_char(seven, 7)
    f14 = restrict_char(adjoint, 14)
    top = 8
    gens = []
    for k in range(top):
        for f in (f7, f14):
            g = [0] * k + f
            if len(g) <= top + 1 and any(g):
                gens.append(g + [0] * (top + 1 - len(g)))
    mat = flint.fmpz_mat(len(gens), top + 1, [x for r in gens for x in r])
    snf = mat.snf()
    diag = [int(snf[i, i]) for i in range(min(snf.nrows(), snf.ncols()))]
    nonzero = [d for d in diag if d]
    torsion = [abs(d) for d in nonzero if abs(d) != 1]
    free_rank = top + 1 - len(nonzero)
    x2 = padd(f14, [-4 * c for c in f7]) if f7 == [0, 2] else None
    return {
        "rho7_minus_7_in_x": f7,
        "rho14_minus_14_in_x": f14,
        "x_squared_equals_(rho14-14)-4(rho7-7)": x2 == [0, 0, 1],
        "smith_free_rank_degree_le_8": free_rank,
        "smith_torsion": torsion,
        "tor_2_zero": any(f7) and any(f14),  # Z[x] is a domain: c f = 0 with f != 0 forces c = 0
        "reduced_quotient": "Z/2" if free_rank == 1 and torsion == [2] else f"free {free_rank - 1}, torsion {torsion}",
    }


# ---------------------------------------------------------------------------------------------------------------------
# Verdict assembly

JOBS = [(name, mkey) for name in PIECES for mkey in ("rep", "m1", "m2", "m3", "m4", "m5")] + list(EXTRA)
EXPECTED_DIM = {"B9": 14, "V": 12, "VB": 11, "Va+": 12, "Va-": 12, "N+": 11, "N-": 11}


def run_all() -> dict[str, Any]:
    t0 = time.time()
    result: dict[str, Any] = {}
    result["algebra"] = check_algebra()
    points = parallel.ordered_map(analyze_point, JOBS, min_items=1)
    result["points"] = points
    result["orbit_tools"] = check_orbit_tools(points)
    by = {(p["piece"], p["move"]): p for p in points}
    moved = [p for p in points if p["move"].startswith("m")]

    # Statement 3: generic orbit dimensions at moved points
    s3_rows = {p["piece"] + "/" + p["move"]: p["compact_orbit_dim_unit_section"] for p in moved}
    s3 = all(p["compact_orbit_dim_unit_section"] == EXPECTED_DIM[p["piece"]] for p in moved)
    result["statement_3"] = {
        "moved_point_orbit_dims": s3_rows,
        "rep_orbit_dims": {p["piece"]: p["compact_orbit_dim_unit_section"] for p in points if p["move"] == "rep"},
        "nullities_ok": all(p["nullity"] == PIECES[p["piece"]][1] for p in points),
        "verdict": "confirmed" if s3 else "refuted",
    }

    # Statement 1: N_+-
    n_rows = [p for p in moved if p["piece"] in ("N+", "N-")]
    seven = {0: 3, 1: 2}
    adj = {0: 3, 1: 4, 2: 1}
    s1_ok = all(
        p["stabilizer_type"] == "u(2)"
        and p["su2_on_kernel"] == {"V_0": 2, "V_1": 3}
        and p["su2_on_7"] == {"V_0": 3, "V_1": 2}
        and p["su2_on_14"] == {"V_0": 3, "V_1": 4, "V_2": 1}
        for p in n_rows
    )
    measured7 = [measured_multiplicities(p["su2_on_7"]) for p in n_rows]
    measured14 = [measured_multiplicities(p["su2_on_14"]) for p in n_rows]
    if any(m != measured7[0] for m in measured7) or any(m != measured14[0] for m in measured14):
        raise RuntimeError("the restriction of 7 or 14 differs between N points")
    ring = ring_quotient(measured7[0], measured14[0])
    ring_ok = ring["reduced_quotient"] == "Z/2" and ring["rho7_minus_7_in_x"] == [0, 2]
    ring_ok = ring_ok and ring["rho14_minus_14_in_x"] == [0, 8, 1]
    result["statement_1"] = {
        "points": {
            p["piece"] + "/" + p["move"]: {
                k: p.get(k)
                for k in ("stabilizer_type", "su2_on_kernel", "su2_on_7", "su2_on_14", "joint_kernel_decomposition")
            }
            for p in n_rows
        },
        "expected_su2_on_7": seven,
        "expected_su2_on_14": adj,
        "ring": ring,
        "verdict": "confirmed" if s1_ok and ring_ok else "refuted",
    }

    # Statement 2
    def principal(p: dict[str, Any]) -> bool:
        return p["stabilizer_type"] == "su(2)" and p["su2_on_kernel"] == {"V_0": 2, "V_1": 2}

    va_v = [p for p in moved if p["piece"] in ("Va+", "Va-", "V")]
    va_rep = [by[(n, "rep")] for n in ("Va+", "Va-", "V")] + [by[k] for k in EXTRA]
    b9 = [p for p in moved if p["piece"] == "B9"]
    vb = [p for p in moved if p["piece"] == "VB"]
    s2_principal = all(principal(p) for p in va_v)
    s2_su3 = all(
        p["stabilizer_dim"] == 8
        and p["derived_dim"] == 8
        and p["derived_killing_negative_definite"]
        and p["su3_casimir_eigenspaces"]["4/9"] == 12
        and all(c == "0" for c in p["cubic_trace_tr(J rho(X)^3)"])
        and all(c != "0" for c in p["cubic_trace_control_tr(I0 rho(X)^3)"])
        and p["invariants"]["rho_squared"] == "1"
        for p in va_rep
    )
    b9_shapes = []
    for p in b9:
        w = [Fraction(x) for x in p.get("kernel_weights", [])]
        cnt = Counter(w)
        vals = sorted(cnt)
        b9_shapes.append(len(vals) == 2 and vals[1] - vals[0] == 1 and all(c == 3 for c in cnt.values()))
    claim_vb = {"V_(0,-4)": 1, "V_(1,-3)": 2, "V_(0,-2)": 1}
    claim_n = {**claim_vb, "V_(1,-1)": 1}
    vb_conv = {p["move"]: convert_joint(p) for p in vb}
    n_conv = {p["piece"] + "/" + p["move"]: convert_joint(p) for p in n_rows}
    b9_conv = {
        p["move"]: sorted(str(-(Fraction(w) + Fraction(p["central_generator"][14]))) for w in p["kernel_weights"])
        for p in b9
    }
    claim_b9 = sorted(["-1", "-1", "-1", "-2", "-2", "-2"])
    vb_ok = all(p.get("stabilizer_type") == "u(2)" for p in vb) and all(d == claim_vb for d in vb_conv.values())
    n_ok = all(d == claim_n for d in n_conv.values())
    b9_ok = all(p.get("stabilizer_type") == "u(1)" for p in b9) and all(w == claim_b9 for w in b9_conv.values())
    result["statement_2"] = {
        "principal_su2_2V0+2V1": {p["piece"] + "/" + p["move"]: p.get("su2_on_kernel") for p in va_v},
        "principal_ok": s2_principal,
        "collinear_su3_3+conj3_ok": s2_su3,
        "convention_note": (
            "weights here use the lift Y_Phi and Z = w J with positive phase coefficient t; the claimed weights equal "
            "-(w + t), the lift Y_Phi + J with the opposite sign, applied uniformly to B9, VB and N_+-"
        ),
        "B9_u1_kernel_weights_native": {p["move"]: p.get("kernel_weights") for p in b9},
        "B9_phase_coefficient_t": {p["move"]: p["central_generator"][14] for p in b9},
        "B9_weights_claim_convention": b9_conv,
        "B9_two_weights_differing_by_1_each_mult_3": all(b9_shapes),
        "B9_ok": b9_ok,
        "VB_joint_native": {p["move"]: p.get("joint_kernel_decomposition") for p in vb},
        "VB_phase_coefficient_t": {p["move"]: p.get("central_generator", [None] * 15)[14] for p in vb},
        "VB_joint_claim_convention": vb_conv,
        "VB_ok": vb_ok,
        "N_joint_claim_convention": n_conv,
        "N_equals_VB_plus_V_(1,-1)": n_ok and vb_ok,
        "verdict": "confirmed" if (s2_principal and s2_su3 and b9_ok and vb_ok and n_ok) else "refuted",
    }

    # Statement 4: level-set dimension against orbit dimension, plus the orbit-joining inputs
    lvl = {}
    s4_dims = True
    for p in moved:
        if "level_set" in p:
            ls = p["level_set"]
            level_dim = ls["unit_section_dim"] - ls["invariant_rank"]
            lvl[p["piece"] + "/" + p["move"]] = {
                **ls,
                "level_set_dim": level_dim,
                "orbit_dim": p["compact_orbit_dim_unit_section"],
            }
            s4_dims = s4_dims and level_dim == p["compact_orbit_dim_unit_section"]
    moduli = {
        piece: sorted(
            {
                json.dumps(p["invariants"].get("rho_squared"))
                + json.dumps(p["invariants"].get("lambda"))
                + json.dumps(p["invariants"].get("gram_normalized"))
                for p in moved
                if p["piece"] == piece
            }
        )
        for piece in ("B9", "V", "VB", "Va+", "Va-")
    }
    forms = all(
        (p["invariants"].get("form_(u,0,+-iu)", True))
        and p["invariants"].get("collinear_v=lambda_u", True)
        and p["invariants"].get("mu^2+(1+lambda^2)u.u=0", True)
        and p["invariants"].get("null", True)
        and p["invariants"].get("cross_zero", True)
        and p["invariants"].get("mu_zero", True)
        for p in points
    )
    gram_ranks = all(
        p["invariants"]["gram_rank"] == (2 if p["piece"] == "B9" else 1) for p in points if p["piece"] in ("B9", "VB")
    )
    tools = result["orbit_tools"]
    result["statement_4"] = {
        "level_sets": lvl,
        "level_set_dim_equals_orbit_dim": s4_dims,
        "distinct_moduli_values": {k: len(v) for k, v in moduli.items()},
        "parametrizations_hold_at_every_point": forms,
        "gram_ranks_B9_2_VB_1": gram_ranks,
        "orbit_tools_pass": tools["pass"],
        "verdict": "confirmed"
        if (s4_dims and forms and gram_ranks and tools["pass"] and all(len(v) >= 2 for v in moduli.values()))
        else "refuted",
    }
    # Statement 5 ingredients (the homotopy models themselves are arguments recorded in verification.md)
    va_pts = [p for p in points if p["piece"] in ("Va+", "Va-")]
    n_pts = [p for p in points if p["piece"] in ("N+", "N-")]
    pencil = vb_pencil_nullities()
    result["statement_5_inputs"] = {
        "Va_points_have_u.u_nonzero": all(Fraction(p["invariants"]["rho_squared"]) > 0 for p in va_pts),
        "N_points_have_u.u_zero_same_form": all(
            p["invariants"]["rho_squared"] == "0" and p["invariants"]["form_(u,0,+-iu)"] for p in n_pts
        ),
        "V_points_mu_nonzero_collinear_relation": all(
            p["invariants"]["mu_nonzero"]
            and p["invariants"]["collinear_v=lambda_u"]
            and p["invariants"]["mu^2+(1+lambda^2)u.u=0"]
            for p in points
            if p["piece"] == "V"
        ),
        "VB_pencil_(n,0,lambda n)_nullity": pencil,
        "B9_generated_subalgebra_dims": [
            r["generated_subalgebra_dim"] for r in tools["plane_and_null_vector_checks"] if r["piece"] == "B9"
        ],
        "B9_phase_coefficient_t": [p["central_generator"][14] for p in b9],
        "VB_phase_coefficient_t": [p.get("central_generator", [None] * 15)[14] for p in vb],
        "N_phase_coefficient_t": [p.get("central_generator", [None] * 15)[14] for p in n_rows],
    }
    s5 = result["statement_5_inputs"]
    s5_ok = (
        s5["Va_points_have_u.u_nonzero"]
        and s5["N_points_have_u.u_zero_same_form"]
        and s5["V_points_mu_nonzero_collinear_relation"]
        and pencil == {"0+1i": 16, "0+-1i": 16, "2+0i": 12, "1+1i": 12, "0+0i": 12}
        and all(d == 8 for d in s5["B9_generated_subalgebra_dims"])
        and all(t == "1" for t in s5["B9_phase_coefficient_t"])
    )
    result["statement_5"] = {
        "verdict": "confirmed (argument; inputs checked)" if s5_ok else "refuted (an input check failed)",
        "note": "the homotopy steps are written arguments in verification.md, not machine-checked",
    }
    return {"result": result, "seconds": round(time.time() - t0, 1)}


def _pencil_nullity(item: tuple[vr.Gq, list[vr.Gq]]) -> int:
    lam, n = item
    z = [*n, vr.Gq(0), *[lam * a for a in n]]
    y = [Fraction(0)] * 32
    for k in range(15):
        y[k + 1] = z[k].re
        y[16 + k + 1] = z[k].im
    return 32 - rank(l_of(y))


def vb_pencil_nullities() -> dict[str, int]:
    """Nullity of L_y at (n, 0, lambda n) for the null vector n of a moved N_+ point and several lambda."""
    n, _mu, _v = z_parts(y_of(split_point("N+", "m1")))
    lams = [vr.Gq(0, 1), vr.Gq(0, -1), vr.Gq(2), vr.Gq(1, 1), vr.Gq(0)]
    nul = parallel.ordered_map(_pencil_nullity, [(lam, n) for lam in lams])
    return {f"{lam.re}+{lam.im}i": k for lam, k in zip(lams, nul, strict=True)}


def measured_multiplicities(dec: dict[str, int]) -> dict[int, int]:
    return {int(key[2:]): mult for key, mult in dec.items()}


def convert_joint(p: dict[str, Any]) -> dict[str, int]:
    """Re-express V_(n, w) in the claimed convention w -> -(w + t), t the phase coefficient of the generator."""
    t = Fraction(p["central_generator"][14])
    out: dict[str, int] = {}
    for key, mult in p.get("joint_kernel_decomposition", {}).items():
        nn, w = key[3:-1].split(",")
        out[f"V_({nn},{-(Fraction(w) + t)})"] = mult
    return out


# ---------------------------------------------------------------------------------------------------------------------
# Self-test


def control(name: str) -> str | None:
    """Run the mutated property; return a description when it fails as required, None if the mutation is not caught."""
    global YPHI
    baseline = analyze_point(("B9", "m1"))["kernel_weights"] if name == "flip_j" else []
    for k in MUTATION:
        MUTATION[k] = k == name
    try:
        if name == "drop_leibniz_term":
            dim = len(compact_derivations())
            return f"derivation space dimension {dim}" if dim != 14 else None
        if name == "zero_phase_lift":
            YPHI = phase_lift()
            alg = check_algebra()
            return f"phase identity failures {alg['phase_lift_identity_failures']}" if not alg["pass"] else None
        if name == "no_phase_direction":
            p = analyze_point(("N+", "m1"))
            return f"N+ stabilizer {p['stabilizer_dim']}" if p.get("stabilizer_type") != "u(2)" else None
        if name == "unmoved_points":
            p = analyze_point(("Va+", "m1"))
            dim = p["compact_orbit_dim_unit_section"]
            return f"Va+ orbit dim {dim}" if dim != 12 else None
        if name == "flip_j":
            p = analyze_point(("B9", "m1"))
            return f"B9 weights {p['kernel_weights']} vs {baseline}" if p["kernel_weights"] != baseline else None
        if name == "wrong_seven_restriction":
            p = analyze_point(("N+", "m1"))
            ring = ring_quotient(measured_multiplicities(p["su2_on_7"]), measured_multiplicities(p["su2_on_14"]))
            reduced = ring["reduced_quotient"]
            return f"measured 7 -> {p['su2_on_7']}, ring {reduced}" if reduced != "Z/2" else None
        raise ValueError(name)
    finally:
        for k in MUTATION:
            MUTATION[k] = False
        YPHI = phase_lift()


def self_test() -> int:
    names = list(MUTATION)
    report = dict(zip(names, parallel.ordered_map(control, names), strict=True))
    print(json.dumps({"controls": report}, indent=1))
    failures = [name for name, msg in report.items() if msg is None]
    if failures:
        print(f"uncaught mutations: {failures}")
        return 1
    print("self-test: every mutation caught")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("--out")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    if not args.out:
        ap.error("--out is required without --self-test")
    start = time.time()
    run = run_all()
    out = {
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "versions": {"python": platform.python_version(), "python_flint": flint.__version__},
        "workers": parallel.workers(),
        **run["result"],
        "total_s": round(time.time() - start, 1),
    }
    Path(args.out).write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print(f"total_s={out['total_s']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
