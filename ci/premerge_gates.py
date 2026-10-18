"""Run the fast gates on the tree a merge into main would produce, against main's own result.

A pull request's CI runs on its merge with main as main stood when CI ran.
A gate that checks a record derived from the whole tree (the toolchain
record over every case circuit, the research-state registry over every
retained run) can then pass on two branches separately and fail on their
combination: one branch adds the record or its gate, the other adds or
regenerates an input the record does not yet cover, and git merges both
without a textual conflict. This script builds that combination before the
merge: it checks out BASE (default origin/main) and the merge of REF into
BASE in two detached worktrees, runs the pr-tier gates whose measured
seconds are at most --max-seconds in each tree through that tree's own
ci/run_gates.py, with $PYTHON resolved to an absolute interpreter, and
reports every gate that passes on BASE and fails on the merge, or that the
merge adds and that fails. Gates that fail on both trees are host or main
failures and are listed without failing the run, so a lint or type gate
whose local toolchain differs from CI's does not mask the comparison. A
textual conflict stops the run with the conflicted paths.

Historical-runtime gates run under the interpreter pins.resolve_replay
chooses from --replay-python, REPLAY_PYTHON or the running interpreter,
verified per tree against that tree's ci/requirements-replay.txt; each
runner receives it as REPLAY_PYTHON in its own environment, so a base whose
runner predates --replay-python runs those gates too. An explicit
interpreter that fails the merge's pins stops the run, and under
GOROROBA_PINS_REQUIRED=1 so does any runtime either tree cannot resolve,
since its gates would fail in both trees and read as shared failures.

The base's passing gates are cached under --cache (default
${XDG_CACHE_HOME:-~/.cache}/gororoba-quantum/premerge) by a key over the base
commit, --max-seconds, each interpreter's path, version and installed
distributions, the PATH tools gates run, and the environment variables
gates read to pick a path, toolchain or thread count (KEY_PREFIXES,
KEY_VARIABLES), so premerges against one main commit under one key run the
base once; a flock serializes concurrent runs over one key and the second
reads the first's entry. Base failures are never cached: a merge failure
absent from the cached passes reruns on the base through run_gates --gates,
so a gate that failed once under load is classified by a fresh run.

The worktrees live under --worktrees (default ~/worktrees/<repository>/premerge,
<repository> naming the primary checkout), named by base, ref and process id,
and are removed on exit. Exit
status: 0 when the merge introduces no failure, 1 when it does, 2 on a merge
conflict.

Usage: "$PYTHON" ci/premerge_gates.py REF [--base origin/main] [--max-seconds 5] [--no-fetch] [--replay-python PATH]
                                     [--cache DIR | --no-cache]
       "$PYTHON" ci/premerge_gates.py --self-test
"""

from __future__ import annotations

import argparse
import contextlib
import fcntl
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Iterator
from pathlib import Path
from typing import Any
from unittest import mock

import pins

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MAX_SECONDS = 5.0
TAIL_LINES = 20
# The merge commit lives only in the scratch worktree and is never pushed, so it
# carries a local identity and no signature.
MERGE_IDENTITY = ["-c", "user.name=premerge", "-c", "user.email=premerge@localhost", "-c", "commit.gpgSign=false"]
VERDICT = re.compile(r"^(PASS|FAIL) (\S+) ")
FAILURE_TAIL = re.compile(r"^=== (\S+) exit ")
CACHE_SCHEMA = "gororoba-premerge-base-v1"
# Gates read these to choose a device, toolchain, live or replay path, thread
# count or warning policy, so each one's value enters the cache key.
KEY_PREFIXES = ("GOROROBA_", "QI_", "OQ_", "QD_", "QISKIT_", "PYTHON", "OMP_", "OPENBLAS_", "MKL_", "BLIS_")
KEY_VARIABLES = ("GLIBC_TUNABLES", "PATH", "HOME", "VIRTUAL_ENV")
# Gates run these from PATH (ci/pinned_tool.py prefers an installed ruff or
# mypy at its pin and otherwise runs the pin through uv), so each one's
# resolved file identity enters the key.
KEY_TOOLS = ("ruff", "mypy", "uv", "shellcheck", "git", "sha256sum", "rocq")
# These name interpreters of the separate service stacks; their installed
# distributions enter the key beside the path.
KEY_INTERPRETERS = ("QI_PYTHON", "OQ_PYTHON", "QD_PYTHON")
DISTRIBUTIONS = (
    "import importlib.metadata as m, json, sys; "
    "print(json.dumps([sys.version, sorted({(d.metadata['Name'] or '', d.version) for d in m.distributions()})]))"
)


def git(repo: Path, *args: str, check: bool = True) -> str:
    completed = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=False)
    if check and completed.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} failed in {repo}:\n{completed.stderr.strip()}")
    return completed.stdout.strip()


def repository_name(repo: Path) -> str:
    """The primary checkout's directory name; a linked worktree's own directory names its branch instead."""
    common = Path(git(repo, "rev-parse", "--path-format=absolute", "--git-common-dir"))
    return common.parent.name


@contextlib.contextmanager
def worktree(repo: Path, path: Path, commit: str) -> Iterator[Path]:
    """A detached worktree of commit at path, removed with its generated files on exit."""
    git(repo, "worktree", "add", "--detach", str(path), commit)
    try:
        yield path
    finally:
        git(repo, "worktree", "remove", "--force", str(path), check=False)
        git(repo, "worktree", "prune", check=False)


def interpreter() -> str:
    """$PYTHON as an absolute path, since every gate runs with its cwd inside a scratch worktree."""
    named = os.environ.get("PYTHON", sys.executable)
    found = shutil.which(named)
    if found is None:
        raise SystemExit(f"PYTHON={named} names no executable")
    return os.path.abspath(found)


def default_cache() -> Path:
    return Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache") / "gororoba-quantum" / "premerge"


def interpreter_identity(python: str) -> list[Any]:
    """The interpreter's real path, version and installed distributions as a gate run under it sees them."""
    completed = subprocess.run(
        [python, "-c", DISTRIBUTIONS], cwd=tempfile.gettempdir(), capture_output=True, text=True, check=False
    )
    if completed.returncode != 0:
        raise SystemExit(f"premerge: {python} cannot list its distributions:\n{completed.stderr.strip()}")
    return [os.path.realpath(python), json.loads(completed.stdout)]


def tool_identity(name: str) -> list[Any] | None:
    """The resolved path, size and modification time of a PATH tool, or None when PATH lacks it."""
    found = shutil.which(name)
    if found is None:
        return None
    real = os.path.realpath(found)
    status = os.stat(real)
    return [real, status.st_size, status.st_mtime_ns]


def cache_key(base_commit: str, max_seconds: float, replay: dict[str, str]) -> tuple[str, dict[str, Any]]:
    """The digest naming a base result and the components it covers.

    Environment values enter as sha256 digests, so a credential a variable
    carries (QISKIT_IBM_TOKEN matches the QISKIT_ prefix) never reaches the
    cache file.
    """
    environment = {
        name: hashlib.sha256(value.encode()).hexdigest()
        for name, value in sorted(os.environ.items())
        if name.startswith(KEY_PREFIXES) or name in KEY_VARIABLES
    }
    services = {
        name: interpreter_identity(os.environ[name])
        for name in KEY_INTERPRETERS
        if os.environ.get(name) and os.access(os.environ[name], os.X_OK)
    }
    components = {
        "schema": CACHE_SCHEMA,
        "base": base_commit,
        "max_seconds": max_seconds,
        "python": interpreter_identity(interpreter()),
        "replay": {variable: interpreter_identity(path) for variable, path in sorted(replay.items())},
        "environment": environment,
        "services": services,
        "tools": {name: tool_identity(name) for name in KEY_TOOLS},
    }
    digest = hashlib.sha256(json.dumps(components, sort_keys=True).encode()).hexdigest()
    return digest, components


@contextlib.contextmanager
def locked(path: Path) -> Iterator[None]:
    """An exclusive flock beside path for the duration of the block."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path.with_suffix(".lock"), "w") as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print(f"premerge: waiting for another run over {path.name}", flush=True)
            fcntl.flock(handle, fcntl.LOCK_EX)
        yield


def cached_passes(path: Path, digest: str) -> set[str] | None:
    """The passing gate names a matching entry records, or None for a missing or foreign entry."""
    try:
        entry = json.loads(path.read_text())
    except (OSError, ValueError):
        return None
    if not isinstance(entry, dict):
        return None
    passed = entry.get("passed")
    if entry.get("schema") != CACHE_SCHEMA or entry.get("key") != digest or not isinstance(passed, list):
        return None
    return {name for name in passed if isinstance(name, str)}


def store_passes(path: Path, digest: str, components: dict[str, Any], base: dict[str, tuple[int, str]]) -> None:
    passed = sorted(name for name, (status, _) in base.items() if status == 0)
    entry = {"schema": CACHE_SCHEMA, "key": digest, "components": components, "passed": passed}
    with tempfile.NamedTemporaryFile("w", dir=path.parent, prefix=path.name, delete=False) as handle:
        try:
            json.dump(entry, handle, indent=1)
            handle.write("\n")
        except BaseException:
            os.unlink(handle.name)
            raise
    os.replace(handle.name, path)


def results(
    root: Path, max_seconds: float, replay: dict[str, str] | None = None, gates: list[str] | None = None
) -> dict[str, tuple[int, str]]:
    """Each gate's status and failure output from the tree's own ci/run_gates.py, optionally only named gates."""
    python = interpreter()
    environment = {**os.environ, "PYTHON": python, **(replay or {})}
    selection = ["--gates", ",".join(gates)] if gates is not None else []
    completed = subprocess.run(
        [python, "-B", str(root / "ci/run_gates.py"), "--tier", "pr", "--max-seconds", str(max_seconds), *selection],
        cwd=root,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    lines = completed.stdout.splitlines()
    statuses = {m.group(2): 0 if m.group(1) == "PASS" else 1 for m in map(VERDICT.match, lines) if m}
    if "unrecognized arguments: --max-seconds" in completed.stderr:
        raise SystemExit(f"{root / 'ci/run_gates.py'} predates --max-seconds; the base needs ci/premerge_gates.py too")
    if gates is not None and "unrecognized arguments: --gates" in completed.stderr:
        print(f"premerge: {root / 'ci/run_gates.py'} predates --gates; the base runs every gate", flush=True)
        return results(root, max_seconds, replay)
    if not statuses and not (gates is not None and completed.returncode == 0):
        raise SystemExit(f"{root / 'ci/run_gates.py'} reported no gate:\n{completed.stdout}{completed.stderr}")
    tails: dict[str, list[str]] = {}
    current: str | None = None
    for line in lines:
        if heading := FAILURE_TAIL.match(line):
            current = heading.group(1)
            tails[current] = []
        elif current is not None:
            tails[current].append(line)
    return {name: (status, "\n".join(tails.get(name, []))) for name, status in statuses.items()}


def compare(base: dict[str, tuple[int, str]], merged: dict[str, tuple[int, str]]) -> tuple[list[str], list[str]]:
    """Gates the merge breaks (pass on base or absent there, fail on the merge) and gates failing on both."""
    introduced = [name for name, (status, _) in merged.items() if status != 0 and base.get(name, (0, ""))[0] == 0]
    shared = [name for name, (status, _) in merged.items() if status != 0 and base.get(name, (0, ""))[0] != 0]
    return introduced, shared


def replay_interpreters(explicit: str | None, root: Path, label: str) -> tuple[dict[str, str], list[str]]:
    """The historical-runtime interpreter variables ROOT's runner receives, verified against ROOT's pins.

    The second element names each runtime left without an interpreter when
    one was demanded, by an explicit interpreter or by PINS_REQUIRED, so a
    caller refuses rather than compare gates neither tree ran.
    """
    found: dict[str, str] = {}
    refused: list[str] = []
    for runtime, (variable, _path) in pins.REPLAY_RUNTIMES.items():
        chosen, reason = pins.resolve_replay(runtime, explicit, os.environ, interpreter(), root)
        print(f"premerge: {label} historical runtime {runtime}: {reason}", flush=True)
        if chosen is not None:
            found[variable] = os.path.abspath(shutil.which(chosen) or chosen)
        elif explicit or pins.pins_required(os.environ):
            refused.append(f"{runtime}: {reason}")
    return found, refused


def premerge(
    repo: Path,
    ref: str,
    base_ref: str,
    max_seconds: float,
    worktrees: Path,
    replay_python: str | None = None,
    cache: Path | None = None,
) -> int:
    base_commit = git(repo, "rev-parse", "--verify", f"{base_ref}^{{commit}}")
    ref_commit = git(repo, "rev-parse", "--verify", f"{ref}^{{commit}}")
    worktrees.mkdir(parents=True, exist_ok=True)
    # The process id keeps two concurrent runs over one base and ref, from any
    # session sharing --worktrees, on separate worktree paths.
    label = f"{base_commit[:12]}-{ref_commit[:12]}-{os.getpid()}"
    try:
        with (
            worktree(repo, worktrees / f"base-{label}", base_commit) as base_tree,
            worktree(repo, worktrees / f"merge-{label}", base_commit) as merge_tree,
        ):
            merged = subprocess.run(
                ["git", "-C", str(merge_tree), *MERGE_IDENTITY, "merge", "--no-ff", "--no-edit", ref_commit],
                capture_output=True,
                text=True,
                check=False,
            )
            if merged.returncode != 0:
                conflicts = git(merge_tree, "diff", "--name-only", "--diff-filter=U", check=False)
                git(merge_tree, "merge", "--abort", check=False)
                print(f"merge of {ref} into {base_ref} conflicts:\n{conflicts or merged.stdout + merged.stderr}")
                return 2
            # Each tree verifies the interpreter against its own pins, so a
            # branch that changes ci/requirements-replay.txt runs its gates
            # under an interpreter holding the new pins. An explicit
            # interpreter must satisfy the merge, the tree under test.
            merge_replay, refused = replay_interpreters(replay_python, merge_tree, "merge")
            if refused:
                raise SystemExit(f"premerge: the merge's historical runtimes cannot run: {'; '.join(refused)}")
            base_replay, base_refused = replay_interpreters(replay_python, base_tree, "base")
            if replay_python and base_refused:
                base_replay, base_refused = replay_interpreters(None, base_tree, "base")
            if base_refused:
                raise SystemExit(f"premerge: the base's historical runtimes cannot run: {'; '.join(base_refused)}")
            base_results, passes = base_gates(base_tree, base_commit, max_seconds, base_replay, cache)
            merge_results = results(merge_tree, max_seconds, merge_replay)
            if passes is not None:
                unknown = sorted(
                    name for name, (status, _) in merge_results.items() if status != 0 and name not in passes
                )
                base_results = {name: (0, "") for name in passes}
                if unknown:
                    print(f"premerge: rerunning {len(unknown)} merge failures on the base: {', '.join(unknown)}")
                    base_results.update(results(base_tree, max_seconds, base_replay, unknown))
    finally:
        with contextlib.suppress(OSError):
            worktrees.rmdir()
    introduced, shared = compare(base_results, merge_results)
    for name in introduced:
        tail = "\n".join(merge_results[name][1].splitlines()[-TAIL_LINES:])
        print(f"=== {name} fails on the merge and passes on {base_ref}\n{tail}\n")
    if shared:
        print(f"failing on {base_ref} and on the merge (host or main): {', '.join(shared)}")
    print(
        f"premerge {ref} ({ref_commit[:12]}) into {base_ref} ({base_commit[:12]}): "
        f"{len(merge_results)} gates at most {max_seconds:g} s, {len(introduced)} introduced failures"
    )
    return 1 if introduced else 0


def base_gates(
    base_tree: Path, base_commit: str, max_seconds: float, replay: dict[str, str], cache: Path | None
) -> tuple[dict[str, tuple[int, str]], set[str] | None]:
    """The base's results when it runs, else the cached passes with an empty result map.

    The lock spans lookup, run and store, so a second run over the same key
    waits for the first and reads its entry rather than running the base
    beside it.
    """
    if cache is None:
        return results(base_tree, max_seconds, replay), None
    digest, components = cache_key(base_commit, max_seconds, replay)
    path = cache / f"{base_commit[:12]}-{digest[:16]}.json"
    with locked(path):
        passes = cached_passes(path, digest)
        if passes is not None:
            print(f"premerge: base cache hit {path} ({len(passes)} passing gates)", flush=True)
            return {}, passes
        print(f"premerge: base cache miss {path}; running the base", flush=True)
        base = results(base_tree, max_seconds, replay)
        store_passes(path, digest, components, base)
    return base, None


def self_test() -> None:
    """A clean merge where one branch adds a record gate and the other changes its input must fail."""
    with tempfile.TemporaryDirectory(prefix="premerge-contract-") as temporary:
        repo = Path(temporary) / "repo"
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
        runner_files = (
            "ci/run_gates.py",
            "ci/gate_inputs.py",
            "ci/pins.py",
            "ci/requirements-replay.txt",
            "gororoba_quantum/parallel.py",
        )
        runner_sources = {name: (ROOT / name).read_text(encoding="utf-8") for name in runner_files}
        commit({"ci/gates.json": gates(host_gate), **runner_sources, "input": "v1\n"}, "base")
        git(repo, "branch", "adds-record")
        git(repo, "branch", "consistent")
        git(repo, "switch", "-q", "adds-record")
        commit({"ci/gates.json": gates(host_gate, record_gate), "record": "v1\n"}, "record and its gate")
        git(repo, "switch", "-q", "consistent")
        commit({"other": "x\n"}, "unrelated file")
        git(repo, "switch", "-q", "main")
        commit({"input": "v2\n"}, "regenerated input")
        worktrees = Path(temporary) / "worktrees"
        for ref, expected, marker in (
            ("adds-record", 1, "=== record fails on the merge"),
            ("consistent", 0, "0 introduced failures"),
        ):
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                status = premerge(repo, ref, "main", DEFAULT_MAX_SECONDS, worktrees)
            text = output.getvalue()
            if status != expected or marker not in text or "(host or main): host" not in text:
                raise RuntimeError(f"premerge {ref} returned {status}, expected {expected}:\n{text}")
            if git(repo, "worktree", "list", "--porcelain").count("worktree ") != 1 or worktrees.exists():
                raise RuntimeError(f"premerge {ref} left a worktree or its directory behind")
        git(repo, "switch", "-q", "-c", "conflicting", "main~1")
        commit({"input": "v3\n"}, "conflicting input")
        git(repo, "switch", "-q", "main")
        with contextlib.redirect_stdout(io.StringIO()):
            status = premerge(repo, "conflicting", "main", DEFAULT_MAX_SECONDS, worktrees)
        if status != 2 or worktrees.exists():
            raise RuntimeError(f"a conflicting merge returned {status}, expected 2, or left its directory")
        # Under PINS_REQUIRED an unnamed historical runtime stops the run
        # rather than failing its gates in both trees as shared failures.
        strict = {key: value for key, value in os.environ.items() if key not in pins.REPLAY_VARIABLES}
        with mock.patch.dict(os.environ, {**strict, pins.PINS_REQUIRED: "1"}, clear=True):
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    premerge(repo, "consistent", "main", DEFAULT_MAX_SECONDS, worktrees)
            except SystemExit as error:
                if "historical runtimes cannot run" not in str(error) or worktrees.exists():
                    raise RuntimeError(f"a strict run without a replay interpreter stopped with {error}") from error
            else:
                raise RuntimeError("a strict run without a replay interpreter compared its gates")
        cache_self_test(repo, worktrees, Path(temporary) / "cache")
    print(
        "premerge: a clean merge that breaks a record gate fails, a consistent merge passes, a conflict stops, "
        "a strict run without a replay interpreter stops, and the base cache stores passes only, hits on its "
        "key, misses on a changed key or a foreign entry, and reruns a base failure"
    )


def cache_self_test(repo: Path, worktrees: Path, cache: Path) -> None:
    """The first run stores the base passes; later runs over the key reuse them and still classify failures."""

    def run(ref: str, max_seconds: float = DEFAULT_MAX_SECONDS) -> tuple[int, str]:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = premerge(repo, ref, "main", max_seconds, worktrees, cache=cache)
        return status, output.getvalue()

    status, text = run("consistent")
    entries = sorted(cache.glob("*.json"))
    if status != 0 or "base cache miss" not in text or len(entries) != 1:
        raise RuntimeError(f"the first cached run returned {status} with entries {entries}:\n{text}")
    if json.loads(entries[0].read_text())["passed"] != ["always"]:
        raise RuntimeError(f"the cache entry stores more than the base passes: {entries[0].read_text()}")
    # A hit skips the base run, so the host gate's base failure comes from
    # the --gates rerun; without it the shared failure reads as introduced.
    for ref, expected, marker, rerun in (
        ("consistent", 0, "0 introduced failures", "host"),
        ("adds-record", 1, "=== record fails on the merge", "host, record"),
    ):
        status, text = run(ref)
        hit = "base cache hit" in text and f"merge failures on the base: {rerun}\n" in text
        if status != expected or marker not in text or not hit or "(host or main): host" not in text:
            raise RuntimeError(f"a cached run of {ref} returned {status}, expected {expected}:\n{text}")
    status, text = run("consistent", DEFAULT_MAX_SECONDS / 2)
    if status != 0 or "base cache miss" not in text or len(list(cache.glob("*.json"))) != 2:
        raise RuntimeError(f"a changed --max-seconds reused another key's entry:\n{text}")
    with mock.patch.dict(os.environ, {"GOROROBA_AER_DEVICE": "premerge-key-probe"}):
        status, text = run("consistent")
    if status != 0 or "base cache miss" not in text or len(list(cache.glob("*.json"))) != 3:
        raise RuntimeError(f"a changed gate variable reused another key's entry:\n{text}")
    if "premerge-key-probe" in "".join(path.read_text() for path in cache.glob("*.json")):
        raise RuntimeError("a cache entry stores an environment value in plain text")
    foreign_entries: list[Any] = [{"schema": CACHE_SCHEMA, "key": "foreign", "passed": ["always", "host"]}, [], None]
    for foreign in foreign_entries:
        entries[0].write_text(json.dumps(foreign))
        status, text = run("consistent")
        if status != 0 or "base cache miss" not in text or "(host or main): host" not in text:
            raise RuntimeError(f"the entry {foreign!r} was trusted:\n{text}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("ref", nargs="?", help="branch, tag or commit to merge into BASE")
    parser.add_argument("--base", default="origin/main")
    parser.add_argument("--max-seconds", type=float, default=DEFAULT_MAX_SECONDS)
    parser.add_argument("--no-fetch", action="store_true", help="use the local refs as they stand")
    parser.add_argument("--worktrees", type=Path, help="scratch directory, default ~/worktrees/<repository>/premerge")
    caching = parser.add_mutually_exclusive_group()
    caching.add_argument(
        "--cache", type=Path, help="base result cache, default $XDG_CACHE_HOME/gororoba-quantum/premerge"
    )
    caching.add_argument("--no-cache", action="store_true", help="run the base on every invocation")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument(
        "--replay-python",
        help="interpreter for historical-runtime gates; it must hold every pin of ci/requirements-replay.txt",
    )
    arguments = parser.parse_args(argv)
    if arguments.self_test:
        self_test()
        return 0
    if arguments.ref is None:
        parser.error("REF is required unless --self-test")
    if not arguments.no_fetch:
        git(ROOT, "fetch", "--quiet", "origin")
    worktrees = arguments.worktrees or Path.home() / "worktrees" / repository_name(ROOT) / "premerge"
    cache = None if arguments.no_cache else arguments.cache or default_cache()
    return premerge(
        ROOT, arguments.ref, arguments.base, arguments.max_seconds, worktrees, arguments.replay_python, cache
    )


if __name__ == "__main__":
    sys.exit(main())
