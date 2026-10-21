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

tests/ci/test_gate_ledger.py plants every read kind and every escape.
"""

from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
import re
import shlex
import stat
import tempfile
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
TRACER = Path(__file__).resolve().parent / "read_trace"
SCHEMA = "gororoba-gate-ledger-v2"
# Manifest fields that change what a gate runs; seconds and tier only schedule it.
MANIFEST_FIELDS = ("cmd", "cwd", "runtime", "workers", "requires", "parent", "case_registry")
# The shell expands globs, tildes and parameters before Python starts, so a
# command holding one reads paths no traced process lists.
SHELL_METACHARACTERS = ("|", ";", ">", "<", "`", "$", "\n", "&", "*", "?", "[", "~", "(", ")")
PYTHON_WORD = "$PYTHON"
# A leading NAME=value sets the child's environment only; the command string,
# and so the assignment, is part of every gate key through MANIFEST_FIELDS.
ASSIGNMENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]*=")
ESCAPING_ASSIGNMENTS = frozenset(("PYTHON", "PYTHONPATH", "PYTHONHOME", "PYTHONSTARTUP"))
# Interpreter and lint caches appear in directory listings as gates run; their
# contents are derived from the sources the read set already hashes.
CACHE_NAMES = frozenset(("__pycache__", ".mypy_cache", ".ruff_cache", ".pytest_cache"))


FILE_TYPES = ((stat.S_ISREG, "file"), (stat.S_ISDIR, "directory"), (stat.S_ISLNK, "link"))


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
    plain = command.replace('"$PYTHON"', "\0").replace("&&", "\0")
    if any(mark in plain for mark in SHELL_METACHARACTERS):
        return "shell command beyond $PYTHON invocations joined by &&"
    for segment in command.split("&&"):
        try:
            words = shlex.split(segment)
        except ValueError:
            return "shell command does not parse"
        while words and ASSIGNMENT.match(words[0]):
            name = words[0].partition("=")[0]
            if name in ESCAPING_ASSIGNMENTS or name.startswith("GOROROBA_READ_TRACE"):
                return f"{name}= replaces the interpreter or the tracer path"
            words = words[1:]
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
    probes: set[tuple[int, str]] = set()
    links: set[str] = set()
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
            elif kind in ("s", "l"):
                probes.add((int(kind == "s"), rest))
            elif kind == "k":
                links.add(rest)
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
        "stats": [list(item) for item in sorted(probes)],
        "links": sorted(links),
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

    def status(self, follow: int, name: str) -> str:
        """The path's existence and file type as os.stat (follow) or os.lstat sees it."""
        key = ("s" if follow else "l", name)
        if key not in self.memo:
            try:
                mode = (os.stat if follow else os.lstat)(self.root / name).st_mode
            except FileNotFoundError:
                self.memo[key] = "absent"
            except NotADirectoryError:
                self.memo[key] = "absent"
            else:
                self.memo[key] = next(
                    (label for test, label in FILE_TYPES if test(mode)),
                    "other",
                )
        return str(self.memo[key])

    def link(self, name: str) -> str:
        key = ("k", name)
        if key not in self.memo:
            try:
                self.memo[key] = "link " + os.readlink(self.root / name)
            except FileNotFoundError:
                self.memo[key] = "absent"
            except OSError:
                self.memo[key] = "not a link"
        return str(self.memo[key])

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
        "stats": [[follow, name, content.status(follow, name)] for follow, name in reads["stats"]],
        "links": {name: content.link(name) for name in reads["links"]},
    }
    return hashlib.sha256(json.dumps(components, sort_keys=True).encode()).hexdigest()


def valid_entry(entry: Any) -> bool:
    if not isinstance(entry, dict) or not isinstance(entry.get("key"), str):
        return False
    reads = entry.get("reads")
    if not isinstance(reads, dict) or set(reads) != {"files", "dirs", "globs", "stats", "links"}:
        return False

    def names(value: Any) -> bool:
        return isinstance(value, list) and all(isinstance(name, str) for name in value)

    def pairs(value: Any) -> bool:
        return isinstance(value, list) and all(
            isinstance(item, list) and len(item) == 2 and isinstance(item[0], int) and isinstance(item[1], str)
            for item in value
        )

    return (
        names(reads["files"])
        and names(reads["dirs"])
        and names(reads["links"])
        and pairs(reads["globs"])
        and pairs(reads["stats"])
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    merging = commands.add_parser("merge", help="overlay shard ledgers on a base ledger")
    merging.add_argument("out", type=Path)
    merging.add_argument("shards", type=Path, nargs="*")
    merging.add_argument("--base", type=Path)
    arguments = parser.parse_args(argv)
    merged, selected = merge(arguments.base, arguments.shards)
    write(arguments.out, merged, selected)
    print(f"gate-ledger: {len(merged)} entries from {len(arguments.shards)} shard ledgers")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
