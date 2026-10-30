"""Left kernel over F_p of the normal forms written by Singular: each kernel vector c gives the fiber relation sum c_b m_b.

Usage: relations_nf.py NF_FILE P MONOMIAL_FILE OUT_FILE
MONOMIAL_FILE lists the target monomials m_b (comma-separated, Singular syntax), in the order of the normal forms.
OUT_FILE receives the relations as one comma-separated Singular ideal body.
"""

import re
import sys

import flint

nf_path, p, mon_path, out_path = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4]


def parse(s):
    out = {}
    for m in re.finditer(r"([+-]?)([^+-]+)", s):
        sign, body = m.groups()
        coef, mon = 1, []
        for f in body.split("*"):
            if f.isdigit():
                coef *= int(f)
            elif f:
                v, _, e = f.partition("^")
                mon.append((v, int(e) if e else 1))
        key = tuple(sorted(mon))
        out[key] = (out.get(key, 0) + (-coef if sign == "-" else coef)) % p
    return out


rows = [parse(s) for s in open(nf_path).read().replace("\n", "").split(",")]
mons = [s.strip() for s in open(mon_path).read().replace("\n", "").split(",")]
if len(mons) != len(rows):
    raise ValueError(f"{len(rows)} normal forms but {len(mons)} monomials")
cols = {}
for r in rows:
    for k in r:
        cols.setdefault(k, len(cols))
# Left kernel of R (rows x cols) is the right kernel of R^T.
t = flint.nmod_mat(len(cols), len(rows), p)
for i, r in enumerate(rows):
    for k, v in r.items():
        t[cols[k], i] = v
kernel, nullity = t.nullspace()
rels = []
for j in range(nullity):
    terms = [f"{int(kernel[i, j])}*{mons[i]}" for i in range(len(rows)) if int(kernel[i, j])]
    rels.append("+".join(terms))
open(out_path, "w").write(",\n".join(rels))
print("normal_forms", len(rows), "rank", len(rows) - nullity, "relations", nullity)
