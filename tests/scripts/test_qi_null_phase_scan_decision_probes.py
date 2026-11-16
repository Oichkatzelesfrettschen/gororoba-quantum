"""Contracts of the decision-rule probe scripts under docs/evidence/qi-null-phase-scan-decision-probes/: the retained
rule-R5 records are written only by modes that pin R5, and a run of the current rule writes R6-named files.

The generator's decisions are stubbed: the tests check which rule a mode passes and which file it writes."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest
import qi_pathion_null_phase_scan_cases as ps

ROOT = Path(__file__).resolve().parents[2]
PROBES = ROOT / "docs/evidence/qi-null-phase-scan-decision-probes"
R5_FILES = {"coverage.json", "nulls.json", "separation_calibration.json"}


def _expect(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _load(name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(f"probe_{name}", PROBES / f"{name}.py")
    if spec is None or spec.loader is None:
        raise AssertionError(f"{name} does not load")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _serial(function: Any, items: list[Any], min_items: int = 2) -> list[Any]:
    return [function(item) for item in items]


@pytest.fixture
def calibrate(monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    module = _load("calibrate_separation")
    monkeypatch.setattr(ps, "build_tables", lambda: 0)
    monkeypatch.setattr(ps, "oc_seed", lambda index=0: 7)
    return module


@pytest.fixture
def probe(monkeypatch: pytest.MonkeyPatch) -> tuple[ModuleType, list[tuple[float, ...]]]:
    module = _load("probe_decision")
    seen: list[tuple[float, ...]] = []

    def decide(batches: Any, matrix_of: Any, flips: tuple[float, ...] = ps.FLIP_GRID, **_: Any) -> dict[str, Any]:
        seen.append(flips)
        return {"label": "exact_parabola", "numbers": {"center_contrast": [0.0], "chi2": None}}

    monkeypatch.setattr(ps, "build_tables", lambda: 0)
    monkeypatch.setattr(ps, "predecessor_matrix", lambda: None)
    monkeypatch.setattr(ps, "truth_row", lambda *a, **k: {ps.CENTER: {"visibility": 0.5, "contrast": 0.0}})
    monkeypatch.setattr(ps, "planted_batches", lambda row: [{"splits": [0.0]}])
    monkeypatch.setattr(ps, "decide", decide)
    monkeypatch.setattr(module, "ordered_map", _serial)
    monkeypatch.setattr(module, "q4_one", lambda item: {"world": item[0]})
    return module, seen


@pytest.mark.parametrize(
    ("mode", "name", "flips"),
    [
        ("coverage", "coverage_r6.json", ps.FLIP_GRID),
        ("nulls", "nulls_r6.json", ps.FLIP_GRID),
        ("coverage-r5", "coverage.json", (0.0,)),
        ("nulls-r5", "nulls.json", (0.0,)),
    ],
)
def test_a_probe_mode_writes_the_file_of_its_rule(
    probe: tuple[ModuleType, list[tuple[float, ...]]], tmp_path: Path, mode: str, name: str, flips: tuple[float, ...]
) -> None:
    module, seen = probe
    module.main([mode, "--out", str(tmp_path)])
    _expect(sorted(p.name for p in tmp_path.iterdir()) == [name], f"{mode} wrote {list(tmp_path.iterdir())}")
    _expect(bool(seen) and all(f == flips for f in seen), f"{mode} fitted flips {set(seen)}")


def test_the_current_rule_of_a_probe_writes_no_retained_r5_file(
    probe: tuple[ModuleType, list[tuple[float, ...]]], tmp_path: Path
) -> None:
    module, _ = probe
    for mode in ("coverage", "nulls", "q4-zero"):
        module.main([mode, "--out", str(tmp_path)])
    written = {p.name for p in tmp_path.iterdir()}
    _expect(written == {"coverage_r6.json", "nulls_r6.json", "q4_zero.json"}, f"wrote {written}")
    _expect(not written & R5_FILES, f"the current rule wrote {written & R5_FILES}")


def test_a_probe_run_without_a_mode_writes_nothing(
    probe: tuple[ModuleType, list[tuple[float, ...]]], tmp_path: Path
) -> None:
    module, _ = probe
    for argv in ([], ["bogus"]):
        with pytest.raises(SystemExit):
            module.main([*argv, "--out", str(tmp_path)])
    _expect(not list(tmp_path.iterdir()), "an invalid invocation wrote a file")


def test_the_r6_calibration_writes_only_its_own_file(
    calibrate: ModuleType, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    calls: list[dict[str, Any]] = []

    def characteristics(**kwargs: Any) -> dict[str, Any]:
        calls.append(kwargs)
        return {"label_counts": {"exact gates": {"offset_absent": 2}}}

    monkeypatch.setattr(ps, "operating_characteristics", characteristics)
    calibrate.main(["r6", "--index", "12", "--out", str(tmp_path)])
    _expect([p.name for p in tmp_path.iterdir()] == ["separation_calibration_r6.json"], "wrong r6 output")
    _expect(all(set(call) == {"index", "separation"} and call["index"] == 12 for call in calls), f"{calls}")


def test_a_calibration_without_a_rule_or_an_r6_index_writes_nothing(calibrate: ModuleType, tmp_path: Path) -> None:
    for argv in ([], ["r6"], ["r5", "--index", "10"]):
        with pytest.raises(SystemExit):
            calibrate.main([*argv, "--out", str(tmp_path)])
    _expect(not list(tmp_path.iterdir()), "an invalid invocation wrote a file")


def test_the_r5_calibration_pins_the_historical_rule(
    calibrate: ModuleType, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    items: list[tuple[Any, ...]] = []

    def worker(item: tuple[Any, ...]) -> dict[str, int]:
        items.append(item)
        return {"offset_absent": item[4] - item[3]}

    monkeypatch.setattr(ps, "oc_worker", worker)
    monkeypatch.setattr(calibrate, "ordered_map", _serial)
    calibrate.main(["r5", "--out", str(tmp_path)])
    _expect([p.name for p in tmp_path.iterdir()] == ["separation_calibration.json"], "wrong r5 output")
    names = [n for n in ps.TRUTHS if n not in calibrate.R5_ADDED] + list(ps.MIXED)
    _expect(len(names) == 25, f"{len(names)} scenarios")
    _expect(all(item[7] == (0.0,) for item in items), "r5 fits a flip")
    _expect(all(item[5] == ps.KIND_MARGIN for item in items), "r5 changes the margin")
    _expect({(item[1], item[2]) for item in items} == {(n, i) for i, n in enumerate(names)}, "r5 positions")
    _expect({item[1] for item in items} == set(names), "r5 scenario set")
    _expect(sum(item[4] - item[3] for item in items if item[1] == names[0]) == 3 * 500, "r5 series count")
