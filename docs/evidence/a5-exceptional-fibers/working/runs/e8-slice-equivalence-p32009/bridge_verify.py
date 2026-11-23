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
    "int v1=size(reduce(T,sKH)); int v2=size(reduce(KH,sT));",
    "int c1=size(reduce(KA,sKH)); int c2=size(reduce(KH,sKA));",
    "ideal B=fbad(KA); ideal sB=std(B); int c3=size(reduce(B,sKH)); int c4=size(reduce(KH,sB));",
    "ideal FI; int a; for(a=1;a<=21;a++){FI[a]=f[a];} matrix G=jacob(FI); int dn=(det(G)!=0);",
    f'"BRIDGE VERIFY cell {cell} transported_mod_header",size(reduce(T,sKH)),'
    '"header_mod_transported",size(reduce(KH,sT)),"generators",size(minbase(T)),size(minbase(KH)),'
    '"dim",dim(sT),dim(sKH),"mult",mult(sT),mult(sKH);',
    f'"BRIDGE CONTROL cell {cell} identity weight_mod_header",size(reduce(KA,sKH)),'
    '"header_mod_weight",size(reduce(KH,sKA));',
    f'"BRIDGE CONTROL cell {cell} perturbed_entry transported_mod_header",size(reduce(B,sKH)),'
    '"header_mod_transported",size(reduce(KH,sB));',
    f'"BRIDGE DET cell {cell} nonzero",dn;',
    "int good=(v1==0 and v2==0 and size(minbase(T))==148 and size(minbase(KH))==148 and dim(sT)==5 and mult(sT)==11"
    " and dn==1 and c1>0 and c2>0 and (c3>0 or c4>0));",
    f'if (good) {{ "BRIDGE VERDICT cell {cell} PASS"; }} else {{ "BRIDGE VERDICT cell {cell} FAIL"; }}',
    '"EXIT 0"; quit;',
]
with open(out, "w", encoding="utf-8") as handle:
    handle.write("\n".join(lines) + "\n")
