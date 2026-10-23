"""The unittest suites that live beside the code they check, run in place inside the behavioral suite.

Each suite imports its siblings by bare name from its own directory (two of them import a module
named ``probe``), so a suite runs with its directory first on sys.path, and afterwards every module
loaded from that directory leaves sys.modules; modules loaded from elsewhere (qiskit, numpy) stay,
since a C extension does not survive re-import. A suite whose docstring states an ``-O`` contract
also runs in a child interpreter under ``-O``, where ``assert`` is stripped. A suite that writes
beside itself runs from a byte-identical copy of its directory's modules under tmp_path, so a run
writes nothing inside the checkout.

A suite that a gate claim cites stays on its own gate (ci/gates.json, docs/state/research_state.json)
and is absent here, so each suite runs once: gororoba_quantum/test_heron_multiprogramming.py (core-256)
and docs/evidence/c881_exhaustive/check_replay.py (sources-188).
"""

from __future__ import annotations

import importlib.util
import io
import os
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

SUITES = (
    "docs/check_verify_sources.py",
    "docs/evidence/folding_proofs/check_compiler_gate.py",
    "docs/evidence/vacuum_endpoint_information/check_probe.py",
    "gororoba_quantum/check_et_rows.py",
    "results/live/test_folded_raw_analysis.py",
    "results/local_compute/mixed_pub_client/check_probe.py",
    "scripts/check_qi_platform_retention.py",
)
# The suite creates its fixtures in a temporary directory beside its own file.
COPIED = {"results/live/test_folded_raw_analysis.py": ("folded_raw_analysis.py",)}
OPTIMIZED = ("docs/evidence/vacuum_endpoint_information/check_probe.py",)


def _within(module: object, directory: Path) -> bool:
    location = getattr(module, "__file__", None)
    return isinstance(location, str) and Path(location).resolve().parent == directory


@pytest.mark.parametrize("suite", SUITES)
def test_unittest_suite(suite: str, tmp_path: Path) -> None:
    path = ROOT / suite
    if suite in COPIED:
        for sibling in (path.name, *COPIED[suite]):
            shutil.copyfile(path.parent / sibling, tmp_path / sibling)
        path = tmp_path / path.name
    directory = path.parent.resolve()
    saved_path = list(sys.path)
    before = set(sys.modules)
    sys.path.insert(0, str(directory))
    try:
        name = "unittest_suite_" + suite.replace("/", "_").removesuffix(".py")
        spec = importlib.util.spec_from_file_location(name, path)
        if spec is None or spec.loader is None:
            raise ImportError(f"cannot load {suite}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        tests = unittest.defaultTestLoader.loadTestsFromModule(module)
        stream = io.StringIO()
        result = unittest.TextTestRunner(stream=stream, verbosity=2).run(tests)
    finally:
        sys.path[:] = saved_path
        for key in set(sys.modules) - before:
            if key.startswith("unittest_suite_") or _within(sys.modules[key], directory):
                del sys.modules[key]
    if result.testsRun == 0:
        raise AssertionError(f"{suite} collected no tests")
    if not result.wasSuccessful():
        raise AssertionError(f"{suite} failed:\n{stream.getvalue()}")


@pytest.mark.parametrize("suite", OPTIMIZED)
def test_unittest_suite_under_optimize(suite: str) -> None:
    path = ROOT / suite
    completed = subprocess.run(
        [sys.executable, "-B", "-O", "-W", "error", path.name],
        cwd=path.parent,
        env={**os.environ, "PYTHONOPTIMIZE": "1"},
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise AssertionError(f"{suite} under -O exited {completed.returncode}:\n{completed.stderr}")
