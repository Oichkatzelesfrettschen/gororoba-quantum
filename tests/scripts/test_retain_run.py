"""scripts/retain_run.sh: one command observes the run's instance, rewrites its audit and appends each register."""

from __future__ import annotations

import os
import stat
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]

# Stands in for "$PYTHON SCRIPT ARGS": records the script and its arguments, prints the observed inventory's path
# (INVENTORY) for the observation, writes --out for the audit, and fails the acquisition when FAIL_ADD is set.
FAKE = """#!/bin/sh
echo "$*" >> "$CALLS"
case "$1" in
scripts/observe_qpu_job_inventory.py) : > "$INVENTORY"; echo "1 settled jobs, 1 s charged; wrote $INVENTORY" ;;
scripts/reconcile_qpu_inventory.py) [ "$2" != --retention-preflight ] || exit "${ACTOR_STATUS:-0}"; echo audit > "$5" ;;
scripts/research_state.py) [ "$2" != --add-acquisition ] || [ -z "${FAIL_ADD:-}" ] || exit 1 ;;
esac
"""


def _retain(
    tmp_path: Path, inventory: str, fail_add: str = "", *, actor: bool = False, actor_status: str = "0"
) -> tuple[subprocess.CompletedProcess[str], list[str]]:
    run = tmp_path / "results/live/2026-10-28T000644.379196Z"
    run.mkdir(parents=True)
    if not actor:
        (run / "collect.json").write_text("[]")
    fake = tmp_path / "fake_python"
    fake.write_text(FAKE)
    fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
    calls = tmp_path / "calls"
    env = os.environ | {
        "PYTHON": str(fake),
        "CALLS": str(calls),
        "INVENTORY": inventory,
        "FAIL_ADD": fail_add,
        "ACTOR_STATUS": actor_status,
    }
    result = subprocess.run(
        ["sh", str(ROOT / "scripts/retain_run.sh"), "results/live/2026-10-28T000644.379196Z/", "acq", "fam", "why?"],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    return result, [line.split()[0] for line in calls.read_text().splitlines()] if calls.exists() else []


@pytest.mark.parametrize(
    ("inventory", "audit", "registers"),
    [
        (
            "results/live/qpu-job-inventory.json",
            "results/live/qpu-job-retention-audit.json",
            ["scripts/compare_submitted_circuits.py", "scripts/ghost_calibrations.py"],
        ),
        (
            "results/live/qpu-job-inventory.f59f9992321c.json",
            "results/live/qpu-job-retention-audit.f59f9992321c.json",
            [],
        ),
    ],
)
def test_retention_appends_every_register_of_the_run_instance(
    tmp_path: Path, inventory: str, audit: str, registers: list[str]
) -> None:
    result, steps = _retain(tmp_path, inventory)
    if result.returncode != 0:
        raise AssertionError(result.stdout + result.stderr)
    expected = [
        "scripts/reconcile_qpu_inventory.py",
        "ci/seed_provenance.py",
        "scripts/observe_qpu_job_inventory.py",
        "scripts/reconcile_qpu_inventory.py",
        *registers,
        "scripts/research_state.py",
    ]
    if steps != expected or (tmp_path / audit).read_text() != "audit\n" or (tmp_path / f"{audit}.new").exists():
        raise AssertionError(f"{steps}")


def test_a_refused_acquisition_fails_the_retention(tmp_path: Path) -> None:
    result, steps = _retain(tmp_path, "results/live/qpu-job-inventory.f59f9992321c.json", fail_add="1")
    if (
        result.returncode != 1
        or steps[-1] != "scripts/research_state.py"
        or steps.count("scripts/research_state.py") != 1
    ):
        raise AssertionError(f"{result.returncode} {steps}")


def test_actor_retention_checks_external_receipt_before_inventory(tmp_path: Path) -> None:
    result, steps = _retain(tmp_path, "results/live/qpu-job-inventory.f59f9992321c.json", actor=True)
    if result.returncode != 0 or steps[:3] != [
        "scripts/reconcile_qpu_inventory.py",
        "ci/seed_provenance.py",
        "scripts/observe_qpu_job_inventory.py",
    ]:
        raise AssertionError(f"{result.returncode} {steps}")


def test_invalid_actor_receipt_refuses_before_inventory(tmp_path: Path) -> None:
    result, steps = _retain(tmp_path, "results/live/qpu-job-inventory.f59f9992321c.json", actor=True, actor_status="1")
    if result.returncode != 1 or steps != ["scripts/reconcile_qpu_inventory.py"]:
        raise AssertionError(f"{result.returncode} {steps}")


def test_actor_preflight_cannot_be_bypassed_with_legacy_collection(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import json
    import sys

    import reconcile_qpu_inventory as audit

    (tmp_path / "record.json").write_text(json.dumps({"schema_version": "readout-actor-run-v1"}))
    (tmp_path / "collect.json").write_text("[]")
    monkeypatch.setattr(audit, "ROOT", tmp_path)
    monkeypatch.setattr(sys, "argv", ["reconcile_qpu_inventory.py", "--retention-preflight", str(tmp_path)])
    with pytest.raises(SystemExit) as failure:
        audit.main()
    if failure.value.code != 1:
        raise AssertionError("actor preflight must require its external anchor")


@pytest.mark.parametrize(
    "record",
    [
        {"schema_version": "readout-actor-run-v2", "family_configuration": {"name": "readout-actor"}},
        {"schema_version": 7, "family_configuration": {"name": "readout-actor"}},
        {"schema_version": "readout-actor-run-v1", "family_configuration": {"name": "other"}},
        {"schema_version": 7, "reviewed_record_sha256": "actor-identity"},
        {"schema_version": "unknown"},
    ],
)
def test_unknown_or_inconsistent_record_refuses_legacy_fallback(tmp_path: Path, record: dict[str, object]) -> None:
    import json

    import reconcile_qpu_inventory as audit

    (tmp_path / "record.json").write_text(json.dumps(record))
    (tmp_path / "collect.json").write_text("[]")
    with pytest.raises(ValueError, match="unsupported or inconsistent"):
        audit.retention_family(tmp_path, allow_recovered=True)


def test_uncollected_actor_run_does_not_block_historical_failure_discovery(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import json

    import reconcile_qpu_inventory as audit

    run = tmp_path / "results/live/queued-actor"
    run.mkdir(parents=True)
    (run / "record.json").write_text(
        json.dumps(
            {
                "schema_version": "readout-actor-run-v1",
                "instance_sha256_12": "b" * 12,
                "submission": {"jobs": [{"job_id": "pending"}]},
            }
        )
    )
    monkeypatch.setattr(audit, "ROOT", tmp_path)
    if audit.failed_collections("b" * 12, "a" * 12):
        raise AssertionError("a queued uncollected actor job cannot become retained failure evidence")
    from decimal import Decimal

    with pytest.raises(ValueError, match="no collection"):
        audit.failed_row({"job_id": "pending"}, None, Decimal(1))


def test_failure_summary_includes_actor_and_legacy_charges() -> None:
    from decimal import Decimal

    import reconcile_qpu_inventory as audit

    rows = [
        {"provenance": "failed_collection", "final_qpu_charge_seconds": 1.25},
        {"provenance": "failed_actor_collection", "final_qpu_charge_seconds": 2.25},
        {"provenance": "registered_actor_collection", "final_qpu_charge_seconds": 9},
    ]
    if audit.failure_summary(rows) != (2, Decimal("3.50")):
        raise AssertionError("actor and legacy failed jobs must both enter failed-charge totals")
