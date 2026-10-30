"""Reconcile the frozen Tuna runtime and canonical analysis encodings without rewriting either."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from qi_tuna_destination_one_analysis import BATCHES, PROPOSAL, ROOT, analyze, digest, json_bytes, timestamp

RUNTIME_ANALYSIS = "analysis.json"
CANONICAL_ANALYSIS = "analysis-canonical.json"
STATE = "execution-state.json"
RUNNER = "scripts/qi_tuna_destination_one_run.py"
RUNTIME_WRITER = "scripts/qi_platform.py"
SUBMISSION_HELPER = "scripts/qi_platform_submission_deadline.py"
VALID_OUTCOMES = {
    "objective established within scope",
    "specified alternative supported",
    "inconclusive within budget",
}


def runtime_bytes(value: Any) -> bytes:
    """Match the frozen qi_platform._write_json call's exact UTF-8 output."""
    return (json.dumps(value, indent=1) + "\n").encode("utf-8")


def validate_sources(campaign: dict[str, Any]) -> dict[str, str]:
    """Bind the runtime writer, call site, analyzer and every declared producer input."""
    producers = campaign["producer_inputs"]
    if not isinstance(producers, dict) or not {RUNNER, RUNTIME_WRITER, SUBMISSION_HELPER} <= producers.keys():
        raise ValueError("frozen campaign lacks runtime writer, runner or submission helper identities")
    analysis = campaign["analysis_contract"]
    sources = dict(producers)
    for record in (analysis, analysis["mathematical_note"]):
        name, expected = record["file"], record["sha256"]
        if name in sources and sources[name] != expected:
            raise ValueError("campaign assigns conflicting hashes to one source")
        sources[name] = expected
    for name, expected in sources.items():
        if (
            not isinstance(name, str)
            or Path(name).is_absolute()
            or ".." in Path(name).parts
            or not isinstance(expected, str)
            or not re.fullmatch(r"[0-9a-f]{64}", expected)
        ):
            raise ValueError("frozen source identities require repository-relative paths and SHA-256 values")
        source = ROOT / name
        if not source.resolve().is_relative_to(ROOT.resolve()) or digest(source) != expected:
            raise ValueError(f"frozen source or writer bytes differ: {name}")
    return sources


def validate_complete_state(run: Path, report: dict[str, Any]) -> None:
    """Require the executor's completed state to match all acquired completion records."""
    state = json.loads((run / STATE).read_bytes())
    expected_keys = {"schema", "phase", "completed", "active_batch", "analysis_outcome", "observed_utc"}
    if (
        not isinstance(state, dict)
        or set(state) != expected_keys
        or state.get("schema") != "qi-tuna-destination-one-state-v1"
        or state.get("phase") != "complete"
        or state.get("active_batch") != BATCHES[-1]
        or state.get("analysis_outcome") != report["outcome"]
        or not isinstance(state.get("completed"), list)
        or len(state["completed"]) != 3
    ):
        raise ValueError("executor state does not describe the complete frozen three-job endpoint")
    expected = [json.loads((run / name / "completion-admission.json").read_bytes()) for name in BATCHES]
    if json_bytes(state["completed"]) != json_bytes(expected):
        raise ValueError("executor completed entries differ from the acquired per-case completion receipts")
    completed_at = timestamp(state["observed_utc"])
    if any(completed_at < timestamp(row["collected_utc"]) for row in report["jobs"]):
        raise ValueError("executor completion observation precedes a required collection")


def receipt(run: Path, proposal: Path = PROPOSAL) -> dict[str, Any]:
    """Validate both exact serializations against a fresh full frozen-analysis replay."""
    campaign = json.loads((run / "sequence-plan.json").read_bytes())
    sources = validate_sources(campaign)
    report = analyze(run, proposal)
    if (
        report.get("schema") != "qi-destination-one-predictable-response-analysis-v1"
        or report.get("outcome") not in VALID_OUTCOMES
        or [row["batch"] for row in report.get("jobs", [])] != list(BATCHES)
        or report.get("contract", {}).get("jobs") != 3
        or report.get("attribution_status") != "unresolved"
        or report.get("physical_continuation_admitted") is not False
        or report.get("retry_authorized") is not False
    ):
        raise ValueError("fresh frozen analyzer refuses the valid complete three-job endpoint")
    validate_complete_state(run, report)
    runtime = (run / RUNTIME_ANALYSIS).read_bytes()
    canonical = (run / CANONICAL_ANALYSIS).read_bytes()
    if runtime != runtime_bytes(report):
        raise ValueError("runtime analysis differs from the frozen indent-one insertion-order byte contract")
    if canonical != json_bytes(report):
        raise ValueError("canonical analysis differs from the frozen indent-two sorted-key byte contract")
    runtime_object, canonical_object = json.loads(runtime), json.loads(canonical)
    if json_bytes(runtime_object) != json_bytes(report) or json_bytes(canonical_object) != json_bytes(report):
        raise ValueError("analysis objects or JSON number representations differ from fresh replay")
    inputs = dict(report["inputs"])
    for name in (RUNTIME_ANALYSIS, CANONICAL_ANALYSIS, STATE):
        inputs[name] = digest(run / name)
    return {
        "schema": "qi-tuna-destination-analysis-encoding-receipt-v1",
        "outcome": report["outcome"],
        "jobs": [{"batch": row["batch"], "job": row["job"], "batch_job": row["batch_job"]} for row in report["jobs"]],
        "inputs": inputs,
        "frozen_sources": sources,
        "runtime_encoding": {
            "file": RUNTIME_ANALYSIS,
            "indent": 1,
            "sort_keys": False,
            "newline": "LF",
            "charset": "UTF-8",
            "writer": RUNTIME_WRITER,
            "call_site": RUNNER,
        },
        "canonical_encoding": {
            "file": CANONICAL_ANALYSIS,
            "indent": 2,
            "sort_keys": True,
            "newline": "LF",
            "charset": "UTF-8",
            "writer": campaign["analysis_contract"]["file"],
        },
        "parsed_objects_and_numbers_identical": True,
        "decision_identical": True,
        "attribution_status": "unresolved",
        "physical_continuation_admitted": False,
        "retry_authorized": False,
        "boundary": (
            "Encoding reconciliation only. Both retained analyses replay the same frozen complete acquisition; "
            "the runtime and canonical files keep their distinct exact byte contracts and scientific scope."
        ),
        "receipt_producer_sha256": digest(Path(__file__)),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    parser.add_argument("--proposal", type=Path, default=PROPOSAL)
    operation = parser.add_mutually_exclusive_group(required=True)
    operation.add_argument("--out", type=Path)
    operation.add_argument("--check", type=Path)
    arguments = parser.parse_args()
    content = json_bytes(receipt(arguments.run, arguments.proposal))
    if arguments.check:
        if arguments.check.read_bytes() != content:
            raise SystemExit("retained analysis-encoding receipt differs from exact replay")
    else:
        with arguments.out.open("xb") as destination:
            destination.write(content)
    print("Runtime and canonical analyses replay identical decisions under both frozen byte contracts.")


if __name__ == "__main__":
    main()
