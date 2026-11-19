"""Probe: is the truncated ideal I of the same-sign X slice ring a span of monomials of k[[a, rho, sig, w]]?"""
import sys, importlib.util
from pathlib import Path
from flint import nmod_mat
root = Path(sys.argv[1]); N = int(sys.argv[2]); p = int(sys.argv[3]) if len(sys.argv) > 3 else 32009
slug = sys.argv[4] if len(sys.argv) > 4 else "xm-nm"
spec = importlib.util.spec_from_file_location("lad", root / "docs/evidence/a5-exceptional-fibers/monomial-ladder/x_same_ladder.py")
lad = importlib.util.module_from_spec(spec); spec.loader.exec_module(lad)
gens = lad.generators(slug, p, N)
ctx = gens[0].context()
def echelon(polys):
    index = {}; rows = []
    for q in polys:
        rows.append({index.setdefault(tuple(int(v) for v in e), len(index)): int(c) for e, c in q.to_dict().items() if sum(e) < N})
    m = nmod_mat(len(rows), len(index), p)
    for i, row in enumerate(rows):
        for j, v in row.items(): m[i, j] = v
    red, r = m.rref()
    monos = [None] * len(index)
    for e, j in index.items(): monos[j] = e
    return red, r, monos
for label, maximal in (("I = sum g R", False), ("m_R I", True)):
    polys = [lad.truncate(ctx, g * b, N) for g in gens for b in lad.ring_basis(ctx, N, maximal)]
    red, r, monos = echelon([q for q in polys if q])
    support = [[monos[j] for j in range(len(monos)) if int(red[i, j])] for i in range(r)]
    single = sum(len(s) == 1 for s in support)
    print(slug, p, "order", N, label, "rank", r, "echelon rows that are single monomials", single, flush=True)
    if single == r:
        cells = {}
        for (e,) in support:
            cells.setdefault((e[0], e[1] + e[2]), []).append(e[3])
        # per (deg a, deg in rho and sig): the least w exponent present, and whether all (rho, sig) splits and all higher w occur
        table = {k: min(v) for k, v in sorted(cells.items())}
        print(" least w-exponent by (deg a, deg rho+sig):", table)
    else:
        worst = max(support, key=len)
        print(" a non-monomial row:", worst[:8])
