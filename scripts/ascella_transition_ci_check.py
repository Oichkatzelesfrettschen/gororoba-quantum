"""Bind the scheduled Ascella repeat to its frozen case and retain matched-mesh analysis."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import ascella_transition_context as context
import ascella_transition_day_repeat as repeat

repeat.BUNDLE = Path("docs/evidence/ascella-transition-day-repeat-ci")

# Ascella's Explorer row reads running while it serves other users' jobs, so the
# scheduler admits that status beside available (scheduler-admission.md).
ADMITTED_STATUSES = ["available", "running"]


def elapsed_allowed(start: float, baseline: float) -> bool:
    """Admit a provider start at least 24 hours after the baseline, the case's preregistered separation."""
    return math.isfinite(start) and math.isfinite(baseline) and start >= baseline + 86_400


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
        or plan.get("admitted_statuses") != ADMITTED_STATUSES
    ):
        raise ValueError("the scheduled plan differs from the frozen case or its bounds")


def check_result(directory: Path) -> dict[str, Any]:
    """Retain the complete analysis under the scheduler's dynamically named run."""
    absolute = directory.resolve()
    absolute.relative_to(repeat.ROOT)
    if absolute.parent != (repeat.ROOT / "results/quandela/runs").resolve():
        raise ValueError("the scheduled result must be a retained Quandela run")
    bundle = repeat.ROOT / repeat.BUNDLE
    campaign, expected = repeat._reported_case(bundle)
    manifest, _, _ = repeat.qd.load_case(absolute)
    if manifest != expected:
        raise ValueError("the retained next-day manifest differs from its reviewed case")
    baseline, earlier = context.read_run(repeat.ROOT / repeat.BASE_RUN)
    measured, later = context.read_run(absolute)
    start = measured["start_time"]
    if (
        isinstance(start, bool)
        or not isinstance(start, int | float)
        or not elapsed_allowed(start, campaign["baseline_start_unix"])
    ):
        raise ValueError("the provider start lies less than 24 hours after the baseline")
    if [row["name"] for row in earlier] != [row["name"] for row in later]:
        raise ValueError("the returned settings differ from the matched baseline")
    comparisons = context.ordered_map(repeat._comparison_job, list(zip(earlier, later, strict=True)), min_items=1)
    result = {
        "schema": "ascella-transition-day-repeat-analysis-v1",
        "campaign_sha256": context._sha((bundle / "campaign.json").read_bytes()),
        "analysis_source_sha256": context._sha(Path(repeat.__file__).read_bytes()),
        "scheduled_analysis_source_sha256": context._sha(Path(__file__).read_bytes()),
        "confidence": 0.95,
        "endpoints": 140,
        "baseline": baseline,
        "repeat": measured,
        "comparisons": comparisons,
        "matched_meshes": sum(row["matched_mesh"] for row in comparisons),
        "elapsed_hours": round((start - campaign["baseline_start_unix"]) / 3_600, 6),
        "boundary": (
            "Same recorded mesh does not establish unchanged analog calibration; "
            "elapsed time and context can confound drift."
        ),
    }
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
