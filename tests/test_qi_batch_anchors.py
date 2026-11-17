"""Contract for gororoba_quantum/qi_batch_anchors.py on counts that equal their expectation exactly."""

from __future__ import annotations

import math

import pytest

import qi_batch_anchors as anchors


def levels(p: tuple[float, float, float], shots: tuple[int, int, int] = (16384, 8192, 16384)) -> list[anchors.Level]:
    times = (0.0, 100.0, 400.0)
    return [anchors.Level(t, round(q * n), n) for t, q, n in zip(times, p, shots, strict=True)]


def test_equal_levels_have_no_shift_and_no_excess_variance() -> None:
    found = anchors.probe_shift(levels((0.03, 0.03, 0.03)))
    chi = anchors.homogeneity(levels((0.03, 0.03, 0.03)))
    if abs(found["shift"]) > 1e-4 or chi["chi_square"] > 1e-3 or chi["freedom"] != 2:
        raise AssertionError((found, chi))


def test_a_shifted_middle_level_reads_its_shift_against_the_time_interpolation() -> None:
    # The middle job sits a quarter of the way from the first to the last, so the interpolation is 0.03 + 0.25 * 0.04.
    found = anchors.probe_shift(levels((0.03, 0.05, 0.07)))
    if abs(found["weight"] - 0.25) > 1e-12 or abs(found["interpolated"] - 0.04) > 1e-4:
        raise AssertionError(found)
    if abs(found["shift"] - 0.01) > 1e-4 or not found["z"] > 3.0:
        raise AssertionError(found)
    chi = anchors.homogeneity(levels((0.03, 0.05, 0.07)))
    if not chi["p"] < 1e-6:
        raise AssertionError(chi)


def test_the_null_standard_error_matches_the_binomial_variance_of_the_combination() -> None:
    data = levels((0.5, 0.5, 0.5))
    found = anchors.probe_shift(data)
    weight = found["weight"]
    want = math.sqrt(0.25 * (1 / 8192 + (1 - weight) ** 2 / 16384 + weight**2 / 16384))
    if abs(found["se"] - want) > 1e-12:
        raise AssertionError((found["se"], want))


def test_levels_order_by_time_and_a_degenerate_set_is_rejected() -> None:
    data = levels((0.03, 0.05, 0.07))
    if anchors.probe_shift(list(reversed(data))) != anchors.probe_shift(data):
        raise AssertionError("the order of the input changes the shift")
    with pytest.raises(ValueError):
        anchors.probe_shift(data[:2])
    with pytest.raises(ValueError):
        anchors.probe_shift([anchors.Level(5.0, 1, 10), anchors.Level(5.0, 1, 10), anchors.Level(5.0, 1, 10)])


def test_an_all_zero_count_gives_zero_statistics_instead_of_a_division_error() -> None:
    zero = [anchors.Level(t, 0, 1000) for t in (0.0, 1.0, 2.0)]
    found = anchors.probe_shift(zero)
    if found["z"] != 0.0 or anchors.homogeneity(zero)["chi_square"] != 0.0:
        raise AssertionError(found)
