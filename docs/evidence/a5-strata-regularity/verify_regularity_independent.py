"""Independent verification of the A_5 strata-regularity record (docs/evidence/a5-strata-regularity/README.md).

Every table comes from gororoba_quantum/cd_core.py: the sedenion and A_5 sign tables are read from
left_mult_matrix_exact and re-checked against cd_multiply_exact. The split table, the invariant form eta, the cross
product, the 14 derivations, the piece polynomials, C_z and the nullity of L_y are built here. The script imports
nothing from strata_regularity.py, rederive_strata_equations.py or scripts/a5_zero_divisor_strata.py.

Coordinates. z_k = y_k + i y_(16+k), k = 1..15; split coordinates z'_k = i^(-popcount k) z_k; u' = z'_1..z'_7,
mu' = z'_8, v' = z'_9..z'_15; s = u' + v', d = u' - v'. In Singular and flint the variable x(k-1) is z'_k.

Methods, chosen to differ from the record's script:
- symmetry: one boost element of infinite order (c, s) = (5/4, 3/4) substituted into every closure ideal, the
  reflection mu' -> -mu', and the 14 derivations applied to every generator, each reduced modulo a standard basis;
- orbits: rank of the 16 H-tangent vectors at the representatives, at their images under unipotent G_2 elements,
  the boost and scaling, and at every R_8 point of Gaussian-integer and integer boxes on the six slices and of the
  complete F_13 slice enumeration;
- smoothness: exact Jacobian rank of the closure generators against the codimension;
- germs: the transverse slice through the representative is the Euclidean orthogonal complement of the orbit
  tangent space; the germ ideal is the intersection of the minimal primes through the point; the tangent cone comes
  from the deformation to the normal cone, (P(h t) : h^infinity) at h = 0, with global orderings only, and its degree
  is the multiplicity;
- the link at x0 = e_1 + e_18: the germs of V and B9 in a Hermitian-orthogonal slice at x0 itself over Q(i).

No random value enters; every point is listed in the source.

Usage:
    GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 "$PYTHON" -B -W error \
        docs/evidence/a5-strata-regularity/verify_regularity_independent.py \
        --out docs/evidence/a5-strata-regularity/verification.json
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import platform
import subprocess
import sys
import tempfile
import time
from collections import Counter
from collections.abc import Callable, Sequence
from fractions import Fraction
from pathlib import Path
from typing import Any

import flint

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import parallel  # noqa: E402
from cd_core import cd_multiply_exact, left_mult_matrix_exact  # noqa: E402

SINGULAR = "Singular"
F_P = 13
F_I = 5  # 5^2 = 25 = -1 mod 13

# ---------------------------------------------------------------------------------------------------------------------
# Tables from cd_core


def _basis(dim: int, k: int) -> list[int]:
    return [1 if j == k else 0 for j in range(dim)]


def sign_table(dim: int) -> list[list[int]]:
    """sign[p][q] with e_p e_q = sign e_(p XOR q), read from column q of left_mult_matrix_exact(dim, e_p)."""
    table = []
    for p in range(dim):
        mat = left_mult_matrix_exact(dim, _basis(dim, p))
        table.append([int(mat[p ^ q][q]) for q in range(dim)])
    return table


SIGN16 = sign_table(16)
SIGN32 = sign_table(32)


def popcount(k: int) -> int:
    return bin(k).count("1")


SPLIT16 = [[(-1) ** popcount(p & q) * SIGN16[p][q] for q in range(16)] for p in range(16)]
ETA = [-SPLIT16[j][j] for j in range(8)]  # e'_j e'_j = -eta_j e'_0, j = 1..7


def table_row_failures(job: tuple[int, int]) -> int:
    """Basis products e_p e_q, q < dim, where cd_multiply_exact differs from the sign table."""
    dim, p = job
    table = SIGN16 if dim == 16 else SIGN32
    bad = 0
    for q in range(dim):
        prod = cd_multiply_exact(dim, _basis(dim, p), _basis(dim, q))
        expect = [0] * dim
        expect[p ^ q] = table[p][q]
        if [int(x) for x in prod] != expect:
            bad += 1
    return bad


def check_tables() -> dict[str, Any]:
    jobs = [(dim, p) for dim in (16, 32) for p in range(dim)]
    bad = sum(parallel.ordered_map(table_row_failures, jobs, min_items=1))
    if bad:
        raise RuntimeError(f"sign tables disagree with cd_multiply_exact on {bad} pairs")
    oct_ok = all(SIGN16[p][q] == sign_table(8)[p][q] for p in range(8) for q in range(8))
    if not oct_ok:
        raise RuntimeError("octonion block of the sedenion table differs from the octonion table")
    return {"pairs_checked": 16 * 16 + 32 * 32, "eta_1_7": ETA[1:8], "octonion_block_consistent": oct_ok}


# ---------------------------------------------------------------------------------------------------------------------
# Exact linear algebra


def q_rank(rows: Sequence[Sequence[Any]]) -> int:
    if not rows or not rows[0]:
        return 0
    return int(
        flint.fmpq_mat([[flint.fmpq(Fraction(x).numerator, Fraction(x).denominator) for x in r] for r in rows]).rank()
    )


def z_rank(rows: Sequence[Sequence[int]]) -> int:
    if not rows or not rows[0]:
        return 0
    return int(flint.fmpz_mat([list(r) for r in rows]).rank())


def q_nullspace(rows: Sequence[Sequence[Any]], ncols: int) -> list[list[Fraction]]:
    """Basis of {w : rows . w = 0} over Q from the reduced row echelon form."""
    if not rows:
        return [[Fraction(int(i == j)) for j in range(ncols)] for i in range(ncols)]
    mat = flint.fmpq_mat([[flint.fmpq(Fraction(x).numerator, Fraction(x).denominator) for x in r] for r in rows])
    rref, rank = mat.rref()
    pivots = []
    for i in range(rank):
        for j in range(ncols):
            if rref[i, j] != 0:
                pivots.append(j)
                break
    free = [j for j in range(ncols) if j not in pivots]
    basis = []
    for f in free:
        w = [Fraction(0)] * ncols
        w[f] = Fraction(1)
        for i, pc in enumerate(pivots):
            val = rref[i, f]
            w[pc] = -Fraction(int(val.p), int(val.q))
        basis.append(w)
    return basis


def integerize(vec: Sequence[Fraction]) -> list[int]:
    den = 1
    for x in vec:
        den = den * x.denominator // _gcd(den, x.denominator)
    ints = [int(x * den) for x in vec]
    g = 0
    for n in ints:
        g = _gcd(g, abs(n))
    return [n // g for n in ints] if g else ints


def _gcd(a: int, b: int) -> int:
    while b:
        a, b = b, a % b
    return abs(a)


class Gq:
    """Exact Gaussian rational."""

    __slots__ = ("im", "re")

    def __init__(self, re: Any = 0, im: Any = 0) -> None:
        self.re = Fraction(re)
        self.im = Fraction(im)

    @staticmethod
    def of(x: Any) -> Gq:
        return x if isinstance(x, Gq) else Gq(x)

    def __add__(self, o: Any) -> Gq:
        o = Gq.of(o)
        return Gq(self.re + o.re, self.im + o.im)

    __radd__ = __add__

    def __sub__(self, o: Any) -> Gq:
        o = Gq.of(o)
        return Gq(self.re - o.re, self.im - o.im)

    def __rsub__(self, o: Any) -> Gq:
        return Gq.of(o) - self

    def __mul__(self, o: Any) -> Gq:
        o = Gq.of(o)
        return Gq(self.re * o.re - self.im * o.im, self.re * o.im + self.im * o.re)

    __rmul__ = __mul__

    def __neg__(self) -> Gq:
        return Gq(-self.re, -self.im)

    def __truediv__(self, o: Any) -> Gq:
        o = Gq.of(o)
        d = o.re * o.re + o.im * o.im
        return self * Gq(o.re / d, -o.im / d)

    def conj(self) -> Gq:
        return Gq(self.re, -self.im)

    def __eq__(self, o: object) -> bool:
        if isinstance(o, (int, Fraction)):
            o = Gq(o)
        return isinstance(o, Gq) and self.re == o.re and self.im == o.im

    def __hash__(self) -> int:
        return hash((self.re, self.im))

    def __bool__(self) -> bool:
        return bool(self.re) or bool(self.im)

    def singular(self) -> str:
        return f"({self.re}+({self.im})*I)"


I_UNIT = Gq(0, 1)


def i_pow(k: int) -> Gq:
    return [Gq(1), Gq(0, 1), Gq(-1), Gq(0, -1)][k % 4]


def realify(rows: Sequence[Sequence[Any]]) -> list[list[Fraction]]:
    """[[A, -B], [B, A]] for the complex matrix A + i B; its rank is twice the complex rank."""
    g = [[Gq.of(x) for x in r] for r in rows]
    top = [[x.re for x in r] + [-x.im for x in r] for r in g]
    bot = [[x.im for x in r] + [x.re for x in r] for r in g]
    return top + bot


def c_rank(rows: Sequence[Sequence[Any]]) -> int:
    if not rows:
        return 0
    rank = q_rank(realify(rows))
    if rank % 2:
        raise RuntimeError("odd realified rank")
    return rank // 2


def c_nullspace_hermitian(rows: Sequence[Sequence[Gq]], ncols: int) -> list[list[Gq]]:
    """Basis over Q(i) of {w : sum conj(r_k) w_k = 0 for every row r}, by Gaussian elimination over Q(i)."""
    mat = [[x.conj() for x in r] for r in rows]
    pivots: list[int] = []
    rank = 0
    for col in range(ncols):
        piv = next((i for i in range(rank, len(mat)) if mat[i][col]), None)
        if piv is None:
            continue
        mat[rank], mat[piv] = mat[piv], mat[rank]
        inv = Gq(1) / mat[rank][col]
        mat[rank] = [x * inv for x in mat[rank]]
        for i in range(len(mat)):
            if i != rank and mat[i][col]:
                fac = mat[i][col]
                mat[i] = [a - fac * b for a, b in zip(mat[i], mat[rank], strict=True)]
        pivots.append(col)
        rank += 1
    basis = []
    for f in (j for j in range(ncols) if j not in pivots):
        w = [Gq(0)] * ncols
        w[f] = Gq(1)
        for i, pc in enumerate(pivots):
            w[pc] = -mat[i][f]
        basis.append(w)
    return basis


# ---------------------------------------------------------------------------------------------------------------------
# Split octonion module: eta, cross product, derivations


def eta2(x: Sequence[Any], y: Sequence[Any]) -> Any:
    total: Any = 0
    for j in range(7):
        total = total + ETA[j + 1] * x[j] * y[j]
    return total


def cross(x: Sequence[Any], y: Sequence[Any]) -> list[Any]:
    """Im(x y) for x, y in the span of e'_1..e'_7 of the split octonions."""
    out: list[Any] = [0] * 7
    for p in range(1, 8):
        for q in range(1, 8):
            k = p ^ q
            if k:
                out[k - 1] = out[k - 1] + SPLIT16[p][q] * x[p - 1] * y[q - 1]
    return out


def derivations() -> list[list[list[Fraction]]]:
    """Basis of the derivations of the split octonions, as 8 x 8 matrices D[i][j] = coefficient of e'_i in D e'_j."""
    rows = []
    for p in range(8):
        for q in range(8):
            for k in range(8):
                r = [0] * 64
                r[k * 8 + (p ^ q)] += SPLIT16[p][q]
                r[(k ^ q) * 8 + p] -= SPLIT16[k ^ q][q]
                r[(p ^ k) * 8 + q] -= SPLIT16[p][p ^ k]
                rows.append(r)
    basis = q_nullspace(rows, 64)
    return [[[v[i * 8 + j] for j in range(8)] for i in range(8)] for v in basis]


DERS8 = derivations()
DERS = [[[d[i][j] for j in range(1, 8)] for i in range(1, 8)] for d in DERS8]  # 7 x 7 blocks


def lift_failures(d: Sequence[Sequence[Fraction]]) -> int:
    """Triples (p, q, k) where the lift D + D of a split octonion derivation breaks the Leibniz rule on SPLIT16."""
    d16 = [[Fraction(0)] * 16 for _ in range(16)]
    for i in range(8):
        for j in range(8):
            d16[i][j] = d[i][j]
            d16[8 + i][8 + j] = d[i][j]
    bad = 0
    for p in range(16):
        for q in range(16):
            for k in range(16):
                lhs = SPLIT16[p][q] * d16[k][p ^ q]
                rhs = d16[k ^ q][p] * SPLIT16[k ^ q][q] + d16[p ^ k][q] * SPLIT16[p][p ^ k]
                if lhs != rhs:
                    bad += 1
    return bad


def check_derivations() -> dict[str, Any]:
    if len(DERS8) != 14:
        raise RuntimeError(f"derivation space has dimension {len(DERS8)}")
    fixes = all(d[i][0] == 0 and d[0][i] == 0 for d in DERS8 for i in range(8))
    skew = all(ETA[i + 1] * d[i][j] + ETA[j + 1] * d[j][i] == 0 for d in DERS for i in range(7) for j in range(7))
    # the lift D + D on (a, b) is a derivation of the split sedenion table
    lift_bad = sum(parallel.ordered_map(lift_failures, list(DERS8), min_items=1))
    if not (fixes and skew) or lift_bad:
        raise RuntimeError("derivation checks failed")
    return {"dimension": 14, "fix_e0_preserve_im": fixes, "eta_skew": skew, "sedenion_lift_failures": lift_bad}


def apply7(d: Sequence[Sequence[Any]], x: Sequence[Any]) -> list[Any]:
    out = []
    for i in range(7):
        acc: Any = 0
        for j in range(7):
            if d[i][j]:
                acc = acc + d[i][j] * x[j]
        out.append(acc)
    return out


def split_z(z: Sequence[Any]) -> tuple[list[Any], Any, list[Any]]:
    return list(z[0:7]), z[7], list(z[8:15])


def join_z(u: Sequence[Any], mu: Any, v: Sequence[Any]) -> list[Any]:
    return list(u) + [mu] + list(v)


def h_tangent(z: Sequence[Any]) -> list[list[Any]]:
    """The 16 tangent vectors of H = G_2 x SO(2) x C^* at z': 14 derivations, the scaling and the boost."""
    u, mu, v = split_z(z)
    vecs = [join_z(apply7(d, u), 0, apply7(d, v)) for d in DERS]
    vecs.append(list(z))
    vecs.append(join_z(v, 0, u))
    return vecs


def orbit_dim(z: Sequence[Any]) -> int:
    return c_rank(h_tangent(z))


# ---------------------------------------------------------------------------------------------------------------------
# Unipotent elements of G_2 (exp of nilpotent derivations) and the other group elements


def matmul7(a: Sequence[Sequence[Fraction]], b: Sequence[Sequence[Fraction]]) -> list[list[Fraction]]:
    return [[sum((a[i][k] * b[k][j] for k in range(7)), Fraction(0)) for j in range(7)] for i in range(7)]


def nilpotent_derivations() -> list[list[list[Fraction]]]:
    """Nilpotent derivations among the basis elements and their sums and differences, in a fixed order."""
    found: list[list[list[Fraction]]] = []
    cands = [DERS[i] for i in range(14)]
    for i, j in itertools.combinations(range(14), 2):
        for s in (1, -1):
            cands.append([[DERS[i][a][b] + s * DERS[j][a][b] for b in range(7)] for a in range(7)])
    for n in cands:
        power = n
        for _ in range(6):
            power = matmul7(power, n)
        if all(x == 0 for r in power for x in r):
            found.append(n)
    return found


def expm_nilpotent(n: Sequence[Sequence[Fraction]]) -> list[list[Fraction]]:
    result = [[Fraction(int(i == j)) for j in range(7)] for i in range(7)]
    term = [[Fraction(int(i == j)) for j in range(7)] for i in range(7)]
    for k in range(1, 8):
        term = [[x / k for x in r] for r in matmul7(term, n)]
        result = [[result[i][j] + term[i][j] for j in range(7)] for i in range(7)]
    return result


def is_automorphism(g: Sequence[Sequence[Fraction]]) -> bool:
    """g (extended by 1 on e'_0) preserves the split octonion product on Im: g(x y) = g(x) g(y) on basis pairs."""
    g8 = [[Fraction(int(i == j == 0)) for j in range(8)] for i in range(8)]
    for i in range(7):
        for j in range(7):
            g8[i + 1][j + 1] = g[i][j]
    for p in range(8):
        for q in range(8):
            lhs = [SPLIT16[p][q] * g8[k][p ^ q] for k in range(8)]
            rhs = [Fraction(0)] * 8
            for a in range(8):
                for b in range(8):
                    if g8[a][p] and g8[b][q]:
                        rhs[a ^ b] += g8[a][p] * g8[b][q] * SPLIT16[a][b]
            if lhs != rhs:
                return False
    return True


def act_g2(g: Sequence[Sequence[Any]], z: Sequence[Any]) -> list[Any]:
    u, mu, v = split_z(z)
    return join_z(apply7(g, u), mu, apply7(g, v))


def act_boost(c: Any, s: Any, z: Sequence[Any]) -> list[Any]:
    u, mu, v = split_z(z)
    return join_z(
        [c * a + s * b for a, b in zip(u, v, strict=True)], mu, [s * a + c * b for a, b in zip(u, v, strict=True)]
    )


BOOST = (Fraction(5, 4), Fraction(3, 4))  # c^2 - s^2 = 1, c + s = 2: infinite order

# ---------------------------------------------------------------------------------------------------------------------
# C_z, L_y, the invariants and the closure predicates


def original_z(zs: Sequence[Any]) -> list[Gq]:
    """z_k = i^popcount(k) z'_k."""
    return [i_pow(popcount(k + 1)) * Gq.of(zs[k]) for k in range(15)]


def cz_matrix(z: Sequence[Gq]) -> list[list[Gq]]:
    """15 x 15 Im-block of left multiplication by z in A_4, from the cd_core sedenion table."""
    full = [Gq(0)] + list(z)
    return [[full[a ^ b] * SIGN16[a ^ b][b] if a != b else Gq(0) for b in range(1, 16)] for a in range(1, 16)]


def rank_cz(zs: Sequence[Any]) -> int:
    return c_rank(cz_matrix(original_z(zs)))


def nullity_ly(zs: Sequence[Any]) -> int:
    z = original_z(zs)
    y = [Fraction(0)] * 32
    for k in range(15):
        y[k + 1] = z[k].re
        y[16 + k + 1] = z[k].im
    mat = left_mult_matrix_exact(32, y)
    return 32 - q_rank([list(r) for r in mat])


def inv_q(z: Sequence[Any]) -> Any:
    u, mu, v = split_z(z)
    return eta2(u, u) - mu * mu - eta2(v, v)


def inv_delta(z: Sequence[Any]) -> Any:
    u, _mu, v = split_z(z)
    w = eta2(u, v)
    return w * w - eta2(u, u) * eta2(v, v)


def minors_vanish(rows: Sequence[Sequence[Any]], size: int) -> bool:
    ncol = len(rows[0])
    for rsel in itertools.combinations(range(len(rows)), size):
        for csel in itertools.combinations(range(ncol), size):
            if _det([[rows[r][c] for c in csel] for r in rsel]):
                return False
    return True


def _det(m: list[list[Any]]) -> Any:
    n = len(m)
    if n == 1:
        return m[0][0]
    if n == 2:
        return m[0][0] * m[1][1] - m[0][1] * m[1][0]
    total: Any = 0
    for j in range(n):
        if m[0][j]:
            sub = [r[:j] + r[j + 1 :] for r in m[1:]]
            term = m[0][j] * _det(sub)
            total = total + term if j % 2 == 0 else total - term
    return total


def _zero(x: Any) -> bool:
    return not x


CLOSURES = ["W8", "E8bar", "Iso", "X+", "X-", "B9", "V", "VB", "Va+", "Va-", "N+", "N-"]
DIMS = {"W8": 12, "E8bar": 11, "Iso": 11, "X+": 10, "X-": 10, "B9": 9, "V": 8, "VB": 7, "Va+": 7, "Va-": 7}
DIMS.update({"N+": 6, "N-": 6})
NULLITY = {"W8": 8, "E8bar": 8, "Iso": 8, "X+": 8, "X-": 8, "B9": 12, "V": 12, "VB": 12, "Va+": 12, "Va-": 12}
NULLITY.update({"N+": 16, "N-": 16})
LOWER = {
    "W8": ["Iso", "B9", "VB", "N+", "N-"],
    "E8bar": ["X+", "X-", "B9", "V", "VB", "Va+", "Va-", "N+", "N-"],
    "Iso": ["B9", "VB", "N+", "N-"],
    "X+": ["B9", "VB", "Va+", "N+", "N-"],
    "X-": ["B9", "VB", "Va-", "N+", "N-"],
    "B9": ["VB", "N+", "N-"],
    "V": ["VB", "Va+", "Va-", "N+", "N-"],
    "VB": ["N+", "N-"],
    "Va+": ["N+"],
    "Va-": ["N-"],
    "N+": [],
    "N-": [],
}


def membership(z: Sequence[Any]) -> dict[str, bool]:
    u, mu, v = split_z(z)
    s = [a + b for a, b in zip(u, v, strict=True)]
    d = [a - b for a, b in zip(u, v, strict=True)]
    mu0 = _zero(mu)
    eu, ev, euv = eta2(u, u), eta2(v, v), eta2(u, v)
    iso = mu0 and _zero(eu) and _zero(ev) and _zero(euv)
    cr = cross(u, v)
    rank1 = minors_vanish([u, v], 2)
    q0 = _zero(inv_q(z))
    e8 = q0 and _zero(inv_delta(z)) and minors_vanish([u, v, cr], 3)
    vpu = all(_zero(a - b) for a, b in zip(u, v, strict=True))
    vmu = all(_zero(a + b) for a, b in zip(u, v, strict=True))
    return {
        "W8": mu0 and _zero(eta2(s, s)) and _zero(eta2(d, d)),
        "E8bar": e8,
        "Iso": iso,
        "X+": e8 and mu0 and _zero(eta2(d, d)),
        "X-": e8 and mu0 and _zero(eta2(s, s)),
        "B9": iso and all(_zero(c) for c in cr),
        "V": rank1 and q0,
        "VB": iso and rank1,
        "Va+": mu0 and vpu,
        "Va-": mu0 and vmu,
        "N+": mu0 and vpu and _zero(eu),
        "N-": mu0 and vmu and _zero(eu),
    }


def pattern(z: Sequence[Any]) -> str:
    m = membership(z)
    return "".join("1" if m[c] else "0" for c in CLOSURES)


def e(k: int) -> list[Fraction]:
    """e'_k in the 7-dimensional module, k = 1..7."""
    return [Fraction(int(j == k - 1)) for j in range(7)]


def vadd(*terms: tuple[Any, Sequence[Any]]) -> list[Any]:
    out: list[Any] = [Fraction(0)] * 7
    for c, vec in terms:
        out = [a + c * b for a, b in zip(out, vec, strict=True)]
    return out


N_VEC = vadd((1, e(1)), (1, e(3)))
K_VEC = vadd((1, e(4)), (1, e(6)))
A_VEC = vadd((1, e(2)), (1, e(3)))
ZERO7 = [Fraction(0)] * 7

REPS: dict[str, list[Fraction]] = {
    "W8": join_z(e(1), 0, e(3)),
    "E8bar": join_z(vadd((1, A_VEC), (3, e(1))), 4, vadd((2, A_VEC), (5, e(1)))),
    "Iso": join_z(N_VEC, 0, vadd((1, e(2)), (1, e(5)))),
    "X+": join_z(vadd((1, A_VEC), (1, e(1))), 0, e(1)),
    "X-": join_z(vadd((1, A_VEC), (1, e(1))), 0, vadd((-1, e(1)))),
    "B9": join_z(vadd((1, N_VEC), (2, K_VEC)), 0, vadd((3, N_VEC), (5, K_VEC))),
    "V": join_z(vadd((3, e(1))), 4, vadd((5, e(1)))),
    "VB": join_z(N_VEC, 0, ZERO7),
    "Va+": join_z(e(1), 0, e(1)),
    "Va-": join_z(e(1), 0, vadd((-1, e(1)))),
    "N+": join_z(N_VEC, 0, N_VEC),
    "N-": join_z(N_VEC, 0, vadd((-1, N_VEC))),
}
REPS = {k: [Fraction(x) for x in v] for k, v in REPS.items()}


def representative_row(job: tuple[str, Sequence[Sequence[Fraction]]]) -> tuple[dict[str, Any], bool]:
    """Nullity, rank C_z, orbit dimension and pattern at one representative and its four moved images."""
    name, g = job
    z = REPS[name]
    nul = nullity_ly(z)
    rk = rank_cz(z)
    od = orbit_dim(z)
    pat = pattern(z)
    moved = {
        "g2": act_g2(g, z),
        "boost": act_boost(BOOST[0], BOOST[1], z),
        "scale": [2 * x for x in z],
        "g2_boost": act_boost(Fraction(13, 12), Fraction(5, 12), act_g2(g, z)),
    }
    moved_rows = {}
    moved_ok = True
    for mname, mz in moved.items():
        mrow = {"nullity": nullity_ly(mz), "orbit_dim": orbit_dim(mz), "pattern": pattern(mz)}
        moved_rows[mname] = mrow
        moved_ok &= mrow == {"nullity": nul, "orbit_dim": od, "pattern": pat}
    expected_pat = "".join("1" if (c == name or c_in(name, c)) else "0" for c in CLOSURES)
    row_ok = nul == NULLITY[name] and nul == 28 - 2 * rk and od == DIMS[name] and pat == expected_pat
    row = {
        "nullity_Ly": nul,
        "28_minus_2_rank_Cz": 28 - 2 * rk,
        "orbit_dim": od,
        "pattern": pat,
        "pattern_expected_from_closure_order": expected_pat,
        "moved": moved_rows,
        "pass": row_ok,
    }
    return row, moved_ok


def check_representatives() -> dict[str, Any]:
    """Nullity of L_y, rank C_z, orbit dimension and pattern at the twelve representatives and at moved points."""
    nil = nilpotent_derivations()
    span = q_rank([[x for r in n for x in r] for n in nil])
    g_a = expm_nilpotent(nil[0])
    g_b = expm_nilpotent(nil[len(nil) // 2])
    g_c = expm_nilpotent(nil[-1])
    g = matmul7(matmul7(g_a, g_b), g_c)
    if span != 14 or not is_automorphism(g):
        raise RuntimeError("unipotent G_2 elements do not span or are not automorphisms")
    rows = {}
    patterns = {}
    ok = True
    names = list(REPS)
    for name, (row, moved_ok) in zip(
        names, parallel.ordered_map(representative_row, [(n, g) for n in names], min_items=1), strict=True
    ):
        ok &= moved_ok and row["pass"]
        rows[name] = row
        patterns[name] = row["pattern"]
    distinct = len(set(patterns.values())) == len(patterns)
    lower_dims = all(DIMS[y] < DIMS[x] for x in LOWER for y in LOWER[x])
    return {
        "pattern_order": CLOSURES,
        "unipotent_g2": {"nilpotent_derivations_found": len(nil), "span": span, "product_is_automorphism": True},
        "rows": rows,
        "patterns_distinct": distinct,
        "lower_closures_smaller_dimension": lower_dims,
        "pass": ok and distinct and lower_dims,
    }


def c_in(orbit: str, closure: str) -> bool:
    """The closure order table: orbit lies in closure."""
    return orbit in LOWER[closure]


# ---------------------------------------------------------------------------------------------------------------------
# Polynomials over Q in the split coordinates (flint), and the closure ideals

CTX = flint.fmpq_mpoly_ctx.get(("x", 15), "degrevlex")
XS = list(CTX.gens())
VAR_NAMES = [f"x{k}" for k in range(15)]


def poly_str(f: Any) -> str:
    text = str(f).replace(" ", "")
    return text if text else "0"


def closure_generators() -> dict[str, list[Any]]:
    u, mu, v = split_z(XS)
    s = [a + b for a, b in zip(u, v, strict=True)]
    d = [a - b for a, b in zip(u, v, strict=True)]
    eu, ev, euv = eta2(u, u), eta2(v, v), eta2(u, v)
    q = eu - mu * mu - ev
    delta = euv * euv - eu * ev
    cr = cross(u, v)
    rows3 = [u, v, cr]
    minors3 = []
    for cols in itertools.combinations(range(7), 3):
        minors3.append(_det([[rows3[r][c] for c in cols] for r in range(3)]))
    minors2 = [u[i] * v[j] - u[j] * v[i] for i, j in itertools.combinations(range(7), 2)]
    iso = [mu, eu, ev, euv]
    e8 = [q, delta, *minors3]
    g = q * q - 4 * delta
    gens = {
        "W8": [mu, eta2(s, s), eta2(d, d)],
        "E8bar": e8,
        "Iso": iso,
        "X+": [*e8, mu, eta2(d, d)],
        "X-": [*e8, mu, eta2(s, s)],
        "B9": [*iso, *cr],
        "V": [*minors2, q],
        "VB": [*iso, *minors2],
        "Va+": [mu, *[b - a for a, b in zip(u, v, strict=True)]],
        "Va-": [mu, *[b + a for a, b in zip(u, v, strict=True)]],
        "N+": [mu, *[b - a for a, b in zip(u, v, strict=True)], eu],
        "N-": [mu, *[b + a for a, b in zip(u, v, strict=True)], eu],
        "VQ": [q],
        "VG": [g],
    }
    return {k: [f for f in fs if not f.is_zero()] for k, fs in gens.items()}


GENS = closure_generators()


def evaluate(f: Any, z: Sequence[Fraction]) -> Fraction:
    val = f(*[flint.fmpq(x.numerator, x.denominator) for x in z])
    return Fraction(int(val.p), int(val.q))


def jacobian_rank(gens: Sequence[Any], z: Sequence[Fraction]) -> int:
    rows = [[evaluate(f.derivative(k), z) for k in range(15)] for f in gens]
    return q_rank(rows)


# ---------------------------------------------------------------------------------------------------------------------
# Singular


def singular_ring(field: str = "0") -> str:
    return f"ring R = {field},({','.join(VAR_NAMES)}),dp;\n"


def ideal_str(name: str, gens: Sequence[Any]) -> str:
    return f"ideal {name} = " + ",\n  ".join(poly_str(f) for f in gens) + ";\n"


def run_singular(job: tuple[str, str]) -> tuple[str, str, float]:
    """Run one Singular script; return (name, stdout, seconds). A Singular error raises."""
    name, script = job
    start = time.time()
    with tempfile.NamedTemporaryFile("w", suffix=".sing", delete=False, encoding="utf-8") as fh:
        fh.write('LIB "primdec.lib";\noption(redSB);\n' + script + '\n"@@done 1";\nquit;\n')
        path = fh.name
    try:
        proc = subprocess.run(
            [SINGULAR, "-q", "--no-warn", path],
            capture_output=True,
            text=True,
            timeout=3600,
            check=False,
            stdin=subprocess.DEVNULL,
        )
    finally:
        os.unlink(path)
    out = proc.stdout + proc.stderr
    if proc.returncode != 0 or "? error" in out or "   ? " in out or "@@done 1" not in out:
        raise RuntimeError(f"Singular job {name} failed:\n{out[-3000:]}")
    return name, out, time.time() - start


def tagged(out: str) -> dict[str, str]:
    """Lines '@@key value' of a Singular output."""
    res = {}
    for line in out.splitlines():
        if line.startswith("@@"):
            key, _, val = line[2:].partition(" ")
            res[key] = val.strip()
    return res


def singular_batch(jobs: Sequence[tuple[str, str]]) -> dict[str, tuple[dict[str, str], float]]:
    results = parallel.ordered_map(run_singular, list(jobs), min_items=1)
    return {name: (tagged(out), secs) for name, out, secs in results}


def _frac_str(x: Fraction) -> str:
    return f"({x.numerator}/{x.denominator})" if x.denominator != 1 else f"({x.numerator})"


def derivation_images(gens: Sequence[Any]) -> list[Any]:
    """D f = sum_k (D z')_k df/dz'_k for the 14 derivations D acting on u' and v' alike."""
    out = []
    for d in DERS:
        dz = h_tangent_poly(d)
        for f in gens:
            acc = CTX.from_dict({})
            for k in range(15):
                if dz[k] != 0:
                    acc = acc + dz[k] * f.derivative(k)
            out.append(acc)
    return out


def h_tangent_poly(d: Sequence[Sequence[Fraction]]) -> list[Any]:
    u, _mu, v = split_z(XS)
    du = [
        sum((flint.fmpq(x.numerator, x.denominator) * u[j] for j, x in enumerate(d[i]) if x), CTX.from_dict({}))
        for i in range(7)
    ]
    dv = [
        sum((flint.fmpq(x.numerator, x.denominator) * v[j] for j, x in enumerate(d[i]) if x), CTX.from_dict({}))
        for i in range(7)
    ]
    return join_z(du, 0, dv)


def symmetry_job(name: str) -> tuple[str, str]:
    gens = GENS[name]
    c, s = BOOST
    u_img = [f"{_frac_str(c)}*x{k}+{_frac_str(s)}*x{k + 8}" for k in range(7)]
    v_img = [f"{_frac_str(s)}*x{k}+{_frac_str(c)}*x{k + 8}" for k in range(7)]
    boost = ",".join([*u_img, "x7", *v_img])
    refl = ",".join([*VAR_NAMES[:7], "-x7", *VAR_NAMES[8:]])
    script = singular_ring() + ideal_str("I", gens) + ideal_str("DI", derivation_images(gens))
    script += f"ideal SI = std(I);\nmap bo = R, {boost};\nmap rf = R, {refl};\n"
    script += '"@@boost " + string(size(reduce(bo(I), SI)));\n'
    script += '"@@reflection " + string(size(reduce(rf(I), SI)));\n'
    script += '"@@derivations " + string(size(reduce(DI, SI)));\n'
    return f"sym-{name}", script


def check_symmetry() -> dict[str, Any]:
    names = [*CLOSURES, "VQ", "VG"]
    res = singular_batch(parallel.ordered_map(symmetry_job, names, min_items=1))
    rows = {}
    ok = True
    for n in names:
        tags, secs = res[f"sym-{n}"]
        row = {k: int(tags[k]) for k in ("boost", "reflection", "derivations")}
        row_ok = all(v == 0 for v in row.values())
        ok &= row_ok
        rows[n] = {"nonzero_normal_forms": row, "pass": row_ok, "seconds": round(secs, 2)}
    return {
        "boost_element": [str(BOOST[0]), str(BOOST[1])],
        "argument": "the boosts g with g(X) in X form a closed subgroup of SO(2,C); it contains the element of infinite"
        " order (5/4, 3/4), hence an infinite closed subgroup of the one-dimensional connected group, hence all of it",
        "rows": rows,
        "pass": ok,
    }


# ---------------------------------------------------------------------------------------------------------------------
# Search of the six slices for R_8 points whose orbit dimension or membership pattern fits no listed orbit

SLICES: dict[str, tuple[list[Fraction], list[Fraction]]] = {
    "P2": (e(1), e(2)),
    "P3a": (A_VEC, e(1)),
    "P3b": (vadd((1, e(2)), (-1, e(3))), e(1)),
    "P3c": (vadd((1, e(2)), (1, e(3)), (1, e(4)), (-1, e(5))), e(1)),
    "P4s": (N_VEC, K_VEC),
    "P4g": (N_VEC, vadd((1, e(2)), (1, e(5)))),
}
DERS_INT = [[[int(x) for x in r] for r in d] for d in DERS]
CZ_INDEX = [(a, b, a ^ b, SIGN16[a ^ b][b]) for a in range(1, 16) for b in range(1, 16) if a != b]
EXPECTED = {name: (pattern(z), DIMS[name], NULLITY[name]) for name, z in REPS.items()}


class GI:
    """Exact Gaussian integer."""

    __slots__ = ("im", "re")

    def __init__(self, re: int = 0, im: int = 0) -> None:
        self.re = re
        self.im = im

    @staticmethod
    def of(x: Any) -> GI:
        return x if isinstance(x, GI) else GI(int(x))

    def __add__(self, o: Any) -> GI:
        o = GI.of(o)
        return GI(self.re + o.re, self.im + o.im)

    __radd__ = __add__

    def __sub__(self, o: Any) -> GI:
        o = GI.of(o)
        return GI(self.re - o.re, self.im - o.im)

    def __rsub__(self, o: Any) -> GI:
        return GI.of(o) - self

    def __mul__(self, o: Any) -> GI:
        o = GI.of(o)
        return GI(self.re * o.re - self.im * o.im, self.re * o.im + self.im * o.re)

    __rmul__ = __mul__

    def __neg__(self) -> GI:
        return GI(-self.re, -self.im)

    def __bool__(self) -> bool:
        return bool(self.re) or bool(self.im)


def classify(rank: int, odim: int, pat: str, expected: dict[str, tuple[str, int, int]] | None = None) -> str | None:
    """The orbit whose closure is the unique minimal closure containing the point, if every invariant fits it."""
    inside = {c for c, bit in zip(CLOSURES, pat, strict=True) if bit == "1"}
    minimal = [x for x in inside if not any(y in inside for y in LOWER[x])]
    if len(minimal) != 1:
        return None
    x = minimal[0]
    exp_pat, exp_dim, exp_nul = (expected or EXPECTED)[x]
    if pat == exp_pat and odim == exp_dim and 28 - 2 * rank == exp_nul:
        return x
    return None


def slice_point(name: str, params: Sequence[Any]) -> list[Any]:
    a_vec, b_vec = SLICES[name]
    a, b, c, d, m = params
    u = [a * int(x) + b * int(y) for x, y in zip(a_vec, b_vec, strict=True)]
    v = [c * int(x) + d * int(y) for x, y in zip(a_vec, b_vec, strict=True)]
    return join_z(u, m, v)


def gi_point_ranks(z: Sequence[GI]) -> tuple[int, int]:
    """(rank_C C_z, rank_C of the 16 H-tangent vectors) at a Gaussian-integer point, by realified integer ranks."""
    rot = [GI(1, 0), GI(0, 1), GI(-1, 0), GI(0, -1)]
    zo = [GI(0)] + [rot[popcount(k + 1) % 4] * z[k] for k in range(15)]
    re = [[0] * 15 for _ in range(15)]
    im = [[0] * 15 for _ in range(15)]
    for a, b, k, sg in CZ_INDEX:
        re[a - 1][b - 1] = sg * zo[k].re
        im[a - 1][b - 1] = sg * zo[k].im
    real = [re[i] + [-x for x in im[i]] for i in range(15)] + [im[i] + re[i] for i in range(15)]
    rank = z_rank(real) // 2
    u, _mu, v = split_z(z)
    vecs = [join_z(apply7(dm, u), GI(0), apply7(dm, v)) for dm in DERS_INT]
    vecs.append(list(z))
    vecs.append(join_z(v, GI(0), u))
    vr = [[GI.of(x).re for x in r] + [-GI.of(x).im for x in r] for r in vecs]
    vi = [[GI.of(x).im for x in r] + [GI.of(x).re for x in r] for r in vecs]
    return rank, z_rank(vr + vi) // 2


def search_item_gaussian(item: tuple[str, int, tuple[tuple[int, int], ...]]) -> dict[str, Any]:
    """All parameter tuples with first entry values[first] over the value set; classify the R_8 points."""
    name, first, values = item
    vals = [GI(r, i) for r, i in values]
    counts: Counter[str] = Counter()
    anomalies = []
    total = 0
    for rest in itertools.product(vals, repeat=4):
        params = (vals[first], *rest)
        z = slice_point(name, params)
        if not any(z):
            continue
        total += 1
        rank, odim = gi_point_ranks(z)
        if rank > 10:
            continue
        pat = pattern(z)
        cls = classify(rank, odim, pat)
        if cls is None:
            anomalies.append(
                {"params": [[p.re, p.im] for p in params], "rank": rank, "orbit_dim": odim, "pattern": pat}
            )
        counts[cls or "unclassified"] += 1
    return {
        "slice": name,
        "points": total,
        "counts": dict(counts),
        "anomalies": anomalies[:5],
        "n_anomalies": len(anomalies),
    }


def search_item_modp(item: tuple[str, int, int]) -> dict[str, Any]:
    """All F_13 parameter tuples with (a, b) fixed; ranks over F_13 with i = 5."""
    name, a0, b0 = item
    p = F_P
    nm = [flint.nmod(k, p) for k in range(p)]
    rot = [nm[1], nm[F_I], nm[p - 1], nm[(p - F_I) % p]]
    counts: Counter[str] = Counter()
    anomalies = []
    total = 0
    for c, d, m in itertools.product(range(p), repeat=3):
        z = slice_point(name, (nm[a0], nm[b0], nm[c], nm[d], nm[m]))
        if not any(z):
            continue
        total += 1
        zo = [nm[0]] + [rot[popcount(k + 1) % 4] * z[k] for k in range(15)]
        mat = [[nm[0]] * 15 for _ in range(15)]
        for a, b, k, sg in CZ_INDEX:
            mat[a - 1][b - 1] = sg * zo[k]
        rank = int(flint.nmod_mat([[int(x) for x in r] for r in mat], p).rank())
        if rank > 10:
            continue
        u, _mu, v = split_z(z)
        vecs = [join_z(apply7(dm, u), nm[0], apply7(dm, v)) for dm in DERS_INT]
        vecs.append(list(z))
        vecs.append(join_z(v, nm[0], u))
        odim = int(flint.nmod_mat([[int(x) for x in r] for r in vecs], p).rank())
        pat = pattern(z)
        cls = classify(rank, odim, pat)
        if cls is None:
            anomalies.append({"params": [a0, b0, c, d, m], "rank": rank, "orbit_dim": odim, "pattern": pat})
        counts[cls or "unclassified"] += 1
    return {
        "slice": name,
        "points": total,
        "counts": dict(counts),
        "anomalies": anomalies[:5],
        "n_anomalies": len(anomalies),
    }


GAUSS9 = tuple((r, i) for r in (-1, 0, 1) for i in (-1, 0, 1))
INT7 = tuple((r, 0) for r in range(-3, 4))


def check_search() -> dict[str, Any]:
    out: dict[str, Any] = {}
    for label, values in (("gaussian_box_{0,+-1}+i{0,+-1}", GAUSS9), ("integer_box_[-3,3]", INT7)):
        items = [(name, k, values) for name in SLICES for k in range(len(values))]
        start = time.time()
        res = parallel.ordered_map(search_item_gaussian, items, min_items=1)
        out[label] = _merge_search(res, time.time() - start)
    items_p = [(name, a, b) for name in SLICES for a in range(F_P) for b in range(F_P)]
    start = time.time()
    res_p = parallel.ordered_map(search_item_modp, items_p, min_items=1)
    out["F13_complete_slices"] = _merge_search(res_p, time.time() - start)
    out["pass_char0"] = all(out[k]["anomalies_total"] == 0 for k in out if not k.startswith("F13"))
    out["pass_F13"] = out["F13_complete_slices"]["anomalies_total"] == 0
    return out


def _merge_search(res: Sequence[dict[str, Any]], secs: float) -> dict[str, Any]:
    per: dict[str, dict[str, Any]] = {}
    for r in res:
        row = per.setdefault(r["slice"], {"points": 0, "counts": Counter(), "anomalies": [], "n_anomalies": 0})
        row["points"] += r["points"]
        row["counts"].update(r["counts"])
        row["n_anomalies"] += r["n_anomalies"]
        row["anomalies"].extend(r["anomalies"][: max(0, 5 - len(row["anomalies"]))])
    for row in per.values():
        row["counts"] = dict(sorted(row["counts"].items()))
    orbits_hit = sorted({k for row in per.values() for k in row["counts"]})
    return {
        "per_slice": per,
        "points_total": sum(r["points"] for r in per.values()),
        "r8_points_total": sum(sum(r["counts"].values()) for r in per.values()),
        "orbits_hit": orbits_hit,
        "anomalies_total": sum(r["n_anomalies"] for r in per.values()),
        "seconds": round(secs, 1),
    }


# ---------------------------------------------------------------------------------------------------------------------
# Transverse germs: Euclidean (or Hermitian) orthogonal slice, minimal primes through the point, tangent cones from
# the deformation to the normal cone with global orderings


def coeff_str(x: Any) -> str:
    if isinstance(x, Gq):
        return x.singular()
    return _frac_str(Fraction(x))


def germ_script(gens: Sequence[Any], point: Sequence[Any], complement: Sequence[Sequence[Any]], gaussian: bool) -> str:
    r = len(complement)
    field = "(0,I)" if gaussian else "0"
    mp = "minpoly = I^2+1;\n" if gaussian else ""
    imgs = []
    for k in range(15):
        terms = [coeff_str(point[k])]
        for j in range(r):
            if complement[j][k]:
                terms.append(f"{coeff_str(complement[j][k])}*t({j + 1})")
        imgs.append("+".join(terms))
    hsub = ",".join([*[f"h*t({j + 1})" for j in range(r)], "h"])
    zero_t = ",".join(["0"] * r)
    script = singular_ring(field) + mp + ideal_str("I", gens)
    script += f"ring S = {field},(t(1..{r})),dp;\n{mp}"
    script += f"ring S2 = {field},(t(1..{r}),h),dp;\n{mp}map psi = S2, {hsub};\n"
    script += "setring S;\n"
    script += f"map phi = R, {','.join(imgs)};\nmap ev0 = S, {zero_t};\n"
    script += """ideal J = phi(I);
list L = minAssGTZ(J);
list T; int i; int j; int k;
for (i=1;i<=size(L);i++){ if (size(jet(L[i],0))==0) { T[size(T)+1] = L[i]; } }
"@@primes_through_point " + string(size(T));
ideal P0 = T[1];
for (i=2;i<=size(T);i++){ P0 = intersect(P0, T[i]); }
list G = P0; for (i=1;i<=size(T);i++){ G[i+1] = T[i]; }
string tg;
for (i=1;i<=size(G);i++) {
  setring S;
  ideal cur = G[i];
  if (i==1) { tg = "germ"; } else { tg = "comp" + string(i-1); }
  "@@" + tg + "_dim " + string(dim(std(cur)));
  matrix Jm = jacob(cur);
  "@@" + tg + "_embdim " + string(nvars(S) - rank(ev0(Jm)));
  setring S2;
  ideal C = imap(S, cur);
  ideal Ch = psi(C);
  ideal Cs = sat(Ch, h);
  Cs = subst(Cs, h, 0);
  setring S;
  ideal TC = std(imap(S2, Cs));
  "@@" + tg + "_tc_homog " + string(homog(TC));
  "@@" + tg + "_tc_dim " + string(dim(TC));
  "@@" + tg + "_mult " + string(mult(TC));
  ideal Lin;
  for (k=1;k<=size(TC);k++){ if (deg(TC[k])==1) { Lin[size(Lin)+1] = TC[k]; } }
  "@@" + tg + "_tc_linear " + string(size(Lin));
  ideal Rd = simplify(reduce(TC, std(Lin)), 2);
  Rd = simplify(interred(Rd), 2);
  string dg = "";
  for (k=1;k<=size(Rd);k++){ dg = dg + string(deg(Rd[k])) + ","; }
  "@@" + tg + "_tc_nonlinear_degrees " + dg;
  if (size(Rd)==1) { if (deg(Rd[1])==2) { "@@" + tg + "_quadric_rank " + string(rank(jacob(jacob(Rd[1])))); } }
  kill cur; kill Jm; kill TC; kill Lin; kill Rd; kill dg;
  setring S2; kill C; kill Ch; kill Cs;
  setring S;
}
setring S;
string mt = "";
for (i=1;i<=size(T);i++){ for (j=i+1;j<=size(T);j++){
  list M = minAssGTZ(T[i]+T[j]); int md = -1;
  for (k=1;k<=size(M);k++){ if (size(jet(M[k],0))==0) { if (dim(std(M[k])) > md) { md = dim(std(M[k])); } } }
  mt = mt + string(i) + "-" + string(j) + ":" + string(md) + ",";
  kill M; kill md;
} }
"@@meets " + mt;
"""
    return script


def transverse_complement(point: Sequence[Fraction]) -> list[list[int]]:
    rows = h_tangent(point)
    return [integerize(w) for w in q_nullspace(rows, 15)]


def orbits_in(closure: str) -> list[str]:
    if closure == "VQ":
        return [o for o in CLOSURES if inv_q(REPS[o]) == 0]
    if closure == "VG":
        return list(CLOSURES)
    return [closure, *LOWER[closure]]


def germ_pairs() -> list[tuple[str, str]]:
    return [(x, o) for x in [*CLOSURES, "VQ", "VG"] for o in orbits_in(x)]


def germ_job(pair: tuple[str, str]) -> tuple[str, str]:
    x, o = pair
    p = REPS[o]
    return f"germ|{x}|{o}", germ_script(GENS[x], p, transverse_complement(p), gaussian=False)


def parse_germ(tags: dict[str, str]) -> dict[str, Any]:
    out: dict[str, Any] = {"sheets": int(tags["primes_through_point"])}
    for key, val in tags.items():
        if key.startswith(("germ_", "comp")):
            out[key] = val if key.endswith("_degrees") else int(val)
    meets = {}
    for item in tags.get("meets", "").split(","):
        if item:
            pair, _, dim = item.partition(":")
            meets[pair] = int(dim)
    out["meets"] = meets
    return out


# Germ table of the record: (closure, orbit) -> (dim, mult, embdim, extra). Every other pair must be smooth.
GERM_TABLE: dict[tuple[str, str], dict[str, Any]] = {}


def _row(pairs: Sequence[tuple[str, str]], dim: int, mult: int, emb: int, **extra: Any) -> None:
    for pr in pairs:
        GERM_TABLE[pr] = {"dim": dim, "mult": mult, "embdim": emb, **extra}


_row([("V", "N+"), ("V", "N-")], 2, 2, 3, sheets=1, quadric_rank=3)
_row([("W8", "N+"), ("W8", "N-")], 6, 2, 7, sheets=1, quadric_rank=7)
_row([("Iso", "VB")], 4, 2, 5, sheets=1, quadric_rank=5)
_row([("Iso", "N+"), ("Iso", "N-")], 5, 2, 6, sheets=1, quadric_rank=5)
_row([("E8bar", "V")], 3, 2, 6, sheets=2, smooth_sheets=True, meet=0)
_row([("E8bar", "Va+"), ("E8bar", "Va-")], 4, 2, 7, sheets=2, smooth_sheets=True, meet=1)
_row([("X+", "Va+"), ("X-", "Va-")], 3, 2, 6, sheets=2, smooth_sheets=True, meet=0)
_row([("E8bar", "B9")], 2, 2, 3, sheets=1)
_row([("E8bar", "VB")], 4, 2, 7, sheets=1)
_row([("E8bar", "N+"), ("E8bar", "N-")], 5, 3, 8, sheets=1)
_row([("X+", "N+"), ("X-", "N-")], 4, 2, 7, sheets=1)
_row([("VG", "W8")], 2, 2, 3, sheets=1, quadric_rank=3)
_row([("VG", "V")], 6, 2, 7, sheets=1, quadric_rank=7)
_row([("VG", "Va+"), ("VG", "Va-")], 7, 2, 8, sheets=1, quadric_rank=7)
_row([("VG", "Iso")], 3, 2, 4, sheets=1, quadric_rank=2)
_row([("VG", "VB")], 7, 2, 8, sheets=1, quadric_rank=2)
_row([("VG", "B9")], 5, 2, 6, sheets=1, quadric_rank=2)
_row([("VG", "N+"), ("VG", "N-")], 8, 3, 9)

# Singular-locus table of the record: orbits along which the closure is singular (the origin is listed separately).
SING_TABLE = {
    "N+": [],
    "N-": [],
    "VB": [],
    "B9": [],
    "VQ": [],
    "Va+": [],
    "Va-": [],
    "V": ["N+", "N-"],
    "W8": ["N+", "N-"],
    "Iso": ["VB", "N+", "N-"],
    "X+": ["Va+", "N+"],
    "X-": ["Va-", "N-"],
    "E8bar": ["V", "B9", "VB", "Va+", "Va-", "N+", "N-"],
    "VG": ["W8", "Iso", "B9", "VB", "V", "Va+", "Va-", "N+", "N-"],
}
LINEAR_CLOSURES = {"Va+", "Va-"}


def ambient_codim(closure: str) -> int:
    return 15 - (14 if closure in ("VQ", "VG") else DIMS[closure])


def moved_point(z: Sequence[Fraction], g: Sequence[Sequence[Fraction]]) -> list[Fraction]:
    return act_boost(Fraction(13, 12), Fraction(5, 12), act_g2(g, [3 * x for x in z]))


def jacobian_ranks(job: tuple[str, str, Sequence[Sequence[Fraction]]]) -> tuple[int, int]:
    """Jacobian rank of the closure generators at the orbit representative and at its image under g, boost, scaling."""
    x, o, g = job
    p = REPS[o]
    return jacobian_rank(GENS[x], p), jacobian_rank(GENS[x], moved_point(p, g))


def check_germs() -> dict[str, Any]:
    nil = nilpotent_derivations()
    g = matmul7(matmul7(expm_nilpotent(nil[0]), expm_nilpotent(nil[len(nil) // 2])), expm_nilpotent(nil[-1]))
    pairs = germ_pairs()
    start = time.time()
    res = singular_batch(parallel.ordered_map(germ_job, pairs, min_items=1))
    ranks = parallel.ordered_map(jacobian_ranks, [(x, o, g) for x, o in pairs], min_items=1)
    rows = []
    ok = True
    for (x, o), (jr, jr_moved) in zip(pairs, ranks, strict=True):
        tags, secs = res[f"germ|{x}|{o}"]
        gm = parse_germ(tags)
        smooth = gm["germ_embdim"] == gm["germ_dim"] and gm["germ_mult"] == 1
        expected_dim = (14 if x in ("VQ", "VG") else DIMS[x]) - DIMS[o]
        row: dict[str, Any] = {
            "closure": x,
            "orbit": o,
            "germ": gm,
            "smooth": smooth,
            "jacobian_rank_of_generators_at_rep": jr,
            "jacobian_rank_at_moved_point": jr_moved,
            "codim": ambient_codim(x),
            "seconds": round(secs, 2),
        }
        checks = [gm["germ_dim"] == expected_dim, gm["germ_tc_dim"] == gm["germ_dim"], gm["germ_tc_homog"] == 1]
        if smooth:
            checks.append(jr <= ambient_codim(x))
        else:
            checks.append(jr < ambient_codim(x) and jr_moved < ambient_codim(x))
        exp = GERM_TABLE.get((x, o))
        if exp is None:
            row["record_says"] = "smooth"
            row["verdict"] = "confirmed" if smooth and all(checks) else "refuted"
        else:
            row["record_says"] = exp
            match = (
                gm["germ_dim"] == exp["dim"] and gm["germ_mult"] == exp["mult"] and gm["germ_embdim"] == exp["embdim"]
            )
            if "sheets" in exp:
                match &= gm["sheets"] == exp["sheets"]
            if "quadric_rank" in exp:
                match &= gm.get("germ_quadric_rank") == exp["quadric_rank"]
                match &= gm["germ_dim"] == gm["germ_embdim"] - 1
            if exp.get("smooth_sheets"):
                for i in range(1, gm["sheets"] + 1):
                    match &= gm[f"comp{i}_dim"] == gm[f"comp{i}_embdim"] == gm["germ_dim"]
            if "meet" in exp:
                match &= set(gm["meets"].values()) == {exp["meet"]}
            row["verdict"] = "confirmed" if match and all(checks) else "refuted"
        row["consistency_checks"] = all(checks)
        ok &= row["verdict"] == "confirmed"
        rows.append(row)
    # Theorem 3: singular loci from the germ smoothness, and the origin
    sing: dict[str, Any] = {}
    closures = [*CLOSURES, "VQ", "VG"]
    spans = parallel.ordered_map(origin_span, [(x, nil) for x in closures], min_items=1)
    for x, span in zip(closures, spans, strict=True):
        singular_orbits = sorted(r["orbit"] for r in rows if r["closure"] == x and not r["smooth"])
        smooth_orbits = sorted(r["orbit"] for r in rows if r["closure"] == x and r["smooth"])
        dim_x = 14 if x in ("VQ", "VG") else DIMS[x]
        origin_singular = span > dim_x
        match = singular_orbits == sorted(SING_TABLE[x]) and origin_singular == (x not in LINEAR_CLOSURES)
        sing[x] = {
            "singular_orbits": singular_orbits,
            "smooth_orbits": smooth_orbits,
            "record_singular_orbits": sorted(SING_TABLE[x]),
            "linear_span_dim_of_sampled_points": span,
            "dim": dim_x,
            "origin_singular": origin_singular,
            "verdict": "confirmed" if match else "refuted",
        }
        ok &= match
    return {"pairs": rows, "singular_loci": sing, "seconds": round(time.time() - start, 1), "pass": ok}


def origin_span(job: tuple[str, Sequence[Any]]) -> int:
    """Dimension of the linear span of the representatives in the closure and their unipotent and boost images."""
    closure, nil = job
    pts = []
    for o in orbits_in(closure):
        p = REPS[o]
        pts.append(p)
        pts.append(act_boost(BOOST[0], BOOST[1], p))
        for n in nil:
            pts.append(act_g2(expm_nilpotent(n), p))
    return q_rank(pts)


# ---------------------------------------------------------------------------------------------------------------------
# The normal link of R_12 = V u B9 at x0 = e_1 + e_18, over Q(i) at x0 itself


def x0_split() -> list[Gq]:
    y = [0] * 32
    y[1] = 1
    y[18] = 1
    z = [Gq(y[k], y[16 + k]) for k in range(1, 16)]
    return [z[k - 1] * i_pow(-popcount(k)) for k in range(1, 16)]


def tangent_cap_script(
    gens_a: Sequence[Any], gens_b: Sequence[Any], point: Sequence[Gq], comp: Sequence[Sequence[Gq]]
) -> str:
    """Dimension of the intersection of the Zariski tangent spaces at the point of the two reduced slice germs."""
    r = len(comp)
    imgs = []
    for k in range(15):
        terms = [coeff_str(point[k])] + [f"{coeff_str(comp[j][k])}*t({j + 1})" for j in range(r) if comp[j][k]]
        imgs.append("+".join(terms))
    script = singular_ring("(0,I)") + "minpoly = I^2+1;\n" + ideal_str("IA", gens_a) + ideal_str("IB", gens_b)
    script += f"ring S = (0,I),(t(1..{r})),dp;\nminpoly = I^2+1;\n"
    script += f"map phi = R, {','.join(imgs)};\nmap ev0 = S, {','.join(['0'] * r)};\n"
    script += """proc germ0(ideal J)
{
  list L = minAssGTZ(J); int i; ideal P = 1;
  for (i=1;i<=size(L);i++){ if (size(jet(L[i],0))==0) { P = intersect(P, L[i]); } }
  return(P);
}
ideal PA = germ0(phi(IA));
ideal PB = germ0(phi(IB));
matrix Jm = jacob(PA + PB);
"@@tangent_cap " + string(nvars(S) - rank(ev0(Jm)));
"""
    return script


def check_x0() -> dict[str, Any]:
    x0 = x0_split()
    y = [0] * 32
    y[1] = 1
    y[18] = 1
    nullity = 32 - q_rank([list(r) for r in left_mult_matrix_exact(32, y)])
    od = orbit_dim(x0)
    pat = pattern(x0)
    tangent = h_tangent(x0)
    comp = c_nullspace_hermitian([[Gq.of(x) for x in r] for r in tangent], 15)
    jobs = []
    for name, gens in (("V", GENS["V"]), ("B9", GENS["B9"]), ("V+B9", GENS["V"] + GENS["B9"]), ("VB", GENS["VB"])):
        jobs.append((f"x0|{name}", germ_script(gens, x0, comp, gaussian=True)))
    jobs.append(("x0|tangent", tangent_cap_script(GENS["V"], GENS["B9"], x0, comp)))
    start = time.time()
    res = singular_batch(jobs)
    tan_cap = int(res.pop("x0|tangent")[0]["tangent_cap"])
    germs = {k.split("|")[1]: parse_germ(t) for k, (t, _s) in res.items()}
    gv, gb, gm, gvb = germs["V"], germs["B9"], germs["V+B9"], germs["VB"]
    v_curve = gv["sheets"] == 1 and gv["germ_dim"] == 1 and gv["germ_embdim"] == 1 and gv["germ_mult"] == 1
    b_surface = gb["sheets"] == 1 and gb["germ_dim"] == 2 and gb["germ_embdim"] == 2 and gb["germ_mult"] == 1
    meet_point = gm["germ_dim"] == 0 and tan_cap == 0
    vb_point = gvb["germ_dim"] == 0
    split_expected = [Gq(0, -1), Gq(1)] + [Gq(0)] * 13
    ok = (
        nullity == 12
        and od == 7
        and pat == EXPECTED["VB"][0]
        and len(comp) == 8
        and v_curve
        and b_surface
        and meet_point
        and vb_point
        and x0 == split_expected
    )
    return {
        "x0_split_coordinates": "u' = e'_2 - i e'_1, mu' = 0, v' = 0",
        "split_coordinates_match": x0 == split_expected,
        "nullity_Ly": nullity,
        "orbit_dim": od,
        "pattern": pat,
        "pattern_equals_VB": pat == EXPECTED["VB"][0],
        "slice_dim": len(comp),
        "germ_V": gv,
        "germ_B9": gb,
        "germ_V_cap_B9_reduced": gm,
        "tangent_space_intersection_in_slice": tan_cap,
        "germ_VB": gvb,
        "tangent_dims_full_space": {
            "V": 7 + gv["germ_embdim"],
            "B9": 7 + gb["germ_embdim"],
            "intersection": 7 + tan_cap,
        },
        "conclusion": "V is a smooth curve germ and B9 a smooth surface germ in the 8-dimensional transverse slice,"
        " meeting only at x0 with transverse tangent spaces; the link of their union is S^1 disjoint union S^3",
        "seconds": round(time.time() - start, 1),
        "pass": ok,
    }


# ---------------------------------------------------------------------------------------------------------------------
# Identities, the nullity-4 locus, closure dimensions, irreducibility and the non-nested intersections


def charpoly_matches(zo: Sequence[int]) -> bool:
    """At an original rational point, charpoly(C_z) = lam (lam^2 + Q)^3 (lam^4 + 2 Q lam^2 + G)^2."""
    lam = flint.fmpq_poly([0, 1])
    cz = [[Fraction(x.re) for x in r] for r in cz_matrix([Gq(x) for x in zo])]
    cp = flint.fmpq_mat([[flint.fmpq(x.numerator, x.denominator) for x in r] for r in cz]).charpoly()
    zs = [Gq(zo[k]) * i_pow(-popcount(k + 1)) for k in range(15)]
    qv, dv = inv_q(zs), inv_delta(zs)
    gv = qv * qv - 4 * dv
    if qv.im or gv.im:
        return False
    qf = flint.fmpq(qv.re.numerator, qv.re.denominator)
    gf = flint.fmpq(gv.re.numerator, gv.re.denominator)
    return bool(cp == lam * (lam**2 + qf) ** 3 * (lam**4 + 2 * qf * lam**2 + gf) ** 2)


def check_identities() -> dict[str, Any]:
    u, mu, v = split_z(XS)
    s = [a + b for a, b in zip(u, v, strict=True)]
    d = [a - b for a, b in zip(u, v, strict=True)]
    q = GENS["VQ"][0]
    g = GENS["VG"][0]
    q_sd = eta2(s, d) - mu * mu
    g_sd = eta2(s, s) * eta2(d, d) - 2 * mu * mu * eta2(s, d) + mu**4
    # gradient: dG/ds = 2 eta(d) eta s - 2 mu^2 eta d, dG/dd = 2 eta(s) eta d - 2 mu^2 eta s, dG/dmu = -4 mu Q
    grad_ok = True
    for j in range(7):
        gs = 2 * eta2(d, d) * ETA[j + 1] * s[j] - 2 * mu * mu * ETA[j + 1] * d[j]
        gd = 2 * eta2(s, s) * ETA[j + 1] * d[j] - 2 * mu * mu * ETA[j + 1] * s[j]
        grad_ok &= g.derivative(j) == gs + gd
        grad_ok &= g.derivative(8 + j) == gs - gd
    grad_ok &= g.derivative(7) == -4 * mu * q
    # cross-product identities over Q[x, y]
    ctx14 = flint.fmpq_mpoly_ctx.get(("y", 14), "degrevlex")
    ys = list(ctx14.gens())
    xv, yv = ys[:7], ys[7:]
    cxy = cross(xv, yv)
    lhs = cross(xv, cxy)
    rhs = [eta2(xv, yv) * a - eta2(xv, xv) * b for a, b in zip(xv, yv, strict=True)]
    cross_ok = lhs == rhs and eta2(cxy, xv) == 0 and eta2(cxy, yv) == 0
    cross_ok &= eta2(cxy, cxy) == eta2(xv, xv) * eta2(yv, yv) - eta2(xv, yv) ** 2
    cross_ok &= all(a == -b for a, b in zip(cxy, cross(yv, xv), strict=True))
    # characteristic polynomial of C_z at rational original points anchors Q and G to cd_core
    charpoly_ok = True
    pts = [
        [1, 2, 0, -1, 3, 0, 1, 2, -2, 1, 0, 1, 1, -1, 2],
        [0, 1, 1, 0, 0, 2, -1, 0, 1, 0, 3, 0, 0, 1, 1],
        [2, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 2, 0, 0],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    ]
    charpoly_ok &= all(parallel.ordered_map(charpoly_matches, pts, min_items=1))
    hess = q_rank([[evaluate(q.derivative(i).derivative(j), [Fraction(0)] * 15) for j in range(15)] for i in range(15)])
    ok = q == q_sd and g == g_sd and grad_ok and cross_ok and charpoly_ok and hess == 15
    return {
        "Q_equals_eta(s,d)-mu^2": q == q_sd,
        "G_equals_eta(s)eta(d)-2mu^2eta(s,d)+mu^4": g == g_sd,
        "gradient_of_G": grad_ok,
        "cross_product_identities": cross_ok,
        "charpoly_of_Cz_at_4_points": charpoly_ok,
        "hessian_rank_Q": hess,
        "pass": ok,
    }


def check_singular_global() -> dict[str, Any]:
    """Closure dimensions, Iso as a complete intersection, the fiber of X_+- over a null vector, intersections."""
    jobs = []
    for x in [*CLOSURES, "VQ", "VG"]:
        jobs.append((f"dim|{x}", singular_ring() + ideal_str("I", GENS[x]) + '"@@dim " + string(dim(std(I)));\n'))
    jobs.append(
        (
            "iso-primes",
            singular_ring()
            + ideal_str("I", GENS["Iso"])
            + "list L = minAssGTZ(I); int i; string ds;\n"
            + 'for(i=1;i<=size(L);i++){ds = ds + string(dim(std(L[i]))) + ",";}\n'
            '"@@primes " + string(size(L)) + " " + ds;\n',
        )
    )
    # fiber of X_+ over d = n0 (and of X_- over s = n0): s in n0-perp with rank [s; n0; s x n0] <= 2
    ctx7 = flint.fmpq_mpoly_ctx.get(("x", 7), "degrevlex")
    sv = list(ctx7.gens())
    n0 = [int(x) for x in N_VEC]
    rows3: list[list[Any]] = [sv, n0, cross(sv, n0)]
    fgens: list[Any] = [eta2(sv, n0)]
    for cols in itertools.combinations(range(7), 3):
        fgens.append(_det([[rows3[r][c] for c in cols] for r in range(3)]))
    fgens = [f for f in fgens if not f.is_zero()]
    fscript = "ring R = 0,(x0,x1,x2,x3,x4,x5,x6),dp;\n" + ideal_str("F", fgens)
    fscript += 'list L = minAssGTZ(F); "@@primes " + string(size(L));\n"@@dim " + string(dim(std(L[1])));\n'
    fscript += "ideal SL = std(L[1]); int lin = 1; int i; for(i=1;i<=size(SL);i++){ if (deg(SL[i])!=1) {lin=0;} }\n"
    fscript += '"@@linear " + string(lin);\n'
    jobs.append(("fiber", fscript))
    # W8 n E8bar = B9 and W8 n V = V n B9 = VB: a power of every generator of the target lies in the sum, and the sum
    # lies in the target ideal
    for name, a, b, target in (("W8cE8", "W8", "E8bar", "B9"), ("W8cV", "W8", "V", "VB"), ("VcB9", "V", "B9", "VB")):
        sc = singular_ring() + ideal_str("A", GENS[a]) + ideal_str("B", GENS[b]) + ideal_str("T", GENS[target])
        # radical membership by powers: the least k <= 4 with f^k in A + B for every generator f of T
        sc += "ideal SS = std(A + B);\nint kmax = 0; int i; int k; int found;\n"
        sc += "for (i=1;i<=size(T);i++){ found = 0;\n"
        sc += "  for (k=1;k<=4;k++){ if (found==0) { if (reduce(T[i]^k, SS)==0) { found = k; } } }\n"
        sc += "  if (found==0) { kmax = 99; } else { if (found > kmax) { kmax = found; } } }\n"
        sc += '"@@target_power_in_sum " + string(kmax);\n"@@sum_in_target " + string(size(reduce(A + B, std(T))));\n'
        jobs.append((f"cap|{name}", sc))
    # nullity 4: dimension of the Jacobian locus of G and of the dependence locus of dQ, dG on V(Q) n V(G)
    q, g = GENS["VQ"][0], GENS["VG"][0]
    jac_g = [g.derivative(k) for k in range(15)]
    jobs.append(("singVG", singular_ring() + ideal_str("I", [g, *jac_g]) + '"@@dim " + string(dim(std(I)));\n'))
    mins = [
        q.derivative(i) * g.derivative(j) - q.derivative(j) * g.derivative(i)
        for i, j in itertools.combinations(range(15), 2)
    ]
    jobs.append(("depQG", singular_ring() + ideal_str("I", [q, g, *mins]) + '"@@dim " + string(dim(std(I)));\n'))
    jobs.append(("QG", singular_ring() + ideal_str("I", [q, g]) + '"@@dim " + string(dim(std(I)));\n'))
    start = time.time()
    res = singular_batch(jobs)
    dims = {x: int(res[f"dim|{x}"][0]["dim"]) for x in [*CLOSURES, "VQ", "VG"]}
    dims_ok = all(dims[x] == DIMS[x] for x in CLOSURES) and dims["VQ"] == 14 and dims["VG"] == 14
    iso_primes = res["iso-primes"][0]["primes"]
    fiber = res["fiber"][0]
    caps = {
        k: {t: int(res[f"cap|{k}"][0][t]) for t in ("target_power_in_sum", "sum_in_target")}
        for k in ("W8cE8", "W8cV", "VcB9")
    }
    caps_ok = all(c["sum_in_target"] == 0 and 1 <= c["target_power_in_sum"] <= 4 for c in caps.values())
    sing_vg = int(res["singVG"][0]["dim"])
    dep = int(res["depQG"][0]["dim"])
    qg = int(res["QG"][0]["dim"])
    # X_+ reaches V^a_+ (and X_- reaches V^a_-) along an explicit curve with d != 0 (s != 0)
    curve_ok = True
    for eps in (Fraction(1), Fraction(1, 2), Fraction(1, 7)):
        zp = join_z(vadd((1, e(1)), (eps, A_VEC)), 0, vadd((1, e(1)), (-eps, A_VEC)))
        zm = join_z(vadd((1, e(1)), (eps, A_VEC)), 0, vadd((-1, e(1)), (eps, A_VEC)))
        curve_ok &= membership(zp)["X+"] and not membership(zp)["Va+"]
        curve_ok &= membership(zm)["X-"] and not membership(zm)["Va-"]
    ok = (
        dims_ok
        and iso_primes.startswith("1 ")
        and fiber["primes"] == "1"
        and fiber["dim"] == "4"
        and caps_ok
        and sing_vg == 12
        and dep <= 11
        and qg == 13
        and curve_ok
    )
    return {
        "closure_dims": dims,
        "closure_dims_match": dims_ok,
        "iso_minimal_primes_over_Q": iso_primes,
        "fiber_of_X_pm_over_null_vector": {
            "primes": int(fiber["primes"]),
            "dim": int(fiber["dim"]),
            "linear": fiber["linear"] == "1",
        },
        "curve_into_Va_pm": curve_ok,
        "intersections": caps,
        "dim_V(G,dG)": sing_vg,
        "dim_dependence_locus_on_V(Q,G)": dep,
        "dim_V(Q,G)": qg,
        "seconds": round(time.time() - start, 1),
        "pass": ok,
    }


# ---------------------------------------------------------------------------------------------------------------------
# Controls and main


def check_controls() -> dict[str, Any]:
    """Mutations that must fail: a compact rotation is no symmetry of Q; swapped representatives fail classification."""
    rot = ",".join([*[f"x{k + 8}" for k in range(7)], "x7", *[f"-x{k}" for k in range(7)]])
    script = singular_ring() + ideal_str("I", GENS["VQ"]) + f"map ro = R, {rot};\n"
    script += '"@@rotation " + string(size(reduce(ro(I), std(I))));\n'
    _name, out, _secs = run_singular(("control-rotation", script))
    rotation_fails = int(tagged(out)["rotation"]) > 0
    swapped = dict(EXPECTED)
    swapped["Va+"], swapped["Va-"] = EXPECTED["Va-"], EXPECTED["Va+"]
    swapped_fails = all(
        classify(rank_cz(REPS[o]), orbit_dim(REPS[o]), pattern(REPS[o]), swapped) is None for o in ("Va+", "Va-")
    )
    ok = rotation_fails and swapped_fails
    return {"rotation_breaks_Q": rotation_fails, "swapped_Va_patterns_rejected": swapped_fails, "pass": ok}


def _timed(fn: Callable[[], dict[str, Any]]) -> dict[str, Any]:
    start = time.time()
    res = fn()
    res["runtime_s"] = round(time.time() - start, 1)
    return res


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    start = time.time()
    singular_version = subprocess.run(
        [SINGULAR, "-v", "--no-rc"], capture_output=True, text=True, check=False, stdin=subprocess.DEVNULL
    ).stdout.splitlines()[0]
    result: dict[str, Any] = {
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "versions": {
            "python": platform.python_version(),
            "python_flint": flint.__version__,
            "singular": singular_version,
        },
        "workers": parallel.workers(),
    }
    result["tables"] = _timed(check_tables)
    result["derivations"] = _timed(check_derivations)
    result["identities"] = _timed(check_identities)
    result["symmetry"] = _timed(check_symmetry)
    result["representatives"] = _timed(check_representatives)
    result["global"] = _timed(check_singular_global)
    result["search"] = _timed(check_search)
    result["germs"] = _timed(check_germs)
    result["x0_link"] = _timed(check_x0)
    result["controls"] = _timed(check_controls)
    result["total_s"] = round(time.time() - start, 1)
    keys = ("identities", "symmetry", "representatives", "global", "germs", "x0_link", "controls")
    result["pass"] = all(result[k]["pass"] for k in keys) and result["search"]["pass_char0"]
    Path(args.out).write_text(json.dumps(result, indent=1, sort_keys=False) + "\n", encoding="utf-8")
    print(f"pass={result['pass']} total_s={result['total_s']}")
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
