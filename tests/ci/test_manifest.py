"""Contract for ci/manifest.py: every entry of ci/gates.json carries the shared fields, a repeated id is refused,
and registered cases split into independently named gates.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import manifest
import pytest

pytestmark = pytest.mark.audit

ROOT = Path(__file__).resolve().parents[2]
REQUIRED_FIELDS = {"cmd", "cwd", "name", "seconds"}


def write(root: Path, listed: list[dict[str, Any]]) -> None:
    (root / manifest.GATES).parent.mkdir(parents=True, exist_ok=True)
    (root / manifest.GATES).write_text(json.dumps({"schema": manifest.SCHEMA, "gates": listed}))


def test_repository_entries_carry_the_shared_shape() -> None:
    document = manifest.read(ROOT)
    if document["schema"] != manifest.SCHEMA:
        raise AssertionError(f"schema {document['schema']!r}")
    for gate in manifest.gates(ROOT):
        if not REQUIRED_FIELDS <= set(gate):
            raise AssertionError(f"{gate['name']} lacks {REQUIRED_FIELDS - set(gate)}")


def test_commands_map_each_gate_id(tmp_path: Path) -> None:
    write(tmp_path, [{"name": "fast", "cwd": ".", "cmd": "true"}, {"name": "slow", "cwd": ".", "cmd": "false"}])
    if manifest.commands(tmp_path) != {"fast": "true", "slow": "false"}:
        raise AssertionError(manifest.commands(tmp_path))


def test_a_repeated_gate_id_is_refused(tmp_path: Path) -> None:
    write(tmp_path, [{"name": "twice", "cwd": ".", "cmd": "true"}, {"name": "twice", "cwd": ".", "cmd": "true"}])
    with pytest.raises(ValueError, match="twice appears twice"):
        manifest.gates(tmp_path)


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
