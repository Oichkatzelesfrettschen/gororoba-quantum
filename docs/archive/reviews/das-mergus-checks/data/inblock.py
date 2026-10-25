import json,collections,numpy as np
from scipy import stats
J=json.load(open("decoded.json"))
tot={}
for j,rows in J.items():
    g=collections.defaultdict(list)
    for r in rows: g[r["cfg"]].append(r)
    chis=[];dfs=0;per=[]
    for v in g.values():
        f,l=v[0],v[-1]
        T=np.array([f["mode"][:4],l["mode"][:4]],float)
        keep=T.sum(0)>0; T=T[:,keep]
        c,p,df,_=stats.chi2_contingency(T,correction=False); chis.append(c); dfs+=df; per.append((p,f["name"],l["name"]))
        # also twelve-mode with outside pooled into one cell
    C=sum(chis); print(j,"block-conditioned 4-cell homogeneity over 30 config pairs: chi2",round(C,2),"df",dfs,"p",stats.chi2.sf(C,dfs),"dispersion",round(C/dfs,3))
    print("   smallest pair p",sorted(per)[:3])
    # all members (including quadruple middles)
    C2=0;d2=0
    for v in g.values():
        T=np.array([r["mode"][:4] for r in v],float); T=T[:,T.sum(0)>0]
        c,p,df,_=stats.chi2_contingency(T,correction=False); C2+=c; d2+=df
    print("   all members chi2",round(C2,2),"df",d2,"p",stats.chi2.sf(C2,d2))
