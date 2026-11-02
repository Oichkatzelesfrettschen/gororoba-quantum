"""The gate manifest ci/gates.json and its one loader.

ci/gates.json lists the on-demand checks: retained-record replays, digest and registry checks, research-script
self-tests and the audit-marked tests (gate core-615). No workflow runs them; ``"$PYTHON" ci/run_gates.py`` runs
them when a pin, a producer script, an input or a source changes. A claim of docs/state/research_state.json cites a
gate by its id. This module is the only reader of the file: ci/run_gates.py, scripts/research_state.py,
ci/runner_image_records.py, ci/premerge_gates.py, ci/check_rocq_ci_pins.py and the manifest tests go through it.
"""

from __future__ import annotations

import ast
import json
import shlex
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
GATES = "ci/gates.json"
SCHEMA = "gororoba-ci-gates-v1"


def read(root: Path = ROOT) -> dict[str, Any]:
    """The parsed manifest at root/ci/gates.json."""
    document: dict[str, Any] = json.loads((root / GATES).read_text(encoding="utf-8"))
    return document


def gates(root: Path = ROOT) -> list[dict[str, Any]]:
    """The gate entries in file order; a repeated gate id is an error."""
    listed: list[dict[str, Any]] = read(root)["gates"]
    seen: set[str] = set()
    for gate in listed:
        if gate["name"] in seen:
            raise ValueError(f"gate {gate['name']} appears twice in {GATES}")
        seen.add(gate["name"])
    return listed


def commands(root: Path = ROOT) -> dict[str, str]:
    """Each gate id with its command."""
    return {gate["name"]: gate["cmd"] for gate in gates(root)}


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
