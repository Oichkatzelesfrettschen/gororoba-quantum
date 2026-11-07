"""Contracts of the four-term coset-block circuit: cd_core certificates, the level law, the arm separations and the
shared routing of the parametrized arms. Every check is matrix or Statevector arithmetic on at most four qubits."""

from __future__ import annotations

import numpy as np
import pytest
from qiskit.quantum_info import Statevector

import pathion_four_term_block as pft

CHOSEN = pft.select_blocks()


def _expect(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


@pytest.mark.parametrize("name", sorted(pft.OPERANDS))
def test_every_block_entry_equals_the_cd_core_left_multiplication(name: str) -> None:
    terms = pft.OPERANDS[name]
    probe = pft.FourBlock(name, terms, 0)
    v0 = {0, probe.u[0], probe.u[1], probe.u[0] ^ probe.u[1]}
    reps = sorted({min(c ^ v for v in v0) for c in range(pft.DIM)})
    _expect(len(reps) == 8, f"{name}: {len(reps)} cosets of V0")
    for coset in reps:
        block = pft.FourBlock(name, terms, coset)
        matrix = pft.block_matrix(block)
        _expect(np.array_equal(matrix, pft.core_block_matrix(block)), f"{block.tag}: sign table differs from cd_core")
        _expect(bool(np.all(np.abs(matrix) == 1.0)), f"{block.tag}: an entry is not +-1")


def test_selected_blocks_carry_the_spectra_absent_below_dimension_32() -> None:
    spectra = {tuple(float(abs(x)) for x in np.round(pft.gram_spectrum(pft.block_matrix(b)), 3)) for b in CHOSEN}
    _expect(spectra == set(pft.NEW_AT_32), f"selected spectra {spectra}")
    _expect(len(CHOSEN) == 2, f"{len(CHOSEN)} selected blocks")


@pytest.mark.parametrize("block", CHOSEN, ids=lambda b: b.tag)
def test_circuit_law_matches_the_level_of_every_arm(block: pft.FourBlock) -> None:
    for arm, (psi, table) in pft.arm_inputs(block).items():
        if psi is None:
            continue
        matrix = pft.block_matrix(block, None if table is None else np.asarray(table))
        circuit = pft.template(block, table).assign_parameters(pft.binding(psi))
        distribution = pft.law(circuit)
        _expect(abs(pft.selector_zero(distribution) - pft.level(matrix, psi)) < 1e-12, f"{block.tag} {arm}: level")
        bins = np.asarray(matrix @ psi) ** 2 / 16.0
        _expect(float(np.abs(distribution[:4] - bins).max()) < 1e-12, f"{block.tag} {arm}: output bins")


@pytest.mark.parametrize("block", CHOSEN, ids=lambda b: b.tag)
def test_mutation_test_separates_the_bright_arm_and_the_null_arms_hold(block: pft.FourBlock) -> None:
    levels = pft.arm_levels(block)
    _expect(levels["D"] < 1e-9, f"{block.tag}: the kernel arm reads {levels['D']}")
    if "D2" in levels:
        _expect(levels["D2"] < 1e-9, f"{block.tag}: the second kernel arm reads {levels['D2']}")
    _expect(abs(levels["E0"] - 0.25) < 1e-12 and abs(levels["E1"] - 0.25) < 1e-12, f"{block.tag}: null level")
    for arm in ("F", "C", "N"):
        _expect(levels["T"] - levels[arm] >= pft.SEPARATION, f"{block.tag}: arm {arm} reads {levels[arm]}")
    _expect(pft.separates(block), f"{block.tag}: separates")


@pytest.mark.parametrize("block", CHOSEN, ids=lambda b: b.tag)
def test_input_state_circuit_prepares_the_vector_up_to_sign(block: pft.FourBlock) -> None:
    for arm in pft.SHARED_ARMS:
        psi = pft.arm_inputs(block)[arm][0]
        if psi is None:
            continue
        state = Statevector(pft.prep_layer().assign_parameters(pft.binding(psi))).data
        overlap = abs(np.vdot(state, psi))
        _expect(abs(overlap - 1.0) < 1e-12, f"{block.tag} {arm}: |<prep|psi>| = {overlap}")


@pytest.mark.parametrize("block", CHOSEN, ids=lambda b: b.tag)
def test_parametrized_arms_share_one_circuit_and_mutated_arms_do_not(block: pft.FourBlock) -> None:
    members = {m.name: m for m in pft.four_term_members((block,))}
    shared = {
        id(members[f"ftb_{block.tag}_{arm}"].circuit) for arm in pft.SHARED_ARMS if f"ftb_{block.tag}_{arm}" in members
    }
    _expect(len(shared) == 1, f"{block.tag}: the shared arms use {len(shared)} circuits")
    for arm in ("C", "N"):
        _expect(id(members[f"ftb_{block.tag}_{arm}"].circuit) not in shared, f"{block.tag}: arm {arm} shares it")


def test_ideal_summary_has_unit_visibility_and_zero_closure() -> None:
    group = pft.four_term_group()
    summary = group.summarize({m.name: m.ideal for m in group.members})
    visibilities = [v for k, v in summary.items() if k.endswith("_visibility")]
    _expect(len(visibilities) == len(CHOSEN) and all(abs(v - 1.0) < 1e-12 for v in visibilities), "visibility")
    closures = [v for k, v in summary.items() if "_closure_" in k]
    _expect(bool(closures) and max(abs(v) for v in closures) < 1e-12, "closure")


def test_second_kernel_arm_exists_exactly_for_a_two_dimensional_kernel() -> None:
    for block in CHOSEN:
        matrix = pft.block_matrix(block)
        kernel_dimension = int(np.sum(pft.gram_spectrum(matrix) < pft.ZERO))
        first, second = pft.kernel_vector(matrix), pft.second_kernel_vector(matrix)
        _expect((second is not None) == (kernel_dimension >= 2), f"{block.tag}: kernel dimension {kernel_dimension}")
        if first is not None and second is not None:
            _expect(abs(float(first @ second)) < 1e-12, f"{block.tag}: the kernel arms are not orthogonal")
            _expect(float(np.linalg.norm(matrix @ second)) < 1e-12, f"{block.tag}: D2 is not in the kernel")
