"""Exact action of the G_2 stabilizer of an orthonormal imaginary pair on the complement of its quaternion subalgebra.

The derivation algebra of the octonions is solved from D(xy) = D(x)y + xD(y) over Q on the cd_core basis. The
stabilizer of (e1, e2) fixes H = span(e0, e1, e2, e1 e2) and acts on H^perp = span(e4, ..., e7). A 4x4 skew block
splits into self-dual and anti-self-dual parts, which are the two su(2) factors of so(4); the stabilizer lies in one
factor exactly when one part has rank 3 and the other rank 0. The mutation adds an anti-self-dual generator to a
self-dual stabilizer, which the same rank test must reject.
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from fractions import Fraction
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

from cd_core import cd_multiply_exact  # noqa: E402

DIMENSION = 8
H_INDICES = [0, 1, 2, 3]
H_PERP_INDICES = [4, 5, 6, 7]
RESULT = HERE / "xi-real-type-result.json"


def _basis(index: int) -> list[Fraction]:
    return [Fraction(int(k == index)) for k in range(DIMENSION)]


def _product(i: int, j: int) -> sp.Matrix:
    return sp.Matrix(
        [sp.Rational(c.numerator, c.denominator) for c in cd_multiply_exact(DIMENSION, _basis(i), _basis(j))]
    )


def _derivation_space(fixed: list[int]) -> list[sp.Matrix]:
    table = [[_product(i, j) for j in range(DIMENSION)] for i in range(DIMENSION)]
    d = sp.Matrix(DIMENSION, DIMENSION, lambda r, c: sp.Symbol(f"d{r}_{c}"))
    equations = list(d[:, 0]) + list(d[0, :])
    for index in fixed:
        equations += list(d[:, index])
    for i, j in itertools.product(range(DIMENSION), repeat=2):
        rhs = sp.zeros(DIMENSION, 1)
        for k in range(DIMENSION):
            rhs += d[k, i] * table[k][j] + d[k, j] * table[i][k]
        equations += list(d * table[i][j] - rhs)
    matrix, _ = sp.linear_eq_to_matrix(equations, list(d))
    return [sp.Matrix(DIMENSION, DIMENSION, list(v)) for v in matrix.nullspace()]


def _duality_ranks(blocks: list[sp.Matrix]) -> tuple[int, int]:
    plus = [[b[0, 1] + b[2, 3], b[0, 2] - b[1, 3], b[0, 3] + b[1, 2]] for b in blocks]
    minus = [[b[0, 1] - b[2, 3], b[0, 2] + b[1, 3], b[0, 3] - b[1, 2]] for b in blocks]
    return sp.Matrix(plus).rank(), sp.Matrix(minus).rank()


def compute() -> dict[str, object]:
    derivations = _derivation_space([])
    stabilizer = _derivation_space([1, 2])
    pair_product = [int(c) for c in _product(1, 2)]
    h_block_zero = all(m.extract(H_INDICES, H_INDICES).is_zero_matrix for m in stabilizer)
    blocks = [m.extract(H_PERP_INDICES, H_PERP_INDICES) for m in stabilizer]
    plus_rank, minus_rank = _duality_ranks(blocks)
    anti_self_dual = sp.Matrix([[0, 1, 0, 0], [-1, 0, 0, 0], [0, 0, 0, -1], [0, 0, 1, 0]])
    mutated_ranks = _duality_ranks([*blocks, anti_self_dual])
    single_factor = sorted([plus_rank, minus_rank]) == [0, 3]
    mutation_rejected = sorted(mutated_ranks) != [0, 3]
    checks = {
        "derivation_dimension_is_14": len(derivations) == 14,
        "pair_product_is_e3": pair_product == [int(k == 3) for k in range(DIMENSION)],
        "stabilizer_dimension_is_3": len(stabilizer) == 3,
        "stabilizer_fixes_H": h_block_zero,
        "stabilizer_in_one_so4_factor": single_factor,
        "mutation_rejected": mutation_rejected,
    }
    return {
        "derivation_dimension": len(derivations),
        "stabilizer_dimension": len(stabilizer),
        "self_dual_rank": plus_rank,
        "anti_self_dual_rank": minus_rank,
        "mutated_ranks": list(mutated_ranks),
        "checks": checks,
        "pass": all(checks.values()),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="compare against the retained result")
    args = parser.parse_args()
    result = compute()
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.check:
        if RESULT.read_text() != text:
            raise SystemExit("xi_real_type: result differs from the retained record")
    else:
        RESULT.write_text(text)
    if not result["pass"]:
        raise SystemExit("xi_real_type: a check failed")
    print("xi_real_type: pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
