"""The successor launcher of the Rees kcompare run against a fake Singular.

run_kcompare_v2.sh passes a cell only when Singular exits 0 and the log holds the verdict line with both known-bad
controls unequal and the terminal line. The fake prints those lines for the cell named by its script argument, or
fails in one way: it exits 7, it leaves out the verdict line, it exits 0 on a SIGTERM that it sends itself without the
terminal line (Singular exits 0 on SIGTERM), or it runs past the time limit, where timeout reports 124.
"""

from __future__ import annotations

import os
import shutil
import stat
import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "docs" / "evidence" / "a5-exceptional-fibers" / "working" / "runs"
DIRECTORY = RUNS / "e8-rees-fibers-v2-kcompare-p32009"
Launch = tuple[Callable[..., "subprocess.CompletedProcess[str]"], Path]
CELLS = ("e8-nm", "iso-nm")
RESULT = "KCMP RESULT cell {} equal 1 control_drop_unequal 1 control_added_unequal 1"

FAKE = """#!/bin/sh
case "$1" in --version) echo "Singular fake version 0"; exit 0;; esac
cell=$(basename "$3" .sing); cell=${cell#kcmp-}
mode=${FAKE_MODE:-pass}
[ "$mode" = fail_second ] && { [ "$cell" = iso-nm ] && mode=exit7 || mode=pass; }
case "$mode" in
  exit7) echo "partial"; exit 7;;
  no_result) echo "KCMP DONE cell $cell"; exit 0;;
  terminated)
    echo "KCMP RESULT cell $cell equal 1 control_drop_unequal 1 control_added_unequal 1"
    trap 'exit 0' TERM
    kill -TERM $$; sleep 5; exit 0;;
  runs_over)
    sleep 60 & child=$!
    trap 'kill $child; exit 0' TERM
    wait $child; exit 0;;
esac
echo "KCMP RESULT cell $cell equal 1 control_drop_unequal 1 control_added_unequal 1"
echo "KCMP DONE cell $cell"
"""


@pytest.fixture
def launch(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Launch:
    """Run the launcher from a copy of its directory with the fake as Singular; returns (result, directory)."""
    missing = [tool for tool in ("timeout", "sha256sum") if shutil.which(tool) is None]
    if missing:
        pytest.skip(f"the launcher needs GNU coreutils; absent: {', '.join(missing)}")
    if (
        not Path("/usr/bin/time").exists()
        or subprocess.run(["/usr/bin/time", "-v", "true"], capture_output=True, check=False).returncode
    ):
        pytest.skip("/usr/bin/time does not take -v (GNU time is not installed)")
    work = tmp_path / "run"
    work.mkdir()
    shutil.copy(DIRECTORY / "run_kcompare_v2.sh", work / "run_kcompare_v2.sh")
    for cell in CELLS:
        (work / f"kcmp-{cell}.sing").write_text("quit;\n", encoding="utf-8")
    fake = tmp_path / "Singular"
    fake.write_text(FAKE, encoding="utf-8")
    fake.chmod(fake.stat().st_mode | stat.S_IXUSR)

    def run(mode: str, limit: str = "30") -> subprocess.CompletedProcess[str]:
        monkeypatch.setenv("FAKE_MODE", mode)
        return subprocess.run(
            ["sh", str(work / "run_kcompare_v2.sh"), str(fake), limit, *CELLS],
            capture_output=True,
            text=True,
            check=False,
            timeout=120,
            env=dict(os.environ),
        )

    return run, work


def _require(condition: bool, message: object) -> None:
    if not condition:
        raise AssertionError(message)


def test_every_cell_that_prints_its_verdict_and_terminal_line_writes_the_done_marker(launch: Launch) -> None:
    run, work = launch
    done = run("pass")
    expected = "".join(f"CELL {cell} EXIT 0\n{RESULT.format(cell)}\nKCMP DONE cell {cell}\n" for cell in CELLS)
    _require(done.returncode == 0, done)
    _require((work / "kcompare.done").read_text(encoding="utf-8") == expected + "KCOMPARE ALL DONE\n", "done marker")
    _require(not (work / "kcompare.failed").exists(), "a failure marker beside a success")
    _require(all((work / f"kcmp-{cell}.time").exists() for cell in CELLS), "timing files")


def _assert_fails_at(run_result: subprocess.CompletedProcess[str], work: Path, cell: str, reason: str) -> None:
    _require(run_result.returncode == 1, run_result)
    _require(not (work / "kcompare.done").exists(), "a done marker after a failed cell")
    failed = (work / "kcompare.failed").read_text(encoding="utf-8").splitlines()
    _require(failed[-1].startswith(f"FAIL cell {cell}: {reason}"), failed)
    _require(not list(work.glob("*.part")), "a partial marker is left")


def test_a_singular_that_exits_nonzero_fails_its_cell(launch: Launch) -> None:
    run, work = launch
    _assert_fails_at(run("exit7"), work, "e8-nm", "Singular exited 7")
    _require("EXIT 7" in (work / "kcmp-e8-nm.log").read_text(encoding="utf-8"), "the exit status is in the log")
    _require(not (work / "kcmp-iso-nm.log").exists(), "the run went on past a failed cell")


def test_a_cell_without_its_verdict_line_fails_though_singular_exits_zero(launch: Launch) -> None:
    run, work = launch
    _assert_fails_at(run("no_result"), work, "e8-nm", "the verdict line")


def test_a_singular_that_exits_zero_on_sigterm_fails_for_the_missing_terminal_line(launch: Launch) -> None:
    run, work = launch
    _assert_fails_at(run("terminated"), work, "e8-nm", "the terminal line KCMP DONE is missing")
    log = (work / "kcmp-e8-nm.log").read_text(encoding="utf-8")
    _require("EXIT 0" in log and RESULT.format("e8-nm") in log, "Singular exited 0 after the TERM with its verdict")


def test_a_singular_that_runs_past_the_limit_fails_on_the_timeout_status(launch: Launch) -> None:
    run, work = launch
    _assert_fails_at(run("runs_over", limit="1"), work, "e8-nm", "Singular exited 124")


def test_a_later_failing_cell_keeps_the_earlier_cell_in_the_failure_marker(launch: Launch) -> None:
    run, work = launch
    _assert_fails_at(run("fail_second"), work, "iso-nm", "Singular exited 7")
    _require("CELL e8-nm EXIT 0" in (work / "kcompare.failed").read_text(encoding="utf-8"), "earlier cell lost")
