"""A counterexample to the lower-bound step of the modular-to-characteristic-0 transfer of fiber Hilbert functions.

    $PYTHON docs/evidence/a5-char0-transfer/transfer_counterexample.py [--out transfer-counterexample.json]

In k[x, y] localized at m = (x, y), with c = 32009 * 32029 and J = 0, take

    I = (g1, g2, g3) = (x^7, y^7, x^4 y^2 (c + x)).

The truncated rank of degree d at order N is r_N(d) = rank [W; P] - rank W, with P the products of d generators and
W the monomial multiples of positive degree of those products (the image of m I^d), both modulo m^N. It is computed
here over Q and over F_p for both primes by exact elimination (python-flint).

The transfer step under test reads: when the ambient quotient k[t]/(J + m^N) has good reduction at p, classes of
I^d / m I^d independent modulo p are independent in characteristic 0, so h_d over Q is at least r_N(d) modulo p. Here
J + m^N = m^N is a monomial ideal, whose reduction is as good as a reduction can be, the degree-2 relation space is 0
over Q and modulo both primes, and still r_22(3) is 10 modulo each prime and 9 over Q: the identity

    (c + x)^3 g1^2 g2 = x^2 y g3^3

puts c^3 g1^2 g2 into m I^3 over Z, so the class of g1^2 g2 dies wherever c is a unit and survives modulo a prime
that divides c. At order 22 the rank of W is 23 over Q and 0 modulo each prime, and a difference of two ranks is
not semicontinuous.

The script asserts the identity, the truncated ranks through degree 3 (3, 6, 9 over Q; 3, 6, 10 modulo each prime;
these are the fiber Hilbert functions, by the count of minimal monomial generators) and the vanishing of the
degree-2 relations, and exits 1 when any differs from the stated value. The independent products of generators, the
monomial multiples of each product and the nine (field, degree) cells run through parallel.ordered_map; a task is a
module-level function over plain integers, and the record is the one a serial loop writes.
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path
from typing import Any

from flint import fmpq, fmpq_mat, fmpz_mpoly_ctx, nmod_mat

PRIMES = (32009, 32029)
C = PRIMES[0] * PRIMES[1]
ORDER = 22
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "gororoba_quantum"))

import parallel  # noqa: E402

Terms = dict[tuple[int, int], int]


def generators() -> tuple[Any, list[Any]]:
    ctx = fmpz_mpoly_ctx.get(("x", "y"), "degrevlex")
    x, y = ctx.gens()
    return ctx, [x**7, y**7, x**4 * y**2 * (x + C)]


def rank(rows: list[list[int]], prime: int) -> int:
    if not rows:
        return 0
    if prime:
        return int(nmod_mat([[v % prime for v in row] for row in rows], prime).rank())
    return int(fmpq_mat([[fmpq(v) for v in row] for row in rows]).rank())


def product_terms(combo: tuple[int, ...]) -> Terms:
    """The product of the generators named by combo, as plain {(a, b): coefficient} terms."""
    ctx, gens = generators()
    value = ctx.from_dict({(0, 0): 1})
    for index in combo:
        value *= gens[index]
    return {(int(e[0]), int(e[1])): int(c) for e, c in value.to_dict().items()}


def columns() -> dict[tuple[int, int], int]:
    """Column of each monomial x^a y^b of degree below ORDER."""
    return {(a, b): i for i, (a, b) in enumerate((a, b) for a in range(ORDER) for b in range(ORDER - a))}


def row_of(terms: Terms, table: dict[tuple[int, int], int]) -> list[int]:
    out = [0] * len(table)
    for key, coefficient in terms.items():
        if key in table:
            out[table[key]] = coefficient
    return out


def multiple_rows(terms: Terms) -> list[list[int]]:
    """The nonzero rows of x^a y^b * product for every monomial of positive degree below ORDER."""
    table = columns()
    rows = []
    for a in range(ORDER):
        for b in range(ORDER - a):
            if a + b > 0:
                shifted = {(i + a, j + b): c for (i, j), c in terms.items()}
                if any(key in table for key in shifted):
                    rows.append(row_of(shifted, table))
    return [r for r in rows if any(r)]


def truncated(degree: int, prime: int) -> dict[str, int]:
    """rank [W; P], rank W and their difference for I^degree modulo m^ORDER over F_prime (Q when prime is 0)."""
    combos = list(itertools.combinations_with_replacement(range(3), degree))
    products = parallel.ordered_map(product_terms, combos, min_items=2)
    table = columns()
    multiples = [r for part in parallel.ordered_map(multiple_rows, products, min_items=2) for r in part]
    w = rank(multiples, prime)
    both = rank(multiples + [row_of(p, table) for p in products], prime)
    return {"products": len(products), "rank_W": w, "rank_W_and_products": both, "r": both - w}


def cell(job: tuple[int, int]) -> dict[str, int]:
    """One (degree, prime) cell of the truncated-rank table."""
    return truncated(*job)


def build() -> dict[str, Any]:
    ctx, (g1, g2, g3) = generators()
    x, y = ctx.gens()
    identity = (x + C) ** 3 * g1**2 * g2 - x**2 * y * g3**3
    fields = {"Q": 0, **{f"F_{p}": p for p in PRIMES}}
    jobs = [(d, prime) for prime in fields.values() for d in (1, 2, 3)]
    results = iter(parallel.ordered_map(cell, jobs, min_items=2))
    table = {name: {str(d): next(results) for d in (1, 2, 3)} for name in fields}
    expected = {"Q": [3, 6, 9], **{f"F_{p}": [3, 6, 10] for p in PRIMES}}
    hilbert = {name: [table[name][str(d)]["r"] for d in (1, 2, 3)] for name in fields}
    relations = {name: 6 - table[name]["2"]["r"] for name in fields}
    return {
        "schema": "a5-char0-transfer-counterexample-v1",
        "ideal": ["x^7", "y^7", f"x^4*y^2*({C} + x)"],
        "c": C,
        "order": ORDER,
        "identity_holds": identity == 0,
        "truncated": table,
        "truncated_rank_degrees_1_to_3": hilbert,
        "degree_2_relations": relations,
        "rank_W_degree_3_drop_modulo_p": {
            f"F_{p}": table["Q"]["3"]["rank_W"] - table[f"F_{p}"]["3"]["rank_W"] for p in PRIMES
        },
        "verdict": "counterexample"
        if identity == 0 and hilbert == expected and all(v == 0 for v in relations.values())
        else "not reproduced",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=HERE / "transfer-counterexample.json")
    arguments = parser.parse_args()
    record = build()
    arguments.out.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=1))
    return 0 if record["verdict"] == "counterexample" else 1


if __name__ == "__main__":
    sys.exit(main())
