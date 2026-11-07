"""Score synthetic returns of the Ascella pathion four-term block case against its preregistered thresholds."""

from __future__ import annotations

import copy
import json
import math
from collections.abc import Callable
from functools import cache
from pathlib import Path
from typing import Any

import ascella_pathion_four_term_blocks_analysis as analysis
import pytest

ROOT = Path(__file__).resolve().parents[2]
CASE = ROOT / "results/quandela/cases/ascella_pathion_four_term_blocks/job-00/cases.json"
SAMPLES = 32768

Model = Callable[[int, dict[str, Any]], float]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


@cache
def frozen() -> str:
    return CASE.read_text(encoding="utf-8")


def manifest() -> dict[str, Any]:
    loaded: dict[str, Any] = json.loads(frozen())
    return loaded


def split(total: int, weights: list[float]) -> list[int]:
    """Deterministic integer split of total by weights (uniform when they vanish); the largest part takes the rest."""
    mass = sum(weights)
    parts = [round(total * w / mass) for w in weights] if mass > 1e-12 else [total // len(weights)] * len(weights)
    parts[max(range(len(parts)), key=lambda i: weights[i] if mass > 1e-12 else 0)] += total - sum(parts)
    return parts


def returned(setting: dict[str, Any], level: float, sentinel: float = 0.0) -> dict[str, Any]:
    """One returned iteration whose success fraction is level and whose sentinel share is sentinel."""
    off = round(sentinel * SAMPLES)
    labeled = SAMPLES - off
    success = round(labeled * level)
    law = setting["ideal_label_law"]
    modes = split(success, law[:4]) + split(labeled - success, law[4:8]) + split(off, [1.0] * 4)
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


def run(model: Model, sentinel: Callable[[int], float] = lambda index: 0.0) -> list[dict[str, Any]]:
    return [
        returned(setting, model(index, setting), sentinel(index))
        for index, setting in enumerate(manifest()["settings"])
    ]


def ideal(index: int, setting: dict[str, Any]) -> float:
    return float(setting["ideal_success"])


def reading(result: dict[str, Any], segment: str, arm: str) -> dict[str, Any]:
    found: dict[str, Any] = next(r for r in result["readings"] if r["segment"] == segment and r["arm"] == arm)
    return found


def status(result: dict[str, Any], name: str) -> str:
    found: str = next(c["status"] for c in result["admission"]["conditions"] if c["condition"] == name)
    return found


def verdicts(result: dict[str, Any]) -> tuple[str, str, str]:
    return result["admission"]["verdict"], result["conformance"]["verdict"], result["mutation"]["verdict"]


def test_frozen_case_has_the_structure_the_scorer_counts() -> None:
    layout = analysis.segment_layout(manifest())
    require(len(layout) == 12 and manifest()["iterations"] == 88, "segment or iteration count")
    require(sum(len(s["arm_indices"]) for s in layout) == 44, "the repeated pairs are not 44")


def test_ideal_returns_pass_every_decision_and_reproduce_every_ideal_level() -> None:
    result = analysis.score(manifest(), run(ideal))
    require(verdicts(result) == ("admitted", "pass", "pass"), f"verdicts {verdicts(result)}")
    require(result["admission"]["unevaluated"] == [], "an ideal run leaves a condition unevaluated")
    require(len(result["readings"]) == 44, "one reading per repeated pair")
    for r in result["readings"]:
        if r["arm"] != "D":
            require(abs(r["a_prime"] - r["ideal"]) < 2e-4, f"{r['segment']} {r['arm']}: {r['a_prime']}")
    require(result["conformance"]["pathion_t_within"] == 8, "pathion T readings")
    require(len(result["conformance"]["outliers"]) == 0, "outliers in an ideal run")
    require(result["mutation"]["readings_present"] == 11, "five C and six N readings")
    require(result["conformance"]["readings_present"] == 18, "eighteen T and F readings")
    require(result["instrument"]["branch_odds_ratio"] is not None, "no branch odds estimate")
    require(math.isclose(result["instrument"]["branch_odds_ratio"], 1.0, abs_tol=1e-3), "odds ratio of an ideal run")
    require(all(row["label_law_distance"] < 1e-3 for row in result["iterations"]), "label law distance")
    json.dumps(result, allow_nan=False)


def test_uniform_contraction_moves_raw_levels_and_leaves_normalized_levels() -> None:
    result = analysis.score(manifest(), run(lambda i, s: 0.04 + 0.88 * s["ideal_success"]))
    require(verdicts(result) == ("admitted", "pass", "pass"), f"verdicts {verdicts(result)}")
    require(abs(result["instrument"]["a_dark"] - 0.04) < 1e-4, "dark level")
    require(abs(result["instrument"]["a_anchor"] - 0.92) < 1e-4, "anchor level")
    top = reading(result, "b12-2", "T")
    require(abs(top["a"] - (0.04 + 0.88 * 0.75)) < 1e-4, "raw level")
    require(abs(top["a_prime"] - 0.75) < 2e-4, f"normalized level {top['a_prime']}")


def test_branch_loss_is_estimated_from_the_null_and_corrected_beside_the_normalized_level() -> None:
    def lossy(index: int, setting: dict[str, Any]) -> float:
        level = float(setting["ideal_success"])
        return 1.07 * level / (1.07 * level + 1 - level)

    result = analysis.score(manifest(), run(lossy))
    require(math.isclose(result["instrument"]["branch_odds_ratio"], 1.07, rel_tol=2e-3), "odds ratio")
    top = reading(result, "c8-4", "T")
    require(top["a_prime"] > top["ideal"] + 0.01, "branch loss does not raise the level")
    require(abs(top["a_prime_odds_corrected"] - top["ideal"]) < 1e-3, "odds correction misses the ideal level")
    require(verdicts(result) == ("admitted", "pass", "pass"), "a 1.07 branch ratio passes at 0.07")


def test_linear_drift_fails_the_anchor_drift_condition_and_withholds_interpretation() -> None:
    result = analysis.score(manifest(), run(lambda i, s: s["ideal_success"] * (1 - 0.0005 * i)))
    require(status(result, "anchor drift") == "fail", f"drift status {status(result, 'anchor drift')}")
    require(result["admission"]["failed"] == ["anchor drift"], f"failed {result['admission']['failed']}")
    require(verdicts(result) == ("instrument not admitted", "not interpreted", "not interpreted"), "verdicts")
    require(all("a_prime" in r for r in result["readings"]), "readings are still reported")


def test_one_flipped_block_fails_conformance_and_names_the_outliers() -> None:
    names = {s["seed_index"]: s["name"] for s in manifest()["segments"]}

    def model(index: int, setting: dict[str, Any]) -> float:
        if setting["arm"] == "T" and names[setting["seed_index"]] == "b12-2":
            return 0.25
        return float(setting["ideal_success"])

    result = analysis.score(manifest(), run(model))
    require(verdicts(result) == ("admitted", "fail", "pass"), f"verdicts {verdicts(result)}")
    require(result["conformance"]["pathion_t_within"] == 7, "seven of eight pathion T readings remain within")
    require(result["conformance"]["outliers"] == [("b12-2", "T")], f"outliers {result['conformance']['outliers']}")


def shifted(arm: str, segments: tuple[str, ...], shift: float) -> Model:
    names = {s["seed_index"]: s["name"] for s in manifest()["segments"]}

    def model(index: int, setting: dict[str, Any]) -> float:
        level = float(setting["ideal_success"])
        if setting["arm"] == arm and names[setting["seed_index"]] in segments:
            return level + shift
        return level

    return model


def test_outlier_allowance_admits_one_f_reading_and_refuses_two() -> None:
    one = analysis.score(manifest(), run(shifted("F", ("c8-4",), 0.10)))
    require(one["conformance"]["outliers"] == [("c8-4", "F")], f"outliers {one['conformance']['outliers']}")
    require(one["conformance"]["verdict"] == "pass", "one outlier within the allowance of 1 must pass")
    two = analysis.score(manifest(), run(shifted("F", ("c8-4", "b12-6"), 0.10)))
    require(len(two["conformance"]["outliers"]) == 2, "two outliers expected")
    require(two["conformance"]["verdict"] == "fail", "two outliers exceed the allowance")


def test_tolerance_edge_separates_a_pass_from_a_fail() -> None:
    inside = analysis.score(manifest(), run(shifted("T", ("c8-5",), 0.069)))
    outside = analysis.score(manifest(), run(shifted("T", ("c8-5",), 0.071)))
    require(inside["conformance"]["verdict"] == "pass", "0.069 lies within 0.07")
    require(outside["conformance"]["verdict"] == "fail", "0.071 lies outside 0.07")


def test_a_mutation_arm_that_reads_the_true_level_fails_the_mutation_decision_only() -> None:
    names = {s["seed_index"]: s["name"] for s in manifest()["segments"]}

    def model(index: int, setting: dict[str, Any]) -> float:
        if setting["arm"] == "N" and names[setting["seed_index"]] == "b12-2":
            return float(setting["true_top_level"])
        return float(setting["ideal_success"])

    result = analysis.score(manifest(), run(model))
    require(verdicts(result) == ("admitted", "pass", "fail"), f"verdicts {verdicts(result)}")
    require(
        result["mutation"]["failures"] == [("b12-2", "N", "follows true level")],
        f"failures {result['mutation']['failures']}",
    )


def test_sentinel_and_null_conditions_fail_on_their_own_thresholds() -> None:
    noisy = analysis.score(manifest(), run(ideal, lambda index: 0.06 if index == 30 else 0.0))
    require(noisy["admission"]["failed"] == ["sentinel share"], f"failed {noisy['admission']['failed']}")
    require(noisy["admission"]["conditions"][4]["value"]["iteration"] == 30, "worst iteration")
    quiet = analysis.score(manifest(), run(ideal, lambda index: 0.05 if index == 30 else 0.0))
    require(status(quiet, "sentinel share") == "pass", "5 % sentinel share passes")
    skew = analysis.score(manifest(), run(shifted("E0", ("null-b12-2",), 0.08)))
    require(skew["admission"]["failed"] == ["null levels"], f"failed {skew['admission']['failed']}")


def test_mesh_spread_within_one_ideal_level_is_reported_beyond_the_tolerance() -> None:
    names = {s["seed_index"]: s["name"] for s in manifest()["segments"]}

    def model(index: int, setting: dict[str, Any]) -> float:
        level = float(setting["ideal_success"])
        if setting["arm"] == "T":
            return level + {"b12-2": 0.04, "b12-6": -0.04}.get(names[setting["seed_index"]], 0.0)
        return level

    result = analysis.score(manifest(), run(model))
    require(result["conformance"]["verdict"] == "pass", "both shifted readings lie within 0.07")
    spread = result["mesh_spread"]["B12"]
    require(spread["exceeds_tolerance"] is True and spread["range"] > 0.07, f"spread {spread}")
    require(spread["attributes_failure_to_mesh_variance"] is True, "0.08 is at least 0.05")
    require(result["mesh_spread"]["C8"]["exceeds_tolerance"] is False, "the C8 blocks agree")
    classes = {c["class"]: c for c in result["classes"]}
    require(len(classes) == 4, f"four D = 32 classes expected, found {sorted(classes)}")
    require(classes["B12 blocks 2, 7"]["segments"] == ["b12-2", "b12-7"], "class membership")
    require(classes["C8 blocks 4 to 7"]["segments"] == ["c8-4", "c8-5", "c8-6", "c8-7"], "class membership")


def test_a_cut_run_without_the_late_anchor_leaves_drift_unevaluated() -> None:
    entries = run(ideal)
    for index in range(84, 88):
        entries[index] = {"missing": True}
    result = analysis.score(manifest(), entries)
    require(status(result, "anchor drift") == "unevaluated", "drift must be unevaluated")
    require(verdicts(result) == ("admitted", "pass", "pass"), f"verdicts {verdicts(result)}")
    require(result["caveats"] == ["unevaluated: anchor drift"], f"caveats {result['caveats']}")
    cut_deeper = run(ideal)
    for index in range(80, 88):
        cut_deeper[index] = {"error": "cut"}
    deeper = analysis.score(manifest(), cut_deeper)
    require(set(deeper["admission"]["unevaluated"]) == {"anchor drift", "null levels"}, "unevaluated set")
    midway = run(ideal)
    midway[79] = {"missing": True}
    partial = analysis.score(manifest(), midway)
    require(partial["conformance"]["verdict"] == "incomplete", "a lost iteration leaves its arm unread")


def test_simulator_gate_proceeds_within_one_percent_and_stops_beyond_it() -> None:
    sim = manifest()
    sim["platforms"] = ["sim:ascella"]
    go = analysis.score(sim, run(lambda i, s: min(1.0, s["ideal_success"] + (0.004 if s["arm"] == "T" else 0.0))))
    require(go["simulator_gate"]["verdict"] == "proceed to the QPU job", f"gate {go['simulator_gate']}")
    stop = analysis.score(sim, run(shifted("T", ("c8-4",), 0.02)))
    require(stop["simulator_gate"]["verdict"] == "stop before the QPU job", f"gate {stop['simulator_gate']}")
    cut = run(ideal)
    cut[87] = {"missing": True}
    require(analysis.score(sim, cut)["simulator_gate"]["verdict"].startswith("stop"), "a cut simulator run stops")
    require("simulator_gate" not in analysis.score(manifest(), run(ideal)), "a QPU run carries no simulator gate")


def test_a_returned_iteration_must_match_its_request_and_the_case_budget() -> None:
    entries = run(ideal)
    entries[5]["iteration"]["compilation_seed"] += 1
    with pytest.raises(ValueError, match="differs from its request"):
        analysis.score(manifest(), entries)
    entries = run(ideal)
    entries[6]["result_fields"]["nb_shots_used"] = SAMPLES + 1
    with pytest.raises(ValueError, match="sample or shot count"):
        analysis.score(manifest(), entries)
    broken = copy.deepcopy(manifest())
    broken["segments"][1]["arms"] = list(reversed(broken["segments"][1]["arms"][:-1])) + ["T"]
    with pytest.raises(ValueError):
        analysis.score(broken, run(ideal))
