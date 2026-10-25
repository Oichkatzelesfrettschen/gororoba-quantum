"""Independent checks of the stiefel-pfaffian-higher claims, built from cd_core.cd_multiply_exact only.

Usage: verify.py SECTION...   (sections: table transport degree irred witness pairs slices bcdi six small three mult)
"""

import itertools
import json
import random
import sys
from fractions import Fraction
from functools import cache
from pathlib import Path

import flint

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
from cd_core import cd_multiply_exact  # noqa: E402

# A prime p = 1 mod 4 (so sqrt(-1) exists), distinct from the script's 2^61 - 1.
P = next(q for q in range((1 << 62) - 1000, (1 << 62)) if q % 4 == 1 and flint.fmpz(q).is_prime())
IOTA = int(flint.nmod(P - 1, P).sqrt())
if IOTA * IOTA % P != P - 1:
    raise RuntimeError("no square root of -1 modulo P")
# Every seed is a value of the ANU QRNG draw docs/evidence/anu_qrng/draw-2026-10-25T221458Z.json, cited by index.
RNG = random.Random(20190)  # index 0
LINE_SEEDS = {6: 60101, 7: 35443, 8: 30416}  # indices 1, 2, 3; one stream per n across tries


def out(*a):
    print(*a, flush=True)


@cache
def table(dim):
    """T[p][q] = (r, s): e_p e_q = s e_r, read off cd_multiply_exact."""
    t = []
    for p_ in range(dim):
        row = []
        ep = [0] * dim
        ep[p_] = 1
        for q_ in range(dim):
            eq = [0] * dim
            eq[q_] = 1
            prod = cd_multiply_exact(dim, ep, eq)
            nz = [(i, v) for i, v in enumerate(prod) if v]
            if len(nz) != 1 or abs(nz[0][1]) != 1:
                raise RuntimeError("basis product not a signed basis vector")
            row.append((nz[0][0], int(nz[0][1])))
        t.append(row)
    return t


def left(dim, y):
    """L_y over Z: column c is y e_c."""
    t = table(dim)
    m = [[0] * dim for _ in range(dim)]
    for p_, v in enumerate(y):
        if v:
            for c in range(dim):
                r, s = t[p_][c]
                m[r][c] += s * v
    return m


def cross(half, z, mod=None):
    """C_z: (a, b) entry = e_a coefficient of z e_b in A_(n-1), a, b = 1 .. h-1; z indexed 1..h-1 as z[k-1]."""
    t = table(half)
    m = [[0] * (half - 1) for _ in range(half - 1)]
    for k in range(1, half):
        zk = z[k - 1]
        if zk:
            for b in range(1, half):
                r, s = t[k][b]
                if r != 0:
                    m[r - 1][b - 1] += s * zk
    if mod:
        m = [[x % mod for x in row] for row in m]
    return m


def rank_mod(m):
    return flint.nmod_mat(m, P).rank()


def fsq_mod(half, z):
    """f(z)^2 mod P from det(C_z without j)/z_j^2, z in F_P."""
    j = next(k for k in range(half - 1) if z[k] % P)
    c = cross(half, z, P)
    keep = [k for k in range(half - 1) if k != j]
    d = int(flint.nmod_mat([[c[a][b] for b in keep] for a in keep], P).det())
    return d * pow(z[j] * z[j], -1, P) % P


# ---------------------------------------------------------------- sections


def sec_table():
    for dim in (64, 128, 256):
        t = table(dim)
        out(
            f"table {dim}: built; e_p e_q index is p^q on all pairs:",
            all(t[p_][q_][0] == p_ ^ q_ for p_ in range(dim) for q_ in range(dim)),
        )
        # L_y against cd_multiply_exact on random dense vectors
        y = [RNG.randint(-3, 3) for _ in range(dim)]
        x = [RNG.randint(-3, 3) for _ in range(dim)]
        lm = left(dim, y)
        lx = tuple(Fraction(sum(lm[r][c] * x[c] for c in range(dim))) for r in range(dim))
        out(f"  L_y x == cd_multiply_exact at {dim}:", lx == cd_multiply_exact(dim, y, x))


def conj_vec(s):
    return [s[0]] + [-v for v in s[1:]]


def sec_transport():
    for n in (6, 7, 8):
        dim = 1 << n
        h = dim // 2
        bad = 0
        for k in range(dim):
            if k in (0, h):
                continue
            # y = e_k ; z = e_k (k<h) or i e_(k-h)
            zr = [0] * h
            zi = [0] * h
            if k < h:
                zr[k] = 1
            else:
                zi[k - h] = 1
            # A(z, conj z) as complex (re, im) h x h
            cr = cross(h, zr[1:])
            ci = cross(h, zi[1:])
            ar = [[0] * h for _ in range(h)]
            ai = [[0] * h for _ in range(h)]
            for a in range(1, h):
                # t = conj z = zr - i zi
                ar[a][0], ai[a][0] = zr[a], -zi[a]
                ar[0][a], ai[0][a] = -zr[a], zi[a]
                for b in range(1, h):
                    ar[a][b], ai[a][b] = cr[a - 1][b - 1], ci[a - 1][b - 1]
            y = [0] * dim
            y[k] = 1
            lm = left(dim, y)
            for c in range(dim):
                col = [lm[r][c] for r in range(dim)]
                r_, s_ = col[:h], col[h:]
                lhs_re, lhs_im = r_, conj_vec(s_)
                x = [0] * dim
                x[c] = 1
                xr, xs = x[:h], x[h:]
                w_re, w_im = xr, [-v for v in conj_vec(xs)]  # conj(phi(x)) = r - i conj(s)
                rhs_re = [sum(ar[a][b] * w_re[b] - ai[a][b] * w_im[b] for b in range(h)) for a in range(h)]
                rhs_im = [sum(ar[a][b] * w_im[b] + ai[a][b] * w_re[b] for b in range(h)) for a in range(h)]
                if rhs_re != lhs_re or rhs_im != lhs_im:
                    bad += 1
                    break
        out(f"transport A_{n}: basis y failing = {bad} of {dim - 2}")


def to_fp(re, im, sign=1):
    return [(a + sign * IOTA * b) % P for a, b in zip(re, im, strict=True)]


def sec_degree():
    """det L_y = N^4 f(z)^2 f(conj z)^2 mod P at random and structured doubly pure y."""
    for n, count in ((6, 6), (7, 3), (8, 2)):
        dim = 1 << n
        h = dim // 2
        pts = []
        for _ in range(count):
            y = [RNG.randint(-4, 4) for _ in range(dim)]
            y[0] = y[h] = 0
            pts.append(("random", y))
        # a pair e_1 + i e_2 (zero divisor) and a non-Stiefel
        y = [0] * dim
        y[1] = 1
        y[h + 2] = 1
        pts.append(("pair e1+ie2", y))
        for label, y in pts:
            pr, qi = y[1:h], y[h + 1 :]
            nn = sum(v * v for v in y)
            det = int(flint.nmod_mat(left(dim, y), P).det())
            a = fsq_mod(h, to_fp(pr, qi, 1))
            b = fsq_mod(h, to_fp(pr, qi, -1))
            ok = det == pow(nn, 4, P) * a % P * b % P
            out(f"degree A_{n} {label}: det==N^4|f|^4 mod p: {ok}; det==0: {det == 0}")


def newton_interp(xs, ys):
    """Coefficients (low first) of the interpolating polynomial over Q."""
    n = len(xs)
    coef = [Fraction(v) for v in ys]
    for j in range(1, n):
        for i in range(n - 1, j - 1, -1):
            coef[i] = (coef[i] - coef[i - 1]) / (xs[i] - xs[i - j])
    q = [flint.fmpq(c.numerator, c.denominator) for c in coef]
    poly = flint.fmpq_poly([q[-1]])
    for i in range(n - 2, -1, -1):
        poly = poly * flint.fmpq_poly([-xs[i], 1]) + q[i]
    return poly


def exact_fsq_line(n, a, b, j):
    h = 1 << (n - 1)
    d = 2 ** (n - 2) - 2
    xs = list(range(0, 2 * d + 3))
    ys = []
    for s in xs:
        z = [u + s * v for u, v in zip(a, b, strict=True)]
        if z[j] == 0:
            raise RuntimeError("z_j vanishes on a node")
        c = cross(h, z)
        keep = [k for k in range(h - 1) if k != j]
        det = int(flint.fmpz_mat([[c[r][cc] for cc in keep] for r in keep]).det())
        q, rem = divmod(det, z[j] * z[j])
        if rem:
            raise RuntimeError("det not divisible by z_j^2")
        ys.append(q)
    poly = newton_interp(xs[: 2 * d + 1], ys[: 2 * d + 1])
    for s, v in zip(xs[2 * d + 1 :], ys[2 * d + 1 :], strict=True):
        if poly(s) != v:
            raise RuntimeError("degree above 2d")
    return poly


def sec_irred(ns=(6, 7, 8), tries=6):
    for n in ns:
        h = 1 << (n - 1)
        d = 2 ** (n - 2) - 2
        found = None
        r = random.Random(LINE_SEEDS[n])
        for t in range(tries):
            a = [r.randint(-9, 9) for _ in range(h - 1)]
            b = [r.randint(-9, 9) for _ in range(h - 1)]
            a[0], b[0] = r.randint(1, 9), r.randint(1, 9)  # z_1 > 0 on every node s >= 0
            poly = exact_fsq_line(n, a, b, 0)
            num = (
                flint.fmpz_poly([int(c * poly.denom()) for c in poly.coeffs()])
                if poly.denom() != 1
                else flint.fmpz_poly([int(c) for c in poly.coeffs()])
            )
            if poly.denom() != 1:
                out("  WARNING: f^2 line polynomial not integral")
            content, facs = num.factor()
            degs = sorted((g.degree(), e) for g, e in facs)
            out(f"irred A_{n} line {t}: deg f^2 = {num.degree()} (2d = {2 * d}), factors {degs}, content {content}")
            if num.degree() == 2 * d and len(facs) == 1 and facs[0][1] == 2 and facs[0][0].degree() == d:
                found = t
                break
        out(f"irred A_{n}: irreducible exact Q-line found: {found}")


def sec_witness():
    sys.path.insert(0, str(ROOT / "scripts"))
    from stiefel_pfaffian_higher import disjoint_stiefel  # witness construction only

    def stiefel(dim, y):
        h = dim // 2
        p_, q_ = y[:h], y[h:]
        return (
            p_[0] == 0 and q_[0] == 0,
            sum(v * v for v in p_) - sum(v * v for v in q_),
            sum(u * v for u, v in zip(p_, q_, strict=True)),
        )

    y = [0] * 64
    for k in (12, 15, 16, 23):
        y[k] = 1
    y[34] = 2
    out(
        "five-term A_6: doubly pure, |p|^2-|q|^2, <p,q> =",
        stiefel(64, y),
        "|p|^2 =",
        sum(v * v for v in y[:32]),
        "rank =",
        flint.fmpz_mat(left(64, y)).rank(),
        "det mod p nonzero:",
        int(flint.nmod_mat(left(64, y), P).det()) != 0,
    )
    y6 = [0] * 64
    for k in (2, 5, 20, 46, 48, 54):
        y6[k] = 1
    out("six-term A_6:", stiefel(64, y6), "rank =", flint.fmpz_mat(left(64, y6)).rank())
    for dim in (64, 128, 256):
        y = disjoint_stiefel(dim)
        out(
            f"disjoint A_{dim.bit_length() - 1}: stiefel",
            stiefel(dim, y),
            "nonzeros",
            sum(1 for v in y if v),
            "rank",
            flint.fmpz_mat(left(dim, y)).rank(),
            "det mod p nonzero:",
            int(flint.nmod_mat(left(dim, y), P).det()) != 0,
        )
        # cross-check L_y against cd_multiply_exact for this witness
        x = [RNG.randint(-2, 2) for _ in range(dim)]
        lm = left(dim, y)
        out(
            "   L_y x == cd_multiply_exact:",
            tuple(Fraction(sum(lm[r][c] * x[c] for c in range(dim))) for r in range(dim))
            == cd_multiply_exact(dim, y, x),
        )
    for dim, k in ((64, 16), (128, 32), (256, 64)):
        y = disjoint_stiefel(dim, avoid=k)
        out(
            f"disjoint avoiding z_{k} at {dim}: stiefel",
            stiefel(dim, y),
            "nullity",
            dim - flint.fmpz_mat(left(dim, y)).rank(),
        )


def sec_pairs():
    h = 32
    counts = {}
    special = {}
    for i in range(1, h):
        for j in range(1, h):
            if i == j:
                continue
            y = [0] * 64
            y[i] = 1
            y[h + j] = 1
            nul = 64 - flint.fmpz_mat(left(64, y)).rank()
            counts[nul] = counts.get(nul, 0) + 1
            if 16 in (i, j):
                special[nul] = special.get(nul, 0) + 1
    out("pairs A_6 nullity counts:", dict(sorted(counts.items())), "through z_16:", special)


def isotropic_point(support, h, rng):
    """Random z in F_P^(h-1) supported on `support` with z.z = 0 (all coordinates nonzero)."""
    while True:
        vals = [rng.randrange(1, P) for _ in support[:-1]]
        rest = (-sum(v * v for v in vals)) % P
        try:
            last = int(flint.nmod(rest, P).sqrt())
        except Exception:
            continue
        if last == 0:
            continue
        z = [0] * (h - 1)
        for k, v in zip(support, vals + [last], strict=True):
            z[k - 1] = v
        return z


def sec_slices(points=2):
    rng = random.Random(12958)  # index 4
    h = 32
    summary = {}
    for size in (3, 4):
        bad = []
        for s in itertools.combinations(range(1, 32), size):
            for _ in range(points):
                z = isotropic_point(list(s), h, rng)
                if rank_mod(cross(h, z, P)) > 28:
                    bad.append(s)
                    break
        summary[size] = bad
        out(f"slices size {size}: subsets with a mod-p Stiefel point where f != 0: {len(bad)} {bad[:10]}")
    # controls: the six-slice and seven-slice must show f != 0 at Q_S = 0 points
    for s in ((2, 5, 14, 16, 20, 22), (3, 4, 13, 14, 16, 22, 26), (2, 5, 14, 20, 22, 3)):
        r = [rank_mod(cross(h, isotropic_point(list(s), h, rng), P)) for _ in range(3)]
        out(f"slice control {s}: ranks at Q_S = 0 points {r}")
    # 5-subsets of 1..16 containing 16
    bad5 = []
    for s in itertools.combinations(range(1, 17), 5):
        if 16 in s:
            z = isotropic_point(list(s), h, rng)
            if rank_mod(cross(h, z, P)) > 28:
                bad5.append(s)
    out("5-subsets of 1..16 containing 16 with f != 0 point:", len(bad5), bad5[:10])


def sec_bcdi():
    rng = random.Random(34530)  # index 5
    h = 32
    on = [rank_mod(cross(h, isotropic_point([k for k in range(1, 32) if k != 16], h, rng), P)) for _ in range(20)]
    off = [rank_mod(cross(h, isotropic_point(list(range(1, 32)), h, rng), P)) for _ in range(20)]
    out("BCDI {Q=0, z16=0} ranks of C_z (28 means f=0):", sorted(set(on)))
    out("generic Stiefel z16 != 0 ranks:", sorted(set(off)))
    for n in (7, 8):
        h2 = 1 << (n - 1)
        s = h2 // 2
        on = [rank_mod(cross(h2, isotropic_point([k for k in range(1, h2) if k != s], h2, rng), P)) for _ in range(4)]
        off = [rank_mod(cross(h2, isotropic_point(list(range(1, h2)), h2, rng), P)) for _ in range(4)]
        out(f"A_{n}: BCDI ranks {sorted(set(on))}, generic Stiefel ranks {sorted(set(off))} (full {h2 - 2})")


def sec_six():
    rng = random.Random(20003)  # index 6
    h = 32
    s = [2, 5, 14, 16, 20, 22]
    ok = []
    for _ in range(10):
        z = isotropic_point(s, h, rng)
        v = {k: z[k - 1] for k in s}
        closed = -256 * (v[5] * v[14] ** 2 * v[16] * v[20] * v[22]) ** 2 * (v[2] ** 2 + v[5] ** 2) % P
        ok.append(fsq_mod(h, z) == closed * closed % P)
    out("six-slice on Q=0: f^2 == (closed form)^2 at 10 points:", all(ok))


def sec_small():
    rng = random.Random(56778)  # index 7
    good4 = good5 = True
    for _ in range(5):
        z = [rng.randrange(P) for _ in range(7)]
        q = sum(v * v for v in z) % P
        good4 &= fsq_mod(8, z) == q * q % P
        z = [rng.randrange(P) for _ in range(15)]
        u, mu, v = z[:7], z[7], z[8:]
        uu = sum(a * a for a in u)
        vv = sum(a * a for a in v)
        uv = sum(a * b for a, b in zip(u, v, strict=True))
        q = (uu + mu * mu + vv) % P
        g = (q * q - 4 * (uu * vv - uv * uv)) % P
        good5 &= fsq_mod(16, z) == (q * g) ** 2 % P
    out("f_4^2 == Q^2:", good4, " f_5^2 == (QG)^2:", good5)


def sec_three():
    rng = random.Random(26843)  # index 8
    for n in (4, 5, 6, 7, 8):
        h = 1 << (n - 1)
        e = 2 ** (n - 3) - 1
        ok = True
        for _ in range(3):
            z = [0] * (h - 1)
            for k in (1, 2, 3):
                z[k - 1] = rng.randrange(1, P)
            q = sum(v * v for v in z) % P
            ok &= fsq_mod(h, z) == pow(q, 2 * e, P)
        out(f"three-slice A_{n}: f^2 == Q^(2*{e}):", ok)


def fsq_line_mod(h, a, b, d):
    xs = list(range(1, 2 * d + 4))
    ys = [fsq_mod(h, [(u + s * v) % P for u, v in zip(a, b, strict=True)]) for s in xs]
    poly = flint.nmod_poly([0], P)
    for i in range(2 * d + 1):
        num = flint.nmod_poly([1], P)
        den = 1
        for jj in range(2 * d + 1):
            if jj != i:
                num *= flint.nmod_poly([-xs[jj] % P, 1], P)
                den = den * (xs[i] - xs[jj]) % P
        poly += num * (ys[i] * pow(den, -1, P) % P)
    for s, v in zip(xs[2 * d + 1 :], ys[2 * d + 1 :], strict=True):
        if int(poly(s)) != v:
            raise RuntimeError("interpolated polynomial disagrees at a check node")
    return poly


def sec_mult():
    """Multiplicity of the z_s root on random isotropic lines over F_P (own construction)."""
    rng = random.Random(46053)  # index 9
    for n in (6, 7):
        h = 1 << (n - 1)
        d = 2 ** (n - 2) - 2
        sidx = h // 2 - 1
        res = []
        for _ in range(3):
            # isotropic plane: a isotropic, b isotropic with a.b = 0. Use b = a' with a' built by solving.
            while True:
                a = isotropic_point(list(range(1, h)), h, rng)
                b = [rng.randrange(P) for _ in range(h - 1)]
                # force a.b = 0 and b.b = 0 by adjusting b along two coordinates (last two): b' = b + x e_m + y a
                # b+y a: (b+ya).(b+ya) = b.b + 2y a.b; a.(b+ya) = a.b. So first fix a.b = 0 via coordinate m.
                m = h - 2
                ab = sum(x * y for x, y in zip(a, b, strict=True)) % P
                b[m] = (b[m] - ab * pow(a[m], -1, P)) % P
                bb = sum(x * x for x in b) % P
                # now a.b = 0; add y a cannot change b.b. Instead add y c with c isotropic? Use scaling trick:
                # replace b by b + t a has b.b unchanged; so pick a second solve: adjust coordinate k=0 and m jointly.
                # Solve along direction e_0 - (a_0/a_m) e_m which keeps a.b = 0: b(t) = b + t v.
                v = [0] * (h - 1)
                v[0] = 1
                v[m] = (-a[0] * pow(a[m], -1, P)) % P
                vv = sum(x * x for x in v) % P
                bv = sum(x * y for x, y in zip(b, v, strict=True)) % P
                disc = (bv * bv - vv * bb) % P
                try:
                    r = int(flint.nmod(disc, P).sqrt())
                except Exception:
                    continue
                t = (-bv + r) * pow(vv, -1, P) % P
                b = [(x + t * y) % P for x, y in zip(b, v, strict=True)]
                if (
                    sum(x * x for x in b) % P == 0
                    and sum(x * y for x, y in zip(a, b, strict=True)) % P == 0
                    and b[sidx]
                ):
                    break
            poly = fsq_line_mod(h, a, b, d)
            root = (-a[sidx] * pow(b[sidx], -1, P)) % P
            mlt = 0
            q = poly
            lin = flint.nmod_poly([-root % P, 1], P)
            while q.degree() >= 1:
                dq, rr = divmod(q, lin)
                if rr != 0:
                    break
                q, mlt = dq, mlt + 1
            res.append((poly.degree() // 2, mlt // 2))
        out(f"isotropic lines A_{n}: (deg f on line, multiplicity of z_s root) = {res}")


SECTIONS = {
    "table": sec_table,
    "transport": sec_transport,
    "degree": sec_degree,
    "irred": sec_irred,
    "witness": sec_witness,
    "pairs": sec_pairs,
    "slices": sec_slices,
    "bcdi": sec_bcdi,
    "six": sec_six,
    "small": sec_small,
    "three": sec_three,
    "mult": sec_mult,
}

if __name__ == "__main__":
    out("prime", P, "iota", IOTA)
    for name in sys.argv[1:]:
        SECTIONS[name]()
    json  # noqa: B018
