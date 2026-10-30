import sys
from pathlib import Path

sys.path.insert(0, str(Path(sys.argv[1]) / "a5-kernel-bundles"))
import kernel_symmetry as ks
from sympy import QQ, Matrix
from sympy.polys.matrices import DomainMatrix

N = 32
g2 = ks._octonion_derivation_triples()
print("g2 triples", len(g2), "rank", ks._rank([ks._flatten_triple(t) for t in g2]))


def commutant_dim(mats):
    # X with X M - M X = 0 for all M; unknowns X (N*N)
    rows = []
    for M in mats:
        for i in range(N):
            for j in range(N):
                r = {}
                for k in range(N):
                    if M[k][j]:
                        r[i * N + k] = r.get(i * N + k, 0) + M[k][j]
                    if M[i][k]:
                        r[k * N + j] = r.get(k * N + j, 0) - M[i][k]
                rows.append(r)
    ent = {(a, c): v for a, r in enumerate(rows) for c, v in r.items() if v}
    D = DomainMatrix.from_dok(ent, (len(rows), N * N), QQ)
    return N * N - D.rank()


def fixed_dim(mats):
    rows = [list(M[i]) for M in mats for i in range(N)]
    return N - Matrix(rows).rank()


for slot, name in enumerate(("base", "domain", "codomain")):
    mats = [t[slot] for t in g2]
    print(name, "commutant dim", commutant_dim(mats), "invariant vectors", fixed_dim(mats))
