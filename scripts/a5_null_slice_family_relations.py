"""Direct so(m,1) relation checks of the first null-slice family at one level of the Cayley-Dickson tower.

The record a5-null-slice-associator-envelope checks the relations [[K_a, K_b], K_c] = delta_bc K_a - delta_ac K_b of the
slice with time index 7 * 2^(n-3) and space [1, 2^(n-2)) without 2^(n-3) directly up to n = 9 and through disjoint
stars above. This record runs the same check (that record's triple_item, imported) directly at one level, one pool
task per pair a < b, so the relations at that level rest on an exhaustive check as well as on the star criterion.
No random draw enters.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from itertools import combinations
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

from a5_null_slice_associator_envelope import triple_item  # noqa: E402

import parallel  # noqa: E402

SOURCE_FILES = (
    "gororoba_quantum/parallel.py",
    "scripts/a5_null_slice_associator_envelope.py",
    "scripts/a5_null_slice_family_relations.py",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def family(level: int) -> tuple[int, tuple[int, ...]]:
    h = 1 << (level - 3)
    return 7 * h, tuple(i for i in range(1, 2 * h) if i != h)


def compute(level: int, space: tuple[int, ...] | None = None) -> dict[str, Any]:
    tau, default_space = family(level)
    chosen = default_space if space is None else space
    tasks = [(1 << level, tau, chosen, a, b) for a, b in combinations(chosen, 2)]
    failures = parallel.ordered_map(triple_item, tasks, min_items=1)
    return {
        "schema": "a5-null-slice-family-relations/1",
        "sources": {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in SOURCE_FILES},
        "level": level,
        "dimension": 1 << level,
        "time": tau,
        "space_size": len(chosen),
        "pairs": len(tasks),
        "relations": len(tasks) * len(chosen),
        "failures": sum(failures),
    }


def validate(result: dict[str, Any]) -> None:
    m = (1 << (result["level"] - 2)) - 2
    require(result["space_size"] == m, f"space size {result['space_size']}")
    require(result["relations"] == m * m * (m - 1) // 2, f"relations {result['relations']}")
    require(result["failures"] == 0, f"failures {result['failures']}")


def self_test() -> None:
    tau, space = family(6)
    good = compute(6)["failures"]
    moved = tuple(sorted({*space[:-1], 1 << 3}))
    bad = compute(6, moved)["failures"]
    require(good == 0 and bad > 0, f"control space: baseline {good}, mutant {bad}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--level", type=int, default=10)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--out", type=Path)
    mode.add_argument("--check", type=Path)
    mode.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        print("self-test: 1 paired control passes")
        return 0
    result = compute(args.level)
    validate(result)
    text = json.dumps(result, indent=1, sort_keys=True) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
        print(f"wrote {args.out}")
        return 0
    if args.check.read_text(encoding="utf-8") != text:
        print("record differs from its recomputation", file=sys.stderr)
        return 1
    print("record matches its recomputation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
