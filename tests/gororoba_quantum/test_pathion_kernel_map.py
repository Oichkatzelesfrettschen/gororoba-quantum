"""Contracts of the pair-resolved kernel map of two-term operands of A_5.

Every ideal law comes from Statevector on the six-qubit circuit; the tests check it against the closed forms of
pathion_kernel_map (selector marginals (16 -+ N)/32, output contrasts +-1 with half-sum N), the nullity against the
aligned-pair count, the mutations against their departures, and the summary against its ideal ratios.
"""

from __future__ import annotations

import numpy as np
import pytest

import pathion_kernel_map as pkm
from experiments import standalone_campaign_groups


def _expect(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


NULLITIES = {(1, 17, 1): 0, (1, 26, 1): 4, (2, 27, 1): 4, (1, 10, 1): 8, (1, 18, 1): 12, (1, 24, 1): 12}


@pytest.mark.parametrize("operand", [*pkm.OPERANDS, *(twin for twin, _ in pkm.TWINS)])
def test_nullity_is_the_aligned_pair_count(operand: tuple[int, int, int]) -> None:
    n = pkm.nullity(operand)
    _expect(n == pkm.aligned_pairs(operand), f"{operand}: nullity {n} differs from the aligned-pair count")
    if operand in NULLITIES:
        _expect(n == NULLITIES[operand], f"{operand}: nullity {n}, expected {NULLITIES[operand]}")


@pytest.mark.parametrize("operand", pkm.OPERANDS)
def test_selector_and_output_contrasts_follow_the_nullity(operand: tuple[int, int, int]) -> None:
    n = pkm.nullity(operand)
    minus = pkm.ideal_law(pkm.kernel_map_circuit(operand, False))
    plus = pkm.ideal_law(pkm.kernel_map_circuit(operand, True))
    _expect(abs(pkm.selector_zero(minus) - (16 - n) / 32) < 1e-12, f"{operand}: minus marginal")
    _expect(abs(pkm.selector_zero(plus) - (16 + n) / 32) < 1e-12, f"{operand}: plus marginal")
    contrast = pkm.output_contrast(plus, minus)
    _expect(bool(np.allclose(np.abs(contrast), 1.0)), f"{operand}: an output contrast differs from +-1")
    _expect(abs(contrast.sum() / 2 - n) < 1e-9, f"{operand}: half the output-contrast sum differs from N")


@pytest.mark.parametrize(("twin", "primary"), pkm.TWINS)
def test_quarter_turn_twin_reads_its_primary(twin: tuple[int, int, int], primary: tuple[int, int, int]) -> None:
    for plus in (False, True):
        a = pkm.selector_zero(pkm.ideal_law(pkm.kernel_map_circuit(twin, plus)))
        b = pkm.selector_zero(pkm.ideal_law(pkm.kernel_map_circuit(primary, plus)))
        _expect(abs(a - b) < 1e-12, f"twin {twin} reads {a} against {b} for {primary}")
    _expect(not set(twin[:2]) & set(primary[:2]), f"twin {twin} shares a basis element with {primary}")


def test_cocycle_free_select_departs_from_the_nullity() -> None:
    want = {(1, 10, 1): -0.375, (1, 18, 1): -0.125}
    for operand in pkm.COCYCLE_FREE:
        minus = pkm.ideal_law(pkm.kernel_map_circuit(operand, False, cocycle_free=True))
        plus = pkm.ideal_law(pkm.kernel_map_circuit(operand, True, cocycle_free=True))
        contrast = pkm.selector_zero(plus) - pkm.selector_zero(minus)
        _expect(abs(contrast - want[operand]) < 1e-12, f"{operand}: cocycle-free contrast {contrast}")
        _expect(abs(contrast - pkm.nullity(operand) / 16) > 0.5, f"{operand}: the mutation does not move the contrast")


def test_single_sign_flip_moves_the_nullity_by_one() -> None:
    operand, n = pkm.FLIP_OPERAND, pkm.nullity(pkm.FLIP_OPERAND)
    minus = pkm.selector_zero(pkm.ideal_law(pkm.kernel_map_circuit(operand, False, flip_input=pkm.FLIP_INPUT)))
    _expect(abs(abs(minus - (16 - n) / 32) - 1 / 32) < 1e-12, f"flip moves P(minus) by {minus - (16 - n) / 32}")


def test_skeleton_reads_selector_zero() -> None:
    law = pkm.ideal_law(pkm.kernel_map_circuit(pkm.SKELETON_OPERAND, False, skeleton=True))
    _expect(abs(pkm.selector_zero(law) - 1.0) < 1e-12, "the selector-disconnected skeleton leaves s = 1 weight")


def test_group_summary_ideal_ratios_and_registration() -> None:
    group = pkm.pathion_kernel_map_group()
    _expect(group.name in {g.name for g in standalone_campaign_groups()}, "the group is not registered")
    _expect(all(m.circuit.num_qubits == pkm.WIDTH and m.ideal.size == 64 for m in group.members), "member shape")
    summary = group.summarize({m.name: m.ideal for m in group.members})
    _expect(abs(summary["nullity_ratio_12_over_4"] - 3.0) < 1e-12, "ideal 12/4 ratio")
    _expect(abs(summary["nullity_ratio_8_over_4"] - 2.0) < 1e-12, "ideal 8/4 ratio")
    _expect(abs(summary["strut9_ratio_e1e24_over_e2e27"] - 3.0) < 1e-12, "ideal strut-9 ratio")
    _expect(all(abs(summary[k]) < 1e-12 for k in summary if k.startswith("twin_difference")), "twin differences")
    _expect(summary["kmap_e1pe17_contrast"] == pytest.approx(0.0, abs=1e-12), "N = 0 contrast")
    _expect(summary["skeleton_p0"] == pytest.approx(1.0), "skeleton")
    _expect(bool(np.isnan(summary["kmap_e1pe17_contrast_ratio"])), "the N = 0 contrast ratio is undefined")


def test_uniform_contraction_preserves_the_nullity_ratios() -> None:
    group = pkm.pathion_kernel_map_group()
    visibility = 0.3
    noisy = {m.name: visibility * m.ideal + (1 - visibility) / m.ideal.size for m in group.members}
    summary = group.summarize(noisy)
    _expect(abs(summary["nullity_ratio_12_over_4"] - 3.0) < 1e-9, "depolarized 12/4 ratio")
    _expect(abs(summary["kmap_e1pe18_contrast_ratio"] - visibility) < 1e-9, "contrast ratio reads the visibility")
    _expect(summary["kmap_e1pe18_sign_agreement"] == 32.0, "a depolarized device keeps every output sign")
