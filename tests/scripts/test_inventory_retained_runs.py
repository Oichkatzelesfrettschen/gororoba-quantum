"""Unexecuted cancellations have a distinct, audit-bound retention channel."""

import copy
import hashlib
import json
from pathlib import Path

import inventory_retained_runs as inventory
import pytest


def test_unexecuted_cancellation_requires_matching_observation() -> None:
    observed = {
        "job_id": "cancelled",
        "status": "CANCELLED",
        "final_qpu_charge_seconds": 0,
        "timestamps": {"running": None},
    }
    snapshot = {"jobs": [observed]}
    entry = {**copy.deepcopy(observed), "run": None, "provenance": "unexecuted_cancellation"}
    audit = {"inventory_sha256": "bound", "jobs": [entry]}
    if inventory.unexecuted_cancellations(snapshot, audit, "bound") != {"cancelled"}:
        raise AssertionError("the cancellation is missing from the audit channel")
    for field, value in (("status", "DONE"), ("final_qpu_charge_seconds", 1), ("timestamps", {})):
        changed = copy.deepcopy(snapshot)
        changed["jobs"][0][field] = value
        with pytest.raises(ValueError, match="evidence differs"):
            inventory.unexecuted_cancellations(changed, audit, "bound")
    with pytest.raises(ValueError, match="different inventory"):
        inventory.unexecuted_cancellations(snapshot, audit, "different")


def test_inventory_accounts_for_cancelled_jobs_without_a_run(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    live = tmp_path / "results/live"
    live.mkdir(parents=True)
    observed = {
        "job_id": "cancelled",
        "status": "CANCELLED",
        "final_qpu_charge_seconds": 0,
        "timestamps": {"running": None},
    }
    snapshot = {
        "observed_at": "2026-10-29T00:00:00Z",
        "instance_crn_hash": "0123456789ab",
        "jobs": [observed],
    }
    inventory_path = live / "qpu-job-inventory.json"
    inventory_path.write_text(json.dumps(snapshot))
    audit = {
        "inventory_sha256": hashlib.sha256(inventory_path.read_bytes()).hexdigest(),
        "jobs": [{**copy.deepcopy(observed), "run": None, "provenance": "unexecuted_cancellation"}],
    }
    (live / "qpu-job-retention-audit.json").write_text(json.dumps(audit))
    monkeypatch.setattr(inventory, "ROOT", tmp_path)
    result = inventory.inventory()
    if result["counts"]["unexecuted_cancellation_jobs"] != 1 or result["unexecuted_cancellation_job_ids"] != [
        "cancelled"
    ]:
        raise AssertionError("the service job must enter the cancellation channel")
