"""scripts/approved_run.sh: plan, check and submit with identical flags, retrying a refused submit."""

from __future__ import annotations

import os
import stat
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/approved_run.sh"

# Stands in for "$PYTHON live_run.py ARGS": a plan writes a run directory and prints its audit record; a submit
# consumes the approval (writing MARKER, an envelope family's per-attempt name or the plain one) unless REFUSALS
# names more refusals than the calls file holds, and then records
# `submission.complete` as COMPLETE and exits SUBMIT_EXIT. "$PYTHON -c CODE RECORD" reads that completion state.
FAKE = """#!/bin/sh
if [ "$1" = -c ]; then grep -q '"complete": true' "$3"; exit $?; fi
shift
echo "$*" >> "$CALLS"
n=$(wc -l < "$CALLS")
run="run$n"
mkdir -p "$run"
echo "{\\"n\\": $n}" > "$run/record.json"
case " $* " in
*" --submit "*)
  approved=$(echo "$*" | sed -n 's/.*--approved-record \\([^ ]*\\).*/\\1/p')
  submits=$(grep -c -- '--submit' "$CALLS")
  if [ "$submits" -gt "${REFUSALS:-0}" ]; then
    : > "$approved/${MARKER:-approval-consumed.json}"
    echo "{\\"submission\\": {\\"complete\\": ${COMPLETE:-true}}}" > "$run/record.json"
    echo "audit record: $run"
    exit "${SUBMIT_EXIT:-0}"
  fi
  echo approval_required
  ;;
esac
echo "audit record: $run"
"""


def _expect(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _run(
    tmp_path: Path,
    *args: str,
    refusals: int = 0,
    complete: str = "true",
    submit_exit: int = 0,
    log: str | None = None,
    marker: str = "approval-consumed.json",
) -> tuple[subprocess.CompletedProcess[str], list[str]]:
    (tmp_path / "gororoba_quantum").mkdir(exist_ok=True)
    fake = tmp_path / "fake_python"
    fake.write_text(FAKE)
    fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
    calls = tmp_path / "calls"
    env = os.environ | {
        "PYTHON": str(fake),
        "CALLS": str(calls),
        "REFUSALS": str(refusals),
        "COMPLETE": complete,
        "SUBMIT_EXIT": str(submit_exit),
        "MARKER": marker,
    }
    done = subprocess.run(
        ["sh", str(SCRIPT), "--log", log or str(tmp_path / "log"), *args],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    return done, calls.read_text().splitlines() if calls.exists() else []


def test_plans_checks_and_submits_with_identical_flags(tmp_path: Path) -> None:
    done, calls = _run(tmp_path, "--check", 'test -f "$RUN/record.json"', "--", "--groups", "g", "--shots", "8")
    _expect(done.returncode == 0, done.stdout + done.stderr)
    _expect(len(calls) == 2 and calls[0] == "--groups g --shots 8", f"calls {calls}")
    _expect(
        calls[1].startswith("--groups g --shots 8 --submit --approved-record run1 --approved-record-sha256 "), calls[1]
    )
    _expect("submitted dry_run=run1" in done.stdout, done.stdout)


def test_a_failed_check_sends_nothing(tmp_path: Path) -> None:
    done, calls = _run(tmp_path, "--check", "false", "--", "--groups", "g")
    _expect(done.returncode == 1 and len(calls) == 1, f"{done.returncode} {calls}")


def test_a_refused_submit_plans_again(tmp_path: Path) -> None:
    done, calls = _run(tmp_path, "--", "--groups", "g", refusals=1)
    _expect(done.returncode == 0 and len(calls) == 4, f"{done.returncode} {calls}")
    _expect("--approved-record run3 " in calls[3], calls[3])


def test_refusals_past_the_attempts_exit_3(tmp_path: Path) -> None:
    done, calls = _run(tmp_path, "--attempts", "2", "--", "--groups", "g", refusals=5)
    _expect(done.returncode == 3 and len(calls) == 4, f"{done.returncode} {calls}")


@pytest.mark.parametrize("flag", ["--submit", "--approved-record", "--approved-record-sha256"])
def test_submit_flags_belong_to_the_runner(tmp_path: Path, flag: str) -> None:
    done, calls = _run(tmp_path, "--", "--groups", "g", flag)
    _expect(done.returncode == 2 and not calls, f"{done.returncode} {calls}")


@pytest.mark.parametrize(("complete", "submit_exit"), [("false", 0), ("true", 1)])
def test_a_consumed_approval_with_a_failed_submission_exits_4(tmp_path: Path, complete: str, submit_exit: int) -> None:
    done, calls = _run(tmp_path, "--", "--groups", "g", complete=complete, submit_exit=submit_exit)
    _expect(done.returncode == 4 and len(calls) == 2, f"{done.returncode} {calls}")
    _expect("approval consumed" in done.stdout, done.stdout)


def test_a_relative_log_directory_resolves_from_the_repository_root(tmp_path: Path) -> None:
    done, _ = _run(tmp_path, "--", "--groups", "g", log="logs")
    _expect(done.returncode == 0 and (tmp_path / "logs" / "dry-1.log").is_file(), done.stdout + done.stderr)


@pytest.mark.parametrize(("complete", "returncode"), [("true", 0), ("false", 4)])
def test_an_envelope_attempt_marker_ends_the_run_after_one_submit(
    tmp_path: Path, complete: str, returncode: int
) -> None:
    done, calls = _run(tmp_path, "--", "--groups", "g", complete=complete, marker="approval-consumed-attempt-1.json")
    _expect(done.returncode == returncode and len(calls) == 2, f"{done.returncode} {calls} {done.stdout}")
    _expect(sum("--submit" in call for call in calls) == 1, f"{calls}")
