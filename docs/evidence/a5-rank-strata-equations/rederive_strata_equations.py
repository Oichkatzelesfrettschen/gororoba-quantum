"""Explicit equations for the A_5 rank strata and an independent covering, from cd_core and Singular.

The script imports nothing from scripts/a5_zero_divisor_strata.py and nothing from the earlier verifier. Every table
comes from cd_core.cd_sign, cross-checked against cd_multiply_exact; every Groebner basis, radical and reduction is a
Singular computation over Q; every rank of a constant matrix is an exact python-flint fmpq_mat rank.

Coordinates. A doubly pure y of A_5 has z_k = y_k + i y_(16+k), k = 1..15, and C_z is the Im-block of left
multiplication by z in A_4, entry (a, b) equal to cd_sign(16, a XOR b, b) z_(a XOR b). Split coordinates are
z_k = i^popcount(k) z'_k, the coefficients on the basis e'_k = i^popcount(k) e_k; module vectors are
u' = z'_1..z'_7, mu' = z'_8, v' = z'_9..z'_15. Every polynomial below is built from its original-coordinate definition
by that substitution over Z[i] and divided by the unit it acquires, so the split forms are derived, never typed in.
In original coordinates (u = z_1..z_7, mu = z_8, v = z_9..z_15, complex bilinear dot products, x ^ y = Im(x y) the
cd_core octonion cross product):

- W8: mu = 0, u.u = v.v, u.v = 0;  V: rank [u; v] <= 1, Q = 0;  B9: mu = 0, u.u = v.v = u.v = 0, u ^ v = 0;
- N_+, N_-: mu = 0, u.u = 0, v = +-i u;  Ehat: Q = 0, Delta = 0, rank [u; v; u ^ v] <= 2;

with Q = u.u + mu^2 + v.v and Delta = (u.u)(v.v) - (u.v)^2.

Parts (keys of the record):
- tables: cd_sign against cd_multiply_exact and left_mult_matrix_exact for dimensions 8, 16 and 32, and the split
  tables (-1)^popcount(p AND q) cd_sign, which are the cd_core tables on the basis e'_k;
- g2: the derivation algebra of the split octonions (dimension 14), the inner derivations D_(x,y), the identity
  D_(x,y) x = c (eta(x) y - eta(x, y) x), the stabilizer of e'_1 acting as sl_3 on the eigenspaces of e'_1 ^ -, the
  null-vector orbits, the isotropic-plane certificate through n = e'_1 + e'_3, and the equivariance of C'_z;
- identities: the cross-product identities the case analysis of Ehat uses, symbolic over Z;
- global: Singular over Q in the 15 split coordinates. Every order-12 Pfaffian of M(z') reduces to 0 modulo standard
  bases of the ideals of Ehat and W8, every order-10 one modulo those of V and B9, every order-8 one modulo those of
  N_+ and N_- (a radical is computed only where that reduction fails);
  dimension and degree of Ehat; the Ehat equations vanish on V and B9; and the saturation of the Ehat ideal by
  f = mu' (u'_1 v'_2 - u'_2 v'_1) is the Ehat ideal, so V(Ehat) is the closure of its part where f != 0;
- slices: on each of six five-parameter slices and each order 12, 10, 8 the radical of the Pfaffian ideal equals the
  radical of the intersection of the two named piece ideals (both inclusions decided by reduction modulo a standard
  basis of a radical);
- points: rational points with the nullity of the 32 x 32 matrix L_y, piece memberships and the Jacobian rank of Ehat.

--self-test runs nine controls: Ehat without Q, W8 with u.u = -v.v (on a slice and globally), the P2 union with Ehat
dropped, a P3c radical moved
into V_+, Ehat with the W8 component added, the isotropic-plane ideal without eta(x) and a derivation lift D + (-D) each
fail their check, and a slice that reads no W8 equation passes.

Usage:
    "$PYTHON" -B -W error docs/evidence/a5-rank-strata-equations/rederive_strata_equations.py --self-test
    "$PYTHON" -B -W error docs/evidence/a5-rank-strata-equations/rederive_strata_equations.py \
        --out docs/evidence/a5-rank-strata-equations/result.json
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
from collections.abc import Callable, Sequence
from fractions import Fraction
from math import gcd
from pathlib import Path
from typing import Any

import flint

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import parallel  # noqa: E402
from cd_core import cd_multiply_exact, cd_sign, left_mult_matrix_exact  # noqa: E402

SINGULAR = "Singular"
GLOBAL_VARS = tuple(f"z{k}" for k in range(1, 16))
SLICE_VARS = ("a", "b", "c", "d", "m")
X_VARS = tuple(f"x{k}" for k in range(1, 8))


def popcount(k: int) -> int:
    return bin(k).count("1")


# ---------------------------------------------------------------------------------------------------------------
# Tables


def unit_vec(dim: int, k: int) -> list[int]:
    return [1 if j == k else 0 for j in range(dim)]


def table_checks() -> dict[str, Any]:
    """cd_sign agrees with cd_multiply_exact; the split tables are the scaled cd_core tables."""
    mismatches = 0
    for dim in (8, 16, 32):
        for p in range(dim):
            mat = left_mult_matrix_exact(dim, unit_vec(dim, p))
            for q in range(dim):
                prod = cd_multiply_exact(dim, unit_vec(dim, p), unit_vec(dim, q))
                expect = [Fraction(0)] * dim
                expect[p ^ q] = Fraction(cd_sign(dim, p, q))
                if list(prod) != expect or mat[p ^ q][q] != cd_sign(dim, p, q):
                    mismatches += 1
    # e'_p e'_q = i^(pc p + pc q) cd_sign e_(p^q) = i^(pc p + pc q - pc(p^q)) cd_sign e'_(p^q); the exponent is
    # 2 popcount(p & q), so the split table is (-1)^popcount(p & q) cd_sign.
    exponent_even = all(
        (popcount(p) + popcount(q) - popcount(p ^ q)) == 2 * popcount(p & q) for p in range(32) for q in range(32)
    )
    return {"pass": mismatches == 0 and exponent_even, "basis_pair_mismatches": mismatches}


def split_sign(dim: int, p: int, q: int) -> int:
    return (-1) ** popcount(p & q) * cd_sign(dim, p, q)


SPLIT8 = [[split_sign(8, p, q) for q in range(8)] for p in range(8)]
SPLIT16 = [[split_sign(16, p, q) for q in range(16)] for p in range(16)]
ETA = [0] + [-SPLIT8[j][j] for j in range(1, 8)]  # e'_j e'_j = -eta_j e'_0 for imaginary e'_j


# ---------------------------------------------------------------------------------------------------------------
# Polynomials over Z[i]: a pair (re, im) of polynomials in one python-flint context


class GP:
    __slots__ = ("im", "re")

    def __init__(self, re: Any, im: Any) -> None:
        self.re = re
        self.im = im

    def __add__(self, o: GP) -> GP:
        return GP(self.re + o.re, self.im + o.im)

    def __sub__(self, o: GP) -> GP:
        return GP(self.re - o.re, self.im - o.im)

    def __mul__(self, o: Any) -> GP:
        if isinstance(o, int):
            return GP(self.re * o, self.im * o)
        return GP(self.re * o.re - self.im * o.im, self.re * o.im + self.im * o.re)

    __rmul__ = __mul__

    def __neg__(self) -> GP:
        return GP(-self.re, -self.im)

    def iszero(self) -> bool:
        return self.re == 0 and self.im == 0

    def real(self) -> Any:
        """The polynomial divided by its unit: exactly one of re, im may be nonzero."""
        if self.im == 0:
            return self.re
        if self.re == 0:
            return self.im
        raise ArithmeticError("polynomial is not a unit times a rational polynomial")


def ipow(k: int, one: Any, zero: Any) -> GP:
    return [GP(one, zero), GP(zero, one), GP(-one, zero), GP(zero, -one)][k % 4]


def original_from_split(zp: Sequence[Any]) -> list[GP]:
    """z_k = i^popcount(k) z'_k for k = 1..15; zp holds z'_1..z'_15 as rational polynomials."""
    zero = zp[0] * 0
    one = zero + 1
    return [ipow(popcount(k), one, zero) * GP(zp[k - 1], zero) for k in range(1, 16)]


def cz_original(z: Sequence[GP]) -> list[list[GP]]:
    zero = z[0] * 0
    out = [[zero] * 15 for _ in range(15)]
    for a in range(1, 16):
        for b in range(1, 16):
            k = a ^ b
            if k:
                out[a - 1][b - 1] = cd_sign(16, k, b) * z[k - 1]
    return out


def split_matrix(zp: Sequence[Any]) -> list[list[Any]]:
    """M(z') = D C_(D z') D with D = diag(i^popcount): a skew matrix over Z[z'] of the same rank as C_z."""
    z = original_from_split(zp)
    c = cz_original(z)
    zero = zp[0] * 0
    one = zero + 1
    rows = []
    for a in range(1, 16):
        row = []
        for b in range(1, 16):
            entry = ipow(popcount(a) + popcount(b), one, zero) * c[a - 1][b - 1]
            if entry.im != 0:
                raise ArithmeticError("D C D has a non-real entry")
            row.append(entry.re)
        rows.append(row)
    for a in range(15):
        for b in range(15):
            if rows[a][b] != -rows[b][a]:
                raise ArithmeticError("D C D is not skew")
    return rows


def pfaffians(mat: Sequence[Sequence[Any]], order: int) -> list[Any]:
    """Distinct nonzero principal Pfaffians of the given order, by expansion along the first row with memo."""
    one = mat[0][0] * 0 + 1
    memo: dict[tuple[int, ...], Any] = {(): one}

    def pf(s: tuple[int, ...]) -> Any:
        hit = memo.get(s)
        if hit is not None:
            return hit
        total = one * 0
        for j in range(1, len(s)):
            entry = mat[s[0]][s[j]]
            if entry == 0:
                continue
            term = entry * pf(s[1:j] + s[j + 1 :])
            total = total + term if j % 2 else total - term
        memo[s] = total
        return total

    seen: dict[str, Any] = {}
    for s in itertools.combinations(range(len(mat)), order):
        p = pf(s)
        if p != 0:
            seen.setdefault(str(p), p)
    return list(seen.values())


def gdot(x: Sequence[GP], y: Sequence[GP]) -> GP:
    total = x[0] * 0
    for p, q in zip(x, y, strict=True):
        total = total + p * q
    return total


def gcross(x: Sequence[GP], y: Sequence[GP]) -> list[GP]:
    """Im(x y) for imaginary octonions x, y in original coordinates (cd_core table)."""
    out = [x[0] * 0 for _ in range(7)]
    for p in range(1, 8):
        for q in range(1, 8):
            r = p ^ q
            if r:
                out[r - 1] = out[r - 1] + cd_sign(8, p, q) * (x[p - 1] * y[q - 1])
    return out


def det3(m: Sequence[Sequence[GP]]) -> GP:
    return (
        m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
        - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
        + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0])
    )


PIECES = ("W8", "V", "B9", "Np", "Nm", "Ehat", "QG")


def piece_ideals(zp: Sequence[Any], mutation: str = "") -> dict[str, list[Any]]:
    """Generators of every piece ideal in split coordinates, built from the original-coordinate definitions."""
    z = original_from_split(zp)
    u, mu, v = z[0:7], z[7], z[8:15]
    big_u, big_v, big_w = gdot(u, u), gdot(v, v), gdot(u, v)
    q = big_u + mu * mu + big_v
    delta = big_u * big_v - big_w * big_w
    x = gcross(u, v)
    iu = [GP(-t.im, t.re) for t in u]
    minors2 = [u[i] * v[j] - u[j] * v[i] for i, j in itertools.combinations(range(7), 2)]
    rows = [u, v, x]
    minors3 = [det3([[rows[r][c] for c in cols] for r in range(3)]) for cols in itertools.combinations(range(7), 3)]
    w8 = [mu, big_u + big_v if mutation == "w8_sign" else big_u - big_v, big_w]
    ehat = [delta, *minors3] if mutation == "ehat_no_q" else [q, delta, *minors3]
    out = {
        "W8": w8,
        "V": [q, *minors2],
        "B9": [mu, big_u, big_v, big_w, *x],
        "Np": [mu, big_u, *[v[k] - iu[k] for k in range(7)]],
        "Nm": [mu, big_u, *[v[k] + iu[k] for k in range(7)]],
        "Ehat": ehat,
        "QG": [q, q * q - 4 * delta],
    }
    return {key: [g.real() for g in gens if not g.iszero()] for key, gens in out.items()}


# ---------------------------------------------------------------------------------------------------------------
# Singular


def singular_version() -> str:
    res = subprocess.run([SINGULAR, "-v", "-q", "--execute", "quit;"], capture_output=True, text=True, check=False)
    head = (res.stdout or res.stderr).strip().splitlines()
    return head[0] if head else "unknown"


def run_singular(script: str) -> dict[str, str]:
    """Run a Singular script; return the 'RESULT key value' lines as a dict."""
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "job.sing"
        path.write_text(script, encoding="utf-8")
        res = subprocess.run([SINGULAR, "-q", "--no-warn", str(path)], capture_output=True, text=True, check=False)
    out: dict[str, str] = {}
    for line in res.stdout.splitlines():
        m = re.match(r"^RESULT (\S+) (.*)$", line.strip())
        if m:
            out[m.group(1)] = m.group(2).strip()
    if res.returncode != 0 or "error" in res.stderr.lower() or "? " in res.stdout:
        out["singular_error"] = (res.stderr + res.stdout)[-2000:]
    return out


def ideal_text(name: str, gens: Sequence[Any]) -> str:
    body = ",\n".join(str(g) for g in gens) if gens else "0"
    return f"ideal {name} = {body};"


def ring_text(names: Sequence[str]) -> str:
    return f"ring r = 0, ({', '.join(names)}), dp;"


SINGULAR_PROCS = """
proc inrad(ideal f, ideal I)
{
  // 1 when every generator of f lies in the radical of I
  ideal S = std(radical(I));
  return(size(reduce(f, S)) == 0);
}
proc inideal(ideal f, ideal I)
{
  ideal S = std(I);
  return(size(reduce(f, S)) == 0);
}
"""


# ---------------------------------------------------------------------------------------------------------------
# Global jobs (15 variables)


def global_ctx() -> Any:
    return flint.fmpz_mpoly_ctx.get(GLOBAL_VARS, "degrevlex")


def global_job(job: tuple[str, str]) -> dict[str, Any]:
    kind, mutation = job
    ctx = global_ctx()
    zp = list(ctx.gens())
    pcs = piece_ideals(zp, mutation)
    head = 'LIB "primdec.lib";\n' + ring_text(GLOBAL_VARS) + "\noption(redSB);\n" + SINGULAR_PROCS
    start = time.perf_counter()
    if kind == "ehat_structure":
        script = head + "\n".join(
            [
                'LIB "elim.lib";',
                ideal_text("E", pcs["Ehat"]),
                ideal_text("W", pcs["W8"]),
                "E = intersect(E, W);" if mutation == "ehat_plus_w8" else "",
                ideal_text("VV", pcs["V"]),
                ideal_text("B", pcs["B9"]),
                "ideal SE = std(E);",
                '"RESULT dim", dim(SE);',
                '"RESULT degree", mult(SE);',
                ideal_text("NP", pcs["Np"]),
                ideal_text("NM", pcs["Nm"]),
                '"RESULT piece_dims", string(dim(std(W))) + " " + string(dim(std(VV))) + " " + string(dim(std(B)))'
                ' + " " + string(dim(std(NP))) + " " + string(dim(std(NM)));',
                '"RESULT ehat_vanishes_on_V", inrad(E, VV);',
                '"RESULT ehat_vanishes_on_B9", inrad(E, B);',
                # f is nonzero exactly where mu' != 0 and u', v' are independent; E : f^infinity = E puts every
                # point of V(E) in the closure of that open part.
                "poly f = z8 * (z1 * z10 - z2 * z9);",
                "ideal S = sat(E, f);",
                '"RESULT saturation_equals_ehat", size(reduce(S, SE)) == 0;',
                "quit;",
            ]
        )
        res = run_singular(script)
    else:
        order = {"pf12": 12, "pf10": 10, "pf8": 8}[kind]
        names = {12: ("Ehat", "W8"), 10: ("V", "B9"), 8: ("Np", "Nm")}[order]
        pf = pfaffians(split_matrix(zp), order)
        lines = [ideal_text("P", pf)]
        for k, nm in enumerate(names):
            lines.append(ideal_text(f"A{k}", pcs[nm]))
            # Ideal membership implies radical membership; the radical is computed only when membership fails.
            lines.append(f'int ii{k} = inideal(P, A{k}); "RESULT in_ideal_{nm}", ii{k};')
            lines.append(f'if (ii{k} == 0) {{ "RESULT in_radical_{nm}", inrad(P, A{k}); }}')
        lines.append(f'"RESULT generators", {len(pf)};')
        lines.append("quit;")
        res = run_singular(head + "\n".join(lines))
    res["seconds"] = f"{time.perf_counter() - start:.1f}"
    return {"job": kind, "mutation": mutation, **res}


# ---------------------------------------------------------------------------------------------------------------
# Slices (5 variables)

SLICE_PLANES: dict[str, tuple[dict[int, int], dict[int, int]]] = {
    "P2": ({1: 1}, {2: 1}),
    "P3a": ({2: 1, 3: 1}, {1: 1}),
    "P3b": ({2: 1, 3: -1}, {1: 1}),
    "P3c": ({2: 1, 3: 1, 4: 1, 5: -1}, {1: 1}),
    "P4s": ({1: 1, 3: 1}, {4: 1, 6: 1}),
    "P4g": ({1: 1, 3: 1}, {2: 1, 5: 1}),
}
LEVELS = {12: ("W8", "Ehat"), 10: ("V", "B9"), 8: ("Np", "Nm")}


def slice_point(name: str, ctx: Any) -> list[Any]:
    """z' = (a A + b B, m, c A + d B) for the slice plane (A, B) in split coordinates."""
    a, b, c, d, m = ctx.gens()
    first, second = SLICE_PLANES[name]
    zero = a * 0
    zp = [zero] * 15
    for j in range(1, 8):
        aj, bj = first.get(j, 0), second.get(j, 0)
        zp[j - 1] = a * aj + b * bj
        zp[7 + j] = c * aj + d * bj
    zp[7] = m
    return zp


def slice_job(job: tuple[str, int, str]) -> dict[str, Any]:
    name, order, mutation = job
    ctx = flint.fmpz_mpoly_ctx.get(SLICE_VARS, "degrevlex")
    zp = slice_point(name, ctx)
    pf = pfaffians(split_matrix(zp), order)
    pcs = piece_ideals(zp, mutation)
    names = LEVELS[order]
    lines = ['LIB "primdec.lib";', ring_text(SLICE_VARS), "option(redSB);", SINGULAR_PROCS, ideal_text("P", pf)]
    for k, nm in enumerate(names):
        lines.append(ideal_text(f"A{k}", pcs[nm] or [0]))
        lines.append(f'"RESULT piece_{nm}_in_R", inrad(P, A{k});')
    lines.append("ideal I = A0;" if mutation == "union_drops_ehat" else "ideal I = intersect(A0, A1);")
    lines.append('"RESULT R_in_union", inrad(I, P);')
    lines.append('list L = minAssGTZ(P); string s = ""; int k;')
    lines.append('for (k = 1; k <= size(L); k++) { s = s + string(dim(std(L[k]))) + " "; }')
    lines.append('"RESULT component_dims", s;')
    lines.append(f'"RESULT generators", {len(pf)};')
    lines.append("quit;")
    start = time.perf_counter()
    res = run_singular("\n".join(lines))
    res["seconds"] = f"{time.perf_counter() - start:.1f}"
    ok = res.get("R_in_union") == "1" and all(res.get(f"piece_{nm}_in_R") == "1" for nm in names)
    return {"slice": name, "order": order, "mutation": mutation, "pass": ok and "singular_error" not in res, **res}


# ---------------------------------------------------------------------------------------------------------------
# G_2 facts in split coordinates over Q


def qmat(rows: Sequence[Sequence[Any]]) -> Any:
    return flint.fmpq_mat(
        len(rows), len(rows[0]), [flint.fmpq(Fraction(x).numerator, Fraction(x).denominator) for r in rows for x in r]
    )


def qrank(rows: Sequence[Sequence[Any]]) -> int:
    return int(qmat(rows).rank()) if rows and rows[0] else 0


def nullspace(rows: Sequence[Sequence[Any]]) -> list[list[Fraction]]:
    """Basis of the right kernel, from python-flint's fmpz_mat nullspace after clearing row denominators."""
    scaled = []
    for row in rows:
        fr = [Fraction(x) for x in row]
        lcm = 1
        for x in fr:
            lcm = lcm * x.denominator // gcd(lcm, x.denominator)
        scaled.append([int(x * lcm) for x in fr])
    cols = len(scaled[0])
    basis, nullity = flint.fmpz_mat(len(scaled), cols, [x for r in scaled for x in r]).nullspace()
    return [[Fraction(int(basis[j, c])) for j in range(cols)] for c in range(int(nullity))]


def omul(x: Sequence[Any], y: Sequence[Any]) -> list[Any]:
    """Product in the split octonions, 8 coordinates."""
    zero = x[0] * 0
    out = [zero] * 8
    for p in range(8):
        if x[p] == 0:
            continue
        for q in range(8):
            if y[q] == 0:
                continue
            out[p ^ q] = out[p ^ q] + SPLIT8[p][q] * x[p] * y[q]
    return out


def eta(x: Sequence[Any], y: Sequence[Any]) -> Any:
    total = x[0] * 0
    for j in range(1, 8):
        total = total + ETA[j] * x[j] * y[j]
    return total


def ocross(x: Sequence[Any], y: Sequence[Any]) -> list[Any]:
    out = omul(x, y)
    out[0] = out[0] * 0
    return out


def apply(mat: Sequence[Sequence[Any]], x: Sequence[Any]) -> list[Any]:
    return [sum((mat[r][c] * x[c] for c in range(len(x))), x[0] * 0) for r in range(len(mat))]


def derivations(table: Sequence[Sequence[int]]) -> list[list[list[Fraction]]]:
    """Basis of {D : D(e_p e_q) = D(e_p) e_q + e_p D(e_q), D e_0 = 0} for the given +-1 table."""
    n = len(table)
    rows = []
    for p in range(n):
        for q in range(n):
            for r in range(n):
                row = [0] * (n * n)  # unknown D[r][s] at index r * n + s
                row[r * n + (p ^ q)] += table[p][q]
                row[(r ^ q) * n + p] -= table[r ^ q][q]
                row[(p ^ r) * n + q] -= table[p][p ^ r]
                rows.append(row)
    for r in range(n):
        row = [0] * (n * n)
        row[r * n] = 1
        rows.append(row)
    return [[[v[r * n + s] for s in range(n)] for r in range(n)] for v in nullspace(rows)]


def lmat(x: Sequence[Any]) -> list[list[Any]]:
    cols = [omul(x, unit_vec(8, s)) for s in range(8)]
    return [[cols[s][r] for s in range(8)] for r in range(8)]


def rmat(x: Sequence[Any]) -> list[list[Any]]:
    cols = [omul(unit_vec(8, s), x) for s in range(8)]
    return [[cols[s][r] for s in range(8)] for r in range(8)]


def mm(a: Sequence[Sequence[Any]], b: Sequence[Sequence[Any]]) -> list[list[Any]]:
    n = len(a)
    return [[sum(a[i][k] * b[k][j] for k in range(n)) for j in range(n)] for i in range(n)]


def msub(a: Sequence[Sequence[Any]], b: Sequence[Sequence[Any]]) -> list[list[Any]]:
    return [[a[i][j] - b[i][j] for j in range(len(a))] for i in range(len(a))]


def madd(a: Sequence[Sequence[Any]], b: Sequence[Sequence[Any]]) -> list[list[Any]]:
    return [[a[i][j] + b[i][j] for j in range(len(a))] for i in range(len(a))]


def comm(a: Sequence[Sequence[Any]], b: Sequence[Sequence[Any]]) -> list[list[Any]]:
    return msub(mm(a, b), mm(b, a))


def inner_derivation(x: Sequence[Any], y: Sequence[Any]) -> list[list[Any]]:
    lx, ly, rx, ry = lmat(x), lmat(y), rmat(x), rmat(y)
    return madd(madd(comm(lx, ly), comm(lx, ry)), comm(rx, ry))


def flat(mat: Sequence[Sequence[Any]]) -> list[Any]:
    return [x for row in mat for x in row]


def vec(spec: dict[int, int]) -> list[Fraction]:
    return [Fraction(spec.get(j, 0)) for j in range(8)]


def orbit_rank(ders: Sequence[Sequence[Sequence[Fraction]]], x: Sequence[Fraction]) -> int:
    return qrank([apply(d, x) for d in ders])


class InSpan:
    """Picklable test that a flattened matrix lies in the rational span of fixed rows."""

    def __init__(self, rows: list[list[Fraction]]) -> None:
        self.rows = rows
        self.rank = qrank(rows)

    def __call__(self, row: list[Any]) -> bool:
        return qrank([*self.rows, row]) == self.rank


def congruence_holds(big: Sequence[Sequence[Fraction]]) -> bool:
    """M(D z') = -(D^T M(z') + M(z') D) over Z[z'] for the restriction D of a lift to Im A_4."""
    zgens = list(global_ctx().gens())
    zero = zgens[0] * 0
    mz = split_matrix(zgens)
    d15 = [[int(big[r][s]) for s in range(1, 16)] for r in range(1, 16)]
    mdz = split_matrix([sum((d15[r][s] * zgens[s] for s in range(15)), zero) for r in range(15)])
    left = [[sum((d15[k][r] * mz[k][c] for k in range(15)), zero) for c in range(15)] for r in range(15)]
    right = [[sum((mz[r][k] * d15[k][c] for k in range(15)), zero) for c in range(15)] for r in range(15)]
    return all(mdz[r][c] == -(left[r][c] + right[r][c]) for r in range(15) for c in range(15))


def g2_facts(mutation: str = "") -> dict[str, Any]:
    ders = derivations(SPLIT8)
    out: dict[str, Any] = {"derivation_dimension": len(ders)}
    # Derivations fix e'_0 and preserve Im and eta.
    preserve = all(d[0][s] == 0 and d[s][0] == 0 for d in ders for s in range(8))
    skew_eta = all(ETA[r] * d[r][s] + ETA[s] * d[s][r] == 0 for d in ders for r in range(1, 8) for s in range(1, 8))
    out["preserve_im_and_eta"] = preserve and skew_eta
    # F1: D_(e_p, e_q) lie in the derivation span, and D_(x, y) x = c (eta(x) y - eta(x, y) x) over Z[x, y].
    in_span = InSpan([flat(d) for d in ders])
    pairs = [(p, q) for p in range(1, 8) for q in range(1, 8)]
    inner_ok = all(
        parallel.ordered_map(in_span, [flat(inner_derivation(unit_vec(8, p), unit_vec(8, q))) for p, q in pairs])
    )
    pctx = flint.fmpz_mpoly_ctx.get(
        tuple(f"x{k}" for k in range(1, 8)) + tuple(f"y{k}" for k in range(1, 8)), "degrevlex"
    )
    gens = pctx.gens()
    zero = gens[0] * 0
    xs = [zero, *gens[0:7]]
    ys = [zero, *gens[7:14]]
    xy, yx, xx = omul(xs, ys), omul(ys, xs), omul(xs, xs)
    # D_(x,y) w = x(y w) - y(x w) + x(w y) - (x w) y + (w y) x - (w x) y, at w = x.
    lhs = [
        a - b + c - d + e - f
        for a, b, c, d, e, f in zip(
            omul(xs, yx), omul(ys, xx), omul(xs, xy), omul(xx, ys), omul(xy, xs), omul(xx, ys), strict=True
        )
    ]
    rhs = [eta(xs, xs) * ys[j] - eta(xs, ys) * xs[j] for j in range(8)]
    # D_(x,y) x is cubic with integer coefficients of size at most 6, so c is one of the nonzero integers up to 8.
    cval = next((c for c in range(-8, 9) if c and all(lhs[j] == c * rhs[j] for j in range(8))), None)
    identity_ok = cval is not None
    out["F1"] = {"inner_derivations_in_span": inner_ok, "constant": cval, "identity": identity_ok}
    # F2: stabilizer of e'_1 acts as sl_3 on V_+ and V_-.
    e1 = vec({1: 1})
    stab = nullspace([[apply(d, e1)[r] for d in ders] for r in range(8)])
    h = [
        [
            [sum((coef_ * ders[i][r][s] for i, coef_ in enumerate(comb)), Fraction(0)) for s in range(8)]
            for r in range(8)
        ]
        for comb in stab
    ]
    k_mat = [[ocross(e1, unit_vec(8, s))[r] for s in range(8)] for r in range(8)]
    perp = [vec({j: 1}) for j in range(2, 8)]
    ksq = mm(k_mat, k_mat)
    ksq_on_perp = all(apply(ksq, w) == [-eta(e1, e1) * x for x in w] for w in perp)
    vplus = nullspace([[k_mat[r][s] - (1 if r == s else 0) for s in range(8)] for r in range(8)])
    vminus = nullspace([[k_mat[r][s] + (1 if r == s else 0) for s in range(8)] for r in range(8)])
    iso = all(eta(a, b) == 0 for space in (vplus, vminus) for a in space for b in space)
    pairing = qrank([[eta(a, b) for b in vminus] for a in vplus])
    commutes = all(comm(d, k_mat) == [[0] * 8 for _ in range(8)] for d in h)

    def restrict(d: Sequence[Sequence[Fraction]], space: list[list[Fraction]]) -> list[list[Fraction]] | None:
        cols = []
        for w in space:
            image = apply(d, w)
            sol = nullspace([[space[i][r] for i in range(len(space))] + [-image[r]] for r in range(8)])
            sol = [s for s in sol if s[-1] != 0]
            if not sol:
                return None
            cols.append([x / sol[0][-1] for x in sol[0][:-1]])
        return [[cols[c][r] for c in range(len(space))] for r in range(len(space))]

    rest = [restrict(d, vplus) for d in h]
    invariant = all(r is not None for r in rest)
    sl3_rank = qrank([flat(r) for r in rest if r is not None]) if invariant else 0
    traceless = invariant and all(sum(r[i][i] for i in range(3)) == 0 for r in rest if r is not None)
    out["F2"] = {
        "stabilizer_dimension": len(h),
        "k_squared_on_perp": ksq_on_perp,
        "eigenspace_dimensions": [len(vplus), len(vminus)],
        "eigenspaces_isotropic": iso,
        "pairing_rank": pairing,
        "stabilizer_commutes_with_k": commutes,
        "image_rank_on_vplus": sl3_rank,
        "traceless": traceless,
    }

    def side(x: Sequence[Fraction]) -> str:
        on_plus = qrank([*vplus, list(x)]) == len(vplus)
        on_minus = qrank([*vminus, list(x)]) == len(vminus)
        return "V+" if on_plus else "V-" if on_minus else "mixed"

    # Slice vectors: P2 is (e'_1, e'_2); the radical vectors of P3a, P3b, P3c; their types.
    radicals = {name: vec(SLICE_PLANES[name][0]) for name in ("P3a", "P3b", "P3c")}
    if mutation == "p3c_radical_in_vplus":
        radicals["P3c"] = vec({2: 1, 3: 1, 4: 1, 5: 1})
    types = {name: side(r) for name, r in radicals.items()}
    nulls = {name: eta(r, r) == 0 and eta(r, e1) == 0 for name, r in radicals.items()}
    p3c = radicals["P3c"]
    plus_part = vec({2: 1, 3: 1})
    minus_part = [p3c[j] - plus_part[j] for j in range(8)]
    e2 = vec({2: 1})
    out["slice_frames"] = {
        "e1_norm": eta(e1, e1),
        "P2_gram": [[eta(e1, e1), eta(e1, e2)], [eta(e2, e1), eta(e2, e2)]],
        "P2_second_vector_type": side(e2),
        "radical_types": types,
        "radicals_null_and_perp_e1": all(nulls.values()),
        "P3c_split_pairing_zero": side(plus_part) == "V+"
        and side(minus_part) == "V-"
        and eta(plus_part, minus_part) == 0,
    }
    # F3: three null types have orbits of dimension 6.
    out["F3"] = {name: orbit_rank(ders, r) for name, r in radicals.items()}
    # F4: stabilizer H of n0 = e'_1 + e'_3; L = ker(n0 ^ -); the induced action on L / n0 is sl_2.
    n0 = vec({1: 1, 3: 1})
    stab_n = nullspace([[apply(d, n0)[r] for d in ders] for r in range(8)])
    hn = [
        [
            [sum((coef_ * ders[i][r][s] for i, coef_ in enumerate(comb)), Fraction(0)) for s in range(8)]
            for r in range(8)
        ]
        for comb in stab_n
    ]
    cross_n = [[ocross(n0, unit_vec(8, s))[r] for s in range(8)] for r in range(8)]
    lker = [w for w in nullspace([row[1:] for row in cross_n[1:]])]
    lvecs = [[Fraction(0), *w] for w in lker]
    l_ok = (
        len(lvecs) == 3
        and qrank([*lvecs, n0]) == 3
        and all(eta(a, b) == 0 for a in lvecs for b in lvecs)
        and all(eta(a, n0) == 0 for a in lvecs)
        and all(qrank([*lvecs, apply(d, w)]) == 3 for d in hn for w in lvecs)
    )
    # Induced action on L / n0: pick a complement pair in L and project away n0.
    comp = [w for w in lvecs if qrank([n0, w]) == 2][:1]
    for w in lvecs:
        if len(comp) == 2:
            break
        if qrank([n0, *comp, w]) == len(comp) + 2:
            comp.append(w)
    sl2 = 0
    if len(comp) == 2:
        mats = []
        for d in hn:
            cols = []
            for w in comp:
                image = apply(d, w)
                sol = nullspace([[n0[r], comp[0][r], comp[1][r], -image[r]] for r in range(8)])
                sol = [s for s in sol if s[-1] != 0]
                cols.append([sol[0][1] / sol[0][3], sol[0][2] / sol[0][3]] if sol else [Fraction(0), Fraction(0)])
            m2 = [[cols[c][r] for c in range(2)] for r in range(2)]
            tr = (m2[0][0] + m2[1][1]) / 2
            mats.append([m2[0][0] - tr, m2[0][1], m2[1][0], m2[1][1] - tr])
        sl2 = qrank(mats)
    p4s_b = vec(SLICE_PLANES["P4s"][1])
    p4g_b = vec(SLICE_PLANES["P4g"][1])
    out["F4"] = {
        "n0_null": eta(n0, n0) == 0,
        "stabilizer_dimension": len(hn),
        "kernel_L_ok": l_ok,
        "sl2_rank_on_L_mod_n0": sl2,
        "P4s_special": eta(p4s_b, p4s_b) == 0 and eta(p4s_b, n0) == 0 and ocross(n0, p4s_b) == [0] * 8,
        "P4g_generic": eta(p4g_b, p4g_b) == 0 and eta(p4g_b, n0) == 0 and ocross(n0, p4g_b) != [0] * 8,
        "hn": [[[str(x) for x in row] for row in d] for d in hn],
        "lvecs": [[str(x) for x in w] for w in lvecs],
    }
    # Equivariance: D + D on the split sedenions is a derivation, and C'_z transforms by it.
    ders16 = derivations(SPLIT16)
    lifts = []
    for d in ders:
        big = [[Fraction(0)] * 16 for _ in range(16)]
        for r in range(8):
            for s in range(8):
                big[r][s] = d[r][s]
                big[8 + r][8 + s] = -d[r][s] if mutation == "lift_sign" else d[r][s]
        lifts.append(big)
    lift_ok = all(parallel.ordered_map(InSpan([flat(d) for d in ders16]), [flat(b) for b in lifts]))
    equiv = parallel.ordered_map(congruence_holds, lifts)
    integral = all(x.denominator == 1 for big in lifts for row in big for x in row)
    out["equivariance"] = {
        "sedenion_derivation_dimension": len(ders16),
        "lifts_are_derivations": lift_ok,
        "integral_lifts": integral,
        "congruence_M(Dz)=-(D^T M + M D)": all(equiv),
    }
    out["pass"] = bool(
        out["derivation_dimension"] == 14
        and out["preserve_im_and_eta"]
        and inner_ok
        and identity_ok
        and len(h) == 8
        and ksq_on_perp
        and [len(vplus), len(vminus)] == [3, 3]
        and iso
        and pairing == 3
        and commutes
        and sl3_rank == 8
        and traceless
        and sorted(types.values()) == ["V+", "V-", "mixed"]
        and all(nulls.values())
        and out["slice_frames"]["P3c_split_pairing_zero"]
        and out["slice_frames"]["P2_second_vector_type"] == "mixed"
        and all(v == 6 for v in out["F3"].values())
        and out["F4"]["n0_null"]
        and len(hn) == 8
        and l_ok
        and sl2 == 3
        and out["F4"]["P4s_special"]
        and out["F4"]["P4g_generic"]
        and lift_ok
        and integral
        and all(equiv)
    )
    return out


def isotropic_plane_job(mutation: str = "") -> dict[str, Any]:
    """Planes span(n0, x), x null in n0-perp: the H-orbit has dimension 3 off L.

    rank [h_1 x, .., h_8 x, n0, x] = 5 means the orbit of the plane has dimension 3 in the quadric of isotropic planes
    through n0. The script decides V(5 x 5 minors, eta(x), eta(n0, x)) inside L by radical membership of the linear
    forms that cut out L.
    """
    facts = g2_facts()
    hn = [
        [[flint.fmpq(Fraction(x).numerator, Fraction(x).denominator) for x in row] for row in d]
        for d in facts["F4"]["hn"]
    ]
    lvecs = [[Fraction(x) for x in w] for w in facts["F4"]["lvecs"]]
    n0 = [1 if j in (1, 3) else 0 for j in range(8)]
    ctx = flint.fmpq_mpoly_ctx.get(X_VARS, "degrevlex")
    xs = [ctx.gens()[0] * 0, *ctx.gens()]
    columns = [apply(d, xs) for d in hn] + [[ctx.gens()[0] * 0 + n0[r] for r in range(8)], xs]
    entries = [[columns[c][r] for c in range(len(columns))] for r in range(1, 8)]
    forms = nullspace([[w[r] for r in range(1, 8)] for w in lvecs])
    lforms = [sum((int(f[j]) * xs[j + 1] for j in range(7)), xs[0] * 0) for f in forms]
    mat_text = ",\n".join(str(e) for row in entries for e in row)
    script = "\n".join(
        [
            'LIB "primdec.lib";',
            ring_text(X_VARS),
            "option(redSB);",
            SINGULAR_PROCS,
            f"matrix M[7][{len(columns)}] = {mat_text};",
            f"ideal I = minor(M, 5), {eta(n0, xs)};"
            if mutation == "iso_no_eta"
            else f"ideal I = minor(M, 5), {eta(xs, xs)}, {eta(n0, xs)};",
            ideal_text("F", lforms),
            '"RESULT forms_in_radical", inrad(F, I);',
            f'"RESULT linear_forms", {len(lforms)};',
            "quit;",
        ]
    )
    res = run_singular(script)
    ok = res.get("forms_in_radical") == "1" and len(lforms) == 4 and "singular_error" not in res
    return {"pass": ok, **res}


# ---------------------------------------------------------------------------------------------------------------
# Identities for the case analysis of Ehat and rational points


def identity_checks() -> dict[str, Any]:
    """Over Z[x, y] in split coordinates, the cross-product identities the case analysis of Ehat uses.

    eta(x ^ y, x) = eta(x ^ y, y) = 0, x ^ y = -(y ^ x), x ^ (x ^ y) = alpha eta(x, y) x + beta eta(x) y and the
    Lagrange identity eta(x ^ y) = lam (eta(x) eta(y) - eta(x, y)^2), with the signs alpha, beta, lam read off.
    """
    ctx = flint.fmpz_mpoly_ctx.get(
        tuple(f"x{k}" for k in range(1, 8)) + tuple(f"y{k}" for k in range(1, 8)), "degrevlex"
    )
    g = ctx.gens()
    zero = g[0] * 0
    xs = [zero, *g[0:7]]
    ys = [zero, *g[7:14]]
    xy = ocross(xs, ys)
    orth = eta(xy, xs) == 0 and eta(xy, ys) == 0
    anti = all(a == -b for a, b in zip(xy, ocross(ys, xs), strict=True))
    dc = ocross(xs, xy)
    found = None
    for alpha in (-1, 1):
        for beta in (-1, 1):
            if all(dc[j] == alpha * eta(xs, ys) * xs[j] + beta * eta(xs, xs) * ys[j] for j in range(8)):
                found = (alpha, beta)
    gram = eta(xs, xs) * eta(ys, ys) - eta(xs, ys) ** 2
    lam = next((sign for sign in (-1, 1) if eta(xy, xy) == sign * gram), None)
    ok = orth and anti and found is not None and lam is not None
    return {
        "pass": ok,
        "orthogonal": orth,
        "anticommutative": anti,
        "double_cross_alpha_beta": found,
        "lagrange_sign": lam,
    }


def l_matrix(y: Sequence[Fraction]) -> list[list[Fraction]]:
    return [list(r) for r in left_mult_matrix_exact(32, list(y))]


def y_from_split(zp: Sequence[Fraction]) -> list[Fraction]:
    """y in A_5 for a split point with Gaussian-rational original coordinates; returns None if not real."""
    y = [Fraction(0)] * 32
    for k in range(1, 16):
        unit = [(1, 0), (0, 1), (-1, 0), (0, -1)][popcount(k) % 4]
        y[k] = unit[0] * zp[k - 1]
        y[16 + k] = unit[1] * zp[k - 1]
    return y


def nullity(y: Sequence[Fraction]) -> int:
    return 32 - qrank(l_matrix(y))


def point_checks() -> dict[str, Any]:
    """Rational split points: nullity of L_y, piece membership, and the Jacobian rank of Ehat at an E8 point."""
    ctx = global_ctx()
    gens = list(ctx.gens())
    pcs = piece_ideals(gens)

    def member(name: str, zp: Sequence[int]) -> bool:
        return all(int(p(*zp)) == 0 for p in pcs[name])

    def split_point(u: dict[int, int], mu: int, v: dict[int, int]) -> list[int]:
        zp = [0] * 15
        for j, x in u.items():
            zp[j - 1] = x
        zp[7] = mu
        for j, x in v.items():
            zp[7 + j] = x
        return zp

    p3a = split_point({2: 1, 3: 1, 1: 3}, 4, {2: 2, 3: 2, 1: 5})  # (a, b, c, d, m) = (1, 3, 2, 5, 4)
    rows = []
    reps = {
        "E8 (P3a)": (p3a, 8, "Ehat"),
        "W8 hyperbolic": (split_point({1: 1}, 0, {3: 1}), 8, "W8"),
        "V": (split_point({1: 3}, 4, {1: 5}), 12, "V"),
        "B9 (P4s)": (split_point({1: 1, 3: 1, 4: 2, 6: 2}, 0, {1: 3, 3: 3, 4: 5, 6: 5}), 12, "B9"),
        "N_+": (split_point({1: 1, 3: 1}, 0, {1: 1, 3: 1}), 16, "Np"),
        "N_-": (split_point({1: 1, 3: 1}, 0, {1: -1, 3: -1}), 16, "Nm"),
    }
    for label, (zp, expect, piece) in reps.items():
        nul = nullity(y_from_split([Fraction(x) for x in zp]))
        rows.append(
            {
                "point": label,
                "nullity": nul,
                "expected": expect,
                "in_piece": member(piece, zp),
                "in_Ehat": member("Ehat", zp),
                "in_W8": member("W8", zp),
            }
        )
    # Jacobian of the Ehat generators at the E8 point: rank 4 = codimension of an 11-dimensional variety.
    jac = [[int(p.derivative(k)(*p3a)) for k in range(15)] for p in pcs["Ehat"]]
    jrank = qrank(jac)
    ok = all(bool(r["nullity"] == r["expected"] and r["in_piece"]) for r in rows)
    ok = ok and bool(rows[0]["in_Ehat"] and not rows[0]["in_W8"] and not rows[1]["in_Ehat"]) and jrank == 4
    # Q on the P3a slice is the rank-3 form d^2 - b^2 - m^2, so {Q = 0} there is an irreducible quadric cone times C^2.
    sctx = flint.fmpz_mpoly_ctx.get(SLICE_VARS, "degrevlex")
    _, b, _, d, m = sctx.gens()
    q_p3a = piece_ideals(slice_point("P3a", sctx))["QG"][0]
    q_form = d * d - b * b - m * m
    q_ok = q_p3a in (q_form, -q_form)
    return {
        "pass": ok and q_ok,
        "rows": rows,
        "ehat_jacobian_rank_at_E8_point": jrank,
        "Q_on_P3a": str(q_p3a),
    }


# ---------------------------------------------------------------------------------------------------------------
# Driver


def global_pass(rows: Sequence[dict[str, Any]]) -> bool:
    by = {r["job"]: r for r in rows}
    s = by["ehat_structure"]
    ok = s.get("dim") == "11" and s.get("ehat_vanishes_on_V") == "1" and s.get("ehat_vanishes_on_B9") == "1"
    ok = ok and s.get("saturation_equals_ehat") == "1"
    ok = ok and s.get("degree") == "24" and s.get("piece_dims") == "12 8 9 6 6"
    # Ideal membership decides containment; the radical is computed, and read, only where membership fails.
    for job, names in (("pf12", ("Ehat", "W8")), ("pf10", ("V", "B9")), ("pf8", ("Np", "Nm"))):
        for nm in names:
            row = by[job]
            ok = ok and (row.get(f"in_ideal_{nm}") == "1" or row.get(f"in_radical_{nm}") == "1")
    return ok and not any("singular_error" in r for r in rows)


def self_test() -> list[str]:
    """Mutation controls: each mutated check returns an explicit 0 from Singular or a failed exact check."""
    failures = []
    bad = slice_job(("P3a", 12, "ehat_no_q"))
    if bad.get("piece_Ehat_in_R") != "0" or "singular_error" in bad:
        failures.append("Ehat without Q lay inside the P3a order-12 Pfaffian variety")
    bad = slice_job(("P2", 12, "w8_sign"))
    if bad.get("piece_W8_in_R") != "0" or "singular_error" in bad:
        failures.append("W8 with u.u = -v.v lay inside the P2 order-12 Pfaffian variety")
    control = slice_job(("P2", 10, "w8_sign"))
    if not control["pass"]:
        failures.append("the order-10 P2 slice, which reads no W8 equation, failed under the W8 mutation")
    facts = g2_facts("p3c_radical_in_vplus")
    if facts["slice_frames"]["radical_types"]["P3c"] != "V+" or facts["pass"]:
        failures.append("a P3c radical inside V_+ passed the slice-frame check")
    res = global_job(("pf12", "w8_sign"))
    if res.get("in_ideal_W8") != "0" or res.get("in_radical_W8") != "0" or res.get("in_ideal_Ehat") != "1":
        failures.append("the order-12 Pfaffians lie in the radical of W8 with u.u = -v.v")
    res = global_job(("ehat_structure", "ehat_plus_w8"))
    if res.get("saturation_equals_ehat") != "0":
        failures.append("Ehat with the W8 component added survived saturation by f")
    res = isotropic_plane_job("iso_no_eta")
    if res.get("forms_in_radical") != "0":
        failures.append("the isotropic-plane certificate held without the null condition eta(x) = 0")
    if g2_facts("lift_sign")["equivariance"]["lifts_are_derivations"]:
        failures.append("a lift D + (-D) passed as a derivation of the split sedenions")
    bad = slice_job(("P2", 12, "union_drops_ehat"))
    if bad.get("R_in_union") != "0" or "singular_error" in bad:
        failures.append("the P2 order-12 Pfaffian variety lay inside W8 alone")
    return failures


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", type=Path)
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if shutil.which(SINGULAR) is None:
        print("Singular is not on PATH")
        return 2
    if args.self_test:
        failures = self_test()
        for line in failures:
            print("FAIL", line)
        print(f"rederive_strata_equations self-test: {9 - len(failures)} of 9 controls behaved as required")
        return 1 if failures else 0
    t0 = time.perf_counter()
    report: dict[str, Any] = {}
    timings: dict[str, float] = {}

    def run(key: str, fn: Callable[[], Any]) -> None:
        start = time.perf_counter()
        report[key] = fn()
        timings[key] = round(time.perf_counter() - start, 2)
        print(f"{key:12s} pass={report[key].get('pass')} {timings[key]:8.2f} s", flush=True)

    run("tables", table_checks)
    run("identities", identity_checks)
    run("g2", g2_facts)
    run("isotropic", isotropic_plane_job)
    run("points", point_checks)

    def slices() -> dict[str, Any]:
        jobs = [(name, order, "") for name in SLICE_PLANES for order in (12, 10, 8)]
        rows = parallel.ordered_map(slice_job, jobs, min_items=1)
        return {"pass": all(r["pass"] for r in rows), "rows": rows}

    def global_() -> dict[str, Any]:
        jobs = [("ehat_structure", ""), ("pf12", ""), ("pf10", ""), ("pf8", "")]
        rows = parallel.ordered_map(global_job, jobs, min_items=1)
        return {"pass": global_pass(rows), "rows": rows}

    run("slices", slices)
    run("global", global_)
    report["g2"]["F4"].pop("hn")
    report["g2"]["F4"].pop("lvecs")
    report["timings_s"] = timings
    report["total_s"] = round(time.perf_counter() - t0, 2)
    report["workers"] = parallel.workers()
    report["script_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    report["versions"] = {
        "python": sys.version.split()[0],
        "python-flint": flint.__version__,
        "singular": singular_version(),
    }
    if args.out:
        args.out.write_text(json.dumps(report, indent=1, default=str) + "\n", encoding="utf-8")
    failed = [k for k, v in report.items() if isinstance(v, dict) and v.get("pass") is False]
    print(f"total {report['total_s']} s; failed: {', '.join(failed) or 'none'}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
