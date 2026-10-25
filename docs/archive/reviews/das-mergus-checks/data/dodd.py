import json,math,numpy as np
from scipy import stats
J=json.load(open("decoded.json"))
th=[k*math.pi/5 for k in range(5)]
T=np.array([[1/5]*5,[2/5*math.cos(2*t) for t in th],[2/5*math.sin(2*t) for t in th],[2/5*math.cos(4*t) for t in th],[2/5*math.sin(4*t) for t in th]])
names=["const","c2","s2","c4","s4"]
for j,rows in J.items():
    d={(r["theta_index"],r["arm"]):r for r in rows if r["readout"]=="direct" and not r["block"].startswith("mutation")}
    D={k:(r["mode"][2]+r["mode"][3])/sum(r["mode"][:4]) for k,r in d.items()}
    V={k:D[k]*(1-D[k])/sum(d[k]["mode"][:4]) for k in d}
    # sign pattern arms 0..3: + - - +
    sg={0:1,1:-1,2:-1,3:1}
    odd=np.array([sum(sg[a]*D[(t,a)] for a in range(4))/4 for t in range(5)])
    c=T@odd
    # binomial variance of coefficients
    vodd=np.array([sum(V[(t,a)] for a in range(4))/16 for t in range(5)])
    vbin=(T**2)@vodd
    # empirical replicate variance: same-sign arms share a configuration
    diffs=[D[(t,0)]-D[(t,3)] for t in range(5)]+[D[(t,1)]-D[(t,2)] for t in range(5)]
    s2=np.mean(np.square(diffs))/2  # per-setting variance, 10 df
    binmean=np.mean(list(V.values()))
    vemp=(T**2)@np.full(5,s2*4/16)
    print(j,"replicate per-setting var",s2,"binomial mean var",binmean,"ratio",s2/binmean,"chi2(10) of replicate diffs under binomial",
          sum(dd**2/(V[(t,a)]+V[(t,b)]) for dd,(t,a,b) in zip(diffs,[(t,0,3) for t in range(5)]+[(t,1,2) for t in range(5)])))
    for i,n in enumerate(names):
        tval=c[i]/math.sqrt(vemp[i]); p=2*stats.t.sf(abs(tval),10)
        print(f"  {n}: coef {c[i]:+.6f}  binomial z {c[i]/math.sqrt(vbin[i]):+.2f}  replicate-variance t10 {tval:+.2f} p {p:.4g}")
