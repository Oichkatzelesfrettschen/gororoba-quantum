import json,collections,math
from scipy import stats
J=json.load(open("decoded.json"))
zc=stats.norm.isf(0.05/30/2)
for j,rows in J.items():
    g=collections.defaultdict(list)
    for r in rows: g[r["cfg"]].append(r)
    best=0
    for v in g.values():
        f,l=v[0],v[-1]
        lr=lambda r: math.log((r["out"]+.5)/r["N"])
        z2=(lr(l)-lr(f))**2/(1/(f["out"]+.5)+1/(l["out"]+.5))
        best=max(best,z2)
    # Wald rejects when z2/phi >= zc^2
    print(j,"break-even dispersion phi* (first Holm rejection reappears below)",round(best/zc**2,1))
print("design-order lag1 +0.280039 asymptotic two-sided p (sd 1/sqrt(64))",2*stats.norm.sf(0.280039*8))
