"""Normalized Hensel arcs on E8-bar -> VB in chart t_C = 1, generalizing chart3.sage to any chart.

Usage: chart.py CHART NORD NORDIR POINTS_JSON
The strict transform's exceptional locus is P(L), L = V(t2, t8, t5 - t6, t3 + t4). A base point on P(L) in chart
t_C = 1 is fixed by three free coordinates; NORDIR/norid.txt and NORDIR/vars.txt hold the Singular normalization of
the strict transform restricted to t_C = 1 (snorm.sing). Over GF(p^2) each base point's fiber in the normalization is
solved, the arc is lifted to order NORD by Newton steps on an independent subset of the normalization relations, and
the leading G-vector F is tested against the two primes of sqrt(K2). Prints one JSON line per arc.
"""

import json
import re
import sys

from sage.all import GF, Matrix, PolynomialRing, vector

p = 32009
F = GF(p**2, "a")
CHART, NORD, NDIR, PTS = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3], json.loads(sys.argv[4])
NORD_CAP = 12
names = re.sub(r"T\((\d+)\)", r"T\1", open(f"{NDIR}/vars.txt").read()).replace(",", " ").split()
R = PolynomialRing(F, names)
g = dict(zip(names, R.gens()))
txt = re.sub(r"T\((\d+)\)", r"T\1", open(f"{NDIR}/norid.txt").read().replace("\n", "").strip())
N = [R(x) for x in txt.split(",")]
tnames = [f"t{i}" for i in range(1, 9) if i != CHART]
Tn = [n for n in names if n not in tnames and n != "h"]
dep_names = Tn + [n for n in ("t2", "t4", "t6", "t8") if n != f"t{CHART}"]
nd = len(dep_names)
Rg = PolynomialRing(F, [f"t{i}" for i in range(1, 9)])
Gl = [Rg(x) for x in open("G.txt").read().replace("\n", "").strip().split(",")]
ys = PolynomialRing(F, [f"y{i}" for i in range(1, 11)])
Pr = [[ys(re.sub(r"y\((\d+)\)", r"y\1", x)) for x in open(fn).read().strip().split(",")]
      for fn in ("primeP1.txt", "primeP2.txt")]
Sr = PolynomialRing(F, "s")
s = Sr.gen()


def tr(f, n):
    return Sr(f.list()[: n + 1])


def ev(f, x, n):
    out = Sr.zero()
    pw = {}
    for e, c in f.dict().items():
        term = Sr(c)
        for i, k in enumerate(e):
            if k:
                if (i, k) not in pw:
                    r = Sr.one()
                    for _ in range(k):
                        r = tr(r * x[i], n)
                    pw[(i, k)] = r
                term = tr(term * pw[(i, k)], n)
        out += term
    return tr(out, n)


def base_t(free):
    """Point of P(L) in chart t_C = 1 as a dict t1..t8; free = the three remaining L coordinates."""
    t = {f"t{i}": F(0) for i in range(1, 9)}
    t[f"t{CHART}"] = F(1)
    pair = {3: 4, 4: 3, 5: 6, 6: 5}
    sign = {3: -1, 4: -1, 5: 1, 6: 1}
    if CHART in pair:
        t[f"t{pair[CHART]}"] = F(sign[CHART])
    frees = [i for i in (1, 3, 5, 7) if i != CHART and not (CHART in pair and i == min(CHART, pair[CHART]))]
    for i, v in zip(frees, free):
        t[f"t{i}"] = F(v)
        if i in pair:
            t[f"t{pair[i]}"] = F(sign[i]) * F(v)
    return t


Tv = PolynomialRing(F, Tn)


def basepts(t):
    fix = {g["h"]: 0, **{g[n]: t[n] for n in tnames}}
    I = Tv.ideal([Tv(str(e.subs(fix))) for e in N])
    if I.dimension() != 0:
        return "posdim"
    return [[pt[v] for v in Tv.gens()] for pt in I.variety(F)]


def arc(t, Tb, nord):
    val = {**dict(zip(Tn, Tb)), **{n: t[n] for n in tnames}}
    x = [s if n == "h" else Sr(val[n]) for n in names]
    depg = [g[n] for n in dep_names]
    M = Matrix(F, len(N), nd, [[ev(f.derivative(v), x, 0)[0] for v in depg] for f in N])
    if M.rank() < nd:
        return ("rank", int(M.rank()))
    sel, cur = [], Matrix(F, 0, nd)
    for i in sorted(range(len(N)), key=lambda i: len(N[i].monomials())):
        st = cur.stack(M[i])
        if st.rank() > cur.nrows():
            cur, sel = st, sel + [i]
        if len(sel) == nd:
            break
    Mi = Matrix(F, [M[i] for i in sel]).inverse()
    idx = [names.index(n) for n in dep_names]
    for n in range(1, nord + 1):
        corr = -Mi * vector(F, [ev(N[i], x, n)[n] for i in sel])
        for b, i in enumerate(idx):
            x[i] = x[i] + corr[b] * s**n
    return x


def lead(x, nord):
    """Leading order and coefficients of G along the arc; tt is exact through s^(nord+1), so None means nu > nord+1."""
    X = dict(zip(names, x))
    tt = [s if i == CHART else tr(s * X[f"t{i}"], nord + 1) for i in range(1, 9)]
    ser = [ev(G, tt, nord + 1) for G in Gl]
    if all(f == 0 for f in ser):
        return None
    nu = min(f.valuation() for f in ser if f != 0)
    return nu, [f[nu] for f in ser]


for free in PTS:
    t = base_t(free)
    bp = basepts(t)
    if bp == "posdim":
        print(json.dumps({"chart": CHART, "free": free, "basepts": "posdim"}), flush=True)
        continue
    for Tb in bp:
        nord, ld = NORD, None
        while True:
            x = arc(t, Tb, nord)
            if isinstance(x, tuple):
                break
            ld = lead(x, nord)
            if ld is not None or nord >= NORD_CAP:
                break
            nord += 2
        if isinstance(x, tuple):
            print(json.dumps({"chart": CHART, "free": free, "jacobian_rank": x[1], "need": nd}), flush=True)
            continue
        resid = sum(1 for f in N if ev(f, x, nord) != 0)
        if ld is None:
            print(json.dumps({"chart": CHART, "free": free, "nbase": len(bp), "resid": resid, "nord": nord,
                              "nu_exceeds": nord + 1}), flush=True)
            continue
        nu, Fv = ld
        inP = [all(pg(*Fv) == 0 for pg in Pp) for Pp in Pr]
        print(json.dumps({"chart": CHART, "free": free, "nbase": len(bp), "resid": resid, "nord": nord, "nu": int(nu),
                          "F": [str(v) for v in Fv], "inP1": inP[0], "inP2": inP[1]}), flush=True)
