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


def _iterations(manifest: dict, visibility: float, flip_control: bool = False) -> list[dict]:
    """Counts proportional to the mixture law of each setting, plus 7 events outside the logical block."""
    iterations = []
    for setting in manifest["settings"]:
        law = case.two_click_law(case.route_operator(setting["block"], setting["route"]), visibility)
        if flip_control and setting["block"] == "control" and setting["route"] == "Lab":
            law = case.two_click_law(case.route_operator("associator", "LaLb"), visibility)
        counts = {_state((int(p[0]), int(p[1]))): round(100000 * v) for p, v in law.items() if v > 1e-12}
        counts[_state((0, 9))] = 7
        iterations.append({"counts": counts})
    return iterations


def _analyze(tmp_path: Path, iterations: list[dict], hom: float | None) -> dict:
    manifest = json.loads((case.CASE / "cases.json").read_text())
    (tmp_path / "cases.json").write_text(json.dumps(manifest))
    (tmp_path / "results.json").write_text(json.dumps({"iterations": iterations}))
    if hom is not None:
        (tmp_path / "submission.json").write_text(json.dumps({"perfs_at_plan": {"HOM (%)": hom}}))
    return case.analyze(tmp_path)


def test_closure_holds_at_any_visibility_and_needs_no_hom(tmp_path: Path) -> None:
    manifest = json.loads((case.CASE / "cases.json").read_text())
    record = _analyze(tmp_path, _iterations(manifest, 0.6), None)
    decisions = record["decisions"]
    if decisions["associator_realised"] is not True or decisions["visibility_closure"] is not True:
        raise AssertionError(f"V = 0.6 counts fail the closure: {decisions}")
    if abs(decisions["compensated_contrast"] - 1) > 1e-4 or abs(decisions["in_situ_visibility"] - 0.6) > 1e-4:
        raise AssertionError(f"compensation or in-situ visibility off: {decisions}")
    if decisions["hom_comparison"] is not None or record["excluded_events"] != 7 * 8:
        raise AssertionError("HOM comparison without a submission record, or exclusions miscounted")
    if record["excluded_by_cause"] != {
        "three_or_more_clicks": 0,
        "two_clicks_outside_block": 56,
        "fewer_than_two_clicks": 0,
    }:
        raise AssertionError(f"exclusion causes {record['excluded_by_cause']}")
    if record["multiphoton_estimate"] is not None:
        raise AssertionError("a multiphoton estimate without a recorded transmittance")


def test_multiphoton_estimate_scales_three_click_events_by_the_loss_ratio(tmp_path: Path) -> None:
    manifest = json.loads((case.CASE / "cases.json").read_text())
    iterations = _iterations(manifest, 0.875)
    for entry in iterations:
        entry["counts"][_state((0, 1, 2))] = 2
    (tmp_path / "cases.json").write_text(json.dumps(manifest))
    (tmp_path / "results.json").write_text(json.dumps({"iterations": iterations}))
    (tmp_path / "submission.json").write_text(
        json.dumps({"perfs_at_plan": {"HOM (%)": 87.34, "Transmittance (%)": 5.2}})
    )
    record = case.analyze(tmp_path)
    estimate = record["multiphoton_estimate"]
    if record["excluded_by_cause"]["three_or_more_clicks"] != 16 or estimate is None:
        raise AssertionError(f"three-click count or estimate {record['excluded_by_cause']}, {estimate}")
    if abs(estimate["estimated_lossy_events"] - 16 * 3 * 0.948 / 0.052) > 1e-6:
        raise AssertionError(f"loss ratio {estimate}")


def test_hom_comparison_is_descriptive_and_reads_the_submission(tmp_path: Path) -> None:
    manifest = json.loads((case.CASE / "cases.json").read_text())
    record = _analyze(tmp_path, _iterations(manifest, 0.8), 87.28)
    comparison = record["decisions"]["hom_comparison"]
    if comparison is None or comparison["within_tolerance"] is not False:
        raise AssertionError(f"V = 0.80 against HOM 87.28 % should depart: {comparison}")
    if record["decisions"]["visibility_closure"] is not True:
        raise AssertionError("the closure depends on the HOM figure")


def test_route_dependent_error_breaks_the_closure(tmp_path: Path) -> None:
    manifest = json.loads((case.CASE / "cases.json").read_text())
    record = _analyze(tmp_path, _iterations(manifest, 0.875, flip_control=True), None)
    if record["decisions"]["visibility_closure"] is not False:
        raise AssertionError(f"a flipped control route passes the closure: {record['decisions']}")


def test_truncated_block_leaves_decisions_undecided(tmp_path: Path) -> None:
    manifest = json.loads((case.CASE / "cases.json").read_text())
    iterations = _iterations(manifest, 0.875)[:6] + [{"missing": True}, {"missing": True}]
    record = _analyze(tmp_path, iterations, 87.5)
    decisions = record["decisions"]
    if decisions["associator_realised"] != "undecided" or decisions["visibility_closure"] != "undecided":
        raise AssertionError(f"a truncated control block decided: {decisions}")
    if record["control"]["Delta"] is None or decisions["hom_comparison"] is None:
        raise AssertionError("partial estimates or the complete associator block's comparison were lost")
