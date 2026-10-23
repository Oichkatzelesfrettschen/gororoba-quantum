"""Exact test of whether the tangent bound T(x) of a rank-locus witness lies in the closed rank cone R_k.

At a witness x of A_5 with nullity k, U and V span the left and right null spaces of L_x and
T(x) = {y : U^T L_y V = 0} is the Zariski tangent space at x of the closed determinantal cone
R_k = {y : rank L_y <= 32 - k}, which contains the cone S_k over the unit stratum D_(5,k)
(rank_locus_local_dimension). A piece of D_(5,k) through x of dimension dim T(x) - 1 spans a cone
of dimension dim T(x) inside R_k whose tangent space at x lies in T(x); if that cone were linear it
would equal T(x), so T(x) would lie inside R_k. The script computes U, V and a basis of T(x) over
the rationals with FLINT (exact_rank.rational_kernel), draws seeded integer combinations y of that
basis, records their weights, and evaluates the exact rank of L_y at each.

Falsifier, stated before the run: one sample with rank L_y > 32 - k is an exact certificate that
T(x) is not inside R_k, so the cone over a piece of the tangent-bound dimension through x, if one
exists, is curved. If T(x) is not inside R_k, some minor of size 33 - k is a nonzero polynomial of
degree 33 - k in the weights, and weights drawn uniformly from 101 integers make every sample miss
it with probability at most ((33 - k) / 101)^6 by the Schwartz-Zippel lemma; samples that all keep
rank 32 - k refute nothing and leave inclusion for an exact proof.

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

SCHEMA = "rank-locus-tangent-linearity-v2"
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


def witness_basis(row: dict[str, Any]) -> tuple[int, list[list[Fraction]]]:
    nullity, basis = tangent_basis([Fraction(value) for value in row["x"]])
    if nullity != row["nullity"]:
        raise SystemExit(f"rank_locus_tangent_linearity: witness {row['witness']} has nullity {nullity}")
    return nullity, basis


def sample_rank(item: tuple[list[list[Fraction]], list[int]]) -> int:
    basis, weights = item
    y = [sum((w * vector[i] for w, vector in zip(weights, basis, strict=True)), Fraction(0)) for i in range(DIM)]
    return int(fmpq(left(y)).rank())


def measure() -> dict[str, Any]:
    rows = witnesses()
    bases = parallel.ordered_map(witness_basis, rows, min_items=2)
    weights = []
    for row, (_, basis) in zip(rows, bases, strict=True):
        rng = random.Random(SEED + row["witness"])
        weights.append([[rng.randint(-COEFFICIENT_BOUND, COEFFICIENT_BOUND) for _ in basis] for _ in range(SAMPLES)])
    items = [(basis, sample) for (_, basis), drawn in zip(bases, weights, strict=True) for sample in drawn]
    ranks = parallel.ordered_map(sample_rank, items, min_items=2)
    out = []
    for index, (row, (nullity, basis), drawn) in enumerate(zip(rows, bases, weights, strict=True)):
        sample_ranks = ranks[index * SAMPLES : (index + 1) * SAMPLES]
        out.append(
            {
                "witness": row["witness"],
                "family": row["family"],
                "nullity": nullity,
                "cone_rank_bound": DIM - nullity,
                "tangent_dimension": len(basis),
                "sample_weights": drawn,
                "sample_ranks": sample_ranks,
                "sample_refutes_tangent_inside_cone": max(sample_ranks) > DIM - nullity,
            }
        )
    return {
        "schema": SCHEMA,
        "seed": SEED,
        "samples": SAMPLES,
        "coefficient_bound": COEFFICIENT_BOUND,
        "rows": out,
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
