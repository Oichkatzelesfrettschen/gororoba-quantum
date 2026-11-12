"""Truncated test of whether the E8-bar slice ideal I is closed under the quadratic algebra S = P + P b.

Modulo n^N the script compares the rank of I = sum g R, spanned by the generators times a basis of the slice ring R,
with the rank of I S, spanned by the generators times a monomial basis of S, and reports the rank of m_R I beside
them. Equal ranks at an order are necessary for I = I S; the exact statement is the Nakayama certificate of
`records/e8-ideal-closure-*.sing`.

    $PYTHON docs/evidence/a5-exceptional-fibers/monomial-ladder/e8_closure_probe.py ORDER [SLUG]
"""

from __future__ import annotations

import itertools
import json
import sys
import time

import e8_ladder as lad

PRIME = 32009


def probe(slug: str, order: int) -> dict[str, int | str | float]:
    ring = lad.Ring(PRIME, order)
    gens = lad.generators(slug, ring)
    full = []
    for e in itertools.product(range(order), repeat=5):
        if sum(e) < order:
            full.append((ring.ctx.from_dict({e: 1}), ring.zero))
        if sum(e) < order - 1:
            full.append((ring.zero, ring.ctx.from_dict({e: 1})))
    started = time.time()
    ranks = {
        name: lad.rank_and_basis(ring, lad.span(ring, gens, basis, order), order)[0]
        for name, basis in (
            ("rank_I", lad.ring_basis(ring, order, False)),
            ("rank_IS", full),
            ("rank_mR_I", lad.ring_basis(ring, order, True)),
        )
    }
    return {"slug": slug, "prime": PRIME, "order": order, **ranks, "seconds": round(time.time() - started, 1)}


if __name__ == "__main__":
    print(json.dumps(probe(sys.argv[2] if len(sys.argv) > 2 else "e8-nm", int(sys.argv[1]))))
