"""Runs the JavaScript checks of the workbench's math module under Node."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).with_name("test_evidence_math.cjs")
NODE = shutil.which("node")


@pytest.mark.skipif(NODE is None, reason="Node is not installed")
def test_math_module_checks_pass_under_node() -> None:
    done = subprocess.run([str(NODE), str(SCRIPT)], capture_output=True, text=True, check=False, timeout=60)
    if done.returncode != 0:
        raise AssertionError(f"node exited {done.returncode}: {done.stderr[-2000:]}")
    summary = json.loads(done.stdout.strip().splitlines()[-1])
    if summary["status"] != "passed" or summary["checks"] != done.stdout.count("PASS "):
        raise AssertionError(f"unexpected summary {summary}")
    if summary["checks"] < 18:
        raise AssertionError(f"only {summary['checks']} checks ran")
