import json,sys,os
repo=sys.argv[1]
st=json.load(open(f"{repo}/docs/state/research_state.json")); cl=st["claims"]
ids={c["id"] for c in cl}; acq={a["id"] for a in st["acquisitions"]}; gates={g["name"] for g in json.load(open(f"{repo}/ci/gates.json"))["gates"]}
ud=[(c["id"],d) for c in cl for d in c.get("depends_on",[]) if d not in ids]
ua=[(c["id"],a) for c in cl for a in c.get("acquisitions",[]) if a not in acq]
ug=[(c["id"],g) for c in cl for g in c.get("gates",{}) if g not in gates]
md=[(c["id"],d) for c in cl for d in c.get("documents",[]) if not d.startswith("http") and not os.path.exists(os.path.join(repo,d.split("#")[0]))]
# cycle detection: Kahn
indeg={i:0 for i in ids}; adj={c["id"]:[d for d in c.get("depends_on",[]) if d in ids] for c in cl}
for i,ds in adj.items():
    for d in ds: indeg[d]+=1
q=[i for i in ids if indeg[i]==0]; seen=0
while q:
    i=q.pop(); seen+=1
    for d in adj[i]:
        indeg[d]-=1
        if indeg[d]==0: q.append(d)
print(repo.split("/")[-1],"unknown deps",len(ud),"unknown acq",len(ua),"unknown gates",len(ug),"missing docs",len(md),"nodes in cycles",len(ids)-seen)
