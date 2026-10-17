"""Sign-block census of signed two-blade products at D = 16, 32 and 64 on cd_core.

For x = e_i + s e_j and y = e_k + t e_l (1 <= i < j < D, 1 <= k < l < D) the
four product terms land on the labels i^k, j^l, i^l and j^k. Either all four
differ, so ||x y||^2 = 4 and the normalized P = ||x y||^2 / 8 is 1/2 for
every sign, or i^j = k^l and the terms pair onto label_0 = i^k = j^l and
label_1 = i^l = j^k. On a two-label pair the product restricted to
span{e_k, e_l} is the sign block

    M = [[g(i,k), s g(j,l)], [s g(j,k), g(i,l)]],   g = cd_core.cd_sign(D, ., .),

with M (1, t) = (c0, c1) and P = (c0^2 + c1^2) / 8, the census convention of
scripts/box_kite_census.py. M has entries +-1, so |perm M| and |det M| are
one 0 and one 2: det M = 0 makes P in {0, 1} (an edge-type pair),
perm M = 0 makes P = 1/2 for both t (a strut-type pair).

The record keeps, per dimension: the two-label pair count by kind (same
plane, edge type, strut type), the ordered signed zero products, the
histogram of sign blocks and of (M, t), and the comparison of the zero
products with the nullity sum of results/hw_estimate/annihilator_strata.json
(a kernel spanned by two-blade partners makes the two equal). The photonic
coverage section requires every (M, t) of every dimension to be a
configuration of results/quandela/cases/box_kite_photonic_single and every
M a pair block of box_kite_photonic_pairs, so the 4-mode photonic circuits
realize every two-label two-blade product through D = 64 by relabeling.

The basis table is the specification: --write also builds the
hypercomplex-engine 0.5.0 standard table at each dimension and retains its
sha256 beside cd_core's; --check recomputes cd_core's tables and requires
both retained digests to equal them, so CI imports no package. Each label X
is an independent item mapped through parallel.ordered_map.

Usage: "$PYTHON" scripts/cd_two_blade_blocks.py (--write PATH | --check PATH | --self-test)
"""

from __future__ import annotations

import argparse
import copy
import functools
import hashlib
import json
import sys
from collections import Counter
from collections.abc import Callable
from fractions import Fraction
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
import parallel  # noqa: E402
from cd_core import cd_sign  # noqa: E402

SCHEMA = "cd-two-blade-blocks-v1"
RECORD = ROOT / "docs/evidence/box_kite_census/two_blade_blocks.json"
STRATA = ROOT / "results/hw_estimate/annihilator_strata.json"
CASES = ROOT / "results/quandela/cases"
DIMENSIONS = (16, 32, 64)
ENGINE = ("hypercomplex-engine", "0.5.0")
SIGNS = (1, -1)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


@functools.cache
def sign_table(dim: int) -> tuple[tuple[int, ...], ...]:
    return tuple(tuple(cd_sign(dim, p, q) for q in range(dim)) for p in range(dim))


def table_digest(signs: Any, dim: int) -> str:
    """sha256 of the ASCII rows 'p q sign index' for every basis pair, index = p XOR q."""
    lines = "".join(f"{p} {q} {int(signs[p][q])} {p ^ q}\n" for p in range(dim) for q in range(dim))
    return hashlib.sha256(lines.encode("ascii")).hexdigest()


def block_key(m: tuple[tuple[int, int], tuple[int, int]]) -> str:
    return f"{m[0][0]:+d}{m[0][1]:+d}{m[1][0]:+d}{m[1][1]:+d}"


def label_census(item: tuple[int, int]) -> dict[str, Any]:
    """Pool worker: every ordered signed pair of planes {i, i^X} x {k, k^X} for one label X."""
    dim, label = item
    g = sign_table(dim)
    planes = sorted({tuple(sorted((i, i ^ label))) for i in range(1, dim) if i ^ label not in (0, i)})
    kinds: Counter[str] = Counter()
    blocks: Counter[str] = Counter()
    configs: Counter[str] = Counter()
    probabilities: Counter[str] = Counter()
    zero = 0
    for i, j in planes:
        for k, el in planes:
            for s in SIGNS:
                m = ((g[i][k], s * g[j][el]), (s * g[j][k], g[i][el]))
                perm = m[0][0] * m[1][1] + m[0][1] * m[1][0]
                det = m[0][0] * m[1][1] - m[0][1] * m[1][0]
                require({abs(perm), abs(det)} == {0, 2}, f"D={dim}: block {m} breaks |perm|, |det| = 0, 2")
                if (i, j) == (k, el):
                    kind = "same_plane"
                else:
                    kind = "edge_type" if det == 0 else "strut_type"
                for t in SIGNS:
                    c0, c1 = m[0][0] + t * m[0][1], m[1][0] + t * m[1][1]
                    p = Fraction(c0 * c0 + c1 * c1, 8)
                    require((p == Fraction(1, 2)) == (perm == 0), f"D={dim}: P = {p} against perm {perm}")
                    kinds[kind] += 1
                    blocks[block_key(m)] += 1
                    configs[f"{block_key(m)} t{t:+d}"] += 1
                    probabilities[str(p)] += 1
                    zero += p == 0
    return {"kinds": kinds, "blocks": blocks, "configs": configs, "probabilities": probabilities, "zero": zero}


def nullity_sum(strata: dict[str, Any], dim: int) -> int:
    row = next(entry for entry in strata["dimensions"] if entry["dimension"] == dim)
    return sum(entry["nullity"] * entry["signed_element_count"] for entry in row["rank_nullity_histogram"])


def dimension_record(dim: int, strata: dict[str, Any]) -> dict[str, Any]:
    parts = parallel.ordered_map(label_census, [(dim, label) for label in range(1, dim)])
    total: dict[str, Counter[str]] = {key: Counter() for key in ("kinds", "blocks", "configs", "probabilities")}
    zero = 0
    for part in parts:
        for key in total:
            total[key].update(part[key])
        zero += part["zero"]
    two_blades = (dim - 1) * (dim - 2)
    two_label = sum(total["kinds"].values())
    nullities = nullity_sum(strata, dim)
    return {
        "dimension": dim,
        "signed_two_blades": two_blades,
        "ordered_signed_pairs": two_blades * two_blades,
        "two_label_pairs": dict(sorted(total["kinds"].items())),
        "four_label_pairs": two_blades * two_blades - two_label,
        "zero_products": zero,
        "annihilator_nullity_sum": nullities,
        "zero_products_equal_nullity_sum": zero == nullities,
        "p_histogram": dict(sorted(total["probabilities"].items())),
        "sign_blocks": dict(sorted(total["blocks"].items())),
        "configurations": dict(sorted(total["configs"].items())),
        "cd_core_table_sha256": table_digest(sign_table(dim), dim),
    }


def case_coverage(cases: Path = CASES) -> dict[str, list[str]]:
    """The (M, t) configurations of the single series and the M of the pairs series."""
    single, pairs = set(), set()
    for path in sorted((cases / "box_kite_photonic_single").glob("job-*/cases.json")):
        for block in json.loads(path.read_text(encoding="utf-8"))["blocks"]:
            if block["kind"] == "two_label":
                single.add(f"{block_key(tuple(map(tuple, block['m'])))} t{block['t']:+d}")  # type: ignore[arg-type]
    for path in sorted((cases / "box_kite_photonic_pairs").glob("job-*/cases.json")):
        for block in json.loads(path.read_text(encoding="utf-8"))["blocks"]:
            if block["kind"] == "pair":
                pairs.add(block_key(tuple(map(tuple, block["m"]))))  # type: ignore[arg-type]
    return {"single_configurations": sorted(single), "pair_blocks": sorted(pairs)}


def engine_digests() -> dict[str, str]:
    import hypercomplex_engine

    out = {}
    for dim in DIMENSIONS:
        signs, index = hypercomplex_engine.build_table("standard", dim.bit_length() - 1)
        for p in range(dim):
            for q in range(dim):
                require(int(index[p][q]) == p ^ q, f"{ENGINE[0]} D={dim}: index of ({p}, {q}) is not p XOR q")
        out[str(dim)] = table_digest(signs, dim)
    return out


def build(strata_path: Path = STRATA, cases: Path = CASES, engine: dict[str, str] | None = None) -> dict[str, Any]:
    strata = json.loads(strata_path.read_text(encoding="utf-8"))
    dimensions = [dimension_record(dim, strata) for dim in DIMENSIONS]
    coverage = case_coverage(cases)
    used_configs = sorted({key for row in dimensions for key in row["configurations"]})
    used_blocks = sorted({key for row in dimensions for key in row["sign_blocks"]})
    return {
        "schema": SCHEMA,
        "convention": "cd_core.cd_sign; x = e_i + s e_j, y = e_k + t e_l; "
        "M = [[g(i,k), s g(j,l)], [s g(j,k), g(i,l)]]; key '+a+b+c+d' lists M row-major",
        "strata": {"path": strata_path.relative_to(ROOT).as_posix()},
        "dimensions": dimensions,
        "oracle": {
            "package": ENGINE[0],
            "version": ENGINE[1],
            "table_sha256": engine,
        },
        "photonic_coverage": {
            **coverage,
            "configurations_used": used_configs,
            "blocks_used": used_blocks,
            "every_configuration_has_a_single_job": set(used_configs) <= set(coverage["single_configurations"]),
            "every_block_has_a_pair_job": set(used_blocks) <= set(coverage["pair_blocks"]),
        },
    }


def validate(record: dict[str, Any]) -> None:
    require(record.get("schema") == SCHEMA, "schema differs")
    for row in record["dimensions"]:
        dim = row["dimension"]
        engine = record["oracle"]["table_sha256"]
        require(
            isinstance(engine, dict) and engine.get(str(dim)) == row["cd_core_table_sha256"],
            f"D={dim}: the {ENGINE[0]} table digest differs from cd_core's",
        )
        require(
            sum(row["two_label_pairs"].values()) + row["four_label_pairs"] == row["ordered_signed_pairs"],
            f"D={dim}: pair classes do not partition the ordered pairs",
        )
        require(
            row["zero_products"] == int(row["p_histogram"].get("0", 0)),
            f"D={dim}: zero products differ from the P histogram",
        )
        require(
            row["zero_products"] == row["annihilator_nullity_sum"] and row["zero_products_equal_nullity_sum"],
            f"D={dim}: zero products differ from the annihilator nullity sum",
        )
    require(record["dimensions"][0]["zero_products"] == 336, "D=16 zero products differ from the 336-row corpus")
    coverage = record["photonic_coverage"]
    require(coverage["every_configuration_has_a_single_job"], "a two-label configuration has no single-series job")
    require(coverage["every_block_has_a_pair_job"], "a sign block has no pairs-series job")


def canonical(record: dict[str, Any]) -> str:
    return json.dumps(record, indent=1, sort_keys=True) + "\n"


def write(path: Path) -> None:
    record = build(engine=engine_digests())
    validate(record)
    path.write_text(canonical(record), encoding="utf-8")
    for row in record["dimensions"]:
        print(
            f"D={row['dimension']}: {row['zero_products']} zero products, nullity sum "
            f"{row['annihilator_nullity_sum']}, {len(row['sign_blocks'])} sign blocks, "
            f"{len(row['configurations'])} configurations"
        )


def check(path: Path) -> None:
    retained = json.loads(path.read_text(encoding="utf-8"))
    record = build(engine=retained.get("oracle", {}).get("table_sha256"))
    validate(record)
    require(canonical(record) == path.read_text(encoding="utf-8"), f"{path} differs from the recomputed census")
    print(f"two-blade blocks: {', '.join(str(r['zero_products']) for r in record['dimensions'])} zero products match")


def self_test() -> int:
    record = build(engine=json.loads(RECORD.read_text(encoding="utf-8"))["oracle"]["table_sha256"])
    validate(record)

    def oracle(r: dict[str, Any]) -> None:
        r["oracle"]["table_sha256"]["32"] = "0" * 64

    def partition(r: dict[str, Any]) -> None:
        r["dimensions"][1]["four_label_pairs"] += 1

    def zeros(r: dict[str, Any]) -> None:
        r["dimensions"][1]["zero_products"] -= 1

    def coverage(r: dict[str, Any]) -> None:
        r["photonic_coverage"]["every_block_has_a_pair_job"] = False

    def nullity(r: dict[str, Any]) -> None:
        r["dimensions"][2]["annihilator_nullity_sum"] += 4

    mutations: list[tuple[str, Callable[[dict[str, Any]], None]]] = [
        ("a nullity sum off the zero products", nullity),
        ("an oracle digest off cd_core", oracle),
        ("pair classes that miss a pair", partition),
        ("a zero count off the P histogram", zeros),
        ("a sign block without a pair job", coverage),
    ]
    for label, mutate in mutations:
        mutated = copy.deepcopy(record)
        mutate(mutated)
        try:
            validate(mutated)
        except ValueError as error:
            print(f"rejected {label}: {error}")
        else:
            raise SystemExit(f"self-test: validate accepted {label}")
    sign_table.cache_clear()
    flipped = [list(row) for row in sign_table(16)]
    flipped[1][4] = -flipped[1][4]
    require(table_digest(flipped, 16) != record["dimensions"][0]["cd_core_table_sha256"], "digest missed a sign")
    print("rejected a flipped basis sign: its digest differs from the retained D=16 table")
    print(f"self-test: {len(mutations) + 1} mutations rejected")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", type=Path)
    group.add_argument("--check", type=Path)
    group.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    if args.write:
        write(args.write)
    else:
        check(args.check)
    return 0


if __name__ == "__main__":
    sys.exit(main())
