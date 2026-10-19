"""Merge shard timing records into ci/gate_timings.json, the measured cost ci/run_gates.py plans shards by.

Each input is a ``gororoba-gate-timings-v1`` file that ``run_gates.py
--timings`` writes. A gate's entry keeps its wall seconds, user plus system
CPU seconds and allocated workers from the last input that measured it;
skipped gates carry no measurement and leave an earlier entry in place.
``--check FILE`` verifies that FILE parses and names only gates the manifest
lists after case expansion, so a removed or renamed gate fails until its
timing goes with it.

Usage: "$PYTHON" ci/merge_gate_timings.py OUT [--base FILE] TIMINGS...
       "$PYTHON" ci/merge_gate_timings.py --check ci/gate_timings.json
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import gate_inputs

ROOT = Path(__file__).resolve().parent.parent
SCHEMA = "gororoba-gate-measured-v1"
SOURCE_SCHEMA = "gororoba-gate-timings-v1"


def manifest_names(root: Path = ROOT) -> set[str]:
    gates = json.loads((root / "ci" / "gates.json").read_text())["gates"]
    return {gate["name"] for gate in gate_inputs.expand_cases(root, gates)}


def entry(row: dict[str, Any]) -> dict[str, Any] | None:
    resources = row.get("resources")
    if not isinstance(resources, dict) or row.get("status") != 0:
        return None
    wall = float(row["seconds"])
    cpu = float(resources["user_seconds"]) + float(resources["system_seconds"])
    return {"wall_seconds": round(wall, 2), "cpu_seconds": round(cpu, 2), "workers": int(resources["workers"])}


def merge(base: dict[str, Any], sources: list[Path]) -> dict[str, Any]:
    gates = dict(base.get("gates", {}))
    for source in sources:
        document = json.loads(source.read_text())
        if document.get("schema") != SOURCE_SCHEMA:
            raise SystemExit(f"{source}: not a {SOURCE_SCHEMA} record")
        for row in document["gates"]:
            measured = entry(row)
            if measured is not None:
                gates[row["name"]] = measured
    return {"schema": SCHEMA, "gates": dict(sorted(gates.items()))}


def check(path: Path, root: Path = ROOT) -> dict[str, Any]:
    document = json.loads(path.read_text())
    if (
        not isinstance(document, dict)
        or document.get("schema") != SCHEMA
        or not isinstance(document.get("gates"), dict)
    ):
        raise SystemExit(f"{path}: not a {SCHEMA} file")
    unknown = sorted(set(document["gates"]) - manifest_names(root))
    if unknown:
        raise SystemExit(f"{path}: names gates absent from ci/gates.json: {', '.join(unknown)}")
    for name, measured in document["gates"].items():
        valid = (
            isinstance(measured, dict)
            and set(measured) == {"wall_seconds", "cpu_seconds", "workers"}
            and all(
                isinstance(measured[field], (int, float)) and math.isfinite(measured[field]) and measured[field] >= 0
                for field in ("wall_seconds", "cpu_seconds")
            )
            and isinstance(measured["workers"], int)
            and measured["workers"] >= 1
        )
        if not valid:
            raise SystemExit(f"{path}: {name} needs finite wall_seconds, cpu_seconds and positive workers")
    return document


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("out", nargs="?", type=Path)
    parser.add_argument("timings", nargs="*", type=Path)
    parser.add_argument("--base", type=Path, help="earlier measured file whose entries persist unless remeasured")
    parser.add_argument("--check", type=Path)
    arguments = parser.parse_args(argv)
    if arguments.check is not None:
        document = check(arguments.check)
        print(f"gate-timings: {len(document['gates'])} measured gates, all in ci/gates.json")
        return 0
    if arguments.out is None or not arguments.timings:
        parser.error("give OUT and at least one timing record, or --check FILE")
    base = json.loads(arguments.base.read_text()) if arguments.base is not None else {}
    merged = merge(base, arguments.timings)
    names = manifest_names()
    merged["gates"] = {name: value for name, value in merged["gates"].items() if name in names}
    arguments.out.write_text(json.dumps(merged, indent=1) + "\n")
    print(f"gate-timings: {len(merged['gates'])} measured gates written to {arguments.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
