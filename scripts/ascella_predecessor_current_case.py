"""Build the Ascella target-slot request against the current Quandela implementation."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import ascella_predecessor_case as original

CASE = original.ROOT / "results/quandela/cases/ascella_predecessor/current-schema"
JOB = "current-schema"
ANALYZER = "scripts/ascella_predecessor_current_analysis.py"
BUILDER = "scripts/ascella_predecessor_current_case.py"


def documents() -> dict[str, bytes]:
    payload = original.documents()
    manifest = json.loads(payload["cases.json"])
    manifest["job"] = JOB
    manifest["preregistered"]["current_case_sources"] = {
        name: hashlib.sha256((original.ROOT / name).read_bytes()).hexdigest() for name in (BUILDER, ANALYZER)
    }
    return {"cases.json": (json.dumps(manifest, indent=1) + "\n").encode(), "circuit.json": payload["circuit.json"]}


def check(directory: Path = CASE) -> dict:
    rebuilt = documents()
    for name, data in rebuilt.items():
        if (directory / name).read_bytes() != data:
            raise ValueError(f"{directory / name} differs from the current source-derived request")
    return json.loads(rebuilt["cases.json"])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--build", action="store_true")
    group.add_argument("--check", action="store_true")
    parser.add_argument("--out", type=Path, default=CASE, help="request directory for the current sources")
    args = parser.parse_args()
    if args.build:
        original.publish_case(args.out, documents())
    print(original.summary(check(args.out)), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
