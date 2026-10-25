import json,collections,numpy as np
from scipy import stats
J=json.load(open("decoded.json"))
for j,rows in J.items():
    g=collections.defaultdict(list)
    for r in rows: g[r["cfg"]].append(r)
    tot=collections.Counter(); df=collections.Counter(); minexp=1e9
    for v in g.values():
        f,l=v[0],v[-1]; kind="mutation" if f["block"].startswith("mutation") or l["block"].startswith("mutation") else f["readout"]
        def st(r):
            m=r["mode"]; N=sum(m[:4])
            if r["readout"]=="direct": z=(m[2]+m[3])/N; return z,z*(1-z)/N
            z=(m[0]-m[3])/N; return z,((m[0]+m[3])/N-z*z)/N
        # use pooled variance under H0
        m=np.array(f["mode"][:4])+np.array(l["mode"][:4]); N=m.sum()
        if f["readout"]=="direct": p=(m[2]+m[3])/N; var=p*(1-p)
        else: zz=(m[0]-m[3])/N; var=(m[0]+m[3])/N-zz*zz
        zf,_=st(f); zl,_=st(l)
        c=(zf-zl)**2/(var*(1/sum(f["mode"][:4])+1/sum(l["mode"][:4])))
        tot[kind]+=c; df[kind]+=1
        E=np.outer([sum(f["mode"][:4]),sum(l["mode"][:4])],m/N); minexp=min(minexp,E[E>0].min())
    print(j,{k:(round(tot[k],2),df[k],round(stats.chi2.sf(tot[k],df[k]),4)) for k in tot},"all",round(sum(tot.values()),2),sum(df.values()),round(stats.chi2.sf(sum(tot.values()),sum(df.values())),4),"min expected cell (4-cell test)",round(minexp,3))
