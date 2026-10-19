"""Independent exact and core-Qiskit checks for the four-qubit rank sectors.

The recursive doubling product supplies all 1,024 basis products independently
of cd_sign. Polynomial matrices certify the complete sector decomposition and
the four fixed singular directions in sectors four through seven. Finite
circuits test the selected block and all selector outcomes on the proposed
grid; the exact rank theorem remains in rank_attachments.py.
"""

from __future__ import annotations

import json
import math
from collections import Counter
from collections.abc import Callable
from fractions import Fraction
from functools import partial
from typing import Any

import numpy as np
import sympy as sp
from qiskit.quantum_info import Operator, Statevector

import parallel
from cd_core import cd_sign
from rank_attachments import COSET_SUBGROUP, common_kernel_basis, path_matrix
from rank_sector_experiments import (
    PARAMETERS,
    SCIENCE_ROWS,
    TOTAL_ROWS,
    exact_success_probability,
    member_name,
    preparation_angles,
    preparation_matrix,
    reference_probes,
    sector_alpha,
    sector_binding,
    sector_configuration,
    sector_contracts,
    sector_groups,
    sector_probes,
    sector_template,
    sector_terms,
    selector_distribution,
)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _conjugate(vector: tuple[int, ...]) -> tuple[int, ...]:
    return (vector[0], *(-value for value in vector[1:]))


def _recursive_product(left: tuple[int, ...], right: tuple[int, ...]) -> tuple[int, ...]:
    if len(left) == 1:
        return (left[0] * right[0],)
    half = len(left) // 2
    first, second = left[:half], left[half:]
    third, fourth = right[:half], right[half:]
    upper_first = _recursive_product(first, third)
    upper_second = _recursive_product(_conjugate(fourth), second)
    lower_first = _recursive_product(fourth, first)
    lower_second = _recursive_product(second, _conjugate(third))
    return tuple(a - b for a, b in zip(upper_first, upper_second, strict=True)) + tuple(
        a + b for a, b in zip(lower_first, lower_second, strict=True)
    )


def _check_basis_row(first: int) -> int:
    left = tuple(int(index == first) for index in range(32))
    for second in range(32):
        right = tuple(int(index == second) for index in range(32))
        observed = _recursive_product(left, right)
        expected = tuple(cd_sign(32, first, second) if index == first ^ second else 0 for index in range(32))
        _require(observed == expected, f"recursive doubling basis product {first},{second}")
    return 32


def _symbolic_sector(sector: int) -> dict[str, Any]:
    parameter = sp.Symbol("t", real=True)
    full = path_matrix(parameter)
    columns = [sector ^ offset for offset in COSET_SUBGROUP]
    rows = [1 ^ column for column in columns]
    block = full.extract(rows, columns)
    outside = [column for column in range(32) if column not in columns]
    _require(full.extract(rows, outside) == sp.zeros(4, 28), f"sector {sector}: off-block polynomial entries")
    terms = [sp.Matrix(matrix) for matrix in sector_terms(sector)]
    for term in terms:
        _require(term.T * term == sp.eye(4), f"sector {sector}: signed-permutation orthogonality")
    coefficients = (1, (parameter - 1) ** 2, parameter * (3 - parameter) / 2, -parameter * (parameter - 1) / 2)
    combination = sum((coefficient * term for coefficient, term in zip(coefficients, terms, strict=True)), sp.zeros(4))
    _require(
        (combination - block).applyfunc(sp.expand) == sp.zeros(4), f"sector {sector}: polynomial term decomposition"
    )
    probes = sector_probes(sector)
    probe_records = []
    for probe in probes:
        vector = sp.Matrix(probe.coordinates)
        image = block * vector
        norm = sp.factor((image.T * image)[0] / (vector.T * vector)[0])
        probe_records.append({"name": probe.name, "squared_norm_polynomial": str(norm)})
    if sector >= 4:
        frame = sp.Matrix.hstack(*(sp.Matrix(probe.coordinates) for probe in probes)) / 2
        _require(frame.T * frame == sp.eye(4), f"sector {sector}: fixed probe frame")
        expected = sp.diag(
            0,
            4 * parameter**2 * (parameter - 2) ** 2,
            (parameter - 2) ** 2 * (parameter - 1) ** 2,
            (parameter**2 - parameter + 2) ** 2,
        )
        _require(
            (frame.T * block.T * block * frame - expected).applyfunc(sp.expand) == sp.zeros(4),
            f"sector {sector}: fixed singular frame polynomial identity",
        )
        canonical_kernel = common_kernel_basis().extract(columns, [sector - 4])
        _require(frame[:, 0] == -canonical_kernel / 2, f"sector {sector}: canonical persistent kernel")
        fixed_frame = True
    else:
        gram = block.T * block
        first = gram.subs(parameter, sp.Rational(1, 2))
        second = gram.subs(parameter, sp.Rational(3, 2))
        _require(first * second != second * first, f"sector {sector}: varying Gram directions")
        fixed_frame = False
    if sector == 4:
        sparse = sp.Matrix((1, -1, 0, 0))
        sparse_image = block * sparse
        _require(
            sp.expand((sparse_image.T * sparse_image)[0] / 2 - 2 * parameter**2 * (parameter - 2) ** 2) == 0,
            "two-component sparse witness normalization",
        )
    return {
        "sector": sector,
        "input_columns": columns,
        "output_rows": rows,
        "ranks_at_parameters": [
            int(block.subs(parameter, value.numerator / sp.Integer(value.denominator)).rank()) for value in PARAMETERS
        ],
        "fixed_orthonormal_singular_frame": fixed_frame,
        "probe_polynomials": probe_records,
    }


def _exact_probability_sector(sector: int) -> None:
    """Compare sparse exact action with the independent full symbolic matrix."""
    columns = [sector ^ offset for offset in COSET_SUBGROUP]
    parameters = (*PARAMETERS, Fraction(1, 7), Fraction(11, 9), Fraction(2**60 - 1, 2**60))
    for parameter in parameters:
        matrix = path_matrix(parameter)[:, columns]
        for probe in sector_probes(sector):
            image = matrix * sp.Matrix(probe.coordinates)
            numerator = sum(coordinate**2 for coordinate in image)
            exact_norm = Fraction(int(numerator.p), int(numerator.q))
            expected = exact_norm / (
                sum(coordinate**2 for coordinate in probe.coordinates) * sector_alpha(parameter) ** 2
            )
            _require(
                exact_success_probability(sector, probe.name, parameter) == expected,
                f"sector {sector}, probe {probe.name}, parameter {parameter}: sparse exact action differs",
            )


def _circuit_sector(sector: int) -> dict[str, Any]:
    _exact_probability_sector(sector)
    template, parameters = sector_template(sector)
    maximum_error = 0.0
    probabilities: list[dict[str, Any]] = []
    columns = [sector ^ offset for offset in COSET_SUBGROUP]
    rows = [1 ^ column for column in columns]
    for probe_index, probe in enumerate(sector_probes(sector)):
        for parameter in PARAMETERS:
            bound = template.assign_parameters(sector_binding(sector, probe.name, parameter, parameters))
            circuit = bound.remove_final_measurements(inplace=False)
            state = Statevector(circuit)
            ideal = selector_distribution(sector, probe.name, parameter)
            exact = exact_success_probability(sector, probe.name, parameter)
            maximum_error = max(
                maximum_error,
                float(np.max(np.abs(state.probabilities((2, 3)) - ideal))),
                abs(float(state.probabilities((2, 3))[0]) - float(exact)),
            )
            if probe_index == 0:
                block = path_matrix(parameter).extract(rows, columns)
                normalized_block = np.asarray(block, dtype=float) / float(sector_alpha(parameter))
                prepare = preparation_matrix(preparation_angles(tuple(float(value) for value in probe.coordinates)))
                expected = normalized_block @ prepare
                observed = Operator(circuit).data[:4, :4]
                maximum_error = max(maximum_error, float(np.max(np.abs(observed - expected))))
            probabilities.append({"member": member_name(sector, probe.name, parameter), "success": str(exact)})
    _require(maximum_error < 1e-12, f"sector {sector}: Qiskit probabilities or complete selected block differ")
    return {
        "sector": sector,
        "circuits": len(probabilities),
        "selected_blocks": len(PARAMETERS),
        "maximum_error": maximum_error,
        "probabilities": probabilities,
    }


def _expect_rejected(operation: Callable[[], object], label: str) -> None:
    try:
        operation()
    except (ValueError, RuntimeError):
        return
    raise RuntimeError(f"invalid rank-sector input accepted: {label}")


def _negative_controls() -> list[str]:
    for invalid_sector in (-1, 8, True):
        _expect_rejected(partial(sector_template, invalid_sector), f"sector {invalid_sector}")
    invalid_parameters: tuple[Any, ...] = (Fraction(-1), Fraction(3), True, 0.5)
    for invalid_parameter in invalid_parameters:
        _expect_rejected(
            partial(exact_success_probability, 4, "bright", invalid_parameter), f"parameter {invalid_parameter}"
        )
    _expect_rejected(lambda: exact_success_probability(0, "persistent_kernel", 0), "unavailable persistent kernel")
    _expect_rejected(lambda: preparation_angles((0.0, 0.0, 0.0, 0.0)), "zero probe")
    _expect_rejected(lambda: sector_contracts(0.08, True, 0.8), "Boolean alpha")
    _expect_rejected(lambda: sector_contracts(0.08, 0.05, math.nan), "nonfinite power")
    template, parameters = sector_template(4)
    binding = sector_binding(4, "bright", Fraction(3, 2), parameters)
    binding[parameters[-1]] = 0.0
    altered = template.assign_parameters(binding).remove_final_measurements(inplace=False)
    altered_probability = float(Statevector(altered).probabilities((2, 3))[0])
    _require(abs(altered_probability - 1) > 0.1, "coefficient-sign mutation fails to expose a discrepancy")
    wrong_alpha_probability = Fraction(9, 16) * sector_alpha(Fraction(1, 2)) ** 2
    _require(wrong_alpha_probability > 1, "omitted LCU normalization fails to expose an invalid probability")
    return [
        "sector-range-and-boolean",
        "parameter-range-exactness-and-boolean",
        "probe-domain",
        "zero-preparation",
        "contract-boolean-and-nonfinite",
        "coefficient-sign",
        "LCU-normalization",
    ]


def audit_rank_sectors() -> dict[str, Any]:
    configuration = sector_configuration()
    basis_count = sum(parallel.ordered_map(_check_basis_row, list(range(32)), min_items=2))
    symbolic = parallel.ordered_map(_symbolic_sector, list(range(8)), min_items=2)
    circuit_checks = parallel.ordered_map(_circuit_sector, list(range(8)), min_items=2)
    columns = [column for record in symbolic for column in record["input_columns"]]
    rows = [row for record in symbolic for row in record["output_rows"]]
    _require(sorted(columns) == sorted(rows) == list(range(32)), "complete sector row and column permutations")
    full_nullities = [
        32 - sum(record["ranks_at_parameters"][index] for record in symbolic) for index in range(len(PARAMETERS))
    ]
    _require(full_nullities == [8, 4, 12, 4, 16], "finite path rank points")
    groups = sector_groups()
    occupancy: Counter[int] = Counter()
    members = {}
    for sector, group in enumerate(groups):
        _require(len(group.members) == 22, f"sector {sector}: member count")
        _require(group.execution_rows is not None and len(group.execution_rows) == 22, f"sector {sector}: row count")
        if group.execution_rows is None:
            raise RuntimeError("missing sector rows")
        occupancy.update(group.execution_rows)
        _require(
            all(member.circuit is group.members[0].circuit for member in group.members),
            f"sector {sector}: members lost their shared template",
        )
        for member in group.members:
            _require(member.name not in members, "unique science and reference names")
            members[member.name] = member
        for probe_name in reference_probes(sector):
            packed = members[member_name(sector, probe_name, 1)]
            reference = members[member_name(sector, probe_name, 1, reference=True)]
            _require(
                packed.circuit is reference.circuit and packed.binding == reference.binding,
                f"sector {sector}: reference differs from packed source",
            )
        summary = group.summarize({member.name: member.ideal for member in group.members})
        _require(
            all(abs(value) < 1e-12 for key, value in summary.items() if key.endswith("_packed_minus_reference")),
            f"sector {sector}: ideal packing reference residual",
        )
    _require(
        occupancy == Counter({row: 8 if row < SCIENCE_ROWS else 1 for row in range(TOTAL_ROWS)}),
        "eight packed lanes and exclusive isolated rows",
    )
    contracts = sector_contracts(0.08, 0.05, 0.8)
    _require(len(contracts) == 196 and len({contract.name for contract in contracts}) == 196, "contract coverage")
    _require(abs(math.fsum(contract.alpha for contract in contracts) - 0.05) < 1e-15, "familywise alpha allocation")
    effects = []
    for contract in contracts:
        _require(all(term.member in members for term in contract.terms), f"contract {contract.name}: member coverage")
        if contract.minimum_effect is not None:
            effect = sum(
                term.sign * float(members[term.member].ideal @ np.asarray(term.values)) for term in contract.terms
            )
            _require(
                effect >= float(Fraction(9, 64)) - 1e-12, f"contract {contract.name}: insufficient ideal separation"
            )
            effects.append({"name": contract.name, "ideal_effect": effect})
    _require(len(effects) == 20, "directional endpoint coverage")
    negative_controls = _negative_controls()
    _require(configuration["source_sha256"] == sector_configuration()["source_sha256"], "source changed during audit")
    return {
        "schema": "rank-sector-exact-and-circuit-audit-v1",
        "qpu_executed": False,
        "configuration": configuration,
        "independent_recursive_basis_products": basis_count,
        "symbolic_sectors": symbolic,
        "full_nullities_at_parameters": full_nullities,
        "circuit_checks": circuit_checks,
        "scientific_circuits": sum(record["circuits"] for record in circuit_checks),
        "selected_blocks": sum(record["selected_blocks"] for record in circuit_checks),
        "contract_count": len(contracts),
        "directional_effects": effects,
        "negative_controls": negative_controls,
    }


def main() -> int:
    print(json.dumps(audit_rank_sectors(), indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
