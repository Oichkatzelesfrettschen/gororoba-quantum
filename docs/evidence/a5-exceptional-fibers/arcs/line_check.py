"""The line t1 = t3 (all other t_i = 0) lies in V(J+G): J and G vanish at (c, 0, c, 0, ..., 0) for every c tried.

The check samples eight values of c and a control point off the line; it proves no polynomial identity.
"""

from __future__ import annotations

import json
import sys

import arclib as A
from arc_targets import TARGETS, Target

VALUES = [1, 2, 3, 5, 7, 11, 100, -4]
CONTROL = [3, 0, 2, 0, 0, 0, 0, 0, 0]


def evaluate(poly: A.Poly, x: list[int], p: int) -> int:
    tot = 0
    for ex, c in poly.items():
        t = c
        for xi, e in zip(x, ex, strict=True):
            if e:
                t = t * pow(xi, e, p) % p
        tot = (tot + t) % p
    return tot


def line_check(target: Target) -> dict[str, object]:
    p = target.prime
    j_gens, g_gens = A.load_slice(target)

    def failures(x: list[int]) -> list[int]:
        return [sum(1 for q in j_gens if evaluate(q, x, p)), sum(1 for q in g_gens if evaluate(q, x, p))]

    rows = [[c, *failures([c % p, 0, c % p, 0, 0, 0, 0, 0, 0])] for c in VALUES]
    return {
        "points": "c, nonvanishing J generators, nonvanishing G generators at (c,0,c,0,0,0,0,0,0)",
        "rows": rows,
        "control_off_line_(3,0,2,0,...)": failures(CONTROL),
    }


def main(argv: list[str]) -> int:
    target = TARGETS[argv[1]]
    res = line_check(target)
    (target.directory / "line_check.json").write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps(res))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
