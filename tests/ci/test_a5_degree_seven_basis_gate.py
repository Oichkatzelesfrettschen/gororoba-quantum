"""The degree-seven basis gate skips optional Singular and propagates required replay failures."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import manifest
import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize("required,status,expected_calls", [(None, 73, 0), ("0", 73, 0), ("1", 73, 1), ("1", 0, 4)])
def test_basis_gate_skips_optional_tools_and_propagates_required_results(
    required: str | None, status: int, expected_calls: int, tmp_path: Path
) -> None:
    """The shell command must skip before interpreter entry or propagate its required verifier result."""
    shell = shutil.which("sh")
    if shell is None:
        pytest.skip("the gate command requires a POSIX shell")
    tools = tmp_path / "tools"
    tools.mkdir()
    timeout = tools / "timeout"
    timeout.write_text('#!/bin/sh\nshift 3\nexec "$@"\n')
    timeout.chmod(0o755)
    interpreter = tmp_path / "controlled-interpreter"
    interpreter.write_text(
        "#!/bin/sh\nprintf 'called\\n' >> \"$CALL_LOG\"\n"
        'printf \'%s\\n\' "$@" >> "$ARGUMENT_LOG"\nexit "$VERIFIER_STATUS"\n'
    )
    interpreter.chmod(0o755)
    calls = tmp_path / "calls"
    arguments = tmp_path / "arguments"
    environment = dict(
        os.environ,
        PATH=str(tools),
        PYTHON=str(interpreter),
        CALL_LOG=str(calls),
        ARGUMENT_LOG=str(arguments),
        VERIFIER_STATUS=str(status),
    )
    environment.pop("GOROROBA_SINGULAR_REQUIRED", None)
    if required is not None:
        environment["GOROROBA_SINGULAR_REQUIRED"] = required
    command = manifest.commands(ROOT)["core-a5-e8-degree-seven-bases"]
    result = subprocess.run(
        [shell, "-c", command], cwd=ROOT, env=environment, capture_output=True, text=True, timeout=5
    )
    actual_calls = calls.read_text().splitlines() if calls.exists() else []
    if len(actual_calls) != expected_calls:
        raise AssertionError((actual_calls, result))
    actual_arguments = arguments.read_text().splitlines() if arguments.exists() else []
    targets = ("e8nm-p32009", "e8nm-p32029", "e8np-p32009", "e8np-p32029")
    ladder = "docs/evidence/a5-exceptional-fibers/monomial-ladder"
    expected_arguments = [
        argument
        for target in targets[:expected_calls]
        for argument in (
            "-B",
            "-W",
            "error",
            f"{ladder}/e8_target_basis_verify.py",
            f"{ladder}/target-records/{target}-d7-basis.json",
        )
    ]
    if actual_arguments != expected_arguments:
        raise AssertionError(actual_arguments)
    if required != "1":
        # A skip exits with the skip status of ci/run_gates.py after its reason line.
        if result.returncode != 77 or not result.stdout.strip().splitlines()[-1].startswith("skipped:"):
            raise AssertionError(result)
    elif result.returncode != status:
        raise AssertionError(result)
