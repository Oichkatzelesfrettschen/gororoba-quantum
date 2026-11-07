"""Score synthetic returns of the Ascella two-coset-block case against its preregistered thresholds."""

from __future__ import annotations

import copy
import json
import math
from collections.abc import Callable
from functools import cache
from pathlib import Path
from typing import Any

import ascella_pathion_coset_block_pairs_analysis as analysis
import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
CASE = ROOT / "results/quandela/cases/ascella_pathion_coset_block_pairs/job-00/cases.json"
SAMPLES = 131072
BRIGHT = 0.5

Model = Callable[[int, dict[str, Any]], np.ndarray]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


@cache
def frozen() -> str:
    return CASE.read_text(encoding="utf-8")


def manifest() -> dict[str, Any]:
    loaded: dict[str, Any] = json.loads(frozen())
    return loaded


def split(total: int, weights: np.ndarray) -> list[int]:
    """Deterministic integer split of total by weights; the largest part takes the rounding remainder."""
    parts = [round(total * float(w) / float(weights.sum())) for w in weights]
    parts[int(np.argmax(weights))] += total - sum(parts)
    return parts


def returned(setting: dict[str, Any], weights: np.ndarray, sentinel: float = 0.0) -> dict[str, Any]:
    """One returned iteration whose labeled-mode click probabilities are the weights (modes 0..8)."""
    off = round(sentinel * SAMPLES)
    modes = split(SAMPLES - off, weights) + split(off, np.ones(3))
    counts = {}
    for mode, count in enumerate(modes):
        if count:
            counts[",".join("1" if i == mode else "0" for i in range(12))] = count
    return {
        "counts": counts,
        "iteration": {"compilation_seed": setting["compilation_seed"], "circuit_params": setting["circuit_params"]},
        "samples": SAMPLES,
        "result_fields": {"nb_shots_used": SAMPLES},
    }


def weights_for(
    setting: dict[str, Any],
    shifts: dict[str, float] | None = None,
    eta: np.ndarray | None = None,
    leak: float = 0.0,
) -> np.ndarray:
    """The ideal label law with slot levels shifted, per-mode efficiencies applied and a uniform leak mixed in."""
    law = np.array(setting["ideal_label_law"][:9], dtype=float)
    out = law.copy()
    for slot, modes in (("A", slice(0, 4)), ("B", slice(4, 8))):
        shift = (shifts or {}).get(slot, 0.0)
        if shift == 0.0:
            continue
        mass = float(law[modes].sum())
        shape = law[modes] / mass if mass > 1e-12 else np.full(4, 0.25)
        out[modes] = shape * max(mass + shift / 2, 0.0)
    out[8] = max(1.0 - float(out[:8].sum()), 0.0)
    if eta is not None:
        out = out * eta
    out = out / out.sum()
    return (1 - leak) * out + leak * np.full(9, 1 / 9)


def run(
    model: Callable[[int, dict[str, Any]], np.ndarray] | None = None, sentinel: Callable[[int], float] | None = None
) -> list[dict[str, Any]]:
    chosen = model or (lambda index, setting: weights_for(setting))
    return [
        returned(setting, chosen(index, setting), 0.0 if sentinel is None else sentinel(index))
        for index, setting in enumerate(manifest()["settings"])
    ]


def shifted(rule: Callable[[int, dict[str, Any], str], float]) -> Model:
    """Model whose slot levels move by rule(index, setting, slot)."""

    def model(index: int, setting: dict[str, Any]) -> np.ndarray:
        return weights_for(setting, {slot: rule(index, setting, slot) for slot in ("A", "B")})

    return model


def status(result: dict[str, Any], name: str) -> str:
    found: str = next(c["status"] for c in result["admission"]["conditions"] if c["condition"] == name)
    return found


def verdicts(result: dict[str, Any]) -> tuple[str, ...]:
    return (
        result["admission"]["verdict"],
        result["conformance"]["verdict"],
        result["mutation"]["verdict"],
        result["crosstalk"]["verdict"],
        result["independence"]["verdict"],
    )


PASSING = ("admitted", "pass", "pass", "pass", "pass")


def item_shift(setting: dict[str, Any], slot: str, block: str, arm: str, amount: float) -> float:
    item = setting["slots"][slot]
    return amount if setting["role"] == "sign" and item["block"] == block and item["arm"] == arm else 0.0


def c8_pattern(setting: dict[str, Any], slot: str, by_slot: bool) -> float:
    """The predecessor's C8 spread on T items: block 7 high, blocks 4 to 6 low, optionally reversed in slot B."""
    item = setting["slots"][slot]
    if setting["role"] != "sign" or not item["block"].startswith("C8/") or item["arm"] != "T":
        return 0.0
    high = item["block"] == "C8/7"
    if by_slot and slot == "B":
        high = not high
    return 0.0227 if high else -0.0243


def test_layout_matches_the_frozen_sequence() -> None:
    structure = analysis.layout(manifest())
    require(manifest()["iterations"] == 52 and len(structure["by_setting"]) == 25, "iteration or setting count")
    require(structure["by_setting"]["anchor"] == {0: [0, 51], 1: [1, 50]}, f"{structure['by_setting']['anchor']}")
    require(structure["by_setting"]["dark"] == {0: [2, 49]}, f"{structure['by_setting']['dark']}")
    broken = copy.deepcopy(manifest())
    broken["settings"][5], broken["settings"][6] = broken["settings"][6], broken["settings"][5]
    with pytest.raises(ValueError):
        analysis.layout(broken)


def test_ideal_returns_pass_every_decision_and_reproduce_every_ideal_level() -> None:
    result = analysis.score(manifest(), run())
    require(verdicts(result) == PASSING, f"verdicts {verdicts(result)}")
    require(result["admission"]["unevaluated"] == [], "an ideal run leaves a condition unevaluated")
    require(result["c8_spread"]["verdict"] == "not reproduced", f"spread {result['c8_spread']['verdict']}")
    for reading in result["readings"]:
        require(abs(reading["l_hat"] - reading["ideal"]) < 2e-4, f"{reading['setting']} {reading['arm']}")
        require(abs(reading["a_prime"] - reading["ideal"]) < 2e-4, f"{reading['setting']} a_prime")
    for slot in ("A", "B"):
        require(math.isclose(result["calibration"]["efficiency"][slot], 1.0, abs_tol=1e-3), "efficiency")
    require(all(row["label_law_distance"] < 1e-3 for row in result["iterations"]), "label law distance")
    require(len(result["readings"]) == 46, f"{len(result['readings'])} readings")
    require(result["conformance"]["t_within"] == result["conformance"]["t_expected"] == 16, "T readings")
    require(result["mutation"]["readings_present"] == 17, "eight C and nine N readings")
    require(
        result["crosstalk"]["readings_present"] == 8, "crosstalk readings: four anchor and four D-setting iterations"
    )
    json.dumps(result, allow_nan=False)


def test_uniform_contraction_leaves_normalized_levels_and_the_calibrated_level() -> None:
    result = analysis.score(manifest(), run(lambda i, s: weights_for(s, leak=0.04)))
    require(verdicts(result) == PASSING, f"verdicts {verdicts(result)}")
    for reading in result["readings"]:
        require(abs(reading["a_prime"] - reading["ideal"]) < 2e-4, f"{reading['setting']} a_prime {reading['a_prime']}")
        require(abs(reading["l_hat"] - reading["ideal"]) < 0.01, f"{reading['setting']} l_hat {reading['l_hat']}")
    require(abs(result["calibration"]["dark"]["A"] - 0.04 * 4 / 9) < 1e-4, "dark share")


def test_branch_efficiency_is_calibrated_per_slot_from_its_anchor() -> None:
    eta = np.array([1.08] * 4 + [1.04] * 4 + [1.0])
    result = analysis.score(manifest(), run(lambda i, s: weights_for(s, eta=eta)))
    require(verdicts(result) == PASSING, f"verdicts {verdicts(result)}")
    efficiency = result["calibration"]["efficiency"]
    require(math.isclose(efficiency["A"], 1.08, rel_tol=2e-3), f"slot A efficiency {efficiency['A']}")
    require(math.isclose(efficiency["B"], 1.04, rel_tol=2e-3), f"slot B efficiency {efficiency['B']}")
    for reading in result["readings"]:
        require(abs(reading["l_hat"] - reading["ideal"]) < 1e-3, f"{reading['setting']} l_hat {reading['l_hat']}")
    top = next(r for r in result["readings"] if r["setting"] == "c-d-TT" and r["item"] == 0)
    require(abs(top["a_prime"] - top["ideal"]) > 0.005, "the anchor-normalized level keeps the denominator coupling")
    group = result["independence"]["groups"]["independence-b12"]
    require(group["range"] < 1e-3 < group["uncalibrated_range"], f"independence ranges {group}")


def test_a_leaky_ideal_device_passes_the_differential_crosstalk_null() -> None:
    result = analysis.score(manifest(), run(lambda i, s: weights_for(s, leak=0.004), lambda i: 0.002))
    require(verdicts(result) == PASSING, f"verdicts {verdicts(result)}")
    require(max(abs(c["excess_over_dark"]) for c in result["crosstalk"]["rows"]) < 1e-3, "excess over the slot's dark")


def test_crosstalk_into_the_kernel_slot_fails_the_crosstalk_decision_alone() -> None:
    def leak(index: int, setting: dict[str, Any], slot: str) -> float:
        item, partner = setting["slots"][slot], setting["slots"]["B" if slot == "A" else "A"]
        return 0.08 if item["arm"] == "D" and partner["ideal_level"] >= BRIGHT else 0.0

    result = analysis.score(manifest(), run(shifted(leak)))
    require(verdicts(result) == ("admitted", "pass", "pass", "fail", "pass"), f"verdicts {verdicts(result)}")
    require(result["crosstalk"]["max_excess"] > 0.07, f"excess {result['crosstalk']['max_excess']}")
    require(all(not c["within_sentinel_scale"] for c in result["crosstalk"]["rows"]), "sentinel-scale flag")


def test_partner_arm_dependence_of_the_fixed_block_fails_independence() -> None:
    def moved(index: int, setting: dict[str, Any], slot: str) -> float:
        item = setting["slots"][slot]
        partner = setting["slots"]["B" if slot == "A" else "A"]
        if setting["group"] == "independence-b12" and item["arm"] == "T" and partner["arm"] == "N":
            return -0.09
        return 0.0

    result = analysis.score(manifest(), run(shifted(moved)))
    require(result["independence"]["verdict"] == "fail", f"verdicts {verdicts(result)}")
    require(result["independence"]["groups"]["independence-c8"]["exceeds"] is False, "the other group is clean")
    require(result["admission"]["verdict"] == "admitted", "independence is a separate decision")


def test_a_spread_that_travels_with_the_block_is_attributed_to_the_block() -> None:
    result = analysis.score(manifest(), run(shifted(lambda i, s, slot: c8_pattern(s, slot, by_slot=False))))
    spread = result["c8_spread"]
    require(spread["verdict"] == "follows the block", f"spread {spread['verdict']}")
    require(spread["slots_reproducing"] == ["A", "B"], f"slots {spread['slots_reproducing']}")
    for slot in ("A", "B"):
        require(math.isclose(spread["contrast"][slot]["contrast"], 0.047, abs_tol=2e-4), f"contrast {spread}")
    require(verdicts(result) == PASSING, "a 0.024 spread conforms at 0.07")
    require(
        all(p["keeps_sign"] for p in result["same_class_pair_differences"] if p["setting"] == "i-f-TT"), "pair sign"
    )


def test_a_spread_that_travels_with_the_slot_is_attributed_to_the_slot() -> None:
    result = analysis.score(manifest(), run(shifted(lambda i, s, slot: c8_pattern(s, slot, by_slot=True))))
    spread = result["c8_spread"]
    require(spread["verdict"] == "follows the mode slot", f"spread {spread['verdict']}")
    require(spread["slots_reproducing"] == ["A"] and spread["slots_reversed"] == ["B"], f"slots {spread}")
    pair = next(p for p in result["same_class_pair_differences"] if p["setting"] == "i-f-TT")
    require(pair["keeps_sign"] is False, f"the block 7 minus block 4 difference must flip: {pair}")


def test_a_per_mode_efficiency_pattern_is_recovered_by_the_mode_fit() -> None:
    eta = np.array([1.0, 1.0, 1.0, 1.0, 1.06, 0.97, 1.02, 0.95, 1.0])
    result = analysis.score(manifest(), run(lambda i, s: weights_for(s, eta=eta)))
    fit = np.array(result["mode_efficiency"])
    expected = eta / np.exp(np.mean(np.log(eta)))
    require(float(np.max(np.abs(fit - expected))) < 5e-3, f"fit {fit}")


def test_one_flipped_block_fails_conformance_and_names_the_outliers() -> None:
    def flipped(index: int, setting: dict[str, Any], slot: str) -> float:
        return item_shift(setting, slot, "B12/7", "T", -0.5)

    result = analysis.score(manifest(), run(shifted(flipped)))
    require(verdicts(result)[:2] == ("admitted", "fail"), f"verdicts {verdicts(result)}")
    require(result["conformance"]["outliers"] == [("e-b-TT", "B12/7", "T")], f"{result['conformance']['outliers']}")
    require(result["conformance"]["t_within"] == 15, "fifteen of sixteen T readings remain within")


def test_outlier_allowance_admits_two_f_readings_and_refuses_three() -> None:
    def far(blocks: tuple[str, ...]) -> Model:
        def rule(index: int, setting: dict[str, Any], slot: str) -> float:
            return sum(item_shift(setting, slot, block, "F", 0.12) for block in blocks)

        return shifted(rule)

    two = analysis.score(manifest(), run(far(("B12/2", "C8/7"))))
    require(len(two["conformance"]["outliers"]) == 2 and two["conformance"]["verdict"] == "pass", "two outliers")
    three = analysis.score(manifest(), run(far(("B12/2", "C8/7", "B12/6"))))
    require(len(three["conformance"]["outliers"]) == 3 and three["conformance"]["verdict"] == "fail", "three outliers")


def test_a_mutation_arm_that_reads_the_true_level_fails_the_mutation_decision_only() -> None:
    def true_level(index: int, setting: dict[str, Any], slot: str) -> float:
        item = setting["slots"][slot]
        return item_shift(setting, slot, "B12/2", "N", item["true_top_level"] - item["ideal_level"])

    result = analysis.score(manifest(), run(shifted(true_level)))
    require(verdicts(result)[:3] == ("admitted", "pass", "fail"), f"verdicts {verdicts(result)}")
    require(
        result["mutation"]["failures"] == [("b-i-NN", "B12/2", "N", "follows true level")],
        f"{result['mutation']['failures']}",
    )


def test_anchor_drift_withholds_interpretation_and_keeps_the_readings() -> None:
    def drift(index: int, setting: dict[str, Any], slot: str) -> float:
        return -0.0008 * index * setting["slots"][slot]["ideal_level"]

    result = analysis.score(manifest(), run(shifted(drift)))
    require(status(result, "anchor drift") == "fail", f"drift status {status(result, 'anchor drift')}")
    require(result["admission"]["verdict"] == "instrument not admitted", "verdict")
    require(result["conformance"]["verdict"] == "not interpreted", "conformance")
    require(all("a_prime" in r for r in result["readings"]), "readings are still reported")


def test_a_slot_bias_beyond_the_mirror_spread_fails_admission() -> None:
    def bias(index: int, setting: dict[str, Any], slot: str) -> float:
        return 0.08 if setting["role"] == "sign" and slot == "B" else 0.0

    result = analysis.score(manifest(), run(shifted(bias)))
    require("mirror agreement" in result["admission"]["failed"], f"failed {result['admission']['failed']}")


def test_sentinel_and_null_conditions_fail_on_their_own_thresholds() -> None:
    noisy = analysis.score(manifest(), run(sentinel=lambda index: 0.06 if index == 30 else 0.0))
    require(noisy["admission"]["failed"] == ["sentinel share"], f"failed {noisy['admission']['failed']}")
    quiet = analysis.score(manifest(), run(sentinel=lambda index: 0.0499 if index == 30 else 0.0))
    require(status(quiet, "sentinel share") == "pass", "5 % sentinel share passes")

    def skew(index: int, setting: dict[str, Any], slot: str) -> float:
        return 0.15 if setting["role"] == "null" and setting["slots"][slot]["arm"] == "E0" else 0.0

    result = analysis.score(manifest(), run(shifted(skew)))
    require("null levels" in result["admission"]["failed"], f"failed {result['admission']['failed']}")


def test_a_cut_run_without_the_late_anchors_leaves_drift_unevaluated() -> None:
    entries = run()
    for index in (49, 50, 51):
        entries[index] = {"missing": True}
    result = analysis.score(manifest(), entries)
    require(status(result, "anchor drift") == "unevaluated", "anchor drift")
    require(status(result, "dark drift") == "unevaluated", "dark drift")
    require(result["admission"]["verdict"] == "admitted", "a cut late segment keeps admission")
    midway = run()
    midway[3] = {"missing": True}
    require(analysis.score(manifest(), midway)["conformance"]["verdict"] == "incomplete", "a lost iteration")
    early = run()
    early[0] = {"error": "cut"}
    early[51] = {"error": "cut"}
    with pytest.raises(ValueError, match="early anchor"):
        analysis.score(manifest(), early)


def test_simulator_gate_proceeds_within_one_percent_and_stops_beyond_it() -> None:
    sim = manifest()
    sim["platforms"] = ["sim:ascella"]
    small = shifted(lambda i, s, slot: 0.004 if s["role"] == "sign" and s["slots"][slot]["arm"] == "T" else 0.0)
    go = analysis.score(sim, run(small))
    require(go["simulator_gate"]["verdict"] == "proceed to the QPU job", f"gate {go['simulator_gate']}")
    large = shifted(lambda i, s, slot: item_shift(s, slot, "C8/4", "T", 0.03))
    stop = analysis.score(sim, run(large))
    require(stop["simulator_gate"]["verdict"] == "stop before the QPU job", f"gate {stop['simulator_gate']}")
    cut = run()
    cut[30] = {"missing": True}
    require(analysis.score(sim, cut)["simulator_gate"]["verdict"].startswith("stop"), "a cut simulator run stops")
    require("simulator_gate" not in analysis.score(manifest(), run()), "a QPU run carries no simulator gate")
    require("noiseless" in go["simulator_gate"]["scope"], "the gate states its scope")


def test_a_returned_iteration_must_match_its_request_and_the_case_budget() -> None:
    entries = run()
    entries[5]["iteration"]["compilation_seed"] += 1
    with pytest.raises(ValueError, match="differs from its request"):
        analysis.score(manifest(), entries)
    entries = run()
    entries[6]["result_fields"]["nb_shots_used"] = SAMPLES + 1
    with pytest.raises(ValueError, match="sample or shot count"):
        analysis.score(manifest(), entries)
    with pytest.raises(ValueError, match="one entry per setting"):
        analysis.score(manifest(), run()[:-1])


def test_the_level_error_is_the_delta_method_through_the_calibration_transform() -> None:
    """Slot efficiencies 0.5 and 1, no dark rate, no failure clicks, click shares 1/3 and 2/3 at n = 10000: the level
    is 1 and its conditional error sqrt(1.125 / n), not the 0.01 of the uncalibrated fold variance."""
    n = 10000.0
    row = {"slot": {"A": n / 3, "B": 2 * n / 3}, "failure": 0.0, "total": n}
    calibration = {
        "dark": {"A": 0.0, "B": 0.0},
        "efficiency": {"A": 0.5, "B": 1.0},
        "anchor_raw": {"A": 1.0, "B": 1.0},
    }
    require(math.isclose(analysis.slot_levels(row, calibration)["A"]["l_hat"], 1.0, rel_tol=1e-12), "calibrated level")
    expected = math.sqrt(1.125 / n)
    for slot in ("A", "B"):
        error = analysis.level_standard_error(row, calibration, slot)
        require(math.isclose(error, expected, rel_tol=1e-5), f"slot {slot}: {error} against {expected}")
    require(abs(expected - 0.010607) < 1e-6 and abs(expected - 0.01) > 5e-4, "the example differs from the old error")


def test_the_reported_error_adds_the_dark_and_anchor_counts_and_shares_them_between_orientations() -> None:
    result = analysis.score(manifest(), run(lambda i, s: weights_for(s, leak=0.04)))
    for reading in result["readings"]:
        require(reading["se"] > reading["se_counting"] > 0, f"{reading['setting']}: calibration adds variance")
        for orientation in reading["orientations"].values():
            require(orientation["se"] > orientation["se_counting"] > 0, f"{reading['setting']} orientation")
    for reading in result["readings"]:
        for orientation in reading["orientations"].values():
            row = result["iterations"][orientation["iteration"]]
            conditional = analysis.level_standard_error(row, result["calibration"], orientation["slot"])
            require(
                math.isclose(conditional, orientation["se_counting"], rel_tol=1e-9), "se_counting is the level error"
            )
    pooled = result["readings"][0]
    first, second = pooled["orientations"]["0"], pooled["orientations"]["1"]
    independent = math.sqrt(first["se"] ** 2 + second["se"] ** 2) / 2
    require(not math.isclose(pooled["se"], independent, rel_tol=1e-3), "the two orientations share one calibration")
    json.dumps(result, allow_nan=False)
