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
degree-2 relations, and exits 1 when any differs from the stated value.
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


def truncated(degree: int, prime: int) -> dict[str, int]:
    """rank [W; P], rank W and their difference for I^degree modulo m^ORDER over F_prime (Q when prime is 0)."""
    ctx, gens = generators()
    x, y = ctx.gens()
    columns = {(a, b): i for i, (a, b) in enumerate((a, b) for a in range(ORDER) for b in range(ORDER - a))}

    def row(poly: Any) -> list[int]:
        out = [0] * len(columns)
        for exponent, coefficient in poly.to_dict().items():
            key = (int(exponent[0]), int(exponent[1]))
            if key in columns:
                out[columns[key]] = int(coefficient)
        return out

    products = []
    for combo in itertools.combinations_with_replacement(range(len(gens)), degree):
        value = ctx.from_dict({(0, 0): 1})
        for index in combo:
            value *= gens[index]
        products.append(value)
    multiples = [row(p * x**a * y**b) for p in products for a in range(ORDER) for b in range(ORDER - a) if a + b > 0]
    multiples = [r for r in multiples if any(r)]
    w = rank(multiples, prime)
    both = rank(multiples + [row(p) for p in products], prime)
    return {"products": len(products), "rank_W": w, "rank_W_and_products": both, "r": both - w}


def build() -> dict[str, Any]:
    ctx, (g1, g2, g3) = generators()
    x, y = ctx.gens()
    identity = (x + C) ** 3 * g1**2 * g2 - x**2 * y * g3**3
    fields = {"Q": 0, **{f"F_{p}": p for p in PRIMES}}
    table = {name: {str(d): truncated(d, prime) for d in (1, 2, 3)} for name, prime in fields.items()}
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
