"""Exact determinant factors retain scalar and orthogonality constraints."""

from fractions import Fraction
from typing import Any

import pytest

import rank_polynomials


@pytest.mark.parametrize(
    "indices,determinant,membership", [((0, 9), 256, False), ((1, 9), 256, False), ((1, 10), 0, True)]
)
def test_membership_controls(indices: tuple[int, int], determinant: int, membership: bool) -> None:
    vector = [int(index in indices) for index in range(16)]
    evaluation = rank_polynomials.evaluate_sedenion_determinant(vector)
    if evaluation.matrix_determinant != determinant or evaluation.factorized_determinant != determinant:
        raise AssertionError(f"determinant factorization misclassified {indices}")
    if evaluation.is_nonzero_zero_divisor is not membership:
        raise AssertionError(f"membership lost the scalar or orthogonality condition for {indices}")


def test_rational_scalar_and_zero() -> None:
    scalar = rank_polynomials.evaluate_sedenion_determinant([Fraction(1, 2)] + [0] * 15)
    if scalar.s != Fraction(1, 4) or scalar.matrix_determinant != Fraction(1, 2**16):
        raise AssertionError("the rational scalar determinant must equal the sixteenth power")
    zero = rank_polynomials.evaluate_sedenion_determinant([0] * 16)
    if zero.matrix_determinant != 0 or zero.is_nonzero_zero_divisor:
        raise AssertionError("the zero vector is singular and lies outside nonzero membership")


@pytest.mark.parametrize("coordinates", [[0] * 8, [0] * 17, [True] + [0] * 15, [1.0] + [0] * 15])
def test_determinant_input_domain(coordinates: Any) -> None:
    with pytest.raises(ValueError):
        rank_polynomials.evaluate_sedenion_determinant(coordinates)
