"""Test whether the truncated ideal of the same-sign X slice is a span of monomials of k[[a, rho, sig, w]].

For I = sum g R and for m_R I, with g the header's generators on the parametrization of x_same_ladder.py and R the
slice ring, the script reduces a spanning set modulo n^N to reduced row echelon form. A subspace is a span of
monomials exactly when every row of that form has one nonzero entry, so the record holds the rank and the number of
single-monomial rows of each space; the two agree when the truncated space is a monomial span.

    $PYTHON docs/evidence/a5-exceptional-fibers/monomial-ladder/monomial_probe.py --slug xm-nm --prime 32009 \
        --order 12 --out monomial-probe-xm-nm-p32009-n12.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import x_same_ladder as ladder
from flint import nmod_mat


def single_rows(polys: list[Any], order: int, prime: int) -> tuple[int, int]:
    """Rank of the span of polys modulo n^order and the number of single-monomial rows of its echelon form."""
    index: dict[tuple[int, ...], int] = {}
    rows = []
    for poly in polys:
        row = {
            index.setdefault(tuple(int(v) for v in e), len(index)): int(c)
            for e, c in poly.to_dict().items()
            if sum(e) < order
        }
        if row:
            rows.append(row)
    matrix = nmod_mat(len(rows), len(index), prime)
    for i, row in enumerate(rows):
        for j, value in row.items():
            matrix[i, j] = value
    reduced, rank = matrix.rref()
    single = sum(sum(1 for j in range(len(index)) if int(reduced[i, j])) == 1 for i in range(rank))
    return int(rank), single


def probe(slug: str, prime: int, order: int) -> dict[str, Any]:
    gens = ladder.generators(slug, prime, order)
    ctx = gens[0].context()
    spaces = {}
    for name, maximal in (("I", False), ("m_R I", True)):
        polys = [ladder.truncate(ctx, g * b, order) for g in gens for b in ladder.ring_basis(ctx, order, maximal)]
        rank, single = single_rows(polys, order, prime)
        spaces[name] = {"rank": rank, "single_monomial_rows": single}
    monomial = all(s["rank"] == s["single_monomial_rows"] for s in spaces.values())
    return {
        "schema": "a5-monomial-probe-v1",
        "slug": slug,
        "prime": prime,
        "order": order,
        "spaces": spaces,
        "verdict": "monomial_span" if monomial else "not_a_monomial_span",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--slug", choices=("xm-nm", "xp-np"), default="xm-nm")
    parser.add_argument("--prime", type=int, default=32009)
    parser.add_argument("--order", type=int, required=True)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    record = probe(args.slug, args.prime, args.order)
    if args.out:
        args.out.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(record))


if __name__ == "__main__":
    main()
