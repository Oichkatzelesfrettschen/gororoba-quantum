import json,math,numpy as np
from scipy import stats
J=json.load(open("decoded.json"))
th=[k*math.pi/5 for k in range(5)]
T=np.array([[1/5]*5,[2/5*math.cos(2*t) for t in th],[2/5*math.sin(2*t) for t in th],[2/5*math.cos(4*t) for t in th],[2/5*math.sin(4*t) for t in th]])
sg={0:1,1:-1,2:-1,3:1}
for j,rows in J.items():
    d=[r for r in rows if r["readout"]=="direct" and not r["block"].startswith("mutation")]
    ideal=lambda r: math.sin(th[r["theta_index"]])**2*0.5
    D=np.array([(r["mode"][2]+r["mode"][3])/sum(r["mode"][:4]) for r in d]); I=np.array([ideal(r) for r in d])
    O=np.array([r["out"]/r["N"] for r in d])
    print(j,"direct D-ideal vs outside frac: spearman",stats.spearmanr(D-I,O))
    dd={(r["theta_index"],r["arm"]):r for r in d}
    oo=np.array([sum(sg[a]*dd[(t,a)]["out"]/dd[(t,a)]["N"] for a in range(4))/4 for t in range(5)])
    print("   sign-odd transform of outside fraction:",np.round(T@oo,5))
    # mode2 vs mode3 split of the D_odd
    for m in (2,3):
        x=np.array([sum(sg[a]*dd[(t,a)]["mode"][m]/sum(dd[(t,a)]["mode"][:4]) for a in range(4))/4 for t in range(5)])
        print("   sign-odd transform of mode",m,"share:",np.round(T@x,5))
