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

# The retained campaign binds the producer digests of the commit that froze it and keeps its bytes. The
# successor binds the current producer digests and names the retained campaign by digest.
RETAINED_CAMPAIGN = "campaign.json"
SUCCESSOR_CAMPAIGN = "campaign-v2.json"
# The two identity fields that bind a retained analysis to the campaign and checker bytes of its own commit.
BOUND_IDENTITIES = ("campaign_sha256", "scheduled_analysis_source_sha256")

# Ascella's Explorer row reads running while it serves other users' jobs, so the
# scheduler admits that status beside available (scheduler-admission.md).
ADMITTED_STATUSES = ["available", "running"]


def elapsed_allowed(now: float, baseline: float) -> bool:
    """Admit a provider start at least 24 hours after the baseline, the case's preregistered separation."""
    return math.isfinite(now) and math.isfinite(baseline) and now >= baseline + 86_400


def validate_registration(result: dict[str, Any], collected: dict[str, Any], campaign: str, producer: str) -> None:
    """Run the runner's registration rules with the 24-hour separation in place of its next-day window.

    validate_registration reads time_allowed as a module global of the runner, whose source digest the
    analysis records, so the scheduled repeat swaps the rule for this call and restores it after.
    """
    original = repeat.time_allowed
    repeat.time_allowed = elapsed_allowed
    try:
        repeat.validate_registration(result, collected, campaign, producer)
    finally:
        repeat.time_allowed = original


def successor_files() -> dict[str, bytes]:
    """The case files the check reads: the retained case beside the successor campaign built from current sources."""
    files = repeat.build_files()
    campaign = json.loads(files.pop(RETAINED_CAMPAIGN))
    retained = (repeat.ROOT / repeat.BUNDLE / RETAINED_CAMPAIGN).read_bytes()
    campaign["successor_of"] = {"file": RETAINED_CAMPAIGN, "sha256": context._sha(retained)}
    files[SUCCESSOR_CAMPAIGN] = context._json_bytes(campaign)
    return files


def write_successor(bundle: Path) -> None:
    """Write the successor campaign once; an existing file with other bytes is an error."""
    path = bundle / SUCCESSOR_CAMPAIGN
    value = successor_files()[SUCCESSOR_CAMPAIGN]
    if path.exists() and path.read_bytes() != value:
        raise ValueError(f"the successor campaign differs: {path}")
    if not path.exists():
        path.write_bytes(value)


def check_files(bundle: Path) -> None:
    """Require the successor campaign and the retained case files to equal what the current sources build."""
    for name, value in successor_files().items():
        path = bundle / name
        if not path.is_file() or path.read_bytes() != value:
            raise ValueError(f"the frozen next-day case differs: {path}")


def _reported_case(bundle: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    check_files(bundle)
    campaign = context._read(bundle / SUCCESSOR_CAMPAIGN)
    source = context._read(bundle / campaign["case"]["file"])
    source.update(
        acquisition_admission="ready",
        source_case_sha256=campaign["case"]["sha256"],
        reviewed_case=campaign["written_case"],
    )
    return campaign, source


def check_plan(plan: dict[str, Any]) -> None:
    """Reject a scheduler plan that differs from the source-bound case."""
    _, manifest = _reported_case(repeat.ROOT / repeat.BUNDLE)
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
    campaign, expected = _reported_case(bundle)
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
        "campaign_sha256": context._sha((bundle / SUCCESSOR_CAMPAIGN).read_bytes()),
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
    producer = context._sha(Path(repeat.__file__).read_bytes())
    retained_path = absolute / "day-repeat-analysis.json"
    if retained_path.exists():
        result = _replay_retained(retained_path, result, bundle)
        validate_registration(result, collected, result["campaign_sha256"], producer)
    else:
        validate_registration(result, collected, result["campaign_sha256"], producer)
        repeat._retain_json(retained_path, result)
    if result["matched_meshes"] != 5:
        raise ValueError("the analysis was retained but fewer than five returned meshes match")
    return result


def _replay_retained(path: Path, recomputed: dict[str, Any], bundle: Path) -> dict[str, Any]:
    """Accept a retained analysis whose measured fields equal the recomputation and whose campaign is known.

    The retained analysis binds the campaign and checker digests of the commit that wrote it, so only those
    two identity fields may differ, and the campaign digest must name the retained or the successor campaign.
    """
    retained = context._read(path)
    known = {context._sha((bundle / name).read_bytes()) for name in (RETAINED_CAMPAIGN, SUCCESSOR_CAMPAIGN)}
    if retained.get("campaign_sha256") not in known:
        raise ValueError(f"the retained analysis binds an unknown campaign: {path}")
    measured = {key: value for key, value in recomputed.items() if key not in BOUND_IDENTITIES}
    if {key: value for key, value in retained.items() if key not in BOUND_IDENTITIES} != measured:
        raise ValueError(f"the retained result differs: {path}")
    return retained


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--plan-check", type=Path)
    group.add_argument("--matched-check", type=Path)
    group.add_argument("--write-successor", action="store_true")
    args = parser.parse_args()
    try:
        if args.write_successor:
            write_successor(repeat.ROOT / repeat.BUNDLE)
            print(f"wrote {SUCCESSOR_CAMPAIGN}")
        elif args.plan_check:
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
