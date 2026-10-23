"""Exact test of whether the tangent bound T(x) of a rank-locus witness is itself inside D_(5,k).

At a witness x of A_5 with nullity k, U and V span the left and right null spaces of L_x
and T(x) = {y : U^T L_y V = 0} is the Zariski tangent space of D_(5,k) = {y : rank L_y <= 32 - k}
at x (rank_locus_local_dimension.tangent_bound). If the linear space T(x) lay inside D_(5,k), it
would be a piece of the tangent-bound dimension through x and would decide
a5-nonzero-divisor-two-dimension-gap there. The script computes U, V and a basis of T(x) over the
rationals with FLINT (exact_rank.rational_kernel) and evaluates the exact rank of L_y at seeded
integer combinations y of that basis.

Falsifier, stated before the run: one sample with rank L_y > 32 - k is an exact certificate that
T(x) is not inside D_(5,k), so the excess piece, if one exists, is curved. If T(x) is not inside
D_(5,k), some minor of size 33 - k is a nonzero polynomial of degree 33 - k in the weights, and
weights drawn uniformly from 101 integers make every sample miss it with probability at most
((33 - k) / 101)^6 by the Schwartz-Zippel lemma; rank 32 - k at every sample would therefore call
for an exact proof that T(x) lies inside D_(5,k).

Usage:
    "$PYTHON" scripts/rank_locus_tangent_linearity.py --out docs/evidence/rank_locus_tangent_linearity/result.json
    "$PYTHON" scripts/rank_locus_tangent_linearity.py --check docs/evidence/rank_locus_tangent_linearity/result.json
"""

from __future__ import annotations

import argparse
import json
import math
import random
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

import flint

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))
from exact_rank import rational_kernel  # noqa: E402
from rank_locus_local_dimension import witnesses  # noqa: E402

import parallel  # noqa: E402
from cd_core import cd_sign  # noqa: E402

SCHEMA = "rank-locus-tangent-linearity-v1"
DIM = 32
SEED = 20_261_023
SAMPLES = 6
COEFFICIENT_BOUND = 50

SIGNS = [[cd_sign(DIM, i, j) for j in range(DIM)] for i in range(DIM)]


def left(y: list[Fraction]) -> list[list[Fraction]]:
    """L_y with (k, j) entry the coefficient of e_k in y e_j."""
    return [[y[k ^ j] * SIGNS[k ^ j][j] for j in range(DIM)] for k in range(DIM)]


def integral(rows: list[list[Fraction]]) -> list[list[int]]:
    """Each row scaled by the least common multiple of its denominators, which keeps its null space."""
    out = []
    for row in rows:
        scale = math.lcm(*(value.denominator for value in row))
        out.append([int(value * scale) for value in row])
    return out


def fmpq(rows: list[list[Fraction]]) -> flint.fmpq_mat:
    return flint.fmpq_mat([[flint.fmpq(value.numerator, value.denominator) for value in row] for row in rows])


def transpose(rows: list[list[Fraction]]) -> list[list[Fraction]]:
    return [list(column) for column in zip(*rows, strict=True)]


def tangent_basis(x: list[Fraction]) -> tuple[int, list[list[Fraction]]]:
    lx = left(x)
    right = rational_kernel(integral(lx))
    left_null = rational_kernel(integral(transpose(lx)))
    u = fmpq(left_null)
    v = fmpq(transpose(right))
    rows: list[list[Fraction]] = [[] for _ in range(len(left_null) * len(right))]
    for m in range(DIM):
        block = u * fmpq(left([Fraction(int(i == m)) for i in range(DIM)])) * v
        for index, value in enumerate(block.entries()):
            rows[index].append(Fraction(int(value.p), int(value.q)))
    return len(right), rational_kernel(integral(rows))


def measure_witness(row: dict[str, Any]) -> dict[str, Any]:
    x = [Fraction(value) for value in row["x"]]
    nullity, basis = tangent_basis(x)
    if nullity != row["nullity"]:
        raise SystemExit(f"rank_locus_tangent_linearity: witness {row['witness']} has nullity {nullity}")
    rng = random.Random(SEED + row["witness"])
    ranks = []
    for _ in range(SAMPLES):
        weights = [rng.randint(-COEFFICIENT_BOUND, COEFFICIENT_BOUND) for _ in basis]
        y = [sum((w * vector[i] for w, vector in zip(weights, basis, strict=True)), Fraction(0)) for i in range(DIM)]
        ranks.append(fmpq(left(y)).rank())
    return {
        "witness": row["witness"],
        "family": row["family"],
        "nullity": nullity,
        "locus_rank": DIM - nullity,
        "tangent_dimension": len(basis),
        "sample_ranks": ranks,
        "tangent_inside_locus": max(ranks) <= DIM - nullity,
    }


def measure() -> dict[str, Any]:
    rows = parallel.ordered_map(measure_witness, witnesses(), min_items=2)
    return {
        "schema": SCHEMA,
        "seed": SEED,
        "samples": SAMPLES,
        "coefficient_bound": COEFFICIENT_BOUND,
        "rows": rows,
        "versions": {"python-flint": flint.__version__},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--out", type=Path)
    mode.add_argument("--check", type=Path)
    arguments = parser.parse_args()
    data = measure()
    if arguments.check is not None:
        retained = json.loads(arguments.check.read_text())
        differing = sorted(key for key in retained.keys() | data.keys() if retained.get(key) != data.get(key))
        if differing:
            raise SystemExit(f"rank_locus_tangent_linearity: {differing} differ from {arguments.check}")
    else:
        arguments.out.parent.mkdir(parents=True, exist_ok=True)
        arguments.out.write_text(json.dumps(data, indent=1, sort_keys=True) + "\n")
    for row in data["rows"]:
        print(
            f"witness {row['witness']:2d} {row['family']:20s} nullity {row['nullity']:2d} "
            f"dim T {row['tangent_dimension']:2d} ranks {row['sample_ranks']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
