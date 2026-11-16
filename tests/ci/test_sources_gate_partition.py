"""The `sources-122` gate type-checks docs/evidence in several mypy processes.

mypy names a source by crawling up from its directory to an explicit package base (an entry of MYPYPATH or the
working directory): when every directory name on the way is a Python identifier the name is the dotted path, and
when one is not, as under a hyphenated evidence directory, the name is the bare file stem (measured with mypy
2.4.1: the single sweep reports the duplicates `make_kernels`, `runner`, `common` and `analyze`). Two files of one
process that receive the same name stop that process before it checks anything (`Duplicate module named ...`).
The gate therefore excludes one directory of each colliding pair from its sweep and gives it a process of its
own. These tests hold the partition: no process holds two sources of one module name, the processes together
cover every tracked Python file the single sweep covered, and every process runs with any failure reaching the
gate's exit status.
"""

from __future__ import annotations

import json
import re
import shlex
import subprocess
from collections import defaultdict
from pathlib import Path, PurePosixPath
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
GATE = "sources-122"
JOIN = " || rc=1; "
# The first process of the gate before the partition: one sweep with the two exclusions it already had.
SINGLE_SWEEP = (
    'MYPYPATH=docs "$PYTHON" ci/pinned_tool.py mypy --explicit-package-bases'
    " --exclude 'ibm-fez-actor-pilot/analyze[.]py$' --exclude 'a5-exceptional-fibers/working/'"
    " docs/verify_sources.py docs/check_verify_sources.py docs/evidence"
)
SINGLE_SWEEP_COLLISIONS = {"analyze", "common", "make_kernels", "runner"}


def _same(found: object, expected: object) -> None:
    if found != expected:
        raise AssertionError((found, expected))


def _gates(node: Any) -> list[dict[str, Any]]:
    if isinstance(node, dict):
        own = [node] if "name" in node and "cmd" in node else []
        return own + [gate for value in node.values() for gate in _gates(value)]
    if isinstance(node, list):
        return [gate for value in node for gate in _gates(value)]
    return []


def gate_command() -> str:
    manifest = json.loads((ROOT / "ci" / "gates.json").read_text(encoding="utf-8"))
    commands = [gate["cmd"] for gate in _gates(manifest) if gate["name"] == GATE]
    _same(len(commands), 1)
    return str(commands[0])


def processes(command: str) -> list[str]:
    """The mypy processes of a command of the form `rc=0; P1 || rc=1; P2 || rc=1; ... exit $rc`."""
    prefix, suffix = "rc=0; ", " || rc=1; exit $rc"
    if not command.startswith(prefix) or not command.endswith(suffix):
        raise AssertionError(f"the gate command does not aggregate its exit status: {command[:60]} ... {command[-30:]}")
    return command[len(prefix) : -len(suffix)].split(JOIN)


def tracked_python_files() -> list[str]:
    listed = subprocess.run(
        ["git", "ls-files", "docs/*.py"], cwd=ROOT, capture_output=True, text=True, check=True, timeout=60
    )
    return sorted(listed.stdout.split())


def sources(process: str, files: list[str]) -> tuple[list[str], list[str]]:
    """The tracked files one mypy process checks, and its package bases (MYPYPATH and the working directory)."""
    words = shlex.split(process)
    bases = ["."] + [word.split("=", 1)[1] for word in words if word.startswith("MYPYPATH=")]
    arguments = words[words.index("mypy") + 1 :]
    excludes: list[re.Pattern[str]] = []
    targets: list[str] = []
    position = 0
    while position < len(arguments):
        if arguments[position] == "--exclude":
            excludes.append(re.compile(arguments[position + 1]))
            position += 2
        elif arguments[position].startswith("--"):
            position += 1
        else:
            targets.append(arguments[position])
            position += 1
    chosen = [
        path
        for path in files
        if any(path == target or path.startswith(target.rstrip("/") + "/") for target in targets)
        and not any(pattern.search(path) for pattern in excludes)
    ]
    return chosen, bases


def module_name(path: str, bases: list[str]) -> str:
    """mypy's module name of a source under `--explicit-package-bases` with namespace packages."""
    file = PurePosixPath(path)
    parts = [file.stem]
    directory = file.parent
    while str(directory) not in bases:
        if not directory.name.isidentifier():
            return file.stem
        parts.append(directory.name)
        directory = directory.parent
    return ".".join(reversed(parts))


def collisions(process: str, files: list[str]) -> dict[str, list[str]]:
    chosen, bases = sources(process, files)
    by_name: dict[str, list[str]] = defaultdict(list)
    for path in chosen:
        by_name[module_name(path, bases)].append(path)
    return {name: paths for name, paths in by_name.items() if len(paths) > 1}


def test_the_single_sweep_holds_the_four_known_collisions() -> None:
    # A subset: a later same-named pair that the partition already separates adds a name here and breaks nothing.
    found = set(collisions(SINGLE_SWEEP, tracked_python_files()))
    _same(sorted(SINGLE_SWEEP_COLLISIONS - found), [])


def test_no_process_of_the_gate_holds_two_sources_of_one_module_name() -> None:
    files = tracked_python_files()
    found = {process: collisions(process, files) for process in processes(gate_command())}
    _same({process: names for process, names in found.items() if names}, {})


def test_the_processes_cover_the_single_sweep_and_each_source_once() -> None:
    files = tracked_python_files()
    swept = set(sources(SINGLE_SWEEP, files)[0])
    counted: dict[str, int] = defaultdict(int)
    for process in processes(gate_command()):
        for path in sources(process, files)[0]:
            counted[path] += 1
    _same(sorted(swept - set(counted)), [])
    _same(sorted(path for path, count in counted.items() if count > 1), [])
    # The sweep's own exclusions stay: the one file with its own process, and the ignored working directory.
    extra = sorted(set(counted) - swept)
    _same(extra, ["docs/evidence/ibm-fez-actor-pilot/analyze.py"])


def test_a_bare_import_in_a_separated_directory_names_its_sibling() -> None:
    files = tracked_python_files()
    directory = "docs/evidence/vacuum_endpoint_information"
    own = [process for process in processes(gate_command()) if process.endswith(" " + directory)]
    _same(len(own), 1)
    chosen, bases = sources(own[0], files)
    _same(module_name(f"{directory}/probe.py", bases), "probe")
    _same(f"{directory}/check_probe.py" in chosen, True)
    sweep_files, sweep_bases = sources(processes(gate_command())[0], files)
    _same([path for path in sweep_files if path.startswith(directory + "/")], [])
    # In the sweep the bare name `probe` belongs to a file under a hyphenated directory.
    named_probe = [path for path in sweep_files if module_name(path, sweep_bases) == "probe"]
    _same(named_probe, ["docs/evidence/hhl-qsvt-falsify/probe.py"])


def _run_skeleton(count: int, failing: int | None) -> tuple[int, list[str]]:
    steps = [f"{{ echo {index}; {'false' if index == failing else 'true'}; }}" for index in range(count)]
    command = "rc=0; " + JOIN.join(steps) + " || rc=1; exit $rc"
    _same(len(processes(command)), count)
    done = subprocess.run(["sh", "-c", "set -eu\n" + command], capture_output=True, text=True, check=False, timeout=30)
    return done.returncode, done.stdout.split()


def test_every_process_runs_and_any_failure_fails_the_gate() -> None:
    count = len(processes(gate_command()))
    everything = [str(index) for index in range(count)]
    _same(_run_skeleton(count, None), (0, everything))
    for failing in range(count):
        _same(_run_skeleton(count, failing), (1, everything))


def test_a_chain_that_stops_at_the_first_failure_is_rejected() -> None:
    chained = " && ".join(processes(gate_command()))
    try:
        processes(chained)
    except AssertionError:
        return
    raise AssertionError("a command joined by && passed as an aggregating command")
