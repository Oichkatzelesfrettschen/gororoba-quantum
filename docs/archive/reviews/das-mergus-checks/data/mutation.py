from pathlib import Path
import json,math
J=json.load(open("decoded.json"))
R=str(Path(__file__).resolve().parents[5] / "results/quandela/runs") + "/"
D={"job-00":R+"2026-10-24T091642Z-qpu_ascella-ascella_signed_coherence-job-00","job-01":R+"2026-10-24T153028Z-qpu_ascella-ascella_signed_coherence-job-01"}
for j,rows in J.items():
    S=sorted(json.load(open(D[j]+"/cases.json"))["settings"],key=lambda s:s["observation_index"])
    ret={e["name"]:e for e in json.load(open(D[j]+"/analysis.json"))["analysis"]["endpoints"]}
    diff=clo=rd=rc=0
    for r,s in zip(rows,S):
        if s["block"]!="mutation": continue
        m=r["mode"]; N=r["N"]
        z=(m[2]+m[3])/N if s["readout"]=="direct" else (m[0]-m[3])/N
        Rg=1 if s["readout"]=="direct" else 2
        wd=0.5 if s["generator"]=="j" else -0.5; wc=0.5 if s["generator"]=="i" else 0
        diff+=wd*z; clo+=wc*z; rd+=wd*wd*Rg*Rg/N; rc+=wc*wc*Rg*Rg/N
    k=0.5*math.log(2*27/0.01)
    for nm,v,rr in (("mutation difference",diff,math.sqrt(k*rd)),("mutation dark",clo,math.sqrt(k*rc))):
        print(j,nm,v,ret[nm]["value"],"|dv|",abs(v-ret[nm]["value"]),"radius",rr,ret[nm]["radius"])
