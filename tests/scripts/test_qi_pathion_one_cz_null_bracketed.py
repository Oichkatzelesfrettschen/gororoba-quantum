"""Contracts of the bracketed-twin successor case of the Tuna-17 one-CZ null series.

Each expectation is computed in the test from plain arithmetic, the retained series' records or the platform's own
constants, never from the producer's design or layout functions. The audit-marked tests regenerate the committed case
directories (the second also the stored operating characteristics, 18 simulations of 20,000 series).
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pytest
import qi_pathion_coset_coin_cases as cc
import qi_pathion_one_cz_null_analysis as ana
import qi_pathion_one_cz_null_bracketed_cases as bc
import qi_pathion_one_cz_null_cases as oc
import qi_pathion_one_cz_null_rule_v2 as rule
import qi_platform

ROOT = Path(__file__).resolve().parents[2]
CASES = ROOT / "results/quantum_inspire/cases"
PREDECESSOR_CASE = CASES / "pathion_one_cz_null_tuna_17"
# sha256 over the sorted "relative path, NUL, file sha256, newline" rows of the 78 files of the frozen predecessor case.
PREDECESSOR_TREE_SHA256 = "d9bc49303f7c8bf66593e460394a25a5e72a5cd77de42c568b013621f715988b"
SELECTOR_BIT = 3  # logical bit order d0, d1, d2, selector, coin
N = 32768
E01, E10 = 0.0281, 0.0296  # the retained one-CZ series' selector means (v3 record references), as the design states


def _expect(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


@pytest.fixture(scope="module")
def built() -> dict[str, dict[str, str]]:
    return bc.build()


def _manifests(files: dict[str, str]) -> list[dict[str, Any]]:
    names = sorted({rel.split("/")[0] for rel in files if rel.startswith("batch-")})
    return [json.loads(files[f"{name}/cases.json"]) for name in names]


# Layout ---------------------------------------------------------------------------------------------------------


def test_the_series_holds_twenty_seven_batches_within_the_platform_limit(built: dict[str, dict[str, str]]) -> None:
    manifests = _manifests(built[bc.TUNA_SERIES])
    _expect(len(manifests) == 27, f"{len(manifests)} batches")
    _expect(all(len(m["circuits"]) <= qi_platform.HARDWARE_BATCH_CIRCUITS == 3 for m in manifests), "batch size")
    _expect(all(m["shots"] <= 131072 and m["register"] == [2, 4, 8, 11, 12] for m in manifests), "limits")
    kinds = [m["kind"] for m in manifests]
    _expect(kinds.count("base") == 8 and kinds.count("twin") == 16 and kinds[24:] == ["joint"] * 3, f"{kinds}")
    _expect([len(m["circuits"]) for m in manifests[24:]] == [3, 3, 2], "the calibration batches")
    bases = sorted(m["template"] for m in manifests if m["kind"] == "base")
    _expect(bases == sorted(["b0", "b0", "k4", "k4", "k8", "k8", "k12", "k12"]), f"{bases}")


def test_a_pair_plus_its_bracket_is_four_circuits_and_exceeds_the_platform_limit() -> None:
    pair_with_bracket = ["readout-0", "coin-0 twin", "coin-1 twin", "readout-1"]
    _expect(len(pair_with_bracket) > qi_platform.HARDWARE_BATCH_CIRCUITS, "a bracketed pair cannot share a batch")


def test_every_twin_batch_is_its_twin_between_the_two_readouts(built: dict[str, dict[str, str]]) -> None:
    twins = [m for m in _manifests(built[bc.TUNA_SERIES]) if m["kind"] == "twin"]
    _expect(len(twins) == 16, "sixteen twin batches")
    for m in twins:
        files = [c["file"] for c in m["circuits"]]
        coin = [c["coin"] for c in m["circuits"] if c["kind"] == "data"]
        _expect(len(coin) == 1 and coin[0] in (0, 1), f"{m['batch']} coins {coin}")
        _expect(
            files == ["readout-0.cq", f"{m['template']}-coin{coin[0]}.cq", "readout-1.cq"], f"{m['batch']}: {files}"
        )
        _expect(m["shots"] == 32768, f"{m['batch']} shots")


def test_the_two_twins_of_a_template_are_adjacent_and_the_mirror_round_reverses_them(
    built: dict[str, dict[str, str]],
) -> None:
    manifests = _manifests(built[bc.TUNA_SERIES])
    position: dict[tuple[str, int, int], int] = {}
    for index, m in enumerate(manifests):
        if m["kind"] == "twin":
            coin = next(c["coin"] for c in m["circuits"] if c["kind"] == "data")
            position[(m["template"], m["replicate"], coin)] = index
    for template in ("b0", "k4", "k8", "k12"):
        _expect(position[(template, 0, 1)] == position[(template, 0, 0)] + 1, f"{template}: forward coin 0 then 1")
        _expect(position[(template, 1, 0)] == position[(template, 1, 1)] + 1, f"{template}: mirror coin 1 then 0")
    forward = [(m["template"], m["kind"]) for m in manifests[:24] if m["replicate"] == 0]
    mirror = [(m["template"], m["kind"]) for m in manifests[:24] if m["replicate"] == 1]
    _expect(len(forward) == 12 and mirror == forward[::-1], "the second round mirrors the first")
    _expect([m["kind"] for m in manifests[:12]] == [k for _, k in forward], "the forward round leads the series")


def test_a_linear_drift_cancels_in_the_pooled_twin_contrast_of_the_mirrored_order() -> None:
    # Position of the coin-1 and coin-0 batch of a template in the forward and the mirror round, from the batch rows.
    rows = bc.batch_rows(bc.TUNA_SERIES)
    gain = 0.01
    for template in ("b0", "k4", "k8", "k12"):
        contrast = []
        for replicate in (0, 1):
            at = {
                r["coin"]: i
                for i, r in enumerate(rows)
                if r["kind"] == "twin" and r["template"] == template and r["replicate"] == replicate
            }
            contrast.append(gain * (at[1] - at[0]))
        _expect(contrast[0] == gain and contrast[1] == -gain and sum(contrast) == 0.0, f"{template}: {contrast}")


def test_every_twin_has_an_ideal_selector_marginal_of_one_half(built: dict[str, dict[str, str]]) -> None:
    rows = []
    for m in _manifests(built[bc.TUNA_SERIES]) + _manifests(built[bc.QX_SERIES]):
        rows += [r for r in m["circuits"] if r["kind"] == "data" and r.get("coin") is not None]
    retained = sorted(PREDECESSOR_CASE.glob("batch-*/cases.json"))
    for path in retained:
        rows += [
            r
            for r in json.loads(path.read_text(encoding="utf-8"))["circuits"]
            if r["kind"] == "data" and r.get("coin") is not None
        ]
    _expect(len(rows) >= 8 + 8 + 16 + 8, f"{len(rows)} twin rows")
    for row in rows:
        ideal = row["ideal"]
        zero = sum(p for i, p in enumerate(ideal) if not (i >> SELECTOR_BIT) & 1)
        _expect(abs(zero - 0.5) < 1e-9, f"{row['file']}: P(s=0) {zero}")


def test_jobs_shots_and_seconds_follow_plain_arithmetic(built: dict[str, dict[str, str]]) -> None:
    jobs = 8 * 3 + 16 * 3 + 8
    shots = 2 * 3 * 131072 + 6 * 3 * 32768 + 16 * 3 * 32768 + (3 + 3 + 2) * 16384
    _expect(jobs == 80 and shots == 3080192, "the spec's counts")
    design = bc.design()
    _expect(design["jobs"] == jobs and design["shots_total"] == shots and design["batches"] == 27, f"{design}")
    manifests = _manifests(built[bc.TUNA_SERIES])
    _expect(sum(len(m["circuits"]) for m in manifests) == jobs, "jobs from the manifests")
    _expect(sum(len(m["circuits"]) * m["shots"] for m in manifests) == shots, "shots from the manifests")
    low = jobs * 2.6 + shots * 0.53e-3
    _expect(abs(low - 1840.5) < 0.05, f"low {low}")
    _expect(design["execution_seconds_range_tenths"][0] == round(low * 10), "low bound")
    rate = oc.coin_timing()["seconds_per_shot_max"]
    _expect(abs(rate - 0.59057e-3) < 1e-8, f"the measured maximum {rate}")
    high = jobs * 2.6 + shots * rate
    _expect(abs(high - 2027.1) < 0.05, f"high {high}")
    _expect(design["execution_seconds_range_tenths"][1] == round(high * 10), "high bound")
    # The rounded 0.59 ms per shot of the case's estimate gives the spec's 2025.3 s and 79.9 s.
    _expect(abs(jobs * 2.6 + shots * 0.59e-3 - 2025.3) < 0.05 and abs(2.6 + 131072 * 0.59e-3 - 79.9) < 0.05, "0.59 ms")
    longest = 2.6 + 131072 * rate
    _expect(longest < 300 and design["longest_job_seconds_tenths"] == round(longest * 10) == 800, f"{longest}")
    _expect(design["pause_seconds_total"] == 26 * 30 == 780, "26 pauses of 30 s")


def test_the_design_standard_errors_follow_the_item_five_formula() -> None:
    e01, e10 = bc.retained_selector_rates()
    _expect(abs(e01 - E01) < 5e-5 and abs(e10 - E10) < 5e-5, f"{e01} {e10}")
    per_p = 0.25 / N
    per_bracket = (e10 * (1 - e10) / N + e01 * (1 - e01) / N) / 4
    _expect(abs(per_p - 7.629e-6) < 1e-9 and abs(per_bracket - 4.27e-7) < 5e-9, f"{per_p} {per_bracket}")
    contrast = math.sqrt(2 * (per_p + per_bracket))
    raw = math.sqrt(2 * per_p)
    _expect(abs(contrast - 0.004014) < 2e-6 and abs(raw - 0.003906) < 2e-6, f"{contrast} {raw}")
    _expect(abs(contrast / raw - 1 - 0.028) < 1e-3, "2.8 percent above the raw se")
    _expect(abs(contrast / math.sqrt(2) - 0.002838) < 2e-6, "pooled over two replicates")
    design = bc.design()
    _expect(design["twin_batch_se_micro"] == round(contrast * 1e6), "design contrast se")
    _expect(design["pooled_se_micro"]["twin"] == round(contrast / math.sqrt(2) * 1e6), "design pooled se")
    _expect(design["raw_twin_batch_se_micro"] == round(raw * 1e6), "design raw se")
    _expect(design["design_selector_readout_e01_e10_ten_thousandths"] == [281, 296], "design rates")


# Estimator ------------------------------------------------------------------------------------------------------


def test_equal_brackets_reduce_the_bracketed_contrast_to_the_raw_one() -> None:
    p0, p1 = 5100 / N, 5400 / N
    for ones0, zeros1 in ((300, 900), (0, 0), (1000, 200)):
        value, _ = bc.twin_contrast(
            bc.twin_reading(5400, N, ones0, N, zeros1, N), bc.twin_reading(5100, N, ones0, N, zeros1, N)
        )
        _expect(abs(value - (p1 - p0)) < 1e-12, f"{value} against {p1 - p0}")


def test_the_estimator_subtracts_each_batch_bracket_offset() -> None:
    p1, p0 = 16600, 16200
    c1 = (950 / N - 880 / N) / 2
    c0 = (1010 / N - 820 / N) / 2
    expected = (p1 / N - c1) - (p0 / N - c0)
    value, _ = bc.twin_contrast(bc.twin_reading(p1, N, 880, N, 950, N), bc.twin_reading(p0, N, 820, N, 1010, N))
    _expect(abs(value - expected) < 1e-12, f"{value} against {expected}")


def test_the_bracket_removes_a_split_pair_offset_that_the_raw_contrast_keeps() -> None:
    # Both twins have corrected P(s=0) = 1/2 exactly; the two batches differ only in their selector readout errors, by
    # the retained series' adjacent-batch step of about 0.005 in e01 (item 4). A raw reading is
    # P = e10 + lambda / 2 = 1/2 + (e10 - e01) / 2.
    e01 = (0.0250, 0.0310)
    e10 = (0.0300, 0.0275)
    readings = []
    raw_p = []
    for k in (0, 1):
        ones0, zeros1 = round(e01[k] * N), round(e10[k] * N)
        zeros = round((0.5 + (zeros1 - ones0) / N / 2) * N)
        raw_p.append(zeros / N)
        readings.append(bc.twin_reading(zeros, N, ones0, N, zeros1, N))
    raw = raw_p[1] - raw_p[0]
    _expect(abs(raw - (-0.00425)) < 1e-4, f"the raw split contrast {raw}")
    value, _ = bc.twin_contrast(readings[1], readings[0])
    _expect(abs(value) < 1e-4, f"the bracketed contrast {value}")


def test_the_variance_is_the_sum_of_the_arm_variances_with_weights_one_and_one_quarter() -> None:
    p, e01, e10 = 17000 / N, 900 / N, 970 / N
    _, variance = bc.twin_reading(17000, N, 900, N, 970, N)
    expected = p * (1 - p) / N + (e01 * (1 - e01) / N + e10 * (1 - e10) / N) / 4
    _expect(abs(variance - expected) < 1e-15, f"{variance} against {expected}")


def test_the_standard_error_agrees_with_a_monte_carlo_of_binomial_counts() -> None:
    rng = np.random.default_rng(bc.OC_SEED)
    draws = 20000
    # Two batches (coin 1 and coin 0) of one template at P(s=0) = 1/2 on the corrected scale and the design brackets.
    p_read = 0.5 + (E10 - E01) / 2
    zeros = rng.binomial(N, p_read, size=(2, draws))
    ones0 = rng.binomial(N, E01, size=(2, draws))
    zeros1 = rng.binomial(N, E10, size=(2, draws))
    contrasts = np.array(
        [
            bc.twin_contrast(
                bc.twin_reading(int(zeros[1, i]), N, int(ones0[1, i]), N, int(zeros1[1, i]), N),
                bc.twin_reading(int(zeros[0, i]), N, int(ones0[0, i]), N, int(zeros1[0, i]), N),
            )[0]
            for i in range(draws)
        ]
    )
    se = math.sqrt(2 * (0.25 / N + (E10 * (1 - E10) / N + E01 * (1 - E01) / N) / 4))
    _expect(abs(float(contrasts.std()) / se - 1) < 0.05, f"{contrasts.std()} against {se}")
    _expect(abs(float(contrasts.mean())) < 4 * se / math.sqrt(draws), f"mean {contrasts.mean()}")


def test_a_deterministic_readout_arm_yields_a_finite_pooled_error() -> None:
    reading = bc.twin_reading(N // 2, N, 0, N, 0, N)
    _expect(reading[1] > 0 and math.isfinite(reading[1]), f"{reading}")
    se = bc.twin_contrast(reading, reading)[1]
    mean, pooled_se = ana.pooled([(0.01, se), (0.02, se)])
    _expect(math.isfinite(mean) and math.isfinite(pooled_se) and pooled_se > 0, f"{pooled_se}")
    # A deterministic selector arm is the QX readout: zero misassigned shots out of N takes the finite-count interval.
    z2 = float(oc.Z_RESOLVE * oc.Z_RESOLVE)
    center = (z2 / 2) / (N + z2)
    _expect(abs(ana.arm_variance(0.0, N) - center * (1 - center) / (N + z2)) < 1e-18, "Agresti-Coull variance")


# Decision -------------------------------------------------------------------------------------------------------


def _twin_se() -> float:
    return math.sqrt(2 * (0.25 / N + (E10 * (1 - E10) / N + E01 * (1 - E01) / N) / 4))


def _rows(base: dict[str, float], twin: dict[str, float]) -> dict[str, dict[str, list[tuple[float, float]]]]:
    se_base = {t: 1 / math.sqrt(oc.CONTROL_SHOTS if t == "b0" else oc.BATCH_SHOTS) for t in oc.TEMPLATES}
    return {
        t: {
            "base": [(base.get(t, 0.0), se_base[t])] * 2,
            "twin": [(twin.get(t, 0.0), _twin_se())] * 2,
        }
        for t in oc.TEMPLATES
    }


def test_rule_v2_labels_hand_built_bracketed_rows() -> None:
    se_t0 = _twin_se() / math.sqrt(2)
    for t0, label in (
        (0.0, "superposition_only"),
        (-0.999 * oc.Z_RESOLVE * se_t0, "superposition_only"),
        (-1.001 * oc.Z_RESOLVE * se_t0, rule.NEGATIVE_TWIN),
        (-0.0164, rule.NEGATIVE_TWIN),
    ):
        got = rule.decide_estimates(_rows({"b0": 0.0164}, {"b0": t0}))
        _expect(got["label"] == label and got["decided"] == (label == "superposition_only"), f"{t0}: {got['label']}")
    zero_block = rule.decide_estimates(_rows({"b0": 0.0164}, {"b0": 0.0166}))
    _expect(zero_block["label"] == "zero", f"{zero_block['label']}")
    absent = rule.decide_estimates(_rows({}, {}))
    _expect(absent["label"] == "offset_absent", f"{absent['label']}")


def test_the_preregistered_text_restates_the_estimates_and_carries_rule_v2() -> None:
    text = bc.preregistered()
    old = oc.preregistered()
    _expect(text["twin_control"] == rule.TWIN_CONTROL != old["twin_control"], "twin control")
    _expect("bracket offset" in text["estimates"] and text["estimates"] != old["estimates"], "estimates")
    _expect({k for k in text if text[k] != old[k]} == {"estimates", "twin_control"}, "nothing else of the rule changes")


# Mutations and worlds -------------------------------------------------------------------------------------------


@pytest.fixture(scope="module")
def manifest(built: dict[str, dict[str, str]]) -> dict[str, Any]:
    loaded: dict[str, Any] = json.loads(built[bc.TUNA_SERIES]["batch-00/cases.json"])
    return loaded


def _selector_estimate(register: list[int]) -> tuple[float, float]:
    """(e01, e10) of the selector q8 in `oc.synthetic_series`' default assignment: (0.02, 0.04) + 0.01 per register
    position."""
    n = register.index(8)
    return 0.02 + 0.01 * n, 0.04 + 0.01 * n


def test_a_coin_conditioned_dropout_survives_the_bracketed_twin_contrast_at_expected_counts() -> None:
    # Only the coin-1 twin's selector misreads more: a true selector 1 reads 0 with probability x on its shots. Both
    # batches carry equal brackets, so the contrast is the dropout's lambda x / 2 on the raw scale.
    x, e01, e10 = 0.0362, E01, E10
    lam = 1 - e01 - e10
    ones0, zeros1 = round(e01 * N), round(e10 * N)
    base = e10 + lam * 0.5
    coin0 = bc.twin_reading(round(base * N), N, ones0, N, zeros1, N)
    coin1 = bc.twin_reading(round((e10 + lam * (0.5 + x / 2)) * N), N, ones0, N, zeros1, N)
    value, se = bc.twin_contrast(coin1, coin0)
    _expect(abs(value - lam * x / 2) < 3 * se and abs(value - lam * x / 2) < 1e-4, f"{value} against {lam * x / 2}")
    _expect(value > oc.Z_RESOLVE * se, "the injected contrast is resolved above 3 se")


@pytest.mark.audit
def test_a_coin_conditioned_dropout_survives_the_bracketed_twin_contrast_of_the_series(
    built: dict[str, dict[str, str]], manifest: dict[str, Any]
) -> None:
    files = built[bc.TUNA_SERIES]
    x = 0.0362
    rows, _ = bc.batch_estimates(oc.synthetic_series(files, manifest, dropout=x), manifest)
    e01, e10 = _selector_estimate(manifest["register"])
    expected = (1 - e01 - e10) * x / 2  # the dropout reads a selector 1 as 0 on half of the coin-1 twin's shots
    for template in oc.TEMPLATES:
        for value, se in rows[template]["twin"]:
            _expect(abs(value - expected) < 3 * se, f"{template}: {value} against {expected} (se {se})")
    clean, _ = bc.batch_estimates(oc.synthetic_series(files, manifest), manifest)
    for template in oc.TEMPLATES:
        _expect(all(abs(v) < 1e-3 for v, _ in clean[template]["twin"]), f"{template}: {clean[template]['twin']}")


@pytest.mark.audit
def test_the_bracket_offsets_of_the_synthetic_series_agree_between_batches(
    built: dict[str, dict[str, str]], manifest: dict[str, Any]
) -> None:
    shots = oc.synthetic_series(built[bc.TUNA_SERIES], manifest)
    qubit = 8
    offsets = []
    for batch in ("batch-01", "batch-02", "batch-21", "batch-22"):
        zero, one = shots[f"{batch}/readout-0.cq"], shots[f"{batch}/readout-1.cq"]
        e01 = sum(int(s[len(s) - 1 - qubit]) for s in zero) / len(zero)
        e10 = sum(1 - int(s[len(s) - 1 - qubit]) for s in one) / len(one)
        offsets.append((e10 - e01) / 2)
    _expect(max(offsets) - min(offsets) < 1e-6, f"{offsets}")


WORLD_LABELS = {**oc.WORLD_LABELS, "twin_opposite_sign": rule.NEGATIVE_TWIN}
WORLD_KWARGS = {**oc.WORLDS, "twin_opposite_sign": {"offsets": {"b0": 0.0164}, "twin_offsets": {"b0": -0.0164}}}


@pytest.fixture(scope="module")
def worlds(built: dict[str, dict[str, str]], manifest: dict[str, Any]) -> dict[str, dict[str, list[str]]]:
    return {w: oc.synthetic_series(built[bc.TUNA_SERIES], manifest, **kw) for w, kw in WORLD_KWARGS.items()}


@pytest.mark.audit
@pytest.mark.parametrize("world", list(WORLD_KWARGS))
def test_each_simulated_world_reads_its_rule_v2_row(
    world: str, worlds: dict[str, dict[str, list[str]]], manifest: dict[str, Any]
) -> None:
    result = bc.evaluate(worlds[world], manifest)
    _expect(result["decision"]["label"] == WORLD_LABELS[world], f"{world}: {result['decision']}")


def _twin_shots(manifest: dict[str, Any]) -> dict[str, list[str]]:
    """Eight-shot lists of every twin batch of the series: the twin circuit and its two readouts (all qubits 0)."""
    width = manifest["nqubits"]
    shots: dict[str, list[str]] = {}
    for row in bc.batch_rows(bc.TUNA_SERIES):
        if row["kind"] != "twin":
            continue
        for circuit in row["circuits"]:
            shots[f"{row['batch']}/{circuit['file']}"] = ["0" * width] * 8
    return shots


def test_a_series_that_lacks_a_twin_batch_is_refused(manifest: dict[str, Any]) -> None:
    shots = _twin_shots(manifest)
    rows, _ = bc.batch_estimates(shots, manifest)
    _expect(all(len(rows[t]["twin"]) == 2 and rows[t]["base"] == [] for t in oc.TEMPLATES), "two replicates a template")
    without = {k: v for k, v in shots.items() if not k.startswith("batch-02/")}
    with pytest.raises(ValueError, match="lacks a coin twin batch"):
        bc.batch_estimates(without, manifest)
    # A twin circuit under a batch that does not hold it is refused as well.
    moved = {(k.replace("batch-02/", "batch-01/") if "coin1" in k else k): v for k, v in shots.items()}
    with pytest.raises(ValueError, match="series layout holds"):
        bc.batch_estimates(moved, manifest)


def test_a_deterministic_series_pools_to_a_finite_decision_error(manifest: dict[str, Any]) -> None:
    rows, _ = bc.batch_estimates(_twin_shots(manifest), manifest)
    for template in oc.TEMPLATES:
        for value, se in rows[template]["twin"]:
            _expect(value == 0.0 and math.isfinite(se) and se > 0, f"{template}: {value} {se}")
        _expect(math.isfinite(ana.pooled(rows[template]["twin"])[1]), template)


# Operating characteristics --------------------------------------------------------------------------------------


def _stored() -> dict[str, Any]:
    stored: dict[str, Any] = json.loads((CASES / bc.TUNA_SERIES / "prediction.json").read_text(encoding="utf-8"))
    return stored


def _holds_float(node: Any) -> bool:
    if isinstance(node, float):
        return True
    if isinstance(node, dict):
        return any(_holds_float(v) for v in node.values())
    return isinstance(node, list) and any(_holds_float(v) for v in node)


def test_the_stored_prediction_record_holds_no_float() -> None:
    _expect(not _holds_float(_stored()), "a float in the record needs a numeric binding to replay")


def test_the_registered_draw_seeds_the_simulation_and_the_prediction_names_it() -> None:
    from qrng_seeds import read_record

    stored = _stored()["operating_characteristics"]
    _expect(stored["qrng_draw"] == bc.OC_DRAW and stored["seed_index"] == bc.OC_SEED_INDEX == 0, "named draw")
    _expect(bc.OC_SEED == int(read_record(bc.OC_DRAW)["values"][0]), "the seed is value 0 of the retained draw")
    _expect(bc.OC_DRAW != oc.OC_DRAW and (ROOT / bc.OC_DRAW).is_file(), "a new draw")


def test_the_stored_tables_keep_the_stationary_decision_power_and_add_the_negative_twin_row() -> None:
    ocs = _stored()["operating_characteristics"]
    share = {
        table: {w: {k: v / 10000 for k, v in row.items()} for w, row in ocs[table].items()}
        for table in ("stationary", "batch_drift_sd_0.003")
    }
    _expect(set(share["stationary"]) == set(rule.WORLDS) == set(share["batch_drift_sd_0.003"]), "worlds")
    for world, label in (
        ("over_rotation", "zero"),
        ("q12_correlation", "zero"),
        ("coin_dropout", "b0_like"),
        ("superposition_only", "superposition_only"),
        (rule.NEGATIVE_TWIN_WORLD, rule.NEGATIVE_TWIN),
    ):
        _expect(share["stationary"][world][label] >= 0.9, f"stationary {world}: {share['stationary'][world]}")
    _expect(share["stationary"]["absent"]["offset_absent"] >= 0.95, "no offset reads absent")
    wrong = share["stationary"]["over_rotation_x_all_before"].get("b0_like", 0.0)
    _expect(0.05 < wrong < 0.12, f"the outside-the-set world's wrong refutation {wrong}")
    for world in ("over_rotation", "q12_correlation", "coin_dropout", "superposition_only"):
        _expect(
            share["batch_drift_sd_0.003"][world].get("unresolved_batch", 0.0) > 0.1,
            "a split twin pair carries sqrt(2) x the drift into the replicate gate",
        )


def test_the_successor_simulation_reaches_spawned_workers_and_is_serial_equal() -> None:
    world = {rule.NEGATIVE_TWIN_WORLD: rule.NEGATIVE_TWIN_MEAN}
    first = bc.operating_characteristics(draws=128, worlds=world)
    again = bc.operating_characteristics(draws=128, worlds=world)
    _expect(first == again, "a rerun reproduces the draws")
    _expect(first[rule.NEGATIVE_TWIN_WORLD].get(rule.NEGATIVE_TWIN, 0.0) >= 0.8, f"{first}")


def test_a_larger_drift_lowers_the_deciding_share_of_the_dropout_world() -> None:
    world = {"coin_dropout": rule.WORLDS["coin_dropout"]}
    still = bc.operating_characteristics(draws=256, worlds=world)["coin_dropout"]["b0_like"]
    drifting = bc.operating_characteristics(draws=256, drift_sd=0.01, worlds=world)["coin_dropout"].get("b0_like", 0.0)
    _expect(still > drifting, f"{still} against {drifting}")


# Directories ----------------------------------------------------------------------------------------------------


def _tree_digest(root: Path) -> tuple[int, str]:
    digest = hashlib.sha256()
    files = [p for p in sorted(root.rglob("*")) if p.is_file()]
    for path in files:
        digest.update(
            f"{path.relative_to(root).as_posix()}\0{hashlib.sha256(path.read_bytes()).hexdigest()}\n".encode()
        )
    return len(files), digest.hexdigest()


def test_the_frozen_predecessor_case_directory_keeps_its_bytes() -> None:
    count, digest = _tree_digest(PREDECESSOR_CASE)
    _expect(count == 78 and digest == PREDECESSOR_TREE_SHA256, f"{count} files, sha256 {digest}")


def test_the_run_directories_of_this_series_are_recognized_and_the_predecessor_series_is_refused() -> None:
    _expect(bc.series_of(Path(f"2026-11-15T000000Z-{bc.TUNA_SERIES}-batch-00")) == bc.TUNA_SERIES, "Tuna-17 series")
    _expect(bc.series_of(Path(f"2026-11-15T000000Z-{bc.QX_SERIES}-batch-00")) == bc.QX_SERIES, "QX series")
    with pytest.raises(SystemExit):
        bc.series_of(Path(f"2026-11-15T000000Z-{oc.TUNA_SERIES}-batch-00"))


@pytest.mark.audit
def test_the_committed_case_directories_reproduce_their_bytes() -> None:
    bc.check(CASES, operating=False)


@pytest.mark.audit
def test_the_stored_operating_characteristics_replay() -> None:
    bc.check(CASES)


# QX control -----------------------------------------------------------------------------------------------------


def _qx_counts(files: dict[str, str]) -> dict[str, dict[str, int]]:
    """Noiseless QX histograms at expected counts: data circuits at their ideal law, readout-1 exciting the register."""
    out: dict[str, dict[str, int]] = {}
    for m in _manifests(files):
        for row in m["circuits"]:
            key = f"{m['batch']}/{row['file']}"
            if row["kind"] == "readout":
                excited = row["file"] == "readout-1.cq"
                out[key] = {("0" * 5 + "1" * 5) if excited else "0" * 10: m["shots"]}
                continue
            roles = m["templates"][row["template"]]["roles"]
            counts = cc.largest_remainder(np.array(row["ideal"]), m["shots"])
            shots = cc.place_counts(counts, cc.KEYS, roles, 10)
            hist: dict[str, int] = {}
            for s in shots:
                hist[s] = hist.get(s, 0) + 1
            out[key] = hist
    return out


def test_the_qx_series_keeps_each_bracket_inside_its_batch(built: dict[str, dict[str, str]]) -> None:
    manifests = _manifests(built[bc.QX_SERIES])
    _expect(len(manifests) == 8 and all(len(m["circuits"]) <= 5 for m in manifests), "eight batches of at most five")
    _expect(sum(len(m["circuits"]) for m in manifests) == 28 and manifests[0]["shots"] == 2048, "28 circuits")
    for m in manifests:
        files = [c["file"] for c in m["circuits"]]
        _expect(len(files) == len(set(files)) and files[0] == "readout-0.cq" and files[2] == "readout-1.cq", f"{files}")


def test_the_qx_check_passes_a_noiseless_run_and_fails_a_misassigned_shot_and_a_wrong_circuit(
    built: dict[str, dict[str, str]],
) -> None:
    counts = _qx_counts(built[bc.QX_SERIES])
    report = bc.qx_check(counts)
    _expect(report["qx_control"]["pass"] and report["qx_brackets"]["pass"], f"{report['qx_brackets']}")
    contrasts = report["qx_brackets"]["twin_contrasts"]
    _expect(all(c["bracketed"] == c["raw"] for c in contrasts.values()), f"{contrasts}")
    # One readout-1 shot that reads the selector (q8 of the register, index 2) as 0 is a misassigned shot.
    bad = {k: dict(v) for k, v in counts.items()}
    one = bad["batch-00/readout-1.cq"]
    one["0" * 5 + "1" * 5] -= 1
    one["0" * 5 + "11011"] = 1
    _expect(not bc.qx_check(bad)["qx_brackets"]["pass"], "a misassigned readout shot passes")
    # A twin that reads another circuit's law fails the control.
    swapped = {k: dict(v) for k, v in counts.items()}
    swapped["batch-00/b0-coin0.cq"], swapped["batch-01/b0-coin1.cq"] = (
        counts["batch-01/b0-coin1.cq"],
        counts["batch-00/b0-coin0.cq"],
    )
    _expect(not bc.qx_check(swapped)["qx_control"]["pass"], "a wrong circuit passes")
