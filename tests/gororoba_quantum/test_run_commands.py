"""run_commands reports each unit's status in argument order and fails when any unit fails."""

from __future__ import annotations

import pytest

import run_commands


def test_statuses_print_in_argument_order(capsys: pytest.CaptureFixture[str]) -> None:
    status = run_commands.main(["echo first", "exit 0", "echo second"])
    lines = capsys.readouterr().out.splitlines()
    if status != 0:
        raise AssertionError(f"all units exited 0 but the status is {status}")
    if lines != [
        "run_commands: exit 0: echo first",
        "first",
        "run_commands: exit 0: exit 0",
        "run_commands: exit 0: echo second",
        "second",
    ]:
        raise AssertionError(f"unexpected report {lines}")


def test_a_failing_unit_fails_the_run_and_keeps_its_stderr(capsys: pytest.CaptureFixture[str]) -> None:
    status = run_commands.main(["echo ok", "echo bad >&2; exit 3"])
    out = capsys.readouterr().out
    if status != 1:
        raise AssertionError(f"a unit exited 3 but the status is {status}")
    if "run_commands: exit 3: echo bad >&2; exit 3\nbad\n" not in out:
        raise AssertionError(f"the failing unit's status or stderr is missing: {out!r}")


def test_no_command_is_an_error() -> None:
    with pytest.raises(SystemExit):
        run_commands.main([])
