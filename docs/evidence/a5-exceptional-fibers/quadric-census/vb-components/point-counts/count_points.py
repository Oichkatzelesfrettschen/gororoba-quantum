"""Count F_p points of V(K2) for E8-bar -> VB from the Q(i) generators dumped by arcs-vb-qi.sing.

Usage: python count_points.py DUMPLOG P [P ...]. For each prime p = 1 mod 4 (not dividing denominators) it maps
I to a square root of -1 mod p, finds the linear span of each minimal prime (its degree-1 generators), enumerates
the projective points of each span, and counts the points of each span where all K2 quadrics vanish; V(K2) lies in
the union of the two spans, so #V(K2)(F_p) = |A| + |B| - |A n B|. It also counts each prime's own zeros.
"""

import itertools
import re
import sys
from fractions import Fraction

import numpy as np
import sympy as sp

log, primes = sys.argv[1], [int(a) for a in sys.argv[2:]]
gens: dict[str, list[str]] = {"K2GEN": [], "P1GEN": [], "P2GEN": []}
for line in open(log, encoding="utf-8"):
    for k in gens:
        if line.startswith(k + " "):
            gens[k].append(line[len(k) + 1 :].strip())
Y = sp.symbols("y1:11")
I_SYM = sp.Symbol("I")


def parse(s):
    s = re.sub(r"y\((\d+)\)", r"y\1", s).replace("^", "**")
    return sp.Poly(sp.sympify(s, locals={**{f"y{j + 1}": Y[j] for j in range(10)}, "I": I_SYM}), *Y)


P = {k: [parse(s) for s in v] for k, v in gens.items()}
print("parsed", {k: len(v) for k, v in P.items()}, flush=True)


def modp(c, p, r):
    c = sp.nsimplify(c)
    re_, im_ = sp.re(c), sp.im(c)

    def f(x):
        x = Fraction(int(sp.numer(x)), int(sp.denom(x)))
        if x.denominator % p == 0:
            raise ValueError("bad prime")
        return x.numerator * pow(x.denominator, -1, p) % p

    return (f(re_) + f(im_) * r) % p


def topoly(poly, p, r):
    return [(m, modp(c.subs(I_SYM, sp.I), p, r)) for m, c in poly.terms()]


def evalq(terms, X, p):
    acc = np.zeros(X.shape[0], dtype=np.int64)
    for m, c in terms:
        t = np.full(X.shape[0], c, dtype=np.int64)
        for j, e in enumerate(m):
            for _ in range(e):
                t = t * X[:, j] % p
        acc = (acc + t) % p
    return acc


def kernel(rows, p, n=10):
    M = [list(r) for r in rows]
    piv = []
    rk = 0
    for col in range(n):
        pr = next((i for i in range(rk, len(M)) if M[i][col] % p), None)
        if pr is None:
            continue
        M[rk], M[pr] = M[pr], M[rk]
        inv = pow(M[rk][col], -1, p)
        M[rk] = [x * inv % p for x in M[rk]]
        for i in range(len(M)):
            if i != rk and M[i][col] % p:
                f = M[i][col]
                M[i] = [(a - f * b) % p for a, b in zip(M[i], M[rk], strict=True)]
        piv.append(col)
        rk += 1
    free = [c for c in range(n) if c not in piv]
    basis = []
    for fcol in free:
        v = [0] * n
        v[fcol] = 1
        for i, pc in enumerate(piv):
            v[pc] = (-M[i][fcol]) % p
        basis.append(v)
    return np.array(basis, dtype=np.int64)


def proj_points(k, p):
    # all projective points of P^(k-1) over F_p, normalized first nonzero coordinate = 1
    out = []
    for lead in range(k):
        rest = k - lead - 1
        grid = (
            np.array(list(itertools.product(range(p), repeat=rest)), dtype=np.int64).reshape(-1, rest)
            if rest
            else np.zeros((1, 0), dtype=np.int64)
        )
        block = np.zeros((grid.shape[0], k), dtype=np.int64)
        block[:, lead] = 1
        block[:, lead + 1 :] = grid
        out.append(block)
    return np.vstack(out)


for p in primes:
    r = next(x for x in range(2, p) if x * x % p == p - 1)
    K = [topoly(q, p, r) for q in P["K2GEN"]]
    spans = []
    for key in ("P1GEN", "P2GEN"):
        lin = [q for q in P[key] if q.total_degree() == 1]
        rows = [[modp(q.coeff_monomial(Y[j]).subs(I_SYM, sp.I), p, r) for j in range(10)] for q in lin]
        B = kernel(rows, p)
        spans.append((key, B, [topoly(q, p, r) for q in P[key]]))
    res = {"p": p}
    zsets = []
    for key, B, gen in spans:
        pts = proj_points(B.shape[0], p)
        X = pts @ B % p
        onK = np.ones(X.shape[0], dtype=bool)
        for t in K:
            onK &= evalq(t, X, p) == 0
        onP = np.ones(X.shape[0], dtype=bool)
        for t in gen:
            onP &= evalq(t, X, p) == 0
        res[key + "_span_dim"] = B.shape[0] - 1
        res[key + "_points"] = int(onP.sum())
        res[key + "_K2_points_in_span"] = int(onK.sum())
        Z = X[onK]
        # normalize projectively for set intersection
        norm = []
        for row in Z:
            nz = np.nonzero(row)[0][0]
            inv = pow(int(row[nz]), -1, p)
            norm.append(tuple((row * inv % p).tolist()))
        zsets.append(set(norm))
    res["union_K2_points"] = len(zsets[0] | zsets[1])
    res["intersection"] = len(zsets[0] & zsets[1])
    q = p
    res["predict_S111_S112_plane"] = (2 * q + 1) * (q * q + q + 1)
    res["predict_S111_veronese_cone"] = (q + 1) * (q * q + q + 1) + (q**3 + q * q + q + 1) - (q * q + q + 1)
    print("RESULT", res, flush=True)
