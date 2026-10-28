"""Bind the scheduled Ascella repeat to its frozen case and retain matched-mesh analysis."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import ascella_transition_context as context
import ascella_transition_day_repeat as repeat


def check_plan(plan: dict[str, Any]) -> None:
    """Reject a scheduler plan that differs from the source-bound case."""
    _, manifest = repeat._reported_case(repeat.ROOT / repeat.BUNDLE)
    expected = context._sha(context._json_bytes(manifest))
    ceiling = plan.get("credit_ceiling")
    if (
        plan.get("cases_sha256") != expected
        or plan.get("platform") != "qpu:ascella"
        or isinstance(ceiling, bool)
        or not isinstance(ceiling, int | float)
        or not math.isfinite(ceiling)
        or not 0 <= ceiling <= context.CREDIT_CEILING
        or plan.get("admitted_statuses") != ["available"]
    ):
        raise ValueError("the scheduled plan differs from the frozen case or its bounds")


def check_result(directory: Path) -> dict[str, Any]:
    """Retain the complete analysis under the scheduler's dynamically named run."""
    absolute = directory.resolve()
    relative = absolute.relative_to(repeat.ROOT)
    if absolute.parent != (repeat.ROOT / "results/quandela/runs").resolve():
        raise ValueError("the scheduled result must be a retained Quandela run")
    repeat.RUN = relative
    result = repeat.analyze(repeat.ROOT / repeat.BUNDLE)
    collected = context._read(absolute / "results.json")
    repeat.validate_registration(
        result,
        collected,
        context._sha((repeat.ROOT / repeat.BUNDLE / "campaign.json").read_bytes()),
        context._sha(Path(repeat.__file__).read_bytes()),
    )
    repeat._retain_json(absolute / "day-repeat-analysis.json", result)
    if result["matched_meshes"] != 5:
        raise ValueError("the analysis was retained but fewer than five returned meshes match")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--plan-check", type=Path)
    group.add_argument("--matched-check", type=Path)
    args = parser.parse_args()
    try:
        if args.plan_check:
            check_plan(json.loads(args.plan_check.read_bytes()))
            print("scheduled plan matches the frozen Ascella repeat")
        else:
            result = check_result(args.matched_check)
            print(f"retained five comparisons; matched meshes: {result['matched_meshes']}/5")
    except (ValueError, OSError) as error:
        raise SystemExit(str(error)) from None
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
