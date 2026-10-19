"""Skip a gate whose traced read set and host identity equal those of a recorded pass.

ci/run_gates.py runs each gate with ci/read_trace/sitecustomize.py on
PYTHONPATH, which records the repository files, directory listings and glob
patterns every Python process of the gate reads. After a pass whose trace is
complete, the ledger stores the gate's key and read set. The key is a
sha256 over the ledger schema, the tracer source, the gate's manifest entry
(command, working directory, runtime, workers, requires, parent), its
allocated worker count, the host identity (ci/host_identity.py) and the read
set's content: each file's sha256, each listed directory's sorted entry
names and each glob pattern's sorted matches, less interpreter and lint caches
(CACHE_NAMES, *.pyc). A later run recomputes the key
from the stored read set and reports SKIP when it is unchanged.

A run stores no entry, and removes the gate's earlier one, when the gate
fails or its trace is incomplete: a shell command other than ``"$PYTHON"``
invocations joined by ``&&``, a Python invocation under -I, -E or -S, a
process that writes inside the repository, starts a program other than a
traced interpreter or starts a child whose environment drops the trace
(the ``U`` records of the tracer).

Usage: "$PYTHON" ci/gate_ledger.py merge OUT [--base LEDGER] SHARD_LEDGER...
       "$PYTHON" ci/gate_ledger.py --self-test
"""

from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
import shlex
import sys
import tempfile
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
TRACER = Path(__file__).resolve().parent / "read_trace"
SCHEMA = "gororoba-gate-ledger-v1"
# Manifest fields that change what a gate runs; seconds and tier only schedule it.
MANIFEST_FIELDS = ("cmd", "cwd", "runtime", "workers", "requires", "parent", "case_registry")
SHELL_METACHARACTERS = ("|", ";", ">", "<", "`", "$(", "\n", "&")
PYTHON_WORD = "$PYTHON"
# Interpreter and lint caches appear in directory listings as gates run; their
# contents are derived from the sources the read set already hashes.
CACHE_NAMES = frozenset(("__pycache__", ".mypy_cache", ".ruff_cache", ".pytest_cache"))


def derived(name: str) -> bool:
    return name in CACHE_NAMES or name.endswith(".pyc")


def tracer_digest() -> str:
    return hashlib.sha256((TRACER / "sitecustomize.py").read_bytes()).hexdigest()


def host_digest(components: Mapping[str, Any]) -> str:
    return hashlib.sha256(json.dumps(components, sort_keys=True).encode()).hexdigest()


def python_flags_escape(arguments: list[str]) -> str | None:
    """The interpreter flag that disables site or the environment, or None."""
    words = iter(arguments)
    for word in words:
        if not word.startswith("-") or word == "-" or word.startswith("--"):
            return None
        for index, letter in enumerate(word[1:]):
            if letter in "IES":
                return f"-{letter}"
            if letter in "cm":
                return None
            if letter in "WX":
                if index == len(word) - 2:
                    next(words, None)
                break
    return None


def shell_untraceable(command: str) -> str | None:
    """Why a gate command escapes the trace, or None when it is ``"$PYTHON"`` calls joined by ``&&``."""
    if any(mark in command.replace("&&", "\0") for mark in SHELL_METACHARACTERS):
        return "shell command beyond $PYTHON invocations joined by &&"
    for segment in command.split("&&"):
        try:
            words = shlex.split(segment)
        except ValueError:
            return "shell command does not parse"
        if not words or words[0] != PYTHON_WORD:
            return f"shell runs {words[0] if words else 'nothing'}"
        if flag := python_flags_escape(words[1:]):
            return f"$PYTHON {flag} skips the tracer"
    return None


def trace_environment(
    environment: Mapping[str, str], trace: Path, root: Path, pythons: Iterable[str]
) -> dict[str, str]:
    """The gate environment that loads the tracer into every Python process of the gate."""
    traced = dict(environment)
    existing = traced.get("PYTHONPATH")
    traced["PYTHONPATH"] = os.pathsep.join([str(TRACER), *([existing] if existing else [])])
    traced["GOROROBA_READ_TRACE"] = str(trace)
    traced["GOROROBA_READ_TRACE_ROOT"] = str(root.resolve())
    traced["GOROROBA_READ_TRACE_PYTHONS"] = os.pathsep.join(sorted({p for p in pythons if p}))
    return traced


def read_trace(trace: Path) -> tuple[dict[str, list[Any]] | None, list[str]]:
    """The union read set of every process record in TRACE, or None with the reasons it is incomplete."""
    files: set[str] = set()
    directories: set[str] = set()
    patterns: set[tuple[int, str]] = set()
    reasons: list[str] = []
    records = sorted(trace.glob("*.tsv")) if trace.is_dir() else []
    if not records:
        reasons.append("no traced Python process")
    for record in records:
        for line in record.read_text(encoding="utf-8", errors="surrogateescape").splitlines():
            kind, _, rest = line.partition("\t")
            if kind == "f":
                files.add(rest)
            elif kind == "d":
                directories.add(rest)
            elif kind == "g":
                recursive, _, pattern = rest.partition("\t")
                patterns.add((int(recursive), pattern))
            elif kind == "U":
                reasons.append(rest)
            else:
                reasons.append(f"unreadable trace record {line[:80]!r}")
    if reasons:
        return None, sorted(set(reasons))
    return {
        "files": sorted(files),
        "dirs": sorted(directories),
        "globs": [list(item) for item in sorted(patterns)],
    }, []


class Content:
    """Memoized content digests of read-set members over one runner invocation."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.memo: dict[tuple[str, str], Any] = {}

    def file(self, name: str) -> str:
        key = ("f", name)
        if key not in self.memo:
            path = self.root / name
            try:
                self.memo[key] = hashlib.sha256(path.read_bytes()).hexdigest()
            except IsADirectoryError:
                self.memo[key] = "directory"
            except FileNotFoundError:
                self.memo[key] = "absent"
            except OSError as error:
                self.memo[key] = f"unreadable {error.errno}"
        return str(self.memo[key])

    def directory(self, name: str) -> list[str] | str:
        key = ("d", name)
        if key not in self.memo:
            try:
                self.memo[key] = sorted(entry for entry in os.listdir(self.root / name) if not derived(entry))
            except FileNotFoundError:
                self.memo[key] = "absent"
            except NotADirectoryError:
                self.memo[key] = "file"
        value: list[str] | str = self.memo[key]
        return value

    def matches(self, recursive: int, pattern: str) -> list[str]:
        key = ("g", f"{recursive}\t{pattern}")
        if key not in self.memo:
            found = glob.glob(pattern, root_dir=self.root, recursive=bool(recursive))
            self.memo[key] = sorted(path for path in found if not any(derived(part) for part in Path(path).parts))
        value: list[str] = self.memo[key]
        return value

    def forget(self) -> None:
        self.memo.clear()


def gate_key(gate: Mapping[str, Any], workers: int, host: str, reads: Mapping[str, list[Any]], content: Content) -> str:
    manifest = {field: gate.get(field) for field in MANIFEST_FIELDS}
    components = {
        "schema": SCHEMA,
        "tracer": tracer_digest(),
        "host": host,
        "manifest": manifest,
        "allocated_workers": workers,
        "files": {name: content.file(name) for name in reads["files"]},
        "dirs": {name: content.directory(name) for name in reads["dirs"]},
        "globs": [[recursive, pattern, content.matches(recursive, pattern)] for recursive, pattern in reads["globs"]],
    }
    return hashlib.sha256(json.dumps(components, sort_keys=True).encode()).hexdigest()


def valid_entry(entry: Any) -> bool:
    if not isinstance(entry, dict) or not isinstance(entry.get("key"), str):
        return False
    reads = entry.get("reads")
    if not isinstance(reads, dict):
        return False
    files, dirs, globs = reads.get("files"), reads.get("dirs"), reads.get("globs")
    return (
        isinstance(files, list)
        and all(isinstance(name, str) for name in files)
        and isinstance(dirs, list)
        and all(isinstance(name, str) for name in dirs)
        and isinstance(globs, list)
        and all(
            isinstance(item, list) and len(item) == 2 and isinstance(item[0], int) and isinstance(item[1], str)
            for item in globs
        )
    )


def load(path: Path | None) -> dict[str, dict[str, Any]]:
    """The valid entries of a ledger file; a missing, foreign or malformed file yields none."""
    if path is None:
        return {}
    try:
        document = json.loads(path.read_text())
    except (OSError, ValueError):
        return {}
    if (
        not isinstance(document, dict)
        or document.get("schema") != SCHEMA
        or not isinstance(document.get("gates"), dict)
    ):
        return {}
    return {name: entry for name, entry in document["gates"].items() if isinstance(name, str) and valid_entry(entry)}


def write(path: Path, entries: Mapping[str, Any], selected: Iterable[str]) -> None:
    """Write the ledger with the names this run decided, so a merge knows which entries it owns."""
    document = {"schema": SCHEMA, "selected": sorted(set(selected)), "gates": dict(sorted(entries.items()))}
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", dir=path.parent, prefix=path.name, delete=False) as handle:
        json.dump(document, handle, indent=1)
        handle.write("\n")
    os.replace(handle.name, path)


def merge(base: Path | None, shards: list[Path]) -> tuple[dict[str, Any], list[str]]:
    """Overlay each shard's decided gates on the base; a selected gate absent from a shard's entries is dropped."""
    merged = load(base)
    selected: set[str] = set()
    for shard in shards:
        document = json.loads(shard.read_text())
        if document.get("schema") != SCHEMA or not isinstance(document.get("selected"), list):
            raise SystemExit(f"{shard}: not a {SCHEMA} shard ledger")
        decided = set(document["selected"])
        entries = load(shard)
        for name in decided:
            if name in entries:
                merged[name] = entries[name]
            else:
                merged.pop(name, None)
        selected |= decided
    return merged, sorted(selected)


def self_test() -> None:
    """Every read kind flips SKIP to RUN after an edit; escapes, failures and key inputs never skip."""
    from unittest import mock

    import host_identity
    import run_gates

    python = sys.executable
    with tempfile.TemporaryDirectory(prefix="gate-ledger-contract-") as temporary:
        root = Path(temporary) / "repo"
        (root / "data" / "listed").mkdir(parents=True)
        (root / "data" / "globbed").mkdir(parents=True)
        (root / "pkg").mkdir()
        files = {
            "plain.py": "import pathlib\npathlib.Path('data/plain.txt').read_text()\n",
            "data/plain.txt": "v1\n",
            "importer.py": "import sys\nsys.path.insert(0, 'pkg')\nimport helper\n",
            "pkg/helper.py": "VALUE = 1\n",
            "globber.py": "import glob\nglob.glob('data/globbed/*.txt')\n",
            "data/globbed/a.txt": "",
            "lister.py": "import os\nos.listdir('data/listed')\n",
            "data/listed/a.txt": "",
            "pooled.py": (
                "import multiprocessing\n"
                "def read(path):\n"
                "    with open(path) as handle:\n"
                "        return handle.read()\n"
                "if __name__ == '__main__':\n"
                "    with multiprocessing.get_context('spawn').Pool(1) as pool:\n"
                "        pool.map(read, ['data/pooled.txt'])\n"
            ),
            "data/pooled.txt": "v1\n",
            "isolated.py": "import subprocess, sys\nsubprocess.run([sys.executable, '-I', '-c', 'pass'], check=True)\n",
            "shells.py": "import subprocess\nsubprocess.run(['true'], check=True)\n",
            "writer.py": "open('data/written.txt', 'w').close()\n",
            "fails.py": "raise SystemExit(1)\n",
        }
        for name, text in files.items():
            (root / name).write_text(text)
        # A pyc-only module: the compiled file stands without its source.
        (root / "compiled").mkdir()
        (root / "compiled" / "only.py").write_text("VALUE = 1\n")
        import py_compile

        py_compile.compile(str(root / "compiled" / "only.py"), cfile=str(root / "compiled" / "only.pyc"))
        (root / "compiled" / "only.py").unlink()

        def recompile(text: str) -> None:
            source = Path(temporary) / "only.py"
            source.write_text(text)
            py_compile.compile(str(source), cfile=str(root / "compiled" / "only.pyc"))

        (root / "pyc.py").write_text("import sys\nsys.path.insert(0, 'compiled')\nimport only\n")

        def gate(name: str, cmd: str) -> dict[str, Any]:
            return {"name": name, "cwd": ".", "cmd": cmd, "seconds": 0.1}

        gates = [
            gate("plain", '"$PYTHON" -B plain.py'),
            gate("import", '"$PYTHON" -B importer.py'),
            gate("pyc", '"$PYTHON" -B pyc.py'),
            gate("glob", '"$PYTHON" -B globber.py'),
            gate("listdir", '"$PYTHON" -B lister.py'),
            gate("pool", '"$PYTHON" -B pooled.py'),
            gate("isolated-child", '"$PYTHON" -B isolated.py'),
            gate("isolated-shell", '"$PYTHON" -I -B plain.py'),
            gate("program-child", '"$PYTHON" -B shells.py'),
            gate("program-shell", 'true && "$PYTHON" -B plain.py'),
            gate("writer", '"$PYTHON" -B writer.py'),
            gate("failure", '"$PYTHON" -B fails.py'),
        ]
        environment = run_gates.environment_for(None)
        environment["PYTHON"] = python
        environment.pop("PYTHONPATH", None)
        ledger = Path(temporary) / "ledger.json"

        def run(chosen: list[dict[str, Any]], host: dict[str, str] | None = None) -> dict[str, str]:
            verdicts: dict[str, str] = {}
            env = dict(environment, **(host or {}))
            outcome = run_gates.execute(chosen, env, root, ledger=ledger, ledger_out=ledger)
            for gate_result in outcome:
                verdicts[gate_result.gate["name"]] = gate_result.verdict
            return verdicts

        first = run(gates)
        expected_first = {gate["name"]: "PASS" for gate in gates}
        expected_first["failure"] = "FAIL"
        if first != expected_first:
            raise RuntimeError(f"first pass verdicts {first}")
        stored = load(ledger)
        traceable = {"plain", "import", "pyc", "glob", "listdir", "pool"}
        if set(stored) != traceable:
            raise RuntimeError(f"the ledger stores {sorted(stored)}, expected {sorted(traceable)}")
        if "compiled/only.pyc" not in stored["pyc"]["reads"]["files"]:
            raise RuntimeError(f"a pyc-only import is outside the read set: {stored['pyc']['reads']}")
        second = run(gates)
        expected_second = {name: ("SKIP" if name in traceable else verdict) for name, verdict in first.items()}
        if second != expected_second:
            raise RuntimeError(f"second pass verdicts {second}, expected {expected_second}")
        edits = {
            "plain": lambda: (root / "data" / "plain.txt").write_text("v2\n"),
            "import": lambda: (root / "pkg" / "helper.py").write_text("VALUE = 2\n"),
            "pyc": lambda: recompile("VALUE = 2\n"),
            "glob": lambda: (root / "data" / "globbed" / "b.txt").write_text(""),
            "listdir": lambda: (root / "data" / "listed" / "b.txt").write_text(""),
            "pool": lambda: (root / "data" / "pooled.txt").write_text("v2\n"),
        }
        for name, edit in edits.items():
            edit()
            verdicts = run([entry for entry in gates if entry["name"] in traceable])
            reran = {gate_name for gate_name, verdict in verdicts.items() if verdict != "SKIP"}
            if reran != {name}:
                raise RuntimeError(f"an edit read by {name} reran {sorted(reran)}")
        plain = [entry for entry in gates if entry["name"] == "plain"]
        edited = [dict(plain[0], cmd='"$PYTHON" -B -W error plain.py')]
        if run(edited) != {"plain": "PASS"}:
            raise RuntimeError("an edited command reused the stored key")
        if run(edited) != {"plain": "SKIP"}:
            raise RuntimeError("an unchanged command after its pass ran again")
        if run(edited, {"GOROROBA_LEDGER_PROBE": "host"}) != {"plain": "PASS"}:
            raise RuntimeError("a changed host identity reused the stored key")
        real_identity = host_identity.interpreter_identity

        def upgraded(python: str) -> list[Any]:
            path, (version, distributions) = real_identity(python)
            return [path, [version, [*distributions, ["planted-distribution", "1.0"]]]]

        with mock.patch.object(host_identity, "interpreter_identity", upgraded):
            if run(edited, {"GOROROBA_LEDGER_PROBE": "host"}) != {"plain": "PASS"}:
                raise RuntimeError("a changed interpreter distribution set reused the stored key")
        (root / "fails.py").write_text("raise SystemExit(0)\n")
        failing = [entry for entry in gates if entry["name"] == "failure"]
        run(failing)
        (root / "fails.py").write_text("raise SystemExit(1)\n")
        if run(failing) != {"failure": "FAIL"} or "failure" in load(ledger):
            raise RuntimeError("a failure after a pass kept the stored pass")
        shards = [Path(temporary) / f"shard-{index}.json" for index in range(2)]
        write(shards[0], {"plain": load(ledger)["plain"]}, ["plain"])
        write(shards[1], {}, ["glob"])
        merged, _selected = merge(ledger, shards)
        if "glob" in merged or "plain" not in merged or "import" not in merged:
            raise RuntimeError(f"a shard merge kept a dropped entry or lost a base entry: {sorted(merged)}")
    for command, escapes in (
        ('"$PYTHON" -B -W error x.py && "$PYTHON" y.py', False),
        ('"$PYTHON" -IB x.py', True),
        ('"$PYTHON" -W error -E x.py', True),
        ('"$PYTHON" x.py | sha256sum', True),
        ("sha256sum -c x", True),
        ('"$PYTHON" x.py; true', True),
    ):
        if (shell_untraceable(command) is not None) != escapes:
            raise RuntimeError(f"shell classification of {command!r} is wrong")
    print(
        "gate-ledger: open, import, pyc-only, glob, listdir and spawn-pool reads each rerun exactly their gate; "
        "-I children, -I shells, non-Python programs and repository writes never skip; a command or host change "
        "reruns, a failure stores nothing and removes the earlier pass, and a shard merge drops decided failures"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--self-test", action="store_true")
    commands = parser.add_subparsers(dest="command")
    merging = commands.add_parser("merge", help="overlay shard ledgers on a base ledger")
    merging.add_argument("out", type=Path)
    merging.add_argument("shards", type=Path, nargs="*")
    merging.add_argument("--base", type=Path)
    arguments = parser.parse_args(argv)
    if arguments.self_test:
        self_test()
        return 0
    if arguments.command == "merge":
        merged, selected = merge(arguments.base, arguments.shards)
        write(arguments.out, merged, selected)
        print(f"gate-ledger: {len(merged)} entries from {len(arguments.shards)} shard ledgers")
        return 0
    parser.error("give --self-test or merge")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
