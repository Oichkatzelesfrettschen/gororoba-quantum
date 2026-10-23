"""Per-job rounding and execution ceilings bound batching without inventing hardware throughput."""

from __future__ import annotations

import importlib
from decimal import Decimal
from typing import Any

import pytest


def budget() -> Any:
    try:
        return importlib.import_module("provider_job_budget")
    except ModuleNotFoundError:
        pytest.fail("the provider budget calculator is absent")


def test_iqm_charges_compilation_and_rounds_each_job() -> None:
    module = budget()
    charge = module.iqm_credits(Decimal("0.5"), Decimal("0.6"), Decimal("0.6"))
    if charge != Decimal("1.0"):
        raise AssertionError("compilation or per-job rounding disappeared")
    separate = 2 * module.iqm_credits(Decimal("0.5"), Decimal("0.2"), Decimal("0.2"))
    combined = module.iqm_credits(Decimal("0.5"), Decimal("0.4"), Decimal("0.4"))
    if separate != Decimal("1.0") or combined != Decimal("0.5"):
        raise AssertionError("the calculator rounded aggregate rather than individual jobs")


def test_circuit_batches_obey_both_circuit_and_execution_limits() -> None:
    result = budget().circuit_batches(250, 20000, 100, 1200000)
    if result != [60, 60, 60, 60, 10]:
        raise AssertionError("a batch crossed the independent execution ceiling")


def test_an_individual_circuit_cannot_cross_execution_limit() -> None:
    with pytest.raises(ValueError, match="execution"):
        budget().circuit_batches(2, 20000, 100, 19999)


def test_ion_shots_need_rounded_credits_not_the_advertised_per_shot_rate_alone() -> None:
    module = budget()
    if module.oq_credits(100, Decimal("0.18"), Decimal("0.048")) != 5:
        raise AssertionError("the minimum ion job lost its task fee or rounding")
    if module.max_oq_shots(1, Decimal("0.18"), Decimal("0.000255"), 10, 50000) != 3215:
        raise AssertionError("the one-credit Rigetti boundary changed")
    if module.max_oq_shots(1, Decimal("0.18"), Decimal("0.048"), 100, 5000) is not None:
        raise AssertionError("one credit admitted an ion job below its minimum shots")


def test_invalid_budget_inputs_fail_instead_of_inventing_capacity() -> None:
    module = budget()
    with pytest.raises(ValueError):
        module.iqm_credits(Decimal("0.5"), Decimal("NaN"), Decimal("0"))
    with pytest.raises(ValueError):
        module.circuit_batches(10, 0, 100, 10000)
