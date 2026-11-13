"""Contracts of the exact-arithmetic successor of the Tuna-17 one-CZ null analysis.

The fixtures hold at most 256 shots per circuit, so the exact statistics cost milliseconds; the retained
19-batch regeneration is the on-demand gate core-pathion-one-cz-null-tuna-analysis-replay. The audit-marked
retained-record test reads two committed JSON files (the schema-v2 record and its schema-v3 successor) and
regenerates nothing.
"""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np
import pytest
import qi_pathion_coset_coin_cases as cc
import qi_pathion_one_cz_null_analysis as ana
import qi_pathion_one_cz_null_cases as oc

import exact_contrast_statistics as ecs
import parallel

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_BATCHES = {"b0": "batch-00", "k4": "batch-03", "k8": "batch-04", "k12": "batch-07"}
SHOTS = 256
READOUT_SHOTS = 64


def _expect(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


@pytest.fixture(scope="module")
def manifest() -> dict[str, Any]:
    loaded: dict[str, Any] = json.loads(oc.build()[oc.TUNA_SERIES]["batch-00/cases.json"])
    return loaded


def _readout_shots(width: int, register: list[int], flips: dict[int, int], prepared: int) -> list[str]:
    """READOUT_SHOTS strings of `width` bits; qubit q reads wrongly in its first flips[q] shots."""
    strings = []
    for shot in range(READOUT_SHOTS):
        value = 0
        for q in register:
            wrong = shot < flips[q]
            value |= (prepared ^ wrong) << q
        strings.append(format(value, f"0{width}b"))
    return strings


def _mini_series(manifest: dict[str, Any]) -> dict[str, list[str]]:
    """One base circuit per template, one readout pair per batch and one coin twin pair per template."""
    width, register = manifest["nqubits"], manifest["register"]
    shots: dict[str, list[str]] = {}
    for position, (template, batch) in enumerate(TEMPLATE_BATCHES.items()):
        roles = manifest["templates"][template]["roles"]
        law = np.array([1.0 + (5 * i + 3 * position) % 7 for i in range(oc.NOUT)])
        counts = cc.largest_remainder(law, SHOTS)
        shots[f"{batch}/{template}.cq"] = cc.place_counts(counts, oc.KEYS, roles, width)
        zero_flips = {q: 1 + (q + position) % 4 for q in register}
        one_flips = {q: 2 + (2 * q + position) % 5 for q in register}
        shots[f"{batch}/readout-0.cq"] = _readout_shots(width, register, zero_flips, 0)
        shots[f"{batch}/readout-1.cq"] = _readout_shots(width, register, one_flips, 1)
        for coin in (0, 1):
            selector = roles["selector"]
            twin = [format(int((shot + coin + position) % 3 == 0) << selector, f"0{width}b") for shot in range(128)]
            shots[f"{batch}/{template}-coin{coin}.cq"] = twin
    return shots


def _jsonable(value: Any) -> Any:
    loaded = json.loads(json.dumps(value, allow_nan=False))
    return loaded


def test_the_successor_equals_the_float_predecessor_within_the_declared_bound(manifest: dict[str, Any]) -> None:
    shots = _mini_series(manifest)
    floats: list[tuple[float, float]] = []
    found = ana.compare_records(
        _jsonable(oc.batch_estimates(shots, manifest)), _jsonable(ana.batch_estimates(shots, manifest)), floats
    )
    _expect(not found, "\n".join(found[:10]))
    _expect(len(floats) >= 400, f"the comparison covered {len(floats)} floats")
    corrected = [
        row["statistics"].keys() for t in ana.batch_estimates(shots, manifest)[1].values() for row in t.values()
    ]
    _expect(all("readout_corrected" in keys for keys in corrected), "every base circuit carries its bracket")


def test_the_successor_bytes_repeat_and_follow_neither_the_worker_count_nor_the_linear_solver(
    manifest: dict[str, Any], monkeypatch: pytest.MonkeyPatch
) -> None:
    shots = _mini_series(manifest)

    def regenerate() -> str:
        return ana.record_text({"rows": ana.batch_estimates(shots, manifest)})

    reference = regenerate()
    _expect(regenerate() == reference, "a second regeneration differs")
    for workers in ("1", "4"):
        monkeypatch.setenv("GOROROBA_WORKERS", workers)
        if parallel.workers() != int(workers):
            pytest.skip(f"fewer than {workers} CPUs available: the worker comparison would run serially")
        _expect(regenerate() == reference, f"{workers} workers differ from the default run")
    predecessor = ana.record_text({"rows": oc.batch_estimates(shots, manifest)})
    monkeypatch.setattr(np.linalg, "solve", lambda matrix, vector: np.linalg.inv(matrix) @ vector)
    resolved = ana.record_text({"rows": oc.batch_estimates(shots, manifest)})
    _expect(resolved != predecessor, "a different linear solver left the predecessor's bytes unchanged")
    _expect(regenerate() == reference, "the successor follows the linear solver")


def test_a_rebound_function_leaves_the_predecessor_module_untouched() -> None:
    pooled_before, heterogeneity_before = oc.pooled, oc.heterogeneity
    _expect(ana.decide_estimates is not oc.decide_estimates, "the rebound decision rule is a copy")
    _expect(oc.decide_estimates.__globals__["pooled"] is pooled_before, "the predecessor still pools by pow")
    _expect(ana.decide_estimates.__globals__["pooled"] is ana.pooled, "the copy pools by products")
    _expect(oc.pooled is pooled_before and oc.heterogeneity is heterogeneity_before, "predecessor names moved")
    _expect(ana.joint_statistics.__globals__["pooled"] is ana.pooled, "the joint calibration pools by products")


def _rows(shifts: dict[str, float]) -> dict[str, dict[str, list[tuple[float, float]]]]:
    return {
        t: {
            kind: [(shifts.get(t, 0.0) + sign * 0.0004, 0.002 + 0.0001 * sign) for sign in (1, -1)]
            for kind in ("base", "twin")
        }
        for t in oc.TEMPLATES
    }


@pytest.mark.parametrize(
    ("shifts", "label"),
    [
        ({"b0": 0.0164}, "zero"),
        ({t: 0.0164 for t in oc.TEMPLATES}, "b0_like"),
        ({}, "offset_absent"),
        ({"b0": 0.5, "k4": -0.4}, "unresolved_batch"),
    ],
)
def test_the_rebound_decision_rule_reads_the_same_label_and_numbers(shifts: dict[str, float], label: str) -> None:
    rows = _rows(shifts)
    if label == "unresolved_batch":
        rows["b0"]["base"] = [(0.5, 0.002), (0.0, 0.002)]
    kept, rebound = oc.decide_estimates(rows), ana.decide_estimates(rows)
    _expect(kept["label"] == label and rebound["label"] == label, f"{kept['label']} and {rebound['label']}")
    floats: list[tuple[float, float]] = []
    found = ana.compare_records(_jsonable(kept), _jsonable(rebound), floats)
    _expect(not found and bool(floats), f"{found[:5]}")
    _expect(max(difference for difference, _ in floats) < 1e-12, "the product form moved a number")


def test_pooling_multiplies_where_the_predecessor_squares() -> None:
    values = [(0.0123, 0.0031), (0.0207, 0.0044), (0.0161, 0.0029)]
    weights = [1.0 / (se * se) for _, se in values]
    mean = sum(w * v for w, (v, _) in zip(weights, values, strict=True)) / sum(weights)
    _expect(ana.pooled(values) == (mean, (1.0 / sum(weights)) ** 0.5), "pooled follows its definition")
    expected = sum(((v - mean) / se) * ((v - mean) / se) for v, se in values)
    _expect(ana.heterogeneity(values) == expected, "heterogeneity sums products")


def test_pooling_and_chi_square_match_a_hand_computed_three_entry_fixture() -> None:
    # weights 1 / se^2 = 4, 16, 64 (sum 84); mean (4 + 32 + 192) / 84 = 19/7; chi-square (576 + 400 + 256) / 49 = 176/7.
    values = [(1.0, 0.5), (2.0, 0.25), (3.0, 0.125)]
    mean, error = ana.pooled(values)
    _expect(mean == pytest.approx(19 / 7, rel=1e-15, abs=0.0), f"pooled mean {mean!r}")
    _expect(error == pytest.approx(1 / 84**0.5, rel=1e-15, abs=0.0), f"pooled error {error!r}")
    _expect(ana.heterogeneity(values) == pytest.approx(176 / 7, rel=1e-15, abs=0.0), "chi-square of the fixture")
    _expect(ana.heterogeneity([(2.0, 0.5), (2.0, 0.25)]) == 0.0, "equal values have zero chi-square")


def test_pooling_an_empty_list_or_a_zero_standard_error_raises_like_the_predecessor() -> None:
    for degenerate in ([], [(1.0, 0.0), (2.0, 0.5)]):
        for function, kept in ((ana.pooled, oc.pooled), (ana.heterogeneity, oc.heterogeneity)):
            with pytest.raises(ZeroDivisionError):
                function(degenerate)
            with pytest.raises(ZeroDivisionError):
                kept(degenerate)


def _flat_rows(
    low_base: dict[str, float], low_twin: dict[str, float], b0_base: float, b0_twin: float
) -> dict[str, dict[str, list[tuple[float, float]]]]:
    """Two identical batch estimates per template, so each batch chi-square is zero and the pooled values are exact."""
    standard_error = 0.002
    values = {"b0": (b0_base, b0_twin), **{t: (low_base[t], low_twin[t]) for t in oc.LOW_NAMES}}
    return {
        t: {"base": [(base, standard_error)] * 2, "twin": [(twin, standard_error)] * 2}
        for t, (base, twin) in values.items()
    }


def _uniform(value: float) -> dict[str, float]:
    return {t: value for t in oc.LOW_NAMES}


@pytest.mark.parametrize(
    ("rows", "label"),
    [
        (_flat_rows(_uniform(0.0164), _uniform(0.0164), 0.0164, 0.0), "superposition_only"),
        (_flat_rows(_uniform(0.0164), _uniform(0.0164), 0.005, 0.002), "unresolved"),
        (_flat_rows(_uniform(0.02), _uniform(0.0), 0.0164, 0.0164), "unresolved_context"),
        (
            _flat_rows({"k4": 0.014, "k8": 0.020, "k12": 0.014}, _uniform(0.016), 0.0164, 0.0164),
            "unresolved_block",
        ),
        (_flat_rows(_uniform(0.008), _uniform(0.008), 0.0164, 0.0164), "intermediate"),
        (_flat_rows(_uniform(-0.02), _uniform(-0.02), 0.0164, 0.0164), "unresolved"),
    ],
    ids=[
        "superposition_only",
        "unresolved_twin_gap",
        "unresolved_context",
        "unresolved_block",
        "intermediate",
        "unresolved_negative_mean",
    ],
)
def test_the_rebound_decision_rule_reaches_every_remaining_branch(
    rows: dict[str, dict[str, list[tuple[float, float]]]], label: str
) -> None:
    kept, rebound = oc.decide_estimates(rows), ana.decide_estimates(rows)
    _expect(
        kept["label"] == label and rebound["label"] == label, f"{kept['label']} and {rebound['label']}, not {label}"
    )
    _expect(rebound["outcome"] == oc.OUTCOMES[label][0], "the outcome text follows the label")
    _expect(rebound["decided"] == (label in oc.DECIDING), "only zero, b0_like and superposition_only decide")


def test_the_implied_contraction_is_the_rooted_corrected_visibility(manifest: dict[str, Any]) -> None:
    template = manifest["templates"]["k4"]
    shots = _mini_series(manifest)
    counts = cc.coin_counts(shots["batch-03/k4.cq"], template["roles"])
    result = _statistics(counts, template)
    corrected = ana.statistics_record(result)
    row = ana.template_row(
        "k4", template, counts, ana.statistics_record(_statistics(counts, template, False)), corrected
    )
    visibility = corrected["visibility"]
    _expect(visibility is not None and visibility > 0, f"fixture visibility {visibility}")
    implied = row["contraction_per_cz_implied"]
    _expect(abs(implied ** template["cz"] - visibility) <= 1e-12 * visibility, f"{implied} ** cz is not {visibility}")
    _expect(row["visibility_readout_corrected"] == visibility, "the row reports the exact corrected visibility")
    low, high = cc.RHO_BAND
    _expect(row["against_rho_band"] == ("below" if implied < low else "above" if implied > high else "inside"), "band")


def _statistics(counts: np.ndarray, template: dict[str, Any], corrected: bool = True) -> Any:
    """The exact statistics of one template's counts under a fixed small assignment (or raw)."""
    readout = tuple((Fraction(2 + k, 64), Fraction(3 + k, 64)) for k in range(5)) if corrected else None
    sign = tuple(int(s) for s in np.sign(np.array(template["ideal_c"])))
    job = ecs.ContrastJob(tuple(int(n) for n in counts), sign, readout, ana.ZERO_WEIGHT)
    return ecs.contrast_statistics(job)


def test_compare_records_names_each_kind_of_difference() -> None:
    base = {"label": "a", "flag": True, "count": 3, "none": None, "list": [1.0, 2.0], "float": 0.5}
    floats: list[tuple[float, float]] = []
    _expect(ana.compare_records(base, json.loads(json.dumps(base)), floats) == [] and len(floats) == 3, "equal")
    cases = {
        "label": "b",
        "flag": False,
        "count": 4,
        "none": 0.0,
        "list": [1.0],
        "float": 0.5 + 1e-6,
        "extra": 1,
    }
    for key, value in cases.items():
        other = {**base, key: value}
        found = ana.compare_records(base, other, [])
        _expect(len(found) == 1 and key in found[0], f"{key}: {found}")
    _expect(ana.compare_records(base, {**base, "float": 0.5 + 1e-13}, []) == [], "a float inside the bound differs")


def test_a_qx_control_record_is_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(ana, "analyze_series", lambda run_dirs: {"claim_kind": oc.CONTROL_KIND})
    with pytest.raises(SystemExit, match="QX control record"):
        ana.analyze([])


def test_only_the_complete_series_of_the_predecessor_batches_names_the_predecessor_record(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    cases = {"batch-00": "aa", "batch-01": "bb"}
    series = {"claim_kind": "hardware acquisition", "complete": True, "batch_cases_sha256": cases}
    monkeypatch.setattr(ana, "analyze_series", lambda run_dirs: dict(series))
    monkeypatch.setattr(ana, "PREDECESSOR_BATCH_CASES_SHA256", ana.batch_cases_digest(series))
    _expect(ana.analyze([])["succeeds"].get("record_sha256") == ana.PREDECESSOR_SHA256, "the matching series")
    monkeypatch.setattr(ana, "analyze_series", lambda run_dirs: {**series, "complete": False})
    _expect(set(ana.analyze([])["succeeds"]) == {"schema", "producer"}, "a partial series names a record")
    monkeypatch.setattr(ana, "analyze_series", lambda run_dirs: {**series, "batch_cases_sha256": {"batch-00": "aa"}})
    _expect(set(ana.analyze([])["succeeds"]) == {"schema", "producer"}, "another series names a record")


def test_the_row_builder_skips_the_float_statistics_the_exact_ones_replace() -> None:
    _expect(ana.row_fields.__code__ is ana.cc.template_row.__code__, "row_fields shares the predecessor code")
    _expect(ana.row_fields.__globals__["coin_statistics"] is ana.unused_statistics, "coin_statistics is rebound")
    _expect(ana.cc.template_row.__globals__["coin_statistics"] is ana.cc.coin_statistics, "the predecessor changed")


@pytest.mark.audit
def test_the_retained_successor_record_names_and_agrees_with_its_predecessor() -> None:
    old = ROOT / ana.PREDECESSOR_RECORD
    new = ROOT / ana.SUCCESSOR_RECORD
    _expect(hashlib.sha256(old.read_bytes()).hexdigest() == ana.PREDECESSOR_SHA256, "the predecessor bytes moved")
    _expect(
        ana.batch_cases_digest(json.loads(old.read_text(encoding="utf-8"))) == ana.PREDECESSOR_BATCH_CASES_SHA256,
        "the predecessor batches moved",
    )
    record = json.loads(new.read_text(encoding="utf-8"))
    _expect(record["schema"] == ana.SCHEMA and ana.SCHEMA.endswith("-v3"), f"{record['schema']}")
    _expect(
        record["succeeds"]
        == {
            "schema": oc.ANALYSIS_SCHEMA,
            "producer": "scripts/qi_pathion_one_cz_null_cases.py --analyze",
            "record": ana.PREDECESSOR_RECORD,
            "record_sha256": ana.PREDECESSOR_SHA256,
        },
        "the record names its predecessor",
    )
    _expect(new.read_text(encoding="utf-8").endswith("}\n"), "the retained record ends with one newline")
    floats: list[tuple[float, float]] = []
    found = ana.compare_records(json.loads(old.read_text(encoding="utf-8")), record, floats)
    found = [d for d in found if not d.startswith(("/schema ", "/arithmetic ", "/succeeds "))]
    _expect(not found, "\n".join(found[:10]))
    _expect(len(floats) == 1365, f"{len(floats)} floats compared")
    _expect(record["decision"]["label"] == "unresolved_batch" and not record["decision"]["decided"], "decision")
