"""Find homogeneous forms of degree <= 3 in the 32 ambient coordinates that vanish on the germ M, mod p."""
import itertools, random, sys
from pathlib import Path
ROOT = Path("~/Projects/IBMQuantum")
sys.path.insert(0, str(ROOT / "scripts"))
import flint
import rank_locus_padic_lift as L

P = L.PRIMES[0]

def lift_vectors(ch, weights, order):
    # Re-run series_lift but capture the kept coefficient vectors.
    kept = []
    orig = L.series_lift
    src_items = (ch, P, weights, order)
    # inline copy: monkeypatch via closure is awkward; re-implement through coefficient capture
    import types
    code = orig.__code__
    res = {}
    def tracer(frame, event, arg):
        if event == "return" and frame.f_code is code:
            res["kept"] = list(frame.f_locals["kept"])
        return tracer
    sys.setprofile(tracer)
    out = orig(src_items)
    sys.setprofile(None)
    if out["order"] is not None:
        raise RuntimeError("obstructed")
    return res["kept"]

def forms(n, deg):
    return list(itertools.combinations_with_replacement(range(n), deg))

def series_mul(a, b, N):
    c = [0]*N
    for i, x in enumerate(a):
        if x:
            for j in range(N - i):
                if b[j]:
                    c[i+j] = (c[i+j] + x*b[j]) % P
    return c

def run(wid, deg, ndir, order):
    row = next(r for r in L.all_rows() if r["witness"] == wid)
    ch = L.chart(row)
    rng = random.Random(7 + wid)
    curves = []
    for _ in range(ndir):
        w = [rng.randrange(1, P) for _ in ch["free"]]
        kept = lift_vectors(ch, w, order)
        curves.append([[kept[j][m] for j in range(order)] for m in range(L.DIM)])
    mons = forms(L.DIM, deg)
    rows = []
    for coords in curves:
        cache = {}
        def prod(mon):
            if mon in cache: return cache[mon]
            if len(mon) == 1: v = coords[mon[0]]
            else: v = series_mul(prod(mon[:-1]), coords[mon[-1]], order)
            cache[mon] = v; return v
        cols = [prod(m) for m in mons]
        for j in range(order):
            rows.append([c[j] for c in cols])
    M = flint.nmod_mat(rows, P)
    rank = M.rank()
    return ch, len(mons), len(rows), rank

if __name__ == "__main__":
    wid, deg, ndir, order = map(int, sys.argv[1:5])
    ch, nm, nr, rank = run(wid, deg, ndir, order)
    print(f"witness {wid} {ch['family']} k={ch['nullity']} dimT={ch['tangent_dimension']} deg={deg} monomials={nm} equations={nr} rank={rank} vanishing_forms={nm-rank}")
