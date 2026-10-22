"""Finite claim checks for Cayley-Dickson circuits in ordinary complex quantum mechanics.

The audit separates bounded circuit equality from polynomial-oracle promises,
algebra representations, and topology. Every Qiskit evaluation uses a local
Statevector; the module imports neither credentials nor a Runtime service.
Run the module to emit its verified, deterministic JSON evidence on stdout.
"""

from __future__ import annotations

import json
import math
import platform
from importlib.metadata import version
from itertools import combinations

import numpy as np
from qiskit.quantum_info import Statevector

import parallel
import predict
from boolean_anf import anf_coefficients, anf_degree_from_coefficients, evaluate_anf, partial_anf_coefficients
from cd_core import cd_multiply_exact
from designs import design_c_associator_spectrum, design_d_phase_sweep

SPECTRUM_DIMENSIONS = (8, 16, 32, 64)
TOLERANCE = 1e-10


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def low_weight_inputs(variable_count: int, maximum_degree: int) -> tuple[int, ...]:
    """Inputs needed to interpolate a degree-promised Boolean polynomial.

    The executable audit bounds the domain at eight variables. The query
    count is sum(comb(n, degree), degree=0..d); uniqueness follows because
    the monomial evaluation matrix on these subsets is unit triangular.
    """
    if not 0 <= variable_count <= 8:
        raise ValueError("variable_count must lie in [0, 8] for the finite audit")
    if not 0 <= maximum_degree <= variable_count:
        raise ValueError("maximum_degree must lie in [0, variable_count]")
    return tuple(
        sorted(
            sum(1 << bit_index for bit_index in support)
            for degree in range(maximum_degree + 1)
            for support in combinations(range(variable_count), degree)
        )
    )


def _classical_recovery_check(case: tuple[int, int]) -> dict[str, object]:
    variable_count, maximum_degree = case
    query_inputs = low_weight_inputs(variable_count, maximum_degree)
    expected_count = sum(math.comb(variable_count, degree) for degree in range(maximum_degree + 1))
    _require(len(query_inputs) == expected_count, "low-weight query count changed")
    # Interpolation is linear, so every coefficient basis vector and a dense
    # combination exercise the complete bounded-degree polynomial space.
    coefficient_cases = [(mask,) for mask in query_inputs] + [query_inputs]
    for coefficients in coefficient_cases:
        samples = {input_value: evaluate_anf(coefficients, input_value) for input_value in query_inputs}
        recovered = partial_anf_coefficients(samples, variable_count, maximum_degree)
        _require(recovered == coefficients, f"degree-promised recovery failed for {case}, {coefficients}")

    higher_degree_mask = (1 << (maximum_degree + 1)) - 1
    _require(maximum_degree < variable_count, "negative control needs an unqueried higher-degree monomial")
    outside_promise = {input_value: evaluate_anf((higher_degree_mask,), input_value) for input_value in query_inputs}
    _require(all(value == 0 for value in outside_promise.values()), "higher-degree alias stopped aliasing")
    recovered_alias = partial_anf_coefficients(outside_promise, variable_count, maximum_degree)
    _require(recovered_alias == (), "zero samples must interpolate the zero polynomial")
    _require(evaluate_anf((higher_degree_mask,), higher_degree_mask) == 1, "higher-degree control vanished")
    return {
        "variables": variable_count,
        "promised_maximum_degree": maximum_degree,
        "classical_queries": len(query_inputs),
        "full_truth_table_size": 1 << variable_count,
        "coefficient_basis_cases": len(query_inputs),
        "dense_case_verified": True,
        "outside_promise_alias_mask": higher_degree_mask,
        "scope": "Unique recovery assumes an ordinary value oracle and degree <= d; promise testing is separate.",
    }


def _spectrum_check(dimension: int) -> dict[str, object]:
    variable_count = dimension.bit_length() - 1
    first_unit, second_unit = 1, dimension // 2
    phase = predict.associator_phase(dimension, first_unit, second_unit)
    truth_table = [int(sign < 0) for sign in phase]
    coefficients = anf_coefficients(truth_table)
    degree = anf_degree_from_coefficients(coefficients)
    _require(degree == variable_count - 2, f"high-bit exemplar degree changed at dimension {dimension}")

    # Direct integer Walsh sums provide an independent reference for both the
    # fast classical transform and the circuit's local statevector.
    walsh_sums = [
        sum(sign * (-1 if (input_value & outcome).bit_count() % 2 else 1) for input_value, sign in enumerate(phase))
        for outcome in range(dimension)
    ]
    probabilities = np.asarray([(coefficient / dimension) ** 2 for coefficient in walsh_sums])
    _require(abs(float(probabilities.sum()) - 1.0) < TOLERANCE, "Walsh probabilities lost normalization")
    _require(
        float(np.max(np.abs(predict.walsh_distribution(phase) - probabilities))) < TOLERANCE,
        "fast Walsh transform disagrees with direct integer sums",
    )
    circuit = design_c_associator_spectrum(dimension, first_unit, second_unit)
    actual = Statevector(circuit.remove_final_measurements(inplace=False)).probabilities()
    maximum_error = float(np.max(np.abs(actual - probabilities)))
    _require(maximum_error < TOLERANCE, f"spectrum circuit differs at dimension {dimension}")
    mutant = design_c_associator_spectrum(dimension, first_unit, second_unit, flip=0)
    mutant_probabilities = Statevector(mutant.remove_final_measurements(inplace=False)).probabilities()
    mutation_error = float(np.max(np.abs(mutant_probabilities - probabilities)))
    _require(mutation_error > TOLERANCE, f"single-sign circuit mutation escaped dimension {dimension}")
    return {
        "dimension": dimension,
        "data_qubits": variable_count,
        "basis_units": [first_unit, second_unit],
        "anf_degree": degree,
        "anf_masks": list(coefficients),
        "walsh_numerators": walsh_sums,
        "probability_denominator": dimension**2,
        "maximum_statevector_error": maximum_error,
        "single_sign_mutation_error": mutation_error,
        "scope": "One circuit sample is one outcome; spectrum reconstruction and hidden-oracle identification differ.",
    }


def _representation_check() -> dict[str, object]:
    octonion_first, octonion_second, octonion_probe = (
        tuple(int(coordinate == index) for coordinate in range(8)) for index in (1, 2, 4)
    )
    product_then_action = cd_multiply_exact(8, cd_multiply_exact(8, octonion_first, octonion_second), octonion_probe)
    composed_actions = cd_multiply_exact(8, octonion_first, cd_multiply_exact(8, octonion_second, octonion_probe))
    _require(product_then_action == (0, 0, 0, 0, 0, 0, 0, 1), "octonion left-associated witness changed")
    _require(composed_actions == (0, 0, 0, 0, 0, 0, 0, -1), "octonion right-associated witness changed")

    sedenion_element = tuple(int(index in (1, 10)) for index in range(16))
    sedenion_probe = tuple(int(index == 4) - int(index == 15) for index in range(16))
    product = cd_multiply_exact(16, sedenion_element, sedenion_probe)
    square = cd_multiply_exact(16, sedenion_element, sedenion_element)
    square_action = cd_multiply_exact(16, square, sedenion_probe)
    action_squared = cd_multiply_exact(16, sedenion_element, product)
    _require(not any(product), "sedenion annihilator witness changed")
    _require(square == (-2,) + (0,) * 15, "sedenion square witness changed")
    _require(not any(action_squared), "repeated annihilator action changed")
    _require(square_action == tuple(-2 * value for value in sedenion_probe), "Jordan square defect changed")
    _require(square_action != action_squared, "left multiplication unexpectedly preserves the witness square")
    return {
        "octonion_product_action": {"basis_index": 7, "coefficient": 1},
        "octonion_composed_actions": {"basis_index": 7, "coefficient": -1},
        "sedenion_element": "e1 + e10",
        "sedenion_probe": "e4 - e15",
        "sedenion_square": "-2 e0",
        "repeated_action_on_probe": "0",
        "square_action_on_probe": "-2 e4 + 2 e15",
        "scope": (
            "These left actions encode products but fail multiplicativity; "
            "the sedenion map also fails Jordan square preservation."
        ),
        "albert_scope": (
            "The 27-dimensional Albert algebra J3(O) uses a different product "
            "from the 16-dimensional sedenion circuits."
        ),
    }


def _walsh_ambiguity_check(variable_count: int) -> dict[str, object]:
    dimension = 1 << variable_count
    first_coefficients, second_coefficients = (7,), (6, 7)
    first_truth = [evaluate_anf(first_coefficients, input_value) for input_value in range(dimension)]
    second_truth = [evaluate_anf(second_coefficients, input_value) for input_value in range(dimension)]
    _require(first_truth != second_truth, "Walsh ambiguity requires distinct Boolean functions")
    _require(
        all(second_truth[input_value] == first_truth[input_value ^ 1] for input_value in range(dimension)),
        "cubic translation witness changed",
    )
    squared_spectra = [
        [
            sum(
                (-1 if (value + (input_value & outcome).bit_count()) % 2 else 1)
                for input_value, value in enumerate(truth_table)
            )
            ** 2
            for outcome in range(dimension)
        ]
        for truth_table in (first_truth, second_truth)
    ]
    _require(squared_spectra[0] == squared_spectra[1], "translated cubics changed their squared Walsh spectrum")
    return {
        "variables": variable_count,
        "first_anf_masks": list(first_coefficients),
        "second_anf_masks": list(second_coefficients),
        "input_translation_xor": 1,
        "squared_walsh_numerators": squared_spectra[0],
        "probability_denominator": dimension**2,
        "scope": "Even exact squared Walsh probabilities cannot distinguish these different cubic functions.",
    }


def _annihilator_fringe_check() -> dict[str, object]:
    element_operator = predict.left_mult_matrix(16, 1).astype(np.int64) + predict.left_mult_matrix(16, 10).astype(
        np.int64
    )
    gram = element_operator.T @ element_operator
    identity = np.eye(16, dtype=np.int64)
    polynomial_residual = gram @ (gram - 2 * identity) @ (gram - 4 * identity)
    _require(np.array_equal(polynomial_residual, np.zeros_like(gram)), "integer Gram polynomial failed")
    _require(int(np.trace(gram)) == 32, "integer Gram trace changed")
    _require(int(np.trace(gram @ gram)) == 96, "integer Gram square trace changed")
    # Symmetry plus the annihilating polynomial restricts eigenvalues to
    # 0, 2, 4; dimension and the two traces fix multiplicities 4, 8, 4.
    normalized_eigenvalues = np.linalg.eigvalsh(gram / 4.0)
    expected_eigenvalues = np.asarray([0.0] * 4 + [0.5] * 8 + [1.0] * 4)
    _require(
        float(np.max(np.abs(normalized_eigenvalues - expected_eigenvalues))) < TOLERANCE,
        "normalized Gram eigenvalues disagree with the exact polynomial and traces",
    )

    phase_rows: list[dict[str, object]] = []
    maximum_error = 0.0
    for phase_index in range(9):
        phase = phase_index * math.pi / 4
        input_state = np.zeros(16, dtype=complex)
        input_state[4] = 1 / math.sqrt(2)
        input_state[15] = np.exp(1j * phase) / math.sqrt(2)
        product = element_operator @ input_state
        product_norm_squared = float(np.vdot(product, product).real)
        probability = product_norm_squared / 4
        expected_probability = (1 + math.cos(phase)) / 2
        _require(abs(probability - expected_probability) < TOLERANCE, "analytic fringe changed")
        circuit = design_d_phase_sweep((1, 10), (4, 15), phase)
        actual = float(Statevector(circuit.remove_final_measurements(inplace=False)).probabilities([4])[0])
        maximum_error = max(maximum_error, abs(actual - probability))
        phase_rows.append(
            {"phase_pi_over_four": phase_index, "product_norm_squared": product_norm_squared, "p0": probability}
        )
        if phase_index == 2:
            _require(abs(input_state[15].imag) > 0.5, "pi/2 probe unexpectedly has real coordinates")
            _require(abs(product_norm_squared - 2.0) < TOLERANCE, "pi/2 probe unexpectedly annihilates")
        if phase_index == 4:
            _require(product_norm_squared < TOLERANCE, "real dark probe left the annihilator")
    _require(maximum_error < TOLERANCE, "phase sweep differs from independent matrix action")
    return {
        "element": "e1 + e10",
        "gram_polynomial": "G(G-2I)(G-4I)=0 for G=(L1+L10)^T(L1+L10)",
        "gram_trace": 32,
        "gram_square_trace": 96,
        "normalized_gram_spectrum": [
            {"value": 0, "multiplicity": 4},
            {"value": 0.5, "multiplicity": 8},
            {"value": 1, "multiplicity": 4},
        ],
        "real_kernel_dimension": 4,
        "fixed_element_unit_kernel_sphere": "S3",
        "phase_rows": phase_rows,
        "maximum_statevector_error": maximum_error,
        "pi_over_two_real_variety_member": False,
        "scope": (
            "A fixed-element unit kernel is S3; the complex fringe leaves "
            "the real zero-product variety and does not measure its topology."
        ),
    }


def _verify_input_limits() -> None:
    for variable_count, maximum_degree in ((-1, 0), (9, 0), (3, -1), (3, 4)):
        try:
            low_weight_inputs(variable_count, maximum_degree)
        except ValueError:
            continue
        raise RuntimeError(f"low-weight input generator accepted invalid {(variable_count, maximum_degree)}")
    _require(low_weight_inputs(0, 0) == (0,), "constant polynomial domain changed")


def audit_claim_boundaries() -> dict[str, object]:
    """Check every fixed witness and return serializable local evidence."""
    _verify_input_limits()
    recovery_cases = [(dimension.bit_length() - 1, dimension.bit_length() - 3) for dimension in SPECTRUM_DIMENSIONS]
    return {
        "schema": "cayley-dickson-claim-boundaries-v1",
        "execution": "local exact arithmetic and Qiskit Statevector",
        "qpu_executed": False,
        "versions": {"python": platform.python_version(), "numpy": version("numpy"), "qiskit": version("qiskit")},
        "classical_recovery": parallel.ordered_map(_classical_recovery_check, recovery_cases, min_items=2),
        "associator_spectra": parallel.ordered_map(_spectrum_check, SPECTRUM_DIMENSIONS, min_items=2),
        "walsh_ambiguity": parallel.ordered_map(_walsh_ambiguity_check, (3, 5), min_items=2),
        "representation": _representation_check(),
        "annihilator_fringe": _annihilator_fringe_check(),
    }


def main() -> int:
    print(json.dumps(audit_claim_boundaries(), indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
