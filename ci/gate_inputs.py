"""Select long replays from local import closure and reviewed dynamic input scopes.

The explicit manifest covers data globs, QPY and source digests that Python
imports cannot express. CI and dependency-pin changes invalidate every replay.
The standard library and git suffice, so selection runs before dependency
installation.
"""

from __future__ import annotations

import ast
import fnmatch
import json
import os
import shlex
import subprocess
from pathlib import Path
from typing import Any

from gate_ledger import MANIFEST_FIELDS

GLOBAL_INPUTS = (
    "ci/**",
    ".github/**",
    "requirements*.txt",
    "**/requirements*.txt",
    "pyproject.toml",
    "**/AGENTS.md",
    "AGENTS.md",
)


# The files the pinned and replay venv cache keys hash (.github/workflows/ci.yml, pins-venv): a change
# to one changes the interpreter every gate runs under.
RUNTIME_INPUTS = (
    "requirements.txt",
    "ci/requirements-ci.txt",
    "ci/requirements-replay.txt",
    "ci/install_pins.sh",
    "ci/patches/**",
)


def matches(path: str, pattern: str) -> bool:
    return fnmatch.fnmatchcase(path, pattern)


def checkout_files(root: Path, pattern: str) -> list[Path]:
    """The files under ROOT matching PATTERN that git tracks or would track.

    ``git ls-files --cached --others --exclude-standard`` lists the tracked
    files and the untracked files .gitignore admits, so a new module counts
    before its commit while an ignored build tree, virtual environment or
    cache never does: the index holds the modules a clone of the commit plus
    the working changes holds, which is what CI's checkout holds.
    """
    completed = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z", "--cached", "--others", "--exclude-standard", "--", pattern],
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise ValueError(f"{root} is not a git work tree: {completed.stderr.decode(errors='replace').strip()}")
    names = {os.fsdecode(name) for name in completed.stdout.split(b"\0") if name}
    # A tracked file deleted from the working tree stays in the index until
    # the deletion is staged; the walk reads only files present on disk.
    return [root / name for name in sorted(names) if (root / name).is_file()]


def module_index(root: Path) -> dict[str, set[Path]]:
    """Index repository modules once per selection."""
    modules: dict[str, set[Path]] = {}
    for path in checkout_files(root, "*.py"):
        if any(part.startswith(".") for part in path.relative_to(root).parts):
            continue
        modules.setdefault(path.stem, set()).add(path)
        if path.name == "__init__.py":
            modules.setdefault(path.parent.name, set()).add(path)
    return modules


def references_of(tree: ast.Module) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """The module names a source imports and the ``.py`` string literals it names, in walk order."""
    names: list[str] = []
    literals: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            names.extend([node.module or "", *(alias.name for alias in node.names)])
        elif isinstance(node, ast.Constant) and isinstance(node.value, str) and node.value.endswith(".py"):
            literals.append(node.value)
    return tuple(names), tuple(literals)


def dependencies(
    root: Path,
    gate: dict[str, Any],
    modules: dict[str, set[Path]],
    references: dict[Path, tuple[tuple[str, ...], tuple[str, ...]]],
) -> set[str]:
    """Follow all local imports, including function-local imports and source literals.

    Bare module names can resolve through sys.path mutations. Include every
    matching repository module rather than guessing which mutation ran first.
    ``references`` caches each file's extracted names across the gates of one
    selection, so a source is parsed and walked once however many gates import it.
    """
    pending = []
    for token in shlex.split(gate["cmd"]):
        source = token.split("::", 1)[0]
        if source.endswith(".py"):
            pending.append((root / gate["cwd"] / source).resolve())
    found: set[str] = set()
    while pending:
        path = pending.pop()
        if not path.is_relative_to(root):
            raise ValueError(f"gate source leaves checkout: {path}")
        relative = path.relative_to(root).as_posix()
        if relative in found:
            continue
        found.add(relative)
        if not path.is_file():
            continue
        if path not in references:
            references[path] = references_of(ast.parse(path.read_text(encoding="utf-8"), filename=relative))
        names, literals = references[path]
        for value in literals:
            # Source manifests hash files without importing them.
            literal = Path(value)
            pending.extend(modules.get(literal.stem, ()))
            if not literal.is_absolute():
                for parent in (root, path.parent, root / "gororoba_quantum", root / "scripts"):
                    candidate = (parent / literal).resolve()
                    if candidate.is_relative_to(root) and candidate.is_file():
                        pending.append(candidate)
        for name in names:
            pending.extend(modules.get(name.rsplit(".", 1)[-1], ()))
    return found


def full_gate_scopes(root: Path, gates: list[dict[str, Any]]) -> dict[str, list[str]]:
    """The reviewed input globs of every full-tier gate, from ci/full_gate_inputs.json."""
    manifest: dict[str, list[str]] = json.loads((root / "ci/full_gate_inputs.json").read_text())["gates"]
    expected = {gate["name"] for gate in gates if gate.get("tier", "pr") == "full"}
    if set(manifest) != expected:
        raise ValueError(f"full gate input coverage differs: {sorted(set(manifest) ^ expected)}")
    for name, patterns in manifest.items():
        if not isinstance(patterns, list) or any(
            not isinstance(pattern, str) or not pattern or pattern.startswith("/") or ".." in pattern.split("/")
            for pattern in patterns
        ):
            raise ValueError(f"{name}: input scopes must be checkout-relative glob strings")
    return manifest


def affected_full(root: Path, gates: list[dict[str, Any]], changed: list[str]) -> set[str]:
    manifest = full_gate_scopes(root, gates)
    full = [gate for gate in gates if gate.get("tier", "pr") == "full"]
    expected = {gate["name"] for gate in full}
    if any(matches(path, pattern) for path in changed for pattern in GLOBAL_INPUTS):
        return expected
    modules = module_index(root)
    for path in changed:
        if path.endswith(".py"):
            modules.setdefault(Path(path).stem, set()).add(root / path)
    references: dict[Path, tuple[tuple[str, ...], tuple[str, ...]]] = {}
    selected = set()
    for gate in full:
        patterns = manifest[gate["name"]]
        sources = dependencies(root, gate, modules, references)
        if any(path in sources or any(matches(path, pattern) for pattern in patterns) for path in changed):
            selected.add(gate["name"])
    return selected


def command_paths(root: Path, gate: dict[str, Any]) -> set[str]:
    """The checkout paths a gate command names as operands, relative to the checkout root.

    A gate checks the records and directories its command names, so a change at or under one of
    them reaches the gate whether or not the gate's sources import anything changed.
    """
    try:
        words = shlex.split(gate["cmd"])
    except ValueError:
        return set()
    named = set()
    for word in words:
        if word.startswith("-") or "$" in word or "=" in word:
            continue
        candidate = (root / gate["cwd"] / word.split("::", 1)[0]).resolve()
        if candidate != root.resolve() and candidate.is_relative_to(root.resolve()):
            named.add(candidate.relative_to(root.resolve()).as_posix())
    return named


def ledger_reaches(reads: dict[str, list[Any]], changed: set[str], listed: set[str]) -> bool:
    """Whether a traced read set (ci/gate_ledger.py) reads a changed path or lists an added or removed one.

    An edited file reaches a gate that read it; an added or removed file also reaches a gate that
    listed its directory, matched it with a glob or probed its existence. Python files are left to the
    import closure, since every gate that imports a sibling lists the module directory.
    """
    probed = set(reads.get("files", [])) | set(reads.get("links", [])) | {path for _, path in reads.get("stats", [])}
    if changed & probed:
        return True
    directories = set(reads.get("dirs", []))
    patterns = [pattern for _, pattern in reads.get("globs", [])]
    for path in listed:
        if path.endswith(".py"):
            continue
        if (os.path.dirname(path) or ".") in directories or any(matches(path, pattern) for pattern in patterns):
            return True
    return False


def affected(
    root: Path,
    gates: list[dict[str, Any]],
    changed: list[str],
    listed: list[str],
    traced: dict[str, dict[str, Any]] | None = None,
    base: list[dict[str, Any]] | None = None,
) -> set[str]:
    """The gates a change reaches: every gate when it changes the pinned runtime, else each gate whose
    manifest entry differs from ``base`` (the merge base's ci/gates.json gates), and each gate reached
    through its import closure, the paths its command names, the reviewed scopes of a full-tier gate, or
    the read set a traced run recorded (``traced`` maps a gate or case name to its ledger entry).
    ``changed`` holds every changed path and ``listed`` the added and removed ones.
    """
    if any(matches(path, pattern) for path in changed for pattern in RUNTIME_INPUTS):
        return {gate["name"] for gate in gates}
    before = {gate["name"]: {field: gate.get(field) for field in MANIFEST_FIELDS} for gate in base or []}
    scopes = full_gate_scopes(root, gates)
    modules = module_index(root)
    for path in changed:
        if path.endswith(".py"):
            modules.setdefault(Path(path).stem, set()).add(root / path)
    references: dict[Path, tuple[tuple[str, ...], tuple[str, ...]]] = {}
    edited, created = set(changed), set(listed)
    # Each changed path with every directory above it, so a command operand naming a directory matches.
    ancestry = {ancestor for path in edited for ancestor in [path, *(p.as_posix() for p in Path(path).parents)]}
    entries = traced or {}
    selected = set()
    for gate in gates:
        name = gate["name"]
        sources = dependencies(root, gate, modules, references) | command_paths(root, gate)
        patterns = scopes.get(name, [])
        reads = [entry["reads"] for key, entry in entries.items() if key == name or key.startswith(f"{name}--")]
        if (
            (base is not None and before.get(name) != {field: gate.get(field) for field in MANIFEST_FIELDS})
            or not ancestry.isdisjoint(sources)
            or any(matches(path, pattern) for path in edited for pattern in patterns)
            or any(ledger_reaches(read, edited, created) for read in reads)
        ):
            selected.add(name)
    return selected


def expand_cases(root: Path, gates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Split registered independent cases before scheduling, preserving parent selection."""
    expanded = []
    for gate in gates:
        registry = gate.get("case_registry")
        if registry is None:
            expanded.append(gate)
            continue
        sources = [token for token in shlex.split(gate["cmd"]) if token.endswith(".py")]
        if len(sources) != 1:
            raise ValueError(f"{gate['name']}: case registry needs one Python entrypoint")
        path = (root / gate["cwd"] / sources[0]).resolve()
        if not path.is_relative_to(root):
            raise ValueError("case entrypoint leaves checkout")
        tree = ast.parse(path.read_text(encoding="utf-8"))
        declarations = [
            node.value
            for node in tree.body
            if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id == registry
        ]
        if len(declarations) != 1 or not isinstance(declarations[0], ast.Dict):
            raise ValueError(f"{gate['name']}: registry must be a static annotated dictionary")
        names = [ast.literal_eval(key) for key in declarations[0].keys if key is not None]
        if len(names) != len(declarations[0].keys) or not names or len(set(names)) != len(names):
            raise ValueError(f"{gate['name']}: case names must be nonempty and distinct")
        if any(not isinstance(name, str) or not name.isidentifier() for name in names):
            raise ValueError(f"{gate['name']}: case names must be identifiers")
        measured = gate.get("case_seconds", {})
        if not isinstance(measured, dict) or set(measured) - set(names):
            raise ValueError(f"{gate['name']}: timings name an unregistered case")
        for name in names:
            expanded.append(
                dict(
                    gate,
                    name=f"{gate['name']}--{name}",
                    parent=gate["name"],
                    cmd=gate["cmd"] + " --case " + shlex.quote(name),
                    seconds=float(measured.get(name, float(gate.get("seconds", 10)) / len(names))),
                )
            )
    return expanded
