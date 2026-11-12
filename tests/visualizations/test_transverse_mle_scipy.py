"""Runs the independent SciPy comparison of the workbench's transverse maximum-likelihood estimator."""

from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).with_name("check_transverse_mle.py")
NODE = shutil.which("node")


@pytest.mark.skipif(importlib.util.find_spec("scipy") is None, reason="SciPy is not installed")
@pytest.mark.skipif(NODE is None, reason="Node is not installed")
def test_transverse_mle_matches_scipy_on_deterministic_grid() -> None:
    done = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True, check=False, timeout=300)
    if done.returncode != 0:
        raise AssertionError(f"check exited {done.returncode}: {done.stderr[-2000:]}")
    report = json.loads(done.stdout)
    if report["passed"] is not True or report["cases"] < 100 or report["maximum_log_likelihood_disagreement"] > 1e-8:
        raise AssertionError(f"unexpected report {report}")
