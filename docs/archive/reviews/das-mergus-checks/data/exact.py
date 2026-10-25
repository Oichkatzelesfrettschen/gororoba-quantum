"""Exact conditional (hypergeometric) two-sided probability-ordered test, integer arithmetic."""
import json,collections,math,random,itertools
from fractions import Fraction
J=json.load(open("decoded.json"))
def fisher2(a,n1,b,n2):
    K=a+b; N=n1+n2
    lo=max(0,K-n2); hi=min(K,n1)
    w={k:math.comb(n1,k)*math.comb(n2,K-k) for k in range(lo,hi+1)}
    obs=w[a]; tot=sum(w.values())
    return Fraction(sum(v for v in w.values() if v<=obs),tot)
def holm(ps,alpha=Fraction(1,20)):
    order=sorted(range(len(ps)),key=lambda i:ps[i]); m=len(ps); rej=[False]*m
    for r,i in enumerate(order):
        if ps[i]<=alpha/(m-r): rej[i]=True
        else: break
    return rej
pairs=[]
for j,rows in J.items():
    g=collections.defaultdict(list)
    for r in rows: g[r["cfg"]].append(r)
    for v in g.values():
        f,l=v[0],v[-1]
        pairs.append(dict(job=j,first=f,last=l,same_parity=(l["pos"]-f["pos"])%2==0,gap=l["pos"]-f["pos"],
                          diffparams=f["params"]!=l["params"]))
ps=[fisher2(p["first"]["out"],p["first"]["N"],p["last"]["out"],p["last"]["N"]) for p in pairs]
rej=holm(ps)
print("pairs",len(pairs),"occurrences",2*len(pairs),"rejected",sum(rej),{j:sum(r for r,p in zip(rej,pairs) if p["job"]==j) for j in J})
big=max(pairs,key=lambda p:abs(math.log((p["last"]["out"]+.5)/(p["first"]["out"]+.5))))
print("largest log change",big["first"]["name"],big["first"]["out"],big["first"]["N"],"->",big["last"]["name"],big["last"]["out"],big["last"]["N"])
print("diff params pairs",[(p["job"],p["first"]["name"],p["last"]["name"]) for p in pairs if p["diffparams"]])
for sp in (True,False):
    sel=[r for r,p in zip(rej,pairs) if p["job"]=="job-01" and p["same_parity"]==sp]
    print("job-01 same_parity=",sp,"rejected",sum(sel),"of",len(sel))
# also per-job Holm (30 each)
for j in J:
    idx=[i for i,p in enumerate(pairs) if p["job"]==j]; r=holm([ps[i] for i in idx]); print(j,"per-job Holm",sum(r))
# Null family: all within-job pairs of DIFFERENT configurations with the same gap multiset; Holm-free rate
# compute raw rejection rate at Holm-equivalent threshold alpha/60 (most stringent) and at the realized Holm cutoff
cut=max([p for p,r in zip(ps,rej) if r]); print("realized Holm max rejected p", float(cut))
def rate(cands):
    rs=[fisher2(a["out"],a["N"],b["out"],b["N"])<=cut for a,b in cands]; return sum(rs),len(rs)
for j,rows in J.items():
    cfgpairs={(p["first"]["pos"],p["last"]["pos"]) for p in pairs if p["job"]==j}
    gaps=collections.Counter(p["gap"] for p in pairs if p["job"]==j)
    cands=[(rows[i],rows[i+gp]) for gp in sorted(gaps) for i in range(64-gp) if rows[i]["cfg"]!=rows[i+gp]["cfg"]]
    print(j,"non-config pairs at the same gaps: rejected at realized cutoff",rate(cands))
    cfgr=[r for r,p in zip(rej,pairs) if p["job"]==j]; print(j,"config pairs rejected",sum(cfgr),len(cfgr))
    for par in (0,1):
        c=[(a,b) for a,b in itertools.combinations(rows,2) if a["cfg"]!=b["cfg"] and (b["pos"]-a["pos"])%2==par]
        print(j,"all non-config pairs, gap parity",par,"rejected",rate(c))
json.dump([dict(job=p["job"],first=p["first"]["name"],last=p["last"]["name"],fpos=p["first"]["pos"],lpos=p["last"]["pos"],
  a=p["first"]["out"],n1=p["first"]["N"],b=p["last"]["out"],n2=p["last"]["N"],p=float(q),holm=r) for p,q,r in zip(pairs,ps,rej)],open("pairs.json","w"),indent=0)
