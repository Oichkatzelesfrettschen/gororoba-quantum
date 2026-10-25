import json,collections,numpy as np
from scipy import stats
J=json.load(open("decoded.json"))
def stat(m,N,readout):
    return ((m[0]-m[3])/N, (m[0]+m[3]-((m[0]-m[3])/N)**2*N)/N/N) if readout in("x","y") else ((m[2]+m[3])/N, ((m[2]+m[3])/N)*(1-(m[2]+m[3])/N)/N)
for denom in ("twelve","block"):
  for ro in ("x","y","direct"):
    pools={}
    for j,rows in J.items():
        g=collections.defaultdict(lambda:[np.zeros(12),0])
        for r in rows:
            if r["readout"]!=ro or r["block"].startswith("mutation"): continue
            g[r["cfg"]][0]+=np.array(r["mode"]); 
        pools[j]={}
        for k,(m,_) in g.items():
            N=m.sum() if denom=="twelve" else m[:4].sum()
            pools[j][k]=stat(m,N,ro)
    ks=sorted(set(pools["job-00"])&set(pools["job-01"]))
    a=np.array([pools["job-00"][k] for k in ks]); b=np.array([pools["job-01"][k] for k in ks])
    chi=(((a[:,0]-b[:,0])**2)/(a[:,1]+b[:,1])).sum()
    print(denom,ro,"configs",len(ks),"chi2",round(chi,3),"p",round(stats.chi2.sf(chi,len(ks)),5),"p if /1.43",round(stats.chi2.sf(chi/1.43,len(ks)),4))
