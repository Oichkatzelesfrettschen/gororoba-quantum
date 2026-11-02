"""Contract for ci/run_gates.py: unique gate names, every CPU, keep-going past a launch failure,
one child worker by default, --device, --max-seconds, --gates, and the requires field.
"""

from __future__ import annotations

import contextlib
import io
import json
import os
import sys
from collections.abc import Iterator
from pathlib import Path
from typing import Any
from unittest.mock import patch

import manifest as manifests
import pytest
import run_gates

pytestmark = pytest.mark.audit

ROOT = Path(__file__).resolve().parents[2]
LISTED: list[dict[str, Any]] = [
    {"name": "fast", "cwd": ".", "cmd": "true", "seconds": 1.0},
    {"name": "slow", "cwd": ".", "cmd": "true", "seconds": 9.0},
    {"name": "unmeasured", "cwd": ".", "cmd": "true"},
]
# A qi gate runs in every lane, on its replay path where the stack is absent, and takes its live path when
# the caller exports GOROROBA_QI_REQUIRED.
QI: list[dict[str, Any]] = [
    {"name": "qi-pr", "cwd": ".", "cmd": 'test "${GOROROBA_QI_REQUIRED:-0}" = 1', "requires": ["qi"]},
]


@pytest.fixture
def root(tmp_path: Path) -> Path:
    (tmp_path / "ci").mkdir()
    return tmp_path


def manifest(root: Path, gates: list[dict[str, Any]]) -> None:
    (root / "ci/gates.json").write_text(json.dumps({"gates": gates}))


@contextlib.contextmanager
def runner(root: Path, **variables: str | None) -> Iterator[io.StringIO]:
    """run_gates.main against ROOT=root with each variable set, or removed when None."""
    output = io.StringIO()
    with patch.object(run_gates, "ROOT", root), patch.dict(os.environ), contextlib.redirect_stdout(output):
        for name, value in variables.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value
        yield output


def test_pool_uses_every_cpu() -> None:
    expected = run_gates.parallel.available_cpus()
    if run_gates._cpus() != expected:
        raise AssertionError(f"gate pool uses {run_gates._cpus()} workers, not every available CPU ({expected})")


@pytest.mark.parametrize("capacity", (1, 2, 4))
@pytest.mark.parametrize("override", (None, "3"))
def test_launch_failure_keeps_going(root: Path, capacity: int, override: str | None) -> None:
    workers = min(capacity, int(override or "1"))
    manifest(
        root,
        [
            {"name": "missing-directory", "cwd": "absent", "cmd": "exit 0"},
            {
                "name": "retained-success",
                "cwd": ".",
                "cmd": f'test "$GOROROBA_WORKERS" = {workers} && printf "success survived\\n"',
            },
        ],
    )
    with patch.object(run_gates, "_cpus", return_value=capacity), runner(root, GOROROBA_WORKERS=override) as output:
        status = run_gates.main([])
    text = output.getvalue()
    if status != 1 or "FAIL missing-directory" not in text or "PASS retained-success" not in text:
        raise AssertionError(f"a launch failure stopped the shard or lost a passing gate:\n{text}")
    if "could not start" not in text or "1 passed, 1 failed of 2" not in text:
        raise AssertionError(f"the launch diagnostic or the keep-going denominator is missing:\n{text}")


@pytest.mark.parametrize(("flag", "device"), (([], "CPU"), (["--device", "GPU"], "GPU")))
def test_device_reaches_every_gate(root: Path, flag: list[str], device: str) -> None:
    manifest(root, [{"name": "device", "cwd": ".", "cmd": f'test "${{GOROROBA_AER_DEVICE:-CPU}}" = {device}'}])
    with runner(root, GOROROBA_AER_DEVICE=None) as output:
        status = run_gates.main(flag)
    text = output.getvalue()
    if status != 0 or f"gates on {device}" not in text:
        raise AssertionError(f"{flag} did not give every gate GOROROBA_AER_DEVICE={device}:\n{text}")


@pytest.mark.parametrize(("limit", "wanted"), ((5.0, ["fast"]), (None, ["fast", "slow", "unmeasured"])))
def test_select_by_measured_seconds(root: Path, limit: float | None, wanted: list[str]) -> None:
    manifest(root, LISTED)
    names = [gate["name"] for gate in run_gates.select(root, limit)]
    if names != wanted:
        raise AssertionError(f"select({limit}) chose {names}, not {wanted}")


@pytest.mark.parametrize(("exported", "expected"), ((True, 0), (False, 1)))
def test_requires_names_the_variable_that_forces_the_live_path(root: Path, exported: bool, expected: int) -> None:
    manifest(root, QI)
    with runner(root, GOROROBA_QI_REQUIRED="1" if exported else None) as output:
        status = run_gates.main([])
    if status != expected:
        raise AssertionError(f"GOROROBA_QI_REQUIRED exported={exported} gave status {status}:\n{output.getvalue()}")


def test_gates_selects_by_name(root: Path) -> None:
    # --gates keeps the named gates and ignores a name the tree lacks.
    manifest(root, LISTED + QI)
    with runner(root) as output:
        run_gates.main(["--list", "--gates", "qi-pr,fast,absent"])
    names = [line.split("\t", 1)[0] for line in output.getvalue().splitlines()]
    if sorted(names) != ["fast", "qi-pr"]:
        raise AssertionError(f"--gates qi-pr,fast,absent listed {names}")


@pytest.mark.parametrize("malformed", ([], ["qi", "qi"], ["kaggle"], "qi", [1]))
def test_malformed_requires_is_refused(root: Path, malformed: Any) -> None:
    manifest(root, [{"name": "malformed", "cwd": ".", "cmd": "true", "requires": malformed}])
    with pytest.raises(SystemExit):
        run_gates.select(root)


def test_repository_manifest_selects() -> None:
    run_gates.select(ROOT)


def test_historical_selection_needs_no_current_runtime(root: Path, tmp_path: Path) -> None:
    # A selection of historical gates alone runs under the replay interpreter
    # even where no interpreter holds the current runtime's pins.
    marker = tmp_path / "ran"
    manifest(root, [{"name": "historical", "cwd": ".", "cmd": f"touch {marker}", "runtime": "qiskit-2.5"}])

    def unresolvable(*_arguments: Any) -> tuple[None, str]:
        raise AssertionError("a historical-only selection resolved the current runtime")

    with (
        patch.object(run_gates.pins, "resolve_current", unresolvable),
        patch.object(run_gates.pins, "mismatches", lambda _python, _pins, _patches=None: []),
        runner(root, REPLAY_PYTHON=os.environ.get("PYTHON") or "python3", GOROROBA_PINS_REQUIRED=None) as output,
    ):
        status = run_gates.main([])
    if status != 0 or not marker.exists():
        raise AssertionError(f"a historical-only selection returned {status}:\n{output.getvalue()}")


def test_unresolved_runtime_runs_no_gate(root: Path, tmp_path: Path) -> None:
    # A selection whose historical runtime no interpreter holds exits 2
    # before any gate runs, rather than failing each of its gates with 127.
    marker = tmp_path / "ran"
    manifest(
        root,
        [
            {"name": "current", "cwd": ".", "cmd": f"touch {marker}"},
            {"name": "historical", "cwd": ".", "cmd": "true", "runtime": "qiskit-2.5"},
        ],
    )
    differing = ["qiskit 2.6.0 (pin 2.5.2)"]
    with (
        patch.object(run_gates.pins, "mismatches", lambda _python, _pins, _patches=None: list(differing)),
        runner(root, REPLAY_PYTHON=None, XDG_CACHE_HOME=str(tmp_path / "cache"), GOROROBA_PINS_REQUIRED=None) as output,
    ):
        status = run_gates.main([])
    text = output.getvalue()
    if status != 2 or marker.exists() or "ci/build_host_envs.sh" not in text:
        raise AssertionError(f"an unresolved runtime returned {status} or ran a gate:\n{text}")


def test_numeric_stack_reports_the_selected_openblas_core() -> None:
    environment = run_gates.environment_for(None) | {"OPENBLAS_CORETYPE": "Prescott"}
    report = json.loads(run_gates.numeric_stack(sys.executable, environment))
    if set(report) != {"avx512f", "cpu", "numpy_dispatch", "openblas"} or not report["openblas"]:
        raise AssertionError(report)
    # OpenBLAS maps the Prescott request onto its oldest x86-64 kernel set, which every runner supports.
    if {item["core"] for item in report["openblas"]} != {"Katmai"}:
        raise AssertionError(report["openblas"])


def test_numeric_stack_names_a_failed_probe() -> None:
    if not run_gates.numeric_stack("/nonexistent/python", dict(os.environ)).startswith("unavailable ("):
        raise AssertionError("a missing interpreter reports unavailable")


def test_repository_claims_cite_existing_gates() -> None:
    names = set(manifests.commands(ROOT))
    expanded = {gate["name"] for gate in manifests.expand_cases(ROOT, manifests.gates(ROOT))}
    claims = json.loads((ROOT / "docs/state/research_state.json").read_text())["claims"]
    cited = {name for claim in claims for name in claim.get("gates", {})}
    missing = sorted(cited - names - expanded)
    if missing:
        raise AssertionError(f"claims cite gates the manifest lacks: {missing}")
