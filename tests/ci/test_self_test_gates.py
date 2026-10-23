"""Every group of the in-process CLI modules runs on exactly one pr gate, and core-615 skips each module.

tests/test_cli_self_tests.py groups its rows for gates core-self-test-NN, and tests/test_cli_record_checks.py
for gates core-record-check-NN.
"""

from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
# (module, its row table, the gate-name prefix of its groups).
MODULES = (
    ("tests/test_cli_self_tests.py", "SELF_TESTS", "core-self-test"),
    ("tests/test_cli_record_checks.py", "RECORD_CHECKS", "core-record-check"),
)


@pytest.mark.parametrize(("module", "table", "prefix"), MODULES)
def test_each_group_has_one_gate(module: str, table: str, prefix: str) -> None:
    spec = importlib.util.spec_from_file_location(f"{prefix}_table", ROOT / module)
    if spec is None or spec.loader is None:
        raise ImportError(module)
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    groups = {row[-1] for row in getattr(loaded, table)}
    gates = json.loads((ROOT / "ci/gates.json").read_text())["gates"]
    selected: dict[int, list[str]] = {}
    for gate in gates:
        if module not in gate["cmd"] or gate["name"] == "core-615":
            continue
        match = re.fullmatch(rf'"\$PYTHON" -B -W error -m pytest -q {re.escape(module)} -k group(\d\d)', gate["cmd"])
        if match is None or gate["name"] != f"{prefix}-{match.group(1)}" or gate.get("tier") != "pr":
            raise AssertionError(f"{gate['name']}: a {prefix} gate is pr tier and runs one group: {gate['cmd']}")
        selected.setdefault(int(match.group(1)), []).append(gate["name"])
    if set(selected) != groups or any(len(names) != 1 for names in selected.values()):
        raise AssertionError(f"groups {sorted(groups)} need one gate each; gates select {selected}")
    suite = next(gate for gate in gates if gate["name"] == "core-615")
    if f"--ignore={module}" not in suite["cmd"].split():
        raise AssertionError(f"core-615 must skip {module}, which its group gates run")
