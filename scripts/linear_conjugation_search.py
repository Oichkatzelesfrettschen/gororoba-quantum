"""Surrogate cost of the N=21 order-finding multipliers conjugated by an uncontrolled linear map.

Round k of the ten-round order-finding circuit applies the controlled
multiplier C(f_k) to the five-bit work register. Replacing it by
B C(g_k) B^-1 with g_k = B^-1 f_k B, for one B in GL(5,2) shared by every
round, implements the same unitary. The operations between rounds act on the
control qubit alone, so each B^-1 B pair between rounds cancels. The first
B^-1 meets the work register in |1> and becomes the basis-state preparation
B^-1 |1>. The last B acts on the work register after its final use, and
order finding never measures that register. The surrogate cost of the
schedule is therefore sum_k s(g_k), with s the phase-controlled CX surrogate
of target_flip.target_flip_network. The baseline B = I gives 2,556.

target_flip_network minimizes over every bit ordering, so B and B P (P a
permutation matrix) cost the same. The search therefore runs over the 83,328
cosets B S_5, each named by the unordered set of its columns B e_i, in
lexicographic order of the sorted column tuple. 16 = 4^-1 mod 21, and the
synthesis minimizes over reversed inverse networks, so s(B^-1 f_16 B) =
s(B^-1 f_4 B). A sampled run computes both and requires equality, and
requires cost(B P) = cost(B) for a seeded P on every sampled coset; shards
compute s for multipliers 4 and 2 only.

Usage:
    "$PYTHON" scripts/linear_conjugation_search.py --sample N --seed S --out PATH
    "$PYTHON" scripts/linear_conjugation_search.py --start A --stop B --out PATH
    "$PYTHON" scripts/linear_conjugation_search.py --merge SHARD... --out PATH
    "$PYTHON" scripts/linear_conjugation_search.py --check PATH [--limit K]

--check recomputes the baseline coset, the retained winners, and the first K
retained cosets (default 40), and requires every retained field the record
derives from its costs to equal what this script derives.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import random
import sys
import time
from collections import Counter
from functools import lru_cache
from itertools import combinations
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
import parallel  # noqa: E402
from modular_arithmetic import modular_permutation  # noqa: E402
from target_flip import CONTROLLED_CX_COST, target_flip_network  # noqa: E402

SCHEMA = "linear-conjugation-search-v1"
MODULUS = 21
WIDTH = 5
SIZE = 1 << WIDTH
# The ten-round schedule of order_finding_plan(21, 2, 10) after its leading
# identity rounds; --check rebuilds it from order_finding.
ROUND_MULTIPLIERS = (4, 16, 4, 16, 4, 16, 4, 16, 4, 2)
SEARCHED_MULTIPLIERS = (4, 2)
COSETS = 83_328
BASELINE_COLUMNS = (1, 2, 4, 8, 16)
BASELINE_COST = 2556
WINNERS = 16
DEFAULT_CHECK_LIMIT = 40


def _require(ok: bool, message: str) -> None:
    if not ok:
        raise SystemExit(f"linear_conjugation_search: {message}")


def _rank(vectors: tuple[int, ...]) -> int:
    basis: list[int] = []
    for vector in vectors:
        for pivot in basis:
            vector = min(vector, vector ^ pivot)
        if vector:
            basis.append(vector)
    return len(basis)


@lru_cache(maxsize=1)
def coset_columns() -> tuple[tuple[int, ...], ...]:
    """Each coset B S_5 as the sorted tuple of its columns, in lexicographic order."""
    cosets = tuple(columns for columns in combinations(range(1, SIZE), WIDTH) if _rank(columns) == WIDTH)
    _require(len(cosets) == COSETS, f"{len(cosets)} independent column sets, expected {COSETS}")
    return cosets


def linear_table(columns: tuple[int, ...]) -> tuple[int, ...]:
    """x -> B x for the matrix whose column i is columns[i]."""
    table = []
    for value in range(SIZE):
        image = 0
        for bit, column in enumerate(columns):
            if value >> bit & 1:
                image ^= column
        table.append(image)
    return tuple(table)


def conjugate(table: tuple[int, ...], permutation: tuple[int, ...]) -> tuple[int, ...]:
    """B^-1 f B as a permutation of the register values."""
    inverse = [0] * SIZE
    for value, image in enumerate(table):
        inverse[image] = value
    return tuple(inverse[permutation[table[value]]] for value in range(SIZE))


def surrogate(permutation: tuple[int, ...]) -> int:
    return sum(CONTROLLED_CX_COST[cube.control_mask.bit_count()] for cube in target_flip_network(permutation))


@lru_cache(maxsize=1)
def _multiplier_tables() -> dict[int, tuple[int, ...]]:
    return {multiplier: modular_permutation(MODULUS, multiplier) for multiplier in (2, 4, 16)}


def costs(columns: tuple[int, ...], multipliers: tuple[int, ...] = SEARCHED_MULTIPLIERS) -> list[int]:
    table = linear_table(columns)
    return [surrogate(conjugate(table, _multiplier_tables()[multiplier])) for multiplier in multipliers]


def schedule_cost(s4: int, s2: int) -> int:
    per_multiplier = {4: s4, 16: s4, 2: s2}
    return sum(per_multiplier[multiplier] for multiplier in ROUND_MULTIPLIERS)


def shard_item(index: int) -> list[int]:
    return costs(coset_columns()[index])


def sample_item(item: tuple[int, tuple[int, ...]]) -> dict[str, Any]:
    """s for multipliers 4, 16, 2 on one coset, and s(B P), s(P B) for multiplier 4 under a seeded P."""
    index, order = item
    columns = coset_columns()[index]
    s4, s16, s2 = costs(columns, (4, 16, 2))
    right = tuple(columns[position] for position in order)
    table = linear_table(columns)
    left = tuple(sum(1 << order[bit] for bit in range(WIDTH) if table[1 << j] >> bit & 1) for j in range(WIDTH))
    return {
        "index": index,
        "s4": s4,
        "s16": s16,
        "s2": s2,
        "s4_right_permuted": costs(right, (4,))[0],
        "s4_left_permuted": costs(left, (4,))[0],
    }


def environment() -> dict[str, Any]:
    return {
        "python": platform.python_version(),
        "machine": platform.machine(),
        "processor": platform.processor() or platform.uname().machine,
        "cpus_available": parallel.available_cpus(),
        "workers": parallel.workers(),
        "kaggle": bool(os.environ.get("KAGGLE_KERNEL_RUN_TYPE")),
    }


def source_digests() -> dict[str, str]:
    paths = ("scripts/linear_conjugation_search.py", "gororoba_quantum/target_flip.py")
    return {path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest() for path in paths}


def run_sample(count: int, seed: int) -> dict[str, Any]:
    rng = random.Random(seed)
    indices = sorted(rng.sample(range(COSETS), count))
    items = [(index, tuple(rng.sample(range(WIDTH), WIDTH))) for index in indices]
    started = time.perf_counter()
    rows = parallel.ordered_map(sample_item, items, min_items=2)
    seconds = time.perf_counter() - started
    _require(all(row["s16"] == row["s4"] for row in rows), "s(16) differs from s(4) on a sampled coset")
    _require(all(row["s4_right_permuted"] == row["s4"] for row in rows), "cost(B P) differs from cost(B)")
    left_differs = sum(row["s4_left_permuted"] != row["s4"] for row in rows)
    costs_by_row = [schedule_cost(row["s4"], row["s2"]) for row in rows]
    return {
        "schema": SCHEMA,
        "mode": "sample",
        "seed": seed,
        "environment": environment(),
        "sources": source_digests(),
        "seconds": round(seconds, 3),
        "syntheses": 5 * count,
        "seconds_per_synthesis_cpu": round(seconds * parallel.workers() / (5 * count), 5),
        "checks": {
            "s16_equals_s4": count,
            "right_permutation_invariant": count,
            "left_permutation_differs": left_differs,
        },
        "schedule_cost_histogram": dict(sorted(Counter(costs_by_row).items())),
        "best": sorted(zip(costs_by_row, indices, strict=True))[:WINNERS],
        "rows": rows,
    }


def run_shard(start: int, stop: int) -> dict[str, Any]:
    _require(0 <= start < stop <= COSETS, f"shard [{start}, {stop}) outside [0, {COSETS})")
    started = time.perf_counter()
    pairs = parallel.ordered_map(shard_item, list(range(start, stop)), min_items=2)
    seconds = time.perf_counter() - started
    return {
        "schema": SCHEMA,
        "mode": "shard",
        "start": start,
        "stop": stop,
        "environment": environment(),
        "sources": source_digests(),
        "seconds": round(seconds, 3),
        "s4": [pair[0] for pair in pairs],
        "s2": [pair[1] for pair in pairs],
    }


def summarize(s4: list[int], s2: list[int]) -> dict[str, Any]:
    """Every field the merged record derives from the per-coset costs."""
    totals = [schedule_cost(a, b) for a, b in zip(s4, s2, strict=True)]
    baseline = coset_columns().index(BASELINE_COLUMNS)
    ranked = sorted(range(len(totals)), key=lambda index: (totals[index], index))
    best4 = min(s4)
    best2 = min(s2)
    return {
        "baseline_index": baseline,
        "baseline_cost": totals[baseline],
        "minimum_cost": totals[ranked[0]],
        "cosets_below_baseline": sum(total < totals[baseline] for total in totals),
        "schedule_cost_histogram": {str(key): value for key, value in sorted(Counter(totals).items())},
        "s4_histogram": {str(key): value for key, value in sorted(Counter(s4).items())},
        "s2_histogram": {str(key): value for key, value in sorted(Counter(s2).items())},
        "winners": [
            {
                "index": index,
                "columns": list(coset_columns()[index]),
                "s4": s4[index],
                "s2": s2[index],
                "cost": totals[index],
            }
            for index in ranked[:WINNERS]
        ],
        "minimum_s4": best4,
        "minimum_s4_cosets": [index for index, value in enumerate(s4) if value == best4][:WINNERS],
        "minimum_s2": best2,
        "minimum_s2_cosets": [index for index, value in enumerate(s2) if value == best2][:WINNERS],
    }


def merge(shards: list[dict[str, Any]]) -> dict[str, Any]:
    shards = sorted(shards, key=lambda shard: shard["start"])
    _require(all(shard["schema"] == SCHEMA and shard["mode"] == "shard" for shard in shards), "not shard records")
    _require(shards[0]["start"] == 0 and shards[-1]["stop"] == COSETS, "shards do not cover every coset")
    _require(
        all(left["stop"] == right["start"] for left, right in zip(shards, shards[1:], strict=False)),
        "shards leave a gap or overlap",
    )
    _require(
        len({json.dumps(shard["sources"], sort_keys=True) for shard in shards}) == 1, "shards ran different sources"
    )
    s4 = [value for shard in shards for value in shard["s4"]]
    s2 = [value for shard in shards for value in shard["s2"]]
    return {
        "schema": SCHEMA,
        "mode": "exhaustive",
        "modulus": MODULUS,
        "round_multipliers": list(ROUND_MULTIPLIERS),
        "weights": "/".join(str(cost) for cost in CONTROLLED_CX_COST),
        "cosets": COSETS,
        "coset_order": "sorted column tuples of GL(5,2), lexicographic",
        "sources": shards[0]["sources"],
        "shards": [{key: shard[key] for key in ("start", "stop", "seconds", "environment")} for shard in shards],
        "summary": summarize(s4, s2),
        "s4": s4,
        "s2": s2,
    }


def check(record: dict[str, Any], limit: int) -> str:
    from order_finding import order_finding_plan

    plan = order_finding_plan(MODULUS, 2, 10)
    schedule = tuple(resource.multiplier for resource in plan.rounds[plan.leading_identity_rounds :])
    _require(schedule == ROUND_MULTIPLIERS, f"order_finding schedule {schedule} differs from {ROUND_MULTIPLIERS}")
    _require(record.get("schema") == SCHEMA and record.get("mode") == "exhaustive", "not an exhaustive record")
    _require(len(record["s4"]) == len(record["s2"]) == COSETS, "the record does not hold every coset")
    _require(record["summary"] == summarize(record["s4"], record["s2"]), "the retained summary differs from the costs")
    _require(record["summary"]["baseline_cost"] == BASELINE_COST, "the baseline coset does not cost 2,556")
    indices = sorted(
        {record["summary"]["baseline_index"], *(winner["index"] for winner in record["summary"]["winners"])}
        | set(range(min(limit, COSETS)))
    )
    recomputed = parallel.ordered_map(shard_item, indices, min_items=2)
    differing = [
        index
        for index, pair in zip(indices, recomputed, strict=True)
        if pair != [record["s4"][index], record["s2"][index]]
    ]
    _require(not differing, f"recomputed costs differ at cosets {differing[:10]}")
    return f"{len(indices)} cosets recomputed; minimum {record['summary']['minimum_cost']} against baseline 2556"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--sample", type=int)
    mode.add_argument("--start", type=int)
    mode.add_argument("--merge", type=Path, nargs="+")
    mode.add_argument("--check", type=Path)
    parser.add_argument("--stop", type=int)
    parser.add_argument("--seed", type=int, default=20261016)
    parser.add_argument("--limit", type=int, default=DEFAULT_CHECK_LIMIT)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if args.check:
        print(f"linear_conjugation_search: {check(json.loads(args.check.read_text(encoding='utf-8')), args.limit)}")
        return 0
    _require(args.out is not None, "--out is required")
    if args.sample is not None:
        record = run_sample(args.sample, args.seed)
        print(json.dumps({key: record[key] for key in ("seconds", "seconds_per_synthesis_cpu", "checks", "best")}))
    elif args.merge:
        record = merge([json.loads(path.read_text(encoding="utf-8")) for path in args.merge])
        print(json.dumps({key: value for key, value in record["summary"].items() if "histogram" not in key}))
    else:
        _require(args.stop is not None, "--start needs --stop")
        record = run_shard(args.start, args.stop)
        print(json.dumps({"start": args.start, "stop": args.stop, "seconds": record["seconds"]}))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
