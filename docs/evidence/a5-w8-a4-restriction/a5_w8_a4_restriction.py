"""Restriction of the A_5 W8 closure ideal to the embedded A_4 coordinates, against the A_4 zero-divisor ideals.

The script builds, with exact integer polynomial arithmetic, the ideals that the Singular comparison reads and checks
them pointwise against cd_core.

W8 comes from the strata records ([a5-rank-strata-equations](../a5-rank-strata-equations/README.md)): in the complex
coordinates z_k = x_k + i x_(16+k), k = 1..15, of a doubly pure y of A_5 the piece W8 is mu = 0, U = V, W = 0 with
u = z_1..z_7, mu = z_8, v = z_9..z_15, U = u.u, V = v.v, W = u.v. The ideal in the 32 real coordinates holds the real
and imaginary part of every generator and the doubly pure equations x_0 = x_16 = 0. Setting x_16..x_31 = 0 restricts it
to the embedded A_4.

Three A_4 zero-divisor ideals are built from Pfaffians of left multiplication, the way the A_5 records build their rank
loci. Every nullity-4 element of A_4 has y_0 = 0, and a skew matrix has rank at most 2r exactly when its principal
Pfaffians of order 2r + 2 vanish.

- PB: the doubly pure encoding w_k = y_k + i y_(8+k), k = 1..7, with the 7 x 7 Im-block C_w of left multiplication by
  w on the complexified octonions. nullity L_y = 12 - 2 rank C_w, so nullity 4 means rank C_w <= 4, the order-6
  principal Pfaffians. The real and imaginary part of each, with y_0 and y_8, generate PB.
- PA: the order-14 principal Pfaffians of the 16 x 16 skew matrix L_y at y_0 = 0, with y_0.
- PAp: the order-12 principal Pfaffians of the 15 x 15 Im-block of L_y at y_0 = 0, the restriction of the A_5 order-12
  Pfaffian ideal of R_8, with y_0.

Each ideal is written for Singular over F_32009 in the ring y0..y15.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
import json
import sys
import time
from pathlib import Path
from typing import Any

import flint

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

from cd_core import (  # noqa: E402
    cd_sign,
    left_mult_matrix_exact,
    sedenion_zero_divisor_corpus,
)

_SPEC = importlib.util.spec_from_file_location(
    "rederive_strata_equations", ROOT / "docs/evidence/a5-rank-strata-equations/rederive_strata_equations.py"
)
assert _SPEC is not None and _SPEC.loader is not None  # noqa: S101 -- import guard, outside tests
REC = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(REC)

PRIME = 32009
Y_NAMES = tuple(f"y{k}" for k in range(16))
X_NAMES = tuple(f"x{k}" for k in range(32))
GP = REC.GP


def check(cond: bool, message: str) -> None:
    if not cond:
        raise RuntimeError(message)


def popcount(k: int) -> int:
    return bin(k).count("1")


# ---------------------------------------------------------------------------------------------------------------
# Exact matrices


def qrank(rows: list[list[Any]]) -> int:
    return int(flint.fmpq_mat([[flint.fmpq(x.numerator, x.denominator) for x in r] for r in rows]).rank())


def nullity_exact(dim: int, vec: list[int]) -> int:
    return dim - qrank([list(r) for r in left_mult_matrix_exact(dim, vec)])


def gauss_rank(a: list[list[int]], b: list[list[int]]) -> int:
    """Rank over C of A + iB for integer matrices, as half the rank of the real block [[A, -B], [B, A]]."""
    n = len(a)
    block = [[0] * (2 * n) for _ in range(2 * n)]
    for r in range(n):
        for c in range(n):
            block[r][c] = a[r][c]
            block[r][n + c] = -b[r][c]
            block[n + r][c] = b[r][c]
            block[n + r][n + c] = a[r][c]
    rank = int(flint.fmpz_mat(block).rank())
    check(rank % 2 == 0, "real block rank of a complex matrix is even")
    return rank // 2


def cw_entries(w: list[tuple[int, int]]) -> tuple[list[list[int]], list[list[int]]]:
    """Real and imaginary part of the 7 x 7 Im-block C_w, entry (a, b) = cd_sign(8, a^b, b) w_(a^b), a, b in 1..7."""
    re = [[0] * 7 for _ in range(7)]
    im = [[0] * 7 for _ in range(7)]
    for a in range(1, 8):
        for b in range(1, 8):
            k = a ^ b
            if k:
                s = cd_sign(8, k, b)
                re[a - 1][b - 1] = s * w[k - 1][0]
                im[a - 1][b - 1] = s * w[k - 1][1]
    return re, im


def doubly_pure_identities(flip: bool = False) -> dict[str, Any]:
    """J = L_(e_8) on A_4 squares to -I, anticommutes with L_(e_k) for k not in {0, 8}, and every L_(e_k) is skew."""

    def lmat(k: int) -> list[list[int]]:
        m = [[int(x) for x in r] for r in left_mult_matrix_exact(16, [1 if t == k else 0 for t in range(16)])]
        return m

    def mm(a: list[list[int]], b: list[list[int]]) -> list[list[int]]:
        return [[sum(a[i][t] * b[t][j] for t in range(16)) for j in range(16)] for i in range(16)]

    j = lmat(8)
    if flip:
        j[0][0] += 1
    ident = [[int(r == c) for c in range(16)] for r in range(16)]
    sq = mm(j, j)
    j_squares = all(sq[r][c] == -ident[r][c] for r in range(16) for c in range(16))
    skew = True
    anti = True
    for k in range(1, 16):
        m = lmat(k)
        skew &= all(m[r][c] == -m[c][r] for r in range(16) for c in range(16))
        if k != 8:
            jm, mj = mm(j, m), mm(m, j)
            anti &= all(jm[r][c] == -mj[r][c] for r in range(16) for c in range(16))
    return {
        "J_squares_to_minus_I": j_squares,
        "all_L_ek_skew": skew,
        "J_anticommutes": anti,
        "pass": j_squares and skew and anti,
    }


# ---------------------------------------------------------------------------------------------------------------
# Polynomial ideals


def y_ctx() -> Any:
    return flint.fmpz_mpoly_ctx.get(Y_NAMES, "degrevlex")


def x_ctx() -> Any:
    return flint.fmpz_mpoly_ctx.get(X_NAMES, "degrevlex")


def w8_ideal_32(mutation: str = "") -> list[Any]:
    """Real and imaginary parts of mu, U - V, W in the 32 real coordinates, with x_0 and x_16.

    The generators are the original-coordinate definitions of the strata record: z_k = x_k + i x_(16+k).
    """
    ctx = x_ctx()
    x = ctx.gens()
    zero = ctx.from_dict({})
    z = [GP(x[k], x[16 + k]) for k in range(1, 16)]
    u, mu, v = z[0:7], z[7], z[8:15]
    big_u, big_v, big_w = REC.gdot(u, u), REC.gdot(v, v), REC.gdot(u, v)
    diff = big_u + big_v if mutation == "w8_sign" else big_u - big_v
    gens: list[Any] = [mu.re, mu.im, diff.re, diff.im, big_w.re, big_w.im]
    if mutation != "w8_no_pure":
        gens += [x[0], x[16]]
    out: list[Any] = []
    seen: set[str] = set()
    for g in gens:
        if g != zero and str(g) not in seen:
            seen.add(str(g))
            out.append(g)
    return out


def restrict_to_a4(gens: list[Any]) -> list[Any]:
    """Substitute x_16..x_31 = 0 and rename x_k to y_k: the image of the ideal in the ring of the embedded A_4."""
    yc = y_ctx()
    y = yc.gens()
    zero = yc.from_dict({})
    images = [*y, *[zero] * 16]
    out: list[Any] = []
    seen: set[str] = set()
    for g in gens:
        h = _compose(g, images, yc)
        if h != zero and str(h) not in seen:
            seen.add(str(h))
            out.append(h)
    return out


def _compose(g: Any, images: list[Any], target: Any) -> Any:
    total = target.from_dict({})
    for exps, coeff in g.to_dict().items():
        term = target.from_dict({tuple([0] * 16): int(coeff)})
        for idx, e in enumerate(exps):
            if e:
                term = term * images[idx] ** e
        total = total + term
    return total


def pf_generic(mat: list[list[Any]], order: int, zero: Any, one: Any) -> list[Any]:
    """Distinct nonzero principal Pfaffians of the given order, by expansion along the first row with memo."""
    memo: dict[tuple[int, ...], Any] = {(): one}

    def pf(s: tuple[int, ...]) -> Any:
        hit = memo.get(s)
        if hit is not None:
            return hit
        total = zero
        for j in range(1, len(s)):
            entry = mat[s[0]][s[j]]
            if _is_zero(entry):
                continue
            term = entry * pf(s[1:j] + s[j + 1 :])
            total = total + term if j % 2 else total - term
        memo[s] = total
        return total

    seen: dict[str, Any] = {}
    for s in itertools.combinations(range(len(mat)), order):
        p = pf(s)
        if not _is_zero(p):
            seen.setdefault(_key(p), p)
    return list(seen.values())


def _is_zero(p: Any) -> bool:
    return bool(p.iszero()) if isinstance(p, GP) else bool(p == 0)


def _key(p: Any) -> str:
    return f"{p.re}|{p.im}" if isinstance(p, GP) else str(p)


def pb_ideal(mutation: str = "") -> tuple[list[Any], list[Any]]:
    """PB: real and imaginary part of every order-6 principal Pfaffian of C_w, with y_0 and y_8.

    Returns the generators and the seven complex Pfaffians (as GP) for the structure check Pf_j = +-(w.w) w_j.
    """
    ctx = y_ctx()
    y = ctx.gens()
    zero = ctx.from_dict({})
    one = zero + 1
    gzero, gone = GP(zero, zero), GP(one, zero)
    w = [GP(y[k], y[8 + k]) for k in range(1, 8)]
    mat = [[gzero] * 7 for _ in range(7)]
    for a in range(1, 8):
        for b in range(1, 8):
            k = a ^ b
            if k:
                mat[a - 1][b - 1] = cd_sign(8, k, b) * w[k - 1]
    for a in range(7):
        for b in range(7):
            check(
                (mat[a][b] + mat[b][a]).iszero(),
                "C_w is not skew",
            )
    order = 6 if mutation != "pb_order4" else 4
    pfs = pf_generic(mat, order, gzero, gone)
    gens: list[Any] = [y[0], y[8]]
    seen: set[str] = {str(y[0]), str(y[8])}
    for p in pfs:
        for part in (p.re, p.im):
            if part != zero:
                neg = -part
                if str(part) not in seen and str(neg) not in seen:
                    seen.add(str(part))
                    gens.append(part)
    return gens, pfs


def pa_ideal() -> list[Any]:
    """PA: order-14 principal Pfaffians of the 16 x 16 skew matrix L_y at y_0 = 0, with y_0."""
    ctx = y_ctx()
    y = ctx.gens()
    zero = ctx.from_dict({})
    mat = [[zero] * 16 for _ in range(16)]
    for r in range(16):
        for c in range(16):
            k = r ^ c
            if k:
                mat[r][c] = cd_sign(16, k, c) * y[k]
    for r in range(16):
        for c in range(16):
            check(mat[r][c] == -mat[c][r], "L_y at y_0 = 0 is not skew")
    return [y[0], *pf_generic(mat, 14, zero, zero + 1)]


def pap_ideal() -> list[Any]:
    """PAp: order-12 principal Pfaffians of the 15 x 15 Im-block of L_y at y_0 = 0, with y_0."""
    ctx = y_ctx()
    y = ctx.gens()
    zero = ctx.from_dict({})
    mat = [[zero] * 15 for _ in range(15)]
    for a in range(1, 16):
        for b in range(1, 16):
            k = a ^ b
            if k:
                mat[a - 1][b - 1] = cd_sign(16, k, b) * y[k]
    return [y[0], *pf_generic(mat, 12, zero, zero + 1)]


def j_ideal() -> list[Any]:
    """The W8 closure ideal restricted to the embedded A_4."""
    return restrict_to_a4(w8_ideal_32())


# ---------------------------------------------------------------------------------------------------------------
# Singular text


def sing_ideal(name: str, gens: list[Any]) -> str:
    body = ",\n".join(str(g) for g in gens)
    return f"ideal {name} = {body};\n"


def write_text(path: Path, text: str) -> str:
    path.write_text(text, encoding="utf-8")
    return hashlib.sha256(text.encode()).hexdigest()


# ---------------------------------------------------------------------------------------------------------------
# Pointwise controls


def two_term_zero_divisors() -> list[list[int]]:
    """Every element e_i + t e_j (t = +-1) that occurs in the corpus as a left or right factor, as 16-vectors."""
    ops: set[tuple[int, int, int]] = set()
    for i, j, t, k, el, s in sedenion_zero_divisor_corpus():
        ops.add((i, j, t))
        ops.add((k, el, s))
    out = []
    for i, j, t in sorted(ops):
        v = [0] * 16
        v[i], v[j] = 1, t
        out.append(v)
    return out


def invertible_points() -> list[list[int]]:
    """Deterministic integer points of A_4 at y_0 = y_8 = 0 (and one family with y_0 != 0) of nullity 0."""
    pts: list[list[int]] = []
    for j in range(40):
        v = [((k * k * 7 + j * 13 + 3) % 11) - 5 for k in range(16)]
        v[0] = v[8] = 0
        pts.append(v)
    return pts


def evaluate(gens: list[Any], point: list[int]) -> list[int]:
    return [int(g(*point)) for g in gens]


def pointwise(ideals: dict[str, list[Any]], j_gens: list[Any]) -> dict[str, Any]:
    zds = two_term_zero_divisors()
    result: dict[str, Any] = {"zero_divisors": len(zds)}
    nul = {nullity_exact(16, v) for v in zds}
    nul32 = {nullity_exact(32, [*v, *[0] * 16]) for v in zds}
    result["nullity_L_a_on_zero_divisors"] = sorted(nul)
    result["nullity_L_(a,0)_on_zero_divisors"] = sorted(nul32)
    on = {name: all(not any(evaluate(gens, v)) for v in zds) for name, gens in ideals.items()}
    on["J"] = all(not any(evaluate(j_gens, v)) for v in zds)
    result["ideals_vanish_on_all_zero_divisors"] = on
    # The unrestricted 32-coordinate W8 ideal vanishes at the embedded points (a, 0).
    w8 = w8_ideal_32()
    result["W8_32_vanishes_on_embedded_zero_divisors"] = all(not any(evaluate(w8, [*v, *[0] * 16])) for v in zds)
    inv = invertible_points()
    nul_inv = {nullity_exact(16, v) for v in inv}
    result["nullity_L_a_on_invertible_points"] = sorted(nul_inv)
    result["invertible_points"] = len(inv)
    off = {name: all(any(evaluate(gens, v)) for v in inv) for name, gens in ideals.items()}
    off["J"] = all(any(evaluate(j_gens, v)) for v in inv)
    result["each_ideal_nonzero_at_every_invertible_point"] = off
    result["pass"] = (
        nul == {4}
        and nul32 == {8}
        and nul_inv == {0}
        and all(on.values())
        and all(off.values())
        and result["W8_32_vanishes_on_embedded_zero_divisors"]
    )
    return result


def transport_check() -> dict[str, Any]:
    """nullity L_y = 12 - 2 rank C_w at the zero divisors and at integer points of y_0 = y_8 = 0."""
    pts = [*two_term_zero_divisors(), *invertible_points()]
    # a rank-2 and a rank-0 style point: vectors supported on one coordinate pair and a single basis vector
    for k in (1, 9):
        v = [0] * 16
        v[k] = 1
        pts.append(v)
    rows = []
    ok = True
    for v in pts:
        w = [(v[k], v[8 + k]) for k in range(1, 8)]
        re, im = cw_entries(w)
        rank = gauss_rank(re, im)
        nul = nullity_exact(16, v)
        rows.append((nul, rank))
        ok &= nul == 12 - 2 * rank
    return {"points": len(pts), "pairs_nullity_rank": sorted(set(rows)), "pass": ok}


def structure_pf(pfs: list[Any]) -> dict[str, Any]:
    """The seven order-6 Pfaffians of C_w equal +-(w.w) w_j, so PB = (w.w) m over C."""
    ctx = y_ctx()
    y = ctx.gens()
    w = [GP(y[k], y[8 + k]) for k in range(1, 8)]
    ww = REC.gdot(w, w)
    targets = [ww * w[j] for j in range(7)]
    matched = 0
    for p in pfs:
        for t in targets:
            if (p.re == t.re and p.im == t.im) or (p.re == -t.re and p.im == -t.im):
                matched += 1
                break
    return {"pfaffians": len(pfs), "matching_ww_times_w_j": matched, "pass": matched == len(pfs) == 7}


def w8_crosscheck() -> dict[str, Any]:
    """The original-coordinate generators equal the record's split-coordinate W8 generators up to a unit.

    At each integer split point z', z_k = i^popcount(k) z'_k; the record's piece_ideals W8 generators are the unit
    multiples of mu, U - V, W at that point.
    """
    gctx = REC.global_ctx()
    zp_polys = list(gctx.gens())
    rec_gens = REC.piece_ideals(zp_polys)["W8"]
    check(len(rec_gens) == 3, "W8 has three generators in the record")
    units = {0: (1, 0), 1: (0, 1), 2: (-1, 0), 3: (0, -1)}
    ok = True
    rows = 0
    for j in range(40):
        zprime = [((k * k * 5 + j * 17 + 1) % 13) - 6 for k in range(1, 16)]
        zc = []
        for k in range(1, 16):
            re, im = units[popcount(k) % 4]
            zc.append((re * zprime[k - 1], im * zprime[k - 1]))
        # original coordinate value c = (mu, U - V, W) as Gaussian integers
        mu = zc[7]

        def dot(p: list[tuple[int, int]], q: list[tuple[int, int]]) -> tuple[int, int]:
            re = sum(a[0] * b[0] - a[1] * b[1] for a, b in zip(p, q, strict=True))
            im = sum(a[0] * b[1] + a[1] * b[0] for a, b in zip(p, q, strict=True))
            return re, im

        uu, vv, uv = dot(zc[0:7], zc[0:7]), dot(zc[8:15], zc[8:15]), dot(zc[0:7], zc[8:15])
        mine = [mu, (uu[0] - vv[0], uu[1] - vv[1]), uv]
        theirs = [int(g(*zprime)) for g in rec_gens]
        for (cr, ci), r in zip(mine, theirs, strict=True):
            rows += 1
            if r == 0:
                ok &= cr == 0 and ci == 0
            else:
                ok &= (cr, ci) in {(r, 0), (0, r), (-r, 0), (0, -r)}
    return {"points": 40, "generator_comparisons": rows, "pass": ok}


def naive_construction_control() -> dict[str, Any]:
    """a = e_0 + s e_1 with s^2 = -1 mod p has nullity 8 at y_0 = 1: the 13 x 13 minors of the real 16 x 16 matrix
    describe the complexified rank locus, which is larger than the zero-divisor locus and carries y_0 != 0."""
    s = next(t for t in range(2, PRIME) if (t * t + 1) % PRIME == 0)
    a = [0] * 16
    a[0], a[1] = 1, s
    mat = [[int(x) % PRIME for x in r] for r in left_mult_matrix_exact(16, a)]
    rank = int(flint.nmod_mat(mat, PRIME).rank())
    return {"s": s, "y0": 1, "rank_L_a_mod_p": rank, "nullity_mod_p": 16 - rank, "pass": rank == 8}


def isotropic_witness(ideals: dict[str, list[Any]], j_gens: list[Any]) -> dict[str, Any]:
    """y = e_1 + s e_9 with s^2 = -1 mod p has Q = y.y = 0 and nullity 8, and U - V = 2 != 0.

    The point lies in V(PA) and V(PAp) and outside V(J) and V(PB): the Pfaffian loci of the real 16 x 16 matrix
    contain complex isotropic points that are no limit of real zero divisors.
    """
    s = next(t for t in range(2, PRIME) if (t * t + 1) % PRIME == 0)
    a = [0] * 16
    a[1], a[9] = 1, s
    mat = [[int(x) % PRIME for x in r] for r in left_mult_matrix_exact(16, a)]
    rank = int(flint.nmod_mat(mat, PRIME).rank())
    vanishes = {name: all(v % PRIME == 0 for v in evaluate(gens, a)) for name, gens in ideals.items()}
    vanishes["J"] = all(v % PRIME == 0 for v in evaluate(j_gens, a))
    return {
        "s": s,
        "rank_L_a_mod_p": rank,
        "nullity_mod_p": 16 - rank,
        "all_generators_vanish_mod_p": vanishes,
        "pass": rank == 8 and vanishes == {"PB": False, "PA": True, "PAp": True, "J": False},
    }


# ---------------------------------------------------------------------------------------------------------------
# Self-test mutations


def self_test() -> list[str]:
    """Each mutation must fail the check it targets; the unmutated ideals must pass them."""
    fails: list[str] = []
    zds = two_term_zero_divisors()
    e0 = [1] + [0] * 15

    def vanishes_on_zero_divisors(gens: list[Any]) -> bool:
        return all(not any(evaluate(gens, v)) for v in zds)

    def contains_identity(gens: list[Any]) -> bool:
        return not any(evaluate(gens, e0))

    if doubly_pure_identities(flip=True)["pass"]:
        fails.append("flipped J passes the doubly pure identities")
    j_ok = restrict_to_a4(w8_ideal_32())
    if not vanishes_on_zero_divisors(j_ok) or contains_identity(j_ok):
        fails.append("restricted W8 fails a control it must pass")
    if vanishes_on_zero_divisors(restrict_to_a4(w8_ideal_32("w8_sign"))):
        fails.append("the U + V version of W8 vanishes on every zero divisor")
    if not contains_identity(restrict_to_a4(w8_ideal_32("w8_no_pure"))):
        fails.append("W8 without x_0 = x_16 = 0 still excludes the invertible point e_0")
    pb_ok, _ = pb_ideal()
    if not vanishes_on_zero_divisors(pb_ok) or contains_identity(pb_ok):
        fails.append("PB fails a control it must pass")
    pb_bad, _ = pb_ideal("pb_order4")
    if vanishes_on_zero_divisors(pb_bad):
        fails.append("the order-4 Pfaffians of C_w vanish on every zero divisor")
    return fails


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", type=Path, help="directory for result.json, the Singular ideal files of J and PB")
    ap.add_argument("--work", type=Path, help="directory for the large Pfaffian ideal files PA and PAp")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        fails = self_test()
        for f in fails:
            print("FAIL", f)
        print(f"a5_w8_a4_restriction self-test: {'failed' if fails else 'all controls behaved as required'}")
        return 1 if fails else 0
    t0 = time.perf_counter()
    report: dict[str, Any] = {}

    def run(key: str, fn: Any) -> Any:
        start = time.perf_counter()
        value = fn()
        report[key] = value[0] if isinstance(value, tuple) else value
        print(f"{key:28s} pass={report[key].get('pass')} {time.perf_counter() - start:7.2f} s", flush=True)
        return value

    run("doubly_pure_dim16", doubly_pure_identities)
    run("w8_crosscheck", w8_crosscheck)
    run("transport", transport_check)
    run("naive_construction_control", naive_construction_control)
    j_gens = j_ideal()
    pb_gens, pfs = pb_ideal()
    run("pb_structure", lambda: structure_pf(pfs))
    pa_gens = pa_ideal()
    pap_gens = pap_ideal()
    ideals = {"PB": pb_gens, "PA": pa_gens, "PAp": pap_gens}
    run("pointwise", lambda: pointwise(ideals, j_gens))
    run("isotropic_witness", lambda: isotropic_witness(ideals, j_gens))
    report["generators"] = {"J": len(j_gens), **{k: len(v) for k, v in ideals.items()}}
    report["J_generators"] = [str(g) for g in j_gens]
    report["w8_32_generators"] = len(w8_ideal_32())
    hashes: dict[str, str] = {}
    if args.out:
        args.out.mkdir(parents=True, exist_ok=True)
        hashes["ring.sing"] = write_text(args.out / "ring.sing", f"ring r = {PRIME}, ({', '.join(Y_NAMES)}), dp;\n")
        hashes["ideal_J.sing"] = write_text(args.out / "ideal_J.sing", sing_ideal("J", j_gens))
        hashes["ideal_PB.sing"] = write_text(args.out / "ideal_PB.sing", sing_ideal("P", pb_gens))
        mutant = restrict_to_a4(w8_ideal_32("w8_sign"))
        hashes["ideal_Jsign.sing"] = write_text(args.out / "ideal_Jsign.sing", sing_ideal("Jm", mutant))
        nopure = restrict_to_a4(w8_ideal_32("w8_no_pure"))
        hashes["ideal_Jnopure.sing"] = write_text(args.out / "ideal_Jnopure.sing", sing_ideal("Jn", nopure))
    work = args.work or args.out
    if work:
        work.mkdir(parents=True, exist_ok=True)
        hashes["ideal_PA.sing"] = write_text(work / "ideal_PA.sing", sing_ideal("P", pa_gens))
        hashes["ideal_PAp.sing"] = write_text(work / "ideal_PAp.sing", sing_ideal("P", pap_gens))
    report["sing_sha256"] = hashes
    report["total_s"] = round(time.perf_counter() - t0, 2)
    report["script_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    report["versions"] = {"python": sys.version.split()[0], "python-flint": flint.__version__}
    failed = [k for k, v in report.items() if isinstance(v, dict) and v.get("pass") is False]
    if args.out:
        (args.out / "result.json").write_text(json.dumps(report, indent=1, default=str) + "\n", encoding="utf-8")
    print(f"total {report['total_s']} s; failed: {', '.join(failed) or 'none'}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
