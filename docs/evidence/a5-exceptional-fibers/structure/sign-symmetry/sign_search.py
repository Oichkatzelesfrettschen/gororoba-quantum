"""Search diagonal sign changes t_i -> s_i t_i carrying (J+, G+) onto (J-, G-) span-wise over F_p.

Prints, for every sign vector that maps span(J+) onto span(J-) generator by generator up to sign, the rank of
span(G-) + span(G+(s)) and which G- generators fall outside span(G+(s)).
"""

from __future__ import annotations

import itertools
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import parallel  # noqa: E402

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


def flip(poly: dict, s: tuple[int, ...], p: int) -> dict:
    out = {}
    for m, c in poly.items():
        sg = 1
        for e, si in zip(m, s, strict=True):
            if si < 0 and e % 2:
                sg = -sg
        out[m] = c if sg > 0 else (-c) % p
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


class SignCheck:
    """One sign vector against the fixed headers; the instance pickles to the pool workers."""

    def __init__(self, p: int, Jp: list[dict], Gp: list[dict], Jm: list[dict], Gm: list[dict]) -> None:
        self.p, self.Jp, self.Gp, self.Jm, self.Gm = p, Jp, Gp, Jm, Gm
        self.rJm, self.rGm = rank(Jm, p), rank(Gm, p)

    def __call__(self, s: tuple[int, ...]) -> str | None:
        p = self.p
        Js = [flip(j, s, p) for j in self.Jp]
        if rank(self.Jm + Js, p) != self.rJm:
            return None
        Gs = [flip(g, s, p) for g in self.Gp]
        r = rank(self.Gm + Gs, p)
        rGs = rank(Gs, p)
        outside = [i for i, g in enumerate(self.Gm) if rank(Gs + [g], p) > rGs] if r > self.rGm else []
        return f"signs {s} J ok rank G- + G+(s) {r} G- outside {outside}"


def main() -> None:
    Jp, Gp = load(sys.argv[1])
    Jm, Gm = load(sys.argv[2])
    check = SignCheck(P, Jp, Gp, Jm, Gm)
    print("rank J-", check.rJm, "rank G-", check.rGm, "rank G+", rank(Gp, P))
    vectors = list(itertools.product((1, -1), repeat=len(VARS)))
    for line in parallel.ordered_map(check, vectors):
        if line is not None:
            print(line)


if __name__ == "__main__":
    main()
