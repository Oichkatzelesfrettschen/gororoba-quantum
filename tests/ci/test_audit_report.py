"""Contract for ci/audit_report.py: a failing gate is listed with every claim citing it, and a passing gate never."""

from __future__ import annotations

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
