"""Contracts of the orientation-bit decision rule (docs/evidence/pathion-kernel-map/orientation-bit/).

The rule must reject injected effects and accept nothing from a null run, read the exchange as operand-following or
state-dependent by the sign of the twin's gap, and size its replica count from the retained scatter with an exact
noncentral-t power.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pytest
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
DIRECTORY = ROOT / "docs/evidence/pathion-kernel-map/orientation-bit"
sys.path.insert(0, str(ROOT / "docs/evidence/pathion-kernel-map/nhat-bias"))
sys.path.insert(0, str(DIRECTORY))
SPEC = importlib.util.spec_from_file_location("orientation_bit_analysis", DIRECTORY / "orientation_bit_analysis.py")
if SPEC is None or SPEC.loader is None:
    raise ImportError("orientation_bit_analysis.py is not importable")
oba = importlib.util.module_from_spec(SPEC)
sys.modules["orientation_bit_analysis"] = oba
SPEC.loader.exec_module(oba)


def _expect(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def test_self_test_passes() -> None:
    lines = oba.self_test(None)
    _expect(len(lines) >= 12, f"self-test ran {len(lines)} checks")


def test_power_function_matches_the_noncentral_t_where_scipy_is_finite() -> None:
    for n, delta in ((6, 0.05), (12, 0.09), (30, 0.04)):
        want = float(stats.nct.sf(stats.t.isf(0.025, n - 1), n - 1, delta * np.sqrt(n) / 0.1))
        want += float(stats.nct.cdf(-stats.t.isf(0.025, n - 1), n - 1, delta * np.sqrt(n) / 0.1))
        _expect(abs(oba.power_at(delta, 0.1, n, 0.05) - want) < 2e-3, f"n={n} delta={delta}")


def test_committed_power_record_holds_the_planned_design_and_matches_the_power_function() -> None:
    """power.json is produced by --power from the retained collect (about 15 s, run by the self-test and the
    reproduction line of the design note); this test reads the record and recomputes two of its entries."""
    record = json.loads((DIRECTORY / "power.json").read_text())
    _expect(record["replicas"] == 30 and record["planned_regions"] == 15 and record["jobs"] == 2, "design")
    _expect(record["tests_in_family"] == oba.FAMILY == 16, "family size")
    _expect(record["regions_needed_if_replicas_of_a_region_are_identical"] <= 15, "needed regions exceed the plan")
    alpha = record["alpha_per_test"]
    _expect(abs(alpha - oba.ALPHA / oba.FAMILY) < 1e-12, "alpha per test")
    for name, row in record["operands"].items():
        stats_ = row["statistics"]
        _expect(set(stats_) == set(oba.STATISTICS), f"{name}: statistics {sorted(stats_)}")
        for stat in ("ctrl_g16", "move_g2", "swap_g16"):
            worst, best = stats_[stat]["regions_rho1"], stats_[stat]["regions_rho0"]
            _expect(worst["power_full_effect"] >= oba.POWER, f"{name} {stat}: power below {oba.POWER} at rho 1")
            _expect(best["power_full_effect"] >= worst["power_full_effect"], f"{name} {stat}: rho 0 below rho 1")
            _expect(best["minimum_detectable_effect"] <= worst["minimum_detectable_effect"], f"{name} {stat}: MDE")
            _expect(worst["power_half_effect"] < oba.POWER, f"{name} {stat}: the half-effect power claims too much")
        _expect("power_full_effect" not in stats_["move_leak16"]["regions_rho1"], "leak16 has no retained effect")
        gap = stats_["ctrl_g16"]
        again = oba.power_at(gap["effect"], gap["sd_per_replica"], 15, alpha)
        _expect(abs(again - gap["regions_rho1"]["power_full_effect"]) < 1e-9, f"{name}: power recomputed {again}")
        both = oba._design_sd(gap["sd_per_replica"], 0.0)
        _expect(abs(both - gap["sd_per_replica"] / 2**0.5) < 1e-12, "the two replicas of a region average")
    smaller = oba.required_replicas(0.10, 0.08, 0.05 / 16) - 1
    _expect(oba.power_at(0.10, 0.08, smaller, 0.05 / 16) < oba.POWER, "one replica fewer still reaches the power")


def test_merge_jobs_averages_the_replicas_of_one_region() -> None:
    n = 4
    first = oba.synthetic_entry(n, 0.08, {"16:e1pe26": -0.12, "16:e1pe18": 0.12}, {}, {})
    second = oba.synthetic_entry(n, 0.08, {"16:e1pe26": -0.12, "16:e1pe18": 0.12}, {}, {}, visibility=0.2)
    regions = [[[0, 1], [2, 3], [4, 5], [6, 7]], [[2, 3], [0, 1], [4, 5], [8, 9]]]
    merged, _ = oba.merge_jobs([first, second], regions)
    name = next(iter(first["measured"]))
    _expect(len(merged["measured"][name]) == 5 and sorted(merged["blocks"]) == [1, 1, 2, 2, 2], "blocks")
    want = (np.asarray(first["measured"][name][0]) + np.asarray(second["measured"][name][1])) / 2.0
    _expect(bool(np.allclose(merged["measured"][name][0], want)), "region [0, 1] is not the mean of its two replicas")
    with pytest.raises(ValueError, match="once"):
        oba.merge_jobs([first, second], [[[0, 1], [0, 1], [2, 3], [4, 5]], regions[1]])
    unregioned, _ = oba.merge_jobs([first, second])
    _expect(len(unregioned["measured"][name]) == n and unregioned["blocks"] == [2] * n, "positional blocks")


def test_floor_band_reads_a_model_floor_as_unresolved_and_a_larger_difference_as_a_difference() -> None:
    n, sd = 60, 0.1
    follow = {"16:e1pe26": -0.12, "16:e1pe18": 0.12}
    weak = {"2:e1pe26": -0.03, "2:e1pe18": 0.03}  # C = G16 - G2 = -0.09 and +0.09, G2 below its threshold
    entry = oba.synthetic_entry(n, sd, follow, weak, follow)
    flat = oba.analyze_flat(entry)
    _expect(all(r["ii_gap_stays_on_bit_4"] for r in flat["readings"]), "a floor at zero band was not read as (ii)")
    inside = {
        "e1pe26": {"lower": [-0.12] * n, "upper": [0.0] * n},
        "e1pe18": {"lower": [0.0] * n, "upper": [0.12] * n},
    }
    result = oba.analyze(entry, inside)
    _expect(all(r["verdict"] == "unresolved" for r in result["readings"]), "a floor inside the band was decided")
    _expect(all(not v["reject"] for k, v in result["tests"].items() if k.startswith("diff_cm")), "band rejected")
    narrow = {t: {"lower": [-0.02] * n, "upper": [0.02] * n} for t in inside}
    beyond = oba.analyze(entry, narrow)
    _expect(all(v["reject"] for k, v in beyond["tests"].items() if k.startswith("diff_cm")), "beyond: no reject")
    with pytest.raises(ValueError, match="floor band"):
        oba.analyze(entry, {t: {"lower": [0.0], "upper": [0.0]} for t in inside})


def test_holm_rejects_nothing_above_its_first_threshold() -> None:
    _expect(not any(oba.holm({"a": 0.5 / 12, "b": 0.9}).values()), "a p value above alpha / m was rejected")
    _expect(not oba.holm({"a": 0.049, "b": 0.9})["a"], "a p value of 0.049 in a family of two passes its threshold")


def test_row_rule_reads_supported_only_when_both_operands_do() -> None:
    table = {
        ("supported", "supported"): "supported",
        ("supported", "unresolved"): "unresolved",
        ("unresolved", "unresolved"): "unresolved",
        ("supported", "refuted"): "refuted",
        ("unresolved", "refuted"): "refuted",
        ("refuted", "refuted"): "refuted",
    }
    for verdicts, want in table.items():
        _expect(oba.row_verdict(list(verdicts)) == want, f"{verdicts} read {oba.row_verdict(list(verdicts))}")
    _expect(oba.row_verdict([]) == "unresolved", "an empty row is not supported")


def test_dead_region_rule_needs_more_than_one_third_dead() -> None:
    n, sd = 12, 0.08
    gap = {"16:e1pe26": -0.12, "16:e1pe18": 0.12}
    for dead, applies in (((0, 1, 2, 3), False), ((0, 1, 2, 3, 4), True)):
        result = oba.analyze_flat(oba.synthetic_entry(n, sd, gap, {}, {}, dead=dead))
        _expect(result["regions"]["dead"] == list(dead), f"dead regions {result['regions']['dead']}")
        _expect(result["regions"]["rule_applied"] is applies, f"{len(dead)} of {n} dead: rule {applies} expected")
        _expect(all(("verdict_live_regions" in r) is applies for r in result["readings"]), "live-region reading")


def test_readout_correlation_is_exploratory_and_checks_its_length() -> None:
    n = 12
    entry = oba.synthetic_entry(n, 0.08, {"16:e1pe26": -0.12, "16:e1pe18": 0.12}, {}, {})
    errors = [0.01 + 0.002 * i for i in range(n)]
    result = oba.analyze_flat(entry, errors)
    block = result["exploratory_readout_correlation"]
    _expect("outside the family" in block["status"], "the correlation is not marked exploratory")
    _expect(set(block["operands"]) == {"e1pe26", "e1pe18"}, f"operands {set(block['operands'])}")
    _expect(all(row["n"] == n and -1.0 <= row["pearson_r"] <= 1.0 for row in block["operands"].values()), "values")
    _expect(len(result["tests"]) == oba.FAMILY, "the correlation entered the family")
    with pytest.raises(ValueError, match="readout errors"):
        oba.analyze_flat(entry, errors[:-1])


def test_operating_characteristics_sum_to_one_and_keep_the_null_from_refuting() -> None:
    power = json.loads((DIRECTORY / "power.json").read_text())
    record = json.loads((DIRECTORY / "case_compile.json").read_text())
    result = oba.operating_characteristics(power, record, log2=6)
    _expect(result["trials_per_cell"] == 64, "trials")
    for scenario, by_rho in result["scenarios"].items():
        for rho, rules in by_rho.items():
            for rule, cell in rules.items():
                _expect(abs(sum(cell["row_verdict"].values()) - 1.0) < 1e-9, f"{scenario} {rho} {rule}: row sums")
                for operand in cell["operands"].values():
                    _expect(abs(sum(operand["verdict"].values()) - 1.0) < 1e-9, f"{scenario} {rho} {rule}: operand")
    null = result["scenarios"]["null"]["rho1"]["band_rule"]["row_verdict"]
    _expect(null.get("refuted", 0.0) < 0.1, f"the null run refuted at {null}")


def test_entry_group_reads_the_retained_group_and_its_merged_successor_with_one_ideal_law() -> None:
    retained = oba.entry_group("pathion_kernel_map_orientation")
    merged = oba.entry_group("pathion_kernel_map_orientation_merged")
    _expect([m.name for m in retained.members] == [m.name for m in merged.members], "member names differ")
    for a, b in zip(retained.members, merged.members, strict=True):
        _expect(bool(np.allclose(a.ideal, b.ideal, atol=1e-12)), f"ideal law of {a.name} differs")
    entry = {"group": merged.name, "measured": {m.name: [list(m.ideal)] for m in merged.members}}
    _expect(len(oba.units_from_entry(entry)) == 8, "units of the merged entry")
    with pytest.raises(ValueError, match="not an orientation-bit group"):
        oba.entry_group("pathion_kernel_map")
