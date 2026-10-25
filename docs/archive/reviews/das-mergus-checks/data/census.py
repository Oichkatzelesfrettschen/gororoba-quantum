import json,sys,subprocess,hashlib,collections,os
repo=sys.argv[1]
st=json.load(open(f"{repo}/docs/state/research_state.json"))
print("top keys",list(st.keys()))
cl=st["claims"];acq=st["acquisitions"]
print("claims",len(cl),"acq",len(acq))
print("status",collections.Counter(c["status"] for c in cl))
print("prov",collections.Counter(a["provider"] for a in acq))
ev=[(c["id"],e) for c in cl for e in c.get("evidence",[])]
print("bindings",len(ev),"unique",len({e["path"] for _,e in ev}))
bad=0;missing=0
for cid,e in ev:
    p=os.path.join(repo,e["path"])
    if not os.path.isfile(p): missing+=1; continue
    if hashlib.sha256(open(p,'rb').read()).hexdigest()!=e.get("sha256"): bad+=1
print("hash mismatch",bad,"missing",missing)
g=json.load(open(f"{repo}/ci/gates.json"));print("gates",len(g["gates"]))
import glob
pl=[json.load(open(p)) for p in glob.glob(f"{repo}/docs/state/plans/*.json")]
print("plans",len(pl),collections.Counter(p.get("state") for p in pl))
