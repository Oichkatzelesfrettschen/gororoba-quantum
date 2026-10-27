"""Exact stabilizer and cellular inputs for the nullity-eight unit-section topology."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections.abc import Sequence
from fractions import Fraction
from pathlib import Path
from typing import Any, TypeAlias

import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
KERNEL_BUNDLES = HERE.parent / "a5-kernel-bundles"
REGULARITY = HERE.parent / "a5-strata-regularity"
EQUATIONS = HERE.parent / "a5-rank-strata-equations"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(KERNEL_BUNDLES))
sys.path.insert(0, str(REGULARITY))
sys.path.insert(0, str(EQUATIONS))
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import compact_orbit_ranks as compact_ranks  # noqa: E402
import kernel_symmetry as symmetry  # noqa: E402
import remaining_orbit_moduli as remaining_moduli  # noqa: E402
import stabilizer_fiber_samples as samples  # noqa: E402
import stabilizer_representation as stabilizer  # noqa: E402
import stabilizer_strata as strata  # noqa: E402
import strata_regularity as regularity  # noqa: E402
import verify_regularity_independent as independent  # noqa: E402

import parallel  # noqa: E402

SCHEMA = "a5-kernel-bundles-nullity8-unit-section-topology-v1"
ORBIT_NAMES = ("W8", "E8bar", "Iso", "X+", "X-")
REGULARITY_NAMES = {"W8": "W8", "E8bar": "Ehat", "Iso": "Iso", "X+": "Xp", "X-": "Xm"}
H_COMPLEX_DIMENSION = 16
FULL_COMPACT_DIMENSION = 16
SOURCE_PATHS = (
    HERE / "unit_section_topology.py",
    HERE / "compact_orbit_ranks.py",
    HERE / "remaining_orbit_moduli.py",
    HERE / "stabilizer_fiber_samples.py",
    HERE / "stabilizer_strata.py",
    HERE / "w8_orbit_moduli.py",
    KERNEL_BUNDLES / "nullity-sixteen-bundle-result.json",
    KERNEL_BUNDLES / "kernel_symmetry.py",
    REGULARITY / "strata_regularity.py",
    REGULARITY / "verify_regularity_independent.py",
)

RationalMatrix: TypeAlias = tuple[tuple[Fraction, ...], ...]
GaussianPoint: TypeAlias = tuple[independent.Gq, ...]
AbelianGroup: TypeAlias = tuple[int, tuple[int, ...]]
CompactFixture: TypeAlias = tuple[str, tuple[Fraction, ...], GaussianPoint, str]


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _zero_matrix(dimension: int) -> list[list[Fraction]]:
    return [[Fraction(0) for _column in range(dimension)] for _row in range(dimension)]


def _matrix_tuple(matrix: Sequence[Sequence[Fraction]]) -> RationalMatrix:
    return tuple(tuple(Fraction(entry) for entry in row) for row in matrix)


def _flatten(matrix: Sequence[Sequence[Fraction]]) -> tuple[Fraction, ...]:
    return tuple(entry for row in matrix for entry in row)


def _matrix_from_flat(vector: Sequence[Fraction], dimension: int) -> RationalMatrix:
    return tuple(
        tuple(Fraction(vector[row * dimension + column]) for column in range(dimension)) for row in range(dimension)
    )


def _linear_combination(coefficients: Sequence[Fraction], matrices: Sequence[RationalMatrix]) -> RationalMatrix:
    _require(len(coefficients) == len(matrices), "coefficient and matrix counts differ")
    dimension = len(matrices[0])
    output = _zero_matrix(dimension)
    for coefficient, matrix in zip(coefficients, matrices, strict=True):
        if coefficient:
            for row in range(dimension):
                for column in range(dimension):
                    output[row][column] += coefficient * matrix[row][column]
    return _matrix_tuple(output)


def _commutator(first: RationalMatrix, second: RationalMatrix) -> RationalMatrix:
    dimension = len(first)
    _require(len(second) == dimension, "commutator matrices have different dimensions")
    output = _zero_matrix(dimension)
    for row in range(dimension):
        for middle in range(dimension):
            if first[row][middle] or second[row][middle]:
                for column in range(dimension):
                    output[row][column] += (
                        first[row][middle] * second[middle][column] - second[row][middle] * first[middle][column]
                    )
    return _matrix_tuple(output)


def _independent_matrices(matrices: Sequence[RationalMatrix]) -> tuple[RationalMatrix, ...]:
    if not matrices:
        return ()
    dimension = len(matrices[0])
    independent = stabilizer._independent_vectors([_flatten(matrix) for matrix in matrices])
    return tuple(_matrix_from_flat(vector, dimension) for vector in independent)


def _in_span(matrix: RationalMatrix, basis: Sequence[RationalMatrix]) -> bool:
    if not basis:
        return not any(_flatten(matrix))
    flattened = [_flatten(value) for value in basis]
    return symmetry._rank([*flattened, _flatten(matrix)]) == len(flattened)


def _h_matrices() -> tuple[RationalMatrix, ...]:
    matrices: list[RationalMatrix] = []
    for derivation in regularity.DERS:
        matrix = _zero_matrix(15)
        for row in range(7):
            for column in range(7):
                matrix[row][column] = Fraction(derivation[row + 1][column + 1])
                matrix[row + 8][column + 8] = Fraction(derivation[row + 1][column + 1])
        matrices.append(_matrix_tuple(matrix))
    scaling = _zero_matrix(15)
    for index in range(15):
        scaling[index][index] = Fraction(1)
    matrices.append(_matrix_tuple(scaling))
    boost = _zero_matrix(15)
    for index in range(7):
        boost[index][index + 8] = Fraction(1)
        boost[index + 8][index] = Fraction(1)
    matrices.append(_matrix_tuple(boost))
    _require(len(matrices) == H_COMPLEX_DIMENSION, "the H action needs sixteen generators")
    return tuple(matrices)


H_MATRICES = _h_matrices()


def _stabilizer_basis(
    point: Sequence[Fraction],
) -> tuple[tuple[tuple[Fraction, ...], ...], tuple[RationalMatrix, ...]]:
    tangent_columns = [stabilizer._matrix_vector(matrix, point) for matrix in H_MATRICES]
    tangent_rows = [[tangent_columns[column][row] for column in range(H_COMPLEX_DIMENSION)] for row in range(15)]
    coefficients = tuple(tuple(row) for row in symmetry.equations.nullspace(tangent_rows))
    matrices = tuple(_linear_combination(row, H_MATRICES) for row in coefficients)
    return coefficients, matrices


def _killing_matrix(basis: Sequence[RationalMatrix]) -> sp.Matrix:
    flattened = [_flatten(matrix) for matrix in basis]
    adjoint: list[sp.Matrix] = []
    for left in basis:
        columns = [
            stabilizer._coordinates(
                flattened,
                _flatten(_commutator(left, right)),
            )
            for right in basis
        ]
        adjoint.append(
            sp.Matrix(
                len(basis),
                len(basis),
                lambda row, column, coordinates=columns: sp.Rational(
                    coordinates[column][row].numerator,
                    coordinates[column][row].denominator,
                ),
            )
        )
    return sp.Matrix(
        len(basis),
        len(basis),
        lambda row, column: sp.trace(adjoint[row] * adjoint[column]),
    )


def _fraction(value: sp.Expr) -> Fraction:
    rational = sp.Rational(value)
    return Fraction(int(rational.p), int(rational.q))


def _nilpotency_class(radical: Sequence[RationalMatrix]) -> int | None:
    if not radical:
        return 0
    current = tuple(radical)
    for nilpotency_class in range(1, len(radical) + 2):
        commutators = [_commutator(left, right) for left in radical for right in current]
        current = _independent_matrices(commutators)
        if not current:
            return nilpotency_class
    return None


def _complex_stabilizer_row(orbit_name: str) -> dict[str, Any]:
    regularity_name = REGULARITY_NAMES[orbit_name]
    point = tuple(Fraction(value) for value in independent.REPS[orbit_name])
    coefficients, basis = _stabilizer_basis(point)
    direct_tangents = regularity.h_generators(point)
    matrix_tangents = [list(stabilizer._matrix_vector(matrix, point)) for matrix in H_MATRICES]
    action_matches = direct_tangents == matrix_tangents
    killing = _killing_matrix(basis)
    killing_kernel_coordinates = [tuple(_fraction(value) for value in vector) for vector in killing.nullspace()]
    killing_radical = tuple(_linear_combination(row, basis) for row in killing_kernel_coordinates)
    killing_kernel_all_nilpotent = all(sp.Matrix(matrix).is_nilpotent() for matrix in killing_radical)
    unipotent_radical_dimension = len(killing_radical) if killing_kernel_all_nilpotent else 0
    external_projection_rank = symmetry._rank(
        [
            tuple(row[-2] for row in coefficients),
            tuple(row[-1] for row in coefficients),
        ]
    )
    radical_is_ideal = all(
        _in_span(_commutator(left, right), killing_radical) for left in basis for right in killing_radical
    )
    nilpotency_class = _nilpotency_class(killing_radical)
    orbit_dimension = regularity.DIMS[regularity_name]
    expected_stabilizer_dimension = H_COMPLEX_DIMENSION - orbit_dimension
    return {
        "orbit": orbit_name,
        "complex_orbit_dimension": orbit_dimension,
        "complex_stabilizer_dimension": len(coefficients),
        "expected_complex_stabilizer_dimension": expected_stabilizer_dimension,
        "h_action_implementations_match": action_matches,
        "killing_matrix_rank": killing.rank(),
        "killing_kernel_dimension": len(killing_radical),
        "killing_kernel_is_ideal": radical_is_ideal,
        "killing_kernel_nilpotency_class": nilpotency_class,
        "killing_kernel_all_matrices_nilpotent": killing_kernel_all_nilpotent,
        "unipotent_radical_dimension": unipotent_radical_dimension,
        "maximal_compact_dimension": len(basis) - unipotent_radical_dimension,
        "external_torus_projection_rank": external_projection_rank,
        "external_torus_projection_rows": [[str(row[-2]), str(row[-1])] for row in coefficients],
        "pass": (
            action_matches
            and len(coefficients) == expected_stabilizer_dimension
            and radical_is_ideal
            and nilpotency_class is not None
        ),
    }


def _gaussian_split_from_rational(point: Sequence[Fraction]) -> GaussianPoint:
    return tuple(independent.Gq(Fraction(value), Fraction(0)) for value in point)


def _real_from_gaussian_split(point: Sequence[independent.Gq]) -> tuple[Fraction, ...]:
    _require(len(point) == 15, "a split point needs fifteen coordinates")
    real_point = [Fraction(0)] * 32
    for index in range(1, 16):
        original = independent.i_pow(independent.popcount(index)) * point[index - 1]
        real_point[index] = original.re
        real_point[16 + index] = original.im
    return tuple(real_point)


def _compact_boost_tangent(point: Sequence[independent.Gq]) -> tuple[Fraction, ...]:
    imaginary_unit = independent.Gq(Fraction(0), Fraction(1))
    tangent = [independent.Gq(Fraction(0), Fraction(0)) for _index in range(15)]
    for index in range(7):
        tangent[index] = imaginary_unit * point[index + 8]
        tangent[index + 8] = imaginary_unit * point[index]
    return _real_from_gaussian_split(tangent)


def _compact_point(orbit_name: str) -> tuple[tuple[Fraction, ...], GaussianPoint, str]:
    if orbit_name in ("X+", "X-"):
        split_point = samples._mostow_x_core_split(orbit_name)
        return (
            samples._real_from_gaussian_split(split_point),
            split_point,
            "Mostow-adapted core point",
        )
    if orbit_name != "Iso":
        rational_point = tuple(Fraction(value) for value in independent.REPS[orbit_name])
        return (
            tuple(symmetry.equations.y_from_split(rational_point)),
            _gaussian_split_from_rational(rational_point),
            "representative",
        )
    quartets = strata._coassociative_quartets()
    _require(bool(quartets), "the coassociative enumeration is empty")
    _summary, real_point, split_point = strata._coassociative_candidate((quartets[0], 1))
    return tuple(real_point), tuple(split_point), "coassociative core point"


def _compact_fixtures() -> tuple[CompactFixture, ...]:
    return tuple((orbit_name, *_compact_point(orbit_name)) for orbit_name in ORBIT_NAMES)


def _compact_stabilizer_row(task: tuple[CompactFixture, str]) -> dict[str, Any]:
    fixture, mutation = task
    orbit_name, real_point, split_point, point_label = fixture
    if mutation not in ("", "delete_boost"):
        raise ValueError(f"unknown compact mutation {mutation!r}")
    compact = stabilizer._compact_triples()
    tangent_columns = [stabilizer._matrix_vector(triple[0], real_point) for _name, triple in compact]
    boost_tangent = _compact_boost_tangent(split_point)
    if mutation == "":
        tangent_columns.append(boost_tangent)
    generator_count = len(tangent_columns)
    tangent_rank = symmetry._rank(tangent_columns)
    tangent_rows = [[tangent_columns[column][row] for column in range(generator_count)] for row in range(32)]
    coefficients = tuple(tuple(row) for row in symmetry.equations.nullspace(tangent_rows))
    _k0_rank, k0_coefficients, _k0_base, _k0_domain = samples._compact_data(real_point, "")
    phase_projection_dimension = symmetry._rank([tuple(row[14] for row in coefficients)]) if coefficients else 0
    boost_projection_dimension = (
        symmetry._rank([tuple(row[15] for row in coefficients)])
        if coefficients and generator_count == FULL_COMPACT_DIMENSION
        else 0
    )
    external_projection_rank = (
        symmetry._rank(
            [
                tuple(row[14] for row in coefficients),
                tuple(row[15] for row in coefficients),
            ]
        )
        if coefficients and generator_count == FULL_COMPACT_DIMENSION
        else phase_projection_dimension
    )
    if len(k0_coefficients) == 3:
        compact_type = "SU(2)"
    elif len(k0_coefficients) == 1:
        compact_type = "U(1)"
    else:
        compact_type = "unclassified"
    return {
        "orbit": orbit_name,
        "point": point_label,
        "mutation": mutation or None,
        "compact_generator_count": generator_count,
        "full_compact_tangent_rank": tangent_rank,
        "compact_stabilizer_dimension": len(coefficients),
        "connected_compact_stabilizer": compact_type,
        "phase_projection_dimension": phase_projection_dimension,
        "boost_projection_dimension": boost_projection_dimension,
        "external_torus_projection_rank": external_projection_rank,
        "external_torus_projection_rows": (
            [[str(row[14]), str(row[15])] for row in coefficients]
            if generator_count == FULL_COMPACT_DIMENSION
            else [[str(row[14])] for row in coefficients]
        ),
        "boost_adds_tangent_dimension": tangent_rank > _k0_rank,
        "pass": compact_type in ("SU(2)", "U(1)"),
    }


def _linear_vector(*terms: tuple[sp.Expr, Sequence[sp.Expr]]) -> tuple[sp.Expr, ...]:
    return tuple(
        sum((coefficient * vector[index] for coefficient, vector in terms), sp.Integer(0)) for index in range(7)
    )


def _external_invariant_differences(real_point: Sequence[Fraction], orbit_name: str) -> dict[str, sp.Expr]:
    phase_real, phase_imaginary, boost_real, boost_imaginary = sp.symbols("a b c d", real=True)
    state = remaining_moduli._state_from_real_coordinates(real_point)
    first_real, first_imaginary, second_real, second_imaginary = remaining_moduli._frame(state)
    boosted_first_real = _linear_vector((boost_real, first_real), (boost_imaginary, second_real))
    boosted_first_imaginary = _linear_vector((boost_real, first_imaginary), (boost_imaginary, second_imaginary))
    boosted_second_real = _linear_vector((-boost_imaginary, first_real), (boost_real, second_real))
    boosted_second_imaginary = _linear_vector((-boost_imaginary, first_imaginary), (boost_real, second_imaginary))
    transformed_frame = (
        _linear_vector((phase_real, boosted_first_real), (-phase_imaginary, boosted_first_imaginary)),
        _linear_vector((phase_imaginary, boosted_first_real), (phase_real, boosted_first_imaginary)),
        _linear_vector((phase_real, boosted_second_real), (-phase_imaginary, boosted_second_imaginary)),
        _linear_vector((phase_imaginary, boosted_second_real), (phase_real, boosted_second_imaginary)),
    )
    transformed_state = tuple(
        [
            *(coordinate for vector in transformed_frame for coordinate in vector),
            phase_real * state[28] - phase_imaginary * state[29],
            phase_imaginary * state[28] + phase_real * state[29],
        ]
    )
    return {
        name: sp.expand(function(transformed_state) - function(state))
        for name, function in remaining_moduli._invariant_functions(orbit_name, "")
    }


def _remainder(expression: sp.Expr, relations: Sequence[sp.Expr]) -> sp.Expr:
    phase_real, phase_imaginary, boost_real, boost_imaginary = sp.symbols("a b c d", real=True)
    basis = sp.groebner(relations, phase_real, phase_imaginary, boost_real, boost_imaginary)
    return sp.factor(basis.reduce(sp.expand(expression))[1])


def _all_zero(expressions: Sequence[sp.Expr], relations: Sequence[sp.Expr]) -> bool:
    return all(_remainder(expression, relations) == 0 for expression in expressions)


def _external_component_row(task: tuple[CompactFixture, dict[str, Any]]) -> dict[str, Any]:
    fixture, compact_row = task
    orbit_name, real_point, _split_point, point_label = fixture
    differences = _external_invariant_differences(real_point, orbit_name)
    phase_real, phase_imaginary, boost_real, boost_imaginary = sp.symbols("a b c d", real=True)
    circle_relations = (
        phase_real**2 + phase_imaginary**2 - 1,
        boost_real**2 + boost_imaginary**2 - 1,
    )
    decisive: dict[str, str]
    if orbit_name == "W8":
        gram_remainder = _remainder(differences["gram_11"], circle_relations)
        branch_relations = (boost_real**2 + boost_imaginary**2 - 1,)
        branches_preserve_all = all(
            _all_zero(
                [expression.subs({phase_real: phase_sign, phase_imaginary: 0}) for expression in differences.values()],
                branch_relations,
            )
            for phase_sign in (-1, 1)
        )
        decisive = {"gram_11_remainder": sp.sstr(gram_remainder)}
        external_image = "{phase=+1,phase=-1} x S^1_boost"
        component_group = "Z/2"
        certificate_pass = gram_remainder == phase_imaginary**2 and branches_preserve_all
        image_connected = False
    elif orbit_name == "E8bar":
        phase_fixed_differences = {
            name: sp.expand(expression.subs({phase_real: 1, phase_imaginary: 0}))
            for name, expression in differences.items()
        }
        boost_relation = (boost_real**2 + boost_imaginary**2 - 1,)
        gram_remainder = _remainder(phase_fixed_differences["gram_14"], boost_relation)
        form_remainder = _remainder(phase_fixed_differences["phi_123"], boost_relation)
        decisive = {
            "mu_real_difference": sp.sstr(sp.factor(differences["mu_real"])),
            "mu_imaginary_difference": sp.sstr(sp.factor(differences["mu_imaginary"])),
            "gram_14_remainder_after_phase_fixing": sp.sstr(gram_remainder),
            "phi_123_remainder_after_phase_fixing": sp.sstr(form_remainder),
        }
        external_image = "identity"
        component_group = "0"
        certificate_pass = (
            differences["mu_real"] == -4 * phase_imaginary
            and differences["mu_imaginary"] == 4 * (phase_real - 1)
            and gram_remainder == 15 * boost_imaginary**2
            and form_remainder == boost_real - 1
            and all(
                expression.subs({phase_real: 1, phase_imaginary: 0, boost_real: 1, boost_imaginary: 0}) == 0
                for expression in differences.values()
            )
        )
        image_connected = True
    elif orbit_name == "Iso":
        all_torus_preserves = _all_zero(list(differences.values()), circle_relations)
        decisive = {"all_invariant_remainders_vanish": str(all_torus_preserves).lower()}
        external_image = "S^1_phase x S^1_boost"
        component_group = "0"
        certificate_pass = all_torus_preserves
        image_connected = True
    else:
        branch_sign = 1 if orbit_name == "X+" else -1
        normal_equation = phase_real * boost_imaginary + branch_sign * phase_imaginary * boost_real
        graph_equation = phase_real * boost_real - branch_sign * phase_imaginary * boost_imaginary - 1
        phi_123_remainder = _remainder(differences["phi_123"], circle_relations)
        phi_124_remainder = _remainder(differences["phi_124"], circle_relations)
        graph_substitution = {
            boost_real: phase_real,
            boost_imaginary: -phase_imaginary if orbit_name == "X+" else phase_imaginary,
        }
        graph_preserves_all = _all_zero(
            [expression.subs(graph_substitution) for expression in differences.values()],
            (phase_real**2 + phase_imaginary**2 - 1,),
        )
        decisive = {
            "phi_123_remainder": sp.sstr(phi_123_remainder),
            "phi_124_remainder": sp.sstr(phi_124_remainder),
        }
        external_image = "phase+boost=0 graph circle" if orbit_name == "X+" else "boost-phase=0 graph circle"
        component_group = "0"
        expected_phi_124 = -2 * graph_equation if orbit_name == "X+" else 2 * graph_equation
        certificate_pass = (
            sp.expand(phi_123_remainder - 2 * normal_equation) == 0
            and sp.expand(phi_124_remainder - expected_phi_124) == 0
            and graph_preserves_all
        )
        image_connected = True
    pointwise_compact_fiber_connected = compact_row["connected_compact_stabilizer"] in ("SU(2)", "U(1)")
    return {
        "orbit": orbit_name,
        "point": point_label,
        "complete_invariant_count": len(differences),
        "external_image": external_image,
        "external_image_connected": image_connected,
        "pointwise_compact_fiber_connected": pointwise_compact_fiber_connected,
        "pointwise_compact_fiber_source": compact_row["connected_compact_stabilizer"],
        "component_group": component_group,
        "decisive_invariant_identities": decisive,
        "pass": certificate_pass and pointwise_compact_fiber_connected,
    }


def _format_group(group: AbelianGroup) -> str:
    free_rank, torsion = group
    terms: list[str] = []
    if free_rank == 1:
        terms.append("Z")
    elif free_rank > 1:
        terms.append(f"Z^{free_rank}")
    for modulus in torsion:
        terms.append(f"Z/{modulus}")
    return " + ".join(terms) if terms else "0"


def _cellular_cohomology(
    cell_degrees: Sequence[int], boundaries: dict[tuple[int, int], int]
) -> dict[int, AbelianGroup]:
    groups: dict[int, AbelianGroup] = {}
    degree_set = set(cell_degrees)
    for degree in sorted(degree_set):
        outgoing = boundaries.get((degree + 1, degree), 0) if degree + 1 in degree_set else 0
        incoming = boundaries.get((degree, degree - 1), 0) if degree - 1 in degree_set else 0
        if outgoing:
            continue
        if incoming == 0:
            groups[degree] = (1, ())
        elif abs(incoming) > 1:
            groups[degree] = (0, (abs(incoming),))
    return groups


def _product_with_free_cohomology(
    first: dict[int, AbelianGroup], second_free_ranks: dict[int, int]
) -> dict[int, AbelianGroup]:
    output: dict[int, AbelianGroup] = {}
    for first_degree, (first_free, first_torsion) in first.items():
        for second_degree, second_rank in second_free_ranks.items():
            degree = first_degree + second_degree
            old_free, old_torsion = output.get(degree, (0, ()))
            output[degree] = (
                old_free + first_free * second_rank,
                tuple([*old_torsion, *(first_torsion * second_rank)]),
            )
    return output


def _graded_k_product(
    first_k0: AbelianGroup,
    first_k1: AbelianGroup,
    second_k0_rank: int,
    second_k1_rank: int,
) -> tuple[AbelianGroup, AbelianGroup]:
    def repeated_sum(parts: Sequence[tuple[AbelianGroup, int]]) -> AbelianGroup:
        free_rank = sum(group[0] * multiplicity for group, multiplicity in parts)
        torsion = tuple(
            modulus for group, multiplicity in parts for _copy in range(multiplicity) for modulus in group[1]
        )
        return free_rank, torsion

    k0 = repeated_sum(((first_k0, second_k0_rank), (first_k1, second_k1_rank)))
    k1 = repeated_sum(((first_k0, second_k1_rank), (first_k1, second_k0_rank)))
    return k0, k1


def _topology_inputs(stiefel_boundary: int) -> dict[str, Any]:
    stiefel_cells = (0, 5, 6, 11)
    stiefel_cohomology = _cellular_cohomology(stiefel_cells, {(6, 5): stiefel_boundary})
    torus_cohomology = {0: 1, 1: 2, 2: 1}
    stiefel_torus_cohomology = _product_with_free_cohomology(stiefel_cohomology, torus_cohomology)
    stiefel_circle_cohomology = _product_with_free_cohomology(stiefel_cohomology, {0: 1, 1: 1})
    stiefel_k0: AbelianGroup = (1, (stiefel_boundary,)) if stiefel_boundary > 1 else (1, ())
    stiefel_k1: AbelianGroup = (1, ())
    stiefel_torus_k0, stiefel_torus_k1 = _graded_k_product(stiefel_k0, stiefel_k1, 2, 2)
    stiefel_circle_k0, stiefel_circle_k1 = _graded_k_product(stiefel_k0, stiefel_k1, 1, 1)

    g2_cells = (0, 3, 5, 6, 8, 9, 11, 14)
    g2_cohomology = _cellular_cohomology(g2_cells, {(6, 5): 2, (9, 8): 2})

    authority = json.loads((KERNEL_BUNDLES / "nullity-sixteen-bundle-result.json").read_text())
    authority_topology = authority["bundle"]["base_topology"]
    authority_cohomology = {int(degree): value for degree, value in authority_topology["integral_cohomology"].items()}
    computed_stiefel = {degree: _format_group(group) for degree, group in stiefel_cohomology.items()}
    authority_matches = (
        authority_topology["euler_boundary"] == stiefel_boundary
        and authority_cohomology == computed_stiefel
        and authority_topology["pi_1"] == "0"
    )
    return {
        "stiefel_factor": {
            "space": "V_2(R^7)",
            "cell_degrees": list(stiefel_cells),
            "cellular_boundary_6_to_5": stiefel_boundary,
            "integral_cohomology": computed_stiefel,
            "K0": _format_group(stiefel_k0),
            "K1": _format_group(stiefel_k1),
            "authority_matches": authority_matches,
        },
        "stiefel_times_torus": {
            "space": "V_2(R^7) x T^2",
            "pi_1": "Z^2",
            "integral_cohomology": {degree: _format_group(group) for degree, group in stiefel_torus_cohomology.items()},
            "K0": _format_group(stiefel_torus_k0),
            "K1": _format_group(stiefel_torus_k1),
            "reduced_K0": _format_group((stiefel_torus_k0[0] - 1, stiefel_torus_k0[1])),
        },
        "stiefel_times_circle": {
            "space": "V_2(R^7) x S^1",
            "pi_1": "Z",
            "integral_cohomology": {
                degree: _format_group(group) for degree, group in stiefel_circle_cohomology.items()
            },
            "K0": _format_group(stiefel_circle_k0),
            "K1": _format_group(stiefel_circle_k1),
            "reduced_K0": _format_group((stiefel_circle_k0[0] - 1, stiefel_circle_k0[1])),
        },
        "g2": {
            "space": "G_2",
            "pi_1": "0",
            "g2_cell_degrees": list(g2_cells),
            "g2_cellular_boundaries": {"6_to_5": 2, "9_to_8": 2},
            "integral_cohomology": {degree: _format_group(group) for degree, group in g2_cohomology.items()},
            "K0": "Z^2",
            "K1": "Z^2",
            "reduced_K0": "Z",
            "K_theory_input": "Hodgkin gives K^0(G_2)=K^1(G_2)=Z^2",
        },
    }


def _core_record(task: tuple[str, tuple[CompactFixture, ...]]) -> dict[str, Any]:
    mutation, compact_fixtures = task
    if mutation not in ("", "delete_boost", "stiefel_euler_boundary_one"):
        raise ValueError(f"unknown mutation {mutation!r}")
    compact_mutation = "delete_boost" if mutation == "delete_boost" else ""
    stiefel_boundary = 1 if mutation == "stiefel_euler_boundary_one" else 2
    complex_rows = parallel.ordered_map(_complex_stabilizer_row, list(ORBIT_NAMES), min_items=1)
    compact_rows = parallel.ordered_map(
        _compact_stabilizer_row,
        [(fixture, compact_mutation) for fixture in compact_fixtures],
        min_items=1,
    )
    complex_by_orbit = {row["orbit"]: row for row in complex_rows}
    compact_by_orbit = {row["orbit"]: row for row in compact_rows}
    component_rows = parallel.ordered_map(
        _external_component_row,
        [(fixture, compact_by_orbit[fixture[0]]) for fixture in compact_fixtures],
        min_items=1,
    )
    components_by_orbit = {row["orbit"]: row for row in component_rows}
    orbit_models = []
    for orbit_name in ORBIT_NAMES:
        complex_row = complex_by_orbit[orbit_name]
        compact_row = compact_by_orbit[orbit_name]
        component_row = components_by_orbit[orbit_name]
        observed_compact_dimension = int(compact_row["compact_stabilizer_dimension"])
        maximal_compact_dimension = int(complex_row["maximal_compact_dimension"])
        external_torus_rank = int(complex_row["external_torus_projection_rank"])
        has_su2_factor = compact_row["connected_compact_stabilizer"] == "SU(2)"
        remaining_torus_rank = 2 - external_torus_rank
        expected_compact_dimension = (3 if has_su2_factor else 0) + external_torus_rank
        if has_su2_factor and remaining_torus_rank == 2:
            core = "V_2(R^7) x T^2"
            core_dimension = 13
        elif has_su2_factor and remaining_torus_rank == 1:
            core = "V_2(R^7) x S^1"
            core_dimension = 12
        elif not has_su2_factor and remaining_torus_rank == 0:
            core = "G_2"
            core_dimension = 14
        else:
            core = "unclassified"
            core_dimension = FULL_COMPACT_DIMENSION - maximal_compact_dimension
        orbit_models.append(
            {
                "orbit": orbit_name,
                "unit_section_dimension": compact_ranks.UNIT_SECTION_DIMENSIONS[orbit_name],
                "maximal_compact_core": core,
                "core_dimension": core_dimension,
                "observed_compact_stabilizer_dimension_at_fixture": observed_compact_dimension,
                "maximal_compact_stabilizer_dimension": maximal_compact_dimension,
                "external_torus_projection_rank": external_torus_rank,
                "remaining_external_torus_rank": remaining_torus_rank,
                "expected_compact_stabilizer_dimension": expected_compact_dimension,
                "fixture_is_mostow_adapted": observed_compact_dimension == maximal_compact_dimension,
                "compact_stabilizer_component_group": component_row["component_group"],
                "core_construction": (
                    "mapping torus of V_2(R^7) with identity monodromy"
                    if orbit_name == "W8"
                    else "connected maximal-compact homogeneous quotient"
                ),
                "pass": (
                    maximal_compact_dimension == expected_compact_dimension
                    and core != "unclassified"
                    and core_dimension == FULL_COMPACT_DIMENSION - maximal_compact_dimension
                    and component_row["pass"]
                ),
            }
        )
    topology = _topology_inputs(stiefel_boundary)
    return {
        "mutation": mutation or None,
        "complex_stabilizers": complex_rows,
        "compact_stabilizers": compact_rows,
        "compact_stabilizer_components": component_rows,
        "orbit_models": orbit_models,
        "topology_inputs": topology,
        "pass": (
            all(row["pass"] for row in complex_rows)
            and all(row["pass"] for row in compact_rows)
            and all(row["pass"] for row in component_rows)
            and all(row["pass"] for row in orbit_models)
            and all(row["compact_generator_count"] == FULL_COMPACT_DIMENSION for row in compact_rows)
            and topology["stiefel_factor"]["authority_matches"]
        ),
    }


def _core_record_task(task: tuple[str, tuple[CompactFixture, ...]]) -> tuple[str, dict[str, Any]]:
    mutation, _compact_fixtures_value = task
    return mutation, _core_record(task)


def build_record() -> dict[str, Any]:
    compact_fixtures = _compact_fixtures()
    records = dict(
        parallel.ordered_map(
            _core_record_task,
            [(mutation, compact_fixtures) for mutation in ("", "delete_boost", "stiefel_euler_boundary_one")],
            min_items=1,
        )
    )
    baseline = records[""]
    mutations = [records["delete_boost"], records["stiefel_euler_boundary_one"]]
    mutation_control = {
        "delete_boost": {
            "detected": not mutations[0]["pass"],
            "compact_ranks_changed": [row["full_compact_tangent_rank"] for row in mutations[0]["compact_stabilizers"]]
            != [row["full_compact_tangent_rank"] for row in baseline["compact_stabilizers"]],
        },
        "stiefel_euler_boundary_one": {
            "detected": not mutations[1]["pass"],
            "downstream_cohomology_changed": (
                mutations[1]["topology_inputs"]["stiefel_times_torus"]["integral_cohomology"]
                != baseline["topology_inputs"]["stiefel_times_torus"]["integral_cohomology"]
            ),
        },
    }
    return {
        "schema": SCHEMA,
        "inputs": {str(path.relative_to(ROOT)): _sha256(path) for path in SOURCE_PATHS},
        **baseline,
        "topology_status": (
            "inferred from the exact stabilizer data by radial normalization and the Mostow homogeneous-space "
            "deformation theorem; the cellular and Kunneth group calculations are executable inputs"
        ),
        "mutation_control": mutation_control,
        "pass": (
            baseline["pass"]
            and mutation_control["delete_boost"]["detected"]
            and mutation_control["delete_boost"]["compact_ranks_changed"]
            and mutation_control["stiefel_euler_boundary_one"]["detected"]
            and mutation_control["stiefel_euler_boundary_one"]["downstream_cohomology_changed"]
        ),
    }


def self_test() -> None:
    record = build_record()
    _require(record["pass"], "baseline unit-section topology inputs failed")
    _require(record["mutation_control"]["delete_boost"]["detected"], "boost deletion survived")
    _require(
        record["mutation_control"]["stiefel_euler_boundary_one"]["detected"],
        "Stiefel boundary mutation survived",
    )


def _record_bytes(record: dict[str, Any]) -> bytes:
    return (json.dumps(record, indent=2, sort_keys=True) + "\n").encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    output = parser.add_mutually_exclusive_group()
    output.add_argument("--out", type=Path)
    output.add_argument("--check", type=Path)
    parser.add_argument("--self-test", action="store_true")
    arguments = parser.parse_args()
    if arguments.self_test:
        self_test()
    if arguments.out is not None:
        arguments.out.write_bytes(_record_bytes(build_record()))
    if arguments.check is not None:
        expected = arguments.check.read_bytes()
        actual = _record_bytes(build_record())
        _require(actual == expected, f"record differs from {arguments.check}")
    if not arguments.self_test and arguments.out is None and arguments.check is None:
        parser.error("select --out, --check, or --self-test")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
