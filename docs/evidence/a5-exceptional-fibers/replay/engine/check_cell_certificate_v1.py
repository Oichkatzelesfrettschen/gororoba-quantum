"""Independent check of an a5-hilbert-cell-certificate-v1 file, in pure Python (standard library only).

The check reads the emitted JSON and, when given, the header file and the retained engine record, and verifies:
  1. lev(row) > lev(col) for every nonzero entry of every M_k (strict level increase, so each t_k acts nilpotently);
  2. M_j M_k = M_k M_j modulo p for every pair, on every basis vector;
  3. J(M) e = 0 for every generator of J and t_k * (class of each product) = 0 (the images lie in W);
  4. the class vectors of the selected products, recomputed here as g(M) e from the G tables, have rank r, and
     left_inverse times them equals the identity;
  5. r equals the retained r_N of the engine record and h_claimed;
and, when the header is given, that its sha256 equals the recorded digest and that the J and G tables equal an
independent parse of the header text.

Usage: check_cell_certificate_v1.py CERT.json [--header HEADER] [--record ENGINE_RECORD.json]
Exit 0 only when every check passes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys


def parse_header(text: str):
    text = text.replace("\n", "")
    m = re.search(r"ring r=(\d+),\(([^)]*)\)", text)
    if m is None:
        raise SystemExit("no ring line")
    p, names = int(m.group(1)), m.group(2).split(",")
    out = {}
    for key in ("J", "G"):
        found = re.search(r"ideal " + key + r"=([^;]*);", text)
        if found is None:
            raise SystemExit(f"no ideal {key}")
        body = found.group(1)
        polys = []
        for s in body.split(","):
            s = "".join(s.split())
            poly: dict[tuple[int, ...], int] = {}
            for sign, term in re.findall(r"([+-]?)([^+-]+)", s):
                coef, e = 1, [0] * len(names)
                for f in term.split("*"):
                    if f.isdigit():
                        coef *= int(f)
                    else:
                        v, _, k = f.partition("^")
                        e[names.index(v)] += int(k) if k else 1
                key_m = tuple(e)
                poly[key_m] = (poly.get(key_m, 0) + (-coef if sign == "-" else coef)) % p
            polys.append({k: c for k, c in poly.items() if c})
        out[key] = polys
    return p, names, out["J"], out["G"]


def rank_mod_p(rows, p):
    rows = [r[:] for r in rows]
    rk, ncols = 0, len(rows[0]) if rows else 0
    for c in range(ncols):
        piv = next((i for i in range(rk, len(rows)) if rows[i][c] % p), None)
        if piv is None:
            continue
        rows[rk], rows[piv] = rows[piv], rows[rk]
        inv = pow(rows[rk][c], -1, p)
        rows[rk] = [x * inv % p for x in rows[rk]]
        for i in range(len(rows)):
            if i != rk and rows[i][c] % p:
                f = rows[i][c]
                rows[i] = [(x - f * y) % p for x, y in zip(rows[i], rows[rk], strict=True)]
        rk += 1
    return rk


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cert")
    ap.add_argument("--header")
    ap.add_argument("--record")
    a = ap.parse_args()
    cert = json.load(open(a.cert))
    results = []

    def report(name, ok, detail=""):
        results.append(ok)
        print(("PASS " if ok else "FAIL ") + name + (": " + detail if detail else ""))

    if cert["schema"] != "a5-hilbert-cell-certificate-v1":
        raise SystemExit("unknown schema")
    p = cert["prime"]
    names = cert["header"]["vars"]
    n = len(names)
    mod = cert["module"]
    q, lev, e = mod["q"], mod["lev"], mod["e"]
    Mm = mod["M"]
    if len(Mm) != n or len(lev) != q:
        raise SystemExit("shape mismatch")
    allvals = [v for ent in Mm for _, _, v in ent]
    report("entries in [1, p-1]", all(1 <= v < p for v in allvals), f"{len(allvals)} nonzero entries")
    cols: list[list[dict[int, int]]] = [[{} for _ in range(q)] for _ in range(n)]  # cols[k][c] = {row: val}
    for k, ent in enumerate(Mm):
        for row, col, val in ent:
            cols[k][col][row] = (cols[k][col].get(row, 0) + val) % p

    report("level increases strictly", all(lev[r] > lev[c] for ent in Mm for r, c, _ in ent))

    def apply(k, vec):
        out = {}
        for c, x in vec.items():
            for r, v in cols[k][c].items():
                out[r] = (out.get(r, 0) + v * x) % p
        return {r: x for r, x in out.items() if x}

    comm_ok = True
    for j in range(n):
        for k in range(j + 1, n):
            for c in range(q):
                if apply(j, apply(k, {c: 1})) != apply(k, apply(j, {c: 1})):
                    comm_ok = False
    report("M_k commute pairwise", comm_ok, f"{n * (n - 1) // 2} pairs on {q} basis vectors")

    def evaluate(table):
        """Class g(M) e of a polynomial table [[coef, exps], ...]; monomials by repeated application."""
        total = {}
        for coef, exps in table:
            vec = {e: 1}
            for k, ek in enumerate(exps):
                for _ in range(ek):
                    vec = apply(k, vec)
            for r, x in vec.items():
                total[r] = (total.get(r, 0) + coef * x) % p
        return {r: x for r, x in total.items() if x}

    j_ok = all(not evaluate(g) for g in cert["header"]["J"])
    report("J(M) e = 0", j_ok, f"{len(cert['header']['J'])} generators")
    prods = cert["products"]
    G = cert["header"]["G"]

    # recompute the class of every selected product from the G tables
    def product_class(tup):
        vec = {e: 1}
        for f in tup:
            new = {}
            for coef, exps in G[f]:
                v = vec
                for k, ek in enumerate(exps):
                    for _ in range(ek):
                        v = apply(k, v)
                for r, x in v.items():
                    new[r] = (new.get(r, 0) + coef * x) % p
            vec = {r: x for r, x in new.items() if x}
        return vec

    allp = [product_class(t) for t in prods["tuples"]]
    killed = all(not apply(k, v) for v in allp for k in range(n))
    report("m * product classes = 0", killed, f"{len(allp)} products")
    sel = prods["selected"]
    dense = [[allp[i].get(c, 0) for c in range(q)] for i in sel]
    rk = rank_mod_p(dense, p)
    report("selected product classes have rank r", rk == len(sel) == prods["r"], f"rank {rk}, r {prods['r']}")
    L = prods["left_inverse"]
    ident = all(
        sum(L[i][c] * dense[j][c] for c in range(q)) % p == (1 if i == j else 0)
        for i in range(len(sel))
        for j in range(len(sel))
    )
    report("left_inverse times selected = identity", ident)
    if a.record:
        rec = json.load(open(a.record))
        report(
            "r equals retained r_N and h_claimed",
            prods["r"] == rec["r_N"] == cert["h_claimed"],
            f"record r_N {rec['r_N']}",
        )
        report(
            "truncation matches record",
            mod["q"] == sum(b["cols"] - b["rank_W"] for b in rec["per_block"].values())
            and cert["truncation"]["N"] == rec["N"]
            and cert["truncation"]["dim_V"] == rec["dim_V"],
        )
    if a.header:
        raw = open(a.header, "rb").read()
        report("header sha256 matches", hashlib.sha256(raw).hexdigest() == cert["header"]["sha256"])
        hp, hn, hJ, hG = parse_header(raw.decode())

        def tab(polys):
            return [sorted([int(c), list(m)] for m, c in poly.items()) for poly in polys]

        report(
            "header tables match an independent parse",
            hp == p
            and hn == names
            and tab(hJ) == [sorted(x) for x in cert["header"]["J"]]
            and tab(hG) == [sorted(x) for x in cert["header"]["G"]],
        )
    report("J_in_W recorded true", cert["J_in_W"] is True)
    ok = all(results)
    print("ALL CHECKS PASS" if ok else "CHECK FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
