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
