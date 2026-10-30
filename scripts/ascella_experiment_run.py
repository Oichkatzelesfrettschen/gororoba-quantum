"""Admit the next frozen Ascella acquisition only after complete predecessor receipts.

The generic provider runner owns the token lock, current availability, tariff,
checkpoint and immutable raw collection. The cohort guard binds its fresh payload
to the reviewed preflight and checks the scientific acquisition prerequisites.
"""

from __future__ import annotations

import argparse
import json
import math
import uuid
from pathlib import Path
from typing import Any

import ascella_experiment_request as request
import qd_platform as qd

ROOT = request.ROOT


def body_projection(body: dict[str, Any]) -> dict[str, Any]:
    """Compare every request field except the SDK's freshly assigned process UUID."""
    process = body.get("process_id")
    if not isinstance(process, str) or str(uuid.UUID(process)) != process:
        raise ValueError("the SDK process_id must be a canonical UUID")
    return {key: value for key, value in body.items() if key != "process_id"}


def prerequisite_decision(campaign: dict[str, Any], index: int, report: dict[str, Any]) -> dict[str, Any]:
    """Require a full fixed target before another job, independent of optical performance."""
    if type(index) is not int or not 0 <= index < len(campaign["cases"]):
        raise ValueError("acquisition index lies outside the frozen case inventory")
    rows = {row["setting_id"]: row for row in report["settings"]}
    jobs = {job["directory"]: job for job in report["jobs"]}
    durations = []
    predecessors = campaign["cases"][:index]
    for case in predecessors:
        for identifier in case["settings"]:
            row = rows.get(identifier, {})
            if row.get("interface_complete") is not True or row.get("accepted_events") != request.SAMPLES:
                raise ValueError(f"predecessor result is incomplete or unattributable: {identifier}")
        job = jobs.get(case["directory"], {})
        duration = job.get("duration_seconds")
        if (
            job.get("status") != "collected"
            or isinstance(duration, bool)
            or not isinstance(duration, int | float)
            or not math.isfinite(duration)
            or not 0 <= duration <= 300
        ):
            raise ValueError(f"predecessor duration is absent, invalid or above the stop limit: {case['name']}")
        durations.append(duration)
    packing_seconds = None
    if index == 5:
        packing_seconds = 12 * max(durations) + 60
        if packing_seconds > 300:
            raise ValueError(f"twelve-setting packing model exceeds 300 seconds: {packing_seconds:g}")
    return {
        "admitted": True,
        "predecessor_cases": [case["name"] for case in predecessors],
        "measured_predecessor_durations": durations,
        "pilot_packing_model_seconds": packing_seconds,
        "runtime_boundary": "The first dark acquisition qualifies unknown runtime under a 300-second stop limit.",
        "scientific_boundary": "Negative optical performance retains the diagnostic controls and pilot question.",
    }


def _json(path: Path) -> Any:
    return json.loads(path.read_bytes())


def _sha(path: Path) -> str:
    return request.sha256(path.read_bytes())


def _retained(path: Path, value: Any) -> None:
    text = request.json_text(value)
    if path.exists():
        if path.read_text(encoding="utf-8") != text:
            raise ValueError(f"admission evidence differs: {path}")
    else:
        path.write_text(text, encoding="utf-8")


def next_acquisition(bundle: Path) -> tuple[int, dict[str, Any], dict[str, Any]]:
    """Audit collected predecessors and locate the first unsubmitted frozen job."""
    from ascella_experiment_analysis import analyze_campaign

    request.check_files(bundle)
    campaign = _json(bundle / "campaign.json")
    predecessors = []
    for index, case in enumerate(campaign["cases"]):
        directory = ROOT / case["directory"]
        if (directory / "submission.json").exists():
            if not (directory / "results.json").exists():
                raise ValueError(f"collect the existing predecessor job before continuing: {directory}")
            predecessors.append(directory)
            continue
        if any((directory / name).exists() for name in ("submission-state.json", "job-body.json")):
            raise ValueError(f"reconcile the existing submission checkpoint: {directory}")
        report = analyze_campaign(bundle / "campaign.json", predecessors)
        return index, prerequisite_decision(campaign, index, report), report
    raise ValueError("all six frozen jobs already have retained acquisitions")


def submit_next(bundle: Path, approval: str) -> dict[str, Any]:
    """Bind the prerequisite evidence, exact case and fresh body before the guarded POST."""
    from ascella_experiment_analysis import _manifest_for_run

    index, decision, report = next_acquisition(bundle)
    campaign = _json(bundle / "campaign.json")
    case = campaign["cases"][index]
    directory = ROOT / case["directory"]
    if not (directory / "cases.json").is_file():
        first = ROOT / campaign["cases"][0]["directory"] / "cases.json"
        first_review = _json(first)["reviewed_case"]
        written_case = ROOT / first_review["file"]
        if _sha(written_case) != first_review["sha256"]:
            raise ValueError("the initial job's written case has changed")
        request.prepare_runs(bundle, written_case, case_index=index)
    manifest, _, _ = qd.load_case(directory)
    frozen = _json(bundle / case["manifest"])
    reviewed = manifest["reviewed_case"]
    if _sha(ROOT / reviewed["file"]) != reviewed["sha256"]:
        raise ValueError("the reviewed written case has changed")
    if manifest.get("source_case_sha256") != case["sha256"]:
        raise ValueError("the prepared manifest names another frozen source case")
    predecessor_sources = [source for job in report["jobs"] for source in job.get("sources", [])]
    evidence = {
        "schema": "ascella-cohort-prerequisite-admission-v1",
        "campaign_sha256": _sha(bundle / "campaign.json"),
        "case": case["name"],
        "source_case_sha256": case["sha256"],
        "reviewed_case": reviewed,
        "decision": decision,
        "predecessor_sources": predecessor_sources,
        "analysis_source_sha256": report["analysis_source_sha256"],
    }
    receipt_path = directory / "prerequisite-admission.json"
    _retained(receipt_path, evidence)
    prerequisites = {"file": receipt_path.relative_to(ROOT).as_posix(), "sha256": _sha(receipt_path)}
    expected = {
        **frozen,
        "acquisition_admission": "ready" if index == 0 else "awaiting-prerequisites",
        "reviewed_case": reviewed,
        "source_case_sha256": case["sha256"],
    }
    promoted = {**expected, "acquisition_admission": "ready", "prerequisites": prerequisites}
    if manifest not in (expected, promoted):
        raise ValueError("the prepared case differs from its exact reviewed admission transition")
    if manifest != promoted:
        qd.write_json(directory / "cases.json", promoted)
    _manifest_for_run(promoted, frozen, ROOT)
    preflight_name = "dark" if index == 0 else case["name"]
    preflight = _json(bundle / f"{preflight_name}-read-only-plan.json")
    promoted_hash = _sha(directory / "cases.json")

    def verify(planned: dict[str, Any]) -> None:
        for source in predecessor_sources:
            if _sha(ROOT / source["ref"]) != source["sha256"]:
                raise qd.PlatformError("predecessor evidence changed during admission")
        if (
            _sha(ROOT / reviewed["file"]) != reviewed["sha256"]
            or _sha(receipt_path) != prerequisites["sha256"]
            or planned["cases_sha256"] != promoted_hash
            or body_projection(planned["body"]) != body_projection(preflight["body"])
            or planned["credit_ceiling"] > request.JOB_CREDIT_CEILING
            or planned["admitted_statuses"] != ["available"]
        ):
            raise qd.PlatformError("the fresh request differs from the reviewed case, prerequisites or body")

    return qd.submit(directory, "qpu:ascella", approval, request.JOB_CREDIT_CEILING, 300, 1, verify=verify)


def main() -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--bundle", type=Path, default=ROOT / request.BUNDLE)
    parser.add_argument("--submit-next", action="store_true")
    parser.add_argument("--approval")
    args = parser.parse_args()
    try:
        if args.submit_next:
            if not args.approval or not args.approval.strip():
                parser.error("--submit-next requires the user's --approval text")
            record = submit_next(args.bundle, args.approval)
            print(f"submitted {record['case']}: {record['job_id']}")
        else:
            index, decision, _ = next_acquisition(args.bundle)
            print(request.json_text({"case_index": index, **decision}), end="")
    except (ValueError, qd.PlatformError) as error:
        raise SystemExit(str(error)) from None
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
