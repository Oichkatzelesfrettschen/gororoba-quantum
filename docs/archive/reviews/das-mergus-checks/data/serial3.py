"""Lag autocorrelations of the log outside-block counts in execution and design order, with a permutation null.

One generator seeded from the ANU QRNG serves both jobs in order: job-00 takes
the first 20,000 permutations of the stream and job-01 the next 20,000, and
the null's lag-one statistics are computed for all permutations at once.
"""
import json
import numpy as np
J=json.load(open("decoded.json"))
def acf(x,l):
    d=x-x.mean(); return float((d[:-l]*d[l:]).sum()/(d*d).sum())
def acf1_rows(X):
    D=X-X.mean(axis=1,keepdims=True); return (D[:,:-1]*D[:,1:]).sum(axis=1)/(D*D).sum(axis=1)
rng=np.random.default_rng(39076)  # ANU QRNG docs/evidence/anu_qrng/draw-2026-10-25T095947Z.json index 0
for j,rows in J.items():
    e=np.log(np.array([r["out"] for r in rows])+0.5)
    d=np.log(np.array([r["out"] for r in sorted(rows,key=lambda r:r["design"])])+0.5)
    print(j,"exec",[round(acf(e,l),6) for l in (1,2,3,4)],"design lag1",round(acf(d,1),6))
    v=acf(e,1)
    null=acf1_rows(rng.permuted(np.tile(e,(20000,1)),axis=1))
    print("  perm p two-sided |null|>=|v|",(1+(np.abs(null)>=abs(v)).sum())/20001, "design lag1 perm p",(1+(np.abs(null)>=abs(acf(d,1))).sum())/20001)
