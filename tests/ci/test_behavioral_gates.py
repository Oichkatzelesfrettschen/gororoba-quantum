"""The behavioral suite's gates partition tests/: each test module runs on exactly one of them.

core-615 runs pytest over tests/ and ignores the paths its sibling gates run, so a new test module joins
core-615 until a measurement moves it. Each core-behavior-NN gate runs a list of paths that core-615
ignores, and no path appears on two gates; the in-process CLI modules are the ignored paths whose
group gates tests/ci/test_self_test_gates.py checks.
"""

from __future__ import annotations

import json
import re
import shlex
from pathlib import Path

import pytest

pytestmark = pytest.mark.audit

ROOT = Path(__file__).resolve().parents[2]
PREFIX = '"$PYTHON" -B -W error -m pytest -n auto --dist loadgroup --durations=15 '
GROUPED = ("tests/test_cli_self_tests.py", "tests/test_cli_record_checks.py")
SPLIT = re.compile(r"core-behavior-\d\d")


def gates() -> dict[str, dict[str, str]]:
    return {gate["name"]: gate for gate in json.loads((ROOT / "ci/gates.json").read_text())["gates"]}


def arguments(gate: dict[str, str]) -> list[str]:
    if not gate["cmd"].startswith(PREFIX) or gate.get("workers") != "all" or gate["cwd"] != ".":
        raise AssertionError(f"{gate['name']}: a behavioral gate runs {PREFIX!r} from the root on all workers")
    return shlex.split(gate["cmd"][len(PREFIX) :])


def module_paths(target: str) -> set[str]:
    path = ROOT / target
    if path.is_dir():
        return {str(p.relative_to(ROOT)) for p in path.rglob("test_*.py")}
    if not path.is_file() or not path.name.startswith("test_"):
        raise AssertionError(f"{target} is not a test module or directory")
    return {target}


def test_split_gates_run_exactly_what_core_615_ignores() -> None:
    manifest = gates()
    suite = arguments(manifest["core-615"])
    if suite[-1] != "tests" or not all(arg.startswith("--ignore=") for arg in suite[:-1]):
        raise AssertionError(f"core-615 runs tests/ with --ignore paths only: {suite}")
    ignored = [arg.removeprefix("--ignore=") for arg in suite[:-1]]
    if not set(GROUPED) <= set(ignored):
        raise AssertionError(f"core-615 must ignore {GROUPED}")
    owners: dict[str, list[str]] = {}
    for name, gate in manifest.items():
        if SPLIT.fullmatch(name) is None:
            continue
        targets = arguments(gate)
        if not targets or any(target.startswith("-") for target in targets):
            raise AssertionError(f"{name}: a split gate names only test paths: {targets}")
        for target in targets:
            owners.setdefault(target, []).append(name)
    shared = {target: names for target, names in owners.items() if len(names) > 1}
    if shared:
        raise AssertionError(f"paths on more than one split gate: {shared}")
    if set(owners) != set(ignored) - set(GROUPED):
        raise AssertionError(
            f"core-615 ignores {sorted(set(ignored) - set(GROUPED) - set(owners))} that no split gate runs; "
            f"split gates run {sorted(set(owners) - set(ignored))} that core-615 also runs"
        )
    # Overlapping targets (a directory and a module inside it) would run a module twice.
    seen: dict[str, str] = {}
    for target in [*GROUPED, *owners]:
        for module in module_paths(target):
            if module in seen:
                raise AssertionError(f"{module} runs under both {seen[module]} and {target}")
            seen[module] = target


def test_split_gates_hold_a_tier() -> None:
    for name, gate in gates().items():
        if SPLIT.fullmatch(name) is not None and gate.get("tier") not in ("pr", "full"):
            raise AssertionError(f"{name}: tier {gate.get('tier')!r}")
