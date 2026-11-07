"""Contracts of the wide kernel-map census (docs/evidence/pathion-kernel-map/census.py, ``--wide``).

The census builds the block laws in numpy; they equal the Statevector laws of pathion_coset_block on the D = 32 blocks
the repository already tests, and a two-term block's class (its aligned-pair count) stays within 0..4 at D = 64.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pytest

import pathion_coset_block as pcb

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("pathion_census", ROOT / "docs/evidence/pathion-kernel-map/census.py")
if SPEC is None or SPEC.loader is None:
    raise ImportError("census.py is not importable")
census = importlib.util.module_from_spec(SPEC)
sys.modules["pathion_census"] = census
SPEC.loader.exec_module(census)

OPERANDS = ((1, 17, 1), (1, 18, 1), (2, 27, 1), (1, 10, 1), (17, 2, -1))


def _expect(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


@pytest.mark.parametrize("operand", OPERANDS)
@pytest.mark.parametrize("plus", [False, True])
def test_numpy_block_law_is_the_statevector_law(operand: tuple[int, int, int], plus: bool) -> None:
    basis = pcb.default_basis(operand)
    _expect(basis == census.default_basis(32, operand[0] ^ operand[1]), "default bases differ")
    for k0 in pcb.cosets(basis):
        reference = pcb.block_law(pcb.block_circuit(pcb.Block("b", operand, basis, k0), plus))
        error = float(np.max(np.abs(reference - census.block_law(32, operand, basis, k0, plus))))
        _expect(error < 1e-12, f"{operand} coset {k0}: law difference {error}")


@pytest.mark.parametrize("operand", [(1, 17, 1), (1, 18, 1), (2, 27, 1), (5, 40, 1), (20, 56, -1)])
def test_two_term_wide_certifies_nullity_and_bounds_block_classes(operand: tuple[int, int, int]) -> None:
    dim = 64
    nullity, aligned, counts, laws = census.two_term_wide((dim, operand))
    _expect(nullity == aligned == sum(counts), f"{operand}: nullity {nullity}, aligned {aligned}, blocks {counts}")
    _expect(len(counts) == dim // 8 and all(0 <= c <= 4 for c in counts), f"{operand}: block counts {counts}")
    _expect(len(laws) == len(counts), f"{operand}: one law key per block")


def test_four_term_blocks_are_pm1_matrices_of_the_known_classes() -> None:
    blocks = census.four_term_blocks_from((16, 1))
    _expect(len(blocks) > 0, "no four-term blocks")
    classes = {census.canonical(block) for block in blocks}
    _expect(1 <= len(classes) <= 12, f"{len(classes)} classes")
    _expect(all(abs(v) == 1 for block in blocks for v in block), "an entry is not +-1")
