"""Genuine quadrics on M in the imaginary coordinates, rationally reconstructed and cross-checked at the second prime."""
import random, sys, json
from fractions import Fraction
sys.path.insert(0, "SCRATCH")
import flint, itertools
import implicit_probe as I
L = I.L

def ratrec(a, m):
    r0, r1, s0, s1 = m, a % m, 0, 1
    bound = int((m // 2) ** 0.5)
    while r1 > bound:
        q = r0 // r1
        r0, r1, s0, s1 = r1, r0 - q * r1, s1, s0 - q * s1
    if s1 == 0 or abs(s1) > bound: return None
    return Fraction(r1, s1) if s1 > 0 else Fraction(-r1, -s1)

def reduced_basis(ch, p, ndir, order, mons):
    I.P = p
    rng = random.Random(11)
    rows = []
    for _ in range(ndir):
        w = [rng.randrange(1, p) for _ in ch["free"]]
        kept = I.lift_vectors(ch, w, order)
        coords = [[kept[j][m] for j in range(order)] for m in range(L.DIM)]
        cache = {}
        def prod(mon):
            if mon in cache: return cache[mon]
            v = coords[mon[0]] if len(mon) == 1 else I.series_mul(prod(mon[:-1]), coords[mon[-1]], order)
            cache[mon] = v; return v
        cols = [prod(m) for m in mons]
        rows += [[c[j] for c in cols] for j in range(order)]
    rref, rank = flint.nmod_mat(rows, p).rref()
    piv, r = [], 0
    for c in range(len(mons)):
        if r < rank and int(rref[r, c]) != 0:
            piv.append(c); r += 1
    free = [c for c in range(len(mons)) if c not in piv]
    basis = []
    for f in free:
        v = {f: 1}
        for i, c in enumerate(piv):
            val = (-int(rref[i, f])) % p
            if val: v[c] = val
        basis.append(v)
    return free, basis

wid = int(sys.argv[1]); ndir = int(sys.argv[2]); order = int(sys.argv[3])
row = next(r for r in L.all_rows() if r["witness"] == wid)
ch = L.chart(row)
zero = [int(c) for c in sys.argv[4].split(",")]
coords = [m for m in range(L.DIM) if m not in zero]
mons = list(itertools.combinations_with_replacement(coords, 2))
p1, p2 = L.PRIMES
f1, b1 = reduced_basis(ch, p1, ndir, order, mons)
f2, b2 = reduced_basis(ch, p2, ndir, order, mons)
print("quadrics", len(b1), len(b2), "same free set", f1 == f2)
out = []
ok = True
for v1, v2 in zip(b1, b2):
    q = {}
    for c, a in v1.items():
        r = ratrec(a, p1)
        if r is None or (r.numerator * pow(r.denominator, -1, p2) - v2.get(c, 0)) % p2:
            ok = False
        q[mons[c]] = r
    if set(v1) != set(v2): ok = False
    out.append(q)
print("reconstruction consistent across primes", ok)
def name(m): return ("p" if m < 16 else "q") + str(m % 16)
for q in out:
    print(" + ".join(f"{c}*{name(a)}{name(b)}" for (a, b), c in sorted(q.items())))
json.dump([[[a, b, str(c)] for (a, b), c in q.items()] for q in out], open(f"SCRATCH/quadrics_w{wid}.json", "w"))
