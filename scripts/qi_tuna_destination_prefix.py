"""Replay descriptive nominal-zero data while preserving the incomplete case's refusal."""

from __future__ import annotations

import argparse
import datetime as dt
import json
from decimal import Decimal
from pathlib import Path
from typing import Any

from qi_tuna_readout_destination_analysis import (
    ANCILLAS,
    BATCHES,
    PROPOSAL,
    ROOT,
    SHOTS,
    analyze,
    digest,
    ordered_map,
    timestamp,
    validate_approval,
    validate_batch,
)

CAMPAIGN_SHA256 = "53eb49080573b876545b5301b195ee06127625653266fbb64b98a60823e07a76"


def validate_recovery(run: Path, rows: list[dict[str, Any]], state: dict[str, Any]) -> dict[str, str]:
    """Bind read-only recovery to the stopped executor and the collected third identity."""
    intent_path = run / "read-only-recovery-intent.json"
    receipt_path = run / "read-only-recovery-receipt.json"
    intent = json.loads(intent_path.read_text())
    receipt = json.loads(receipt_path.read_text())
    last = rows[-1]
    completion_path = run / last["batch"] / "completion-admission.json"
    if (
        intent.get("schema") != "qi-read-only-recovery-v1"
        or receipt.get("schema") != "qi-read-only-recovery-v1"
        or type(intent.get("job")) is not int
        or type(receipt.get("job")) is not int
        or intent["job"] != last["job"]
        or intent.get("case") != last["batch"]
        or intent.get("provider_resource_creation_authorized") is not False
        or receipt.get("provider_resource_creation_authorized") is not False
        or intent.get("original_execution_state_sha256") != digest(run / "execution-state.json")
        or receipt.get("automatic_executor_resumed") is not False
        or receipt.get("status") != "collected"
        or receipt.get("completion_admission_sha256") != digest(completion_path)
        or any(receipt.get(key) != value for key, value in intent.items())
    ):
        raise ValueError("recovery receipt differs from the stopped executor, read-only scope or third job")
    started = timestamp(intent["started_utc"])
    completed = timestamp(receipt["completed_utc"])
    collected = timestamp(json.loads((completion_path.parent / "results.json").read_text())["collected_utc"])
    if not timestamp(state["observed_utc"]) <= started <= completed or not (
        max(started, timestamp(last["finished_utc"])) <= collected <= completed
    ):
        raise ValueError("recovery chronology contradicts stop, completion or collection")
    automatic = [json.loads((run / row["batch"] / "completion-admission.json").read_text()) for row in rows[:2]]
    if state["completed"] != automatic or state["active_batch"] != last["batch"]:
        raise ValueError("stopped executor does not preserve exactly the first two automatic completions")
    return {path.relative_to(run).as_posix(): digest(path) for path in (intent_path, receipt_path)}


def validate_readbacks(run: Path, rows: list[dict[str, Any]]) -> dict[str, str]:
    """Check stored source identity without inferring the served analog program."""
    provenance = {}
    for row in rows:
        directory = run / row["batch"]
        manifest = json.loads((directory / "cases.json").read_text())
        source = manifest["circuits"][0]
        path = directory / "stored-source-observation.json"
        record = json.loads(path.read_text())
        observations = record.get("jobs")
        if (
            record.get("schema") != "qi-stored-source-observation-v1"
            or not isinstance(observations, list)
            or len(observations) != 1
        ):
            raise ValueError("stored-source receipt schema or job scope differs")
        observed = observations[0]
        if not isinstance(observed, dict) or not isinstance(observed.get("response_field_names"), list):
            raise ValueError("stored-source observation must identify response fields in an object")
        expected = digest(directory / source["file"])
        if (
            type(observed.get("job")) is not int
            or observed["job"] != row["job"]
            or observed.get("file") != source["file"]
            or observed.get("source_matches") is not True
            or observed.get("local_source_sha256") != expected
            or observed.get("stored_source_sha256") != expected
            or not isinstance(observed.get("compile_properties"), dict)
            or not isinstance(observed.get("compile_stage"), str)
            or "content" not in observed.get("response_field_names", [])
            or timestamp(record["observed_utc"]) < timestamp(row["created_utc"])
        ):
            raise ValueError("stored-source observation differs from the acquired job or approved source")
        provenance[path.relative_to(run).as_posix()] = digest(path)
    return provenance


def replay(run: Path) -> dict[str, Any]:
    """Validate the acquired prefix and return counts without a statistical acceptance decision."""
    if digest(run / "sequence-plan.json") != CAMPAIGN_SHA256:
        raise ValueError("descriptive replay requires the approved campaign")
    primary = analyze(run)
    if primary != json.loads((run / "analysis.json").read_text()):
        raise ValueError("retained primary refusal differs from frozen replay")
    if primary["outcome"] != "implementation route unavailable":
        raise ValueError("prefix description requires the retained incomplete-case outcome")
    state = json.loads((run / "execution-state.json").read_text())
    if state["phase"] != "stopped" or state["error_type"] != "TimeoutError":
        raise ValueError("prefix description requires the recorded request-deadline stop")
    submitted = [name for name in BATCHES if (run / name / "submission.json").exists()]
    if submitted != list(BATCHES[:3]):
        raise ValueError("description requires exactly the three nominal-zero submissions")
    campaign = json.loads((run / "sequence-plan.json").read_text())
    bindings, approval = validate_approval(run, campaign)
    rows = ordered_map(
        validate_batch,
        [(run, PROPOSAL, batch, campaign, bindings, approval) for batch in campaign["batches"][:3]],
    )
    if len({row["job"] for row in rows}) != 3 or len({row["batch_job"] for row in rows}) != 3:
        raise ValueError("prefix job or batch identities repeat")
    for before, after in zip(rows, rows[1:], strict=False):
        if timestamp(after["created_utc"]) < timestamp(before["finished_utc"]) + dt.timedelta(seconds=30):
            raise ValueError("prefix violates completion plus the frozen pause")
    recovery_inputs = validate_recovery(run, rows, state)
    source_inputs = validate_readbacks(run, rows)
    comparisons = []
    for index, qubit in enumerate(ANCILLAS):
        before, rotated, after = [row["joint_counts"][index] for row in rows]
        comparisons.append(
            {
                "ancilla_qubit": qubit,
                "joint_cell_order": ["00", "01", "10", "11"],
                "joint_counts_before_rotated_after": [before, rotated, after],
                "early_one_counts": [counts[2] + counts[3] for counts in (before, rotated, after)],
                "terminal_one_counts": [counts[1] + counts[3] for counts in (before, rotated, after)],
                "response_numerators": [2 * rotated[cell] - before[cell] - after[cell] for cell in range(4)],
                "response_denominator": 2 * SHOTS,
                "baseline_numerators": [after[cell] - before[cell] for cell in range(4)],
                "baseline_denominator": SHOTS,
            }
        )
    return {
        "schema": "qi-nominal-zero-prefix-description-v1",
        "primary_case_outcome": primary["outcome"],
        "scope": "Posthoc description of the complete nominal-zero prefix; the six-job endpoint remains unavailable.",
        "statistical_acceptance_admitted": False,
        "causal_attribution": "unresolved",
        "shots_total": 3 * SHOTS,
        "execution_seconds_decimal": str(sum((Decimal(row["execution_seconds_decimal"]) for row in rows), Decimal(0))),
        "jobs": rows,
        "comparisons": comparisons,
        "inputs": {
            **recovery_inputs,
            **source_inputs,
            **{
                name: digest(run / name)
                for name in ("analysis.json", "execution-state.json", "read-only-recovery-receipt.json")
            },
        },
        "producer": {"file": Path(__file__).relative_to(ROOT).as_posix(), "sha256": digest(Path(__file__))},
        "frozen_analyzer_sha256": primary["analyzer_sha256"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    operation = parser.add_mutually_exclusive_group(required=True)
    operation.add_argument("--out", type=Path)
    operation.add_argument("--check", type=Path)
    arguments = parser.parse_args()
    content = json.dumps(replay(arguments.run), indent=2, sort_keys=True) + "\n"
    if arguments.check:
        if arguments.check.read_text() != content:
            raise SystemExit("retained descriptive prefix differs from exact replay")
    else:
        with arguments.out.open("x") as output:
            output.write(content)
    print("descriptive prefix replays; the complete-case refusal remains in force")


if __name__ == "__main__":
    main()
