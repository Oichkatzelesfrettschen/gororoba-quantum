"""Contracts of the click visibility of Perceval's source model and its inversion."""

from __future__ import annotations

import pytest

import quandela_source_model as model

# Perceval 1.3.1, computed (issue 888): the click visibility of each (M, g2) pair, divided by the coincidence of
# distinguishable photons at the same g2 (the dip depth of a Hong-Ou-Mandel scan) and by 0.5 (the issue's figures).
PAIRS = [
    (0.8728, 0.020, 0.8552),
    (0.911, 0.020, 0.8926),
    (0.825, 0.009, 0.8175),
    (0.9438, 0.00732, 0.9369),
]
PAIRS_HALF = [
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
    for reference in model.REFERENCES:
        seen = model.click_visibility(overlap, 0.0, reference)
        _expect(abs(seen - overlap) < 1e-12, f"g2 = 0 gives V = {seen} for M = {overlap} ({reference})")


@pytest.mark.parametrize(("overlap", "g2", "visibility"), PAIRS)
def test_multiphoton_emission_lowers_the_click_visibility_below_the_overlap(
    overlap: float, g2: float, visibility: float
) -> None:
    seen = model.click_visibility(overlap, g2)
    _expect(abs(seen - visibility) < 5e-5, f"V({overlap}, {g2}) = {seen}, computed {visibility}")
    _expect(0.005 < overlap - seen < 0.025, f"the offset {overlap - seen} is not of the order of g2 {g2}")
    half = model.click_visibility(overlap, g2, "half")
    expected = next(v for m, g, v in PAIRS_HALF if (m, g) == (overlap, g2))
    _expect(abs(half - expected) < 5e-5, f"V_half({overlap}, {g2}) = {half}, computed {expected}")
    _expect(half < seen, f"the half normalization {half} must read below the dip depth {seen}")


@pytest.mark.parametrize(("overlap", "g2", "visibility"), PAIRS)
def test_the_inversion_returns_the_overlap_that_simulates_the_stated_visibility(
    overlap: float, g2: float, visibility: float
) -> None:
    solved = model.overlap_for_click_visibility(model.click_visibility(overlap, g2), g2)
    _expect(abs(solved - overlap) < 1e-11, f"the inversion of V({overlap}, {g2}) returned {solved}")
    stated = model.overlap_for_click_visibility(visibility, g2)
    _expect(abs(model.click_visibility(stated, g2) - visibility) < 1e-9, f"M = {stated} does not simulate {visibility}")
    _expect(stated > visibility, f"the overlap {stated} for a stated visibility {visibility} must exceed it")


def test_distinguishable_photons_read_zero_under_the_dip_depth_and_below_zero_under_half() -> None:
    _expect(abs(model.click_visibility(0.0, 0.02)) < 1e-12, "the dip depth of distinguishable photons is not 0")
    _expect(model.click_visibility(0.0, 0.02, "half") < 0, "the half form of distinguishable photons is not negative")
    with pytest.raises(ValueError, match="reference"):
        model.click_visibility(0.5, 0.02, "other")


def test_a_visibility_inside_the_simulator_cutoff_gap_is_refused() -> None:
    # V reads 0.999999 at M = 1 - 1e-6 and exactly 1.0 from about 1 - 5e-7, so no overlap simulates 0.99999999.
    with pytest.raises(ValueError, match="no overlap simulates"):
        model.overlap_for_click_visibility(0.99999999, 0.0)


def test_the_half_normalization_inverts_to_the_overlap_too() -> None:
    overlap, g2, _ = PAIRS_HALF[0]
    seen = model.click_visibility(overlap, g2, "half")
    solved = model.overlap_for_click_visibility(seen, g2, "half")
    _expect(abs(solved - overlap) < 1e-11, f"the half inversion returned {solved}")


def test_the_ceiling_visibility_inverts_to_full_overlap_and_the_floor_to_zero() -> None:
    # The simulator drops probabilities below 1e-6, so V is flat within about 1e-6 of M = 1.
    ceiling = model.overlap_for_click_visibility(model.click_visibility(1.0, 0.02), 0.02)
    _expect(ceiling == 1.0, f"the ceiling inverts to {ceiling}")
    floor = model.overlap_for_click_visibility(model.click_visibility(0.0, 0.02), 0.02)
    _expect(abs(floor) < 1e-11, f"the floor inverts to {floor}")


@pytest.mark.parametrize(("overlap", "g2", "visibility"), PAIRS)
def test_the_two_photon_sector_visibility_is_the_overlap(overlap: float, g2: float, visibility: float) -> None:
    # Conditioned on exactly two photons in the two modes, the multiphoton tails drop out and V = M.
    import perceval as pcvl

    processor = pcvl.Processor("SLOS", pcvl.BS(), noise=pcvl.NoiseModel(indistinguishability=overlap, g2=g2))
    processor.with_input(pcvl.BasicState([1, 1]))
    results = processor.probs()["results"]
    sector = {tuple(state): float(p) for state, p in results.items() if sum(state) == 2}
    mixed = sector[(1, 1)] / sum(sector.values())
    seen = 1.0 - mixed / 0.5
    _expect(abs(seen - overlap) < 1e-12, f"the two-photon sector gives {seen} for M {overlap}")


def test_a_visibility_outside_the_reachable_range_and_a_bad_g2_are_refused() -> None:
    ceiling = model.click_visibility(1.0, 0.02)
    with pytest.raises(ValueError, match="outside"):
        model.overlap_for_click_visibility(ceiling + 1e-3, 0.02)
    with pytest.raises(ValueError, match="g2"):
        model.click_visibility(0.9, 1.0)
    floor = model.click_visibility(0.0, 0.02)
    with pytest.raises(ValueError, match="outside"):
        model.overlap_for_click_visibility(floor - 1e-3, 0.02)
    with pytest.raises(ValueError, match="g2"):
        model.click_visibility(0.9, -0.01)
    with pytest.raises(ValueError, match="overlap"):
        model.click_visibility(1.1, 0.0)
    with pytest.raises(ValueError, match="overlap"):
        model.click_visibility(-0.1, 0.0)
