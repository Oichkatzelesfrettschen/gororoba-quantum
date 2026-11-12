"""Certify the coordinate map t8 -> -t8, t9 -> -t9 between the E8-bar -> N+ and N- inputs.

For sigma = (t8, t9) -> (-t8, -t9): checks J+(sigma) and J- generator by generator for G+(sigma)_i = c_i G-_{pi(i)}
with c_i = +-1, comparing the printed coefficients, which are balanced F_p residues of the producer's Q(i)
coefficients; a match is therefore an identity over F_p at the header's (p, i), not over Q(i). A pair that matches
only up to units or recombination reports a failed match. Writes one JSON line.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys

VARS = [f"t{i}" for i in range(1, 10)]
SIGMA = (1, 1, 1, 1, 1, 1, 1, -1, -1)


def field(pattern: str, text: str) -> str:
    m = re.search(pattern, text)
    if m is None:
        raise ValueError(f"header lacks {pattern}")
    return m.group(1)


def parse(text: str) -> dict[tuple[int, ...], int]:
    poly: dict[tuple[int, ...], int] = {}
    for sign, body in re.findall(r"([+-]?)([^+-]+)", text.replace(" ", "").replace("\n", "")):
        coef = 1
        exps = [0] * 9
        for f in body.split("*"):
            if re.fullmatch(r"\d+", f):
                coef *= int(f)
            else:
                v, _, e = f.partition("^")
                exps[VARS.index(v)] += int(e) if e else 1
        m = tuple(exps)
        poly[m] = poly.get(m, 0) + (-coef if sign == "-" else coef)
    return {m: c for m, c in poly.items() if c}


def load(path: str) -> tuple[int, list, list]:
    t = open(path).read()
    p = int(field(r"ring r=(\d+),", t))
    J = [parse(g) for g in field(r"ideal J=([^;]*);", t).split(",")]
    G = [parse(g) for g in field(r"ideal G=([^;]*);", t).split(",")]
    return p, J, G


def flip(poly: dict) -> dict:
    out = {}
    for m, c in poly.items():
        odd = sum(e for e, s in zip(m, SIGMA, strict=True) if s < 0) % 2
        out[m] = -c if odd else c
    return out


def match(src: list[dict], dst: list[dict]) -> list:
    """For each src_i find (j, c) with src_i == c * dst_j as integer polynomials, else None."""
    out = []
    for a in src:
        hit = None
        for j, b in enumerate(dst):
            if a.keys() != b.keys():
                continue
            m0 = next(iter(a))
            if a[m0] % b[m0]:
                continue
            c = a[m0] // b[m0]
            if all(a[m] == c * b[m] for m in a):
                hit = (j, c)
                break
        out.append(hit)
    return out


def main() -> None:
    pp, Jp, Gp = load(sys.argv[1])
    pm, Jm, Gm = load(sys.argv[2])
    Jmap = match([flip(j) for j in Jp], Jm)
    Gmap = match([flip(g) for g in Gp], Gm)
    rec = {
        "check": "e8-np-nm-coordinate-map",
        "sigma": "t8 -> -t8, t9 -> -t9",
        "primes": [pp, pm],
        "inputs": sys.argv[1:3],
        "inputs_sha256": [hashlib.sha256(open(f, "rb").read()).hexdigest() for f in sys.argv[1:3]],
        "J_generators": [len(Jp), len(Jm)],
        "G_generators": [len(Gp), len(Gm)],
        "J_map": Jmap,
        "G_map": Gmap,
        "J_integer_identity": all(h is not None for h in Jmap) and len({h[0] for h in Jmap}) == len(Jm),
        "G_integer_identity": all(h is not None for h in Gmap) and len({h[0] for h in Gmap}) == len(Gm),
    }
    print(json.dumps(rec))


if __name__ == "__main__":
    main()
