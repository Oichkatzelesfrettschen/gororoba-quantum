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
    _expect(len(lines) >= 9, f"self-test ran {len(lines)} checks")


def test_power_function_matches_the_noncentral_t_where_scipy_is_finite() -> None:
    for n, delta in ((6, 0.05), (12, 0.09), (30, 0.04)):
        want = float(stats.nct.sf(stats.t.isf(0.025, n - 1), n - 1, delta * np.sqrt(n) / 0.1))
        want += float(stats.nct.cdf(-stats.t.isf(0.025, n - 1), n - 1, delta * np.sqrt(n) / 0.1))
        _expect(abs(oba.power_at(delta, 0.1, n, 0.05) - want) < 2e-3, f"n={n} delta={delta}")


def test_replica_count_comes_from_the_retained_scatter() -> None:
    path = ROOT / oba.RETAINED_COLLECT
    if not path.is_file():
        pytest.skip(f"{oba.RETAINED_COLLECT} is absent from this checkout")
    record = oba.power_record(json.loads(path.read_text()))
    _expect(record["replicas_needed"] == 14, f"replicas needed {record['replicas_needed']}")
    _expect(record["replicas"] == 15, f"replicas planned {record['replicas']}")
    _expect(record["tests_in_family"] == 14, "family size")
    for name, row in record["operands"].items():
        _expect(row["power_at_n_full_effect"] >= oba.POWER, f"{name}: gap power below {oba.POWER}")
        _expect(row["power_diff_at_n_full_effect"] >= oba.POWER, f"{name}: C power below {oba.POWER}")
        _expect(row["power_at_n_half_effect"] < oba.POWER, f"{name}: the half-effect power claims too much")
    smaller = oba.required_replicas(0.10, 0.08, 0.05 / 14) - 1
    _expect(oba.power_at(0.10, 0.08, smaller, 0.05 / 14) < oba.POWER, "one replica fewer still reaches the power")


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
        result = oba.analyze(oba.synthetic_entry(n, sd, gap, {}, {}, dead=dead))
        _expect(result["regions"]["dead"] == list(dead), f"dead regions {result['regions']['dead']}")
        _expect(result["regions"]["rule_applied"] is applies, f"{len(dead)} of {n} dead: rule {applies} expected")
        _expect(all(("verdict_live_regions" in r) is applies for r in result["readings"]), "live-region reading")


def test_readout_correlation_is_exploratory_and_checks_its_length() -> None:
    n = 12
    entry = oba.synthetic_entry(n, 0.08, {"16:e1pe26": -0.12, "16:e1pe18": 0.12}, {}, {})
    errors = [0.01 + 0.002 * i for i in range(n)]
    result = oba.analyze(entry, errors)
    block = result["exploratory_readout_correlation"]
    _expect("outside the family" in block["status"], "the correlation is not marked exploratory")
    _expect(set(block["operands"]) == {"e1pe26", "e1pe18"}, f"operands {set(block['operands'])}")
    _expect(all(row["n"] == n and -1.0 <= row["pearson_r"] <= 1.0 for row in block["operands"].values()), "values")
    _expect(len(result["tests"]) == oba.FAMILY, "the correlation entered the family")
    with pytest.raises(ValueError, match="readout errors"):
        oba.analyze(entry, errors[:-1])
