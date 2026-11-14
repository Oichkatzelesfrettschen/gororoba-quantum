"""Contracts of the bracketed-twin successor case of the Tuna-17 one-CZ null series.

Each expectation is computed in the test from plain arithmetic, the retained series' records or the platform's own
constants, never from the producer's design or layout functions. The audit-marked tests regenerate the committed case
directories (the second also the stored operating characteristics, 27 simulations of 20,000 series).
"""

from __future__ import annotations

import hashlib
import json
import math
import shutil
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np
import pytest
import qi_pathion_coset_coin_cases as cc
import qi_pathion_one_cz_null_analysis as ana
import qi_pathion_one_cz_null_bracketed_cases as bc
import qi_pathion_one_cz_null_cases as oc
import qi_pathion_one_cz_null_rule_v2 as rule
import qi_platform_wave as wave

import qi_records

ROOT = Path(__file__).resolve().parents[2]
CASES = ROOT / "results/quantum_inspire/cases"
PREDECESSOR_CASE = CASES / "pathion_one_cz_null_tuna_17"
# sha256 over the sorted "relative path, NUL, file sha256, newline" rows of the 78 files of the frozen predecessor case.
PREDECESSOR_TREE_SHA256 = "d9bc49303f7c8bf66593e460394a25a5e72a5cd77de42c568b013621f715988b"
SELECTOR_BIT = 3  # logical bit order d0, d1, d2, selector, coin
N = 16384  # shots per circuit of a template batch: half the predecessor's 32,768
TWIN_BATCHES = [8 * r + n for r in range(4) for n in (1, 2, 5, 6)]  # four rounds of the 8-batch round
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

BACKEND_RECORD = {"max_jobs_per_batch_job": 5, "batchjobs_per_queue_limit": 5}


def test_the_series_holds_thirty_five_batches_within_the_wave_policy(built: dict[str, dict[str, str]]) -> None:
    manifests = _manifests(built[bc.TUNA_SERIES])
    _expect(len(manifests) == 35, f"{len(manifests)} batches")
    _expect(all(m["hardware_policy"] == "wave-v1" for m in manifests), "every batch names the wave policy")
    _expect(all(len(m["circuits"]) <= 5 for m in manifests), "five circuits a batch at most")
    _expect(all(m["shots"] <= 131072 and m["register"] == [2, 4, 8, 11, 12] for m in manifests), "limits")
    kinds = [m["kind"] for m in manifests]
    _expect(kinds.count("base") == 16 and kinds.count("twin") == 16 and kinds[32:] == ["joint"] * 3, f"{kinds}")
    _expect([len(m["circuits"]) for m in manifests if m["kind"] == "base"] == [3] * 16, "base batches")
    _expect([len(m["circuits"]) for m in manifests if m["kind"] == "twin"] == [4] * 16, "twin batches")
    _expect([len(m["circuits"]) for m in manifests[32:]] == [3, 3, 2], "the calibration batches")
    for kind in ("base", "twin"):
        held = Counter(m["template"] for m in manifests if m["kind"] == kind)
        _expect(held == {"b0": 4, "k4": 4, "k8": 4, "k12": 4}, f"four replicates of every template and kind: {held}")
    shots = {(m["kind"], m["template"]): m["shots"] for m in manifests if m["kind"] in ("base", "twin")}
    _expect(shots[("base", "b0")] == 65536 and shots[("twin", "b0")] == 16384, "b0 base 65,536, a twin 16,384")
    _expect(shots[("base", "k4")] == shots[("twin", "k12")] == 16384, "16,384 shots per other circuit")
    _expect({m["shots"] for m in manifests[32:]} == {16384}, "calibration shots")
    _expect(
        sorted(m["batch"] for m in manifests if m["kind"] == "twin") == [f"batch-{n:02d}" for n in TWIN_BATCHES],
        "twins",
    )


def test_the_wave_policy_admits_the_manifests_and_the_legacy_policy_refuses_a_twin_batch(
    built: dict[str, dict[str, str]],
) -> None:
    for m in _manifests(built[bc.TUNA_SERIES]):
        limits = wave.hardware_limits(m, BACKEND_RECORD)
        _expect((limits.batch_circuits, limits.queued_batches, limits.pause_seconds) == (5, 3, 60), f"{limits}")
        _expect(len(m["circuits"]) <= limits.batch_circuits, f"{m['batch']} exceeds the wave policy")
        legacy = {k: v for k, v in m.items() if k != "hardware_policy"}
        too_big = len(m["circuits"]) > wave.hardware_limits(legacy, BACKEND_RECORD).batch_circuits
        _expect(too_big == (m["kind"] == "twin"), f"{m['batch']}: only a twin batch needs the wave policy")
    _expect(all("hardware_policy" not in m for m in _manifests(built[bc.QX_SERIES])), "QX is no hardware backend")


def test_the_series_index_groups_the_batches_into_waves_of_at_most_fifteen_circuits(
    built: dict[str, dict[str, str]],
) -> None:
    files = built[bc.TUNA_SERIES]
    index = json.loads(files["cases.json"])
    names = [f"batch-{n:02d}" for n in range(35)]
    expected = [names[i : i + 3] for i in range(0, 35, 3)]
    _expect(index["hardware_policy"] == "wave-v1" and index["waves"] == expected, f"{index['waves']}")
    _expect(len(expected) == 12 and [len(w) for w in expected] == [3] * 11 + [2], "twelve waves")
    for names_in_wave in expected:
        circuits = sum(len(json.loads(files[f"{b}/cases.json"])["circuits"]) for b in names_in_wave)
        _expect(circuits <= 15, f"{names_in_wave}: {circuits} circuits")


def test_every_twin_batch_holds_both_coin_twins_between_the_two_readouts(built: dict[str, dict[str, str]]) -> None:
    twins = [m for m in _manifests(built[bc.TUNA_SERIES]) if m["kind"] == "twin"]
    _expect(len(twins) == 16, "sixteen twin batches")
    for m in twins:
        files = [c["file"] for c in m["circuits"]]
        order = (0, 1) if m["replicate"] % 2 == 0 else (1, 0)
        want = ["readout-0.cq", *(f"{m['template']}-coin{c}.cq" for c in order), "readout-1.cq"]
        _expect(files == want, f"{m['batch']}: {files}")
        _expect([c.get("coin") for c in m["circuits"] if c["kind"] == "data"] == list(order), f"{m['batch']} coins")
        _expect(m["shots"] == 16384, f"{m['batch']} shots")


def test_the_rounds_alternate_forward_and_mirror_order(built: dict[str, dict[str, str]]) -> None:
    manifests = _manifests(built[bc.TUNA_SERIES])
    rounds = [[(m["template"], m["kind"]) for m in manifests[8 * r : 8 * r + 8]] for r in range(4)]
    _expect(rounds[1] == rounds[0][::-1] and rounds[2] == rounds[0] and rounds[3] == rounds[0][::-1], "alternating")
    _expect([m["replicate"] for m in manifests[:32]] == [r for r in range(4) for _ in range(8)], "replicate labels")
    _expect(
        [m["kind"] for m in manifests[:8]] == ["base", "twin", "twin", "base", "base", "twin", "twin", "base"], "lead"
    )


def test_a_linear_drift_cancels_in_the_pooled_twin_contrast_of_the_mirrored_order() -> None:
    # A drift of `gain` per circuit position across the series. The coin-1 twin runs after the coin-0 twin in a forward
    # round and before it in a mirror round, so the contrast carries +gain and -gain and four replicates sum to zero.
    rows = bc.batch_rows(bc.TUNA_SERIES)
    gain = 0.01
    for template in ("b0", "k4", "k8", "k12"):
        contrast = []
        for replicate in range(4):
            (row,) = [
                r for r in rows if r["kind"] == "twin" and r["template"] == template and r["replicate"] == replicate
            ]
            at = {c["coin"]: i for i, c in enumerate(row["circuits"]) if c["kind"] == "data"}
            contrast.append(gain * (at[1] - at[0]))
        _expect(contrast == [gain, -gain, gain, -gain] and sum(contrast) == 0.0, f"{template}: {contrast}")


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
    _expect(len(rows) >= 16 + 8 + 16 + 8, f"{len(rows)} twin rows")
    for row in rows:
        ideal = row["ideal"]
        zero = sum(p for i, p in enumerate(ideal) if not (i >> SELECTOR_BIT) & 1)
        _expect(abs(zero - 0.5) < 1e-9, f"{row['file']}: P(s=0) {zero}")


def test_jobs_shots_and_seconds_follow_plain_arithmetic(built: dict[str, dict[str, str]]) -> None:
    jobs = 16 * 3 + 16 * 4 + 8
    shots = 4 * 3 * 65536 + 3 * 4 * 3 * 16384 + 4 * 4 * 4 * 16384 + (3 + 3 + 2) * 16384
    _expect(jobs == 120 and shots == 2555904, "the layout's counts")
    design = bc.design()
    _expect(design["jobs"] == jobs and design["shots_total"] == shots and design["batches"] == 35, f"{design}")
    _expect(design["waves"] == 12 and design["circuits_per_batch_max"] == 4, "waves and batch size")
    _expect(design["hardware_policy"] == "wave-v1" and design["circuits_per_wave_max"] == 11, f"{design}")
    _expect(design["replicates"] == 4 and design["batch_chi2_degrees_of_freedom"] == 3, f"{design}")
    manifests = _manifests(built[bc.TUNA_SERIES])
    _expect(sum(len(m["circuits"]) for m in manifests) == jobs, "jobs from the manifests")
    _expect(sum(len(m["circuits"]) * m["shots"] for m in manifests) == shots, "shots from the manifests")
    low = jobs * 2.6 + shots * 0.53e-3
    _expect(abs(low - 1666.6) < 0.05, f"low {low}")
    _expect(design["execution_seconds_range_tenths"][0] == round(low * 10), "low bound")
    rate = oc.coin_timing()["seconds_per_shot_max"]
    _expect(abs(rate - 0.59057e-3) < 1e-8, f"the measured maximum {rate}")
    high = jobs * 2.6 + shots * rate
    _expect(abs(high - 1821.4) < 0.05, f"high {high}")
    _expect(design["execution_seconds_range_tenths"][1] == round(high * 10), "high bound")
    # The rounded 0.59 ms per shot of the case's estimate gives 41.3 s for the longest job.
    _expect(abs(2.6 + 65536 * 0.59e-3 - 41.3) < 0.05, "0.59 ms")
    longest = 2.6 + 65536 * rate
    _expect(longest < 300 and design["longest_job_seconds_tenths"] == round(longest * 10) == 413, f"{longest}")
    # A wave procedure pays one 60 s pause per wave boundary (policy table), 11 boundaries between 12 waves.
    _expect(design["pause_seconds_per_wave"] == 60 and design["pause_seconds_total"] == 11 * 60 == 660, "pauses")


def test_the_design_standard_errors_follow_the_arm_variances() -> None:
    e01, e10 = bc.retained_selector_rates()
    _expect(abs(e01 - E01) < 5e-5 and abs(e10 - E10) < 5e-5, f"{e01} {e10}")
    per_p = 0.25 / N
    per_bracket = (e10 * (1 - e10) / N + e01 * (1 - e01) / N) / 4
    _expect(abs(per_p - 1.5259e-5) < 1e-9 and abs(per_bracket - 8.55e-7) < 5e-9, f"{per_p} {per_bracket}")
    contrast = math.sqrt(2 * per_p)
    _expect(abs(contrast - 0.005524) < 2e-6, f"{contrast}")
    _expect(abs(contrast / 2 - 0.002762) < 2e-6, "pooled over four replicates: the two-replicate error at 32,768 shots")
    design = bc.design()
    _expect(design["twin_batch_se_micro"] == round(contrast * 1e6), "design contrast se")
    _expect(design["pooled_se_micro"]["twin"] == round(contrast / 2 * 1e6), "design pooled se")
    _expect(design["pooled_se_micro"]["base"] == round(1 / math.sqrt(N * 4) * 1e6) == 3906, "pooled base se")
    _expect(design["pooled_se_micro"]["b0_base"] == round(1 / math.sqrt(65536 * 4) * 1e6) == 1953, "pooled b0 base se")
    _expect(design["bracket_offset_se_micro"] == round(math.sqrt(per_bracket) * 1e6), "design offset se")
    _expect(design["design_selector_readout_e01_e10_ten_thousandths"] == [281, 296], "design rates")


# Estimator ------------------------------------------------------------------------------------------------------


def test_the_bracket_offset_cancels_in_the_twin_contrast() -> None:
    p0, p1 = 5100 / N, 5400 / N
    value, se = bc.twin_contrast(5400, N, 5100, N)
    _expect(abs(value - (p1 - p0)) < 1e-12, f"{value} against {p1 - p0}")
    # (P1 - c) - (P0 - c) with the batch's own c, from any readout counts, is the same number.
    for ones0, zeros1 in ((300, 900), (0, 0), (1000, 200)):
        c, _ = bc.bracket_offset(ones0, N, zeros1, N)
        _expect(abs(((p1 - c) - (p0 - c)) - value) < 1e-12, f"offset {c}")
    expected = math.sqrt(p1 * (1 - p1) / N + p0 * (1 - p0) / N)
    _expect(abs(se - expected) < 1e-15, f"{se} against {expected}")


def test_the_bracket_offset_and_its_variance_follow_the_assignment_errors() -> None:
    c, variance = bc.bracket_offset(900, N, 970, N)
    e01, e10 = 900 / N, 970 / N
    _expect(abs(c - (e10 - e01) / 2) < 1e-15, f"{c}")
    _expect(abs(variance - (e01 * (1 - e01) / N + e10 * (1 - e10) / N) / 4) < 1e-15, f"{variance}")


def _selector_string(selector: int, width: int = 5) -> str:
    """A bit string of `width` bits with the selector qubit (register index 2) set to `selector`."""
    bits = ["0"] * width
    bits[width - 1 - 2] = str(selector)
    return "".join(bits)


def _shots(zeros: int, total: int) -> list[str]:
    return [_selector_string(0)] * zeros + [_selector_string(1)] * (total - zeros)


def test_the_batch_brackets_report_each_offset_and_the_corrected_twin_readings() -> None:
    manifest = {"templates": {"b0": {"roles": {"selector": 2}}}}
    n = 1000
    shots = {
        "batch-01/readout-0.cq": _shots(n - 30, n),  # 30 of 1000 read 1: e01 = 0.030
        "batch-01/readout-1.cq": _shots(50, n),  # 50 of 1000 read 0: e10 = 0.050
        "batch-01/b0-coin0.cq": _shots(480, n),
        "batch-01/b0-coin1.cq": _shots(530, n),
        "batch-00/b0.cq": _shots(n // 2, n),
    }
    got = bc.batch_brackets(shots, manifest)
    _expect(list(got) == ["batch-01"], f"{list(got)}")
    row = got["batch-01"]
    c = (0.050 - 0.030) / 2
    _expect(row["template"] == "b0" and abs(row["offset"] - c) < 1e-15, f"{row}")
    se = math.sqrt((0.05 * 0.95 / n + 0.03 * 0.97 / n) / 4)
    _expect(abs(row["offset_se"] - se) < 1e-15, f"{row['offset_se']} against {se}")
    _expect(
        abs(row["corrected_p"]["0"] - (0.480 - c)) < 1e-15 and abs(row["corrected_p"]["1"] - (0.530 - c)) < 1e-15,
        "P - c",
    )


def test_the_standard_error_agrees_with_a_monte_carlo_of_binomial_counts() -> None:
    from qrng_seeds import read_record

    rng = np.random.default_rng(int(read_record(bc.OC_DRAW)["values"][bc.OC_SEED_INDICES[bc.STATIONARY_TABLE]]))
    draws = 20000
    p_read = 0.5 + (E10 - E01) / 2
    zeros = rng.binomial(N, p_read, size=(2, draws))
    contrasts = np.array([bc.twin_contrast(int(zeros[1, i]), N, int(zeros[0, i]), N)[0] for i in range(draws)])
    se = math.sqrt(2 * 0.25 / N)
    _expect(abs(float(contrasts.std()) / se - 1) < 0.05, f"{contrasts.std()} against {se}")
    _expect(abs(float(contrasts.mean())) < 4 * se / math.sqrt(draws), f"mean {contrasts.mean()}")


def test_a_deterministic_arm_yields_a_finite_pooled_error() -> None:
    value, se = bc.twin_contrast(N, N, N, N)
    _expect(value == 0.0 and se > 0 and math.isfinite(se), f"{value} {se}")
    mean, pooled_se = ana.pooled([(0.01, se), (0.02, se)])
    _expect(math.isfinite(mean) and math.isfinite(pooled_se) and pooled_se > 0, f"{pooled_se}")
    _, offset_variance = bc.bracket_offset(0, N, 0, N)
    _expect(offset_variance > 0 and math.isfinite(offset_variance), f"{offset_variance}")
    # A deterministic selector arm is the QX readout: zero misassigned shots out of N takes the finite-count interval.
    z2 = float(oc.Z_RESOLVE * oc.Z_RESOLVE)
    center = (z2 / 2) / (N + z2)
    _expect(abs(ana.arm_variance(0.0, N) - center * (1 - center) / (N + z2)) < 1e-18, "Agresti-Coull variance")


# Decision -------------------------------------------------------------------------------------------------------


def _twin_se() -> float:
    return math.sqrt(2 * 0.25 / N)


def _rows(base: dict[str, float], twin: dict[str, float]) -> dict[str, dict[str, list[tuple[float, float]]]]:
    se_base = {t: 1 / math.sqrt(bc.CONTROL_SHOTS if t == "b0" else bc.BATCH_SHOTS) for t in oc.TEMPLATES}
    return {
        t: {
            "base": [(base.get(t, 0.0), se_base[t])] * bc.REPLICATES,
            "twin": [(twin.get(t, 0.0), _twin_se())] * bc.REPLICATES,
        }
        for t in oc.TEMPLATES
    }


def test_rule_v2_labels_hand_built_bracketed_rows() -> None:
    se_t0 = _twin_se() / math.sqrt(bc.REPLICATES)
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
    _expect("cancels in t" in text["estimates"] and text["estimates"] != old["estimates"], "estimates")
    _expect(
        {k for k in text if text[k] != old[k]} == {"estimates", "twin_control", "heterogeneity"},
        "only the estimates, the twin control and the replicate-matched heterogeneity bound change",
    )
    _expect(str(bc.BATCH_CHI2) in text["heterogeneity"] and "3 degrees of freedom" in text["heterogeneity"], "gate")


def _survival(dof: int, x: float) -> float:
    """P(chi-square with `dof` degrees of freedom > x) for 1, 2 and 3 degrees of freedom, in closed form."""
    if dof == 1:
        return math.erfc(math.sqrt(x / 2))
    if dof == 2:
        return math.exp(-x / 2)
    return math.erfc(math.sqrt(x / 2)) + math.sqrt(2 * x / math.pi) * math.exp(-x / 2)


def test_the_batch_gate_is_the_alpha_0_001_quantile_of_the_replicates_degrees_of_freedom() -> None:
    for dof, bound in bc.CHI2_ALPHA_001.items():
        _expect(abs(_survival(dof, bound) - 0.001) < 5e-7, f"{dof} degrees of freedom: {bound}")
    _expect(bc.BATCH_CHI2 == bc.CHI2_ALPHA_001[bc.REPLICATES - 1] == 16.266, "four replicates, 3 degrees of freedom")
    _expect(oc.BATCH_CHI2 == bc.CHI2_ALPHA_001[1], "the predecessor's bound is the 1-degree-of-freedom value")


def test_the_replicate_matched_gate_admits_the_spread_that_the_one_degree_bound_rejects() -> None:
    # Four twin contrasts of k4 at [0, 0, 0, d se] have chi-square 3 d^2 / 4 about their weighted mean.
    se = _twin_se()
    for d, matched_rejects in ((4.5, False), (5.0, True)):
        rows = _rows({"b0": 0.0164}, {})
        rows["k4"]["twin"] = [(0.0, se), (0.0, se), (0.0, se), (d * se, se)]
        chi2 = 0.75 * d * d
        _expect((chi2 > 16.266) == matched_rejects and chi2 > 10.828, f"{chi2}")
        _expect(rule.decide_estimates(rows)["label"] == "unresolved_batch", "the 1-degree bound rejects the spread")
        got = bc.decide_estimates(rows)["label"]
        _expect((got == "unresolved_batch") == matched_rejects, f"{chi2}: {got}")


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


def test_a_coin_conditioned_dropout_survives_the_twin_contrast_at_expected_counts() -> None:
    # Only the coin-1 twin's selector misreads more: a true selector 1 reads 0 with probability x on its shots. Both
    # twins share the batch's bracket, so the contrast is the dropout's lambda x / 2 on the raw scale.
    x, e01, e10 = 0.0362, E01, E10
    lam = 1 - e01 - e10
    coin0 = round((e10 + lam * 0.5) * N)
    coin1 = round((e10 + lam * (0.5 + x / 2)) * N)
    value, se = bc.twin_contrast(coin1, N, coin0, N)
    _expect(abs(value - lam * x / 2) < 3 * se and abs(value - lam * x / 2) < 1e-4, f"{value} against {lam * x / 2}")
    _expect(value > oc.Z_RESOLVE * se, "the injected contrast is resolved above 3 se")


@pytest.mark.audit
def test_a_coin_conditioned_dropout_survives_the_twin_contrast_of_the_series(
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
    brackets = bc.batch_brackets(shots, manifest)
    _expect(sorted(brackets) == [f"batch-{n:02d}" for n in TWIN_BATCHES], f"{sorted(brackets)}")
    offsets = [row["offset"] for row in brackets.values()]
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
    """Eight-shot lists of every twin batch of the series: its two twin circuits and two readouts (all qubits 0)."""
    width = manifest["nqubits"]
    shots: dict[str, list[str]] = {}
    for row in bc.batch_rows(bc.TUNA_SERIES):
        if row["kind"] != "twin":
            continue
        for circuit in row["circuits"]:
            shots[f"{row['batch']}/{circuit['file']}"] = ["0" * width] * 8
    return shots


def test_a_twin_batch_estimate_is_the_raw_contrast_of_its_two_twins(manifest: dict[str, Any]) -> None:
    shots = _twin_shots(manifest)
    width = manifest["nqubits"]
    selector = manifest["templates"]["b0"]["roles"]["selector"]
    zero, one = "0" * width, "0" * (width - 1 - selector) + "1" + "0" * selector
    shots["batch-01/b0-coin1.cq"] = [zero] * 6 + [one] * 2
    rows, _ = bc.batch_estimates(shots, manifest)
    value, se = bc.twin_contrast(6, 8, 8, 8)
    got = rows["b0"]["twin"]
    _expect(len(got) == 4 and abs(got[0][0] - value) < 1e-15 and abs(got[0][1] - se) < 1e-15, f"{got}")
    _expect(abs(value - (6 / 8 - 1.0)) < 1e-15, f"{value}")


def test_a_series_with_a_missing_or_misplaced_twin_is_refused(manifest: dict[str, Any]) -> None:
    shots = _twin_shots(manifest)
    rows, _ = bc.batch_estimates(shots, manifest)
    _expect(
        all(len(rows[t]["twin"]) == 4 and rows[t]["base"] == [] for t in oc.TEMPLATES), "four replicates a template"
    )
    without = {k: v for k, v in shots.items() if not k.startswith("batch-02/")}
    rows, _ = bc.batch_estimates(without, manifest)
    _expect(len(rows["k4"]["twin"]) == 3, "a missing batch leaves three k4 replicates for the evaluation to refuse")
    half = {k: v for k, v in shots.items() if k != "batch-02/k4-coin1.cq"}
    with pytest.raises(ValueError, match="holds one coin twin"):
        bc.batch_estimates(half, manifest)
    moved = {(k.replace("batch-02/", "batch-01/") if "k4-coin1" in k else k): v for k, v in shots.items()}
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


def test_each_table_seeds_from_its_own_value_of_the_registered_draw_in_index_order() -> None:
    from qrng_seeds import read_record

    stored = _stored()["operating_characteristics"]
    tables = ("stationary", "batch_drift_sd_0.003", "pair_common_drift_sd_0.003")
    indices = [stored["seed_indices"][t] for t in tables]
    _expect(stored["qrng_draw"] == bc.OC_DRAW and stored["seed_indices"] == bc.OC_SEED_INDICES, "named draw")
    _expect(indices == sorted(set(indices)) and indices[0] >= 920, f"{indices}: increasing, distinct, from 920 up")
    values = read_record(bc.OC_DRAW)["values"]
    seeds = [int(values[i]) for i in indices]
    _expect(len(set(seeds)) == 3, "three distinct seed values")
    world = {rule.NEGATIVE_TWIN_WORLD: rule.NEGATIVE_TWIN_MEAN}
    a = bc.operating_characteristics(indices[0], draws=64, worlds=world)
    _expect(a == bc.operating_characteristics(indices[0], draws=64, worlds=world), "an index fixes the draws")
    _expect(bc.OC_DRAW != oc.OC_DRAW and (ROOT / bc.OC_DRAW).is_file(), "a new draw")


def test_the_stored_tables_hold_the_power_of_each_drift_model() -> None:
    ocs = _stored()["operating_characteristics"]
    tables = ("stationary", "batch_drift_sd_0.003", "pair_common_drift_sd_0.003")
    share = {t: {w: {k: v / 10000 for k, v in row.items()} for w, row in ocs[t].items()} for t in tables}
    _expect(all(set(share[t]) == set(rule.WORLDS) for t in tables), "worlds")
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
    # The preregistered power rule (80 percent) under a drift of 0.003: met both when every twin contrast drifts
    # independently and when the drift of a batch is common to the two twins of its pair.
    for world, label in (("coin_dropout", "b0_like"), ("superposition_only", "superposition_only")):
        _expect(share["pair_common_drift_sd_0.003"][world][label] >= 0.80, f"pair-common {world}")
        _expect(share["batch_drift_sd_0.003"][world][label] >= 0.80, f"per-contrast {world}")
        _expect(
            share["pair_common_drift_sd_0.003"][world][label] > share["batch_drift_sd_0.003"][world][label],
            f"a drift that cancels in the pair raises the power of {world}",
        )


def test_the_successor_simulation_reaches_spawned_workers_and_is_serial_equal() -> None:
    world = {rule.NEGATIVE_TWIN_WORLD: rule.NEGATIVE_TWIN_MEAN}
    seed = bc.OC_SEED_INDICES[bc.STATIONARY_TABLE]
    first = bc.operating_characteristics(seed, draws=128, worlds=world)
    again = bc.operating_characteristics(seed, draws=128, worlds=world)
    _expect(first == again, "a rerun reproduces the draws")
    _expect(first[rule.NEGATIVE_TWIN_WORLD].get(rule.NEGATIVE_TWIN, 0.0) >= 0.8, f"{first}")


def test_a_drift_shared_by_a_pair_spares_its_twin_contrast_and_an_unknown_model_is_refused() -> None:
    world = {rule.NEGATIVE_TWIN_WORLD: rule.NEGATIVE_TWIN_MEAN}
    seed = bc.OC_SEED_INDICES[bc.CONTRAST_DRIFT_TABLE]
    independent = bc.operating_characteristics(seed, draws=256, drift_sd=0.01, worlds=world)
    shared = bc.operating_characteristics(seed, draws=256, drift_sd=0.01, worlds=world, drift_model="pair")
    decided = rule.NEGATIVE_TWIN
    _expect(
        shared[rule.NEGATIVE_TWIN_WORLD].get(decided, 0.0) > independent[rule.NEGATIVE_TWIN_WORLD].get(decided, 0.0),
        "twin drift",
    )
    with pytest.raises(ValueError, match="drift_model"):
        bc.operating_characteristics(seed, draws=8, drift_model="batch")


def test_a_larger_drift_lowers_the_deciding_share_of_the_dropout_world() -> None:
    world = {"coin_dropout": rule.WORLDS["coin_dropout"]}
    seed = bc.OC_SEED_INDICES[bc.STATIONARY_TABLE]
    still = bc.operating_characteristics(seed, draws=256, worlds=world)["coin_dropout"]["b0_like"]
    drifting = bc.operating_characteristics(seed, draws=256, drift_sd=0.01, worlds=world)["coin_dropout"].get(
        "b0_like", 0.0
    )
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
    _expect(len(manifests) == 4 and all(len(m["circuits"]) == 5 for m in manifests), "four batches of five")
    _expect(sum(len(m["circuits"]) for m in manifests) == 20 and manifests[0]["shots"] == 2048, "20 circuits")
    for m in manifests:
        files = [c["file"] for c in m["circuits"]]
        name = m["template"]
        want = ["readout-0.cq", f"{name}-coin0.cq", f"{name}-coin1.cq", "readout-1.cq", f"{name}.cq"]
        _expect(files == want, f"{files}")


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
    swapped["batch-00/b0-coin0.cq"], swapped["batch-00/b0-coin1.cq"] = (
        counts["batch-00/b0-coin1.cq"],
        counts["batch-00/b0-coin0.cq"],
    )
    _expect(not bc.qx_check(swapped)["qx_control"]["pass"], "a wrong circuit passes")


def _runs(root: Path, series: str, files: dict[str, str], shots: dict[str, list[str]]) -> list[Path]:
    """Collected run directories `<stamp>-<series>-batch-NN` of every batch, in qi_platform.collect's layout."""
    cases_root = root / "cases" / series
    for rel, text in files.items():
        path = cases_root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    dirs = []
    for batch in sorted({rel.split("/")[0] for rel in files if rel.startswith("batch-")}):
        cases = json.loads((cases_root / batch / "cases.json").read_text(encoding="utf-8"))
        run = root / "runs" / f"2026-11-15T000000Z-{series}-{batch}"
        shutil.copytree(cases_root / batch, run)
        (run / "raw").mkdir()
        n = int(batch.removeprefix("batch-"))
        submitted, collected = [], []
        for k, row in enumerate(cases["circuits"]):
            listed = shots[f"{batch}/{row['file']}"]
            (run / "raw" / f"{row['file']}.json").write_text(json.dumps(listed), encoding="utf-8")
            job = {
                "id": 100 * n + k,
                "created_on": f"2026-11-15T00:{n:02d}:00.000000Z",
                "status": "completed",
                "batch_job_id": 77 + n,
                "queued_at": f"2026-11-15T00:{n:02d}:{k:02d}.000000Z",
                "finished_at": f"2026-11-15T01:{n:02d}:{k:02d}.000000Z",
                "number_of_shots": cases["shots"],
            }
            result = {
                "job_id": job["id"],
                "shots_requested": cases["shots"],
                "shots_done": cases["shots"],
                "results": dict(sorted(Counter(listed).items())),
            }
            submitted.append({"file": row["file"], "job": job["id"], "sha256": row["sha256"]})
            collected.append({"file": row["file"], "job": job, "results": [result], "logs": ""})
        receipt = {
            "schema": "qi-submission-v2",
            "state": "enqueued",
            "approval": "fixture",
            "backend": cases["backend"],
            "backend_type_id": cases["backend_type_id"],
            "cases_sha256": qi_records.digest((run / "cases.json").read_bytes()),
            "batch_job": 77 + n,
            "shots": cases["shots"],
            "jobs": submitted,
        }
        (run / "submission.json").write_text(json.dumps(receipt), encoding="utf-8")
        (run / "results.json").write_text(
            json.dumps({"schema": "qi-collection-v1", "transactions": [], "jobs": collected}), encoding="utf-8"
        )
        dirs.append(run)
    return dirs


def test_analyze_reads_the_collected_qx_series_and_reports_the_bracket_arithmetic(
    tmp_path: Path, built: dict[str, dict[str, str]]
) -> None:
    files = built[bc.QX_SERIES]
    counts = _qx_counts(files)
    shots = {key: [s for s, n in sorted(hist.items()) for _ in range(n)] for key, hist in counts.items()}
    dirs = _runs(tmp_path, bc.QX_SERIES, files, shots)
    record = bc.analyze(dirs, tmp_path / "cases")
    _expect(record["claim_kind"] == oc.CONTROL_KIND and record["complete"], f"{record}")
    _expect(record["schema"] == bc.ANALYSIS_SCHEMA, "the successor's analysis schema")
    _expect(record["qx_control"]["pass"] and record["qx_brackets"]["pass"], f"{record['qx_brackets']}")
    _expect(len(record["qx_control"]["arms"]) == 12, "every base circuit and twin is controlled")
    json.dumps(record, allow_nan=False)
    partial = bc.analyze(dirs[:3], tmp_path / "cases")
    _expect(not partial["complete"] and "qx_brackets" not in partial, f"{partial['batches']}")


@pytest.mark.audit
def test_analyze_scores_the_collected_tuna_series_and_reports_an_incomplete_one(
    tmp_path: Path, built: dict[str, dict[str, str]], worlds: dict[str, dict[str, list[str]]]
) -> None:
    dirs = _runs(tmp_path, bc.TUNA_SERIES, built[bc.TUNA_SERIES], worlds["over_rotation"])
    record = bc.analyze(dirs, tmp_path / "cases")
    _expect(record["complete"] and record["claim_kind"] == "hardware acquisition", f"{record.get('batches')}")
    _expect(record["schema"] == bc.ANALYSIS_SCHEMA and record["decision"]["label"] == "zero", f"{record['decision']}")
    json.dumps(record, allow_nan=False)
    _expect(len(record["batch_contrasts"]["b0"]["twin"]) == 4, "four twin contrasts per template")
    brackets = record["twin_brackets"]
    _expect(sorted(brackets) == [f"batch-{n:02d}" for n in TWIN_BATCHES], f"{sorted(brackets)}")
    _expect(all(math.isfinite(b["offset"]) and b["offset_se"] > 0 for b in brackets.values()), "offsets")
    partial = bc.analyze(dirs[:3], tmp_path / "cases")
    _expect(not partial["complete"] and partial["batches"] == ["batch-00", "batch-01", "batch-02"], f"{partial}")
    sanity = bc.sanity(dirs[:8], tmp_path / "cases")
    _expect(sanity["batches"] == [f"batch-{n:02d}" for n in range(8)] and sanity["drift"], "sanity")
