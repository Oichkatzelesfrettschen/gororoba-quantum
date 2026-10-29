"""Check normalization, endpoint laws and register order of the independent oracle."""

import itertools
from decimal import Decimal, localcontext

import pytest
from qi_projector_distribution_audit import audit, local_probability, outcome_probability


@pytest.mark.parametrize("angle", [0, 45, 90])
@pytest.mark.parametrize("endpoint", ["x", "z"])
def test_local_law_matches_moments(angle: int, endpoint: str) -> None:
    with localcontext() as context:
        context.prec = 50
        probabilities = {
            bits: local_probability(bits[0], bits[1], bits[2], angle, endpoint)
            for bits in itertools.product((0, 1), repeat=3)
        }
        total = sum(probabilities.values(), Decimal(0))
        herald = sum((value for (_, ancilla, _), value in probabilities.items() if ancilla == 0), Decimal(0))
        joint = sum((value for (data, ancilla, _), value in probabilities.items() if data == ancilla == 0), Decimal(0))
        expected = {0: Decimal("0.5"), 45: Decimal("0.375"), 90: Decimal("0.25")}
        if endpoint == "x":
            expected[0] = Decimal("0.25")
        if any(
            abs(actual - target) > Decimal("1e-45")
            for actual, target in ((total, 1), (herald, Decimal("0.5")), (joint, expected[angle]))
        ):
            raise AssertionError("independent full law differs from the frozen moments")


def test_outcome_order_and_exact_zero() -> None:
    label, probability = outcome_probability(((0, 1, 1) * 3, (0, 0, 0), "z"))
    if label != "110110110" or probability != Decimal("0.125"):
        raise AssertionError("qubit-zero-rightmost serialization differs")
    _, impossible = outcome_probability(((1, 0, 0) + (0, 0, 0) * 2, (0, 0, 0), "z"))
    if impossible != 0:
        raise AssertionError("the mutation cannot flip a data qubit")


def test_retained_shots_have_ideal_support() -> None:
    rows = audit()["circuits"]
    if [row["ideal_support_size"] for row in rows] != [128, 8, 128]:
        raise AssertionError("ideal support sizes differ")
    if any(row["impossible_outcomes"] for row in rows):
        raise AssertionError("retained QX shots contain an impossible ideal outcome")
