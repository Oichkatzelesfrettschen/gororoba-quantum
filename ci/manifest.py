"""The gate manifests and the one loader of gate ids.

ci/gates.json lists the checks every pull request and every push to main runs (the ``gates`` job of
.github/workflows/pr.yml). ci/replays.json lists the checks that reproduce a retained record or take longer than a
pull-request run allows; no workflow runs them, and ``"$PYTHON" ci/run_gates.py --manifest ci/replays.json`` runs
them on demand. Both files share one schema and one namespace of gate ids, so a claim of
docs/state/research_state.json cites a gate of either. This module is the only reader of those files: a consumer of
gate ids (ci/run_gates.py, scripts/research_state.py, ci/runner_image_records.py, the premerge check and the
manifest tests) goes through ``entries``, ``gates`` or ``all_gates``, so a gate that moves between the
files changes no consumer.

A tree without ci/replays.json holds an empty replay manifest.
"""

from __future__ import annotations

import ast
import json
import shlex
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
GATES = "ci/gates.json"
REPLAYS = "ci/replays.json"
MANIFESTS = (GATES, REPLAYS)
SCHEMA = "gororoba-ci-gates-v1"


def read(root: Path, relative: str) -> dict[str, Any]:
    """The parsed manifest at root/relative; ci/replays.json is empty where the tree has none."""
    if relative not in MANIFESTS:
        raise ValueError(f"{relative}: not one of {', '.join(MANIFESTS)}")
    path = root / relative
    if relative == REPLAYS and not path.is_file():
        return {"schema": SCHEMA, "gates": []}
    document: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    return document


def gates(root: Path = ROOT, relative: str = GATES) -> list[dict[str, Any]]:
    """The gate entries of one manifest in file order."""
    listed: list[dict[str, Any]] = read(root, relative)["gates"]
    return listed


def entries(root: Path = ROOT) -> dict[str, tuple[str, dict[str, Any]]]:
    """Every gate id of both manifests with the manifest that lists it and its entry; a repeated id is an error."""
    found: dict[str, tuple[str, dict[str, Any]]] = {}
    for relative in MANIFESTS:
        for gate in gates(root, relative):
            name = gate["name"]
            if name in found:
                raise ValueError(f"gate {name} appears in {found[name][0]} and {relative}")
            found[name] = (relative, gate)
    return found


def commands(root: Path = ROOT) -> dict[str, str]:
    """Each gate id of both manifests with its command."""
    return {name: gate["cmd"] for name, (_, gate) in entries(root).items()}


def all_gates(root: Path = ROOT) -> list[dict[str, Any]]:
    """Every entry of both manifests, for a consumer that reads fields of each gate rather than looking one up by id."""
    return [gate for _, gate in entries(root).values()]


def expand_cases(root: Path, listed: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Split registered independent cases before scheduling, preserving parent selection."""
    expanded = []
    for gate in listed:
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
