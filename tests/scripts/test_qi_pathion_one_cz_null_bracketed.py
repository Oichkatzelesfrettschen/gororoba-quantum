"""Contracts of the bracketed-twin successor case of the Tuna-17 one-CZ null series.

Each expectation is computed in the test from plain arithmetic, the retained series' records or the platform's own
constants, never from the producer's design or layout functions. The audit-marked tests regenerate the committed case
directories (the second also the stored operating characteristics, 60 simulations of 20,000 series).
"""

from __future__ import annotations

import copy
import hashlib
import itertools
import json
import math
import os
import shutil
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pytest
import qi_pathion_coset_coin_cases as cc
import qi_pathion_one_cz_null_analysis as ana
import qi_pathion_one_cz_null_bracketed_cases as bc
import qi_pathion_one_cz_null_cases as oc
import qi_pathion_one_cz_null_executed_order as eo
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
    text = bc.control_preregistered()
    old = oc.preregistered()
    _expect(text["twin_control"] == rule.TWIN_CONTROL != old["twin_control"], "twin control")
    _expect("cancels in t" in text["estimates"] and text["estimates"] != old["estimates"], "estimates")
    _expect(
        {k for k in text if text[k] != old[k]} == {"estimates", "twin_control", "heterogeneity"},
        "only the estimates, the twin control and the replicate-matched heterogeneity bound change",
    )
    _expect(str(bc.BATCH_CHI2) in text["heterogeneity"] and "3 degrees of freedom" in text["heterogeneity"], "gate")


def test_the_registered_rule_states_the_executed_order_once_and_names_every_label_it_can_read() -> None:
    text, control = bc.preregistered(), bc.control_preregistered()
    _expect(set(text) - set(control) == {"executed_order", "base_level", "drift_monitor", "withheld"}, f"{set(text)}")
    _expect({k for k in control if control[k] != text[k]} == {"estimates"}, "only the estimates restate")
    _expect("executed" in text["estimates"] and "plain" not in text["estimates"], text["estimates"])
    for label in bc.WITHHELD_LABELS:
        _expect(label in text["withheld"] and label in bc.OUTCOMES, f"{label} is not registered")
    _expect(set(bc.WITHHELD_LABELS) == {k for k in bc.OUTCOMES if k not in rule.OUTCOMES}, "labels outside the table")
    # The Tuna-17 manifests and the prediction record state the executed-order text; the QX control manifests state the
    # control text that the hosted run's receipts bind.
    built = bc.build()
    for rel, body in built[bc.TUNA_SERIES].items():
        if rel.endswith("cases.json") and "/" in rel:
            _expect(json.loads(body)["preregistered"] == text, f"{rel} states another rule")
    for rel, body in built[bc.QX_SERIES].items():
        if rel.endswith("cases.json") and "/" in rel:
            _expect(json.loads(body)["preregistered"] == control, f"{rel} states another rule")
    _expect(bc.predictions(operating=False)["preregistered"] == text, "the prediction record states another rule")
    _expect(set(bc.predictions(operating=False)["outcomes"]) == set(bc.OUTCOMES), "the outcomes of the record")


# sha256 of the four QX batch manifests: the `cases_sha256` of the hosted run's submission receipts, so the QX case
# directory keeps the bytes those receipts bind.
QX_MANIFEST_SHA256 = {
    "batch-00": "9904dc68030fd23abed32e905320c0b67e1a74df6e79a14645a2a91fc99393ee",
    "batch-01": "7aec9908027c5f06e7dcb9a288acb27de9bc9f9890b067a94dc8b5d1e43cba37",
    "batch-02": "5ac4b6c411b4234493911400da264f08f3c5b60f4184b0858ba16264c19d9b7e",
    "batch-03": "47a25a62683d922f5cc2e6461e057370871225b9d9cbed7ec6cdb74b28a1fef5",
}


def test_the_qx_manifests_keep_the_bytes_that_the_retained_receipts_bind() -> None:
    # The stored bytes are read, not rebuilt: a rebuild rounds differently on darwin-arm64.
    for batch, digest in QX_MANIFEST_SHA256.items():
        stored = (CASES / bc.QX_SERIES / batch / "cases.json").read_bytes()
        _expect(hashlib.sha256(stored).hexdigest() == digest, f"the stored {batch} manifest changed")
        _expect(json.loads(stored)["preregistered"] == bc.control_preregistered(), f"{batch} states another text")


def test_a_zero_residue_of_either_sign_serializes_as_one_zero() -> None:
    # The state-vector product leaves 1e-17..1e-33 residue where the exact value is zero, and a bare round() writes a
    # negative residue as -0.0.
    for digits in (6, 9, 12):
        for residue in (0.0, -0.0, 1e-33, -1e-33, 1.1102230246251565e-16, -1.1102230246251565e-16):
            _expect(json.dumps(oc.canonical_float(residue, digits)) == "0.0", f"{residue!r} at {digits} digits")
    _expect(json.dumps(round(-1e-33, 12)) == "-0.0", "the bare rounding of a negative residue is the hazard")
    _expect(json.dumps(oc.canonical_float(-0.995869, 6)) == "-0.995869", "a nonzero value keeps its sign and digits")
    _expect(json.dumps(oc.canonical_float(0.1248440288385, 12)) == "0.124844028839", "a nonzero value keeps its digits")


def test_the_manifest_writer_serializes_a_negative_residue_as_zero(monkeypatch: pytest.MonkeyPatch) -> None:
    # Every probability source returns -1e-33: the written manifests hold 0.0 through canonical_float at the
    # ideal_selector_contrast, ideal_c and per-circuit ideal fields.
    real_plan = oc.series_plan()
    plan = copy.deepcopy(real_plan)
    for t in plan["templates"].values():
        t["ideal_selector_contrast"] = -1e-33
        t["ideal_c"] = [-1e-33] * len(t["ideal_c"])
        t["ideal"] = np.full(len(t["ideal"]), -1e-33)
    monkeypatch.setattr(oc, "series_plan", lambda: plan)
    width = len(real_plan["templates"]["b0"]["ideal"])
    monkeypatch.setattr(oc.blk, "ideal_of_record", lambda circuit: np.full(width, -1e-33))
    oc.twin_entry.cache_clear()  # the coin-fixed twins are cached; none built from the patched sources may outlive it
    try:
        files = oc.build()[oc.QX_SERIES]
    finally:
        oc.twin_entry.cache_clear()
    _expect(all("-0.0" not in text for rel, text in files.items() if rel.endswith("cases.json")), "a -0.0 was written")
    seen = 0
    for manifest in _manifests(files):
        for name, t in manifest["templates"].items():
            _expect(t["ideal_selector_contrast"] == 0.0 and t["ideal_c"] == [0.0] * len(t["ideal_c"]), name)
        for record in manifest["circuits"]:
            if "ideal" in record:
                seen += 1
                _expect(all(x == 0.0 for x in record["ideal"]), "a circuit ideal kept a nonzero residue")
    _expect(seen > 0, "no circuit ideal was checked")


def test_the_retained_qx_manifests_hold_no_negative_zero() -> None:
    for batch in QX_MANIFEST_SHA256:
        text = (CASES / bc.QX_SERIES / batch / "cases.json").read_text(encoding="utf-8")
        _expect("-0.0," not in text and "-0.0\n" not in text, f"{batch} holds a -0.0")


def _b0_diagnostic() -> str:
    """The b0 compile of this platform as text: leg versions, BLAS, transpiler seed and the gate sequence with each
    rz angle before and after round_to_grid; the first transpile pass that differs between legs shows in this sequence."""
    import platform

    import qi_pathion_coset_block_cases as blk
    import qiskit
    import scipy

    compiled = oc.compile_b0()
    rounded = blk.round_to_grid(compiled)
    config = np.show_config(mode="dicts")  # type: ignore[no-untyped-call]
    blas = config.get("Build Dependencies", {}).get("blas", {})
    lines = [
        f"platform {platform.platform()} machine {platform.machine()} python {platform.python_version()}",
        f"qiskit {qiskit.__version__} numpy {np.__version__} scipy {scipy.__version__}",
        f"blas {blas.get('name')} {blas.get('version')} {blas.get('openblas configuration')}",
        f"transpiler_seed {oc.reference()['seed']} ops {dict(sorted(compiled.count_ops().items()))}",
    ]
    for k, (raw, snapped) in enumerate(zip(compiled.data, rounded.data, strict=True)):
        qubits = ",".join(str(compiled.find_bit(q).index) for q in raw.qubits)
        if raw.operation.name == "rz":
            angle = float(raw.operation.params[0])
            after = float(snapped.operation.params[0])
            lines.append(f"{k} rz q{qubits} {angle!r} -> {after!r} step {round(angle / blk.GRID)}")
        else:
            lines.append(f"{k} {raw.operation.name} q{qubits}")
    return "\n".join(lines)


def _first_difference(left: object, right: object, path: str = "$") -> str | None:
    """The JSON path of the first differing leaf of two parsed manifests, with both values, or None when equal."""
    if isinstance(left, dict) and isinstance(right, dict):
        for key in sorted(set(left) | set(right)):
            if key not in left or key not in right:
                return f"{path}.{key}: present in {'rebuilt' if key in left else 'stored'} only"
            found = _first_difference(left[key], right[key], f"{path}.{key}")
            if found:
                return found
        return None
    if isinstance(left, list) and isinstance(right, list):
        if len(left) != len(right):
            return f"{path}: length {len(left)} rebuilt, {len(right)} stored"
        for i, (a, b) in enumerate(zip(left, right, strict=True)):
            found = _first_difference(a, b, f"{path}[{i}]")
            if found:
                return found
        return None
    if json.dumps(left) != json.dumps(right):
        return f"{path}: rebuilt {json.dumps(left)}, stored {json.dumps(right)}"
    return None


def test_the_rebuilt_qx_manifests_equal_the_stored_bytes_and_the_receipt_digests(
    built: dict[str, dict[str, str]],
) -> None:
    out = os.environ.get("QX_B0_DIAGNOSTIC_FILE")
    if out:
        Path(out).write_text(_b0_diagnostic() + "\n", encoding="utf-8")
    # Measured on linux x86_64 and linux aarch64 with the CI-pinned interpreter: 4 of 4 rebuilt manifests have the
    # sha256 of the stored file and of the receipt's cases_sha256. hypothesis: darwin-arm64 differs in the sign of a
    # zero residue, which oc.canonical_float clears; no darwin run has measured it. Every platform runs the rebuild, and
    # a mismatch names the first differing JSON path with both values.
    for batch, digest in QX_MANIFEST_SHA256.items():
        rebuilt = built[bc.QX_SERIES][f"{batch}/cases.json"].encode()
        stored = (CASES / bc.QX_SERIES / batch / "cases.json").read_bytes()
        if rebuilt != stored:
            where = _first_difference(json.loads(rebuilt), json.loads(stored))
            _expect(
                False,
                f"the rebuilt {batch} manifest differs from the stored file at {where}\n{_b0_diagnostic()}",
            )
        _expect(hashlib.sha256(rebuilt).hexdigest() == digest, f"the rebuilt {batch} manifest differs from the receipt")
        _expect(rebuilt == stored, f"the rebuilt {batch} manifest differs from the stored file")


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
    result = bc.evaluate(worlds[world], manifest, _stamped())
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
    tables = ("stationary", "batch_drift_sd_0.003", "pair_common_drift_sd_0.003", *bc.EXECUTED_TABLES)
    indices = [stored["seed_indices"][t] for t in tables]
    _expect(stored["qrng_draw"] == bc.OC_DRAW and stored["seed_indices"] == bc.OC_SEED_INDICES, "named draw")
    _expect(indices == sorted(set(indices)) and indices[0] >= 920, f"{indices}: increasing, distinct, from 920 up")
    _expect(indices == list(range(920, 920 + len(tables))), f"{indices}: each value of the run used once")
    values = read_record(bc.OC_DRAW)["values"]
    seeds = [int(values[i]) for i in indices]
    _expect(len(set(seeds)) == len(tables), "distinct seed values")
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


def _executed_table(name: str) -> dict[str, Any]:
    table: dict[str, Any] = _stored()["operating_characteristics"][name]
    return {
        "labels": {w: {k: v / 10000 for k, v in row.items()} for w, row in table["labels"].items()},
        "gate": {w: v / 10000 for w, v in table["heterogeneity_gate_fired"].items()},
    }


def test_the_stored_executed_order_tables_hold_the_power_and_the_gate_rates() -> None:
    # Power at the design effect (the dropout world reads b0_like, the superposition-only world its own row) under the
    # registered rule; the preregistered power rule is 80 percent. The drift the rule corrects is the drift simulated.
    for name in ("executed_in_order", "executed_reordered_stationary", "executed_reordered_linear_drift"):
        table = _executed_table(name)
        _expect(set(table["labels"]) == set(rule.WORLDS), f"{name}: worlds")
        _expect(
            table["labels"]["coin_dropout"]["b0_like"] >= 0.88, f"{name}: dropout {table['labels']['coin_dropout']}"
        )
        _expect(table["labels"]["superposition_only"]["superposition_only"] >= 0.90, f"{name}: superposition")
        _expect(table["labels"]["twin_opposite_sign"][rule.NEGATIVE_TWIN] >= 0.94, f"{name}: negative twin")
        # False alarms of the heterogeneity gate: three errors of the difference on four templates, about one percent.
        _expect(all(0.005 < gate < 0.02 for gate in table["gate"].values()), f"{name}: gate {table['gate']}")
    kept, moved = _executed_table("executed_in_order"), _executed_table("executed_reordered_linear_drift")
    for world, label in (("coin_dropout", "b0_like"), ("superposition_only", "superposition_only")):
        _expect(abs(kept["labels"][world][label] - moved["labels"][world][label]) < 0.02, f"reordering costs {world}")
    # The stress of the 80 percent power rule: a drift of 0.003 on every contrast, or on the base contrasts alone, under
    # reordering. The pool that ignores the order reads 82.1 / 85.2 and 86.8 / 90.1 (stored tables above).
    independent = _executed_table("executed_reordered_independent_drift_sd_0.003")
    shared = _executed_table("executed_reordered_pair_common_drift_sd_0.003")
    for table, floor in ((independent, 0.80), (shared, 0.85)):
        _expect(
            table["labels"]["coin_dropout"]["b0_like"] >= floor, f"stress dropout {table['labels']['coin_dropout']}"
        )
        _expect(table["labels"]["superposition_only"]["superposition_only"] >= floor, "stress superposition-only")
    _expect(
        shared["labels"]["coin_dropout"]["b0_like"] > independent["labels"]["coin_dropout"]["b0_like"],
        "a drift that cancels in the pair raises the power",
    )
    # Detection of a planted departure of the k4 twin drift from the shared 0.003 per position.
    small, large = (
        _executed_table("executed_planted_departure_0.0075"),
        _executed_table("executed_planted_departure_0.015"),
    )
    _expect(set(small["gate"]) == set(bc.GATE_WORLDS) == set(large["gate"]), "gate worlds")
    for world in bc.GATE_WORLDS:
        _expect(0.25 < small["gate"][world] < 0.50, f"departure 0.0075 in {world}: {small['gate'][world]}")
        _expect(large["gate"][world] > 0.90, f"departure 0.015 in {world}: {large['gate'][world]}")
        _expect(large["labels"][world]["unresolved_drift_heterogeneity"] >= 0.90, f"{world}: {large['labels'][world]}")


def test_an_executed_order_table_does_not_depend_on_the_worker_count_and_rereads_its_children() -> None:
    world = {"coin_dropout": rule.WORLDS["coin_dropout"]}
    params = bc.EXECUTED_TABLES["executed_reordered_linear_drift"]
    first = bc.executed_operating_characteristics(925, params, draws=48, worlds=world)
    _expect(first == bc.executed_operating_characteristics(925, params, draws=48, worlds=world), "a rerun")
    from qrng_seeds import read_record

    children = np.random.SeedSequence(int(read_record(bc.OC_DRAW)["values"][925])).spawn(48)
    serial = [bc._executed_series(child, mean=world["coin_dropout"], params=params) for child in children]
    counts = Counter(label for label, _ in serial)
    _expect(first["labels"]["coin_dropout"] == {k: round(v / 48, 4) for k, v in sorted(counts.items())}, f"{first}")
    _expect(first["heterogeneity_gate_fired"]["coin_dropout"] == round(sum(g for _, g in serial) / 48, 4), "gate")


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


# The executed order of the batches --------------------------------------------------------------------------------


def _stamped(order_of: Any = None) -> dict[str, str]:
    """Per-job start stamps for every batch of the series; `order_of(row, files)` returns the files in execution order,
    the requested order when None. Batch n runs in minute n, one second per job."""
    stamps: dict[str, str] = {}
    for row in bc.batch_rows(bc.TUNA_SERIES):
        files = [circuit["file"] for circuit in row["circuits"]]
        for position, name in enumerate(files if order_of is None else order_of(row, files)):
            stamps[f"{row['batch']}/{name}"] = f"2026-11-08T01:{int(row['batch'][-2:]):02d}:{position:02d}.000000Z"
    return stamps


def test_the_retained_start_stamps_order_the_executions_of_a_predecessor_batch() -> None:
    # Batch-06 of the predecessor series requested readout-0, k12-coin0, k12-coin1 and ran k12-coin1 first: each job's
    # queued_at follows the previous job's finished_at within a second, so the stamps order the executions.
    run = ROOT / "results/quantum_inspire/runs/2026-11-07T202323Z-pathion_one_cz_null_tuna_17-batch-06"
    requested = [row["file"] for row in json.loads((run / "cases.json").read_text())["circuits"]]
    jobs = {row["file"]: row["job"] for row in json.loads((run / "results.json").read_text())["jobs"]}
    ran = sorted(requested, key=lambda name: jobs[name]["queued_at"])
    _expect(requested == ["readout-0.cq", "k12-coin0.cq", "k12-coin1.cq"], f"{requested}")
    _expect(ran == ["k12-coin1.cq", "readout-0.cq", "k12-coin0.cq"], f"executed {ran}")
    for earlier, later in zip(ran, ran[1:], strict=False):
        gap = (
            datetime.fromisoformat(jobs[later]["queued_at"]) - datetime.fromisoformat(jobs[earlier]["finished_at"])
        ).total_seconds()
        _expect(0 <= gap < 1.0, f"{later} queued {gap} s after {earlier} finished")


@pytest.fixture
def contrasts_of(monkeypatch: pytest.MonkeyPatch) -> Any:
    """bc.evaluate on synthetic contrasts: the simulated series is replaced by (value, se) rows that follow the drift
    models v = t + g x (twin, x the executed position offset of the given stamps) and v = mu + h (t - tau) (base, t the
    executed start of the base circuit), so the order rule alone is under test."""
    state: dict[str, Any] = {}

    def fake(shots: dict[str, list[str]], manifest: dict[str, Any], executed: Any = None) -> dict[str, Any]:
        rows = state["rows"]
        return {
            "decision": bc.decide_estimates(rows),
            "batch_contrasts": {t: {k: [list(x) for x in v] for k, v in rows[t].items()} for t in rows},
        }

    def reference(shots: Any, manifest: Any, seconds: dict[str, float]) -> tuple[list[float], list[float], list[float]]:
        times = [
            (seconds[f"{row['batch']}/readout-0.cq"] + seconds[f"{row['batch']}/readout-1.cq"]) / 2
            for row in sorted(bc.batch_rows(bc.TUNA_SERIES), key=lambda r: r["batch"])
            if row["kind"] in ("base", "twin")
        ]
        middle = sorted(times)[len(times) // 2]
        values = [0.02 + state["monitor_slope"] * t + (state["monitor_step"] if t > middle else 0.0) for t in times]
        return times, values, [1e-4] * len(times)

    def calibration(shots: Any, manifest: Any, seconds: dict[str, float]) -> list[dict[str, Any]]:
        started = {
            row["batch"]: [seconds[f"{row['batch']}/{c['file']}"] for c in row["circuits"]]
            for row in bc.batch_rows(bc.TUNA_SERIES)
            if row["kind"] == "joint"
        }
        return [{"batch": b, "time": sum(t) / len(t), "se": 1e-3} for b, t in started.items()]

    monkeypatch.setattr(bc, "evaluate_decision", fake)
    monkeypatch.setattr(bc, "batch_brackets", lambda shots, manifest: {})
    monkeypatch.setattr(bc, "bracket_series", reference)
    monkeypatch.setattr(bc, "calibration_readings", calibration)

    def evaluate(
        stamps: dict[str, Any] | None,
        truth_stamps: dict[str, str] | None = None,
        drift: Any = 0.01,
        base_slope: float = 0.0,
        monitor_slope: float = 0.0,
        monitor_step: float = 0.0,
    ) -> dict[str, Any]:
        """The record for `stamps`; the data follow the offsets and the start times of `truth_stamps` (the stamps when
        omitted), a twin drift per template (a number for one shared drift) and a base drift of `base_slope` per
        second about the template's twin reference time."""
        truth = truth_stamps if truth_stamps is not None else stamps
        offsets = bc.twin_offsets(truth)
        seconds = bc.circuit_seconds(truth)  # type: ignore[arg-type]
        tau = bc.twin_reference_times(seconds)
        per = drift if isinstance(drift, dict) else dict.fromkeys(oc.TEMPLATES, drift)
        twin: dict[str, list[tuple[float, float]]] = {t: [] for t in oc.TEMPLATES}
        for batch, (template, _, _) in sorted(bc.twin_layout().items()):
            twin[template].append((TRUE_TWIN[template] + per[template] * offsets[batch], TWIN_SE))
        base = {
            t: [
                (BASE_MU + base_slope * (seconds[f"{batch}/{t}.cq"] - tau[t]), BASE_SE)
                for batch in bc.base_batch_ids()[t]
            ]
            for t in oc.TEMPLATES
        }
        state.update(monitor_slope=monitor_slope, monitor_step=monitor_step)
        state["rows"] = {t: {"base": base[t], "twin": twin[t]} for t in oc.TEMPLATES}
        return bc.evaluate({}, {}, stamps)

    return evaluate


BASE_MU = 0.0164
TRUE_TWIN = {"b0": 0.0164, "k4": 0.0, "k8": 0.0, "k12": 0.0}
TWIN_SE = 0.0055
BASE_SE = 0.004


def _stamps_of(batch: str, order: list[str], stamps: dict[str, str]) -> dict[str, str]:
    """`stamps` with the circuits of `batch` executed in `order`, one second apart."""
    out = dict(stamps)
    for position, name in enumerate(order):
        out[f"{batch}/{name}"] = f"2026-11-08T01:{int(batch[-2:]):02d}:{position:02d}.000000Z"
    return out


def test_a_series_that_kept_its_requested_order_pools_to_the_plain_pool(contrasts_of: Any) -> None:
    record = contrasts_of(_stamped())
    fit = record["executed_order_fit"]
    _expect(fit["status"] == "fitted" and record["order_gate"]["intact"] is True, f"{fit['status']}")
    for template in oc.TEMPLATES:
        weights = [1.0 / TWIN_SE**2] * 4
        _expect(
            abs(fit["contrast"][template] - TRUE_TWIN[template]) < 1e-12, f"{template}: {fit['contrast'][template]}"
        )
        _expect(abs(fit["error"][template] - 1.0 / math.sqrt(sum(weights))) < 1e-12, f"{template}: {fit['error']}")
    _expect(abs(fit["drift"] - 0.01) < 1e-12, f"drift {fit['drift']}")
    _expect(record["decision"]["label"] == record["order_ignored_label"], "an order that was kept changed the label")


def test_a_reordered_batch_is_analyzed_on_its_executed_order_and_matches_the_series_submitted_in_order(
    contrasts_of: Any,
) -> None:
    # The platform ran three twin batches out of the requested order, to executed offsets -2, +1 and -1 (the retained
    # batches show -2, +1 and -3). The data carry a drift of 0.01 per position, so the plain
    # pool of the reordered series is biased while the executed-order fit recovers the contrasts of the series that kept
    # its order, and reads the executed offset of each batch rather than the requested one.
    layout = bc.twin_layout()
    batches = sorted(layout)
    requested = _stamped()
    plan = {
        batches[0]: lambda c0, c1, r0, r1: [c1, r0, c0, r1],
        batches[5]: lambda c0, c1, r0, r1: [r0, r1, c0, c1],
        batches[9]: lambda c0, c1, r0, r1: [c1, c0, r0, r1],
    }
    stamps = dict(requested)
    for batch, order in plan.items():
        template, c0, c1 = layout[batch]
        stamps = _stamps_of(batch, order(c0, c1, "readout-0.cq", "readout-1.cq"), stamps)
    kept = contrasts_of(requested)
    ran = contrasts_of(stamps)
    expected = {
        batch: (rank(stamps, batch, layout[batch][2]) - rank(stamps, batch, layout[batch][1])) for batch in batches
    }
    _expect(ran["executed_order_fit"]["offsets"] == expected, f"{ran['executed_order_fit']['offsets']}")
    _expect([expected[b] for b in plan] == [-2, 1, -1], f"{[expected[b] for b in plan]}")
    _expect(ran["order_gate"]["intact"] is False and kept["order_gate"]["intact"] is True, "the strict reading")
    for template in oc.TEMPLATES:
        _expect(
            abs(ran["executed_order_fit"]["contrast"][template] - kept["executed_order_fit"]["contrast"][template])
            < 1e-12,
            f"{template}: {ran['executed_order_fit']['contrast'][template]}",
        )
    _expect(abs(ran["executed_order_fit"]["drift"] - 0.01) < 1e-12, f"{ran['executed_order_fit']['drift']}")
    plain_pool = {t: sum(v for v, _ in ran["batch_contrasts"][t]["twin"]) / 4 for t in oc.TEMPLATES}
    _expect(
        max(abs(plain_pool[t] - TRUE_TWIN[t]) for t in oc.TEMPLATES) > 1e-3,
        f"the plain pool of the reordered series is not biased: {plain_pool}",
    )
    _expect(ran["decision"]["label"] == kept["decision"]["label"], f"{ran['decision']['label']}")
    _expect(not ran["decision"]["label"].startswith(("unresolved_order", "unresolved_drift")), "the fit withheld it")
    _expect(
        any(ran["executed_order_fit"]["error"][t] > kept["executed_order_fit"]["error"][t] for t in oc.TEMPLATES),
        "a reordered batch costs precision",
    )


def rank(stamps: dict[str, str], batch: str, name: str) -> int:
    """Executed place of circuit `name` among the circuits of `batch`, from the stamps alone."""
    own = sorted(key for key in stamps if key.startswith(f"{batch}/"))
    return sorted(own, key=lambda key: stamps[key]).index(f"{batch}/{name}")


@pytest.mark.parametrize(
    "defect",
    [
        "no stamps",
        "empty stamps",
        "a twin batch lacks one stamp",
        "a base batch lacks one stamp",
        "a base circuit lacks its stamp",
        "a stamp is null",
        "two jobs of a twin batch share a stamp",
    ],
)
def test_an_unusable_order_fails_closed_and_decides_nothing(contrasts_of: Any, defect: str) -> None:
    stamps: dict[str, Any] | None = _stamped()
    twin_batch = f"batch-{TWIN_BATCHES[0]:02d}"
    if defect == "no stamps":
        stamps = None
    elif defect == "empty stamps":
        stamps = {}
    elif defect == "a twin batch lacks one stamp":
        del stamps[f"{twin_batch}/readout-0.cq"]  # type: ignore[union-attr]
    elif defect == "a base batch lacks one stamp":
        del stamps["batch-00/readout-0.cq"]  # type: ignore[union-attr]
    elif defect == "a base circuit lacks its stamp":
        del stamps["batch-00/b0.cq"]  # type: ignore[union-attr]
    elif defect == "a stamp is null":
        stamps[f"{twin_batch}/readout-1.cq"] = None  # type: ignore[index]
    else:
        stamps[f"{twin_batch}/{oc.twin_file('b0', 0)}"] = stamps[f"{twin_batch}/readout-0.cq"]  # type: ignore[index]
    record = contrasts_of(stamps, truth_stamps=_stamped())
    decision = record["decision"]
    _expect(decision["label"] == "unresolved_order" and decision["decided"] is False, f"{defect}: {decision}")
    _expect("label_if_order_ignored" in decision and record["executed_order_fit"]["status"] == "unusable", defect)
    _expect(bc.order_gate({}) is None, "an empty mapping read as an intact order")


def test_a_series_whose_templates_keep_one_offset_is_confounded(contrasts_of: Any) -> None:
    # Every twin batch executed with the coin-0 twin first: each template then has the one offset +1 and no drift is
    # separable from the contrasts.
    layout = bc.twin_layout()
    stamps = _stamped()
    for batch, (_, c0, c1) in layout.items():
        stamps = _stamps_of(batch, ["readout-0.cq", c0, c1, "readout-1.cq"], stamps)
    record = contrasts_of(stamps, truth_stamps=_stamped())
    _expect(record["decision"]["label"] == "unresolved_order_confounded", f"{record['decision']}")
    _expect(record["decision"]["decided"] is False and record["executed_order_fit"]["status"] == "confounded", "d")


def test_a_template_whose_own_drift_departs_from_the_shared_drift_reads_heterogeneity(contrasts_of: Any) -> None:
    common = contrasts_of(_stamped(), drift=0.01)
    _expect(common["decision"]["label"] != "unresolved_drift_heterogeneity", f"{common['decision']['label']}")
    own = {"b0": 0.01, "k4": 0.06, "k8": 0.01, "k12": 0.01}
    record = contrasts_of(_stamped(), drift=own)
    decision = record["decision"]
    _expect(decision["label"] == "unresolved_drift_heterogeneity" and decision["decided"] is False, f"{decision}")
    _expect("label_if_nothing_withheld" in decision, "the label the rule would have read stays beside it")
    fit = record["executed_order_fit"]
    _expect(abs(fit["template_drift"]["k4"] - 0.06) < 1e-12, f"{fit['template_drift']}")


def test_the_base_level_of_a_hand_computed_fixture() -> None:
    # Three replicates of one template at times 0, 1 and 3 with equal errors 0.002, the level read at time 2. By hand:
    # mean time 4/3, S_tt about the weighted mean 14/9 x ... the slope is 0.023 / 7, the level 0.118 / 7, and the
    # error is 0.002 sqrt(3 / 7) (cost 1 + (2/3)^2 / (14/9) = 9 / 7 over the plain error 0.002 / sqrt(3)).
    rows, fit = eo.level_rows([0.010, 0.014, 0.020], [0.002] * 3, [0.0, 1.0, 3.0], 2.0)
    _expect(abs(fit["slope"] - 0.023 / 7) < 1e-15, f"slope {fit['slope']}")
    _expect(abs(fit["level"] - 0.118 / 7) < 1e-15, f"level {fit['level']}")
    _expect(abs(fit["level_se"] - 0.002 * math.sqrt(3 / 7)) < 1e-15, f"error {fit['level_se']}")
    _expect(abs(fit["cost"] - 9 / 7) < 1e-12, f"cost {fit['cost']}")
    weights = [1.0 / (se * se) for _, se in rows]
    mean = sum(w * v for w, (v, _) in zip(weights, rows, strict=True)) / sum(weights)
    _expect(abs(mean - 0.118 / 7) < 1e-15, f"the pooled rows read {mean}")
    _expect(abs(1.0 / math.sqrt(sum(weights)) - fit["level_se"]) < 1e-15, "the pooled error")


def test_replicates_centered_on_the_reference_time_pool_to_the_plain_pool() -> None:
    values = [0.010, 0.020, 0.015, 0.017]
    rows, fit = eo.level_rows(values, [0.002] * 4, [-3.0, -1.0, 1.0, 3.0], 0.0)
    _expect(abs(fit["level"] - sum(values) / 4) < 1e-12, f"{fit['level']}")
    _expect(abs(fit["cost"] - 1.0) < 1e-12 and all(abs(se - 0.002) < 1e-12 for _, se in rows), f"{fit['cost']}")
    with pytest.raises(eo.ConfoundedOrder):
        eo.level_rows(values, [0.002] * 4, [1.0] * 4, 0.0)


def _seconds_of(stamps: dict[str, str], keys: list[str]) -> list[float]:
    """Start times of `keys` in seconds after the earliest stamp, from the stamps alone."""
    origin = min(datetime.fromisoformat(v).timestamp() for v in stamps.values())
    return [datetime.fromisoformat(stamps[k]).timestamp() - origin for k in keys]


def test_a_base_batch_executed_out_of_order_gets_the_time_weights_of_its_executed_positions(
    contrasts_of: Any,
) -> None:
    # Two b0 base batches ran 20 minutes after their requested slot, one of them with its template circuit last. The
    # data carry a base drift of 1e-4 per second about the twin reference time: the fit at the executed times recovers
    # the level of the series that kept its order, and the plain pool of the base rows is biased by the drift.
    requested = _stamped()
    ids = bc.base_batch_ids()["b0"]
    moved = _stamps_of(ids[2], ["readout-0.cq", "readout-1.cq", "b0.cq"], requested)
    stamps = dict(moved)
    for batch in (ids[0], ids[2]):
        for key in [k for k in moved if k.startswith(f"{batch}/")]:
            stamps[key] = (datetime.fromisoformat(moved[key]) + timedelta(minutes=20)).isoformat()
    kept = contrasts_of(requested, base_slope=1e-4)
    ran = contrasts_of(stamps, base_slope=1e-4)
    keys = [f"{batch}/b0.cq" for batch in ids]
    fit = ran["base_level_fit"]["templates"]["b0"]
    _expect(fit["times"] == _seconds_of(stamps, keys), f"{fit['times']} against the stamps")
    spread = [t - u for t, u in zip(fit["times"], kept["base_level_fit"]["templates"]["b0"]["times"], strict=True)]
    _expect(spread[0] - spread[1] == 1200.0 and spread[2] - spread[3] == 1201.0, f"the executed times {spread}")
    for result in (kept, ran):
        _expect(abs(result["base_level_fit"]["templates"]["b0"]["level"] - BASE_MU) < 1e-9, "the level")
    plain = sum(v for v, _ in ran["batch_contrasts"]["b0"]["base"]) / 4
    _expect(abs(plain - BASE_MU) > 1e-3, f"the plain base pool is not biased: {plain}")
    _expect(ran["decision"]["label"] == kept["decision"]["label"], f"{ran['decision']['label']}")
    # With no base drift the level is the plain pooled value of the series that kept its order.
    still = contrasts_of(requested, base_slope=0.0)
    _expect(abs(still["base_level_fit"]["templates"]["b0"]["level"] - BASE_MU) < 1e-15, "no drift, no shift")


def test_base_replicates_that_share_one_start_time_read_base_drift_confounded(contrasts_of: Any) -> None:
    stamps = _stamped()
    for batch in bc.base_batch_ids()["b0"]:
        stamps[f"{batch}/b0.cq"] = "2026-11-08T01:00:00.500000Z"
    record = contrasts_of(stamps, truth_stamps=_stamped())
    _expect(record["decision"]["label"] == "unresolved_base_drift_confounded", f"{record['decision']['label']}")
    _expect(record["decision"]["decided"] is False and record["base_level_fit"]["status"] == "confounded", "d")


def test_a_reference_series_that_is_not_a_line_reads_drift_model_and_flags_the_calibration(contrasts_of: Any) -> None:
    line = contrasts_of(_stamped(), monitor_slope=0.0)
    _expect(line["drift_monitor"]["adequate"] is True, f"{line['drift_monitor']}")
    _expect(line["decision"]["label"] != "unresolved_drift_model", f"{line['decision']['label']}")
    _expect(not any(r["unresolved_calibration_drift"] for r in line["calibration_drift"]), "a flat series")
    step = contrasts_of(_stamped(), monitor_step=0.05)
    _expect(step["decision"]["label"] == "unresolved_drift_model", f"{step['decision']['label']}")
    _expect(step["decision"]["decided"] is False and step["drift_monitor"]["adequate"] is False, "step")
    steep = contrasts_of(_stamped(), monitor_slope=1e-4)
    _expect(steep["drift_monitor"]["adequate"] is True, "a steep line is still a line")
    _expect(all(r["unresolved_calibration_drift"] for r in steep["calibration_drift"]), f"{steep['calibration_drift']}")
    _expect(len(steep["calibration_drift"]) == 3 and steep["calibration_drift"][0]["sigma_sys"] > 1e-3, "sigma_sys")


def test_the_executed_offset_orders_by_instant_and_refuses_a_tie() -> None:
    stamps = {
        k: bc.stamp_instant(v)
        for k, v in {"a": "2026-11-08T01:00:03Z", "b": "2026-11-08T01:00:01Z", "c": "2026-11-08T01:00:02Z"}.items()
    }
    _expect(eo.executed_offset(stamps, "a", "b") == -2, "a ran third and b first")
    with pytest.raises(eo.ConfoundedOrder):
        eo.executed_offset({**stamps, "c": stamps["a"]}, "a", "b")


# Stamps that cannot order the series ---------------------------------------------------------------------------------


@pytest.fixture(scope="module")
def small_files(built: dict[str, dict[str, str]]) -> dict[str, str]:
    """The Tuna-17 series files with every batch manifest at 256 shots: a complete series of a few thousand strings."""
    files = dict(built[bc.TUNA_SERIES])
    for rel in files:
        if rel.startswith("batch-") and rel.endswith("/cases.json"):
            files[rel] = json.dumps({**json.loads(files[rel]), "shots": 256}, indent=1) + "\n"
    return files


@pytest.fixture(scope="module")
def small_shots(small_files: dict[str, str], manifest: dict[str, Any]) -> dict[str, list[str]]:
    return oc.synthetic_series(small_files, manifest)


@pytest.fixture(scope="module")
def plain_record(small_shots: dict[str, list[str]], manifest: dict[str, Any]) -> dict[str, Any]:
    """The real `evaluate_decision` of the small series, read once: it ranks nothing, so every stamp defect below
    reaches it unchanged and a replay of this record is its result."""
    return bc.evaluate_decision(small_shots, manifest, None)


@pytest.fixture
def replay(monkeypatch: pytest.MonkeyPatch, plain_record: dict[str, Any]) -> None:
    monkeypatch.setattr(bc, "evaluate_decision", lambda shots, manifest, executed=None: copy.deepcopy(plain_record))


def _first_twin_batch_stamps() -> tuple[str, dict[str, str]]:
    return f"batch-{TWIN_BATCHES[0]:02d}", _stamped()


def test_a_valid_series_reads_its_executed_order_through_the_real_decision(
    small_shots: dict[str, list[str]],
    manifest: dict[str, Any],
    plain_record: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    record = bc.evaluate(small_shots, manifest, _stamped())
    _expect(record["executed_order_fit"]["status"] == "fitted", f"{record['executed_order_fit']}")
    _expect(record["decision"]["label"] not in bc.WITHHELD_LABELS, f"{record['decision']['label']}")
    # The plain decision ranks nothing, so it does not depend on the stamps' spelling; the respelled series reads the
    # module's record of it, and the stamp parsing, offsets and executed-order decision run unchanged.
    monkeypatch.setattr(bc, "evaluate_decision", lambda shots, manifest, executed=None: copy.deepcopy(plain_record))
    # The same instants spelled with another offset and fraction width read one series.
    shifted = {
        key: datetime.fromisoformat(value).astimezone(timezone(timedelta(hours=5, minutes=30))).isoformat()
        for key, value in _stamped().items()
    }
    again = bc.evaluate(small_shots, manifest, shifted)
    _expect(again["decision"] == record["decision"], "an offset other than Z changed the decision")
    _expect(again["executed_order_fit"]["offsets"] == record["executed_order_fit"]["offsets"], "offsets")


@pytest.mark.parametrize(
    "defect",
    [
        "a base circuit stamp is null",
        "a twin circuit stamp is null",
        "a calibration circuit stamp is null",
        "a key is absent",
        "a stamp is empty text",
        "a stamp is an integer",
        "a stamp is not ISO 8601",
        "a stamp has no UTC offset",
        "a stamp is a date only",
        "two twin circuits start at one instant in two spellings",
    ],
)
def test_a_stamp_that_cannot_order_the_series_reads_the_registered_label_through_the_real_decision(
    small_shots: dict[str, list[str]], manifest: dict[str, Any], replay: None, defect: str
) -> None:
    twin, stamps = _first_twin_batch_stamps()
    coin0 = f"{twin}/{oc.twin_file('b0', 0)}"
    if defect == "a base circuit stamp is null":
        stamps["batch-00/b0.cq"] = None  # type: ignore[assignment]
    elif defect == "a twin circuit stamp is null":
        stamps[coin0] = None  # type: ignore[assignment]
    elif defect == "a calibration circuit stamp is null":
        stamps["batch-32/joint-011.cq"] = None  # type: ignore[assignment]
    elif defect == "a key is absent":
        del stamps[coin0]
    elif defect == "a stamp is empty text":
        stamps[coin0] = ""
    elif defect == "a stamp is an integer":
        stamps[coin0] = 1794794714  # type: ignore[assignment]
    elif defect == "a stamp is not ISO 8601":
        stamps[coin0] = "yesterday at noon"
    elif defect == "a stamp has no UTC offset":
        stamps[coin0] = "2026-11-08T01:01:05.000000"
    elif defect == "a stamp is a date only":
        stamps[coin0] = "2026-11-08"
    else:
        stamps[coin0] = "2026-11-08T01:01:07Z"
        stamps[f"{twin}/{oc.twin_file('b0', 1)}"] = "2026-11-08T01:01:07.000000+00:00"
    record = bc.evaluate(small_shots, manifest, stamps)
    decision = record["decision"]
    _expect(decision["label"] == "unresolved_order" and decision["decided"] is False, f"{defect}: {decision['label']}")
    _expect(decision["label"] in bc.OUTCOMES and decision["outcome"] == bc.OUTCOMES[decision["label"]][0], "text")
    _expect(record["executed_order_fit"]["status"] == "unusable", f"{record['executed_order_fit']}")
    _expect(decision["label_if_order_ignored"] == record["order_ignored_label"], "the plain label stays beside it")
    _expect(not (record["order_gate"] or {"intact": False})["intact"], "the strict reading read it as intact")


@pytest.mark.parametrize("how", ["null", "absent"])
def test_a_collected_job_without_its_start_stamp_reads_unresolved_order(
    tmp_path: Path, small_files: dict[str, str], small_shots: dict[str, list[str]], how: str
) -> None:
    root = tmp_path / how
    dirs = _runs(root, bc.TUNA_SERIES, small_files, small_shots)
    results = dirs[1] / "results.json"
    record = json.loads(results.read_text(encoding="utf-8"))
    if how == "null":
        record["jobs"][0]["job"]["queued_at"] = None
    else:
        del record["jobs"][0]["job"]["queued_at"]
    results.write_text(json.dumps(record), encoding="utf-8")
    scored = bc.analyze(dirs, root / "cases")
    decision = scored["decision"]
    _expect(decision["label"] == "unresolved_order" and decision["decided"] is False, f"{how}: {decision['label']}")
    _expect(scored["executed_order_fit"]["status"] == "unusable", f"{how}: {scored['executed_order_fit']}")


def test_start_stamps_rank_by_instant_and_not_by_text() -> None:
    # 38 s past the minute with no fraction and with a fraction: the text of the fractionless stamp sorts later ('Z'
    # above '.') although it is the earlier instant.
    early, late = "2026-11-08T01:01:38Z", "2026-11-08T01:01:38.500000Z"
    _expect(early > late, "the premise: text order and time order differ")
    _expect(bc.stamp_instant(early) < bc.stamp_instant(late), "instant order")
    _expect(bc.stamp_instant(early) == bc.stamp_instant("2026-11-08T01:01:38.000000+00:00"), "one instant")
    _expect(bc.stamp_instant("2026-11-08T03:01:38+02:00") == bc.stamp_instant(early), "an offset")
    _expect(bc.stamp_instant("2026-11-08T01:23:38.076340Z") % 1_000_000 == 76340, "microseconds are kept")
    stamps = _stamped()
    twin = f"batch-{TWIN_BATCHES[0]:02d}"
    stamps[f"{twin}/{oc.twin_file('b0', 1)}"] = early
    stamps[f"{twin}/{oc.twin_file('b0', 0)}"] = late
    stamps[f"{twin}/readout-0.cq"] = "2026-11-08T01:01:30Z"
    stamps[f"{twin}/readout-1.cq"] = "2026-11-08T01:01:39Z"
    _expect(bc.twin_offsets(stamps)[twin] == -1, "the coin-1 twin ran first at instants")


@pytest.mark.parametrize("stamp", [None, "", 7, "noon", "2026-11-08", "2026-11-08T01:01:38", "2026-13-40T99:00:00Z"])
def test_an_unusable_stamp_is_refused_by_name(stamp: Any) -> None:
    with pytest.raises(bc.UnusableOrder):
        bc.stamp_instant(stamp)


def _fine_stamps(reversed_batch: str | None = None) -> tuple[dict[str, str], dict[str, str]]:
    """Canonical and mixed-spelling start stamps of one series. Job p of batch n starts p x 50 ms into minute n, so the
    jobs of a batch fall within one second; a batch named by `reversed_batch` runs its jobs in the reverse order. The
    spelled stamps write p = 0 without a fraction ('...:00Z', which sorts after '...:00.05Z' as text), p % 3 == 1 with
    its trailing zeros trimmed, p % 3 == 2 with a +00:00 offset and the others with six digits and Z."""
    canonical: dict[str, str] = {}
    spelled: dict[str, str] = {}
    for row in bc.batch_rows(bc.TUNA_SERIES):
        files = [circuit["file"] for circuit in row["circuits"]]
        ran = files[::-1] if row["batch"] == reversed_batch else files
        minute = int(row["batch"][-2:])
        for p, name in enumerate(ran):
            head, micros = f"2026-11-08T01:{minute:02d}:00", p * 50_000
            key = f"{row['batch']}/{name}"
            canonical[key] = f"{head}.{micros:06d}Z"
            if p == 0:
                spelled[key] = f"{head}Z"
            elif p % 3 == 1:
                spelled[key] = f"{head}.{micros:06d}".rstrip("0") + "Z"
            elif p % 3 == 2:
                spelled[key] = f"{head}.{micros:06d}+00:00"
            else:
                spelled[key] = canonical[key]
    return canonical, spelled


@pytest.mark.parametrize("reversed_batch", [None, f"batch-{TWIN_BATCHES[0]:02d}"])
def test_mixed_stamp_spellings_rank_by_instant_in_every_path_that_reads_the_order(
    small_shots: dict[str, list[str]], manifest: dict[str, Any], reversed_batch: str | None
) -> None:
    canonical, spelled = _fine_stamps(reversed_batch)
    twin = f"batch-{TWIN_BATCHES[0]:02d}"
    files = [
        circuit["file"] for circuit in next(r for r in bc.batch_rows(bc.TUNA_SERIES) if r["batch"] == twin)["circuits"]
    ]
    by_text = sorted(files, key=lambda name: spelled[f"{twin}/{name}"])
    by_instant = sorted(files, key=lambda name: canonical[f"{twin}/{name}"])
    _expect(by_text != by_instant, "the premise: the text order of the spelled stamps differs from the instant order")
    _expect(bc.twin_offsets(spelled) == bc.twin_offsets(canonical), "twin offsets")
    _expect(bc.circuit_seconds(spelled) == bc.circuit_seconds(canonical), "seconds")
    gate, plain = bc.order_gate(spelled), bc.order_gate(canonical)
    if gate is None:
        raise AssertionError("the strict gate read no stamps")
    _expect(gate == plain, "the strict gate")
    _expect(gate["batches"][twin]["executed"] == by_instant, "the strict gate ran the batch in text order")
    _expect(gate["intact"] is (reversed_batch is None), f"intact {gate['intact']}")
    got, want = bc.evaluate(small_shots, manifest, spelled), bc.evaluate(small_shots, manifest, canonical)
    _expect(got["decision"] == want["decision"], "the decision")
    _expect(got["executed_order_fit"] == want["executed_order_fit"], "the executed-order fit")
    _expect(got["order_ignored_label"] == want["order_ignored_label"], "the pool that ignores the order")
    _expect(got["order_gate"] == want["order_gate"], "the record of the strict gate")


def test_circuits_of_a_twin_batch_that_start_at_one_instant_withhold_the_decision_and_one_microsecond_apart_rank(
    small_shots: dict[str, list[str]], manifest: dict[str, Any]
) -> None:
    twin = f"batch-{TWIN_BATCHES[0]:02d}"
    coin0, coin1 = f"{twin}/{oc.twin_file('b0', 0)}", f"{twin}/{oc.twin_file('b0', 1)}"
    stamps = _stamped()
    stamps[coin1] = stamps[coin0]
    tied = bc.evaluate(small_shots, manifest, stamps)
    _expect(tied["decision"]["label"] == "unresolved_order", f"{tied['decision']['label']}")
    _expect("one instant" in tied["executed_order_fit"]["reason"], f"{tied['executed_order_fit']}")
    stamps[coin1] = stamps[coin0].replace(".000000Z", ".000001Z")
    apart = bc.evaluate(small_shots, manifest, stamps)
    _expect(apart["decision"]["label"] != "unresolved_order", f"{apart['decision']['label']}")
    _expect(apart["executed_order_fit"]["status"] != "unusable", f"{apart['executed_order_fit']}")
    _expect(bc.stamp_instant(stamps[coin1]) - bc.stamp_instant(stamps[coin0]) == 1, "one microsecond")


def test_a_stamp_outside_the_series_layout_is_ignored_and_a_missing_layout_stamp_is_not() -> None:
    stamps = _stamped()
    extra = {**stamps, "batch-99/b0.cq": None, "batch-00/other.cq": "not a stamp"}
    _expect(
        bc.twin_offsets(extra) == bc.twin_offsets(stamps), "a key that no circuit of the series owns changed a read"
    )
    _expect(bc.circuit_seconds(extra) == bc.circuit_seconds(stamps), "seconds")
    del extra["batch-00/b0.cq"]
    with pytest.raises(bc.UnusableOrder):
        bc.circuit_seconds(extra)


def test_two_stamps_of_one_instant_in_a_base_batch_order_nothing_and_decide_nothing_wrong() -> None:
    # Only a twin batch ranks its circuits, so a tie elsewhere is a reading of the strict gate and no unresolved label.
    stamps = _stamped()
    stamps["batch-00/b0.cq"] = stamps["batch-00/readout-0.cq"]
    bc.twin_offsets(stamps)
    gate = bc.order_gate(stamps)
    _expect(gate is not None and gate["batches"]["batch-00"]["intact"] is False, "the strict reading counts the tie")


# Pairing of batches and contrasts, the reference series and the calibration reads -------------------------------------


def test_each_twin_and_base_row_is_paired_with_the_batch_that_the_layout_lists_literally() -> None:
    # Batches 0..7 are the forward round (b0 base, b0 twin, k4 twin, k4 base, k8 base, k8 twin, k12 twin, k12 base),
    # batches 8..15 its mirror reversed, 16..23 and 24..31 repeat them. The twin rows of a template are listed in
    # batch order; each carries a value that follows its own batch's executed offset, so a pairing that left the batch
    # order would recover no contrast.
    literal = {
        "b0": ["batch-01", "batch-14", "batch-17", "batch-30"],
        "k4": ["batch-02", "batch-13", "batch-18", "batch-29"],
        "k8": ["batch-05", "batch-10", "batch-21", "batch-26"],
        "k12": ["batch-06", "batch-09", "batch-22", "batch-25"],
    }
    offsets = {
        "batch-01": 1, "batch-14": -3, "batch-17": 1, "batch-30": -1,
        "batch-02": 1, "batch-13": -1, "batch-18": 1, "batch-29": -1,
        "batch-05": -1, "batch-10": 1, "batch-21": -1, "batch-26": 1,
        "batch-06": 1, "batch-09": -1, "batch-22": 3, "batch-25": -1,
    }  # fmt: skip
    truth = {"b0": 0.0164, "k4": 0.001, "k8": -0.002, "k12": 0.0}
    contrasts = {
        t: {
            "base": [(0.0164, 0.004)] * 4,
            "twin": [(truth[t] + 0.01 * offsets[b], 0.0055) for b in literal[t]],
        }
        for t in truth
    }
    _expect(bc.twin_batch_ids(contrasts) == literal, f"{bc.twin_batch_ids(contrasts)}")
    rows, fitted = bc.executed_twin_fit(contrasts, offsets)
    for template, value in truth.items():
        _expect(abs(fitted["contrast"][template] - value) < 1e-12, f"{template}: {fitted['contrast'][template]}")
        _expect(all(abs(v - value) < 1e-12 for v, _ in rows[template]["twin"]), f"{template}: {rows[template]['twin']}")
    _expect(abs(fitted["drift"] - 0.01) < 1e-12, f"{fitted['drift']}")
    _expect(
        bc.base_batch_ids()
        == {
            "b0": ["batch-00", "batch-15", "batch-16", "batch-31"],
            "k4": ["batch-03", "batch-12", "batch-19", "batch-28"],
            "k8": ["batch-04", "batch-11", "batch-20", "batch-27"],
            "k12": ["batch-07", "batch-08", "batch-23", "batch-24"],
        },
        f"{bc.base_batch_ids()}",
    )


def _bracket_shots(n: int = 1000) -> dict[str, list[str]]:
    """Readout shots of the 32 base and twin batches: batch b has 10 + b of $n readout-0 shots read 1 (e01) and 20 + 2 b
    of readout-1 shots read 0 (e10), so its offset is c_b = (10 + b) / 2000."""
    shots: dict[str, list[str]] = {}
    for b in range(32):
        shots[f"batch-{b:02d}/readout-0.cq"] = _shots(n - (10 + b), n)
        shots[f"batch-{b:02d}/readout-1.cq"] = _shots(20 + 2 * b, n)
    return shots


def test_the_reference_series_places_each_batch_offset_at_the_mean_start_of_its_two_readouts() -> None:
    manifest = {"templates": {t: {"roles": {"selector": 2}} for t in oc.TEMPLATES}}
    seconds = {}
    for b in range(32):
        seconds[f"batch-{b:02d}/readout-0.cq"] = 100.0 * b
        seconds[f"batch-{b:02d}/readout-1.cq"] = 100.0 * b + 30.0
    times, values, ses = bc.bracket_series(_bracket_shots(), manifest, seconds)
    _expect(times == [100.0 * b + 15.0 for b in range(32)], f"{times}")
    _expect(all(abs(v - (10 + b) / 2000) < 1e-15 for b, v in enumerate(values)), f"{values}")
    e01, e10 = 12 / 1000, 24 / 1000  # batch 2
    _expect(abs(ses[2] - math.sqrt((e01 * (1 - e01) + e10 * (1 - e10)) / 1000 / 4)) < 1e-15, f"{ses[2]}")


def test_the_calibration_reads_carry_the_largest_selector_error_and_the_mean_start_of_each_batch() -> None:
    # Prepared selector value of each X-only circuit: the middle digit of its name.
    prepared = {
        "batch-32": {"joint-011.cq": 1, "joint-111.cq": 1, "joint-000.cq": 0},
        "batch-33": {"joint-010.cq": 1, "joint-110.cq": 1, "joint-001.cq": 0},
        "batch-34": {"joint-100.cq": 0, "joint-101.cq": 0},
    }
    n = 1000
    rates = [0.01, 0.03, 0.02]
    shots: dict[str, list[str]] = {}
    seconds: dict[str, float] = {}
    for batch, circuits in prepared.items():
        for k, (name, value) in enumerate(circuits.items()):
            wrong = round(rates[k] * n)
            read = _selector_string(1 - value)
            shots[f"{batch}/{name}"] = [read] * wrong + [_selector_string(value)] * (n - wrong)
            seconds[f"{batch}/{name}"] = 1000.0 * int(batch[-2:]) + 10.0 * k
    manifest = {"joint_qubits": {"selector": 2}}
    got = bc.calibration_readings(shots, manifest, seconds)
    _expect([r["batch"] for r in got] == ["batch-32", "batch-33", "batch-34"], f"{got}")
    for reading, batch in zip(got, prepared, strict=True):
        k = len(prepared[batch])
        top = max(rates[:k])
        _expect(abs(reading["se"] - math.sqrt(top * (1 - top) / n)) < 1e-15, f"{batch}: {reading['se']}")
        _expect(abs(reading["time"] - (1000.0 * int(batch[-2:]) + 10.0 * (k - 1) / 2)) < 1e-12, f"{batch}: {reading}")


def test_every_withheld_label_after_the_first_is_listed_beside_it(contrasts_of: Any) -> None:
    # One series that is base-confounded (the b0 replicates share a start), whose reference series is a step and whose
    # k4 template drifts on its own: three withholdings, read in the registered order.
    stamps = _stamped()
    for batch in bc.base_batch_ids()["b0"]:
        stamps[f"{batch}/b0.cq"] = "2026-11-08T01:00:00.500000Z"
    record = contrasts_of(
        stamps,
        truth_stamps=_stamped(),
        drift={"b0": 0.01, "k4": 0.06, "k8": 0.01, "k12": 0.01},
        monitor_step=0.05,
    )
    decision = record["decision"]
    _expect(decision["label"] == "unresolved_base_drift_confounded", f"{decision['label']}")
    _expect(
        decision["also_withheld"] == ["unresolved_drift_model", "unresolved_drift_heterogeneity"],
        f"{decision['also_withheld']}",
    )
    _expect("label_if_nothing_withheld" in decision and decision["decided"] is False, f"{decision}")
    _expect(set([decision["label"], *decision["also_withheld"]]) <= set(bc.WITHHELD_LABELS), "unregistered label")


def _hand_rows(base: dict[str, float], twin: dict[str, float]) -> dict[str, dict[str, list[tuple[float, float]]]]:
    return {
        t: {
            "base": [(base.get(t, 0.0), 0.004 if t != "b0" else 0.002)] * 4,
            "twin": [(twin.get(t, 0.0), 0.004)] * 4,
        }
        for t in oc.TEMPLATES
    }


def _diagonal(rows: dict[str, dict[str, list[tuple[float, float]]]]) -> dict[str, dict[str, float]]:
    errors = {t: ana.pooled(rows[t]["twin"])[1] for t in oc.TEMPLATES}
    return {a: {b: errors[a] ** 2 if a == b else 0.0 for b in oc.TEMPLATES} for a in oc.TEMPLATES}


@pytest.mark.parametrize(
    ("base", "twin"),
    [
        ({"b0": 0.0164}, {"b0": 0.0166}),
        ({"b0": 0.0164}, {"b0": 0.0}),
        ({"b0": 0.0164}, {"b0": -0.0164}),
        ({"b0": 0.0164, "k4": 0.01, "k8": 0.01, "k12": 0.01}, {"b0": 0.0164, "k4": 0.01, "k8": 0.01, "k12": 0.01}),
        ({"b0": 0.0164}, {"b0": 0.0164, "k4": 0.02}),
        ({}, {}),
        ({"b0": 0.0164, "k4": 0.01}, {"b0": 0.0164, "k4": 0.01}),
    ],
)
def test_a_diagonal_twin_covariance_gives_the_decision_of_rule_v2(
    base: dict[str, float], twin: dict[str, float]
) -> None:
    rows = _hand_rows(base, twin)
    plain = bc.decide_estimates(rows)
    got = bc.decide_correlated(rows, _diagonal(rows))
    _expect(got["label"] == plain["label"] and got["decided"] == plain["decided"], f"{got['label']} {plain['label']}")
    for key in ("s_b0", "t_b0", "c_six_cz_base", "d_six_cz_twin", "m_six_cz", "r_b0", "r_minus_m"):
        _expect(
            all(
                math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-15)
                for a, b in zip(got["numbers"][key], plain["numbers"][key], strict=True)
            ),
            f"{key}: {got['numbers'][key]} against {plain['numbers'][key]}",
        )
    for kind in ("base", "twin"):
        _expect(
            math.isclose(
                got["numbers"]["block_chi2"][kind], plain["numbers"]["block_chi2"][kind], rel_tol=1e-9, abs_tol=1e-12
            ),
            f"block {kind}",
        )


def test_a_shared_drift_covariance_widens_the_pooled_error_and_narrows_the_difference_error_by_hand() -> None:
    # Three 6-CZ twin contrasts of error s with pairwise correlation rho: the equal-weight pool has variance
    # s^2 (1 + 2 rho) / 3. b0 shares covariance q with each of them, so cov(t0, d) = q.
    rho = 0.5
    rows = _hand_rows({"b0": 0.0164}, {"b0": 0.0164})
    pooled_se = {t: ana.pooled(rows[t]["twin"])[1] for t in oc.TEMPLATES}  # 0.004 / 2 at four replicates
    q = 0.3 * pooled_se["b0"] ** 2
    cov = {
        a: {
            b: pooled_se[a] ** 2 if a == b else (q if "b0" in (a, b) else rho * pooled_se[a] * pooled_se[b])
            for b in oc.TEMPLATES
        }
        for a in oc.TEMPLATES
    }
    s = pooled_se["k4"]
    got = bc.decide_correlated(rows, cov)["numbers"]
    _expect(abs(got["d_six_cz_twin"][1] - s * math.sqrt((1 + 2 * rho) / 3)) < 1e-15, f"{got['d_six_cz_twin']}")
    # r - m = (1 - a) s0 + a t0 - (1 - b) c - b d, a and b the inverse-variance weights of t0 and d in their pairs.
    base_se = ana.pooled(rows["k4"]["base"])[1]
    c_se = base_se / math.sqrt(3)
    d_se = got["d_six_cz_twin"][1]
    s0_se, t0_se = ana.pooled(rows["b0"]["base"])[1], pooled_se["b0"]
    a = (1 / t0_se**2) / (1 / s0_se**2 + 1 / t0_se**2)
    b = (1 / d_se**2) / (1 / c_se**2 + 1 / d_se**2)
    variance = (1 - a) ** 2 * s0_se**2 + a**2 * t0_se**2 + (1 - b) ** 2 * c_se**2 + b**2 * d_se**2
    variance -= 2 * a * b * q
    _expect(abs(got["r_minus_m"][1] - math.sqrt(variance)) < 1e-15, f"{got['r_minus_m']} against {math.sqrt(variance)}")
    independent = bc.decide_correlated(rows, _diagonal(rows))["numbers"]
    _expect(got["d_six_cz_twin"][1] > independent["d_six_cz_twin"][1], "a positive correlation widens the pool")
    _expect(got["r_minus_m"][1] < math.hypot(got["r_b0"][1], got["m_six_cz"][1]), "and narrows the difference")


def test_the_covariance_of_the_template_contrasts_is_the_weighted_least_squares_covariance() -> None:
    rows = {
        "b0": [(0.0, 0.003, -3.0), (0.0, 0.004, 1.0), (0.0, 0.005, -1.0), (0.0, 0.003, 1.0)],
        "k4": [(0.0, 0.004, 1.0), (0.0, 0.003, -1.0), (0.0, 0.006, 1.0), (0.0, 0.004, -3.0)],
        "k8": [(0.0, 0.004, -1.0), (0.0, 0.003, -1.0), (0.0, 0.006, 1.0), (0.0, 0.004, 1.0)],
    }
    fitted = eo.fit(rows)
    # The independent derivation: the weighted least squares of v on one indicator per template and x has the
    # covariance (X' W X)^-1, whose template block is the covariance of t_T and t_U and whose last entry is var(g).
    names = list(rows)
    design, weights = [], []
    for k, name in enumerate(names):
        for _, se, x in rows[name]:
            design.append([1.0 if j == k else 0.0 for j in range(len(names))] + [x])
            weights.append(1.0 / se**2)
    x_matrix = np.array(design)
    covariance = np.linalg.inv(x_matrix.T @ np.diag(weights) @ x_matrix)
    for i, a in enumerate(names):
        for j, b in enumerate(names):
            got = fitted["covariance"][a][b]  # type: ignore[index]
            _expect(abs(got - covariance[i, j]) < 1e-15, f"{a},{b}: {got} against {covariance[i, j]}")
    _expect(abs(fitted["drift_se"] ** 2 - covariance[-1, -1]) < 1e-15, "var(g)")  # type: ignore[operator]


def test_one_template_that_alone_varies_its_offset_departs_from_nothing() -> None:
    # Its own drift and the shared drift are one quantity; the two weighted sums differ by rounding of about 1e-18, and
    # the error of the difference is zero, so a comparison with no floor reads a departure there (measured on 652 of
    # 1,970 random series that vary one template: own - shared = 1.7e-18 against an error of 0).
    for pattern in itertools.product((-3, -1, 1, 3), repeat=4):
        if len(set(pattern)) == 1:
            continue
        for ses in ((0.003, 0.004, 0.005, 0.006), (0.0075, 0.0031, 0.0052, 0.0045), (0.0055,) * 4):
            offsets = {"k4": [1] * 4, "k8": [-1] * 4, "k12": [1] * 4, "b0": list(pattern)}
            rows = {
                t: [(0.01 * s + (0.0164 if t == "b0" else 0.0), ses[i], float(s)) for i, s in enumerate(v)]
                for t, v in offsets.items()
            }
            fitted = eo.fit(rows)
            _expect(bc.stray_templates(fitted) == [], f"{pattern} {ses}: {bc.stray_templates(fitted)}")
    # A real departure still reads: b0's own drift 0.06 against 0.01 in the others. The shared drift is their weighted
    # mean, 0.0275, so every template departs from it by more than three errors of the difference.
    rows = {
        "b0": [(0.06 * s, 0.0055, float(s)) for s in (1, -1, 1, -1)],
        "k4": [(0.01 * s, 0.0055, float(s)) for s in (1, -1, 1, -1)],
        "k8": [(0.01 * s, 0.0055, float(s)) for s in (1, -1, 1, -1)],
        "k12": [(0.01 * s, 0.0055, float(s)) for s in (1, -1, 1, -1)],
    }
    _expect(bc.stray_templates(eo.fit(rows)) == ["b0", "k4", "k8", "k12"], f"{bc.stray_templates(eo.fit(rows))}")
