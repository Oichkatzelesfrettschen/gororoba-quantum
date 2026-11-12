"""Falsifiers for exact LCU normalization, kernel filtering and finite-field shortcuts."""

from __future__ import annotations

from fractions import Fraction
from typing import Literal

import pytest

import cd_core
from cd_quantum_contracts import (
    NaturalLCU,
    basis_unit_properties,
    isotropy_counterexample,
    kernel_projector,
    modular_rank_counterexample,
)


def test_signed_weighted_lcu_matches_direct_multiplication() -> None:
    coefficients = (Fraction(2, 3), Fraction(-5, 4), Fraction(0), Fraction(7, 6))
    encoding = NaturalLCU(4, coefficients)
    if encoding.alpha != Fraction(37, 12) or encoding.selector_qubits != 2:
        raise AssertionError("the signed weights or padded selector size differ")
    if sum(encoding.preparation_probabilities) != 1 or encoding.preparation_probabilities[-1] != 0:
        raise AssertionError("the selector probabilities are not normalized with zero padding")
    block = encoding.selected_block()
    vector = (Fraction(1, 2), Fraction(-2), Fraction(3, 5), Fraction(7))
    direct = cd_core.cd_multiply_exact(4, coefficients, vector)
    actual = tuple(sum(value * entry for value, entry in zip(row, vector, strict=True)) for row in block)
    if actual != tuple(value / encoding.alpha for value in direct):
        raise AssertionError("the selected block lost the coefficient sign or normalization")
    if encoding.normalization_ratio_upper_squared > len(encoding.terms):
        raise AssertionError("the coefficient-norm bound exceeds the support-size bound")
    if encoding.select_action(3, 2) != (2, 1):
        raise AssertionError("a padded SELECT state does not act as identity")


def test_negative_single_term_has_no_selector_and_keeps_its_phase() -> None:
    encoding = NaturalLCU(2, (0, -3))
    if encoding.selector_qubits != 0 or encoding.preparation_probabilities != (Fraction(1),):
        raise AssertionError("a single term acquired a selector")
    if encoding.selected_block() != ((Fraction(0), Fraction(1)), (Fraction(-1), Fraction(0))):
        raise AssertionError("a negative coefficient became an unobservable dropped global sign")


@pytest.mark.parametrize("coefficients", [(0, 0), (1,), (1, True), (1, 0.5)])
def test_lcu_rejects_zero_wrong_length_and_inexact_coefficients(coefficients: tuple) -> None:
    with pytest.raises(ValueError):
        NaturalLCU(2, coefficients)


@pytest.mark.parametrize("selector,basis_index", [(True, 0), (-1, 0), (2, 0), (0, 4), (0, False)])
def test_lcu_rejects_indices_outside_its_register(selector: int, basis_index: int) -> None:
    with pytest.raises(ValueError):
        NaturalLCU(4, (1, -1, 0, 0)).select_action(selector, basis_index)


def test_a5_lcu_uses_support_size_not_pauli_count() -> None:
    dense = NaturalLCU(32, tuple(range(1, 33)))
    sparse = NaturalLCU(32, tuple(int(i == 1) + int(i == 10) for i in range(32)))
    if dense.data_qubits != 5 or dense.selector_qubits != 5 or sparse.selector_qubits != 1:
        raise AssertionError("natural LCU register counts do not follow the number of basis terms")
    if dense.normalization_ratio_upper_squared > 32 or sparse.alpha != 2:
        raise AssertionError("the natural coefficient normalization differs")


@pytest.mark.parametrize("strategy", ["diagonal", "reed_muller"])
@pytest.mark.parametrize("first,second,sign", [(1, 10, 1), (25, 8, -1)])
def test_existing_two_term_select_encodes_the_exact_a5_block(
    first: int, second: int, sign: int, strategy: Literal["diagonal", "reed_muller"]
) -> None:
    import numpy as np
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Operator

    from select_lcu import select_circuit

    coefficients = tuple(int(index == first) + sign * int(index == second) for index in range(32))
    encoding = NaturalLCU(32, coefficients)
    terms = encoding.terms
    circuit = QuantumCircuit(6)
    circuit.h(5)
    circuit.compose(select_circuit(32, terms[0][0], terms[1][0], strategy), inplace=True)
    if terms[0][1] < 0:
        circuit.x(5)
        circuit.z(5)
        circuit.x(5)
    if terms[1][1] < 0:
        circuit.z(5)
    circuit.h(5)
    block = Operator(circuit).data[:32, :32]
    expected = np.asarray(encoding.selected_block(), dtype=np.complex128)
    if not np.allclose(block, expected, atol=1e-12, rtol=0):
        raise AssertionError("the existing SELECT circuit differs from the exact signed LCU block")


def test_kernel_projector_recovers_a_noncoordinate_kernel() -> None:
    certificate = kernel_projector(((1, 1, 0), (0, 0, 2)), (2, 4))
    expected = (
        (Fraction(1, 2), Fraction(-1, 2), Fraction(0)),
        (Fraction(-1, 2), Fraction(1, 2), Fraction(0)),
        (Fraction(0),) * 3,
    )
    if certificate.projector != expected or certificate.nullity != 1 or certificate.rank != 2:
        raise AssertionError("the exact projector does not recover span((1,-1,0))")


@pytest.mark.parametrize("roots", [(2,), (2, 3), (), (0, 2), (-1, 2), (2, 2), (True, 4), (2.0, 4)])
def test_projector_rejects_incomplete_wrong_or_inexact_roots(roots: tuple) -> None:
    with pytest.raises(ValueError):
        kernel_projector(((1, 1, 0), (0, 0, 2)), roots)


@pytest.mark.parametrize("matrix", [(), ((),), ((1,), (1, 2)), ((1.0,),), ((True,),)])
def test_projector_rejects_malformed_or_inexact_matrices(matrix: tuple) -> None:
    with pytest.raises(ValueError):
        kernel_projector(matrix, (1,))


def test_zero_matrix_and_invertible_matrix_have_complementary_projectors() -> None:
    zero = kernel_projector(((0, 0),), ())
    invertible = kernel_projector(((0, -2), (2, 0)), (4,))
    if zero.nullity != 2 or zero.rank != 0 or invertible.nullity != 0 or invertible.rank != 2:
        raise AssertionError("the zero or invertible limiting case differs")


@pytest.mark.parametrize("left,second,sign,expected_nullity", [(1, 10, 1, 8), (25, 8, -1, 12)])
def test_selected_a5_singular_matrices_have_exact_kernel_filters(
    left: int, second: int, sign: int, expected_nullity: int
) -> None:
    coefficients = tuple(int(index == left) + sign * int(index == second) for index in range(32))
    matrix = cd_core.left_mult_matrix_exact(32, coefficients)
    certificate = kernel_projector(matrix, (2, 4))
    if certificate.nullity != expected_nullity:
        raise AssertionError("the A5 Gram-polynomial projector has the wrong exact nullity")


@pytest.mark.parametrize("modulus", [32009, 32029])
def test_isotropy_can_hold_for_an_invertible_a5_matrix(modulus: int) -> None:
    witness = isotropy_counterexample(32, 1, modulus)
    if witness["quadratic_form"] != 0 or witness["image"] != [0, 1] + [0] * 30:
        raise AssertionError("the explicit isotropic vector is not the nonkernel witness e0")
    if not witness["invertible_by_signed_permutation"] or not witness["quadratic_form_zero_on_all_vectors"]:
        raise AssertionError("the counterexample lost its full-rank or all-vectors certificate")


@pytest.mark.parametrize("imaginary_index,modulus", [(0, 32009), (1, 2), (1, 9.0), (1, True)])
def test_isotropy_certificate_enforces_its_domain(imaginary_index: int, modulus: int) -> None:
    with pytest.raises(ValueError):
        isotropy_counterexample(4, imaginary_index, modulus)


def test_identity_basis_is_a_permutation_but_not_skew_symmetric() -> None:
    identity = basis_unit_properties(4, 0)
    if identity["skew_symmetric"] or not identity["signed_permutation"]:
        raise AssertionError("the scalar control is not separated from imaginary basis units")


@pytest.mark.parametrize("prime", [32009, 32029, 2**61 - 1])
def test_modular_kernel_is_not_the_complex_or_rational_kernel(prime: int) -> None:
    witness = modular_rank_counterexample(prime)
    if witness["matrix"] != [[1, 2], [(prime + 1) // 2, 1]] or witness["determinant_over_Z"] != -prime:
        raise AssertionError("the matrix does not have determinant minus the modulus")
    if witness["rank_over_Q"] != 2 or witness["rank_over_Fp"] != 1:
        raise AssertionError("an integer lift inherited finite-field rank")
    vector = witness["modular_kernel_vector"]
    if vector != [prime - 2, 1] or witness["modular_image"] != [0, 0] or witness["integer_image"] == [0, 0]:
        raise AssertionError("the modular kernel vector was not separated from the rational kernel")


@pytest.mark.parametrize("prime", [2, 9, -3, True, 5.0])
def test_modular_rank_certificate_rejects_nonprime_or_inexact_moduli(prime: int) -> None:
    with pytest.raises(ValueError):
        modular_rank_counterexample(prime)
