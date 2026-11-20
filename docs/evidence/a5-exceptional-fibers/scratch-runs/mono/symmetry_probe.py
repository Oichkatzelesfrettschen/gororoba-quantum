"""Probe: substitutions of (a, rho, sig, w) that preserve the truncated ideal I of the same-sign X slice."""
import sys, importlib.util, itertools
from pathlib import Path
from flint import nmod_mat
root = Path(sys.argv[1]); N = int(sys.argv[2]); p = 32009
spec = importlib.util.spec_from_file_location("lad", root / "docs/evidence/a5-exceptional-fibers/monomial-ladder/x_same_ladder.py")
lad = importlib.util.module_from_spec(spec); spec.loader.exec_module(lad)
gens = lad.generators("xm-nm", p, N)
ctx = gens[0].context(); a, rho, sig, w = ctx.gens()
monos = lad.ring_basis(ctx, N, False)  # a basis of the slice ring R modulo n^N, so the span is I, not I P
def rank(polys):
    index = {}; rows = []
    for q in polys:
        row = {index.setdefault(tuple(int(v) for v in e), len(index)): int(c) for e, c in q.to_dict().items() if sum(e) < N}
        rows.append(row)
    m = nmod_mat(len(rows), len(index), p)
    for i, row in enumerate(rows):
        for j, v in row.items(): m[i, j] = v
    return m.rank()
ideal = [lad.truncate(ctx, g * m, N) for g in gens for m in monos]
ideal = [q for q in ideal if q]
r0 = rank(ideal); print("order", N, "rank of truncated ideal", r0, flush=True)
inv = lambda v: pow(v, -1, p)
i = next(v for v in range(2, p) if v * v % p == p - 1)
c, s = 3 * inv(5) % p, 4 * inv(5) % p
subs = {
 "identity (control)": (a, rho, sig, w),
 "parity (-rho, -sig)": (a, -rho, -sig, w),
 "swap rho, sig": (a, sig, rho, w),
 "(sig, -rho)": (a, sig, -rho, w),
 "(rho, -sig)": (a, rho, -sig, w),
 "(-rho, sig)": (a, -rho, sig, w),
 "rotation 3/5, 4/5": (a, c * rho - s * sig, s * rho + c * sig, w),
 "hyperbolic (2 rho, sig/2)": (a, 2 * rho, inv(2) * sig, w),
 "scale (2 rho, 2 sig)": (a, 2 * rho, 2 * sig, w),
 "boost in rho+-sig": (a, (2 + inv(2)) * inv(2) * rho + (2 - inv(2)) * inv(2) * sig, (2 - inv(2)) * inv(2) * rho + (2 + inv(2)) * inv(2) * sig, w),
 "boost in rho+-i sig": (a, (2 + inv(2)) * inv(2) * rho + i * (2 - inv(2)) * inv(2) * sig, -i * (2 - inv(2)) * inv(2) * rho + (2 + inv(2)) * inv(2) * sig, w),
 "a -> -a": (-a, rho, sig, w),
 "a -> 2a": (2 * a, rho, sig, w),
 "shear a -> a + rho": (a + rho, rho, sig, w),
 "shear rho -> rho + a": (a, rho + a, sig, w),
 "w -> 2w (leaves the slice ring)": (a, rho, sig, 2 * w),
 "a -> a + w^2": (a + w * w, rho, sig, w),
 "rho -> rho (1 + w)": (a, rho + rho * w, sig, w),
 "a -> a (1 + w)": (a + a * w, rho, sig, w),
 "w -> -w/(1+w)": (a, rho, sig, lad.truncate(ctx, -w * sum(((-w) ** k for k in range(N)), ctx.from_dict({})), N)),
}
for name, images in subs.items():
    moved = [lad.truncate(ctx, g.compose(*images), N) for g in gens]
    print(name, "preserves" if rank(ideal + moved) == r0 else "moves", flush=True)
