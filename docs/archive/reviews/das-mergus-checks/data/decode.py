"""Independent decoder for the two Ascella signed-coherence raw results."""
from pathlib import Path
import json,base64,zlib,hashlib,re,sys
R=str(Path(__file__).resolve().parents[5] / "results/quandela/runs") + "/"
JOBS={"job-00":R+"2026-10-24T091642Z-qpu_ascella-ascella_signed_coherence-job-00",
      "job-01":R+"2026-10-24T153028Z-qpu_ascella-ascella_signed_coherence-job-01"}
def unz(s):
    if not s.startswith(":PCVL:zip:"): raise ValueError(s[:20])
    return zlib.decompress(base64.b64decode(s[10:])).decode()
def bscount(s):
    m=re.fullmatch(r":PCVL:BSCount:\{(.*)\}",s)
    out={}
    for item in m.group(1).split(";"):
        k,v=item.split(">=")
        st=tuple(int(x) for x in k.lstrip("|").split(","))
        if len(st)!=12: raise ValueError(k)
        out[st]=out.get(st,0)+int(v)
    return out
def load():
    jobs={}
    for j,d in JOBS.items():
        raw=json.load(open(d+"/raw/result.json"))
        x=json.loads(raw["results"]); L=x["results_list"]
        cases=json.load(open(d+"/cases.json"))
        S=sorted(cases["settings"],key=lambda s:s["observation_index"])
        if len(L)!=64 or len(S)!=64: raise ValueError
        rows=[]
        for pos,(e,s) in enumerate(zip(L,S)):
            cp=e["iteration"]["circuit_params"]
            if any(abs(cp[k]-s["circuit_params"][k])>1e-15 for k in s["circuit_params"]) or set(cp)!=set(s["circuit_params"]):
                raise ValueError(("param mismatch",j,pos))
            c=bscount(unz(e["results"]))
            single={st:n for st,n in c.items() if sum(st)==1}
            mode=[0]*12
            for st,n in single.items(): mode[st.index(1)]+=n
            cfg=hashlib.sha256((unz(e["computed_circuit"])+"|"+e["computed_input"]).encode()).hexdigest()[:16]
            rows.append(dict(pos=pos,name=s["name"],design=s.get("design_index",s["observation_index"]),
              readout=s["readout"],arm=s["arm"],theta_index=s.get("theta_index"),block=s["block"],
              total=sum(c.values()),multi=sum(n for st,n in c.items() if sum(st)>1),
              vac=sum(n for st,n in c.items() if sum(st)==0),
              N=sum(mode),mode=mode,out=sum(mode[4:]),cfg=cfg,
              params=tuple(round(cp[k],12) for k in sorted(cp,key=lambda q:int(q[1:]))),
              nb_shots_used=e["nb_shots_used"],max_samples=e["iteration"]["max_samples"]))
        jobs[j]=rows
    return jobs
if __name__=="__main__":
    J=load()
    for j,rows in J.items():
        print(j,"iters",len(rows),"total",sum(r["total"] for r in rows),"eligible",sum(r["N"] for r in rows),
              "multi",sum(r["multi"] for r in rows),"vac",sum(r["vac"] for r in rows),"outside",sum(r["out"] for r in rows),
              "cfgs",len({r["cfg"] for r in rows}),"maxsamples",{r["max_samples"] for r in rows})
        print(" out frac", sum(r["out"] for r in rows)/sum(r["N"] for r in rows))
        print(" outside list", [r["out"] for r in rows])
    json.dump({j:[{k:(list(v) if isinstance(v,tuple) else v) for k,v in r.items()} for r in rows] for j,rows in J.items()},open("decoded.json","w"))
