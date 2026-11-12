"""Check that y_i -> c_i y_i carries the E8-bar -> N- quadric relations onto the N+ quadric span over F_p.

Usage: k2_transport.py NPLUS_REL NMINUS_REL P MAP_JSON
The signs c_i come from the G_map of MAP_JSON, a single npm_map.py record whose permutation
must be the identity; a relation file is a comma-separated list of polynomials in y(1..21).
"""

from __future__ import annotations

import json
import re
import sys


def parse_rel(path: str, p: int) -> list[dict]:
    out = []
    for text in open(path).read().replace("\n", "").split(","):
        poly: dict = {}
        for sign, body in re.findall(r"([+-]?)([^+-]+)", text.replace(" ", "")):
            coef, mon = 1, []
            for f in body.split("*"):
                m = re.fullmatch(r"y\((\d+)\)(?:\^(\d+))?", f)
                if m:
                    mon += [int(m.group(1))] * int(m.group(2) or 1)
                else:
                    coef *= int(f)
            key = tuple(sorted(mon))
            poly[key] = (poly.get(key, 0) + (-coef if sign == "-" else coef)) % p
        poly = {k: v for k, v in poly.items() if v}
        if poly:
            out.append(poly)
    return out


def rank(rows: list[dict], p: int) -> int:
    piv: dict = {}
    for r0 in rows:
        r = dict(r0)
        while r:
            k = max(r)
            if k not in piv:
                inv = pow(r[k], -1, p)
                piv[k] = {m: v * inv % p for m, v in r.items()}
                break
            c = r[k]
            for m, v in piv[k].items():
                x = (r.get(m, 0) - c * v) % p
                if x:
                    r[m] = x
                else:
                    r.pop(m, None)
    return len(piv)


def main() -> None:
    plus, minus, p, map_path = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
    gmap = json.loads(open(map_path).read())["G_map"]
    if [j for j, _ in gmap] != list(range(len(gmap))):
        raise ValueError("G_map permutation is not the identity")
    signs = [c for _, c in gmap]
    Kp, Km = parse_rel(plus, p), parse_rel(minus, p)
    moved = []
    for f in Km:
        g = {}
        for mon, c in f.items():
            s = 1
            for i in mon:
                s *= signs[i - 1]
            g[mon] = c if s > 0 else (-c) % p
        moved.append(g)
    rp, rm, rboth = rank(Kp, p), rank(moved, p), rank(Kp + moved, p)
    print(
        json.dumps(
            {
                "check": "e8-k2-transport",
                "prime": p,
                "relations": [plus, minus],
                "map": map_path,
                "rank_K2_plus": rp,
                "rank_K2_minus_moved": rm,
                "rank_union": rboth,
                "equal_spans": rp == rm == rboth,
            }
        )
    )


if __name__ == "__main__":
    main()
