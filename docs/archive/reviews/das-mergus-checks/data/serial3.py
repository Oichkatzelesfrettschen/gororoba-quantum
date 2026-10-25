import json,numpy as np
J=json.load(open("decoded.json"))
def acf(x,l):
    d=x-x.mean(); return float((d[:-l]*d[l:]).sum()/(d*d).sum())
for j,rows in J.items():
    e=np.log(np.array([r["out"] for r in rows])+0.5)
    d=np.log(np.array([r["out"] for r in sorted(rows,key=lambda r:r["design"])])+0.5)
    print(j,"exec",[round(acf(e,l),6) for l in (1,2,3,4)],"design lag1",round(acf(d,1),6))
    # exact-ish permutation null for lag1, 20000 draws fixed seed (classical nuisance, not new science seed)
    rng=np.random.default_rng(39076); v=acf(e,1)  # ANU QRNG docs/evidence/anu_qrng/draw-2026-10-25T095947Z.json index 0
    null=np.array([acf(rng.permutation(e),1) for _ in range(20000)])
    print("  perm p two-sided |null|>=|v|",(1+(np.abs(null)>=abs(v)).sum())/20001, "design lag1 perm p",(1+(np.abs(null)>=abs(acf(d,1))).sum())/20001)
