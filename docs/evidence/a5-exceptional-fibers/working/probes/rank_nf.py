"""Rank over F_p of the k-span of polynomials written by Singular `write` (one per comma-separated entry)."""
import re
import sys

import flint

p = int(sys.argv[2])
txt = open(sys.argv[1]).read().replace("\n", "")
polys = [s for s in txt.split(",") if s.strip()]
term = re.compile(r"([+-]?)(\d*)\*?((?:[a-z]\w*(?:\^\d+)?\*?)*)")


def parse(s):
    out = {}
    for m in re.finditer(r"([+-]?)([^+-]+)", s.replace("^-", "^m")):
        sign, body = m.groups()
        coef, mon = 1, []
        for f in body.split("*"):
            if f.isdigit():
                coef *= int(f)
            elif f:
                v, _, e = f.partition("^")
                mon.append((v, int(e) if e else 1))
        out_key = tuple(sorted(mon))
        out[out_key] = (out.get(out_key, 0) + (-coef if sign == "-" else coef)) % p
    return out


rows = [parse(s) for s in polys]
cols = {}
for r in rows:
    for k in r:
        cols.setdefault(k, len(cols))
M = flint.nmod_mat(len(rows), len(cols), p)
for i, r in enumerate(rows):
    for k, v in r.items():
        M[i, cols[k]] = v
print("polys", len(rows), "monomials", len(cols), "rank", M.rank())
