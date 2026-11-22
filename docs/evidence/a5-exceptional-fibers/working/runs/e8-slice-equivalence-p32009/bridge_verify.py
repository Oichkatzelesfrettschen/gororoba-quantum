"""Writes the Singular verification of a map found by slice_bridge.py.

Usage: bridge_verify.py CELL RECORD.json KA.sing KH.sing OUT.sing
"""

import json
import sys

cell, rec, ka, kh, out = sys.argv[1:6]
with open(rec, encoding="utf-8") as handle:
    r = json.load(handle)
if r["verdict"] != "map_found":
    sys.exit("no map in the record")
g = r["map"]


def images(m: list[list[int]]) -> str:
    return ",".join("+".join(f"{c}*y({j + 1})" for j, c in enumerate(row) if c) for row in m)


bad = [row[:] for row in g]
bad[0][0] = (bad[0][0] + 1) % r["prime"]
lines = [
    "ring r=32009,(y(1..21)),dp; option(redSB);",
    f'< "{ka}";',
    f'< "{kh}";',
    f"map f=r,{images(g)};",
    f"map fbad=r,{images(bad)};",
    "ideal T=f(KA); ideal sT=std(T); ideal sKH=std(KH); ideal sKA=std(KA);",
    f'"BRIDGE VERIFY cell {cell} transported_mod_header",size(reduce(T,sKH)),'
    '"header_mod_transported",size(reduce(KH,sT)),"generators",size(minbase(T)),size(minbase(KH)),'
    '"dim",dim(sT),dim(sKH),"mult",mult(sT),mult(sKH);',
    f'"BRIDGE CONTROL cell {cell} identity weight_mod_header",size(reduce(KA,sKH)),'
    '"header_mod_weight",size(reduce(KH,sKA));',
    "ideal B=fbad(KA); ideal sB=std(B);",
    f'"BRIDGE CONTROL cell {cell} perturbed_entry transported_mod_header",size(reduce(B,sKH)),'
    '"header_mod_transported",size(reduce(KH,sB));',
    "ideal FI; int a; for(a=1;a<=21;a++){FI[a]=f[a];} matrix G=jacob(FI);",
    f'"BRIDGE DET cell {cell} nonzero",det(G)!=0;',
    '"EXIT 0"; quit;',
]
with open(out, "w", encoding="utf-8") as handle:
    handle.write("\n".join(lines) + "\n")
