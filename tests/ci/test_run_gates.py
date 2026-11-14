"""Contract for ci/run_gates.py: unique gate names, every CPU, keep-going past a launch failure,
one child worker by default, --device, --max-seconds, --gates, and the requires field.
"""

from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
import subprocess
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
    if "could not start" not in text or "1 passed, 0 skipped, 1 failed of 2" not in text:
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


SKIPPING: list[dict[str, Any]] = [
    {"name": "passes", "cwd": ".", "cmd": "true"},
    {
        "name": "skips",
        "cwd": ".",
        "cmd": 'if [ "${GOROROBA_SINGULAR_REQUIRED:-0}" = 1 ]; then true; else echo "skipped: absent"; exit 77; fi',
        "requires": ["singular"],
    },
]


def test_a_skipped_gate_is_reported_and_counted_apart_from_the_passes(root: Path, tmp_path: Path) -> None:
    manifest(root, SKIPPING)
    timings = tmp_path / "timings.json"
    with runner(root, GOROROBA_SINGULAR_REQUIRED=None) as output:
        status = run_gates.main(["--timings", str(timings)])
    text = output.getvalue()
    wanted = ("SKIP skips", "PASS passes", "1 passed, 1 skipped, 0 failed of 2", "skipped, replay not run: skips")
    if status != 0 or any(part not in text for part in wanted) or "PASS skips" in text or "skipped: absent" not in text:
        raise AssertionError(f"a skip was not reported apart from the passes (status {status}):\n{text}")
    verdicts = {row["name"]: row["verdict"] for row in json.loads(timings.read_text())["gates"]}
    if verdicts != {"passes": "PASS", "skips": "SKIP"}:
        raise AssertionError(f"the timings record holds {verdicts}")


def test_a_run_that_only_skips_exits_with_the_skip_status(root: Path) -> None:
    manifest(root, SKIPPING[1:])
    with runner(root, GOROROBA_SINGULAR_REQUIRED=None) as output:
        status = run_gates.main([])
    if status != run_gates.SKIP_STATUS or "0 passed, 1 skipped, 0 failed of 1" not in output.getvalue():
        raise AssertionError(f"an all-skip run returned {status}:\n{output.getvalue()}")
    manifest(root, [SKIPPING[1], {"name": "fails", "cwd": ".", "cmd": "false"}])
    with runner(root, GOROROBA_SINGULAR_REQUIRED=None) as output:
        status = run_gates.main([])
    if status != 1:
        raise AssertionError(f"a run with a skip and a failure returned {status}:\n{output.getvalue()}")


def test_the_required_variable_turns_the_skip_into_the_live_path(root: Path) -> None:
    manifest(root, SKIPPING)
    with runner(root, GOROROBA_SINGULAR_REQUIRED="1") as output:
        status = run_gates.main([])
    if status != 0 or "2 passed, 0 skipped, 0 failed of 2" not in output.getvalue():
        raise AssertionError(f"the live path did not pass:\n{output.getvalue()}")


def test_the_skip_status_from_a_gate_without_requires_is_a_failure(root: Path) -> None:
    manifest(root, [{"name": "undeclared", "cwd": ".", "cmd": "exit 77"}])
    with runner(root) as output:
        status = run_gates.main([])
    if status != 1 or "FAIL undeclared" not in output.getvalue():
        raise AssertionError(f"status 77 without requires did not fail:\n{output.getvalue()}")


@pytest.mark.parametrize(
    "command",
    (
        "exit 77",
        'echo "no reason here"; exit 77',
        'echo "skipped: early"; echo "later line"; exit 77',
        'echo "skipped:"; exit 77',
        'echo "skipped:   "; exit 77',
    ),
)
def test_the_skip_status_without_a_closing_reason_line_is_a_failure(root: Path, tmp_path: Path, command: str) -> None:
    manifest(root, [{"name": "silent", "cwd": ".", "cmd": command, "requires": ["singular"]}])
    timings = tmp_path / "timings.json"
    with runner(root) as output:
        status = run_gates.main(["--timings", str(timings)])
    text = output.getvalue()
    verdicts = [row["verdict"] for row in json.loads(timings.read_text())["gates"]]
    if (
        status != 1
        or "FAIL silent" not in text
        or "0 passed, 0 skipped, 1 failed of 1" not in text
        or verdicts != ["FAIL"]
    ):
        raise AssertionError(f"status 77 without a closing skipped: line did not fail (status {status}):\n{text}")


def test_a_skip_under_the_required_variable_is_a_failure(root: Path) -> None:
    # The guard of this gate ignores the variable; the runner still refuses the skip once the caller requires the tool.
    manifest(root, [{"name": "ignores", "cwd": ".", "cmd": 'echo "skipped: x"; exit 77', "requires": ["singular"]}])
    with runner(root, GOROROBA_SINGULAR_REQUIRED="1") as output:
        required = run_gates.main([])
    with runner(root, GOROROBA_SINGULAR_REQUIRED=None, GOROROBA_QI_REQUIRED="1") as other:
        unrelated = run_gates.main([])
    if required != 1 or "FAIL ignores" not in output.getvalue():
        raise AssertionError(f"a skip under GOROROBA_SINGULAR_REQUIRED=1 did not fail:\n{output.getvalue()}")
    if unrelated != run_gates.SKIP_STATUS or "SKIP ignores" not in other.getvalue():
        raise AssertionError(f"another toolchain's variable changed the verdict:\n{other.getvalue()}")


def test_every_repository_gate_that_prints_a_skip_line_exits_with_the_skip_status() -> None:
    lacking = [
        gate["name"]
        for gate in run_gates.select(ROOT)
        if "skipped:" in gate["cmd"] and not ("; exit 77; fi" in gate["cmd"] and gate.get("requires"))
    ]
    if lacking:
        raise AssertionError(f"gates print a skip line and exit 0, which reads as a pass: {lacking}")


def test_gates_selects_by_name(root: Path) -> None:
    # --gates keeps the named gates and ignores a name the tree lacks.
    manifest(root, LISTED + QI)
    with runner(root) as output:
        run_gates.main(["--list", "--gates", "qi-pr,fast,absent"])
    names = [line.split("\t", 1)[0] for line in output.getvalue().splitlines()]
    if sorted(names) != ["fast", "qi-pr"]:
        raise AssertionError(f"--gates qi-pr,fast,absent listed {names}")


def math_fixture(root: Path, tmp_path: Path, flipped: bool = False) -> Path:
    """A gororoba-math checkout whose one source a ledger row of root binds, committed at the pin of root."""
    math = tmp_path / "math"
    (math / "rocq/quantum").mkdir(parents=True)
    source = b"Definition one := 1.\n"
    (math / "rocq/quantum/_RocqProject").write_text('-Q . ""\nCdOne.v\n', encoding="utf-8")
    (math / "rocq/quantum/CdOne.v").write_bytes(source + (b"x" if flipped else b""))
    identity = ["-c", "user.name=t", "-c", "user.email=t@example.invalid"]
    for arguments in (["init", "-q"], ["add", "."], [*identity, "commit", "-q", "-m", "fixture"]):
        subprocess.run(["git", "-C", str(math), *arguments], check=True, capture_output=True)
    pin = subprocess.run(
        ["git", "-C", str(math), "rev-parse", "HEAD"], check=True, capture_output=True, text=True
    ).stdout.strip()
    (root / "ci/gororoba_math.pin").write_text(pin + "\n", encoding="utf-8")
    (root / "docs/evidence/b").mkdir(parents=True)
    (root / "docs/evidence/b/source_hashes.sha256").write_text(
        f"{hashlib.sha256(source).hexdigest()}  proofs/CdOne.v\n", encoding="utf-8"
    )
    (root / "docs/state").mkdir()
    (root / "docs/state/research_state.json").write_text('{"claims": []}', encoding="utf-8")
    return math


MATH_GATE = [
    {
        "name": "ledger",
        "cwd": ".",
        "cmd": "sha256sum --strict -c docs/evidence/b/source_hashes.sha256",
        "requires": ["gororoba-math"],
    }
]


def test_a_gororoba_math_gate_skips_unset_and_fails_when_required(root: Path, tmp_path: Path) -> None:
    math_fixture(root, tmp_path)
    manifest(root, MATH_GATE)
    with runner(root, GOROROBA_MATH=None, GOROROBA_MATH_REQUIRED=None) as output:
        status = run_gates.main([])
    if status != run_gates.SKIP_STATUS or "SKIP ledger" not in output.getvalue():
        raise AssertionError(f"an unset GOROROBA_MATH did not skip (status {status}):\n{output.getvalue()}")
    with runner(root, GOROROBA_MATH=None, GOROROBA_MATH_REQUIRED="1") as output:
        status = run_gates.main([])
    if status != 1 or "FAIL ledger" not in output.getvalue():
        raise AssertionError(f"GOROROBA_MATH_REQUIRED=1 did not fail the skip (status {status}):\n{output.getvalue()}")


def test_a_gororoba_math_gate_reads_the_checkout_through_proofs(root: Path, tmp_path: Path) -> None:
    math = math_fixture(root, tmp_path)
    manifest(root, MATH_GATE)
    with runner(root, GOROROBA_MATH=str(math)) as output:
        status = run_gates.main([])
    if status != 0 or "PASS ledger" not in output.getvalue():
        raise AssertionError(f"the ledger did not verify against the checkout (status {status}):\n{output.getvalue()}")


def test_a_gororoba_math_gate_fails_on_a_source_that_differs_from_the_ledger(root: Path, tmp_path: Path) -> None:
    math = math_fixture(root, tmp_path, flipped=True)
    manifest(root, MATH_GATE)
    with runner(root, GOROROBA_MATH=str(math)) as output:
        status = run_gates.main([])
    if status != 1 or "differs from the retained digest" not in output.getvalue():
        raise AssertionError(f"a flipped byte passed (status {status}):\n{output.getvalue()}")


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
