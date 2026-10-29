"""Exact segment fitting and explicit undefined-response boundaries."""

from fractions import Fraction

import pytest
from qi_tuna_readout_response_mixture import fit_response, joint_tables, rational, replay


def test_known_mixture() -> None:
    result = fit_response([10, 0, 0, 0], [0, 0, 0, 10], [3, 0, 0, 7])
    if result["fitted_segment_coordinate"] != rational(Fraction(7, 10)):
        raise AssertionError("known mixture coordinate changed")
    if result["fitted_residual"]["total_variation"] != rational(Fraction(0)):
        raise AssertionError("exact mixture has residual")
    if result["half_mixture_residual"]["total_variation"] != rational(Fraction(1, 5)):
        raise AssertionError("half mixture residual changed")
    for marginal in result["marginal_affine_weights"].values():
        if marginal["affine_weight_unclipped"] != rational(Fraction(7, 10)):
            raise AssertionError("marginal affine inversion changed")


def test_offsegment_projection_clips() -> None:
    result = fit_response([1, 1, 0, 0], [0, 1, 1, 0], [0, 0, 1, 0])
    if result["unconstrained_segment_coordinate"] != rational(Fraction(3, 2)):
        raise AssertionError("offsegment line projection changed")
    if result["fitted_segment_coordinate"] != rational(Fraction(1)) or not result["clipped_to_segment"]:
        raise AssertionError("upper endpoint clipping failed")
    if result["fitted_residual"]["total_variation"] != rational(Fraction(1, 2)):
        raise AssertionError("offsegment residual changed")
    reverse = fit_response([0, 1, 1, 0], [1, 1, 0, 0], [0, 0, 1, 0])
    if reverse["fitted_segment_coordinate"] != rational(Fraction(0)):
        raise AssertionError("lower endpoint clipping failed")


def test_identical_controls_are_unidentified() -> None:
    result = fit_response([1, 1, 1, 1], [2, 2, 2, 2], [1, 0, 0, 0])
    if (
        result["fitted_segment_coordinate"] is not None
        or result["fit_status"] != "unidentified_identical_control_tables"
    ):
        raise AssertionError("degenerate controls received a fitted coordinate")
    if result["fitted_residual"]["total_variation"] != rational(Fraction(3, 4)):
        raise AssertionError("constant-segment residual changed")
    if any(value["affine_weight_unclipped"] is not None for value in result["marginal_affine_weights"].values()):
        raise AssertionError("zero contrast received an affine weight")


def test_joint_fit_can_exist_with_zero_marginal_contrast() -> None:
    result = fit_response([1, 0, 0, 1], [0, 1, 1, 0], [1, 1, 1, 1])
    if result["fitted_segment_coordinate"] != rational(Fraction(1, 2)):
        raise AssertionError("joint-table direction was lost")
    if any(
        value["status"] != "undefined_zero_control_contrast" for value in result["marginal_affine_weights"].values()
    ):
        raise AssertionError("zero-contrast marginal was identified")


@pytest.mark.parametrize("counts", [[0, 0, 0, 0], [1, -1, 1, 0], [1, 0, 0], [True, 0, 0, 1]])
def test_invalid_counts_rejected(counts: list[int]) -> None:
    with pytest.raises(ValueError, match="joint counts"):
        fit_response(counts, [1, 0, 0, 0], [1, 0, 0, 0])


def test_bit_order_and_all_qubit_tables() -> None:
    shot = ["0"] * 20
    shot[19 - 17] = "1"
    shot[19 - 11] = "1"
    shot[19 - 19] = "1"
    shot[19 - 6] = "1"
    table = joint_tables([["".join(shot)] * 4096] * 3)
    expected = [[0, 0, 4096, 0], [0, 4096, 0, 0], [0, 0, 0, 4096]]
    if table != [expected] * 3:
        raise AssertionError("early/terminal cell or classical bit order changed")


@pytest.mark.parametrize("shot", ["0" * 19, "x" * 20])
def test_malformed_raw_rejected(shot: str) -> None:
    with pytest.raises(ValueError):
        joint_tables([[shot] * 4096] * 3)


def test_retained_response_diagnostic_keeps_failed_qualification() -> None:
    report = replay()
    if report["frozen_qualification_passed"] is not False:
        raise AssertionError("posthoc fit changed the qualification failure")
    if [row["physical_qubit"] for row in report["qubits"]] != [4, 11, 6]:
        raise AssertionError("physical qubits changed")
    for row in report["qubits"]:
        metric = row["fitted_residual"]["total_variation"]
        if Fraction(metric["numerator"], metric["denominator"]) >= Fraction(1, 100):
            raise AssertionError("retained descriptive residual exceeds one percent")
