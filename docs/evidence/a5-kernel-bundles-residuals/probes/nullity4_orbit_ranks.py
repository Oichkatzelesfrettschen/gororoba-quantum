import itertools
import json
import sys
from fractions import Fraction
from pathlib import Path

EV = Path(sys.argv[1])
sys.path.insert(0, str(EV / "a5-kernel-bundles"))
import kernel_symmetry as ks  # noqa: E402

eq, reg = ks.equations, ks.regularity
import parallel  # noqa: E402


def tangent(item):
    zp, gens = item
    y = tuple(eq.y_from_split([Fraction(v) for v in zp]))
    nul = eq.nullity(y)
    if nul != 4:
        return zp, nul, None
    vecs = [ks._rational_matrix_vector_product(g, y) for g in gens]
    return zp, nul, ks._rank(vecs)


if __name__ == "__main__":
    triples, _, _ = ks._solve_lie_triples("")
    gens = tuple(t[0] for t in triples)
    print(
        "symmetry dimension",
        ks._rank([ks._flatten_triple(t) for t in triples]),
        "base rank",
        ks._rank([ks._flatten_matrix(g) for g in gens]),
    )
    pts = [reg.split_point({1: 1}, 3, {1: 5, 3: 3})]  # the V(G) point of the strata record
    # small-grid candidates: u = e1 + a e2, mu, v = b e1 + c e3 + d e5
    for a, mu, b, c, d in itertools.product(range(0, 3), range(0, 4), range(-2, 4), range(0, 4), range(0, 3)):
        pts.append(reg.split_point({1: 1, 2: a}, mu, {1: b, 3: c, 5: d}))
    rows = parallel.ordered_map(tangent, [(p, gens) for p in pts], min_items=1)
    n4 = [(p, r) for p, n, r in rows if n == 4]
    print("candidates", len(rows), "nullity-4", len(n4))
    ranks = sorted({r for _, r in n4})
    print("unit-section K-orbit ranks at nullity-4 points:", ranks)
    print("first points:", json.dumps(n4[:5]))
    ideals = reg.closure_ideals()
    from collections import Counter

    tally: Counter[tuple[str, int]] = Counter()
    for p, r in n4:
        inq = reg.member(ideals["VQ"], p)
        ing = reg.member(ideals["VG"], p)
        tally[(("VQ" if inq else "") + ("VG" if ing else ""), r)] += 1
    print("stratum x orbit rank:", dict(tally))
