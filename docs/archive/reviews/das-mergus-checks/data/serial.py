import json,numpy as np
from scipy import stats
J=json.load(open("decoded.json"))
def acf1(x):
    x=np.asarray(x,float); m=x.mean(); d=x-m
    return float((d[:-1]*d[1:]).sum()/(d*d).sum())
def pear1(x):
    x=np.asarray(x,float); return float(np.corrcoef(x[:-1],x[1:])[0,1])
for j,rows in J.items():
    cnt=[r["out"] for r in rows]; fr=[r["out"]/r["N"] for r in rows]
    print(j,"exec acf1 counts",acf1(cnt),"frac",acf1(fr),"pearson-lag counts",pear1(cnt),"frac",pear1(fr))
    byd=sorted(rows,key=lambda r:r["design"])
    c2=[r["out"] for r in byd]; f2=[r["out"]/r["N"] for r in byd]
    print("   design-order acf1 counts",acf1(c2),"frac",acf1(f2),"pearson",pear1(c2),pear1(f2))
    par=np.array([r["pos"]%2 for r in rows]); lf=np.log(np.array(fr))
    print("   exec parity mean frac even/odd", np.mean(np.array(fr)[par==0]),np.mean(np.array(fr)[par==1]), "MWU p", stats.mannwhitneyu(np.array(fr)[par==0],np.array(fr)[par==1]).pvalue)
a={r["name"]:r for r in J["job-00"]}; b={r["name"]:r for r in J["job-01"]}
names=list(a)
for lab,key in (("count","out"),):
    x=[a[n]["out"] for n in names]; y=[b[n]["out"] for n in names]
    print("identity spearman counts",stats.spearmanr(x,y))
    xf=[a[n]["out"]/a[n]["N"] for n in names]; yf=[b[n]["out"]/b[n]["N"] for n in names]
    print("identity spearman frac",stats.spearmanr(xf,yf))
    xp=[r["out"] for r in J["job-00"]]; yp=[r["out"] for r in J["job-01"]]
    print("positional spearman counts",stats.spearmanr(xp,yp))
    print("positional spearman frac",stats.spearmanr([r["out"]/r["N"] for r in J["job-00"]],[r["out"]/r["N"] for r in J["job-01"]]))
# parity-adjusted identity: compare residual after removing exec-parity mean of log frac
def resid(rows):
    lf=np.log(np.array([r["out"]/r["N"] for r in rows])); p=np.array([r["pos"]%2 for r in rows])
    out=lf.copy()
    for k in (0,1): out[p==k]-=lf[p==k].mean()
    return {r["name"]:out[i] for i,r in enumerate(rows)}
ra,rb=resid(J["job-00"]),resid(J["job-01"])
print("identity spearman after removing exec parity (log frac):",stats.spearmanr([ra[n] for n in names],[rb[n] for n in names]))
