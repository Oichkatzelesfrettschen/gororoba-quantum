"""Exact paired randomization counts retain ties and reject unsafe arithmetic."""

from __future__ import annotations

import importlib
from fractions import Fraction
from typing import Any

import pytest


def analysis() -> Any:
    try:
        return importlib.import_module("packed_pauli_analysis")
    except ModuleNotFoundError:
        pytest.fail("the paired randomization analysis is absent")


def test_all_four_same_sign_differences_have_two_extreme_assignments() -> None:
    if analysis().paired_pvalue([2, 2, 2, 2]) != Fraction(1, 8):
        raise AssertionError("the exact test lost a tail or changed its assignment denominator")


def test_zero_observed_difference_keeps_all_assignments() -> None:
    if analysis().paired_pvalue([1, -1]) != 1 or analysis().paired_pvalue([0, 0]) != 1:
        raise AssertionError("randomization ties were discarded")


def test_mixed_sign_differences_keep_the_exact_tail_mass() -> None:
    if analysis().paired_pvalue([1, 1, 1, -1]) != Fraction(5, 8):
        raise AssertionError("the batched signed sum changed its exact mixed-sign tail")


def test_sixteen_pairs_have_the_declared_exact_resolution() -> None:
    if analysis().paired_pvalue([1] * 16) != Fraction(1, 32768):
        raise AssertionError("the sixteen-pair assignment denominator changed")


def test_nonintegral_or_overflowing_statistics_are_rejected() -> None:
    with pytest.raises(ValueError):
        analysis().paired_pvalue([1.5, 2])
    with pytest.raises(ValueError):
        analysis().paired_pvalue([2**63, 1])
