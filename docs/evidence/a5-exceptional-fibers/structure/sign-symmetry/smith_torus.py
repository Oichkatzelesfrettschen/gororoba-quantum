"""Smith invariants of the exponent-difference lattice of every displayed J and G polynomial, for each header.

A diagonal scaling t_i -> a_i t_i makes every displayed polynomial an eigenvector exactly when the character a
vanishes on the lattice spanned by exponent differences within each polynomial. The group of such scalings over an
algebraic closure of odd characteristic is the dual of Z^n / lattice; full rank with invariant factors 1, ..., 1, 2, 2
gives the order-four group. Usage: smith_torus.py HEADER...; prints one JSON line per header.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import flint


def field(pattern: str, text: str) -> str:
    m = re.search(pattern, text)
    if m is None:
        raise ValueError(f"header lacks {pattern}")
    return m.group(1)


def exponents(text: str, names: list[str]) -> list[list[int]]:
    out = []
    for _sign, body in re.findall(r"([+-]?)([^+-]+)", text.replace(" ", "").replace("\n", "")):
        exps = [0] * len(names)
        for f in body.split("*"):
            if not re.fullmatch(r"\d+", f):
                v, _, e = f.partition("^")
                exps[names.index(v)] += int(e) if e else 1
        out.append(exps)
    return out


def main() -> None:
    for path in sys.argv[1:]:
        t = Path(path).read_text()
        names = field(r"ring r=\d+,\(([^)]*)\)", t).split(",")
        rows = []
        for ideal in ("J", "G"):
            for poly in field(rf"ideal {ideal}=([^;]*);", t).split(","):
                e = exponents(poly, names)
                rows += [[a - b for a, b in zip(x, e[0], strict=True)] for x in e[1:]]
        snf = flint.fmpz_mat(rows).snf()
        diag = [int(snf[i, i]) for i in range(min(snf.nrows(), snf.ncols()))]
        nonzero = [d for d in diag if d]
        order = 1
        for d in nonzero:
            order *= d
        print(
            json.dumps(
                {
                    "header": path,
                    "vars": len(names),
                    "lattice_rank": len(nonzero),
                    "invariant_factors": nonzero,
                    "torus_order": order if len(nonzero) == len(names) else "infinite",
                }
            )
        )


if __name__ == "__main__":
    main()
