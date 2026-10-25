from pathlib import Path
import json,math,numpy as np
J=json.load(open("decoded.json"))
R=str(Path(__file__).resolve().parents[5] / "results/quandela/runs") + "/"
A={"job-00":R+"2026-10-24T091642Z-qpu_ascella-ascella_signed_coherence-job-00/analysis.json","job-01":R+"2026-10-24T153028Z-qpu_ascella-ascella_signed_coherence-job-01/analysis.json"}
th=[k*math.pi/5 for k in range(5)]
T=np.array([[1/5]*5,[2/5*math.cos(2*t) for t in th],[2/5*math.sin(2*t) for t in th],[2/5*math.cos(4*t) for t in th],[2/5*math.sin(4*t) for t in th]])
B=["constant","cos(2 theta)","sin(2 theta)","cos(4 theta)","sin(4 theta)"]
sg={0:1,1:-1,2:-1,3:1}
for j,rows in J.items():
    ret={e["name"]:e for e in json.load(open(A[j]))["analysis"]["endpoints"]}
    idx={(r["readout"],r["theta_index"],r["arm"]):r for r in rows if not r["block"].startswith("mutation")}
    worst=0;worstr=0;n=0
    for lab,ro,par in (("X_odd","x","odd"),("Y_odd","y","odd"),("X_even","x","even"),("Y_even","y","even"),("dark","direct","even")):
        for b in range(5):
            val=0;rad=0
            for k in range(5):
                for a in range(4):
                    r=idx[(ro,k,a)]; m=r["mode"]; N=r["N"]
                    z=(m[2]+m[3])/N if ro=="direct" else (m[0]-m[3])/N
                    w=T[b,k]*(sg[a] if par=="odd" else 1)/4
                    val+=w*z; rad+=w*w*(1 if ro=="direct" else 4)/N
            rad=math.sqrt(0.5*math.log(2*27/0.01)*rad)
            name=f"{lab} {B[b]}"
            if name not in ret: print("missing",name, list(ret)[:30]); continue
            worst=max(worst,abs(val-ret[name]["value"])); worstr=max(worstr,abs(rad-ret[name]["radius"])); n+=1
    print(j,"endpoints compared",n,"max |value diff|",worst,"max |radius diff|",worstr,"retained endpoint count",len(ret),"verdicts",{v:sum(e["verdict"]==v for e in ret.values()) for v in set(e["verdict"] for e in ret.values())})
