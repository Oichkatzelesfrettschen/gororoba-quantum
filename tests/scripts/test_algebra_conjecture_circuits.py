"""Source-derived circuit controls preserve the intended measured observables."""

from __future__ import annotations

import importlib
import importlib.util
from typing import Any

import pytest


def implementation() -> Any:
    if importlib.util.find_spec("algebra_conjecture_circuits") is None:
        raise AssertionError("the circuit case bank is missing")
    return importlib.import_module("algebra_conjecture_circuits")


def test_case_bank_contains_source_derived_and_instrument_controls() -> None:
    module = implementation()
    bank = module.bank()
    if {row["family"] for row in bank} != {"sector", "order", "measurement", "instrument", "dimension"}:
        raise AssertionError("case families are incomplete")
    module.ordered_map(module.check_case, bank, min_items=1)


def test_heralded_filter_accounts_for_failure_without_conditioning_it_away() -> None:
    module = implementation()
    row = next(row for row in module.bank() if row["name"] == "contraction-success-failure")
    checked = module.check_case(row)
    if abs(checked["probabilities"]["00"] - 0.5) > 1e-12 or abs(checked["probabilities"]["11"] - 0.375) > 1e-12:
        raise AssertionError(checked)


def test_repeated_measurement_keeps_each_intermediate_bit() -> None:
    row = next(row for row in implementation().bank() if row["name"] == "measurement-fixed-evolution-4")
    if row["circuit"].num_clbits != 4 or row["circuit"].count_ops().get("measure") != 4:
        raise AssertionError("intermediate outcomes were overwritten")


def test_bank_includes_dephased_fixed_and_unmeasured_reset_controls() -> None:
    module = implementation()
    cases = {row["name"]: row for row in module.bank()}
    controls = (
        "order-dephased",
        "order-fixed-xz",
        "order-fixed-zx",
        "measurement-unmeasured-4",
        "measurement-reset-4",
    )
    for name in controls:
        if name not in cases:
            raise AssertionError(f"missing logical control: {name}")
    module.ordered_map(module.check_case, [cases[name] for name in controls], min_items=1)


def test_nonfinite_expected_law_cannot_pass_the_numerical_tolerance() -> None:
    module = implementation()
    case = next(row for row in module.bank() if row["name"] == "sector-dark")
    case["expected"] = {"0": float("nan"), "1": 1.0}
    with pytest.raises(ValueError, match="finite"):
        module.check_case(case)
