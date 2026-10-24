"""Contract for ci/audit_report.py: a failing gate is listed with every claim citing it, and a passing gate never."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import audit_report

SHARD = audit_report.SHARD_SCHEMA
RECORDS: list[dict[str, Any]] = [
    {"schema": SHARD, "gates": [{"name": "core-1", "status": 0}, {"name": "core-2", "status": 1}]},
    {"schema": SHARD, "gates": [{"name": "core-3", "status": 124}]},
    # The merged cost file of ci/merge_gate_timings.py: gates maps names to costs.
    {"schema": "gororoba-gate-measured-v1", "gates": {"core-4": {"seconds": 1.0}}},
]
STATE = {
    "claims": [
        {"id": "claim-a", "gates": {"core-2": "replay"}},
        {"id": "claim-b", "gates": {"core-1": "replay", "core-2": "regression"}},
        {"id": "claim-c"},
    ]
}


def test_failing_gates_come_from_every_shard() -> None:
    if audit_report.failing_gates(RECORDS) != ["core-2", "core-3"]:
        raise AssertionError(audit_report.failing_gates(RECORDS))


def test_report_names_citing_claims_and_failed_jobs() -> None:
    body = audit_report.report("URL", ["rocq-replay"], RECORDS, STATE)
    expected = (
        "| `core-2` | `claim-a`, `claim-b` |",
        "| `core-3` | none |",
        "Failing jobs: `rocq-replay`.",
    )
    missing = [line for line in expected if line not in body]
    if missing or "core-1" in body or "core-4" in body:
        raise AssertionError(body)


def test_an_unloadable_registry_still_lists_the_failing_gates(tmp_path: Path) -> None:
    broken = tmp_path / "research_state.json"
    broken.write_text("<<<<<<< conflict", encoding="utf-8")
    shard = tmp_path / "gate-timings.json"
    shard.write_text(json.dumps(RECORDS[0]), encoding="utf-8")
    truncated = tmp_path / "qi-timings.json"
    truncated.write_text('{"schema": ', encoding="utf-8")
    if audit_report.load(broken) is not None or audit_report.load(tmp_path / "absent.json") is not None:
        raise AssertionError("an unreadable file loaded")
    body = audit_report.report("URL", [], [RECORDS[0]], None)
    if "| `core-2` | unavailable: docs/state/research_state.json did not load |" not in body:
        raise AssertionError(body)
    if audit_report.main(["--run-url", "URL", "--research-state", str(broken), str(shard), str(truncated)]) != 0:
        raise AssertionError("main failed on an unreadable input")
