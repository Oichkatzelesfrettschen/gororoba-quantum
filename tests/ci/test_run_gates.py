"""Contract for ci/run_gates.py: unique gate names, every CPU, keep-going past a launch failure,
one child worker by default, --device, --max-seconds, --gates, and the requires field with --requires.
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

import gate_inputs
import pytest
import run_gates

pytestmark = pytest.mark.audit

ROOT = Path(__file__).resolve().parents[2]
LISTED: list[dict[str, Any]] = [
    {"name": "fast", "cwd": ".", "cmd": "true", "seconds": 1.0},
    {"name": "slow", "cwd": ".", "cmd": "true", "seconds": 9.0},
    {"name": "unmeasured", "cwd": ".", "cmd": "true"},
    {"name": "full-only", "cwd": ".", "cmd": "true", "seconds": 1.0, "tier": "full"},
]
# A qi gate runs in every lane, on its replay path where the stack is absent;
# --requires qi keeps only the qi gates and makes each take its live path.
QI: list[dict[str, Any]] = [
    {"name": "qi-pr", "cwd": ".", "cmd": 'test "${GOROROBA_QI_REQUIRED:-0}" = 1', "requires": ["qi"]},
    {"name": "qi-full", "cwd": ".", "cmd": "true", "requires": ["qi"], "tier": "full"},
]
# A singular gate guards its live path on GOROROBA_SINGULAR_REQUIRED, which only
# --requires singular exports.
SINGULAR: list[dict[str, Any]] = [
    {
        "name": "singular-full",
        "cwd": ".",
        "cmd": 'test "${GOROROBA_SINGULAR_REQUIRED:-0}" = 1',
        "requires": ["singular"],
        "tier": "full",
    },
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


def test_gate_names_are_unique() -> None:
    # run_gates selects and reports gates by name, so two gates of one name make a shard result ambiguous.
    names = [gate["name"] for gate in json.loads((ROOT / "ci/gates.json").read_text())["gates"]]
    duplicates = sorted({name for name in names if names.count(name) > 1})
    if duplicates:
        raise AssertionError(f"ci/gates.json names more than one gate {', '.join(duplicates)}")


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
    if status != 0 or f"gates in shard 0/1 on {device}" not in text:
        raise AssertionError(f"{flag} did not give every gate GOROROBA_AER_DEVICE={device}:\n{text}")


@pytest.mark.parametrize(
    ("tier", "limit", "wanted"), (("pr", 5.0, ["fast"]), ("pr", None, ["fast", "slow", "unmeasured"]))
)
def test_select_by_tier_and_measured_seconds(root: Path, tier: str, limit: float | None, wanted: list[str]) -> None:
    manifest(root, LISTED)
    names = [gate["name"] for gate in run_gates.select(root, tier, limit)]
    if names != wanted:
        raise AssertionError(f"select({tier}, {limit}) chose {names}, not {wanted}")


@pytest.mark.parametrize(
    ("tier", "requires", "wanted"),
    (
        ("pr", None, ["fast", "slow", "unmeasured", "qi-pr"]),
        ("pr", "qi", ["qi-pr"]),
        ("full", "qi", ["qi-pr", "qi-full"]),
    ),
)
def test_select_by_requires(root: Path, tier: str, requires: str | None, wanted: list[str]) -> None:
    manifest(root, LISTED + QI)
    names = [gate["name"] for gate in run_gates.select(root, tier, None, requires)]
    if names != wanted:
        raise AssertionError(f"select({tier}, requires={requires}) chose {names}, not {wanted}")


@pytest.mark.parametrize(("flag", "expected"), (([], 1), (["--requires", "qi"], 0)))
def test_requires_sets_the_live_path(root: Path, flag: list[str], expected: int) -> None:
    manifest(root, LISTED + QI)
    with runner(root, GOROROBA_QI_REQUIRED=None) as output:
        status = run_gates.main(["--tier", "pr", *flag])
    if status != expected:
        raise AssertionError(f"{flag or 'no flag'} gave GOROROBA_QI_REQUIRED wrongly:\n{output.getvalue()}")


@pytest.mark.parametrize(("flag", "expected"), (([], 1), (["--requires", "singular"], 0)))
def test_requires_singular_sets_the_live_path(root: Path, flag: list[str], expected: int) -> None:
    manifest(root, LISTED + QI + SINGULAR)
    with runner(root, GOROROBA_SINGULAR_REQUIRED=None) as output:
        status = run_gates.main(["--tier", "full", *flag])
    if status != expected:
        raise AssertionError(f"{flag or 'no flag'} gave GOROROBA_SINGULAR_REQUIRED wrongly:\n{output.getvalue()}")


def test_select_requires_singular_keeps_only_singular_gates(root: Path) -> None:
    manifest(root, LISTED + QI + SINGULAR)
    names = [gate["name"] for gate in run_gates.select(root, "full", None, "singular")]
    if names != ["singular-full"]:
        raise AssertionError(f"select(full, requires=singular) chose {names}")


def test_gates_selects_by_name(root: Path) -> None:
    # --gates keeps the named gates of the tier and ignores a name the tree lacks.
    manifest(root, LISTED + QI)
    with runner(root) as output:
        run_gates.main(["--tier", "pr", "--list", "--gates", "qi-pr,fast,absent"])
    names = [line.split("\t", 1)[0] for line in output.getvalue().splitlines()]
    if sorted(names) != ["fast", "qi-pr"]:
        raise AssertionError(f"--gates qi-pr,fast,absent listed {names}")


@pytest.mark.parametrize("malformed", ([], ["qi", "qi"], ["kaggle"], "qi", [1]))
def test_malformed_requires_is_refused(root: Path, malformed: Any) -> None:
    manifest(root, [{"name": "malformed", "cwd": ".", "cmd": "true", "requires": malformed}])
    with pytest.raises(SystemExit):
        run_gates.select(root, "pr")


def test_repository_manifest_selects() -> None:
    run_gates.select(ROOT, "full")


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


def test_only_a_changed_files_run_decides_admission(root: Path, tmp_path: Path) -> None:
    # A --changed-files run is the merge verdict, so pins.resolve_current
    # refuses a $PYTHON that differs from the pins there and only there.
    manifest(root, [{"name": "fast", "cwd": ".", "cmd": "true", "seconds": 1.0}])
    changed = tmp_path / "changed"
    changed.write_bytes(b"")
    seen: list[bool] = []

    def record(_environment: Any, current: str, _root: Path, admission: bool = False) -> tuple[str, str]:
        seen.append(admission)
        return current, "recorded"

    with (
        patch.object(run_gates.pins, "resolve_current", record),
        patch.object(run_gates.gate_inputs, "affected_full", lambda _root, _gates, _changed: set()),
        runner(root) as output,
    ):
        statuses = [run_gates.main([]), run_gates.main(["--changed-files", str(changed)])]
    if statuses != [0, 0] or seen != [False, True]:
        raise AssertionError(f"admission passed as {seen} with statuses {statuses}:\n{output.getvalue()}")


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


def test_within_budget_takes_cheapest_first_and_names_the_rest() -> None:
    gates = [
        {"name": "slow", "seconds": 50.0, "cmd": "x"},
        {"name": "fast", "seconds": 1.0, "cmd": "x"},
        {"name": "mid", "seconds": 10.0, "cmd": "x"},
    ]
    selected, pending = run_gates.within_budget(gates, 12.0)
    if [gate["name"] for gate in selected] != ["fast", "mid"]:
        raise AssertionError(f"budget selected {[gate['name'] for gate in selected]}")
    if [gate["name"] for gate in pending] != ["slow"]:
        raise AssertionError(f"budget deferred {[gate['name'] for gate in pending]}")
    selected, pending = run_gates.within_budget(gates, 0.5)
    if selected or len(pending) != 3:
        raise AssertionError("a budget below every gate defers every gate")


def test_report_pending_writes_the_step_summary(tmp_path: Path) -> None:
    summary = tmp_path / "summary.md"
    with patch.dict(os.environ, {"GITHUB_STEP_SUMMARY": str(summary)}):
        run_gates.report_pending([{"name": "slow", "seconds": 50.0, "cmd": "sleep 50"}])
    text = summary.read_text()
    if "PENDING slow" not in text or "1 reached gates pending" not in text:
        raise AssertionError(text)


def test_cited_gates_reads_every_claim(tmp_path: Path) -> None:
    registry = tmp_path / "research_state.json"
    registry.write_text(
        json.dumps({"claims": [{"gates": {"core-1": {}, "core-2": {}}}, {"gates": {"core-2": {}}}, {}]})
    )
    if run_gates.cited_gates(registry) != {"core-1", "core-2"}:
        raise AssertionError(run_gates.cited_gates(registry))


def test_repository_claims_cite_existing_gates() -> None:
    names = {gate["name"] for gate in run_gates.select(ROOT, "full")}
    expanded = {gate["name"] for gate in gate_inputs.expand_cases(ROOT, run_gates.select(ROOT, "full"))}
    missing = sorted(run_gates.cited_gates(ROOT / "docs/state/research_state.json") - names - expanded)
    if missing:
        raise AssertionError(f"claims cite gates the manifest lacks: {missing}")


def test_audit_lane_gates_leave_the_pull_request_selection() -> None:
    gates = json.loads((ROOT / "ci/gates.json").read_text())["gates"]
    audit_only = [gate["name"] for gate in gates if gate.get("lane") == "audit"]
    if "core-615" not in audit_only:
        raise AssertionError("the behavioral suite gate carries lane audit")
    if any(gate.get("lane") not in (None, "audit") for gate in gates):
        raise AssertionError("lane takes only the value audit")
