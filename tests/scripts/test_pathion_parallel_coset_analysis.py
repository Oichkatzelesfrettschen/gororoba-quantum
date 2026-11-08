"""Contracts of the parallel coset-block drain analysis on a synthetic run: ideal laws pushed through placement-specific
asymmetric readout channels (confusion-matrix arithmetic, no sampling), so every rule reads a known answer."""

from __future__ import annotations

import json
from functools import cache

import numpy as np
import pathion_parallel_coset_analysis as analysis

import pathion_parallel_coset as ppc

PLACEMENTS = 3
SHOTS = 16384
GROUP = ppc.pathion_parallel_coset_group()
NAMES = [m.name for m in GROUP.members]
IDEAL = {m.name: np.asarray(m.ideal, dtype=float) for m in GROUP.members}
NULL = analysis.NULL_OPERAND


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def channel(placement: int, scale: float = 1.0) -> tuple[list[float], list[float]]:
    """Per-clbit (P(1 | 0), P(0 | 1)) of one placement; E10 exceeds E01 and both vary by placement and clbit."""
    e01 = [scale * (0.002 + 0.001 * placement + 0.0005 * bit) for bit in range(4)]
    e10 = [scale * (0.012 + 0.004 * placement + 0.002 * bit) for bit in range(4)]
    return e01, e10


def through(law: np.ndarray, lists: tuple[list[float], list[float]]) -> np.ndarray:
    out = np.asarray(law, dtype=float)
    for bit in range(4):
        out = ppc.apply_readout_clbit(out, bit, lists[0][bit], lists[1][bit])
    return out


@cache
def synthetic() -> analysis.Run:
    readout = {name: [channel(k) for k in range(PLACEMENTS)] for name in NAMES}
    dists = {name: [through(IDEAL[name], readout[name][k]) for k in range(PLACEMENTS)] for name in NAMES}
    model = [
        GROUP.summarize({name: through(IDEAL[name], channel(k, 0.9)) for name in NAMES}) for k in range(PLACEMENTS)
    ]
    return analysis.Run(
        directory="synthetic",
        backend="ibm_fez",
        job_id="synthetic",
        shots=SHOTS,
        charge_seconds=None,
        calibration="synthetic",
        members=NAMES,
        ideal=IDEAL,
        dists=dists,
        isolated=dists["cmap_e1pe17_k0_minus"][0].copy(),
        isolated_member="cmap_e1pe17_k0_minus_isolated",
        cz={name: 1 for name in NAMES},
        readout=readout,
        model=model,
        facts={
            "approved_dry_run": "synthetic",
            "model_calibration": "synthetic",
            "ceiling_seconds": 1,
            "operator_excluded_qubits": {},
        },
    )


@cache
def analyzed() -> dict:
    return analysis.analyze([synthetic()])


def test_readout_inversion_per_placement_restores_the_null_operand_and_the_estimator_is_biased_before_it() -> None:
    run = synthetic()
    raw = analysis.summaries(run, run.dists)
    corrected = analysis.summaries(run, analysis.corrected_laws(run))
    for k in analysis.NULL_BLOCKS:
        key = f"{NULL}_k{k}_nullity_estimate"
        flip = f"{NULL}_k{k}_flip_nullity_estimate"
        require(max(abs(v) for v in analysis.column(corrected, key)) < 1e-9, f"corrected k{k} base")
        require(max(abs(v) for v in analysis.column(corrected, flip)) < 1e-9, f"corrected k{k} flip")
    require(min(analysis.column(raw, f"{NULL}_nullity_estimate")) > 0.05, "raw N_hat reads positive under E10 > E01")
    require(min(analysis.column(raw, f"{NULL}_odd_nullity")) > 0.05, "the readout asymmetry lands in the odd part")
    require(max(abs(v) for v in analysis.column(raw, f"{NULL}_even_nullity")) < 0.02, "the even part stays near zero")


def test_readout_only_odd_part_equals_the_measured_odd_part_when_readout_is_the_only_noise() -> None:
    body = analyzed()["backends"]["ibm_fez"]
    per = body["per_placement"]
    require(
        max(abs(a - b) for a, b in zip(per["o_measured"], per["o_readout_only"], strict=True)) < 1e-5,
        "measured O equals the readout-only O of the executed channels",
    )
    drift = body["calibration_drift_check"]["measured_minus_readout_only_odd"]
    require(abs(drift["mean"]) < 1e-5, f"no shortfall against the executed calibration: {drift['mean']}")


def test_synthetic_run_passes_the_rules_it_satisfies() -> None:
    rules = analyzed()["backends"]["ibm_fez"]["rules"]
    for rule_id in ("resolution", "nullity_bands", "four_term_blocks", "parallel_crosstalk", "null_nhat_per_placement"):
        require(rules[rule_id]["verdict"] == "PASS", f"{rule_id}: {rules[rule_id]['verdict']}")
    require(rules["parallel_crosstalk"]["difference"] == 0.0, "packed replica 0 equals the isolated law")
    require(rules["parallel_crosstalk"]["method"] == "newcombe_wilson", "the k0 minus score is a proportion")
    require(
        all(v["integer_nullity"] == round(v["corrected_mean"]) for v in rules["nullity_bands"]["operands"].values()),
        "corrected operand totals round to the integer nullity",
    )
    require(abs(rules["offset_odd"]["measured_mean"]) > 0.05, "the null operand's odd part is the readout offset")


def test_band_verdict_separates_fail_uninformative_and_pass() -> None:
    tight = {"mean": 0.001, "se": 0.0005, "lo": 0.0, "hi": 0.002, "n": 17.0}
    wide = {"mean": 0.001, "se": 0.02, "lo": -0.04, "hi": 0.042, "n": 17.0}
    out = {"mean": 0.05, "se": 0.001, "lo": 0.048, "hi": 0.052, "n": 17.0}
    require(analysis.band_verdict(tight, 0.006, 2.0)["verdict"] == "PASS", "tight mean inside the band")
    require(analysis.band_verdict(wide, 0.006, 2.0)["verdict"] == "UNINFORMATIVE", "inside the band, band unresolved")
    require(analysis.band_verdict(out, 0.006, 2.0)["verdict"] == "FAIL", "mean outside the band")
    two_se = {"mean": 0.004, "se": 0.001, "lo": 0.002, "hi": 0.006, "n": 17.0}
    require(
        analysis.band_verdict(two_se, 0.006, 2.0)["verdict"] == "FAIL", "inside 0.006 but beyond two standard errors"
    )
    require(
        analysis.band_verdict(two_se, 0.006)["verdict"] == "PASS", "the same mean without the standard-error clause"
    )


def rows(contrast: dict[int, float], jitter: float = 0.001) -> list[dict[str, float]]:
    out = []
    for p in range(PLACEMENTS):
        sign = 1.0 if p % 2 == 0 else -1.0
        row = {}
        for k, value in contrast.items():
            row[f"{NULL}_k{k}_selector_contrast"] = value + sign * jitter
            row[f"{NULL}_k{k}_flip_selector_contrast"] = value + sign * jitter
        out.append(row)
    return out


def test_selector_rule_flags_the_sx_overrotation_signature_only_for_k0() -> None:
    signature = analysis.rule_selector(rows({0: 0.012, 4: 0.0, 8: 0.0, 12: 0.0}))
    require(signature["verdict"] == "FAIL" and signature["sx_overrotation_signature"], "k0 above 0.006, 1-CZ at zero")
    every = analysis.rule_selector(rows({0: 0.012, 4: 0.012, 8: 0.012, 12: 0.012}))
    require(not every["sx_overrotation_signature"], "a positive 1-CZ block is not the sx signature")
    quiet = analysis.rule_selector(rows({0: 0.0, 4: 0.0, 8: 0.0, 12: 0.0}))
    require(quiet["verdict"] == "PASS" and not quiet["sx_overrotation_signature"], "all contrasts at zero")


def test_crosstalk_rule_has_three_outcomes() -> None:
    base = synthetic()
    member = "cmap_e1pe17_k0_minus"
    support = IDEAL[member] > 1e-9
    worse = base.dists[member][0].copy()
    moved = 0.05 * float(worse[support].sum())
    worse[support] *= 0.95
    worse[~support] += moved / float((~support).sum())

    def verdict(dists0: np.ndarray, shots: int) -> str:
        dists = dict(base.dists)
        dists[member] = [dists0, *base.dists[member][1:]]
        run = analysis.Run(**{**base.__dict__, "dists": dists, "shots": shots})
        return str(analysis.rule_crosstalk(run)["verdict"])

    require(verdict(base.dists[member][0], SHOTS) == "PASS", "equal scores")
    require(verdict(worse, SHOTS) == "FAIL", "packed score 0.05 below the isolated reference at 16384 shots")
    require(verdict(worse, 200) == "UNINFORMATIVE", "the same gap at 200 shots is unresolved")


def test_student_interval_matches_scipy_and_output_is_deterministic() -> None:
    values = [0.1, 0.25, -0.05, 0.3, 0.12]
    summary = analysis.t_stats(values)
    from scipy import stats

    low, high = stats.t.interval(0.95, len(values) - 1, loc=np.mean(values), scale=stats.sem(values))
    require(abs(summary["lo"] - low) < 1e-12 and abs(summary["hi"] - high) < 1e-12, "Student t over placements")
    first = analysis.rounded({"a": float("nan"), "b": np.float64(1.23456789), "c": [np.int64(3)]})
    require(first == {"a": None, "b": 1.234568, "c": [3]}, f"{first}")
    text = json.dumps(analyzed(), sort_keys=True, allow_nan=False)
    require(text == json.dumps(json.loads(text), sort_keys=True, allow_nan=False), "the record round-trips as JSON")
    require(analyzed()["cross_device"]["verdict"] == "not run", "one backend gives no device rule")
