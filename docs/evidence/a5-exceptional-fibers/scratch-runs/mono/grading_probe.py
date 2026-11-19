"""Probe: which gradings of k[a,rho,sig,w] make the same-sign X generators homogeneous."""
import sys, importlib.util
from pathlib import Path
root = Path(sys.argv[1])
spec = importlib.util.spec_from_file_location("lad", root / "docs/evidence/a5-exceptional-fibers/monomial-ladder/x_same_ladder.py")
lad = importlib.util.module_from_spec(spec); spec.loader.exec_module(lad)
p = 32009
N = int(sys.argv[2])
gens = lad.generators("xm-nm", p, N)
ctx = gens[0].context()
a, rho, sig, w = ctx.gens()
print("gens", len(gens))
def degs(g, f):
    return sorted({f(e) for e in g.to_dict()})
for name, f in (("rhosig total", lambda e: e[1] + e[2]), ("rho", lambda e: e[1]), ("sig", lambda e: e[2]), ("a", lambda e: e[0]), ("rho-sig", lambda e: e[1]-e[2])):
    print(name, [degs(g, f) for g in gens])
# torus candidates: rho = x + c*y, sig = d*(x - c*y)... test substitution rho=(x+y), sig=k*(x-y) for k in {1, i, -i}
i = next(v for v in range(2, p) if v * v % p == p - 1)
for label, k in (("rho+-sig", 1), ("rho+-i sig", i)):
    out = []
    for g in gens:
        h = g.compose(a, rho + sig, k * (rho - sig), w)
        out.append(degs(h, lambda e: e[1] - e[2]))
    print(label, out)
