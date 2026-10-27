"""Contracts of the permuted Ascella repeat: the job-01 request, its analysis and the comparison statistics."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import ascella_coherence_analysis as analysis
import ascella_coherence_repeat as repeat
import ascella_coherence_request as request
import ascella_seed_repeat_reading as seed_repeat
import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
CASES = ROOT / "results/quandela/cases/ascella_signed_coherence"


def manifest(job: str) -> dict[str, Any]:
    return json.loads((CASES / job / "cases.json").read_text(encoding="utf-8"))


def test_permuted_request_holds_job_00_settings_in_draw_order() -> None:
    first, second = manifest("job-00")["settings"], manifest("job-01")["settings"]
    order = request.permutation(request.ORDER_DRAW, 64)
    if sorted(order) != list(range(64)):
        raise AssertionError("the draw order is not a permutation of the 64 design entries")
    for position, setting in enumerate(second):
        design = first[setting["design_index"]]
        if order[position] != setting["design_index"] or setting["name"] != design["name"]:
            raise AssertionError(f"position {position} does not submit design entry {order[position]}")
        if setting["circuit_params"] != design["circuit_params"] or setting["observation_index"] != position:
            raise AssertionError(f"{setting['name']} departs from job-00 beyond its position")


def test_seed_repeat_request_holds_job_02_meshes_with_fixed_anchors() -> None:
    first, second = manifest("job-02")["settings"], manifest("job-03")["settings"]
    by_name = {setting["name"]: setting for setting in first}
    if sorted(by_name) != sorted(setting["name"] for setting in second):
        raise AssertionError("job-03 does not hold job-02's 64 settings")
    for position, setting in enumerate(second):
        earlier = by_name[setting["name"]]
        if (setting["compilation_seed"], setting["circuit_params"]) != (
            earlier["compilation_seed"],
            earlier["circuit_params"],
        ):
            raise AssertionError(f"{setting['name']} departs from job-02 beyond its position")
        anchor = position % request.ANCHOR_STRIDE == 0
        if anchor != (setting["compilation_seed"] == 0):
            raise AssertionError(f"position {position} breaks the anchor stride")
    moved = [s["name"] for s in second if s["compilation_seed"]] != [s["name"] for s in first if s["compilation_seed"]]
    if not moved:
        raise AssertionError("the perturbed meshes keep job-02's order")


def test_ideal_response_to_permuted_manifest_qualifies_every_endpoint() -> None:
    cases = manifest("job-01")
    rows = [[16384 * abs(complex(*entry)) ** 2 for entry in setting["column"]] for setting in cases["settings"]]
    result = analysis.analyze(cases, rows)
    if result["verdicts"] != {"qualifies": 27, "falsified": 0, "inconclusive": 0} or result["ideal_excluded"]:
        raise AssertionError(result["verdicts"])


def test_unregistered_job_is_refused() -> None:
    with pytest.raises(ValueError, match="not registered"):
        request.job_of({"family": "ascella_signed_coherence", "job": "job-99"})


def test_analyze_refuses_job_00(tmp_path: Path) -> None:
    (tmp_path / "cases.json").write_bytes((CASES / "job-00" / "cases.json").read_bytes())
    with pytest.raises(ValueError, match="owns job-00"):
        repeat.analyze(tmp_path)


def test_alternating_series_reads_negative_lag_one() -> None:
    series = repeat.log_counts(np.array([10.0, 400.0] * 32))
    result = repeat.autocorrelation_test(series, 1)
    if not (result["value"] < -0.9 and result["p"] < repeat.ALPHA):
        raise AssertionError(result)


def test_zero_outside_count_stays_finite() -> None:
    if not np.isfinite(repeat.log_counts(np.array([0.0, 3.0]))).all():
        raise AssertionError("a setting without outside-block clicks breaks the log statistic")


def test_seed_repeat_reading_thresholds_match_the_preregistered_case() -> None:
    limits = seed_repeat.fixed_bound(56)
    if abs(limits["ceiling"] - 0.880) > 5e-4 or abs(limits["bound"] - 0.784) > 5e-4:
        raise AssertionError(f"the reproduction ceiling and bound moved from 0.880 and 0.784: {limits}")
    rows = np.array([[0.1, 0.2, 0.3], [0.3, 0.1, 0.2]])
    if not np.allclose(seed_repeat.correlations(rows[0], rows), [1.0, -0.5]):
        raise AssertionError("correlations is not Pearson r per row")
