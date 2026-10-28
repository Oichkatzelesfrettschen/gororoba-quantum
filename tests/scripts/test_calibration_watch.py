"""scripts/calibration_watch.py and scripts/wait_calibration.sh: detect a new published calibration and stop."""

from __future__ import annotations

import os
import stat
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import calibration_watch  # noqa: E402

# Stands in for "$PYTHON scripts/calibration_watch.py ARGS": each call takes the next exit status from STATUSES
# (space separated, the last one repeating) and prints a line naming the call.
FAKE = """#!/bin/sh
n=$(( $(cat "$CALLS" 2>/dev/null || echo 0) + 1 ))
echo "$n" > "$CALLS"
set -- $STATUSES
while [ "$n" -gt 1 ] && [ $# -gt 1 ]; do shift; n=$((n - 1)); done
echo "poll $(cat "$CALLS") status $1"
exit "$1"
"""


def _expect(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _props(stamp: str, t1: dict[int, float], t2: dict[int, float]) -> SimpleNamespace:
    return SimpleNamespace(
        last_update_date=datetime.fromisoformat(stamp), t1=lambda q: t1[q] * 1e-6, t2=lambda q: t2[q] * 1e-6
    )


def test_qubit_list_reads_indices_and_ranges() -> None:
    _expect(calibration_watch.qubit_list("3,0-2,9") == [0, 1, 2, 3, 9], "comma list with an inclusive range")


def test_a_stamp_change_alone_counts_without_qubits() -> None:
    base = calibration_watch.reading(_props("2026-10-27T16:09:17-07:00", {}, {}), [])
    now = calibration_watch.reading(_props("2026-10-27T16:36:38-07:00", {}, {}), [])
    _expect(calibration_watch.decide(base, now, 0)[0], "a new stamp is a change when no qubits are named")
    _expect(not calibration_watch.decide(base, base, 0)[0], "the same stamp is no change")


def test_named_qubits_need_both_t1_and_t2_to_move() -> None:
    qubits = [0, 1, 2, 3]
    base = calibration_watch.reading(
        _props("2026-10-27T16:09:17-07:00", dict.fromkeys(qubits, 250.0), dict.fromkeys(qubits, 160.0)), qubits
    )
    stamp_only = calibration_watch.reading(
        _props("2026-10-27T16:36:38-07:00", dict.fromkeys(qubits, 250.0), dict.fromkeys(qubits, 160.0)), qubits
    )
    t1_only = calibration_watch.reading(
        _props("2026-10-27T16:36:38-07:00", dict.fromkeys(qubits, 240.0), dict.fromkeys(qubits, 160.0)), qubits
    )
    refreshed = calibration_watch.reading(
        _props("2026-10-27T16:36:38-07:00", {0: 240.0, 1: 241.0, 2: 250.0, 3: 250.0}, dict.fromkeys(qubits, 150.0)),
        qubits,
    )
    _expect(not calibration_watch.decide(base, stamp_only, 2)[0], "a republished stamp with stale T1/T2 waits")
    _expect(not calibration_watch.decide(base, t1_only, 2)[0], "T2 must move too")
    changed, summary = calibration_watch.decide(base, refreshed, 2)
    _expect(changed and "t1_moved=2 t2_moved=4 n=4" in summary, summary)
    _expect(not calibration_watch.decide(base, refreshed, 3)[0], "two moved T1 values fall short of three")


def _wait(tmp_path: Path, statuses: str, *args: str) -> subprocess.CompletedProcess[str]:
    fake = tmp_path / "fake_python"
    fake.write_text(FAKE)
    fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
    env = os.environ | {"PYTHON": str(fake), "CALLS": str(tmp_path / "calls"), "STATUSES": statuses}
    return subprocess.run(
        ["sh", str(ROOT / "scripts/wait_calibration.sh"), "--interval", "0", *args, "--", "ibm_kingston"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )


@pytest.mark.parametrize(
    ("statuses", "deadline", "code", "line"),
    [
        ("1 1 0", "60", 0, "poll 3 status 0"),
        ("1 3 1 0", "60", 0, "poll 4 status 0"),
        ("1", "0", 2, "deadline: poll 1 status 1"),
        ("1 3 3 3 3 3", "60", 3, "poll 6 status 3"),
        ("2", "60", 2, "poll 1 status 2"),
    ],
)
def test_wait_loop_exits_on_change_deadline_failures_and_usage(
    tmp_path: Path, statuses: str, deadline: str, code: int, line: str
) -> None:
    result = _wait(tmp_path, statuses, "--deadline", deadline, "--log", str(tmp_path / "log"))
    _expect(result.returncode == code, f"{statuses}: exit {result.returncode}\n{result.stdout}{result.stderr}")
    _expect(line in result.stdout + result.stderr, f"{statuses}: {result.stdout}{result.stderr}")
