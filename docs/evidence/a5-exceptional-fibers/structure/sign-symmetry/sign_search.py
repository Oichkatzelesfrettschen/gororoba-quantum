"""Search diagonal sign changes t_i -> s_i t_i carrying (J+, G+) onto (J-, G-) span-wise over F_p.

Prints, for every sign vector that maps span(J+) onto span(J-) generator by generator up to sign, the rank of
span(G-) + span(G+(s)) and which G- generators fall outside span(G+(s)).
"""

from __future__ import annotations

import itertools
import re
import sys

P = 0
VARS: list[str] = []


def field(pattern: str, text: str) -> str:
    m = re.search(pattern, text)
    if m is None:
        raise ValueError(f"header lacks {pattern}")
    return m.group(1)


def parse(text: str) -> dict[tuple[int, ...], int]:
    poly: dict[tuple[int, ...], int] = {}
    for sign, body in re.findall(r"([+-]?)([^+-]+)", text.replace(" ", "").replace("\n", "")):
        coef = 1
        exps = [0] * len(VARS)
        for f in body.split("*"):
            if re.fullmatch(r"\d+", f):
                coef *= int(f)
            else:
                v, _, e = f.partition("^")
                exps[VARS.index(v)] += int(e) if e else 1
        m = tuple(exps)
        poly[m] = (poly.get(m, 0) + (-coef if sign == "-" else coef)) % P
    return {m: c for m, c in poly.items() if c}


def load(path: str) -> tuple[list, list]:
    global P, VARS
    t = open(path).read()
    P = int(field(r"ring r=(\d+),", t))
    VARS = field(r"ring r=\d+,\(([^)]*)\)", t).split(",")
    J = [parse(g) for g in field(r"ideal J=([^;]*);", t).split(",")]
    G = [parse(g) for g in field(r"ideal G=([^;]*);", t).split(",")]
    return J, G


def flip(poly: dict, s: tuple[int, ...]) -> dict:
    out = {}
    for m, c in poly.items():
        sg = 1
        for e, si in zip(m, s, strict=True):
            if si < 0 and e % 2:
                sg = -sg
        out[m] = c if sg > 0 else (-c) % P
    return out


def rank(rows: list[dict]) -> int:
    piv: dict = {}
    for r0 in rows:
        r = dict(r0)
        while r:
            k = max(r)
            if k not in piv:
                inv = pow(r[k], -1, P)
                piv[k] = {m: v * inv % P for m, v in r.items()}
                break
            c = r[k]
            for m, v in piv[k].items():
                x = (r.get(m, 0) - c * v) % P
                if x:
                    r[m] = x
                else:
                    r.pop(m, None)
    return len(piv)


def main() -> None:
    Jp, Gp = load(sys.argv[1])
    Jm, Gm = load(sys.argv[2])
    rJm, rGm = rank(Jm), rank(Gm)
    print("rank J-", rJm, "rank G-", rGm, "rank G+", rank(Gp))
    for s in itertools.product((1, -1), repeat=len(VARS)):
        Js = [flip(j, s) for j in Jp]
        if rank(Jm + Js) != rJm:
            continue
        Gs = [flip(g, s) for g in Gp]
        r = rank(Gm + Gs)
        outside = [i for i, g in enumerate(Gm) if rank(Gs + [g]) > rank(Gs)] if r > rGm else []
        print("signs", s, "J ok", "rank G- + G+(s)", r, "G- outside", outside)


if __name__ == "__main__":
    main()
