"""Exact invariant classification of the two nullity-sixteen kernel bundles.

The connected homogeneous representation reduces from ``U(2)`` to the
``SU(2)`` bundle ``G_2 -> V_2(R^7)``.  The ordinary complex bundle is
``C^2 + 3 xi``, where ``xi`` is the standard complex doublet associated to
that principal bundle.  This replay computes the cellular (co)homology, the
homogeneous representation-ring Koszul complex, the resulting torsion
K-class, and the real, complex, and quaternionic consequences.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections.abc import Sequence
from fractions import Fraction
from itertools import product
from pathlib import Path
from typing import Any

import stabilizer_representation as stabilizer
import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
STABILIZER_RESULT = HERE / "stabilizer-result.json"
STABILIZER_SCRIPT = HERE / "stabilizer_representation.py"
SEDENION_BUNDLE_SCRIPT = ROOT / "gororoba_quantum" / "sedenion_bundle.py"
SEDENION_BUNDLE_RESULT = ROOT / "results" / "hw_estimate" / "sedenion_bundle.json"

BASE_DIMENSION = 11
COMPLEX_RANK = 8
REAL_RANK = 16

Quaternion = tuple[Fraction, Fraction, Fraction, Fraction]
RationalMatrix = tuple[tuple[Fraction, ...], ...]
IntegerPolynomial = tuple[int, ...]


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _identity(dimension: int) -> RationalMatrix:
    return tuple(
        tuple(Fraction(row_index == column_index) for column_index in range(dimension))
        for row_index in range(dimension)
    )


def _matrix_product(first: RationalMatrix, second: RationalMatrix) -> RationalMatrix:
    if not first or len(first[0]) != len(second):
        raise ValueError("matrix dimensions do not compose")
    return tuple(
        tuple(
            sum(
                (
                    first[row_index][middle_index] * second[middle_index][column_index]
                    for middle_index in range(len(second))
                ),
                Fraction(0),
            )
            for column_index in range(len(second[0]))
        )
        for row_index in range(len(first))
    )


def _matrix_add(first: RationalMatrix, second: RationalMatrix) -> RationalMatrix:
    return tuple(
        tuple(left + right for left, right in zip(first_row, second_row, strict=True))
        for first_row, second_row in zip(first, second, strict=True)
    )


def _matrix_scale(matrix: RationalMatrix, scalar: int) -> RationalMatrix:
    return tuple(tuple(scalar * entry for entry in row) for row in matrix)


def _block_diagonal(blocks: tuple[RationalMatrix, ...]) -> RationalMatrix:
    total_dimension = sum(len(block) for block in blocks)
    output = [[Fraction(0) for _ in range(total_dimension)] for _ in range(total_dimension)]
    offset = 0
    for block in blocks:
        _require(bool(block) and all(len(row) == len(block) for row in block), "block diagonal input must be square")
        for row_index, values in enumerate(block):
            for column_index, value in enumerate(values):
                output[offset + row_index][offset + column_index] = value
        offset += len(block)
    return tuple(tuple(row) for row in output)


def _quaternion_multiply(first: Quaternion, second: Quaternion) -> Quaternion:
    first_scalar, first_i, first_j, first_k = first
    second_scalar, second_i, second_j, second_k = second
    return (
        first_scalar * second_scalar - first_i * second_i - first_j * second_j - first_k * second_k,
        first_scalar * second_i + first_i * second_scalar + first_j * second_k - first_k * second_j,
        first_scalar * second_j - first_i * second_k + first_j * second_scalar + first_k * second_i,
        first_scalar * second_k + first_i * second_j - first_j * second_i + first_k * second_scalar,
    )


def _quaternion_conjugate(quaternion: Quaternion) -> Quaternion:
    scalar, first, second, third = quaternion
    return scalar, -first, -second, -third


def _quaternion_norm_squared(quaternion: Quaternion) -> Fraction:
    return sum((coordinate * coordinate for coordinate in quaternion), Fraction(0))


def _left_quaternion_matrix(quaternion: Quaternion) -> RationalMatrix:
    scalar, first, second, third = quaternion
    return (
        (scalar, -first, -second, -third),
        (first, scalar, -third, second),
        (second, third, scalar, -first),
        (third, -second, first, scalar),
    )


def _right_quaternion_matrix(quaternion: Quaternion) -> RationalMatrix:
    basis = (
        (Fraction(1), Fraction(0), Fraction(0), Fraction(0)),
        (Fraction(0), Fraction(1), Fraction(0), Fraction(0)),
        (Fraction(0), Fraction(0), Fraction(1), Fraction(0)),
        (Fraction(0), Fraction(0), Fraction(0), Fraction(1)),
    )
    columns = [_quaternion_multiply(basis_vector, quaternion) for basis_vector in basis]
    return tuple(tuple(columns[column_index][row_index] for column_index in range(4)) for row_index in range(4))


def _complex_standard_matrix(quaternion: Quaternion) -> sp.Matrix:
    scalar, first, second, third = quaternion

    def rational(value: Fraction) -> sp.Rational:
        return sp.Rational(value.numerator, value.denominator)

    return sp.Matrix(
        [
            [rational(scalar) + sp.I * rational(first), rational(second) + sp.I * rational(third)],
            [-rational(second) + sp.I * rational(third), rational(scalar) - sp.I * rational(first)],
        ]
    )


def _real_transition(quaternion: Quaternion, standard_doublets: int) -> RationalMatrix:
    return _block_diagonal((_identity(4), *(_left_quaternion_matrix(quaternion) for _ in range(standard_doublets))))


def _complex_transition(quaternion: Quaternion, standard_doublets: int) -> sp.Matrix:
    standard = _complex_standard_matrix(quaternion)
    return sp.diag(sp.eye(2), *(standard for _ in range(standard_doublets)))


def _transition_checks(standard_doublets: int) -> dict[str, Any]:
    quaternion_basis: tuple[Quaternion, ...] = (
        (Fraction(1), Fraction(0), Fraction(0), Fraction(0)),
        (Fraction(0), Fraction(1), Fraction(0), Fraction(0)),
        (Fraction(0), Fraction(0), Fraction(1), Fraction(0)),
        (Fraction(0), Fraction(0), Fraction(0), Fraction(1)),
    )
    real_homomorphism = all(
        _matrix_product(_left_quaternion_matrix(first), _left_quaternion_matrix(second))
        == _left_quaternion_matrix(_quaternion_multiply(first, second))
        for first, second in product(quaternion_basis, repeat=2)
    )
    complex_homomorphism = all(
        sp.simplify(_complex_standard_matrix(first) * _complex_standard_matrix(second))
        == _complex_standard_matrix(_quaternion_multiply(first, second))
        for first, second in product(quaternion_basis, repeat=2)
    )

    first: Quaternion = (Fraction(3, 5), Fraction(4, 5), Fraction(0), Fraction(0))
    second: Quaternion = (Fraction(5, 13), Fraction(0), Fraction(12, 13), Fraction(0))
    product_quaternion = _quaternion_multiply(first, second)
    _require(_quaternion_norm_squared(first) == 1, "first transition quaternion is not unit")
    _require(_quaternion_norm_squared(second) == 1, "second transition quaternion is not unit")
    _require(_quaternion_norm_squared(product_quaternion) == 1, "transition product is not unit")

    real_first = _real_transition(first, standard_doublets)
    real_second = _real_transition(second, standard_doublets)
    real_product = _real_transition(product_quaternion, standard_doublets)
    real_inverse = _real_transition(_quaternion_conjugate(first), standard_doublets)
    real_dimension = len(real_first)
    real_cocycle = _matrix_product(real_first, real_second) == real_product
    inverse_verified = _matrix_product(real_first, real_inverse) == _identity(real_dimension)

    complex_first = _complex_transition(first, standard_doublets)
    complex_second = _complex_transition(second, standard_doublets)
    complex_product = _complex_transition(product_quaternion, standard_doublets)
    complex_cocycle = sp.simplify(complex_first * complex_second - complex_product) == sp.zeros(complex_first.rows)
    complex_unitary = sp.simplify(complex_first.conjugate().T * complex_first) == sp.eye(complex_first.rows)
    complex_special = sp.simplify(complex_first.det()) == 1

    right_i = _right_quaternion_matrix((Fraction(0), Fraction(1), Fraction(0), Fraction(0)))
    right_j = _right_quaternion_matrix((Fraction(0), Fraction(0), Fraction(1), Fraction(0)))
    quaternionic_i = _block_diagonal(tuple(right_i for _ in range(standard_doublets + 1)))
    quaternionic_j = _block_diagonal(tuple(right_j for _ in range(standard_doublets + 1)))
    minus_identity = _matrix_scale(_identity(real_dimension), -1)
    zero_matrix = tuple(tuple(Fraction(0) for _ in range(real_dimension)) for _ in range(real_dimension))
    quaternionic_relations = (
        _matrix_product(quaternionic_i, quaternionic_i) == minus_identity
        and _matrix_product(quaternionic_j, quaternionic_j) == minus_identity
        and _matrix_add(
            _matrix_product(quaternionic_i, quaternionic_j),
            _matrix_product(quaternionic_j, quaternionic_i),
        )
        == zero_matrix
        and _matrix_product(real_first, quaternionic_i) == _matrix_product(quaternionic_i, real_first)
        and _matrix_product(real_first, quaternionic_j) == _matrix_product(quaternionic_j, real_first)
    )
    transition_pass = (
        standard_doublets == 3
        and real_dimension == REAL_RANK
        and complex_first.rows == COMPLEX_RANK
        and real_homomorphism
        and complex_homomorphism
        and real_cocycle
        and inverse_verified
        and complex_cocycle
        and complex_unitary
        and complex_special
        and quaternionic_relations
    )
    return {
        "chart_count": 7,
        "representation": "diag(I_2,Q,Q,Q)",
        "structure_group": "diagonal SU(2)=Sp(1) inside Sp(4) and SU(8)",
        "real_transition_dimension": real_dimension,
        "complex_transition_dimension": complex_first.rows,
        "quaternion_basis_homomorphism_real": real_homomorphism,
        "quaternion_basis_homomorphism_complex": complex_homomorphism,
        "cocycle_real": real_cocycle,
        "cocycle_complex": complex_cocycle,
        "inverse": inverse_verified,
        "unitary": complex_unitary,
        "determinant_one": complex_special,
        "quaternionic_structures_preserved": quaternionic_relations,
        "pass": transition_pass,
    }


def _trim_polynomial(polynomial: IntegerPolynomial) -> IntegerPolynomial:
    values = list(polynomial)
    while len(values) > 1 and values[-1] == 0:
        values.pop()
    return tuple(values)


def _shift_polynomial(polynomial: IntegerPolynomial, shift: int) -> IntegerPolynomial:
    """Substitute ``t=x+shift`` in an ascending-coefficient polynomial."""
    output = [0] * len(polynomial)
    for degree, coefficient in enumerate(polynomial):
        for selected_degree in range(degree + 1):
            output[selected_degree] += (
                coefficient * int(sp.binomial(degree, selected_degree)) * shift ** (degree - selected_degree)
            )
    return _trim_polynomial(tuple(output))


def _polynomial_add(first: IntegerPolynomial, second: IntegerPolynomial) -> IntegerPolynomial:
    degree_count = max(len(first), len(second))
    return _trim_polynomial(
        tuple(
            (first[degree] if degree < len(first) else 0) + (second[degree] if degree < len(second) else 0)
            for degree in range(degree_count)
        )
    )


def _polynomial_multiply(first: IntegerPolynomial, second: IntegerPolynomial) -> IntegerPolynomial:
    output = [0] * (len(first) + len(second) - 1)
    for first_degree, first_coefficient in enumerate(first):
        for second_degree, second_coefficient in enumerate(second):
            output[first_degree + second_degree] += first_coefficient * second_coefficient
    return _trim_polynomial(tuple(output))


def _octonion_block(matrix: RationalMatrix) -> RationalMatrix:
    return tuple(tuple(matrix[row][column] for column in range(8)) for row in range(8))


def _square_matrix_commutator(first: RationalMatrix, second: RationalMatrix) -> RationalMatrix:
    first_second = _matrix_product(first, second)
    second_first = _matrix_product(second, first)
    return tuple(
        tuple(left - right for left, right in zip(first_row, second_row, strict=True))
        for first_row, second_row in zip(first_second, second_first, strict=True)
    )


def _su2_character_polynomial(multiplicities: IntegerPolynomial) -> IntegerPolynomial:
    irreducibles: list[IntegerPolynomial] = [(1,)]
    if len(multiplicities) > 1:
        irreducibles.append((0, 1))
    for highest_weight in range(2, len(multiplicities)):
        irreducibles.append(
            _polynomial_add(
                _polynomial_multiply((0, 1), irreducibles[highest_weight - 1]),
                tuple(-coefficient for coefficient in irreducibles[highest_weight - 2]),
            )
        )
    character: IntegerPolynomial = (0,)
    for multiplicity, irreducible in zip(multiplicities, irreducibles, strict=True):
        character = _polynomial_add(character, tuple(multiplicity * coefficient for coefficient in irreducible))
    return character


def _casimir_restriction(
    derived_domains: Sequence[RationalMatrix], representation: Sequence[sp.Matrix]
) -> tuple[IntegerPolynomial, dict[str, int]]:
    killing_inverse = stabilizer._killing_matrix(derived_domains).inv()
    dimension = representation[0].rows
    casimir = sp.zeros(dimension)
    for row, left in enumerate(representation):
        for column, right in enumerate(representation):
            casimir += killing_inverse[row, column] * left * right
    eigenvalues = sp.simplify(casimir).eigenvals()
    multiplicities: dict[int, int] = {}
    for eigenvalue, eigenspace_dimension in eigenvalues.items():
        highest_weight = stabilizer._highest_weight(eigenvalue)
        irreducible_dimension = highest_weight + 1
        _require(
            eigenspace_dimension % irreducible_dimension == 0,
            "Casimir eigenspace dimension is not divisible by its irreducible dimension",
        )
        multiplicities[highest_weight] = eigenspace_dimension // irreducible_dimension
    restriction = tuple(multiplicities.get(highest_weight, 0) for highest_weight in range(max(multiplicities) + 1))
    _require(
        sum(coefficient * (degree + 1) for degree, coefficient in enumerate(restriction)) == dimension,
        "Casimir restriction does not recover the representation dimension",
    )
    spectrum = {sp.sstr(value): int(eigenspace_dimension) for value, eigenspace_dimension in eigenvalues.items()}
    return _trim_polynomial(restriction), spectrum


def _branching_certificate(mutation: str) -> dict[str, Any]:
    point = stabilizer._representative("Np")
    compact = stabilizer._compact_triples()
    compact_domains = [triple[1] for _name, triple in compact]
    stabilizer_coefficients = stabilizer._stabilizer_coefficients(point)
    stabilizer_domains = [
        stabilizer._linear_combination(coefficients, compact_domains) for coefficients in stabilizer_coefficients
    ]
    derived_domains = stabilizer._derived_basis(stabilizer_domains)
    derived_octonion_blocks = [_octonion_block(matrix) for matrix in derived_domains]
    fundamental_representation = [
        sp.Matrix([[matrix[row][column] for column in range(1, 8)] for row in range(1, 8)])
        for matrix in derived_octonion_blocks
    ]

    g2_octonion_blocks = [_octonion_block(matrix) for matrix in compact_domains[:14]]
    flattened_g2 = [stabilizer._flatten(matrix) for matrix in g2_octonion_blocks]
    adjoint_representation: list[sp.Matrix] = []
    for left in derived_octonion_blocks:
        columns = [
            stabilizer._coordinates(
                flattened_g2,
                stabilizer._flatten(_square_matrix_commutator(left, right)),
            )
            for right in g2_octonion_blocks
        ]
        adjoint_representation.append(
            sp.Matrix(
                14,
                14,
                lambda row, column, values=columns: stabilizer._sympy_rational(values[column][row]),
            )
        )

    measured_fundamental, fundamental_spectrum = _casimir_restriction(derived_domains, fundamental_representation)
    measured_adjoint, adjoint_spectrum = _casimir_restriction(derived_domains, adjoint_representation)
    downstream_fundamental_multiplicities = (5, 1) if mutation == "kill_k_theory_torsion" else measured_fundamental
    fundamental_character = _su2_character_polynomial(downstream_fundamental_multiplicities)
    adjoint_character = _su2_character_polynomial(measured_adjoint)
    return {
        "source_orbit": "N_+ representative",
        "derived_stabilizer_dimension": len(derived_domains),
        "casimir_normalization": "V_n has eigenvalue n(n+2)/8",
        "fundamental_7_casimir_spectrum": fundamental_spectrum,
        "adjoint_14_casimir_spectrum": adjoint_spectrum,
        "measured_fundamental_multiplicities": list(measured_fundamental),
        "measured_adjoint_multiplicities": list(measured_adjoint),
        "downstream_fundamental_multiplicities": list(downstream_fundamental_multiplicities),
        "downstream_fundamental_character_in_V1": list(fundamental_character),
        "downstream_adjoint_character_in_V1": list(adjoint_character),
        "mutation": mutation if mutation == "kill_k_theory_torsion" else "",
        "pass": mutation != "kill_k_theory_torsion"
        and len(derived_domains) == 3
        and measured_fundamental == (3, 2)
        and measured_adjoint == (3, 4, 1),
    }


def _representation_ring_checks(branching: dict[str, Any]) -> dict[str, Any]:
    fundamental_restriction = tuple(int(value) for value in branching["downstream_fundamental_character_in_V1"])
    adjoint_restriction = tuple(int(value) for value in branching["downstream_adjoint_character_in_V1"])
    fundamental_dimension = sum(coefficient * 2**degree for degree, coefficient in enumerate(fundamental_restriction))
    adjoint_dimension = sum(coefficient * 2**degree for degree, coefficient in enumerate(adjoint_restriction))
    fundamental_augmentation_relation = list(fundamental_restriction)
    fundamental_augmentation_relation[0] -= 7
    adjoint_augmentation_relation = list(adjoint_restriction)
    adjoint_augmentation_relation[0] -= 14
    first_koszul_relation = _shift_polynomial(tuple(fundamental_augmentation_relation), 2)
    second_koszul_relation = _shift_polynomial(tuple(adjoint_augmentation_relation), 2)
    _require(first_koszul_relation[0] == 0, "fundamental augmentation relation has nonzero rank")
    _require(second_koszul_relation[0] == 0, "adjoint augmentation relation has nonzero rank")
    torsion_order = abs(first_koszul_relation[1])
    second_relation_reduces_to_x_squared = (
        second_koszul_relation == (0, 8, 1) and torsion_order > 0 and 8 % torsion_order == 0
    )
    first_syzygy_component: IntegerPolynomial = (-8, -1)
    second_syzygy_component: IntegerPolynomial = (2,)
    syzygy_residual = _polynomial_add(
        _polynomial_multiply(first_koszul_relation, first_syzygy_component),
        _polynomial_multiply(second_koszul_relation, second_syzygy_component),
    )
    second_koszul_boundary = (
        tuple(-coefficient for coefficient in second_koszul_relation),
        first_koszul_relation,
    )
    syzygy_times_x = (
        _polynomial_multiply((0, 1), first_syzygy_component),
        _polynomial_multiply((0, 1), second_syzygy_component),
    )
    koszul_first_syzygy = (
        first_koszul_relation == (0, 2)
        and second_koszul_relation == (0, 8, 1)
        and syzygy_residual == (0,)
        and second_koszul_boundary == syzygy_times_x
    )
    representation_pass = (
        branching["pass"]
        and fundamental_dimension == 7
        and adjoint_dimension == 14
        and torsion_order == 2
        and second_relation_reduces_to_x_squared
        and koszul_first_syzygy
    )
    return {
        "representation_ring": "R(SU(2))=Z[t], t=V_1; x=t-2",
        "method": "Hodgkin Tor spectral sequence for simply connected G_2 and connected SU(2)",
        "restriction_of_g2_fundamental_7": ("3 V_0 + 2 V_1" if fundamental_restriction == (3, 2) else "5 V_0 + V_1"),
        "restriction_of_g2_adjoint_14": "3 V_0 + 4 V_1 + V_2",
        "fundamental_dimension": fundamental_dimension,
        "adjoint_dimension": adjoint_dimension,
        "koszul_relations": [
            "2x" if first_koszul_relation == (0, 2) else "x",
            "x^2+8x",
        ],
        "tor_0": "Z[x]/(2x,x^2)=Z + (Z/2)x" if torsion_order == 2 else "Z",
        "tor_1": ("Z generated by (-(x+8),2) modulo x multiples" if torsion_order == 2 else "not the baseline complex"),
        "tor_2": "0",
        "reduced_k0": "Z/2",
        "k1": "Z",
        "generator": "x=[xi]-2",
        "generator_nonzero": torsion_order == 2,
        "generator_order": torsion_order,
        "second_relation_reduces_to_x_squared": second_relation_reduces_to_x_squared,
        "first_syzygy_verified": syzygy_residual == (0,),
        "second_koszul_boundary_is_x_times_first_syzygy": second_koszul_boundary == syzygy_times_x,
        "pass": representation_pass,
    }


def _rank_one_cellular_groups(cell_degrees: list[int], boundary_by_source: dict[int, int]) -> dict[str, dict[str, str]]:
    homology: dict[str, str] = {}
    cohomology: dict[str, str] = {}
    cell_degree_set = set(cell_degrees)
    for degree in cell_degrees:
        homology_outgoing = boundary_by_source.get(degree, 0)
        homology_incoming = boundary_by_source.get(degree + 1, 0) if degree + 1 in cell_degree_set else 0
        _require(
            homology_outgoing == 0 or homology_incoming == 0,
            f"cellular boundary fails d^2=0 at degree {degree}",
        )
        if homology_outgoing == 0:
            homology[str(degree)] = "Z" if homology_incoming == 0 else f"Z/{abs(homology_incoming)}"

        cohomology_outgoing = boundary_by_source.get(degree + 1, 0) if degree + 1 in cell_degree_set else 0
        cohomology_incoming = boundary_by_source.get(degree, 0)
        if cohomology_outgoing == 0:
            cohomology[str(degree)] = "Z" if cohomology_incoming == 0 else f"Z/{abs(cohomology_incoming)}"
    return {
        "homology": {degree: group for degree, group in homology.items() if group != "Z/1"},
        "cohomology": {degree: group for degree, group in cohomology.items() if group != "Z/1"},
    }


def _base_topology_checks(mutation: str) -> dict[str, Any]:
    # The unit tangent sphere fibration S^5 -> S(TS^6) -> S^6 has Euler
    # boundary chi(S^6)=2.  Its standard product-cell filtration has one cell
    # in degrees 0,5,6,11 and the sole nonzero cellular boundary d_6=2.
    sphere_cell_degrees = [0] if mutation == "change_euler_boundary" else [0, 6]
    sphere_euler_characteristic = sum((-1) ** degree for degree in sphere_cell_degrees)
    cell_degrees = [0, 5, 6, 11]
    euler_boundary = abs(sphere_euler_characteristic)
    boundary_by_source = {6: euler_boundary}
    cellular_groups = _rank_one_cellular_groups(cell_degrees, boundary_by_source)
    integral_homology = cellular_groups["homology"]
    integral_cohomology = cellular_groups["cohomology"]
    topology_pass = (
        mutation != "change_euler_boundary"
        and cell_degrees == [0, 5, 6, 11]
        and boundary_by_source == {6: 2}
        and integral_homology == {"0": "Z", "5": "Z/2", "11": "Z"}
        and integral_cohomology == {"0": "Z", "6": "Z/2", "11": "Z"}
    )
    return {
        "base": "V_2(R^7)=S(TS^6)",
        "sphere_fibration": "S^5 -> V_2(R^7) -> S^6",
        "sphere_cell_degrees": sphere_cell_degrees,
        "sphere_euler_characteristic": sphere_euler_characteristic,
        "euler_boundary_derivation": "absolute Euler characteristic of the standard two-cell CW model of S^6",
        "euler_boundary": euler_boundary,
        "cell_degrees": cell_degrees,
        "cellular_boundary_maps": {"6_to_5": euler_boundary},
        "pi_1": "0",
        "integral_homology": integral_homology,
        "integral_cohomology": integral_cohomology,
        "positive_degree_cup_products": "zero by degree",
        "complex_k_ahss": "K^0=Z+(Z/2), K^1=Z; all differentials vanish by degree and torsion",
        "pass": topology_pass,
    }


def _load_inputs() -> tuple[dict[str, Any], dict[str, str]]:
    stabilizer_result = json.loads(STABILIZER_RESULT.read_text(encoding="utf-8"))
    stabilizer_script_digest = hashlib.sha256(STABILIZER_SCRIPT.read_bytes()).hexdigest()
    _require(stabilizer_result.get("pass") is True, "stabilizer result does not pass")
    _require(
        stabilizer_result.get("script_sha256") == stabilizer_script_digest,
        "stabilizer result is stale against its producer",
    )
    sedenion_result = json.loads(SEDENION_BUNDLE_RESULT.read_text(encoding="utf-8"))
    _require(
        sedenion_result.get("schema") == "sedenion-quaternion-bundle-atlas-v1",
        "sedenion bundle result has an unexpected schema",
    )
    return stabilizer_result, {
        "stabilizer_result_sha256": hashlib.sha256(STABILIZER_RESULT.read_bytes()).hexdigest(),
        "sedenion_bundle_script_sha256": hashlib.sha256(SEDENION_BUNDLE_SCRIPT.read_bytes()).hexdigest(),
        "sedenion_bundle_result_sha256": hashlib.sha256(SEDENION_BUNDLE_RESULT.read_bytes()).hexdigest(),
    }


def _fiber_classification(stabilizer_result: dict[str, Any], k_theory: dict[str, Any]) -> dict[str, Any]:
    rows = stabilizer_result["stabilizer_representation"]["rows"]
    restrictions = [row["su2_restriction"] for row in rows]
    expected_restriction = {"trivial_lines": 2, "standard_doublets": 3}
    _require(all(restriction == expected_restriction for restriction in restrictions), "unexpected SU(2) restriction")
    _require(
        rows[0]["irreducible_decomposition"] == rows[1]["irreducible_decomposition"],
        "the two components have different connected representations",
    )
    decomposition = rows[0]["irreducible_decomposition"]
    summands: list[dict[str, Any]] = []
    doublet_count = 0
    for representation in decomposition:
        highest_weight = int(representation["sl2_highest_weight"])
        multiplicity = int(representation["multiplicity"])
        central_weight = str(representation["central_weight"])
        central_weight_label = "-1" if central_weight == "-I" else central_weight.removesuffix("*I")
        if highest_weight == 0:
            stable_class = "0"
            stable_trivial = True
            actual_trivial = True
            ordinary_bundle = "C"
        elif highest_weight == 1:
            stable_class = "x"
            stable_trivial = False
            actual_trivial = False
            ordinary_bundle = "xi"
            doublet_count += multiplicity
        else:
            raise RuntimeError(f"unclassified SU(2) highest weight {highest_weight}")
        summands.append(
            {
                "representation": f"V_({highest_weight},{central_weight_label})",
                "multiplicity": multiplicity,
                "complex_rank_per_copy": highest_weight + 1,
                "ordinary_bundle_per_copy": ordinary_bundle,
                "c3_mod_2_per_copy": 0,
                "reduced_k_class_per_copy": stable_class,
                "complex_stably_trivial_per_copy": stable_trivial,
                "complex_actually_trivial_per_copy": actual_trivial,
            }
        )
    _require(doublet_count == 3, "fiber does not contain three standard doublets")
    total_reduced_class = doublet_count % int(k_theory["generator_order"])
    return {
        "ordinary_complex_bundle": "E_C=C^2+3 xi",
        "summands": summands,
        "total_c3_mod_2": 0,
        "total_w6": 0,
        "all_ordinary_chern_classes": "zero",
        "reduced_complex_k_group": "Z/2 generated by x=[xi]-2",
        "kernel_bundle_reduced_k_class": "3x=x != 0" if total_reduced_class else "0",
        "complex_stable_triviality": total_reduced_class == 0,
        "complex_triviality": "trivial" if total_reduced_class == 0 else "nontrivial",
        "quaternionic_bundle": "E_H=H+3 xi_H",
        "quaternionic_stable_triviality": False,
        "quaternionic_triviality": "nontrivial",
        "xi_real_stable_relation": "xi_R+R^4=R^8",
        "kernel_real_stable_relation": "E_R+R^12=R^28",
        "kernel_real_rank_exceeds_base_dimension": REAL_RANK > BASE_DIMENSION,
        "real_bundle": "trivial rank 16 by stable-range cancellation",
        "individual_xi_real_triviality": "not decided by the stable relation",
        "stiefel_whitney_classes_of_E_R": "all zero",
        "pontryagin_classes_of_E_R": "all zero",
        "euler_class_of_E_R": "zero because H^16(base)=0",
        "pass": total_reduced_class == 1,
    }


def bundle_checks(mutation: str = "") -> dict[str, Any]:
    if mutation not in ("", "drop_standard_doublet", "kill_k_theory_torsion", "change_euler_boundary"):
        raise ValueError(f"unknown mutation {mutation!r}")
    stabilizer_result, input_digests = _load_inputs()
    topology = _base_topology_checks(mutation)
    branching = _branching_certificate(mutation)
    k_theory = _representation_ring_checks(branching)
    fiber = _fiber_classification(stabilizer_result, k_theory)
    standard_doublets = 2 if mutation == "drop_standard_doublet" else 3
    transition = _transition_checks(standard_doublets)
    mutation_absent = mutation == ""
    return {
        "mutation": mutation,
        "components": [row["orbit"] for row in stabilizer_result["stabilizer_representation"]["rows"]],
        "input_digests": input_digests,
        "homogeneous_reduction": ("(G_2 x U(1)) x_(U(2)) V reduces along G_2 -> V_2(R^7) to G_2 x_(SU(2)) Res(V)"),
        "base_topology": topology,
        "branching": branching,
        "representation_ring_k_theory": k_theory,
        "transition": transition,
        "topology_and_characteristics": fiber,
        "pass": mutation_absent and topology["pass"] and k_theory["pass"] and transition["pass"] and fiber["pass"],
    }


def build_result() -> dict[str, Any]:
    result = bundle_checks()
    return {
        "schema": "a5-nullity-sixteen-bundle-invariants-v2",
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "bundle": result,
        "pass": result["pass"],
    }


def _self_test_mutation_task(mutation: str) -> tuple[str, dict[str, Any]]:
    """Build one independent bundle mutation for the parent self-test."""
    return mutation, bundle_checks(mutation)


def self_test() -> None:
    baseline = bundle_checks()
    if not baseline["pass"]:
        raise RuntimeError("baseline nullity-sixteen bundle invariant check failed")
    mutations = dict(
        stabilizer.symmetry.parallel.ordered_map(
            _self_test_mutation_task,
            ["drop_standard_doublet", "kill_k_theory_torsion", "change_euler_boundary"],
            min_items=1,
        )
    )
    rank_mutation = mutations["drop_standard_doublet"]
    if rank_mutation["pass"] or rank_mutation["transition"]["complex_transition_dimension"] == COMPLEX_RANK:
        raise RuntimeError("representation-rank mutation survived the invariant check")
    torsion_mutation = mutations["kill_k_theory_torsion"]
    if torsion_mutation["pass"] or torsion_mutation["representation_ring_k_theory"]["generator_nonzero"]:
        raise RuntimeError("K-theory torsion mutation survived the invariant check")
    topology_mutation = mutations["change_euler_boundary"]
    if topology_mutation["pass"] or topology_mutation["base_topology"]["integral_cohomology"].get("6") == "Z/2":
        raise RuntimeError("Euler-boundary mutation survived the invariant check")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--check", type=Path)
    parser.add_argument("--self-test", action="store_true")
    arguments = parser.parse_args()
    if arguments.check is not None and (arguments.self_test or arguments.out is not None):
        parser.error("--check cannot be combined with --self-test or --out")
    if arguments.self_test:
        self_test()
        print("PASS: nullity-sixteen bundle invariant self-test")
    if arguments.out is not None or arguments.check is not None:
        result = build_result()
        payload = (json.dumps(result, indent=2, sort_keys=True) + "\n").encode()
        if arguments.check is not None:
            if payload != arguments.check.read_bytes():
                raise SystemExit(f"nullity_sixteen_bundle.py: fresh JSON differs byte-for-byte from {arguments.check}")
            print(f"nullity_sixteen_bundle.py: fresh JSON matches {arguments.check}")
        else:
            arguments.out.write_bytes(payload)
            print(f"wrote {arguments.out}")
    if not arguments.self_test and arguments.out is None and arguments.check is None:
        parser.error("choose --self-test, --out, or --check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
