"""Independent exact checks at the 21 retained rank-locus witnesses (rank_locus_local_dimension/result.json):
family membership in the companion's equations, own Jacobian ranks, own Schur tangent dimension, nullity.
"""

import json
import os
from fractions import Fraction

import flint
import sympy as sp
from common import REPO, lmat, nullity, sign

rows = json.load(open(os.path.join(REPO, "docs/evidence/rank_locus_local_dimension/result.json")))["rows"]
F = flint.fmpq
I = sp.I
Y = sp.symbols("y0:32")
z = [Y[k] + I * Y[16 + k] for k in range(1, 16)]
u, mu, v = z[0:7], z[7], z[8:15]


def dot(a, b):
    return sp.expand(sum(x * y for x, y in zip(a, b)))


def ocross(a, b):
    res = [0] * 7
    for i in range(7):
        for j in range(7):
            k = (i + 1) ^ (j + 1)
            if k:
                res[k - 1] += sign(8, i + 1, j + 1) * a[i] * b[j]
    return [sp.expand(x) for x in res]


U, V0, W = dot(u, u), dot(v, v), dot(u, v)
Q = sp.expand(U + mu**2 + V0)
Dl = sp.expand(U * V0 - W**2)
G = sp.expand(Q**2 - 4 * Dl)
w = ocross(u, v)
wedge = []
for i in range(7):
    for j in range(i + 1, 7):
        for k in range(j + 1, 7):
            wedge.append(sp.expand(sp.Matrix([[u[i], u[j], u[k]], [v[i], v[j], v[k]], [w[i], w[j], w[k]]]).det()))


def realparts(exprs):
    outl = []
    for e in exprs:
        outl += [sp.re(sp.expand(e).subs({s: sp.Symbol(s.name, real=True) for s in Y})), None]
    return outl


Yr = sp.symbols("r0:32", real=True)
sub = dict(zip(Y, Yr))


def reim(e):
    e = sp.expand(e.subs(sub))
    return [sp.re(e), sp.im(e)]


def jac_rank(exprs, point):
    rowsl = []
    pt = {Yr[i]: point[i] for i in range(32)}
    for e in exprs:
        rowsl.append([sp.Rational(sp.diff(e, Yr[i]).subs(pt)) for i in range(32)])
    M = flint.fmpq_mat(len(rowsl), 32, [F(int(x.p), int(x.q)) for r in rowsl for x in r])
    return M.rank()


def zns(M):
    from math import lcm
    den = 1
    for i in range(M.nrows()):
        for j in range(M.ncols()):
            den = lcm(den, int(M[i, j].q))
    Z = flint.fmpz_mat(M.nrows(), M.ncols(), [int(M[i, j] * den) for i in range(M.nrows()) for j in range(M.ncols())])
    X, k = Z.nullspace()
    return flint.fmpq_mat(M.ncols(), k, [F(int(X[i, j])) for i in range(M.ncols()) for j in range(k)]), k


def schur_tangent(point):
    L = lmat(32, point)
    Nr, k = zns(L)
    Nl, k2 = zns(L.transpose())
    cols = []
    for h in range(32):
        e = [F(int(i == h)) for i in range(32)]
        Mh = Nl.transpose() * lmat(32, e) * Nr
        cols.append([Mh[i, j] for i in range(k) for j in range(k)])
    M = flint.fmpq_mat(k * k, 32, [cols[h][r] for r in range(k * k) for h in range(32)])
    return 32 - M.rank(), k


purity = [Yr[0], Yr[16]]
EQ_Q = reim(Q)
EQ_G = reim(G)
EQ_W = [x for e in wedge for x in reim(e)]
EQ_Z = reim(mu) + reim(U - V0) + reim(W)
EQ_V = [x for i in range(7) for j in range(i + 1, 7) for x in reim(u[i] * v[j] - u[j] * v[i])] + EQ_Q

fam_eq = {"nonzd-axis": ("V", purity + EQ_V), "zd-nonzd-locus": ("Q + 35 quartics", purity + EQ_Q + EQ_W),
          "zd-nonzd-generic": ("G", purity + EQ_G), "nonzd-nonzd-locus": ("Q (Stiefel)", purity + EQ_Q),
          "zd-zd-generic": ("Z", purity + EQ_Z)}
report = []
for idx, row in enumerate(rows):
    fam = row["family"]
    if fam not in fam_eq:
        continue
    x = [Fraction(s) for s in row["x"]]
    xs = [sp.Rational(q.numerator, q.denominator) for q in x]
    pt = dict(zip(Y, xs))
    vals = {name: sp.nsimplify(sp.expand(e.subs(pt))) for name, e in (("Q", Q), ("G", G), ("Delta", Dl), ("mu", mu))}
    wedge_zero = all(sp.expand(e.subs(pt)) == 0 for e in wedge)
    extra = {}
    if fam == "zd-nonzd-locus":
        uu = [sp.expand(a.subs(pt)) for a in u]
        vv = [sp.expand(a.subs(pt)) for a in v]
        Uv = sp.expand(sum(a * a for a in uu))
        lam = sp.simplify(sp.expand(sum(a * b for a, b in zip(uu, vv))) / Uv)
        n = [sp.expand(b - lam * a) for a, b in zip(uu, vv)]
        uxn = ocross(uu, n)
        j = next(i for i in range(7) if n[i] != 0)
        rho = sp.simplify(uxn[j] / n[j])
        extra = {"lambda": str(lam), "rho": str(rho), "rho2+U": str(sp.simplify(rho**2 + Uv)),
                 "eigvec": all(sp.simplify(a - rho * b) == 0 for a, b in zip(uxn, n))}
    name, eqs = fam_eq[fam]
    jr = jac_rank(eqs, xs)
    tdim, k = schur_tangent([F(q.numerator, q.denominator) for q in x])
    report.append({"row": idx, "family": fam, "nullity": k, "record_unit_bound": row.get("dimension_upper_bound"),
                   "Q": str(vals["Q"]), "G": str(vals["G"]), "Delta": str(vals["Delta"]), "mu": str(vals["mu"]),
                   "wedge_zero": wedge_zero, "equations": name, "jacobian_rank": jr, "equation_cone_dim_upper": 32 - jr,
                   "schur_tangent_cone_dim": tdim, **extra})
print(json.dumps(report, indent=1))
