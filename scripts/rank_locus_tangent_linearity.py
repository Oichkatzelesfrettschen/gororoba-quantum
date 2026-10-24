"""Exact test of whether the tangent bound T(x) of a rank-locus witness lies in the closed rank cone R_k.

At a witness x of A_5 with nullity k, U and V span the left and right null spaces of L_x and
T(x) = {y : U^T L_y V = 0} is the Zariski tangent space at x of the closed determinantal cone
R_k = {y : rank L_y <= 32 - k}, which contains the cone S_k over the unit stratum D_(5,k)
(rank_locus_local_dimension). A piece of D_(5,k) through x of dimension dim T(x) - 1 spans a cone
of dimension dim T(x) inside R_k whose tangent space at x lies in T(x); if that cone were linear it
would equal T(x), so T(x) would lie inside R_k. The script computes U, V and a basis of T(x) over
the rationals with FLINT through rank_locus_gap_directions.verified_kernel, which checks every basis
vector against its integer equations and pins each kernel size by a rank modulo a prime. It draws
seeded integer combinations y of that basis, records their weights, and evaluates the exact rank of
L_y at each.

Falsifier, stated before the run: one sample with rank L_y > 32 - k is an exact certificate that
T(x) is not inside R_k, so the cone over a piece of the tangent-bound dimension through x, if one
exists, is curved. If T(x) is not inside R_k, some minor of size 33 - k is a nonzero polynomial of
degree 33 - k in the weights, and weights drawn uniformly from 101 integers make every sample miss
it with probability at most ((33 - k) / 101)^6 by the Schwartz-Zippel lemma; samples that all keep
rank 32 - k refute nothing and leave inclusion for an exact proof.

Usage:
    "$PYTHON" scripts/rank_locus_tangent_linearity.py --out docs/evidence/rank_locus_tangent_linearity/result.json
    "$PYTHON" scripts/rank_locus_tangent_linearity.py --check docs/evidence/rank_locus_tangent_linearity/result.json
    "$PYTHON" scripts/rank_locus_tangent_linearity.py --self-test
"""

from __future__ import annotations

import argparse
import copy
import json
import random
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

import flint

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))
from rank_locus_gap_directions import verified_kernel  # noqa: E402
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


def fmpq(rows: list[list[Fraction]]) -> flint.fmpq_mat:
    return flint.fmpq_mat([[flint.fmpq(value.numerator, value.denominator) for value in row] for row in rows])


def transpose(rows: list[list[Fraction]]) -> list[list[Fraction]]:
    return [list(column) for column in zip(*rows, strict=True)]


def tangent_basis(x: list[Fraction]) -> tuple[int, list[list[Fraction]]]:
    lx = left(x)
    right = verified_kernel(lx, DIM)
    left_null = verified_kernel(transpose(lx), DIM)
    u = fmpq(left_null)
    v = fmpq(transpose(right))
    rows: list[list[Fraction]] = [[] for _ in range(len(left_null) * len(right))]
    for m in range(DIM):
        block = u * fmpq(left([Fraction(int(i == m)) for i in range(DIM)])) * v
        for index, value in enumerate(block.entries()):
            rows[index].append(Fraction(int(value.p), int(value.q)))
    return len(right), verified_kernel(rows, DIM)


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


def verdicts(record: dict[str, Any], fresh: dict[str, Any]) -> list[str]:
    """Fields that differ from the fresh measurement, and rows whose own fields disagree with each other."""
    found = [key for key in sorted(record.keys() | fresh.keys()) if key != "rows" and record.get(key) != fresh.get(key)]
    rows = record.get("rows", [])
    if len(rows) != len(fresh["rows"]):
        return [*found, "rows"]
    for row, expected in zip(rows, fresh["rows"], strict=True):
        label = f"witness {expected['witness']}"
        found += [f"{label} {key}" for key in sorted(row.keys() | expected.keys()) if row.get(key) != expected.get(key)]
        ranks, weights = row.get("sample_ranks", []), row.get("sample_weights", [])
        if row.get("cone_rank_bound") != DIM - row.get("nullity", -1):
            found.append(f"{label} cone bound is not 32 minus the nullity")
        if len(ranks) != SAMPLES or len(weights) != SAMPLES:
            found.append(f"{label} sample count")
        elif row.get("sample_refutes_tangent_inside_cone") != (max(ranks) > row.get("cone_rank_bound", DIM)):
            found.append(f"{label} refutation flag disagrees with its ranks")
        if any(len(w) != row.get("tangent_dimension") or max(map(abs, w)) > COEFFICIENT_BOUND for w in weights):
            found.append(f"{label} weight vector outside the tangent dimension or coefficient bound")
    return found


def self_test() -> str:
    """Corrupted ranks, flags, weights, nullities, tangent dimensions and sample counts are each rejected."""
    record = measure()
    if verdicts(record, record):
        raise SystemExit(f"rank_locus_tangent_linearity: the honest record fails: {verdicts(record, record)}")
    mutations = {
        "rank 20 at a nullity-8 witness": lambda r: r["rows"][3]["sample_ranks"].__setitem__(0, 20),
        "refutation flag false": lambda r: r["rows"][5].__setitem__("sample_refutes_tangent_inside_cone", False),
        "weight changed": lambda r: r["rows"][0]["sample_weights"][2].__setitem__(1, COEFFICIENT_BOUND + 1),
        "nullity shifted by 4": lambda r: r["rows"][4].__setitem__("nullity", r["rows"][4]["nullity"] - 4),
        "tangent dimension shifted by 1": lambda r: r["rows"][4].__setitem__(
            "tangent_dimension", r["rows"][4]["tangent_dimension"] - 1
        ),
        "sample dropped": lambda r: r["rows"][6]["sample_ranks"].pop(),
        "witness dropped": lambda r: r["rows"].pop(),
        "schema changed": lambda r: r.__setitem__("schema", "rank-locus-tangent-linearity-v1"),
    }
    for label, change in mutations.items():
        bad = copy.deepcopy(record)
        change(bad)
        if not verdicts(bad, record):
            raise SystemExit(f"rank_locus_tangent_linearity: the {label} mutation passes")
    return f"{len(mutations)} corruptions rejected"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--out", type=Path)
    mode.add_argument("--check", type=Path)
    mode.add_argument("--self-test", action="store_true")
    arguments = parser.parse_args()
    if arguments.self_test:
        print(f"rank_locus_tangent_linearity self-test: {self_test()}")
        return 0
    data = measure()
    if arguments.check is not None:
        differing = verdicts(json.loads(arguments.check.read_text()), data)
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
