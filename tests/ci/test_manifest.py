"""Contract for ci/manifest.py: both manifests share one namespace of gate ids, a tree without ci/replays.json holds
an empty replay manifest, a repeated id is refused, and registered cases split into independently named gates.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import manifest
import pytest

pytestmark = pytest.mark.audit

ROOT = Path(__file__).resolve().parents[2]
REQUIRED_FIELDS = {"cmd", "cwd", "name", "seconds", "tier"}


def write(root: Path, relative: str, listed: list[dict[str, Any]]) -> None:
    (root / relative).parent.mkdir(parents=True, exist_ok=True)
    (root / relative).write_text(json.dumps({"schema": manifest.SCHEMA, "gates": listed}))


def test_repository_gate_ids_are_unique_across_both_manifests() -> None:
    names = [gate["name"] for relative in manifest.MANIFESTS for gate in manifest.gates(ROOT, relative)]
    if len(names) != len(set(names)):
        raise AssertionError(
            f"gate ids repeated across the manifests: {sorted({n for n in names if names.count(n) > 1})}"
        )
    if set(manifest.entries(ROOT)) != set(names):
        raise AssertionError("entries() differs from the union of both manifests")


def test_repository_entries_carry_the_shared_shape() -> None:
    for relative in manifest.MANIFESTS:
        document = manifest.read(ROOT, relative)
        if document["schema"] != manifest.SCHEMA:
            raise AssertionError(f"{relative}: schema {document['schema']!r}")
        for gate in document["gates"]:
            if not REQUIRED_FIELDS <= set(gate) or gate["tier"] not in ("pr", "full"):
                raise AssertionError(f"{relative}: {gate['name']} lacks {REQUIRED_FIELDS - set(gate)} or holds a tier")


def test_a_tree_without_replays_holds_an_empty_replay_manifest(tmp_path: Path) -> None:
    write(tmp_path, manifest.GATES, [{"name": "only", "cwd": ".", "cmd": "true"}])
    if manifest.gates(tmp_path, manifest.REPLAYS) != [] or list(manifest.entries(tmp_path)) != ["only"]:
        raise AssertionError("a missing ci/replays.json is not empty")


def test_entries_name_the_manifest_of_each_gate(tmp_path: Path) -> None:
    write(tmp_path, manifest.GATES, [{"name": "fast", "cwd": ".", "cmd": "true"}])
    write(tmp_path, manifest.REPLAYS, [{"name": "slow", "cwd": ".", "cmd": "false"}])
    found = manifest.entries(tmp_path)
    if {name: where for name, (where, _) in found.items()} != {"fast": manifest.GATES, "slow": manifest.REPLAYS}:
        raise AssertionError(found)
    if manifest.commands(tmp_path) != {"fast": "true", "slow": "false"}:
        raise AssertionError(manifest.commands(tmp_path))


def test_a_gate_listed_in_both_manifests_is_refused(tmp_path: Path) -> None:
    write(tmp_path, manifest.GATES, [{"name": "twice", "cwd": ".", "cmd": "true"}])
    write(tmp_path, manifest.REPLAYS, [{"name": "twice", "cwd": ".", "cmd": "true"}])
    with pytest.raises(ValueError, match="twice appears in ci/gates.json and ci/replays.json"):
        manifest.entries(tmp_path)


def test_an_unknown_manifest_path_is_refused(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        manifest.read(tmp_path, "ci/other.json")


def test_case_expansion_names_one_gate_per_registered_case(tmp_path: Path) -> None:
    (tmp_path / "entry.py").write_text("CONTRACT_CASES: dict = {'first': first, 'second': second}\n")
    parent = {"name": "long", "cwd": ".", "cmd": '"$PYTHON" entry.py', "case_registry": "CONTRACT_CASES", "seconds": 10}
    expanded = manifest.expand_cases(tmp_path, [parent])
    if [gate["name"] for gate in expanded] != ["long--first", "long--second"]:
        raise AssertionError(expanded)
    if [gate["seconds"] for gate in expanded] != [5, 5] or {gate["parent"] for gate in expanded} != {"long"}:
        raise AssertionError(expanded)
    if [gate["cmd"] for gate in expanded] != ['"$PYTHON" entry.py --case first', '"$PYTHON" entry.py --case second']:
        raise AssertionError(expanded)


@pytest.mark.parametrize("malformed", ("{}", "{'first': first, 'first': second}", "{**other}"))
def test_a_malformed_case_registry_is_refused(tmp_path: Path, malformed: str) -> None:
    (tmp_path / "entry.py").write_text(f"CONTRACT_CASES: dict = {malformed}\n")
    parent = {"name": "long", "cwd": ".", "cmd": '"$PYTHON" entry.py', "case_registry": "CONTRACT_CASES"}
    with pytest.raises(ValueError):
        manifest.expand_cases(tmp_path, [parent])
