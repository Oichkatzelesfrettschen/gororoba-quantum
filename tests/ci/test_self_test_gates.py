"""Every group of tests/test_cli_self_tests.py runs on exactly one pr gate, and core-615 skips the module."""

from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE = "tests/test_cli_self_tests.py"


def test_each_self_test_group_has_one_gate() -> None:
    spec = importlib.util.spec_from_file_location("cli_self_tests_table", ROOT / MODULE)
    if spec is None or spec.loader is None:
        raise ImportError(MODULE)
    table = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(table)
    groups = {group for _, _, group in table.SELF_TESTS}
    gates = json.loads((ROOT / "ci/gates.json").read_text())["gates"]
    selected: dict[int, list[str]] = {}
    for gate in gates:
        if MODULE not in gate["cmd"] or gate["name"] == "core-615":
            continue
        match = re.fullmatch(rf'"\$PYTHON" -B -W error -m pytest -q {re.escape(MODULE)} -k group(\d\d)', gate["cmd"])
        if match is None or gate["name"] != f"core-self-test-{match.group(1)}" or gate.get("tier") != "pr":
            raise AssertionError(f"{gate['name']}: a self-test gate is pr tier and runs one group: {gate['cmd']}")
        selected.setdefault(int(match.group(1)), []).append(gate["name"])
    if set(selected) != groups or any(len(names) != 1 for names in selected.values()):
        raise AssertionError(f"groups {sorted(groups)} need one gate each; gates select {selected}")
    suite = next(gate for gate in gates if gate["name"] == "core-615")
    if f"--ignore={MODULE}" not in suite["cmd"].split():
        raise AssertionError("core-615 must skip the module its group gates run")
