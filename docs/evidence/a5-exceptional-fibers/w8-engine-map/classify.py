"""Per-block standard-monomial counts of k[y]/K2 by character class, from engine v11's own functions (not edited).

Usage: classify.py QG_FILE DMAX  (QG_FILE: a retained qG.txt export of the header; DMAX: highest degree)
The block of a degree-d product tuple t is the xor of the blocks of its generators, the engine's own rule
(block_products: beta ^ gchar[f]). Prints JSON.
"""
import importlib.util
import json
import os
import sys

import numpy as np

spec = importlib.util.spec_from_file_location("fiber_rank_v11", os.environ["FIBER_ENGINE"])
E = importlib.util.module_from_spec(spec)
sys.modules["fiber_rank_v11"] = E
spec.loader.exec_module(E)
qg, dmax = sys.argv[1], int(sys.argv[2])
header, receipt = os.environ["HEADER"], os.environ["RECEIPT"]
p, names, j_txt, g_txt = E.parse_header(header)
n = len(names)
J = [E.parse_poly(s, names, p) for s in j_txt]
G = [E.parse_poly(s, names, p) for s in g_txt]
group = E.sign_group([J, G], n, p)
gens = E.independent_generators(group, n)
var_char = [int(sum((int(g[k]) % 2) << i for i, g in enumerate(gens))) for k in range(n)]
gpolys = E.read_list(qg, names, p)
gchar = []
for poly in gpolys:
    chars = set()
    for m in poly:
        e = np.array(m, dtype=np.int64)
        chars.add(int(sum(((e @ g) % 2) << i for i, g in enumerate(gens))))
    if len(chars) != 1:
        raise SystemExit(f"generator spans blocks {chars}")
    gchar.append(chars.pop())
rel, rec = E.load_receipt(receipt, header, p, len(G))
levels, leads = E.standard_monomials(rel, rec, len(G), p, dmax, os.environ["SINGULAR"])
out = {"sign_group": [[names[i] for i in fl] for fl in group], "var_char": dict(zip(names, var_char)),
       "gchar": gchar, "gens_per_block": [gchar.count(b) for b in range(4)], "counts": {}}
for d in range(1, dmax + 1):
    cnt = [0, 0, 0, 0]
    for v in levels[d]:
        b = 0
        for c in E.exps_to_tuple(v):
            b ^= gchar[c]
        cnt[b] += 1
    out["counts"][str(d)] = {"total": len(levels[d]), "per_block": cnt}
print(json.dumps(out))
