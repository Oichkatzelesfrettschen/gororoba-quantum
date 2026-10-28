"""Contracts of the Ascella two-photon associator request: the frozen case, its binding and its analysis."""

from __future__ import annotations

import json
from pathlib import Path

import ascella_associator_case as case


def test_retained_request_rebuilds_and_binds() -> None:
    if case.check() != 0:
        raise AssertionError("the frozen request does not check")


def test_preregistered_pairs_and_visibility_model() -> None:
    if case.PLUS_PAIRS != ("12", "03") or case.MINUS_PAIRS != ("01", "23"):
        raise AssertionError(f"pair labels {case.PLUS_PAIRS}, {case.MINUS_PAIRS}")
    if abs(case.predicted_difference(1.0) - 2.0) > 1e-12 or abs(case.predicted_difference(0.0)) > 1e-12:
        raise AssertionError("visibility model endpoints")


def _state(occupied: tuple[int, ...]) -> str:
    return ",".join("1" if mode in occupied else "0" for mode in range(case.MODES))


def test_analysis_recovers_ideal_and_excludes_outside_events(tmp_path: Path) -> None:
    manifest = json.loads((case.CASE / "cases.json").read_text())
    iterations = []
    for setting in manifest["settings"]:
        counts = {_state((int(p[0]), int(p[1]))): 500 for p in setting["ideal"]["two_click_law_indistinguishable"]}
        counts[_state((0, 9))] = 7
        iterations.append({"counts": counts})
    (tmp_path / "cases.json").write_text(json.dumps(manifest))
    (tmp_path / "results.json").write_text(json.dumps({"iterations": iterations}))
    record = case.analyze(tmp_path)
    if record["associator"]["Delta"] != 2.0 or record["control"]["Delta"] != 0.0:
        raise AssertionError(f"ideal counts give {record}")
    if record["excluded_events"] != 7 * 8:
        raise AssertionError("events outside the logical block were not excluded")
