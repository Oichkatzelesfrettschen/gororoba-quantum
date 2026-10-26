from pathlib import Path
import json,math,collections,numpy as np
from fractions import Fraction as F
J=json.load(open("decoded.json"))
th=[k*math.pi/5 for k in range(5)]
T=np.array([[1/5]*5,[2/5*math.cos(2*t) for t in th],[2/5*math.sin(2*t) for t in th],[2/5*math.cos(4*t) for t in th],[2/5*math.sin(4*t) for t in th]])
sg={0:1,1:-1,2:-1,3:1}
for j,rows in J.items():
    d={(r["theta_index"],r["arm"]):r for r in rows if r["readout"]=="direct" and not r["block"].startswith("mutation")}
    W=np.zeros((5,20)); z=[];v=[];N=[];keys=sorted(d)
    for i,k in enumerate(keys):
        r=d[k]; n4=sum(r["mode"][:4]); D=(r["mode"][2]+r["mode"][3])/n4; z.append(D); v.append(D*(1-D)/n4); N.append(n4)
        W[:,i]=T[:,k[0]]*sg[k[1]]/4
    z=np.array(z);c=W@z;S=(W*np.array(v))@W.T
    rad=np.sqrt(0.5*math.log(2*5/0.01)*((W*W)@(1/np.array(N))))
    def gls(X):
        Si=np.linalg.inv(S); b=np.linalg.solve(X.T@Si@X,X.T@Si@c); r=c-X@b; return float(r@Si@r),b
    q1,b1=gls(np.array([[0],[0],[1.],[0],[0]])); q2,_=gls(np.array([[1.],[-1],[0],[0],[0]]))
    print(j,"radii",np.round(rad,6),"theta-shift chi2",round(q1,3),"eps",round(0.5*math.asin(4*b1[0]),4),"phi-offset chi2",round(q2,3))
# residual correlations in pooled config comparison (block, non-mutation)
for ro in ("x","y","direct"):
    vals={}
    for j,rows in J.items():
        g=collections.defaultdict(lambda:np.zeros(12)); idl={}
        for r in rows:
            if r["readout"]!=ro or r["block"].startswith("mutation"): continue
            g[r["cfg"]]+=np.array(r["mode"])
        vals[j]={k:((m[2]+m[3])/m[:4].sum() if ro=="direct" else (m[0]-m[3])/m[:4].sum()) for k,m in g.items()}
    # ideal from cases
    cases=json.load(open(str(Path(__file__).resolve().parents[5]) + "/results/quandela/runs/2026-10-24T091642Z-qpu_ascella-ascella_signed_coherence-job-00/cases.json"))["settings"]
    rows=J["job-00"]; ideal={}
    for r,s in zip(rows,sorted(cases,key=lambda s:s["observation_index"])):
        if r["readout"]==ro and not r["block"].startswith("mutation"): ideal[r["cfg"]]=s["ideal"]["dark" if ro=="direct" else "z"]
    ks=sorted(ideal); a=np.array([vals["job-00"][k]-ideal[k] for k in ks]); b=np.array([vals["job-01"][k]-ideal[k] for k in ks])
    print(ro,"residual correlation",round(float(np.corrcoef(a,b)[0,1]),4))
# detector-efficiency counterexample r=2, exact on grid
def x(t,r): s=math.sin(t)**2; return 2*s/(1+r+(1-r)*s)
f=np.array([x(t,2) for t in th]); print("r=2 coefficients",np.round(T@f,8))
