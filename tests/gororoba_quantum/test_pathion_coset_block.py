"""Contracts of the coset-block restriction of the A_5 kernel map.

Every check is Statevector arithmetic on at most six qubits: the block law equals the module's six-qubit law on the
output coset, the cosets of one subspace tile the 32 outputs and add up to the nullity, the parametrized plus arm
equals the explicit plus oracle, and the cocycle-free block reads the module's cocycle-free law.
"""

from __future__ import annotations

import numpy as np
import pytest

import pathion_coset_block as pcb
import pathion_kernel_map as pkm

BLOCKS = (
    pcb.Block("ba", (1, 18, 1), (19, 2, 12), 1),
    pcb.Block("bb", (1, 26, 1), (27, 2, 9), 0),
    pcb.Block("b0", (1, 17, 1), (16, 1, 2), 0),
    pcb.Block("bc", (1, 24, 1), (25, 3, 8), 1),
    pcb.Block("be", (2, 27, 1), (25, 2, 9), 1),
)
ALIGNED = {"ba": 2, "bb": 2, "b0": 0, "bc": 2, "be": 4}


def _expect(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


@pytest.mark.parametrize("block", BLOCKS, ids=lambda b: b.name)
@pytest.mark.parametrize("plus", [False, True])
@pytest.mark.parametrize("free", [False, True])
def test_block_law_is_the_module_law_on_the_output_coset(block: pcb.Block, plus: bool, free: bool) -> None:
    error = pcb.restriction_error(block, plus, cocycle_free=free)
    _expect(error < 1e-12, f"{block.name}: probability difference {error}")


@pytest.mark.parametrize("block", BLOCKS, ids=lambda b: b.name)
def test_output_contrast_is_the_module_contrast_and_counts_aligned_pairs(block: pcb.Block) -> None:
    _expect(pcb.contrast_restriction_error(block) < 1e-12, f"{block.name}: c(y) departs from the module's c(k)")
    _expect(pcb.aligned_in_block(block) == ALIGNED[block.name], f"{block.name}: aligned pairs")
    plus = pcb.block_law(pcb.block_circuit(block, True))
    minus = pcb.block_law(pcb.block_circuit(block, False))
    _expect(abs(pcb.selector_contrast(plus, minus) - ALIGNED[block.name] / 4) < 1e-12, f"{block.name}: N_b / 4")


@pytest.mark.parametrize("block", BLOCKS, ids=lambda b: b.name)
def test_parametrized_plus_arm_equals_the_explicit_plus_oracle(block: pcb.Block) -> None:
    _expect(0 in pcb.upper_qubits(block), f"{block.name}: data qubit 0 carries m, so it carries bit h")
    _expect(pcb.orientation_error(block) < 1e-12, f"{block.name}: the phase pi does not reproduce the plus oracle")


@pytest.mark.parametrize("block", BLOCKS[:3], ids=lambda b: b.name)
def test_cosets_of_one_subspace_tile_the_map(block: pcb.Block) -> None:
    tiled = pcb.tile(block.operand, block.basis)
    aligned = [int(n) for n in tiled["aligned"]]  # type: ignore[attr-defined]
    _expect(bool(tiled["covers_once"]), f"{block.name}: the output cosets do not cover 32 indices once")
    _expect(sum(aligned) == tiled["nullity"], f"{block.name}: {aligned} against {tiled['nullity']}")
    _expect(float(tiled["contrast_gap"]) < 1e-12, f"{block.name}: concatenated c(y) differs from c(k)")  # type: ignore[arg-type]


def test_cocycle_free_block_reads_the_module_cocycle_free_law() -> None:
    ba, bb, b0 = BLOCKS[0], BLOCKS[1], BLOCKS[2]
    contrast = {}
    for block in (ba, bb, b0):
        plus = pcb.block_law(pcb.block_circuit(block, True, cocycle_free=True))
        minus = pcb.block_law(pcb.block_circuit(block, False, cocycle_free=True))
        contrast[block.name] = pcb.selector_contrast(plus, minus)
    _expect(abs(contrast["ba"] + 1.0) < 1e-12, f"cocycle-free ba contrast {contrast['ba']}")
    _expect(abs(contrast["bb"]) < 1e-12, f"cocycle-free bb contrast {contrast['bb']}")
    _expect(abs(contrast["b0"] - 0.5) < 1e-12, f"cocycle-free b0 contrast {contrast['b0']}")


def test_ba_and_bb_share_a_selector_contrast_and_differ_in_two_bins() -> None:
    laws = {}
    for block in BLOCKS[:2]:
        plus = pcb.block_law(pcb.block_circuit(block, True))
        minus = pcb.block_law(pcb.block_circuit(block, False))
        laws[block.name] = (pcb.selector_contrast(plus, minus), pcb.output_contrast(plus, minus))
    _expect(abs(laws["ba"][0] - laws["bb"][0]) < 1e-12, "the selector contrasts differ")
    differing = np.flatnonzero(np.abs(laws["ba"][1] - laws["bb"][1]) > 0.5)
    _expect(differing.tolist() == [2, 6], f"ba and bb differ in bins {differing.tolist()}")


def test_block_rejects_a_basis_that_does_not_start_with_m() -> None:
    with pytest.raises(ValueError, match="first basis vector"):
        pcb.Block("bad", (1, 18, 1), (2, 19, 12), 1)
    with pytest.raises(ValueError, match="linearly dependent"):
        pcb.Block("bad", (1, 18, 1), (19, 19, 12), 1)


def test_output_labels_are_the_coset_the_select_permutation_reaches() -> None:
    block = BLOCKS[0]
    labels = pcb.output_labels(block)
    _expect(sorted(set(labels)) == sorted(labels) and len(labels) == 8, "output labels repeat")
    _expect(
        sorted(labels) == sorted(block.coset ^ block.operand[0] ^ v for v in pcb.span(block.basis)),
        "output labels are not (k0 XOR i) + V",
    )
    _expect(pkm.DIM == 32, "the module's dimension")
