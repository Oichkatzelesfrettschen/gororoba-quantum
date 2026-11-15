"""Contracts of the click visibility of Perceval's source model and its inversion."""

from __future__ import annotations

import pytest

import quandela_source_model as model

# Perceval 1.3.1, computed (issue 888): the click visibility of each (M, g2) pair.
PAIRS = [
    (0.8728, 0.020, 0.8537),
    (0.911, 0.020, 0.8915),
    (0.825, 0.009, 0.8167),
    (0.9438, 0.00732, 0.9366),
]


def _expect(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


@pytest.mark.parametrize("overlap", [0.0, 0.5, 0.8728, 1.0])
def test_without_multiphoton_emission_the_click_visibility_is_the_overlap(overlap: float) -> None:
    # Two photons of overlap M on a balanced beam splitter coincide with probability (1 - M) / 2, so V = M.
    seen = model.click_visibility(overlap, 0.0)
    _expect(abs(seen - overlap) < 1e-12, f"g2 = 0 gives V = {seen} for M = {overlap}")


@pytest.mark.parametrize(("overlap", "g2", "visibility"), PAIRS)
def test_multiphoton_emission_lowers_the_click_visibility_below_the_overlap(
    overlap: float, g2: float, visibility: float
) -> None:
    seen = model.click_visibility(overlap, g2)
    _expect(abs(seen - visibility) < 5e-5, f"V({overlap}, {g2}) = {seen}, computed {visibility}")
    _expect(0.005 < overlap - seen < 0.025, f"the offset {overlap - seen} is not of the order of g2 {g2}")


@pytest.mark.parametrize(("overlap", "g2", "visibility"), PAIRS)
def test_the_inversion_returns_the_overlap_that_simulates_the_stated_visibility(
    overlap: float, g2: float, visibility: float
) -> None:
    solved = model.overlap_for_click_visibility(model.click_visibility(overlap, g2), g2)
    _expect(abs(solved - overlap) < 1e-9, f"the inversion of V({overlap}, {g2}) returned {solved}")
    stated = model.overlap_for_click_visibility(visibility, g2)
    _expect(abs(model.click_visibility(stated, g2) - visibility) < 1e-9, f"M = {stated} does not simulate {visibility}")
    _expect(stated > visibility, f"the overlap {stated} for a stated visibility {visibility} must exceed it")


def test_a_visibility_outside_the_reachable_range_and_a_bad_g2_are_refused() -> None:
    ceiling = model.click_visibility(1.0, 0.02)
    with pytest.raises(ValueError, match="outside"):
        model.overlap_for_click_visibility(ceiling + 1e-3, 0.02)
    with pytest.raises(ValueError, match="g2"):
        model.click_visibility(0.9, 1.0)
    with pytest.raises(ValueError, match="overlap"):
        model.click_visibility(1.1, 0.0)
