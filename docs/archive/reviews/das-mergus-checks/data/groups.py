import json,collections
J=json.load(open("decoded.json"))
for j,rows in J.items():
    g=collections.defaultdict(list)
    for r in rows: g[r["cfg"]].append(r)
    mult=collections.Counter(len(v) for v in g.values()); print(j,"multiplicities",mult)
    for k,v in g.items():
        ps={tuple(r["params"]) for r in v}
        tag="" if len(ps)==1 else f" DISTINCT-PARAMS({len(ps)})"
        if len(v)!=2 or tag: print("  ",[ (r["pos"],r["name"],r["out"],r["N"]) for r in v],tag)
    # parity of first/last positions
    same=sum(1 for v in g.values() if (v[0]["pos"]-v[-1]["pos"])%2==0); print("  same-parity first/last pairs",same,"of",len(g))
    print("  pair gaps",sorted(v[-1]["pos"]-v[0]["pos"] for v in g.values()))
    # design-adjacent same exec parity
    byd=sorted(rows,key=lambda r:r["design"]); print("  design-adjacent same exec parity",sum((byd[i]["pos"]-byd[i+1]["pos"])%2==0 for i in range(63)),"/63")
