"""Nullspace of quadrics on M, their Jacobian rank at x, and validation at higher order on fresh directions."""
import random, sys
sys.path.insert(0, "SCRATCH")
import flint
import implicit_probe as I
L = I.L; P = I.P

def curves(ch, ndir, order, seed):
    rng = random.Random(seed)
    out = []
    for _ in range(ndir):
        w = [rng.randrange(1, P) for _ in ch["free"]]
        kept = I.lift_vectors(ch, w, order)
        out.append([[kept[j][m] for j in range(order)] for m in range(L.DIM)])
    return out

def conditions(cs, mons, order):
    rows = []
    for coords in cs:
        cache = {}
        def prod(mon):
            if mon in cache: return cache[mon]
            v = coords[mon[0]] if len(mon) == 1 else I.series_mul(prod(mon[:-1]), coords[mon[-1]], order)
            cache[mon] = v; return v
        cols = [prod(m) for m in mons]
        rows += [[c[j] for c in cols] for j in range(order)]
    return flint.nmod_mat(rows, P)

wid, ndir, order = map(int, sys.argv[1:4])
row = next(r for r in L.all_rows() if r["witness"] == wid)
ch = L.chart(row)
mons = I.forms(L.DIM, 2)
A = conditions(curves(ch, ndir, order, 11), mons, order)
rref, rank = A.rref()
# nullspace basis from rref
piv = []
r = 0
for c in range(len(mons)):
    if r < rank and int(rref[r, c]) == 1 and all(int(rref[i, c]) == 0 for i in range(rank) if i != r):
        piv.append(c); r += 1
free = [c for c in range(len(mons)) if c not in piv]
basis = []
for f in free:
    v = [0]*len(mons); v[f] = 1
    for i, c in enumerate(piv):
        v[c] = (-int(rref[i, f])) % P
    basis.append(v)
print("quadrics", len(basis), "rank", rank)
x = [L.reduce_mod(v, P) for v in ch["x"]]
jac = []
for v in basis:
    g = [0]*L.DIM
    for coef, (a, b) in zip(v, mons):
        if coef:
            g[a] = (g[a] + coef * x[b]) % P
            g[b] = (g[b] + coef * x[a]) % P
    jac.append(g)
for lin in range(L.DIM):
    pass
jr = flint.nmod_mat(jac, P).rank()
print("jacobian rank of quadrics at x", jr, "codim of M", L.DIM - ch["tangent_dimension"])
# validation: fresh directions at higher order
B = conditions(curves(ch, 6, 48, 99), mons, 48)
bad = 0
for v in basis:
    col = flint.nmod_mat([[c] for c in v], P)
    prod = B * col
    if any(int(e) for e in prod.entries()):
        bad += 1
print("quadrics failing at order 48 on 6 fresh directions:", bad)
# sparsity summary
supp = sorted({len([c for c in v if c]) for v in basis})
print("support sizes", supp[:10], "...", supp[-3:])
# structure: halves p = coords 0..15, q = 16..31
from collections import Counter
kinds = Counter()
for v in basis:
    k = set()
    for coef, (a, b) in zip(v, mons):
        if coef:
            k.add(("p" if a < 16 else "q") + ("p" if b < 16 else "q"))
    kinds[tuple(sorted(k))] += 1
print("block types", dict(kinds))
print("x support", [m for m in range(32) if x[m]])
# linear forms on M
mons1 = I.forms(L.DIM, 1)
A1 = conditions(curves(ch, 60, 12, 5), mons1, 12)
r1 = A1.rref()
print("linear rank", r1[1], "pivots-free coords", [c for c in range(32) if all(int(r1[0][i, c]) == 0 for i in range(r1[1]))])
