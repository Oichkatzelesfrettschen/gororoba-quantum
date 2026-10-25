import json,numpy as np
from scipy import stats
J=json.load(open("decoded.json"))
def acf1(x):
    x=np.asarray(x,float); d=x-x.mean(); return float((d[:-1]*d[1:]).sum()/(d*d).sum())
for j,rows in J.items():
    fr=np.array([r["out"]/r["N"] for r in rows]); byd=sorted(rows,key=lambda r:r["design"])
    fd=np.array([r["out"]/r["N"] for r in byd])
    for lab,f in (("log",np.log),("rank",stats.rankdata)):
        print(j,lab,"exec",acf1(f(fr)),"design",acf1(f(fd)), "spearman lag exec",stats.spearmanr(fr[:-1],fr[1:])[0],"design",stats.spearmanr(fd[:-1],fd[1:])[0])
    # where does the alternation phase flip (exec order)
    hi=(np.log(fr)>np.median(np.log(fr))).astype(int)
    print("  hi pattern exec",''.join(map(str,hi)))
    print("  hi pattern design",''.join(map(str,(np.log(fd)>np.median(np.log(fd))).astype(int))))
