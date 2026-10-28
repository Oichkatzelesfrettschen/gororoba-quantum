"""Prepare a time-gated, matched-mesh repeat of Ascella transition settings."""

from __future__ import annotations

import argparse
import copy
import json
import math
import os
import subprocess
import sys
import tempfile
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import ascella_transition_context as context
import qd_platform as qd

ROOT = context.ROOT
SOURCE = Path("docs/evidence/ascella-transition-context-diagnostics/cases/packed-forward/cases.json")
BASE_RUN = Path("results/quandela/runs/ascella-context-packed-forward")
BUNDLE = Path("docs/evidence/ascella-transition-day-repeat")
INTERVENTION_ANALYSIS = Path("results/quandela/ascella-transition-mesh-port-analysis.json")
RUN = Path("results/quandela/runs/ascella-transition-matched-mesh-day-repeat")
PACIFIC = ZoneInfo("America/Los_Angeles")


def time_allowed(now: float, baseline: float) -> bool:
    """Admit only the following Pacific date after at least 24 elapsed hours."""
    if not math.isfinite(now) or not math.isfinite(baseline) or now < baseline + 86_400:
        return False
    try:
        current_date = datetime.fromtimestamp(now, UTC).astimezone(PACIFIC).date()
        baseline_date = datetime.fromtimestamp(baseline, UTC).astimezone(PACIFIC).date()
    except (OverflowError, OSError, ValueError):
        return False
    return current_date == baseline_date + timedelta(days=1)


def make_manifest(source: dict[str, Any]) -> dict[str, Any]:
    """Reproduce the exact five-setting forward iterator with a new case identity."""
    result = copy.deepcopy(source)
    if result.get("iterations") != 5 or len(result.get("settings", [])) != 5:
        raise ValueError("the retained forward iterator must contain five settings")
    for row in result["settings"]:
        row.update(cohort_id="ascella-transition-day-repeat", context="day-repeat")
    result.update(
        job="transition-matched-mesh-day-repeat",
        cohort_id="ascella-transition-day-repeat",
        diagnostic_context="day-repeat",
        acquisition_admission="awaiting-day-guard",
        preregistered={
            "primary": "all physical output categories, invalid outcomes and leakage",
            "comparison": "matched returned-mesh output distributions at least 24 hours apart",
            "endpoints": 140,
            "confidence": 0.95,
        },
    )
    return result


def safe_to_post(directory: Path) -> bool:
    """Any existing POST checkpoint requires collection or explicit reconciliation."""
    return not any(
        (directory / name).exists() for name in ("submission.json", "submission-state.json", "job-body.json")
    )


def build_files() -> dict[str, bytes]:
    """Freeze a next-day case against the completed context and intervention cohorts."""
    source_bytes = (ROOT / SOURCE).read_bytes()
    source = json.loads(source_bytes)
    baseline_metadata, baseline_entries = context.read_run(ROOT / BASE_RUN)
    if len(baseline_entries) != 5:
        raise ValueError("the matched baseline must contain five complete settings")
    baseline_time = baseline_metadata["start_time"]
    if (
        isinstance(baseline_time, bool)
        or not isinstance(baseline_time, int | float)
        or not math.isfinite(baseline_time)
    ):
        raise ValueError("the baseline job lacks a finite execution start")
    intervention_bytes = (ROOT / INTERVENTION_ANALYSIS).read_bytes()
    if not json.loads(intervention_bytes).get("complete"):
        raise ValueError("the independent-mesh and port cohort is incomplete")
    manifest = make_manifest(source)
    circuit = (ROOT / SOURCE.parent / source["circuit"]["file"]).read_bytes()
    if context._sha(circuit) != source["circuit"]["sha256"]:
        raise ValueError("the baseline circuit digest differs")
    manifest_bytes = context._json_bytes(manifest)
    written = ROOT / BUNDLE / "README.md"
    campaign = {
        "schema": "ascella-transition-day-repeat-campaign-v1",
        "source_manifest": {"file": SOURCE.as_posix(), "sha256": context._sha(source_bytes)},
        "baseline_run": BASE_RUN.as_posix(),
        "baseline_start_unix": baseline_time,
        "not_before_utc": datetime.fromtimestamp(baseline_time + 86_400, UTC).isoformat(),
        "required_pacific_date": (
            datetime.fromtimestamp(baseline_time, UTC).astimezone(PACIFIC).date() + timedelta(days=1)
        ).isoformat(),
        "intervention_analysis": {"file": INTERVENTION_ANALYSIS.as_posix(), "sha256": context._sha(intervention_bytes)},
        "written_case": {"file": written.relative_to(ROOT).as_posix(), "sha256": context._sha(written.read_bytes())},
        "producer_sha256": context._sha(Path(__file__).read_bytes()),
        "dependencies": [
            {"file": name, "sha256": context._sha((ROOT / name).read_bytes())}
            for name in (
                "scripts/ascella_transition_context.py",
                "scripts/ascella_transition_interventions.py",
                "scripts/ascella_experiment_analysis.py",
                "scripts/qd_platform.py",
                "scripts/ascella_transition_day_repeat_service.sh",
                "gororoba_quantum/parallel.py",
            )
        ],
        "case": {"file": "case/cases.json", "sha256": context._sha(manifest_bytes)},
        "run": RUN.as_posix(),
        "endpoints": 140,
        "confidence": 0.95,
        "credit_ceiling": context.CREDIT_CEILING,
    }
    return {
        "campaign.json": context._json_bytes(campaign),
        "case/cases.json": manifest_bytes,
        "case/circuit.json": circuit,
    }


def write_files(bundle: Path) -> None:
    for name, value in build_files().items():
        path = bundle / name
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists() and path.read_bytes() != value:
            raise ValueError(f"the frozen next-day case differs: {path}")
        if not path.exists():
            path.write_bytes(value)


def check_files(bundle: Path) -> None:
    for name, value in build_files().items():
        path = bundle / name
        if not path.is_file() or path.read_bytes() != value:
            raise ValueError(f"the frozen next-day case differs: {path}")


def preflight(bundle: Path) -> dict[str, Any]:
    check_files(bundle)
    record = qd.plan(bundle / "case", "qpu:ascella", context.CREDIT_CEILING, 300, 1)
    record["preflight_observed_utc"] = qd.now()
    path = bundle / "preflight.json"
    qd.write_json(path, record, exclusive=True)
    return record


def _reported_case(bundle: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    check_files(bundle)
    campaign = context._read(bundle / "campaign.json")
    source = context._read(bundle / campaign["case"]["file"])
    source.update(
        acquisition_admission="ready",
        source_case_sha256=campaign["case"]["sha256"],
        reviewed_case=campaign["written_case"],
    )
    return campaign, source


def submit(bundle: Path, approval: str, now: float | None = None) -> dict[str, Any]:
    """Reject early, late or ambiguous retries before the provider can receive a POST."""
    if not approval.strip():
        raise ValueError("the user's next-day instruction is required")
    campaign, manifest = _reported_case(bundle)
    instant = time.time() if now is None else now
    if not time_allowed(instant, campaign["baseline_start_unix"]):
        raise ValueError("the request is outside the frozen next-day Pacific window")
    directory = ROOT / RUN
    if not safe_to_post(directory):
        raise ValueError("an existing submission checkpoint requires collection or reconciliation")
    directory.mkdir(parents=True, exist_ok=True)
    for name, value in (
        ("cases.json", context._json_bytes(manifest)),
        ("circuit.json", (bundle / "case/circuit.json").read_bytes()),
    ):
        path = directory / name
        if path.exists() and path.read_bytes() != value:
            raise ValueError(f"the prepared next-day case differs: {path}")
        if not path.exists():
            path.write_bytes(value)
    preflight_record = context._read(bundle / "preflight.json")
    manifest_hash = context._sha((directory / "cases.json").read_bytes())

    def verify(planned: dict[str, Any]) -> None:
        if (
            not time_allowed(time.time(), campaign["baseline_start_unix"])
            or planned["cases_sha256"] != manifest_hash
            or context.body_projection(planned["body"]) != context.body_projection(preflight_record["body"])
            or planned["credit_ceiling"] > context.CREDIT_CEILING
            or planned["admitted_statuses"] != ["available"]
        ):
            raise qd.PlatformError("the next-day timing, payload, price or availability differs from the case")
        check_files(bundle)

    return qd.submit(directory, "qpu:ascella", approval, context.CREDIT_CEILING, 300, 1, verify=verify)


def analyze(bundle: Path) -> dict[str, Any]:
    """Compare the five returned distributions to their exact matched baseline."""
    campaign, expected = _reported_case(bundle)
    directory = ROOT / RUN
    manifest, _, _ = qd.load_case(directory)
    if manifest != expected:
        raise ValueError("the retained next-day manifest differs from its reviewed case")
    baseline_metadata, earlier = context.read_run(ROOT / BASE_RUN)
    repeat_metadata, later = context.read_run(directory)
    start = repeat_metadata["start_time"]
    if (
        isinstance(start, bool)
        or not isinstance(start, int | float)
        or not time_allowed(start, campaign["baseline_start_unix"])
    ):
        raise ValueError("the provider start lies outside the registered next-day window")
    if [row["name"] for row in earlier] != [row["name"] for row in later]:
        raise ValueError("the returned settings differ from the matched baseline")
    comparisons = context.ordered_map(_comparison_job, list(zip(earlier, later, strict=True)), min_items=1)
    return {
        "schema": "ascella-transition-day-repeat-analysis-v1",
        "campaign_sha256": context._sha((bundle / "campaign.json").read_bytes()),
        "analysis_source_sha256": context._sha(Path(__file__).read_bytes()),
        "confidence": 0.95,
        "endpoints": 140,
        "baseline": baseline_metadata,
        "repeat": repeat_metadata,
        "comparisons": comparisons,
        "matched_meshes": sum(row["matched_mesh"] for row in comparisons),
        "boundary": (
            "Same recorded mesh does not establish unchanged analog calibration; "
            "elapsed time and context can confound drift."
        ),
    }


def _comparison_job(arguments: tuple[dict[str, Any], dict[str, Any]]) -> dict[str, Any]:
    first, second = arguments
    return {"setting": first["name"], **context.compare(first, second, endpoints=140)}


def append_registry(text: str, acquisition: dict[str, Any], claim: dict[str, Any]) -> str:
    """Append one acquisition and claim without reformatting existing registry records."""
    original = json.loads(text)
    if original.get("schema") != "research-state-v2" or not original.get("acquisitions") or not original.get("claims"):
        raise ValueError("the research registry has an unexpected structure")
    if any(row["id"] == acquisition["id"] for row in original["acquisitions"]) or any(
        row["id"] == claim["id"] for row in original["claims"]
    ):
        raise ValueError("the next-day acquisition or claim is already registered")

    def formatted(row: dict[str, Any]) -> str:
        return "\n".join("    " + line for line in json.dumps(row, indent=2, ensure_ascii=False).splitlines())

    marker = '\n  ],\n  "claims": ['
    if text.count(marker) != 1:
        raise ValueError("the research registry array boundary differs")
    updated = text.replace(marker, ",\n" + formatted(acquisition) + marker, 1)
    ending = "\n  ]\n}\n"
    if not updated.endswith(ending):
        raise ValueError("the research registry closing boundary differs")
    updated = updated[: -len(ending)] + ",\n" + formatted(claim) + ending
    expected = {
        **original,
        "acquisitions": [*original["acquisitions"], acquisition],
        "claims": [*original["claims"], claim],
    }
    if json.loads(updated) != expected:
        raise ValueError("the registry insertion changed an existing record")
    return updated


def _retain_json(path: Path, value: dict[str, Any]) -> None:
    if path.exists():
        if context._read(path) != value:
            raise ValueError(f"the retained result differs: {path}")
    else:
        qd.write_json(path, value, exclusive=True)


def validate_registration(
    result: dict[str, Any], collected: dict[str, Any], campaign_hash: str, producer_hash: str
) -> None:
    """Admit only a complete, time-qualified analysis before registering a hardware claim."""
    if (
        result.get("schema") != "ascella-transition-day-repeat-analysis-v1"
        or result.get("campaign_sha256") != campaign_hash
        or result.get("analysis_source_sha256") != producer_hash
        or result.get("endpoints") != 140
        or result.get("confidence") != 0.95
    ):
        raise ValueError("the next-day analysis identity or confidence family differs")
    comparisons = result.get("comparisons")
    if not isinstance(comparisons, list) or len(comparisons) != 5:
        raise ValueError("the next-day analysis requires all five comparisons")
    if [row.get("setting") for row in comparisons] != [name for _, name in context.SELECTION]:
        raise ValueError("the next-day comparison settings differ from the frozen order")
    for row in comparisons:
        bounds = row.get("simultaneous_total_variation_bounds")
        if (
            type(row.get("matched_mesh")) is not bool
            or not isinstance(bounds, list)
            or len(bounds) != 2
            or not all(isinstance(value, int | float) and math.isfinite(value) for value in bounds)
            or not 0 <= bounds[0] <= bounds[1] <= 1
        ):
            raise ValueError("a next-day comparison lacks finite attributable bounds")
    if result.get("matched_meshes") != sum(row["matched_mesh"] for row in comparisons):
        raise ValueError("the reported matched-mesh count differs from the comparisons")
    baseline = result.get("baseline", {}).get("start_time")
    repeat = result.get("repeat", {}).get("start_time")
    if (
        isinstance(baseline, bool)
        or not isinstance(baseline, int | float)
        or isinstance(repeat, bool)
        or not isinstance(repeat, int | float)
        or not time_allowed(repeat, baseline)
    ):
        raise ValueError("the provider starts do not establish the frozen next-day window")
    duration = collected.get("status", {}).get("duration")
    if (
        collected.get("status", {}).get("status") != "completed"
        or collected.get("samples") != 5 * context.SAMPLES
        or isinstance(duration, bool)
        or not isinstance(duration, int | float)
        or not math.isfinite(duration)
        or not 0 <= duration <= 300
    ):
        raise ValueError("the next-day acquisition lacks the complete bounded sample target")


def register_result(bundle: Path, result: dict[str, Any]) -> None:
    """Register the delayed acquisition without overwriting concurrent tracked changes."""
    directory = ROOT / RUN
    facts = qd.run_facts(directory)
    submission = context._read(directory / "submission.json")
    collected = context._read(directory / "results.json")
    validate_registration(
        result,
        collected,
        context._sha((bundle / "campaign.json").read_bytes()),
        context._sha(Path(__file__).read_bytes()),
    )
    output = ROOT / "results/quandela/ascella-transition-day-repeat-analysis.json"
    inventory = {
        "schema": "ascella-transition-day-repeat-inventory-v1",
        "job_id": submission["job_id"],
        "status": collected["status"]["status"],
        "duration_seconds": collected["status"]["duration"],
        "accepted_samples": collected["samples"],
        "recorded_credit_charge": facts["charge"],
        "raw_result_sha256": context._sha((directory / "raw/result.json").read_bytes()),
        "result_sha256": context._sha((directory / "results.json").read_bytes()),
        "matched_meshes": result["matched_meshes"],
    }
    inventory_path = bundle / "acquisition-inventory.json"
    _retain_json(inventory_path, inventory)
    lines = [
        "# Ascella next-day matched-mesh findings",
        "",
        f"The delayed Ascella job completed with {collected['samples']:,} accepted events in "
        f"{collected['status']['duration']} provider seconds. The returned circuit and input matched the "
        f"baseline in {result['matched_meshes']} of five settings.",
        "",
        "| Setting | Returned mesh matches | Observed total variation | Simultaneous interval |",
        "|---|---|---:|---|",
    ]
    for row in result["comparisons"]:
        lower, upper = row["simultaneous_total_variation_bounds"]
        lines.append(
            f"| {row['setting']} | {row['matched_mesh']} | {row['observed_total_variation']:.6f} | "
            f"[{lower:.6f}, {upper:.6f}] |"
        )
    lines.extend(
        [
            "",
            "The [analysis](../../../results/quandela/ascella-transition-day-repeat-analysis.json) "
            "binds every retained result and the 140-endpoint confidence family. Coverage assumes IID "
            "accepted events within each setting. Matched returned mesh metadata does not establish "
            "unchanged applied analog controls, and a day-separated difference does not by itself identify "
            "calibration drift as the cause.",
            "",
        ]
    )
    findings = bundle / "findings.md"
    findings_text = "\n".join(lines)
    if findings.exists() and findings.read_text(encoding="utf-8") != findings_text:
        raise ValueError("the retained next-day findings differ")
    if not findings.exists():
        findings.write_text(findings_text, encoding="utf-8")
    for args in (("diff", "--quiet"), ("diff", "--cached", "--quiet")):
        if subprocess.run(["git", *args], cwd=ROOT, check=False).returncode != 0:
            raise ValueError("tracked worktree changes appeared; retain the raw result and review registry integration")
    registry = ROOT / "docs/state/research_state.json"
    current = registry.read_text(encoding="utf-8")
    entries = context._read(registry)
    acquisition_id = "qd-ascella-transition-matched-mesh-day-repeat"
    claim_id = "ascella-transition-day-separated-matched-mesh"
    known_acquisition = [row for row in entries["acquisitions"] if row["id"] == acquisition_id]
    known_claim = [row for row in entries["claims"] if row["id"] == claim_id]
    if known_acquisition or known_claim:
        if len(known_acquisition) != 1 or len(known_claim) != 1 or known_acquisition[0]["run"] != RUN.as_posix():
            raise ValueError("the existing next-day registry identifiers differ")
    else:
        acquisition = {
            "id": acquisition_id,
            "provider": "quandela",
            "run": RUN.as_posix(),
            "family": "day-separated dimension-six matched meshes",
            "question": (
                "How do five retained transition distributions compare at least 24 hours later "
                "under matching returned mesh identities?"
            ),
        }
        references = (output, inventory_path, bundle / "campaign.json")
        claim: dict[str, Any] = {
            "id": claim_id,
            "statement": (
                f"The five-setting Ascella repeat completed at least 24 hours after its baseline and retained "
                f"{collected['samples']:,} accepted events. Returned circuit and input serializations match "
                f"the baseline for {result['matched_meshes']} of five settings; the registered analysis "
                "reports each conditional output-distribution comparison."
            ),
            "domain": "hardware",
            "evidence_class": "preregistered hardware inference",
            "status": "established",
            "boundary": (
                "Five selected settings, a fixed 140-endpoint family and IID accepted-event intervals. "
                "A matched returned mesh does not establish identical applied analog controls; elapsed time, "
                "calibration and source or detector response can confound the comparison."
            ),
            "evidence": [
                {"path": path.relative_to(ROOT).as_posix(), "sha256": context._sha(path.read_bytes())}
                for path in references
            ],
            "documents": [
                (bundle / "README.md").relative_to(ROOT).as_posix(),
                findings.relative_to(ROOT).as_posix(),
            ],
            "gates": {},
            "acquisitions": [acquisition_id],
            "assumptions": [
                "Simultaneous binomial coverage is conditional on IID accepted events within each setting."
            ],
            "depends_on": ["ascella-transition-context-matched-mesh"],
            "supersedes": [],
            "superseded_by": None,
        }
        updated = append_registry(current, acquisition, claim)
        descriptor, temporary = tempfile.mkstemp(prefix=".research-state-", dir=registry.parent)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
                stream.write(updated)
                stream.flush()
                os.fsync(stream.fileno())
            if registry.read_text(encoding="utf-8") != current:
                raise ValueError("the research registry changed during integration")
            os.replace(temporary, registry)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
    subprocess.run([sys.executable, "scripts/research_state.py", "--write"], cwd=ROOT, check=True)
    subprocess.run([sys.executable, "scripts/research_state.py", "--check"], cwd=ROOT, check=True)
    print("registered the next-day acquisition and rendered the research state", flush=True)


def run(bundle: Path, approval: str) -> dict[str, Any]:
    """Execute once, retain raw data, and permit only read-only retries before any POST checkpoint."""
    campaign, _ = _reported_case(bundle)
    directory = ROOT / RUN
    if not (directory / "submission.json").exists():
        if not safe_to_post(directory):
            raise ValueError("an ambiguous existing POST checkpoint requires reconciliation")
        status = subprocess.run(
            ["git", "-c", "core.fsmonitor=false", "status", "--porcelain", "--untracked-files=all"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        if status.stdout:
            raise ValueError(
                "the acquisition worktree has uncommitted changes; preserve and review them before the repeat"
            )
        deadline = min(time.time() + 3_600, campaign["baseline_start_unix"] + 30 * 3_600)
        while True:
            if not time_allowed(time.time(), campaign["baseline_start_unix"]):
                raise ValueError("the next-day Pacific execution window is closed")
            try:
                receipt = submit(bundle, approval)
                print(f"submitted {receipt['case']}: {receipt['job_id']}", flush=True)
                break
            except qd.PlatformError as error:
                text = str(error).lower()
                retryable = qd.transient(error) or any(
                    fragment in text for fragment in ("running or queued", "is calibration", "is maintenance")
                )
                if not retryable or not safe_to_post(directory) or time.time() + 60 > deadline:
                    raise
                print(
                    "provider unavailable or token busy; retrying the read-only admission after 60 seconds", flush=True
                )
                time.sleep(60)
    collected = qd.collect(directory, 5, 1_800)
    if collected["status"]["status"] != "completed":
        raise ValueError(f"the next-day job ended as {collected['status']['status']}")
    result = analyze(bundle)
    output = ROOT / "results/quandela/ascella-transition-day-repeat-analysis.json"
    _retain_json(output, result)
    register_result(bundle, result)
    print(f"retained {output.relative_to(ROOT)}; matched meshes: {result['matched_meshes']}/5", flush=True)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--bundle", type=Path, default=ROOT / BUNDLE)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--approval")
    args = parser.parse_args()
    os.environ.setdefault("QUANDELA_TOKEN_FILE", str(Path.home() / ".config/quandela/cloud-token"))
    try:
        if args.run:
            run(args.bundle, args.approval or "")
        elif args.preflight:
            record = preflight(args.bundle)
            print(context._json_bytes(qd.plan_summary(record)).decode(), end="")
        elif args.check:
            check_files(args.bundle)
            print("the next-day case matches its retained sources")
        else:
            write_files(args.bundle)
            print("wrote the next-day matched-mesh case")
    except (ValueError, qd.PlatformError, subprocess.CalledProcessError) as error:
        raise SystemExit(str(error)) from None
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
