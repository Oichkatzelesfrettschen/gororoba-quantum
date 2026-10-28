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
scripts/reconcile_qpu_inventory.py) echo audit > "$5" ;;
scripts/research_state.py) [ "$2" != --add-acquisition ] || [ -z "${FAIL_ADD:-}" ] || exit 1 ;;
esac
"""


def _retain(tmp_path: Path, inventory: str, fail_add: str = "") -> tuple[subprocess.CompletedProcess[str], list[str]]:
    run = tmp_path / "results/live/2026-10-28T000644.379196Z"
    run.mkdir(parents=True)
    (run / "collect.json").write_text("[]")
    fake = tmp_path / "fake_python"
    fake.write_text(FAKE)
    fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
    calls = tmp_path / "calls"
    env = os.environ | {"PYTHON": str(fake), "CALLS": str(calls), "INVENTORY": inventory, "FAIL_ADD": fail_add}
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
        "ci/seed_provenance.py",
        "scripts/observe_qpu_job_inventory.py",
        "scripts/reconcile_qpu_inventory.py",
        *registers,
        "scripts/research_state.py",
        "scripts/research_state.py",
    ]
    if steps != expected or (tmp_path / audit).read_text() != "audit\n" or (tmp_path / f"{audit}.new").exists():
        raise AssertionError(f"{steps}")


def test_a_refused_acquisition_stops_before_the_views(tmp_path: Path) -> None:
    result, steps = _retain(tmp_path, "results/live/qpu-job-inventory.f59f9992321c.json", fail_add="1")
    if (
        result.returncode != 1
        or steps[-1] != "scripts/research_state.py"
        or steps.count("scripts/research_state.py") != 1
    ):
        raise AssertionError(f"{result.returncode} {steps}")
