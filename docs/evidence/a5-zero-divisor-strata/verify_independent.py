"""Independent verification of the A_5 zero-divisor strata claims of a5_zero_divisor_strata.py.

Every product comes from gororoba_quantum/cd_core.py: the 32 x 32 left-multiplication matrices of A_5, the 15 x 15
Im-blocks S_k of left multiplication by e_k in A_4, and the octonion table, all read from left_mult_matrix_exact, with
the tables re-checked against cd_multiply_exact. The script imports nothing from scripts/a5_zero_divisor_strata.py.

Conventions. A doubly pure y has y_0 = y_16 = 0 and z_k = y_k + i y_(16+k), k = 1..15; u = z_1..z_7, mu = z_8,
v = z_9..z_15; dot products are complex bilinear; U = u.u, V = v.v, W = u.v, Q = U + mu^2 + V, Delta = U V - W^2,
G = Q^2 - 4 Delta; C_z = sum_k z_k S_k. Piece tests use the original coordinates and the cd_core octonion product:
- W8: mu = 0, U = V, W = 0;  V: rank [u; v] <= 1, Q = 0;  B9: mu = 0, U = V = W = 0, Im(u v) = 0;
- N+: mu = 0, v = i u, U = 0;  N-: mu = 0, v = -i u, U = 0;
- Ehat: Q = 0, Delta = 0, rank [u; v; Im(u v)] <= 2. Ehat is closed and contains E8 (a plane span(n, e) with n
  null, e.e = -1, n an eigenvector of e x -, and Q = 0), so it contains E8-bar: a nullity-8 point outside W8 u Ehat
  refutes R_8 = W8 u E8-bar. E8i (Ehat with a 2-plane of Gram rank exactly 1) is the intrinsic E8 family.

Exact rank of L_y over Q decides every nullity; rank_C C_z comes from the realification [[A, -B], [B, A]]. The Zariski
tangent space of R_k at a point where rank C_z = r is {w : x^T C_w x' = 0 for x, x' in ker C_z}, because the skew
matrices of rank <= r form a variety smooth at rank exactly r with that tangent space.

Randomness. Every random value comes from two ANU QRNG draws of 1024 uint16 values, each index used once:
- DRAW_A indices 0..119: eight integer points z in [0, 65535]^15 for the Schwartz-Zippel identity tests;
- DRAW_A indices 120..139: one numpy PCG64 seed per random point family, in FAMILIES order (20 families);
- DRAW_A indices 200..227: two integer pairs (x, w) in [0, 65535]^7 for the double-cross identity;
- DRAW_B index 0: seed of the B9-to-E8 curve parameters; indices 1..4: seeds of the F_p full-space samples
  (p = 7 and 13, two batches each); index 5: seed of the float search starts.

Usage (--self-test runs the four mutation controls):
    "$PYTHON" -B docs/evidence/a5-zero-divisor-strata/verify_independent.py --self-test
    "$PYTHON" -B docs/evidence/a5-zero-divisor-strata/verify_independent.py \
        --out docs/evidence/a5-zero-divisor-strata/verification.json
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
import time
from collections import Counter
from collections.abc import Callable, Sequence
from fractions import Fraction
from pathlib import Path
from typing import Any

import flint
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import parallel  # noqa: E402
from cd_core import cd_multiply_exact, left_mult_matrix_exact  # noqa: E402

DRAW_A = "docs/evidence/anu_qrng/draw-2026-10-26T012526Z.json"
DRAW_B = "docs/evidence/anu_qrng/draw-2026-10-26T012529Z.json"
SZ_POINTS = 8
FAMILY_SEED_BASE = 120


def qrng_values(path: str) -> list[int]:
    record = json.loads((ROOT / path).read_text(encoding="utf-8"))
    return [int(x) for x in json.loads(record["raw"])["data"]]


QA = qrng_values(DRAW_A)
QB = qrng_values(DRAW_B)

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


SIGN32 = sign_table(32)
SIGN16 = sign_table(16)
OCT = sign_table(8)
DP = [k for k in range(1, 32) if k != 16]  # doubly pure coordinates of y


class Gq:
    """Exact Gaussian rational."""

    __slots__ = ("im", "re")

    def __init__(self, re: Any = 0, im: Any = 0) -> None:
        self.re = Fraction(re)
        self.im = Fraction(im)

    @staticmethod
    def of(x: Any) -> Gq:
        return x if isinstance(x, Gq) else Gq(x)

    def __add__(self, o: Any) -> Any:
        if isinstance(o, Dual):
            return NotImplemented
        o = Gq.of(o)
        return Gq(self.re + o.re, self.im + o.im)

    __radd__ = __add__

    def __sub__(self, o: Any) -> Any:
        if isinstance(o, Dual):
            return NotImplemented
        o = Gq.of(o)
        return Gq(self.re - o.re, self.im - o.im)

    def __rsub__(self, o: Any) -> Any:
        return Gq.of(o) - self

    def __mul__(self, o: Any) -> Any:
        if isinstance(o, Dual):
            return NotImplemented
        o = Gq.of(o)
        return Gq(self.re * o.re - self.im * o.im, self.re * o.im + self.im * o.re)

    __rmul__ = __mul__

    def __neg__(self) -> Gq:
        return Gq(-self.re, -self.im)

    def __truediv__(self, o: Any) -> Any:
        if isinstance(o, Dual):
            return NotImplemented
        o = Gq.of(o)
        d = o.re * o.re + o.im * o.im
        if d == 0:
            raise ZeroDivisionError("Gaussian division by zero")
        return Gq((self.re * o.re + self.im * o.im) / d, (self.im * o.re - self.re * o.im) / d)

    def __rtruediv__(self, o: Any) -> Any:
        return Gq.of(o) / self

    def __eq__(self, o: object) -> bool:
        if isinstance(o, (int, Fraction)):
            return self.im == 0 and self.re == o
        if isinstance(o, Gq):
            return self.re == o.re and self.im == o.im
        return NotImplemented

    def __hash__(self) -> int:
        return hash((self.re, self.im))

    def __bool__(self) -> bool:
        return bool(self.re) or bool(self.im)

    def __repr__(self) -> str:
        return f"({self.re}+{self.im}i)"


class Dual:
    """Forward-mode derivative over Gq: value and gradient with respect to the family parameters."""

    __slots__ = ("d", "v")

    def __init__(self, v: Gq, d: tuple[Gq, ...]) -> None:
        self.v = v
        self.d = d

    def _c(self, o: Any) -> Dual:
        return o if isinstance(o, Dual) else Dual(Gq.of(o), tuple(Gq() for _ in self.d))

    def __add__(self, o: Any) -> Dual:
        o = self._c(o)
        return Dual(self.v + o.v, tuple(a + b for a, b in zip(self.d, o.d, strict=True)))

    __radd__ = __add__

    def __sub__(self, o: Any) -> Dual:
        o = self._c(o)
        return Dual(self.v - o.v, tuple(a - b for a, b in zip(self.d, o.d, strict=True)))

    def __rsub__(self, o: Any) -> Dual:
        return self._c(o) - self

    def __mul__(self, o: Any) -> Dual:
        o = self._c(o)
        return Dual(self.v * o.v, tuple(a * o.v + self.v * b for a, b in zip(self.d, o.d, strict=True)))

    __rmul__ = __mul__

    def __neg__(self) -> Dual:
        return Dual(-self.v, tuple(-a for a in self.d))

    def __truediv__(self, o: Any) -> Dual:
        o = self._c(o)
        den = o.v * o.v
        return Dual(self.v / o.v, tuple((a * o.v - self.v * b) / den for a, b in zip(self.d, o.d, strict=True)))

    def __rtruediv__(self, o: Any) -> Dual:
        return self._c(o) / self


IU = Gq(0, 1)


def value(x: Any) -> Any:
    return x.v if isinstance(x, Dual) else x


# ---------------------------------------------------------------------------------------------------------------------
# Generic vector algebra (scalars: int, complex, Gq or Dual)


def dot(a: Sequence[Any], b: Sequence[Any]) -> Any:
    total: Any = 0
    for x, y in zip(a, b, strict=True):
        total = total + x * y
    return total


def lin(*terms: tuple[Any, Sequence[Any]]) -> list[Any]:
    n = len(terms[0][1])
    out: list[Any] = [0] * n
    for c, vec in terms:
        for j in range(n):
            out[j] = out[j] + c * vec[j]
    return out


def cross(a: Sequence[Any], b: Sequence[Any]) -> list[Any]:
    """Im(a b) for pure octonions a, b given by their 7 imaginary coordinates, from the cd_core table."""
    out: list[Any] = [0] * 7
    for p in range(1, 8):
        if a[p - 1] == 0:
            continue
        for q in range(1, 8):
            if p != q:
                out[(p ^ q) - 1] = out[(p ^ q) - 1] + OCT[p][q] * a[p - 1] * b[q - 1]
    return out


def split(z: Sequence[Any]) -> tuple[list[Any], Any, list[Any]]:
    return list(z[:7]), z[7], list(z[8:15])


def invariants(z: Sequence[Any]) -> dict[str, Any]:
    u, mu, v = split(z)
    uu, vv, uv = dot(u, u), dot(v, v), dot(u, v)
    q = uu + mu * mu + vv
    delta = uu * vv - uv * uv
    return {"U": uu, "V": vv, "W": uv, "mu": mu, "Q": q, "Delta": delta, "G": q * q - 4 * delta}


def minors_zero(rows: Sequence[Sequence[Any]], size: int) -> bool:
    n = len(rows[0])
    for cols in itertools.combinations(range(n), size):
        sub = [[r[c] for c in cols] for r in rows]
        if size == 2:
            det = sub[0][0] * sub[1][1] - sub[0][1] * sub[1][0]
        else:
            det = (
                sub[0][0] * (sub[1][1] * sub[2][2] - sub[1][2] * sub[2][1])
                - sub[0][1] * (sub[1][0] * sub[2][2] - sub[1][2] * sub[2][0])
                + sub[0][2] * (sub[1][0] * sub[2][1] - sub[1][1] * sub[2][0])
            )
        if det != 0:
            return False
    return True


def pieces(z: Sequence[Any]) -> dict[str, bool]:
    """Membership of z in the claimed pieces, from their equations in original coordinates."""
    u, mu, v = split(z)
    inv = invariants(z)
    c = cross(u, v)
    dependent = minors_zero([u, v], 2)
    gram_zero = inv["U"] == 0 and inv["V"] == 0 and inv["W"] == 0
    ehat = inv["Q"] == 0 and inv["Delta"] == 0 and minors_zero([u, v, c], 3)
    iu = [IU * x if isinstance(x, Gq) else 1j * x for x in u]
    return {
        "W8": mu == 0 and inv["U"] == inv["V"] and inv["W"] == 0,
        "V": dependent and inv["Q"] == 0,
        "B9": mu == 0 and gram_zero and all(x == 0 for x in c),
        "Np": mu == 0 and inv["U"] == 0 and all(a == b for a, b in zip(v, iu, strict=True)),
        "Nm": mu == 0 and inv["U"] == 0 and all(a == -b for a, b in zip(v, iu, strict=True)),
        "Ehat": ehat,
        "E8i": ehat and not dependent and not gram_zero,
        "VQ": inv["Q"] == 0,
        "VG": inv["G"] == 0,
    }


# ---------------------------------------------------------------------------------------------------------------------
# Exact linear algebra


def _fq(x: Fraction) -> flint.fmpq:
    return flint.fmpq(x.numerator, x.denominator)


def realify(rows: Sequence[Sequence[Any]]) -> list[list[Fraction]]:
    rows = [[Gq.of(x) for x in r] for r in rows]
    out = []
    for r in rows:
        out.append([x.re for x in r] + [-x.im for x in r])
    for r in rows:
        out.append([x.im for x in r] + [x.re for x in r])
    return out


def qrank(rows: Sequence[Sequence[Fraction]]) -> int:
    if not rows:
        return 0
    return int(flint.fmpq_mat(len(rows), len(rows[0]), [_fq(x) for r in rows for x in r]).rank())


def crank(rows: Sequence[Sequence[Gq]]) -> int:
    if not rows:
        return 0
    return qrank(realify(rows)) // 2


def ckernel(rows: Sequence[Sequence[Gq]]) -> list[list[Gq]]:
    """A complex spanning set of the kernel of a complex matrix, from the rational kernel of its realification."""
    real = realify(rows)
    n = len(rows[0])
    ints = []
    for r in real:
        den = 1
        for x in r:
            den = den * x.denominator // _gcd(den, x.denominator)
        ints.append([int(x * den) for x in r])
    mat = flint.fmpz_mat(len(ints), 2 * n, [x for r in ints for x in r])
    basis, nullity = mat.nullspace()
    vecs = []
    for col in range(int(nullity)):
        entries = [Fraction(int(basis[j, col])) for j in range(2 * n)]
        vecs.append([Gq(entries[j], entries[n + j]) for j in range(n)])
    return vecs


def _gcd(a: int, b: int) -> int:
    while b:
        a, b = b, a % b
    return a


def cz_rows(z: Sequence[Any]) -> list[list[Any]]:
    """C_z = sum_k z_k S_k, S_k the Im-block of L_(e_k) in A_4: entry (a, b) = sign(a XOR b, b) z_(a XOR b)."""
    rows = []
    for a in range(1, 16):
        row: list[Any] = []
        for b in range(1, 16):
            k = a ^ b
            row.append(0 if k == 0 else SIGN16[k][b] * z[k - 1])
        rows.append(row)
    return rows


def y_of(z: Sequence[Gq]) -> list[Fraction]:
    y = [Fraction(0)] * 32
    for k in range(1, 16):
        y[k] = z[k - 1].re
        y[16 + k] = z[k - 1].im
    return y


def nullity_L(y: Sequence[Fraction]) -> int:
    entries = []
    for r in range(32):
        for c in range(32):
            entries.append(_fq(y[r ^ c] * SIGN32[r ^ c][c]))
    return 32 - int(flint.fmpq_mat(32, 32, entries).rank())


def rank_cz(z: Sequence[Gq]) -> int:
    return crank([[Gq.of(x) for x in r] for r in cz_rows(z)])


def tangent(z: Sequence[Gq]) -> dict[str, int]:
    """Zariski tangent dimension of R_k at z (k the nullity of z), with and without the mu-direction."""
    kernel = ckernel([[Gq.of(x) for x in r] for r in cz_rows(z)])
    rows = []
    for x, xp in itertools.combinations(kernel, 2):
        row = []
        for k in range(1, 16):
            total = Gq()
            for d in range(1, 16):
                c = k ^ d
                if c != 0:
                    total = total + x[c - 1] * SIGN16[k][d] * xp[d - 1]
            row.append(total)
        if any(row):
            rows.append(row)
    rank = crank(rows)
    mu_row = [Gq(1 if k == 8 else 0) for k in range(1, 16)]
    rank_mu = crank([*rows, mu_row])
    mu_in_tangent = all(not r[7] for r in rows)
    return {"tangent": 15 - rank, "tangent_mu0": 15 - rank_mu, "mu_direction_in_tangent": int(mu_in_tangent)}


def jacobian_rank(family: Callable[[list[Any]], list[Any]], params: list[Gq]) -> int:
    n = len(params)
    duals = [Dual(p, tuple(Gq(1 if j == i else 0) for j in range(n))) for i, p in enumerate(params)]
    out = family(duals)
    rows = []
    for x in out:
        if isinstance(x, Dual):
            rows.append(list(x.d))
        else:
            rows.append([Gq() for _ in range(n)])
    return crank(rows)


# ---------------------------------------------------------------------------------------------------------------------
# Point families (original coordinates); every parameter vector is a list of Gaussian integers


E1 = [Gq(1 if j == 0 else 0) for j in range(7)]
N0 = [Gq(1), IU] + [Gq() for _ in range(5)]


def nullvec(t: Sequence[Any], n0: Sequence[Any]) -> list[Any]:
    """(t.t) n0 - 2 (n0.t) t is null for null n0."""
    return lin((dot(t, t), n0), (-2 * dot(n0, t), t))


def house(t: Sequence[Any], x: Sequence[Any]) -> list[Any]:
    return lin((1, x), (-2 * dot(t, x) / dot(t, t), t))


def orth(ts: Sequence[Sequence[Any]], x: Sequence[Any]) -> list[Any]:
    out = list(x)
    for t in ts:
        out = house(t, out)
    return out


def unit7(t: Sequence[Any]) -> list[Any]:
    return house(t, E1)


def ev(n: int, j: int) -> list[Gq]:
    return [Gq(1 if i == j else 0) for i in range(n)]


def assemble(u: Sequence[Any], mu: Any, v: Sequence[Any]) -> list[Any]:
    return [*u, mu, *v]


def pyth(kappa: Any, r: Any, q: Any) -> tuple[Any, Any, Any]:
    """(X, Y, M) with X^2 + Y^2 = M^2."""
    return kappa * (r * r - q * q), kappa * 2 * r * q, kappa * (r * r + q * q)


def fam_generic(p: list[Any]) -> list[Any]:
    return list(p[:15])


def fam_vq(p: list[Any]) -> list[Any]:
    n0 = [Gq(1), IU] + [Gq() for _ in range(13)]
    return nullvec(p[:15], n0)


def fam_vq_mu0(p: list[Any]) -> list[Any]:
    n0 = [Gq(1), IU] + [Gq() for _ in range(12)]
    w = nullvec(p[:14], n0)
    return [*w[:7], Gq(), *w[7:]]


def _frame(p: list[Any]) -> tuple[list[Any], list[Any], list[Any], list[Any]]:
    ts = [p[0:7], p[7:14], p[14:21]]
    return orth(ts, ev(7, 0)), orth(ts, ev(7, 1)), orth(ts, ev(7, 2)), orth(ts, ev(7, 3))


def fam_vg(p: list[Any]) -> list[Any]:
    f1, f2, _, _ = _frame(p)
    s, kappa, r, q = p[21:25]
    x, y, m = pyth(kappa, r, q)
    t = s - x
    return assemble(lin((s, f1)), IU * m, lin((y, f1), (t, f2)))


def fam_vg_mu0(p: list[Any]) -> list[Any]:
    f1, f2, _, _ = _frame(p)
    s, kappa = p[21:23]
    t = s - kappa
    return assemble(lin((s, f1)), Gq(), lin((IU * kappa, f1), (t, f2)))


def fam_vqg_p3c(p: list[Any]) -> list[Any]:
    f1, f2, f3, _ = _frame(p)
    n = lin((1, f2), (IU, f3))
    kappa, r, q, c = p[21:25]
    x, y, m = pyth(kappa, r, q)
    return assemble(lin((x, f1)), IU * m, lin((y, f1), (c, n)))


def fam_p2_q0(p: list[Any]) -> list[Any]:
    f1, f2, _, _ = _frame(p)
    n0 = [Gq(1), IU, Gq(), Gq(), Gq()]
    a, b, c, d, m = nullvec(p[21:26], n0)
    return assemble(lin((a, f1), (b, f2)), m, lin((c, f1), (d, f2)))


def fam_w8_hyp(p: list[Any]) -> list[Any]:
    x = nullvec(p[0:7], N0)
    w = nullvec(p[7:14], N0)
    return assemble(lin((Fraction(1, 2), x), (Fraction(1, 2), w)), Gq(), lin((IU / 2, x), (-IU / 2, w)))


def _iso_pair(p: list[Any]) -> tuple[list[Any], list[Any]]:
    ts = [p[0:7], p[7:14], p[14:21]]
    x1 = orth(ts, lin((1, ev(7, 0)), (IU, ev(7, 1))))
    w1 = orth(ts, lin((1, ev(7, 2)), (IU, ev(7, 3))))
    a, b, c, d = p[21:25]
    return lin((a, x1), (b, w1)), lin((c, x1), (d, w1))


def fam_w8_iso(p: list[Any]) -> list[Any]:
    x, w = _iso_pair(p)
    return assemble(lin((Fraction(1, 2), x), (Fraction(1, 2), w)), Gq(), lin((IU / 2, x), (-IU / 2, w)))


def fam_iso_mu(p: list[Any]) -> list[Any]:
    x, w = _iso_pair(p)
    return assemble(lin((Fraction(1, 2), x), (Fraction(1, 2), w)), p[25], lin((IU / 2, x), (-IU / 2, w)))


def _e8_frame(p: list[Any]) -> tuple[list[Any], list[Any]]:
    e = lin((IU, unit7(p[0:7])))
    x = p[7:14]
    y = lin((1, x), (-dot(x, e) / dot(e, e), e))
    n = lin((Fraction(1, 2), y), (Fraction(1, 2), cross(e, y)))
    return e, n


def fam_e8(p: list[Any]) -> list[Any]:
    e, n = _e8_frame(p)
    a, c, kappa, r, q = p[14:19]
    b, d, m = pyth(kappa, r, q)
    return assemble(lin((a, n), (b, e)), m, lin((c, n), (d, e)))


def fam_e8_mu0(p: list[Any]) -> list[Any]:
    e, n = _e8_frame(p)
    a, c, b = p[14:17]
    return assemble(lin((a, n), (b, e)), Gq(), lin((c, n), (IU * b, e)))


def fam_p3a_qne0(p: list[Any]) -> list[Any]:
    e, n = _e8_frame(p)
    a, b, c, d, m = p[14:19]
    return assemble(lin((a, n), (b, e)), m, lin((c, n), (d, e)))


def fam_v(p: list[Any]) -> list[Any]:
    w = unit7(p[0:7])
    kappa, r, q = p[7:10]
    a, b, m = pyth(kappa, r, q)
    return assemble(lin((a, w)), IU * m, lin((b, w)))


def _special_plane(p: list[Any]) -> tuple[list[Any], list[Any]]:
    n = nullvec(p[0:7], N0)
    y0 = p[7:14]
    y = lin((1, y0), (-dot(n, y0) / n[0], E1))
    return n, cross(n, y)


def fam_b9(p: list[Any]) -> list[Any]:
    n, x = _special_plane(p)
    a, b, c, d = p[14:18]
    return assemble(lin((a, n), (b, x)), Gq(), lin((c, n), (d, x)))


def fam_vb9(p: list[Any]) -> list[Any]:
    n = nullvec(p[0:7], N0)
    return assemble(lin((p[7], n)), Gq(), lin((p[8], n)))


def fam_axis_p(p: list[Any]) -> list[Any]:
    return assemble(p[0:7], Gq(), lin((IU, p[0:7])))


def fam_axis_m(p: list[Any]) -> list[Any]:
    return assemble(p[0:7], Gq(), lin((-IU, p[0:7])))


def fam_np(p: list[Any]) -> list[Any]:
    n = nullvec(p[0:7], N0)
    return assemble(n, Gq(), lin((IU, n)))


def fam_nm(p: list[Any]) -> list[Any]:
    n = nullvec(p[0:7], N0)
    return assemble(n, Gq(), lin((-IU, n)))


# name, family, parameter count, points, expected nullity, required memberships, forbidden memberships,
# expected tangent dimension (None: not a claim), expected lower bound (None: not a claim)
FAMILIES: list[tuple[str, Callable[[list[Any]], list[Any]], int, int, int, tuple[str, ...], tuple[str, ...], Any, Any]]
FAMILIES = [
    ("generic", fam_generic, 15, 6, 0, (), ("VQ", "VG"), None, 15),
    ("V(Q) generic", fam_vq, 15, 6, 4, ("VQ",), ("VG",), 14, 14),
    ("V(G) generic", fam_vg, 25, 6, 4, ("VG",), ("VQ",), 14, 14),
    ("V(Q) n V(G), Gram rank 1 unaligned", fam_vqg_p3c, 25, 6, 4, ("VQ", "VG"), ("Ehat", "W8"), None, None),
    ("V(Q), nondegenerate plane", fam_p2_q0, 26, 6, 4, ("VQ",), ("VG",), None, None),
    ("W8 hyperbolic", fam_w8_hyp, 14, 12, 8, ("W8", "VG"), ("VQ", "Ehat", "V", "B9"), 12, 12),
    ("W8 generic isotropic", fam_w8_iso, 25, 12, 8, ("W8", "VQ", "VG"), ("Ehat", "V", "B9"), 12, None),
    ("E8", fam_e8, 19, 8, 8, ("E8i", "Ehat", "VQ", "VG"), ("W8", "V", "B9"), 11, 11),
    ("V", fam_v, 10, 8, 12, ("V", "Ehat", "VQ", "VG"), ("B9", "W8"), 8, 8),
    ("B9", fam_b9, 18, 8, 12, ("B9", "W8", "Ehat", "VQ", "VG"), ("V",), 9, 9),
    ("V n B9", fam_vb9, 9, 6, 12, ("V", "B9", "W8"), ("Np", "Nm"), None, 7),
    ("{a,0} axis +", fam_axis_p, 7, 4, 12, ("V",), ("B9", "W8"), 8, 7),
    ("{a,0} axis -", fam_axis_m, 7, 4, 12, ("V",), ("B9", "W8"), 8, 7),
    ("N+", fam_np, 7, 6, 16, ("Np", "V", "B9", "W8"), ("Nm",), 6, 6),
    ("N-", fam_nm, 7, 6, 16, ("Nm", "V", "B9", "W8"), ("Np",), 6, 6),
    ("isotropic plane, mu != 0", fam_iso_mu, 26, 4, 0, (), ("VQ", "VG"), None, None),
    ("Gram rank 1 aligned, Q != 0", fam_p3a_qne0, 19, 4, 0, (), ("VQ", "VG"), None, None),
    ("E8 n {mu = 0}", fam_e8_mu0, 17, 6, 8, ("E8i",), ("W8",), 11, 10),
    ("V(G) n {mu = 0}", fam_vg_mu0, 23, 4, 4, ("VG",), ("VQ",), 14, 13),
    ("V(Q) n {mu = 0}", fam_vq_mu0, 14, 4, 4, ("VQ",), ("VG",), 14, 13),
]


def family_params() -> list[tuple[int, list[list[tuple[int, int]]]]]:
    """Gaussian-integer parameters of every family point, drawn first in FAMILIES order from QRNG-seeded PCG64."""
    out = []
    for index, (_, _, nparams, npoints, *_rest) in enumerate(FAMILIES):
        rng = np.random.Generator(np.random.PCG64(QA[FAMILY_SEED_BASE + index]))
        points = []
        for _ in range(npoints * 3):  # spares for degenerate draws
            raw = rng.integers(-4, 5, size=(nparams, 2))
            points.append([(int(a), int(b)) for a, b in raw])
        out.append((index, points))
    return out


def evaluate_family(item: tuple[int, list[list[tuple[int, int]]]]) -> dict[str, Any]:
    index, candidates = item
    name, family, _, npoints, nullity, required, forbidden, tan_expected, lower_expected = FAMILIES[index]
    rows: list[dict[str, Any]] = []
    for raw in candidates:
        if len(rows) == npoints:
            break
        params = [Gq(a, b) for a, b in raw]
        try:
            z = [Gq.of(value(x)) for x in family(params)]
        except ZeroDivisionError:
            continue
        if not any(z):
            continue
        y = y_of(z)
        nul = nullity_L(y)
        rc = rank_cz(z)
        mem = pieces(z)
        row: dict[str, Any] = {"nullity": nul, "rank_C": rc, "identity_holds": nul == 28 - 2 * rc}
        row["members"] = sorted(k for k, ok in mem.items() if ok)
        row["required_ok"] = all(mem[k] for k in required)
        row["forbidden_ok"] = not any(mem[k] for k in forbidden)
        row["mu_zero"] = z[7] == 0
        if rc < 14:
            row.update(tangent(z))
        if lower_expected is not None:
            row["lower_bound"] = jacobian_rank(family, params)
        rows.append(row)
    ok = (
        len(rows) == npoints
        and all(r["nullity"] == nullity and r["identity_holds"] for r in rows)
        and all(r["required_ok"] and r["forbidden_ok"] for r in rows)
        and (tan_expected is None or all(r.get("tangent") == tan_expected for r in rows))
        and (lower_expected is None or max(r["lower_bound"] for r in rows) == lower_expected)
    )
    summary = {
        "family": name,
        "seed": {"draw": DRAW_A, "index": FAMILY_SEED_BASE + index, "value": QA[FAMILY_SEED_BASE + index]},
        "points": len(rows),
        "expected": {
            "nullity": nullity,
            "required": list(required),
            "forbidden": list(forbidden),
            "tangent": tan_expected,
            "lower_bound": lower_expected,
        },
        "nullities": sorted(Counter(r["nullity"] for r in rows).items()),
        "tangents": sorted(Counter(r.get("tangent") for r in rows if "tangent" in r).items()),
        "tangent_mu0": sorted(Counter(r.get("tangent_mu0") for r in rows if "tangent_mu0" in r).items()),
        "mu_direction_in_tangent": sorted(
            Counter(r.get("mu_direction_in_tangent") for r in rows if "mu_direction_in_tangent" in r).items()
        ),
        "lower_bounds": sorted(Counter(r["lower_bound"] for r in rows if "lower_bound" in r).items()),
        "member_sets": sorted(Counter(",".join(r["members"]) for r in rows).items()),
        "pass": ok,
    }
    return summary


# ---------------------------------------------------------------------------------------------------------------------
# Structural and polynomial identity checks


def table_checks() -> dict[str, Any]:
    """The tables agree with cd_multiply_exact; J = L_(e_16) and the L_(e_k) satisfy the doubly-pure identities."""
    oct_ok = all(
        cd_multiply_exact(8, _basis(8, p), _basis(8, q))[p ^ q] == OCT[p][q] for p in range(8) for q in range(8)
    )
    s16_ok = all(
        cd_multiply_exact(16, _basis(16, p), _basis(16, q))[p ^ q] == SIGN16[p][q] for p in range(16) for q in range(16)
    )

    def lmat(k: int) -> list[list[int]]:
        return [[SIGN32[r ^ c][c] if (r ^ c) == k else 0 for c in range(32)] for r in range(32)]

    def mm(a: list[list[int]], b: list[list[int]]) -> list[list[int]]:
        return [[sum(a[i][t] * b[t][j] for t in range(32)) for j in range(32)] for i in range(32)]

    j = lmat(16)
    ident = [[1 if r == c else 0 for c in range(32)] for r in range(32)]
    j2 = mm(j, j)
    j2_ok = all(j2[r][c] == -ident[r][c] for r in range(32) for c in range(32))
    skew_ok = True
    anti_ok = True
    for k in range(1, 32):
        lk = lmat(k)
        skew_ok &= all(lk[r][c] == -lk[c][r] for r in range(32) for c in range(32))
        if k != 16:
            a, b = mm(j, lk), mm(lk, j)
            anti_ok &= all(a[r][c] + b[r][c] == 0 for r in range(32) for c in range(32))
    # cross() against cd_multiply_exact on rational vectors built from QRNG-free fixed integers
    xa = [Fraction(v) for v in (0, 3, -1, 4, 1, -5, 9, 2)]
    xb = [Fraction(v) for v in (0, 6, 5, -3, 5, 8, -9, 7)]
    prod = cd_multiply_exact(8, xa, xb)
    cross_ok = cross(xa[1:], xb[1:]) == list(prod[1:])
    anti_oct = all(OCT[p][q] == -OCT[q][p] for p in range(1, 8) for q in range(1, 8) if p != q)
    return {
        "octonion_imaginary_units_anticommute": anti_oct,
        "octonion_table_matches_cd_multiply_exact": oct_ok,
        "sedenion_table_matches_cd_multiply_exact": s16_ok,
        "J_squared_is_minus_identity": j2_ok,
        "L_ek_skew_for_k_nonzero": skew_ok,
        "J_anticommutes_with_L_ek_for_k_not_0_16": anti_ok,
        "cross_matches_cd_multiply_exact": cross_ok,
        "pass": oct_ok and s16_ok and j2_ok and skew_ok and anti_ok and cross_ok and anti_oct,
    }


def sz_point(index: int) -> dict[str, Any]:
    """Integer z from QRNG values: characteristic polynomial, minimal relation and 14 x 14 cofactor identities."""
    z = QA[15 * index : 15 * index + 15]
    c = flint.fmpz_mat(15, 15, [x for r in cz_rows(z) for x in r])
    u, mu, v = z[:7], z[7], z[8:]
    uu, vv, uv = dot(u, u), dot(v, v), dot(u, v)
    q = uu + mu * mu + vv
    g = q * q - 4 * (uu * vv - uv * uv)
    lam = flint.fmpz_poly([0, 1])
    expected = lam * (lam**2 + q) ** 3 * (lam**4 + 2 * q * lam**2 + g) ** 2
    char_ok = c.charpoly() == expected
    ident = flint.fmpz_mat(15, 15, [1 if r == s else 0 for r in range(15) for s in range(15)])
    c2 = c * c
    relation = c * (c2 + ident * q) * (c2 * c2 + c2 * (2 * q) + ident * g)
    rel_ok = relation.is_zero()
    signs = []
    for j in range(15):
        keep = [t for t in range(15) if t != j]
        minor = flint.fmpz_mat(14, 14, [c[a, b] for a in keep for b in keep])
        det = minor.det()
        target = (q * g * z[j]) ** 2
        signs.append(1 if det == target else (-1 if det == -target else 0))
    return {"char_poly": char_ok, "minimal_relation": rel_ok, "cofactor_signs": signs, "Q_nonzero": q != 0}


def double_cross() -> dict[str, Any]:
    """x x (x x w) = (x.w) x - (x.x) w for the cd_core octonion cross product, a cubic identity over Z checked at two
    QRNG integer pairs (DRAW_A indices 200..227); with x.x = x.w = w.w = 0 it forces x x w in span(x, w) to be 0."""
    vals = QA[200:228]
    ok = True
    for j in range(2):
        x = vals[14 * j : 14 * j + 7]
        w = vals[14 * j + 7 : 14 * j + 14]
        lhs = cross(x, cross(x, w))
        rhs = lin((dot(x, w), x), (-dot(x, x), w))
        ok &= lhs == rhs
    return {"draw": DRAW_A, "indices": [200, 227], "identity_holds": ok, "pass": ok}


def identity_checks() -> dict[str, Any]:
    rows = parallel.ordered_map(sz_point, list(range(SZ_POINTS)), min_items=1)
    signs = [r["cofactor_signs"] for r in rows]
    consistent = all(0 not in s for s in signs) and all(s == signs[0] for s in signs)
    return {
        "points": SZ_POINTS,
        "draw": DRAW_A,
        "indices": [0, 15 * SZ_POINTS - 1],
        "char_poly_all": all(r["char_poly"] for r in rows),
        "minimal_relation_all": all(r["minimal_relation"] for r in rows),
        "cofactor_det_equals_sign_times_QGz_squared": consistent,
        "cofactor_signs": signs[0],
        "schwartz_zippel_bound_per_identity": f"(15/65536)^{SZ_POINTS}",
        "pass": all(r["char_poly"] and r["minimal_relation"] for r in rows) and consistent,
    }


def g_irreducibility() -> dict[str, Any]:
    """G in split coordinates z_k = i^popcount(k) z'_k has rational coefficients, is irreducible over Q and has a smooth
    rational zero; Q and G in the original coordinates are integer polynomials."""
    names = [f"w{k}" for k in range(1, 16)]
    ctx = flint.fmpq_mpoly_ctx.get(names, "lex")
    gens = ctx.gens()
    zero = ctx.from_dict({})
    unit = [(1, 0), (0, 1), (-1, 0), (0, -1)]

    def cmul(a: tuple[Any, Any], b: tuple[Any, Any]) -> tuple[Any, Any]:
        return (a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0])

    def cadd(a: tuple[Any, Any], b: tuple[Any, Any]) -> tuple[Any, Any]:
        return (a[0] + b[0], a[1] + b[1])

    z = []
    for k in range(1, 16):
        re, im = unit[k.bit_count() % 4]
        z.append((gens[k - 1] * re, gens[k - 1] * im))

    def cdot(a: list[Any], b: list[Any]) -> tuple[Any, Any]:
        total = (zero, zero)
        for x, y in zip(a, b, strict=True):
            total = cadd(total, cmul(x, y))
        return total

    u, mu, v = z[:7], z[7], z[8:]
    uu, vv, uv = cdot(u, u), cdot(v, v), cdot(u, v)
    q = cadd(cadd(uu, cmul(mu, mu)), vv)
    delta = cadd(cmul(uu, vv), cmul((-uv[0], -uv[1]), uv))
    qq = cmul(q, q)
    g = (qq[0] - 4 * delta[0], qq[1] - 4 * delta[1])
    real = q[1] == zero and g[1] == zero
    gs = g[0]
    factors = gs.factor()
    irreducible = len(factors[1]) == 1 and factors[1][0][1] == 1
    # smooth rational zero: u' = e'_1, mu' = 4, v' = 5 e'_1 + 2 e'_3
    point = [0] * 15
    point[0], point[7], point[8], point[10] = 1, 4, 5, 2
    pt = [flint.fmpq(x) for x in point]
    g_at = gs(*pt)
    grad = [gs.derivative(k)(*pt) for k in range(15)]
    return {
        "Q_and_G_real_in_split_coordinates": real,
        "G_terms": len(gs),
        "G_irreducible_over_Q": irreducible,
        "factorization_shape": [(str(f)[:40], m) for f, m in factors[1]],
        "smooth_zero": {"point": point, "G": int(g_at), "gradient_nonzero": any(x != 0 for x in grad)},
        "Q_hessian_rank_original": qrank([[Fraction(2 if i == j else 0) for j in range(15)] for i in range(15)]),
        "pass": real and irreducible and g_at == 0 and any(x != 0 for x in grad),
    }


# ---------------------------------------------------------------------------------------------------------------------
# Exhaustive integer search: doubly pure y in {-1, 0, 1}^30 with support <= 4


def _pos_tables() -> tuple[list[list[tuple[int, int]]], list[list[tuple[int, int, int]]]]:
    l32 = []
    for k in range(32):
        l32.append([(((k ^ c) * 32 + c), SIGN32[k][c]) for c in range(32)])
    cz = []
    for k in range(1, 16):
        cz.append([(a - 1, b - 1, SIGN16[k][b]) for b in range(1, 16) for a in [k ^ b] if a != 0])
    return l32, cz


L32POS, CZPOS = _pos_tables()


def classify_point(z: Sequence[Any], nullity: int, stats: Counter[str], bad: list[Any], tag: Any) -> None:
    mem = pieces(z)
    stats[f"nullity_{nullity}"] += 1
    if (nullity >= 4) != (mem["VQ"] or mem["VG"]):
        bad.append(("QG=0 iff nullity>=4", tag, nullity))
    if nullity >= 8 and not (mem["W8"] or mem["Ehat"]):
        bad.append(("nullity>=8 outside W8 u Ehat", tag, nullity))
    if nullity >= 12 and not (mem["V"] or mem["B9"]):
        bad.append(("nullity>=12 outside V u B9", tag, nullity))
    if nullity >= 16 and not (mem["Np"] or mem["Nm"]):
        bad.append(("nullity>=16 outside N+ u N-", tag, nullity))
    if nullity >= 20:
        bad.append(("nullity>=20", tag, nullity))
    if mem["W8"] and nullity < 8:
        bad.append(("W8 point with nullity<8", tag, nullity))
    if mem["E8i"] and nullity < 8:
        bad.append(("E8i point with nullity<8", tag, nullity))
    if (mem["V"] or mem["B9"]) and nullity < 12:
        bad.append(("V or B9 point with nullity<12", tag, nullity))
    if (mem["Np"] or mem["Nm"]) and nullity < 16:
        bad.append(("N point with nullity<16", tag, nullity))
    if nullity >= 8:
        key = "+".join(k for k in ("W8", "E8i", "Ehat", "V", "B9", "Np", "Nm") if mem[k])
        stats[f"n{nullity}:{key}"] += 1


def exhaustive_item(combo: tuple[int, ...]) -> tuple[dict[str, int], list[Any]]:
    stats: Counter[str] = Counter()
    bad: list[Any] = []
    for signs in itertools.product((1, -1), repeat=len(combo)):
        flat = [0] * 1024
        for k, s in zip(combo, signs, strict=True):
            for pos, sg in L32POS[k]:
                flat[pos] += s * sg
        nullity = 32 - int(flint.fmpz_mat(32, 32, flat).rank())
        re = [0] * 15
        im = [0] * 15
        for k, s in zip(combo, signs, strict=True):
            if k < 16:
                re[k - 1] = s
            else:
                im[k - 17] = s
        real = [0] * 900
        for k in range(15):
            if re[k] or im[k]:
                for a, b, sg in CZPOS[k]:
                    real[a * 30 + b] += re[k] * sg
                    real[(a + 15) * 30 + b + 15] += re[k] * sg
                    real[a * 30 + b + 15] -= im[k] * sg
                    real[(a + 15) * 30 + b] += im[k] * sg
        rank_c = int(flint.fmpz_mat(30, 30, real).rank()) // 2
        if nullity != 28 - 2 * rank_c:
            bad.append(("nullity identity", combo, signs, nullity, rank_c))
        z = [complex(re[k], im[k]) for k in range(15)]
        classify_point(z, nullity, stats, bad, (combo, signs))
    return dict(stats), bad


def exhaustive_search() -> dict[str, Any]:
    combos = [c for size in range(1, 5) for c in itertools.combinations(DP, size)]
    results = parallel.ordered_map(exhaustive_item, combos)
    stats: Counter[str] = Counter()
    bad: list[Any] = []
    for s, b in results:
        stats.update(s)
        bad.extend(b)
    return {
        "points": sum(2 ** len(c) for c in combos),
        "counts": dict(sorted(stats.items())),
        "violations": [str(b) for b in bad[:20]],
        "violation_count": len(bad),
        "pass": not bad,
    }


# ---------------------------------------------------------------------------------------------------------------------
# Witnesses of the local-dimension record


def witness_item(row: dict[str, Any]) -> dict[str, Any]:
    x = [Fraction(v) for v in row["x"]]
    nul = nullity_L(x)
    pure = x[0] == 0 and x[16] == 0
    out: dict[str, Any] = {"family": row["family"], "witness": row["witness"], "nullity": nul}
    out["recorded"] = row["nullity"]
    if pure:
        z = [Gq(x[k], x[16 + k]) for k in range(1, 16)]
        rc = rank_cz(z)
        mem = pieces(z)
        stats: Counter[str] = Counter()
        bad: list[Any] = []
        classify_point(z, nul, stats, bad, row["witness"])
        out.update({"rank_C": rc, "identity": nul == 28 - 2 * rc, "mu_zero": z[7] == 0, "violations": bad})
        out["members"] = sorted(k for k, ok in mem.items() if ok)
        if 0 < nul < 32:
            out.update(tangent(z))
    else:
        out.update({"identity": nul == 0, "violations": [] if nul == 0 else ["not doubly pure but singular"]})
    return out


def witness_checks() -> dict[str, Any]:
    record = json.loads((ROOT / "docs/evidence/rank_locus_local_dimension/result.json").read_text(encoding="utf-8"))
    rows = parallel.ordered_map(witness_item, record["rows"], min_items=1)
    ok = all(r["nullity"] == r["recorded"] and r["identity"] and not r["violations"] for r in rows)
    return {"rows": rows, "pass": ok}


# ---------------------------------------------------------------------------------------------------------------------
# B9 inside E8-bar: E8 curves ending at random B9 points


def b9_curve_item(raw: list[tuple[int, int]]) -> dict[str, Any] | None:
    p = [Gq(a, b) for a, b in raw]
    try:
        n, k = _special_plane(p)
    except ZeroDivisionError:
        return None
    # e0 with e0 . n = 0, e0 . k = 0 and Im(e0 n) = n: linear in e0
    rows = [list(n), list(k)]
    rhs = [Gq(), Gq()]
    for r in range(7):
        row = []
        for j in range(7):
            col = cross(ev(7, j), n)
            row.append(col[r])
        rows.append(row)
        rhs.append(n[r])
    aug = [[*r, b] for r, b in zip(rows, rhs, strict=True)]
    if crank(rows) != crank(aug):
        return {"solvable": False}
    e0 = solve_complex(rows, rhs)
    if dot(e0, e0) == 0:
        return {"solvable": True, "e0_null": True}
    # Q(s) = s^2 ((e0.e0)(beta^2 + delta^2) + m^2): beta^2 + delta^2 = -e0.e0 through (beta + i delta) = A,
    # (beta - i delta) = -e0.e0 / A, and m = e0.e0
    alpha, gamma, big_a = p[14:17]
    eps = dot(e0, e0)
    norm = -eps
    beta = (big_a + norm / big_a) / 2
    delta = (big_a - norm / big_a) / (2 * IU)
    m = eps

    def curve(s: Any) -> list[Any]:
        ks = lin((1, k), (s, e0))
        return assemble(lin((alpha, n), (beta, ks)), m * s, lin((gamma, n), (delta, ks)))

    samples = []
    for s in range(1, 9):
        z = [Gq.of(x) for x in curve(Gq(s))]
        mem = pieces(z)
        samples.append({"s": s, "rank_C": rank_cz(z), "E8i": mem["E8i"], "W8": mem["W8"]})
    z0 = [Gq.of(x) for x in curve(Gq())]
    mem0 = pieces(z0)
    t0 = tangent(z0)
    return {
        "solvable": True,
        "rank_le_10_at_8_values": all(sm["rank_C"] <= 10 for sm in samples),
        "E8i_at_all_s": all(sm["E8i"] and not sm["W8"] for sm in samples),
        "endpoint_B9": mem0["B9"] and not mem0["V"],
        "endpoint_nullity": nullity_L(y_of(z0)),
        "endpoint_tangent": t0["tangent"],
    }


def solve_complex(rows: list[list[Gq]], rhs: list[Gq]) -> list[Gq]:
    """One solution of a consistent complex linear system, by exact Gauss-Jordan elimination."""
    m = [[*r, b] for r, b in zip(rows, rhs, strict=True)]
    n = len(rows[0])
    pivots = []
    r = 0
    for c in range(n):
        piv = next((i for i in range(r, len(m)) if m[i][c]), None)
        if piv is None:
            continue
        m[r], m[piv] = m[piv], m[r]
        inv = Gq(1) / m[r][c]
        m[r] = [x * inv for x in m[r]]
        for i in range(len(m)):
            if i != r and m[i][c]:
                f = m[i][c]
                m[i] = [a - f * b for a, b in zip(m[i], m[r], strict=True)]
        pivots.append(c)
        r += 1
    sol = [Gq() for _ in range(n)]
    for i, c in enumerate(pivots):
        sol[c] = m[i][n]
    return sol


def b9_curves() -> dict[str, Any]:
    rng = np.random.Generator(np.random.PCG64(QB[0]))
    raws = [[(int(a), int(b)) for a, b in rng.integers(-4, 5, size=(18, 2))] for _ in range(8)]
    rows = [r for r in parallel.ordered_map(b9_curve_item, raws, min_items=1) if r is not None]
    good = [r for r in rows if r.get("solvable") and "rank_le_10_at_8_values" in r]
    ok = len(good) >= 4 and all(
        r["rank_le_10_at_8_values"]
        and r["E8i_at_all_s"]
        and r["endpoint_B9"]
        and r["endpoint_nullity"] == 12
        and r["endpoint_tangent"] == 9
        for r in good
    )
    return {"seed": {"draw": DRAW_B, "index": 0, "value": QB[0]}, "curves": rows, "pass": ok}


# ---------------------------------------------------------------------------------------------------------------------
# Finite-field checks in split coordinates


def split_matrices() -> np.ndarray:
    """M_k = D S_k D i^popcount(k) with D = diag(i^popcount(a)); every entry is a real integer."""
    mk = np.zeros((15, 15, 15), dtype=np.int64)
    for k in range(1, 16):
        for a in range(1, 16):
            b = a ^ k
            if b == 0:
                continue
            e = (a.bit_count() + b.bit_count() + k.bit_count()) % 4
            if e % 2:
                raise ValueError("odd power of i in the split matrix")
            mk[k - 1, a - 1, b - 1] = SIGN16[k][b] * (1 if e == 0 else -1)
    return mk


MK = split_matrices()
ETA = np.array([(-1) ** j.bit_count() for j in range(1, 8)], dtype=np.int64)
SPLIT8 = [[(-1) ** (p & q).bit_count() * OCT[p][q] for q in range(8)] for p in range(8)]


def split_consistency() -> dict[str, Any]:
    """D C_z D = M(z') and the split forms agree with the original ones at a point with z_k = i^popcount(k) z'_k."""
    zp = [Gq(v) for v in (3, -1, 4, 1, -5, 9, 2, -6, 5, 3, -5, 8, 9, -7, 9)]
    unit = [Gq(1), IU, Gq(-1), -IU]
    z = [unit[k.bit_count() % 4] * zp[k - 1] for k in range(1, 16)]
    c = cz_rows(z)
    d = [unit[a.bit_count() % 4] for a in range(1, 16)]
    ok_m = all(
        d[a] * Gq.of(c[a][b]) * d[b] == int(sum(MK[k, a, b] * int(zp[k].re) for k in range(15)))
        for a in range(15)
        for b in range(15)
    )
    inv = invariants(z)
    up, mup, vp = [int(x.re) for x in zp[:7]], int(zp[7].re), [int(x.re) for x in zp[8:]]
    eu = int(sum(ETA * np.array(up) ** 2))
    evv = int(sum(ETA * np.array(vp) ** 2))
    euv = int(sum(ETA * np.array(up) * np.array(vp)))
    q_ok = inv["Q"] == eu - mup * mup - evv
    d_ok = inv["Delta"] == euv * euv - eu * evv
    # cross: original Im(u v) equals i times the split cross product, coordinates scaled by i^popcount
    u, _, v = split(z)
    co = cross(u, v)
    cs = [0] * 7
    for p in range(1, 8):
        for q in range(1, 8):
            if p != q:
                cs[(p ^ q) - 1] += SPLIT8[p][q] * up[p - 1] * vp[q - 1]
    cross_ok = all(co[r - 1] == IU * unit[r.bit_count() % 4] * cs[r - 1] for r in range(1, 8))
    skew_ok = all(int(MK[k, a, b]) == -int(MK[k, b, a]) for k in range(15) for a in range(15) for b in range(15))
    return {
        "M_equals_DCD": ok_m,
        "Q": q_ok,
        "Delta": d_ok,
        "cross": cross_ok,
        "M_skew": skew_ok,
        "pass": ok_m and q_ok and d_ok and cross_ok and skew_ok,
    }


def rank_mod_p(mats: np.ndarray, p: int) -> np.ndarray:
    """Ranks of a batch of square matrices over F_p by masked Gaussian elimination."""
    a = (mats % p).astype(np.int32)
    n, rows, cols = a.shape
    inv = np.zeros(p, dtype=np.int32)
    for x in range(1, p):
        inv[x] = pow(x, p - 2, p)
    rank = np.zeros(n, dtype=np.int64)
    idx = np.arange(rows)
    ar = np.arange(n)
    for c in range(cols):
        cand = (a[:, :, c] != 0) & (idx[None, :] >= rank[:, None])
        has = cand.any(axis=1)
        rr = np.minimum(rank, rows - 1)
        piv = np.where(has, np.argmax(cand, axis=1), rr)
        row_r = a[ar, rr].copy()
        a[ar, rr] = a[ar, piv]
        a[ar, piv] = row_r
        pivrow = a[ar, rr] * inv[a[ar, rr, c]][:, None] % p
        factor = a[:, :, c] * ((idx[None, :] > rr[:, None]) & has[:, None])
        a = (a - factor[:, :, None] * pivrow[:, None, :]) % p
        rank += has
    return rank


def rank_crosscheck() -> dict[str, Any]:
    """rank_mod_p against flint nmod_mat on the first 3000 F_11 points of P3a and of P4s with a = 1 (ranks 6 to 14)."""
    ours: list[int] = []
    ref: list[int] = []
    for name in ("P3a", "P4s"):
        first, second = SLICES[name]
        grid = np.array(list(itertools.product(range(11), repeat=4))[:3000], dtype=np.int64)
        zs = np.zeros((len(grid), 15), dtype=np.int64)
        for k, coef in first.items():
            zs[:, k - 1] += coef
            zs[:, 7 + k] += grid[:, 1] * coef
        for k, coef in second.items():
            zs[:, k - 1] += grid[:, 0] * coef
            zs[:, 7 + k] += grid[:, 2] * coef
        zs[:, 7] = grid[:, 3]
        mats = np.einsum("nk,kab->nab", zs % 11, MK) % 11
        ours.extend(int(x) for x in rank_mod_p(mats, 11))
        ref.extend(int(flint.nmod_mat(m.tolist(), 11).rank()) for m in mats)
    return {"matrices": len(ref), "ranks_seen": sorted(Counter(ref).items()), "pass": ours == ref}


def split_classify(zs: np.ndarray, p: int) -> dict[str, np.ndarray]:
    zs = zs % p
    u, mu, v = zs[:, 0:7], zs[:, 7], zs[:, 8:15]
    eu = (u * u * ETA).sum(1) % p
    evv = (v * v * ETA).sum(1) % p
    euv = (u * v * ETA).sum(1) % p
    q = (eu - mu * mu - evv) % p
    delta = (euv * euv - eu * evv) % p
    g = (q * q - 4 * delta) % p
    cr = np.zeros_like(u)
    for a in range(1, 8):
        for b in range(1, 8):
            if a != b:
                cr[:, (a ^ b) - 1] += SPLIT8[a][b] * u[:, a - 1] * v[:, b - 1]
    cr %= p
    wedge = np.zeros(len(zs), dtype=bool)
    for i, j in itertools.combinations(range(7), 2):
        wedge |= (u[:, i] * v[:, j] - u[:, j] * v[:, i]) % p != 0
    m3 = np.zeros(len(zs), dtype=bool)
    for i, j, k in itertools.combinations(range(7), 3):
        det = (
            u[:, i] * (v[:, j] * cr[:, k] - v[:, k] * cr[:, j])
            - u[:, j] * (v[:, i] * cr[:, k] - v[:, k] * cr[:, i])
            + u[:, k] * (v[:, i] * cr[:, j] - v[:, j] * cr[:, i])
        ) % p
        m3 |= det != 0
    gram0 = (eu == 0) & (evv == 0) & (euv == 0)
    ehat = (q == 0) & (delta == 0) & ~m3
    return {
        "W8": (mu == 0) & ((eu + evv) % p == 0) & (euv == 0),
        "V": ~wedge & (q == 0),
        "B9": (mu == 0) & gram0 & (cr == 0).all(1),
        "Np": (mu == 0) & (eu == 0) & ((v - u) % p == 0).all(1),
        "Nm": (mu == 0) & (eu == 0) & ((v + u) % p == 0).all(1),
        "Ehat": ehat,
        "E8i": ehat & wedge & ~gram0,
        "QG0": (q * g) % p == 0,
        "Q0": q == 0,
        "mu0": mu == 0,
        "zero": (zs == 0).all(1),
    }


def fp_verdicts(rank: np.ndarray, cls: dict[str, np.ndarray]) -> dict[str, int]:
    nz = ~cls["zero"]
    return {
        "points": int(nz.sum()),
        "R8_points": int((nz & (rank <= 10)).sum()),
        "R12_points": int((nz & (rank <= 8)).sum()),
        "R16_points": int((nz & (rank <= 6)).sum()),
        "bad_R4_vs_QG": int((nz & ((rank <= 12) != cls["QG0"])).sum()),
        "bad_R8_outside_W8_Ehat": int((nz & (rank <= 10) & ~(cls["W8"] | cls["Ehat"])).sum()),
        "bad_W8_or_E8i_not_in_R8": int((nz & (cls["W8"] | cls["E8i"]) & (rank > 10)).sum()),
        "bad_R12_vs_V_B9": int((nz & ((rank <= 8) != (cls["V"] | cls["B9"]))).sum()),
        "bad_R16_vs_N": int((nz & ((rank <= 6) != (cls["Np"] | cls["Nm"]))).sum()),
        "bad_rank_below_6": int((nz & (rank < 6)).sum()),
        "R8_not_W8_E8i_V_B9": int((nz & (rank <= 10) & ~(cls["W8"] | cls["E8i"] | cls["V"] | cls["B9"])).sum()),
        "Ehat_rank_gt_10": int((nz & cls["Ehat"] & (rank > 10)).sum()),
        "E8i_in_R8": int((nz & cls["E8i"] & (rank <= 10)).sum()),
    }


SLICES = {
    "P2": ({1: 1}, {2: 1}),
    "P3a": ({2: 1, 3: 1}, {1: 1}),
    "P3b": ({2: 1, 3: -1}, {1: 1}),
    "P3c": ({2: 1, 3: 1, 4: 1, 5: -1}, {1: 1}),
    "P4s": ({1: 1, 3: 1}, {4: 1, 6: 1}),
    "P4g": ({1: 1, 3: 1}, {2: 1, 5: 1}),
}


def slice_item(item: tuple[str, int, int]) -> dict[str, Any]:
    """All F_p points of one slice with first parameter a fixed: compare rank strata with the claimed slice table."""
    name, p, a0 = item
    first, second = SLICES[name]
    grid = np.array(list(itertools.product(range(p), repeat=4)), dtype=np.int64)
    params = np.concatenate([np.full((len(grid), 1), a0, dtype=np.int64), grid], axis=1)  # a, b, c, d, m
    zs = np.zeros((len(params), 15), dtype=np.int64)
    for k, coef in first.items():
        zs[:, k - 1] += params[:, 0] * coef
        zs[:, 7 + k] += params[:, 2] * coef
    for k, coef in second.items():
        zs[:, k - 1] += params[:, 1] * coef
        zs[:, 7 + k] += params[:, 3] * coef
    zs[:, 7] = params[:, 4]
    mats = np.einsum("nk,kab->nab", zs % p, MK)
    rank = rank_mod_p(mats, p)
    cls = split_classify(zs, p)
    nz = ~cls["zero"]
    table12 = {
        "P2": cls["W8"] | cls["V"],
        "P3a": cls["Q0"],
        "P3b": cls["Q0"],
        "P3c": cls["V"],
        "P4s": cls["mu0"],
        "P4g": cls["mu0"],
    }[name]
    table10 = cls["mu0"] if name == "P4s" else cls["V"]
    table8 = cls["Np"] | cls["Nm"]
    out = fp_verdicts(rank, cls)
    out["bad_table_order12"] = int((nz & ((rank <= 10) != table12)).sum())
    out["bad_table_order10"] = int((nz & ((rank <= 8) != table10)).sum())
    out["bad_table_order8"] = int((nz & ((rank <= 6) != table8)).sum())
    return out


def fp_slices(primes: Sequence[int]) -> dict[str, Any]:
    items = [(name, p, a0) for p in primes for name in SLICES for a0 in range(p)]
    rows = parallel.ordered_map(slice_item, items, min_items=1)
    out: dict[str, Any] = {}
    for (name, p, _), row in zip(items, rows, strict=True):
        key = f"{name}@{p}"
        acc = out.setdefault(key, Counter())
        acc.update(row)
    result = {k: dict(v) for k, v in out.items()}
    bad_keys = [k for k in next(iter(result.values())) if k.startswith("bad_")]
    ok = all(v[b] == 0 for v in result.values() for b in bad_keys)
    return {"slices": result, "pass": ok}


def sample_item(item: tuple[int, int, int]) -> dict[str, int]:
    p, seed, count = item
    rng = np.random.Generator(np.random.PCG64(seed))
    zs = rng.integers(0, p, size=(count, 15), dtype=np.int64)
    mats = np.einsum("nk,kab->nab", zs, MK)
    rank = rank_mod_p(mats, p)
    return fp_verdicts(rank, split_classify(zs, p))


def fp_samples(count: int) -> dict[str, Any]:
    plan = [(7, QB[1]), (7, QB[2]), (13, QB[3]), (13, QB[4])]
    chunk = 25000
    items = []
    for p, seed in plan:
        rng = np.random.Generator(np.random.PCG64(seed))
        for _ in range(count // chunk):
            items.append((p, int(rng.integers(0, 2**63 - 1)), chunk))
    rows = parallel.ordered_map(sample_item, items, min_items=1)
    out: dict[str, Counter[str]] = {}
    for (p, _, _), row in zip(items, rows, strict=True):
        out.setdefault(str(p), Counter()).update(row)
    result = {k: dict(v) for k, v in out.items()}
    bad = [k for k in next(iter(result.values())) if k.startswith("bad_")]
    return {
        "seeds": [{"draw": DRAW_B, "index": i, "value": QB[i]} for i in (1, 2, 3, 4)],
        "per_prime": result,
        "pass": all(v[b] == 0 for v in result.values() for b in bad),
    }


# ---------------------------------------------------------------------------------------------------------------------
# Float search (corroboration only): alternating projections onto rank <= r inside {C_z}


SK = np.zeros((15, 15, 15))
for _k in range(1, 16):
    for _b in range(1, 16):
        _a = _k ^ _b
        if _a:
            SK[_k - 1, _a - 1, _b - 1] = SIGN16[_k][_b]


def float_item(item: tuple[int, list[float]]) -> dict[str, Any]:
    r, start = item
    z = np.array(start[:15]) + 1j * np.array(start[15:])
    z /= np.linalg.norm(z)
    converged = False
    for _ in range(2000 if r == 4 else 10000):
        c = np.einsum("k,kab->ab", z, SK)
        uu, s, vh = np.linalg.svd(c)
        if s[r] / s[0] < 1e-12:
            converged = True
            break
        s[r:] = 0
        x = (uu * s) @ vh
        z = np.einsum("kab,ab->k", SK, x) / 14.0
        z /= np.linalg.norm(z)
    c = np.einsum("k,kab->ab", z, SK)
    s = np.linalg.svd(c, compute_uv=False)
    u, mu, v = z[:7], z[7], z[8:]
    tol = 1e-7
    uu_, vv_, uv_ = u @ u, v @ v, u @ v
    q = uu_ + mu * mu + vv_
    delta = uu_ * vv_ - uv_ * uv_
    cr = np.array(cross(list(u), list(v)), dtype=complex)
    sv2 = np.linalg.svd(np.array([u, v]), compute_uv=False)
    sv3 = np.linalg.svd(np.array([u, v, cr]), compute_uv=False)
    w8 = abs(mu) < tol and abs(uu_ - vv_) < tol and abs(uv_) < tol
    v_piece = sv2[1] < tol and abs(q) < tol
    b9 = abs(mu) < tol and max(abs(uu_), abs(vv_), abs(uv_)) < tol and np.linalg.norm(cr) < tol
    ehat = abs(q) < tol and abs(delta) < tol and sv3[2] < tol
    npm = abs(mu) < tol and abs(uu_) < tol and min(np.linalg.norm(v - 1j * u), np.linalg.norm(v + 1j * u)) < tol
    return {
        "target_rank": r,
        "converged": converged,
        "sigma_ratio": float(s[r] / s[0]),
        "W8": bool(w8),
        "V": bool(v_piece),
        "B9": bool(b9),
        "Ehat": bool(ehat),
        "N": bool(npm),
    }


def float_search(per_rank: int) -> dict[str, Any]:
    rng = np.random.Generator(np.random.PCG64(QB[5]))
    items = []
    for r in (10, 8, 6, 4):
        for _ in range(per_rank):
            items.append((r, [float(x) for x in rng.standard_normal(30)]))
    rows = parallel.ordered_map(float_item, items, min_items=1)
    summary: dict[str, Any] = {}
    unexplained = 0
    for r in (10, 8, 6, 4):
        sel = [x for x in rows if x["target_rank"] == r]
        conv = [x for x in sel if x["converged"]]
        if r == 10:
            explained = [x for x in conv if x["W8"] or x["Ehat"]]
        elif r == 8:
            explained = [x for x in conv if x["V"] or x["B9"]]
        elif r == 6:
            explained = [x for x in conv if x["N"]]
        else:
            explained = []
        unexplained += len(conv) - len(explained)
        summary[str(r)] = {
            "starts": len(sel),
            "converged": len(conv),
            "explained": len(explained),
            "W8": sum(x["W8"] for x in conv),
            "Ehat_not_W8": sum(x["Ehat"] and not x["W8"] for x in conv),
            "V": sum(x["V"] for x in conv),
            "B9": sum(x["B9"] for x in conv),
            "N": sum(x["N"] for x in conv),
        }
    return {"seed": {"draw": DRAW_B, "index": 5, "value": QB[5]}, "by_rank": summary, "unexplained": unexplained}


# ---------------------------------------------------------------------------------------------------------------------


def self_test() -> list[str]:
    """Mutation controls: each corrupted input must be rejected by the check that guards it."""
    failures = []
    z = QA[:15]
    c = flint.fmpz_mat(15, 15, [x for r in cz_rows(z) for x in r])
    u, mu, w = z[:7], z[7], z[8:]
    uu, vv, uv = dot(u, u), dot(w, w), dot(u, w)
    q = uu + mu * mu + vv
    g_bad = q * q - 3 * (uu * vv - uv * uv)
    lam = flint.fmpz_poly([0, 1])
    if c.charpoly() == lam * (lam**2 + q) ** 3 * (lam**4 + 2 * q * lam**2 + g_bad) ** 2:
        failures.append("a wrong quartic passed the characteristic polynomial check")
    global pieces
    original = pieces

    def bad_w8(zz: Sequence[Any]) -> dict[str, bool]:
        m = original(zz)
        inv = invariants(zz)
        m["W8"] = zz[7] == 0 and inv["U"] == -inv["V"] and inv["W"] == 0
        return m

    pieces = bad_w8  # type: ignore[assignment]
    try:
        violations = sum(len(exhaustive_item(combo)[1]) for combo in list(itertools.combinations(DP, 2))[:200])
    finally:
        pieces = original
    if violations == 0:
        failures.append("a W8 test with U = -V passed the exhaustive classification")
    global _e8_frame
    frame = _e8_frame

    def unaligned(pp: list[Any]) -> tuple[list[Any], list[Any]]:
        e, n = frame(pp)
        y = lin((1, pp[7:14]), (-dot(pp[7:14], e) / dot(e, e), e))
        return e, lin((1, n), (1, lin((Fraction(1, 2), y), (Fraction(-1, 2), cross(e, y)))))

    _e8_frame = unaligned  # type: ignore[assignment]
    try:
        index = [f[0] for f in FAMILIES].index("E8")
        row = evaluate_family((index, family_params()[index][1]))
    finally:
        _e8_frame = frame
    if row["pass"]:
        failures.append("an E8 family with an unaligned radical passed")
    mats = np.array([[[0, 1], [-1, 0]], [[0, 0], [0, 0]], [[0, 7], [-7, 0]]], dtype=np.int64)
    if list(rank_mod_p(mats, 7)) != [2, 0, 0]:
        failures.append("rank_mod_p is wrong on 2 x 2 controls")
    return failures


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", type=Path)
    ap.add_argument("--fp-samples", type=int, default=400000)
    ap.add_argument("--float-starts", type=int, default=150)
    ap.add_argument("--slice-primes", default="11,13")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        failures = self_test()
        for line in failures:
            print("FAIL", line)
        print(f"verify_independent self-test: {4 - len(failures)} of 4 mutation controls rejected")
        return 1 if failures else 0
    t0 = time.perf_counter()
    timings: dict[str, float] = {}
    report: dict[str, Any] = {}

    def run(key: str, fn: Callable[[], Any]) -> None:
        start = time.perf_counter()
        report[key] = fn()
        timings[key] = round(time.perf_counter() - start, 2)
        status = report[key].get("pass", "n/a") if isinstance(report[key], dict) else "n/a"
        print(f"{key:24s} pass={status} {timings[key]:7.2f} s", flush=True)

    run("tables", table_checks)
    run("split_consistency", split_consistency)
    run("identities", identity_checks)
    run("double_cross", double_cross)
    run("g_irreducibility", g_irreducibility)
    run("families", lambda: {"rows": parallel.ordered_map(evaluate_family, family_params(), min_items=1)})
    report["families"]["pass"] = all(r["pass"] for r in report["families"]["rows"])
    print(f"{'families (all rows)':24s} pass={report['families']['pass']}", flush=True)
    run("witnesses", witness_checks)
    run("b9_curves", b9_curves)
    run("exhaustive", exhaustive_search)
    run("rank_crosscheck", rank_crosscheck)
    primes = [int(x) for x in args.slice_primes.split(",") if x]
    run("fp_slices", lambda: fp_slices(primes))
    run("fp_samples", lambda: fp_samples(args.fp_samples))
    run("float_search", lambda: float_search(args.float_starts))
    report["timings_s"] = timings
    report["total_s"] = round(time.perf_counter() - t0, 2)
    report["workers"] = parallel.workers()
    report["versions"] = {"python": sys.version.split()[0], "python-flint": flint.__version__, "numpy": np.__version__}
    print(f"total {report['total_s']} s on {report['workers']} workers")
    if args.out:
        args.out.write_text(json.dumps(report, indent=1, default=str) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
