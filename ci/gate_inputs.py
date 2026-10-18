"""Select long replays from local import closure and reviewed dynamic input scopes.

The explicit manifest covers data globs, QPY and source digests that Python
imports cannot express. CI and dependency-pin changes invalidate every replay.
The standard library suffices so selection runs before dependency installation.
"""

from __future__ import annotations

import ast
import fnmatch
import json
import shlex
from pathlib import Path
from typing import Any

GLOBAL_INPUTS = ("ci/**", ".github/workflows/**", "requirements*.txt", "pyproject.toml", "**/AGENTS.md", "AGENTS.md")


def matches(path: str, pattern: str) -> bool:
    return fnmatch.fnmatchcase(path, pattern)


def module_index(root: Path) -> dict[str, set[Path]]:
    """Index repository modules once per selection."""
    modules: dict[str, set[Path]] = {}
    for path in root.rglob("*.py"):
        if any(part.startswith(".") for part in path.relative_to(root).parts):
            continue
        modules.setdefault(path.stem, set()).add(path)
        if path.name == "__init__.py":
            modules.setdefault(path.parent.name, set()).add(path)
    return modules


def dependencies(
    root: Path, gate: dict[str, Any], modules: dict[str, set[Path]], references: dict[Path, ast.Module]
) -> set[str]:
    """Follow all local imports, including function-local imports and source literals.

    Bare module names can resolve through sys.path mutations. Include every
    matching repository module rather than guessing which mutation ran first.
    """
    pending = []
    for token in shlex.split(gate["cmd"]):
        if token.endswith(".py"):
            pending.append((root / gate["cwd"] / token).resolve())
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
            references[path] = ast.parse(path.read_text(encoding="utf-8"), filename=relative)
        tree = references[path]
        for node in ast.walk(tree):
            names: list[str] = []
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [node.module or "", *(alias.name for alias in node.names)]
            elif isinstance(node, ast.Constant) and isinstance(node.value, str) and node.value.endswith(".py"):
                # Source manifests hash files without importing them.
                literal = Path(node.value)
                pending.extend(modules.get(literal.stem, ()))
                if not literal.is_absolute():
                    for parent in (root, path.parent, root / "gororoba_quantum", root / "scripts"):
                        candidate = (parent / literal).resolve()
                        if candidate.is_relative_to(root) and candidate.is_file():
                            pending.append(candidate)
            for name in names:
                pending.extend(modules.get(name.rsplit(".", 1)[-1], ()))
    return found


def affected_full(root: Path, gates: list[dict[str, Any]], changed: list[str]) -> set[str]:
    manifest: dict[str, list[str]] = json.loads((root / "ci/full_gate_inputs.json").read_text())["gates"]
    full = [gate for gate in gates if gate.get("tier", "pr") == "full"]
    expected = {gate["name"] for gate in full}
    if set(manifest) != expected:
        raise ValueError(f"full gate input coverage differs: {sorted(set(manifest) ^ expected)}")
    for name, patterns in manifest.items():
        if not isinstance(patterns, list) or any(
            not isinstance(pattern, str) or not pattern or pattern.startswith("/") or ".." in pattern.split("/")
            for pattern in patterns
        ):
            raise ValueError(f"{name}: input scopes must be checkout-relative glob strings")
    if any(matches(path, pattern) for path in changed for pattern in GLOBAL_INPUTS):
        return expected
    modules = module_index(root)
    for path in changed:
        if path.endswith(".py"):
            modules.setdefault(Path(path).stem, set()).add(root / path)
    references: dict[Path, ast.Module] = {}
    selected = set()
    for gate in full:
        patterns = manifest[gate["name"]]
        sources = dependencies(root, gate, modules, references)
        if any(path in sources or any(matches(path, pattern) for pattern in patterns) for path in changed):
            selected.add(gate["name"])
    return selected
