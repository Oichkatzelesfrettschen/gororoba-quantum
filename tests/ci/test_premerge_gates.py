"""Contract for ci/premerge_gates.py: a clean merge that breaks a record gate fails, a consistent merge
passes, a conflict stops, a strict run without a replay interpreter stops, and the base cache stores
passes only, hits on its key, misses on a changed key or a foreign entry, and reruns a base failure.
"""

from __future__ import annotations

import contextlib
import io
import json
import os
from pathlib import Path
from typing import Any
from unittest import mock

import pins
import premerge_gates
import pytest
import run_gates
from host_identity import KEY_PREFIXES, KEY_VARIABLES
from premerge_gates import CACHE_SCHEMA, DEFAULT_MAX_SECONDS, MERGE_IDENTITY, ROOT, git, premerge

pytestmark = pytest.mark.audit

RUNNER_FILES = (
    "ci/run_gates.py",
    "ci/gate_inputs.py",
    "ci/gate_ledger.py",
    "ci/host_identity.py",
    "ci/read_trace/sitecustomize.py",
    "ci/pins.py",
    "ci/requirements-replay.txt",
    "gororoba_quantum/parallel.py",
)


@pytest.fixture(autouse=True)
def hermetic(monkeypatch: pytest.MonkeyPatch) -> None:
    # The contracts build synthetic trees without historical-runtime gates, so
    # the caller's replay environment cannot decide them; the strict-runtime
    # case sets PINS_REQUIRED itself.
    monkeypatch.delenv(pins.PINS_REQUIRED, raising=False)


def test_disposable_defaults_use_system_temporary_directory(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "persistent-cache"))
    monkeypatch.setattr(premerge_gates.tempfile, "gettempdir", lambda: str(tmp_path))
    monkeypatch.setattr(premerge_gates, "repository_name", lambda _repo: "quantum-repository")
    if premerge_gates.default_cache() != tmp_path / "gororoba-quantum/premerge":
        raise AssertionError("disposable cache escaped the system temporary directory")
    if premerge_gates.default_worktrees() != tmp_path / "gororoba-quantum/premerge-worktrees/quantum-repository":
        raise AssertionError("disposable worktrees escaped the system temporary directory")


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """main regenerates a record's input; adds-record adds the record and its gate; consistent touches neither."""
    repo = tmp_path / "repo"
    (repo / "ci").mkdir(parents=True)
    git(repo, "init", "-q", "-b", "main")

    def commit(files: dict[str, str], message: str) -> None:
        for name, text in files.items():
            (repo / name).parent.mkdir(parents=True, exist_ok=True)
            (repo / name).write_text(text)
        git(repo, "add", "-A")
        git(repo, *MERGE_IDENTITY, "commit", "-q", "-m", message)

    def gates(*extra: dict[str, Any]) -> str:
        listed = [{"name": "always", "cwd": ".", "cmd": "true", "seconds": 0.1, "tier": "pr"}, *extra]
        return json.dumps({"gates": listed})

    record_gate = {"name": "record", "cwd": ".", "cmd": 'test "$(cat input)" = "$(cat record)"', "seconds": 0.1}
    host_gate = {"name": "host", "cwd": ".", "cmd": "false", "seconds": 0.1}
    runner_sources = {name: (ROOT / name).read_text(encoding="utf-8") for name in RUNNER_FILES}
    commit({"ci/gates.json": gates(host_gate), **runner_sources, "input": "v1\n"}, "base")
    git(repo, "branch", "adds-record")
    git(repo, "branch", "consistent")
    git(repo, "switch", "-q", "adds-record")
    commit({"ci/gates.json": gates(host_gate, record_gate), "record": "v1\n"}, "record and its gate")
    git(repo, "switch", "-q", "consistent")
    commit({"other": "x\n"}, "unrelated file")
    git(repo, "switch", "-q", "main")
    commit({"input": "v2\n"}, "regenerated input")
    git(repo, "switch", "-q", "-c", "conflicting", "main~1")
    commit({"input": "v3\n"}, "conflicting input")
    git(repo, "switch", "-q", "main")
    return repo


@pytest.mark.parametrize(
    ("ref", "expected", "marker"),
    (("adds-record", 1, "=== record fails on the merge"), ("consistent", 3, "0 introduced failures")),
)
def test_merge_classification(repo: Path, tmp_path: Path, ref: str, expected: int, marker: str) -> None:
    worktrees = tmp_path / "worktrees"
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        status = premerge(repo, ref, "main", DEFAULT_MAX_SECONDS, worktrees)
    text = output.getvalue()
    if status != expected or marker not in text or "blocking admission: host" not in text:
        raise AssertionError(f"premerge {ref} returned {status}, expected {expected}:\n{text}")
    if git(repo, "worktree", "list", "--porcelain").count("worktree ") != 1 or worktrees.exists():
        raise AssertionError(f"premerge {ref} left a worktree or its directory behind")


def test_conflict_stops(repo: Path, tmp_path: Path) -> None:
    worktrees = tmp_path / "worktrees"
    with contextlib.redirect_stdout(io.StringIO()):
        status = premerge(repo, "conflicting", "main", DEFAULT_MAX_SECONDS, worktrees)
    if status != 2 or worktrees.exists():
        raise AssertionError(f"a conflicting merge returned {status}, expected 2, or left its directory")


def test_strict_run_needs_a_replay_interpreter(repo: Path, tmp_path: Path) -> None:
    # Under PINS_REQUIRED an unnamed historical runtime stops the run
    # rather than failing its gates in both trees as shared failures.
    worktrees = tmp_path / "worktrees"
    strict = {key: value for key, value in os.environ.items() if key not in pins.REPLAY_VARIABLES}
    with mock.patch.dict(os.environ, {**strict, pins.PINS_REQUIRED: "1"}, clear=True):
        errors = io.StringIO()
        try:
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(errors):
                premerge(repo, "consistent", "main", DEFAULT_MAX_SECONDS, worktrees)
        except SystemExit as error:
            if error.code != 2 or "historical runtimes cannot run" not in errors.getvalue() or worktrees.exists():
                raise AssertionError(f"a strict run without a replay interpreter stopped with {error}") from error
        else:
            raise AssertionError("a strict run without a replay interpreter compared its gates")


def test_admission_refuses_an_interpreter_off_the_pins() -> None:
    # A premerge verdict decides admission, so an explicit $PYTHON that
    # differs from the pins stops the run with status 2.
    errors = io.StringIO()
    with (
        mock.patch.dict(os.environ, {"PYTHON": "/named/python"}),
        mock.patch.object(pins, "mismatches", lambda _python, _pins, _patches=None: ["qiskit 2.5.2 (pin 2.6.0)"]),
        contextlib.redirect_stdout(io.StringIO()),
        contextlib.redirect_stderr(errors),
        pytest.raises(SystemExit) as stopped,
    ):
        premerge_gates.interpreter.__wrapped__(ROOT)
    if stopped.value.code != 2 or "cannot decide admission" not in errors.getvalue():
        raise AssertionError(f"an off-pin interpreter stopped with {stopped.value.code}: {errors.getvalue()}")


def test_run_gates_variables_fall_under_the_cache_key() -> None:
    # Every variable the runner sets for its gates changes their results,
    # so each one must fall under the key.
    supplied = run_gates.environment_for(None)
    unkeyed = sorted(
        name
        for name in supplied
        if not (name.startswith(KEY_PREFIXES) or name in KEY_VARIABLES) and name not in os.environ
    )
    if unkeyed:
        raise AssertionError(f"run_gates sets variables the cache key omits: {unkeyed}")


def test_base_cache(repo: Path, tmp_path: Path) -> None:
    """The first run stores the base passes; later runs over the key reuse them and still classify failures."""
    worktrees = tmp_path / "worktrees"
    cache = tmp_path / "cache"

    def run(ref: str, max_seconds: float = DEFAULT_MAX_SECONDS) -> tuple[int, str]:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = premerge(repo, ref, "main", max_seconds, worktrees, cache=cache)
        return status, output.getvalue()

    status, text = run("consistent")
    entries = sorted(cache.glob("*.json"))
    if status != 3 or "base cache miss" not in text or len(entries) != 1:
        raise AssertionError(f"the first cached run returned {status} with entries {entries}:\n{text}")
    if json.loads(entries[0].read_text())["passed"] != ["always"]:
        raise AssertionError(f"the cache entry stores more than the base passes: {entries[0].read_text()}")
    # A hit skips the base run, so the host gate's base failure comes from
    # the --gates rerun; without it the shared failure reads as introduced.
    for ref, expected, marker, rerun in (
        ("consistent", 3, "0 introduced failures", "host"),
        ("adds-record", 1, "=== record fails on the merge", "host, record"),
    ):
        status, text = run(ref)
        hit = "base cache hit" in text and f"merge failures on the base: {rerun}\n" in text
        if status != expected or marker not in text or not hit or "blocking admission: host" not in text:
            raise AssertionError(f"a cached run of {ref} returned {status}, expected {expected}:\n{text}")
    status, text = run("consistent", DEFAULT_MAX_SECONDS / 2)
    if status != 3 or "base cache miss" not in text or len(list(cache.glob("*.json"))) != 2:
        raise AssertionError(f"a changed --max-seconds reused another key's entry:\n{text}")
    # A base runner without --gates reruns every gate. Its results replace
    # only the requested failures, so a cached pass whose rerun happens to
    # fail still marks the merge failure introduced.
    real_results = premerge_gates.results

    def legacy(
        root: Path, max_seconds: float, replay: dict[str, str] | None = None, gates: list[str] | None = None
    ) -> dict[str, tuple[int, str]]:
        found = real_results(root, max_seconds, replay)
        if root.name.startswith("merge-") or gates is not None:
            found["always"] = (1, "planted failure")
        return found

    with mock.patch.object(premerge_gates, "results", legacy):
        status, text = run("consistent")
    if status != 1 or "=== always fails on the merge" not in text:
        raise AssertionError(f"a legacy base rerun overwrote a cached pass:\n{text}")
    with mock.patch.dict(os.environ, {"GOROROBA_AER_DEVICE": "premerge-key-probe"}):
        status, text = run("consistent")
    if status != 3 or "base cache miss" not in text or len(list(cache.glob("*.json"))) != 3:
        raise AssertionError(f"a changed gate variable reused another key's entry:\n{text}")
    if "premerge-key-probe" in "".join(path.read_text() for path in cache.glob("*.json")):
        raise AssertionError("a cache entry stores an environment value in plain text")
    foreign_entries: list[Any] = [{"schema": CACHE_SCHEMA, "key": "foreign", "passed": ["always", "host"]}, [], None]
    for foreign in foreign_entries:
        entries[0].write_text(json.dumps(foreign))
        status, text = run("consistent")
        if status != 3 or "base cache miss" not in text or "blocking admission: host" not in text:
            raise AssertionError(f"the entry {foreign!r} was trusted:\n{text}")
