"""Offline Tuna-17 conditional-Ramsey proposal with a laddered interbatch pause budget.

Plan schema `qi-zz-map-plan-v2` states the account-wide pause between hardware batches as the interval
[floor, ceiling] of qi_platform.HARDWARE_PAUSE_LADDER (30/60/90/120 s): `minimum_interbatch_pause_seconds`
is (batches - 1) times the ladder's first step, the least spacing a series can use, and
`ceiling_interbatch_pause_seconds` is (batches - 1) times its last step, the budget every escalation finishes
inside. The 139-batch series therefore spans 4140 s to 16560 s of pauses.

Schema `qi-zz-map-plan-v1`, written by qi_zz_map.py for every retained case set, binds the ceiling alone as its
minimum. The retained sets embed the SHA-256 of qi_zz_map.py, so the builder stays byte-fixed and this module
derives the v2 files from its output: the circuits, scientific settings and batching are those of v1, and
only the plan schema, the pause fields, the builder digest list and the case hashes that bind them change.
This module performs no network access and has no submit command.

Usage: "$PYTHON" scripts/qi_zz_map_floor.py (--write DIR | --check DIR | --self-test)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import qi_zz_map as v1  # noqa: E402
from qi_platform import HARDWARE_PAUSE_LADDER  # noqa: E402

PLAN_SCHEMA = "qi-zz-map-plan-v2"
FLOOR_PAUSE_SECONDS = HARDWARE_PAUSE_LADDER[0]
CEILING_PAUSE_SECONDS = HARDWARE_PAUSE_LADDER[-1]
PAUSE_SCOPE = (
    "account-wide hardware spacing only; excludes the initial wait, execution, collection, "
    "queueing, calibration and other sessions' jobs"
)


def build(catalogue_path: Path = v1.CATALOGUE, shots: int | None = None) -> dict[str, str]:
    files = v1.build(catalogue_path, shots)
    plan = json.loads(files["plan.json"])
    v1.require(plan["schema"] == v1.PLAN_SCHEMA, "base builder changed its plan schema: review the v2 derivation")
    v1.require(
        plan["cost"]["hardware_policy_pause_seconds"] == CEILING_PAUSE_SECONDS,
        "base builder no longer binds the ladder ceiling: review the v2 derivation",
    )
    intervals = max(0, plan["cost"]["batches"] - 1)
    sources = {**plan["source_digests"], "pause_floor_builder_sha256": v1.digest(Path(__file__).read_bytes())}
    for batch in plan["batches"]:
        path = f"{batch['directory']}/cases.json"
        cases = json.loads(files[path])
        cases["plan_schema"] = PLAN_SCHEMA
        cases["source_digests"] = sources
        files[path] = v1.json_text(cases)
        batch["cases_sha256"] = v1.digest(files[path])
    plan["schema"] = PLAN_SCHEMA
    plan["source_digests"] = sources
    cost = plan["cost"]
    del cost["hardware_policy_pause_seconds"]
    cost["hardware_policy_pause_floor_seconds"] = FLOOR_PAUSE_SECONDS
    cost["hardware_policy_pause_ceiling_seconds"] = CEILING_PAUSE_SECONDS
    cost["minimum_interbatch_pause_seconds"] = intervals * FLOOR_PAUSE_SECONDS
    cost["ceiling_interbatch_pause_seconds"] = intervals * CEILING_PAUSE_SECONDS
    cost["pause_scope"] = PAUSE_SCOPE
    validate_plan(plan, files)
    files["plan.json"] = v1.json_text(plan)
    return files


def validate_plan(plan: dict[str, Any], files: dict[str, str]) -> None:
    """Check the v2 pause fields and the case hashes that bind them; circuit checks live in qi_zz_map."""
    cost = plan["cost"]
    v1.require(plan["schema"] == PLAN_SCHEMA, "plan schema differs")
    intervals = cost["batches"] - 1
    v1.require(
        cost["minimum_interbatch_pause_seconds"] == intervals * HARDWARE_PAUSE_LADDER[0],
        "minimum interbatch pause is not the ladder floor times the batch intervals",
    )
    v1.require(
        cost["ceiling_interbatch_pause_seconds"] == intervals * HARDWARE_PAUSE_LADDER[-1],
        "ceiling interbatch pause is not the ladder top times the batch intervals",
    )
    v1.require(
        cost["minimum_interbatch_pause_seconds"] <= cost["ceiling_interbatch_pause_seconds"],
        "pause floor exceeds the ceiling",
    )
    for batch in plan["batches"]:
        text = files[f"{batch['directory']}/cases.json"]
        v1.require(v1.digest(text) == batch["cases_sha256"], "case hash mismatch")
        v1.require(json.loads(text)["plan_schema"] == PLAN_SCHEMA, "case plan schema differs")


def write(directory: Path, catalogue: Path, shots: int | None) -> None:
    v1.require(not list(directory.glob("**/submission.json")), "refusing to overwrite a submitted proposal")
    files = build(catalogue, shots)
    for relative, content in files.items():
        path = directory / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    cost = json.loads(files["plan.json"])["cost"]
    print(
        f"Tuna ZZ proposal v2: {cost['total_jobs']} circuits, {cost['batches']} batches, pauses "
        f"{cost['minimum_interbatch_pause_seconds']} to {cost['ceiling_interbatch_pause_seconds']} s -> {directory}"
    )


def check(directory: Path, catalogue: Path, shots: int | None) -> None:
    files = build(catalogue, shots)
    existing = {path.relative_to(directory).as_posix() for path in directory.rglob("*") if path.is_file()}
    v1.require(existing == set(files), f"proposal file set differs from regeneration: {sorted(existing ^ set(files))}")
    for relative, content in files.items():
        v1.require(
            (directory / relative).read_text(encoding="utf-8") == content, f"{relative}: differs from regeneration"
        )
    print(f"Tuna ZZ proposal v2: {len(files)} source-bound files match; pauses by ladder floor and ceiling")


def self_test(catalogue: Path = v1.CATALOGUE) -> None:
    v1.self_test(catalogue)
    files = build(catalogue)
    base = v1.build(catalogue)
    plan = json.loads(files["plan.json"])
    base_plan = json.loads(base["plan.json"])
    v1.require(plan["cost"]["batches"] == 139, "batch count differs")
    v1.require(plan["cost"]["minimum_interbatch_pause_seconds"] == 138 * 30 == 4140, "pause floor differs")
    v1.require(plan["cost"]["ceiling_interbatch_pause_seconds"] == 138 * 120 == 16560, "pause ceiling differs")
    v1.require(base_plan["cost"]["minimum_interbatch_pause_seconds"] == 16560, "v1 pause binding differs")
    v1.require(base_plan["schema"] == "qi-zz-map-plan-v1", "v1 plan schema differs")
    v1.require(
        {name: text for name, text in files.items() if name.endswith(".cq")}
        == {name: text for name, text in base.items() if name.endswith(".cq")},
        "v2 circuits differ from v1",
    )
    changed = json.loads(files["plan.json"])
    changed["cost"]["minimum_interbatch_pause_seconds"] = 16560
    try:
        validate_plan(changed, files)
    except ValueError:
        pass
    else:
        raise ValueError("a ceiling-valued pause minimum escaped validation")
    print("Tuna ZZ v2: ladder floor 4140 s and ceiling 16560 s, v1 binding and circuit identity checked")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", type=Path)
    mode.add_argument("--check", type=Path)
    mode.add_argument("--self-test", action="store_true")
    parser.add_argument("--catalogue", type=Path, default=v1.CATALOGUE)
    parser.add_argument("--shots", type=int, default=None, help="proposed shots; defaults to the retained catalogue")
    args = parser.parse_args()
    if args.write:
        write(args.write, args.catalogue, args.shots)
    elif args.check:
        check(args.check, args.catalogue, args.shots)
    else:
        self_test(args.catalogue)


if __name__ == "__main__":
    main()
