"""Contracts of the coset-block scoring module: sign-decided bins, the precision floor, the explicit-input decisions.

Every function takes its inputs explicitly, so each test builds the counts, references and design values it needs.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import numpy as np
import pytest

import pathion_coset_analysis as pca
import qi_records


def _check(condition: object, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def test_signed_z_decides_a_deterministic_bin_by_an_exact_sign_match() -> None:
    _check(pca.signed_z(1.0, 0.0, 1.0) == math.inf, "match on a deterministic bin")
    _check(pca.signed_z(-1.0, 0.0, -1.0) == math.inf, "match with a negative ideal sign")
    _check(pca.signed_z(-1.0, 0.0, 1.0) == -math.inf, "mismatch on a deterministic bin")
    _check(pca.signed_z(0.0, 0.0, 1.0) == 0.0, "a zero contrast decides nothing")
    _check(pca.signed_z(0.5, 0.0, 0.0) == 0.0, "a zero ideal sign decides nothing")
    _check(abs(pca.signed_z(0.3, 0.1, 1.0) - 3.0) < 1e-12, "a sampled bin keeps c * sign / se")
    _check(pca.ratio_or_none(1.0, 0.0) is None and pca.ratio_or_none(1.0, 0.5) == 2.0, "ratio_or_none")


def test_a_deterministic_bin_counts_only_with_enough_shots_in_each_arm() -> None:
    least = pca.DETERMINISTIC_MIN_COUNT
    tail = 0.5 * math.erfc(pca.Z_RESOLVE / math.sqrt(2.0))
    _check(4.0**-least <= tail < 4.0 ** -(least - 1), f"{least} is the least count with 4^-n below the normal tail")
    _check(pca.signed_z(1.0, 0.0, 1.0, n_min=least) == math.inf, "a deterministic bin at the minimum count decides")
    _check(pca.signed_z(1.0, 0.0, 1.0, n_min=least - 1) == 0.0, "a chance-deterministic bin decides nothing")
    _check(pca.signed_z(-1.0, 0.0, 1.0, n_min=least - 1) == 0.0, "a short bin never reads as a contrary result")
    _check(abs(pca.signed_z(0.3, 0.1, 1.0, n_min=1) - 3.0) < 1e-12, "a sampled bin ignores the count rule")


def _noise_reference() -> dict[str, Any]:
    entry = {"ratio": 0.0, "se": 0.0, "se_mean": 0.0, "coset": 0}
    return {"labels": {label: entry for label in range(32)}}


def test_a_high_uncertainty_bin_set_does_not_count_eight_of_eight() -> None:
    """IBM ratios 0 against Tuna ratios 1 at a standard error of 1: every z is 1; a design of 0.05 refuses all eight."""
    statistics = {"ratio": [1.0] * 8, "ratio_se": [1.0] * 8}
    labels = list(range(8))
    _check(pca.cross_platform(statistics, labels, _noise_reference())["bins_within"] == 8, "z = 1 reads as agreement")
    floored = pca.cross_platform(statistics, labels, _noise_reference(), design_se=[0.05] * 8)
    _check(floored["bins_within"] == 0 and floored["bins_within_unfloored"] == 8, f"{floored}")
    reached = pca.cross_platform(
        {"ratio": [0.01] * 8, "ratio_se": [0.04] * 8}, labels, _noise_reference(), design_se=[0.05] * 8
    )
    _check(reached["bins_within"] == 8 and all(reached["precise"]), "a run at the design precision counts its bins")
    at_factor = pca.cross_platform(
        {"ratio": [0.0] * 8, "ratio_se": [pca.PRECISION_FACTOR * 0.05] * 8},
        labels,
        _noise_reference(),
        design_se=[0.05] * 8,
    )
    _check(at_factor["bins_within"] == 8, "a combined error at exactly PRECISION_FACTOR times the design is precise")
    beyond = pca.cross_platform(
        {"ratio": [0.0] * 8, "ratio_se": [pca.PRECISION_FACTOR * 0.05 * 1.01] * 8},
        labels,
        _noise_reference(),
        design_se=[0.05] * 8,
    )
    _check(beyond["bins_within"] == 0, "a combined error beyond the factor is imprecise")


def test_a_selector_contrast_at_a_coarse_error_is_uninformative_not_a_null() -> None:
    design = 0.004
    holds = pca.null_decision(0.003, 0.005, design)
    _check(holds["outcome"] == "holds" and holds["holds"], f"{holds}")
    fails = pca.null_decision(0.05, 0.005, design)
    _check(fails["outcome"] == "fails" and not fails["holds"], f"{fails}")
    coarse = pca.null_decision(0.5, 1.0, design)
    _check(coarse["outcome"] == "uninformative" and not coarse["holds"], "a contrast of 0.5 at se 1 satisfies no null")
    _check(coarse["z"] == 0.5 and coarse["informative"] is False, f"{coarse}")


def _statistics(ratio: float, se: float) -> dict[str, Any]:
    return {"ratio": [ratio] * 8, "ratio_se": [se] * 8}


def test_cross_decision_reads_only_the_named_primary_templates() -> None:
    """The primary argument selects the templates of the rule: an unread primary template fails the decision and an
    unnamed one is never consulted."""
    reference = {"e1pe2": _noise_reference()}
    templates = {name: {"block": name, "operand": (1, 2, 1)} for name in ("ba", "bb", "extra")}
    labels = {name: {"ibm_data_index_of_bin": list(range(8))} for name in templates}
    design = {"cross_se": {"dev": {name: [0.05] * 8 for name in templates}}}
    scale = {name: 1.0 for name in templates}
    consulted: list[str] = []

    def statistic(name: str) -> dict[str, Any] | None:
        consulted.append(name)
        return {pca.CROSS_STATISTIC: _statistics(0.0, 0.05)} if name == "ba" else None

    decision = pca.cross_decision(templates, labels, {"dev": reference}, statistic, design, scale, ("ba", "bb"))
    _check(consulted == ["ba", "bb"], f"consulted {consulted}")
    _check(decision["devices"]["dev"]["templates"]["ba"]["outcome"] == "holds", f"{decision}")
    _check(decision["devices"]["dev"]["templates"]["bb"] == {"read": False, "outcome": "not read"}, f"{decision}")
    _check(decision["outcome"] == "not read" and not decision["holds"], f"{decision}")


def test_design_standard_errors_take_the_larger_rho_band_end_of_each_named_device() -> None:
    def cell(low: float, high: float) -> dict[str, Any]:
        return {
            f"rho_{rho}": {pca.CROSS_STATISTIC: {"se": [se] * 8}}
            for rho, se in zip((0.9, 0.95), (low, high), strict=True)
        }

    prediction = {
        "templates": {"ba": {"rho_0.9": {"selector_se": 0.01}, "rho_0.95": {"selector_se": 0.02}}},
        "cross_platform": {"templates": {"ba": {"dev": cell(0.04, 0.03), "other": cell(0.5, 0.5)}}},
    }
    design = pca.design_from_prediction(prediction, (0.9, 0.95), ["dev"])
    _check(design["selector_se"] == {"ba": 0.02}, f"{design}")
    _check(design["cross_se"] == {"dev": {"ba": [0.04] * 8}}, f"{design}")
    scaled = pca.scale_design(design, 2.0)
    _check(scaled["cross_se"]["dev"]["ba"] == [0.08] * 8 and scaled["selector_se"] == {"ba": 0.04}, f"{scaled}")
    _check(pca.design_scale(1024, 256) == 2.0, "sampling errors scale with the inverse root of the shots")


def test_the_pool_task_equals_the_direct_statistics() -> None:
    plus = np.array([20.0 + 3.0 * (5 * i % 11) for i in range(16)])
    minus = np.array([25.0 + 2.0 * (7 * i % 13) for i in range(16)])
    sign = np.where(np.arange(8) % 3 == 0, -1.0, 1.0)
    matrix = pca.confusion([(0.02, 0.05)] * 4)
    for assignment in (None, matrix):
        direct = pca.contrast_statistics(plus, minus, sign, assignment)
        _check(pca.ContrastTask()((plus, minus, sign, assignment)) == direct, "the task departs from the function")


def test_a_control_arm_passes_within_the_factor_of_the_sampling_floor() -> None:
    law = [0.5, 0.5, 0.0, 0.0]
    exact = ["00"] * 512 + ["01"] * 512
    skewed = ["00"] * 1000 + ["01"] * 24

    def counts_of(shots: list[str], roles: dict[str, int]) -> np.ndarray:
        counts = np.zeros(4)
        for shot in shots:
            counts[int(shot, 2)] += 1
        return counts

    report = pca.control_report({"b/ok": (exact, {}, law), "b/skewed": (skewed, {}, law)}, counts_of)
    _check(report["arms"]["b/ok"]["ok"] and not report["arms"]["b/skewed"]["ok"], f"{report}")
    _check(not report["pass"] and report["factor"] == pca.CONTROL_FLOOR_FACTOR, f"{report}")
    _check(pca.control_report({}, counts_of)["pass"] is False, "an empty control passes nothing")


def test_an_undefined_statistic_is_null_in_the_statistics_record() -> None:
    flat = np.full(16, 1.0 / 16)
    statistics = pca.contrast_statistics(flat * 100, flat * 100, np.ones(8))
    _check(statistics["visibility"] == 0.0 and all(r is None for r in statistics["ratio"]), f"{statistics}")
    _check(statistics["nullity_estimate"] is None and statistics["nullity_se"] is None, "N_hat at zero visibility")
    _check(all(e is None for e in statistics["ratio_se"]), "the error of an undefined ratio is undefined")


def _stub_series(root: Path, monkeypatch: pytest.MonkeyPatch, extras: list[dict[str, Any]]) -> tuple[list[Path], Any]:
    """Run directories whose cases.json carry the given extra fields, read through a stub qi_records.read_run and a
    load_run that returns each directory's cases; the shared-series comparison is the unit under test."""
    monkeypatch.setattr(qi_records, "read_run", lambda *_: SimpleNamespace(completed=True, statuses={}))
    runs: dict[Path, dict[str, Any]] = {}
    for number, extra in enumerate(extras):
        run_dir = root / f"run-{number:02d}"
        run_dir.mkdir(parents=True)
        cases = {
            "batch": f"batch-{number:02d}",
            "circuits": [{"file": "a.cq", "kind": "data", "template": "ba", "ideal": [1.0]}],
            "templates": {"ba": {"roles": {"d0": 0}}},
            **extra,
        }
        (run_dir / "cases.json").write_text(json.dumps(cases), encoding="utf-8")
        runs[run_dir] = {"cases": cases, "shots": {"a.cq": ["0"]}, "jobs": {"a.cq": {"queued_at": "t"}}}
    return list(runs), lambda run_dir, _case: runs[run_dir]


def test_read_series_binds_every_batch_to_one_series(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    dirs, load_run = _stub_series(tmp_path, monkeypatch, [{"shots": 8}, {"shots": 8}])
    read = pca.read_series(dirs, None, None, "data", ("batch", "circuits"), load_run)
    _check(sorted(read["shots"]) == ["batch-00/a.cq", "batch-01/a.cq"], f"{sorted(read['shots'])}")
    _check(sorted(read["arms"]) == sorted(read["shots"]) and read["shared"]["shots"] == 8, f"{read}")
    mixed_dirs, mixed_load = _stub_series(tmp_path / "mixed", monkeypatch, [{"shots": 8}, {"shots": 9}])
    with pytest.raises(ValueError, match="describes a different series"):
        pca.read_series(mixed_dirs, None, None, "data", ("batch", "circuits"), mixed_load)


def test_read_series_refuses_an_empty_run_list_and_an_incomplete_job(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    with pytest.raises(ValueError, match="needs its run directories"):
        pca.read_series([], None, None, "data", (), lambda *_: {})
    dirs, load_run = _stub_series(tmp_path, monkeypatch, [{}])
    monkeypatch.setattr(
        qi_records, "read_run", lambda *_: SimpleNamespace(completed=False, statuses={"a.cq": "failed"})
    )
    with pytest.raises(ValueError, match="a job did not complete"):
        pca.read_series(dirs, None, None, "data", ("batch", "circuits"), load_run)


def test_visibility_gap_splits_the_nullity_error_exactly() -> None:
    # One aligned pair and three misaligned pairs: five bins of ideal sign +1, three of -1, N = 1.
    sign = np.array([1.0, 1.0, 1.0, 1.0, 1.0, -1.0, -1.0, -1.0])
    c = np.array([0.31, 0.27, 0.35, 0.29, 0.33, -0.22, -0.25, -0.19])
    split = pca.visibility_gap(c, sign)
    _check(split["nullity_ideal"] == 1.0, "N from the bin signs")
    _check(math.isclose(split["nullity_estimate"], pca.contrast_vector(c, sign)[17], rel_tol=1e-15), "same N_hat")
    _check(math.isclose(split["weight"], 15 / 8, rel_tol=1e-15), "weight |B+| |B-| / |B|")
    error = split["nullity_estimate"] - split["nullity_ideal"]
    _check(math.isclose(error, split["bias"], rel_tol=1e-12), f"N_hat - N {error} against the split {split['bias']}")
    _check(not split["fixed_by_signs"], "a block with both signs carries its contrasts")


def test_visibility_gap_marks_an_all_aligned_block_as_fixed() -> None:
    sign = np.ones(8)
    for c in (np.full(8, 0.8), np.array([0.9, 0.1, 0.5, 0.7, 0.2, 0.6, 0.3, 0.4])):
        split = pca.visibility_gap(c, sign)
        _check(split["fixed_by_signs"] and split["weight"] == 0.0, "no dark bin")
        _check(math.isclose(split["nullity_estimate"], 4.0, rel_tol=1e-15), "N_hat equals 4 for any contrasts")


def test_visibility_gap_needs_a_sign_on_every_bin() -> None:
    with pytest.raises(ValueError, match="ideal sign"):
        pca.visibility_gap(np.ones(8), np.array([1.0, 1.0, 1.0, 1.0, 0.0, -1.0, -1.0, -1.0]))
    with pytest.raises(ValueError, match="ideal sign"):
        pca.visibility_gap(np.ones(8), np.array([2.0, 1.0, 1.0, 1.0, 1.0, -1.0, -1.0, -1.0]))


def test_visibility_gap_reports_zero_visibility_as_undefined() -> None:
    sign = np.array([1.0, 1.0, 1.0, 1.0, 1.0, -1.0, -1.0, -1.0])
    c = np.array([0.5, 0.25, 0.25, 0.0, 0.0, 0.25, 0.25, 0.5])
    split = pca.visibility_gap(c, sign)
    _check(split["visibility"] == 0.0, "the contrasts cancel along the ideal signs")
    _check(math.isnan(split["nullity_estimate"]) and math.isnan(split["bias"]), "N_hat and bias are undefined")


def test_visibility_gap_marks_an_all_minus_block_as_fixed() -> None:
    split = pca.visibility_gap(np.array([-0.4, -0.2, -0.6, -0.1]), -np.ones(4))
    _check(split["fixed_by_signs"] and split["weight"] == 0.0, "no bin of sign +1")
    _check(math.isclose(split["nullity_estimate"], -2.0, rel_tol=1e-15), "N_hat equals the ideal -2")


def test_visibility_gap_rejects_empty_or_mismatched_bins() -> None:
    with pytest.raises(ValueError, match="one entry per bin"):
        pca.visibility_gap(np.array([]), np.array([]))
    with pytest.raises(ValueError, match="one entry per bin"):
        pca.visibility_gap(np.ones(7), np.ones(8))
