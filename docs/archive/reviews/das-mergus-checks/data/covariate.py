import json,collections,numpy as np
from scipy import stats
J=json.load(open("decoded.json"))
for j,rows in J.items():
    o=np.array([r["out"] for r in rows],float); N=np.array([r["N"] for r in rows],float)
    lr=np.log((o+0.5)/N)
    pred=np.full(64,np.nan)
    for t in range(64):
        nb=[lr[s] for s in (t-2,t+2) if 0<=s<64]; pred[t]=np.mean(nb)
    res=lr-pred
    print(j,"var log-rate",lr.var().round(4),"var residual after lag-2 neighbor predictor",res.var().round(4),"R2",round(1-res.var()/lr.var(),3))
    # Pearson dispersion of counts against neighbor-predicted rates
    mu=N*np.exp(pred); phi=((o-mu)**2/mu).sum()/63; print("  quasi-Poisson dispersion phi vs neighbor prediction",round(phi,1))
    g=collections.defaultdict(list)
    for r in rows: g[r["cfg"]].append(r["pos"])
    fl=[(v[0],v[-1]) for v in g.values()]
    a=np.array([res[f] for f,l in fl]); b=np.array([res[l] for f,l in fl])
    print("  config-mate residual Spearman",stats.spearmanr(a,b))
    # raw log-rate config-mate agreement
    print("  config-mate raw log-rate Spearman",stats.spearmanr([lr[f] for f,l in fl],[lr[l] for f,l in fl]))
    # overdispersed Wald test of first vs last: var = phi*(1/o_f+1/o_l) on log scale
    z=[(lr[l]-lr[f])/np.sqrt(phi*(1/(o[f]+.5)+1/(o[l]+.5))) for f,l in fl]
    p=2*stats.norm.sf(np.abs(z)); 
    ps=sorted(p); m=len(ps); k=0
    while k<m and ps[k]<=0.05/(m-k): k+=1
    print("  overdispersed log-Wald first-vs-last Holm(30) rejections",k)
