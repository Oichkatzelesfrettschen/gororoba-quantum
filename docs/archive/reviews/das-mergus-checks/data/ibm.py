import json,glob,sys,collections
root=sys.argv[1]
files=sorted(glob.glob(root+"/results/live/**/raw/*/pub_*.json",recursive=True))
pubs=len(files); regs=0; entries=0; positions=0; bits=0; mismatch=0; jobs=set(); shots_hist=collections.Counter()
for f in files:
    d=json.load(open(f)); jobs.add(f.split("/raw/")[1].split("/")[0])
    R=d["registers"]; regs+=len(R)
    ns={r["num_shots"] for r in R.values()}
    lens={len(r["bitstrings"]) for r in R.values()}
    if len(ns)!=1 or ns!=lens: mismatch+=1
    positions+=max(ns); shots_hist[max(ns)]+=1
    for r in R.values(): entries+=len(r["bitstrings"]); bits+=len(r["bitstrings"])*r["num_bits"]
print(dict(root=root,jobs=len(jobs),pubs=pubs,register_descriptions=regs,stored_register_entries=entries,aligned_positions=positions,stored_bits=bits,pubs_with_unaligned_registers=mismatch,shots_hist=dict(shots_hist)))
