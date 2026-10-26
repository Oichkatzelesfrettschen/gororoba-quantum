"""Exact stabilizer representations on the aligned nullity-twelve fibers.

The aligned pieces ``V^a_+`` and ``V^a_-`` have principal compact stabilizer
``SU(2)`` and a collinear endpoint with stabilizer algebra ``su(3)``.  This
replay restricts the compact symmetry lifts to the complex kernel defined by
``J=L_(e_16)``, decomposes the rank-six fibers, and compares their limit with
the rank-eight nullity-sixteen boundary representation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections.abc import Sequence
from fractions import Fraction
from pathlib import Path
from typing import Any

import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import aligned_orbit_moduli as aligned  # noqa: E402
import kernel_symmetry as symmetry  # noqa: E402
import stabilizer_representation as stabilizer  # noqa: E402

from cd_core import left_mult_matrix_exact  # noqa: E402

DIMENSION = 32
COMPACT_GENERATOR_COUNT = 15
ALIGNED_RESULT = HERE / "aligned-orbit-moduli-result.json"
ALIGNED_SCRIPT = HERE / "aligned_orbit_moduli.py"
NULLITY_SIXTEEN_RESULT = HERE / "stabilizer-result.json"
NULLITY_SIXTEEN_SCRIPT = HERE / "stabilizer_representation.py"

RationalMatrix = symmetry.RationalMatrix


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _sympy_rational(value: Fraction) -> sp.Rational:
    return sp.Rational(value.numerator, value.denominator)


def _flatten(matrix: RationalMatrix) -> tuple[Fraction, ...]:
    return tuple(entry for row in matrix for entry in row)


def _matrix_from_flat(values: Sequence[Fraction]) -> RationalMatrix:
    _require(len(values) == DIMENSION * DIMENSION, "flattened matrix has the wrong size")
    return tuple(
        tuple(Fraction(values[row * DIMENSION + column]) for column in range(DIMENSION)) for row in range(DIMENSION)
    )


def _adapted_kernel_basis(
    left_matrix: RationalMatrix,
    complex_structure: RationalMatrix,
    expected_real_nullity: int,
) -> tuple[tuple[Fraction, ...], ...]:
    kernel_basis = [tuple(vector) for vector in symmetry.equations.nullspace(left_matrix)]
    _require(
        len(kernel_basis) == expected_real_nullity,
        f"representative has real nullity {len(kernel_basis)}, not {expected_real_nullity}",
    )
    adapted: list[tuple[Fraction, ...]] = []
    for candidate in kernel_basis:
        partner = stabilizer._matrix_vector(complex_structure, candidate)
        if symmetry._rank([*adapted, candidate, partner]) == len(adapted) + 2:
            adapted.extend((candidate, partner))
    _require(len(adapted) == expected_real_nullity, "J-adapted basis does not span the real kernel")
    return tuple(adapted)


def _fiber_matrix(
    domain: RationalMatrix,
    adapted_basis: Sequence[Sequence[Fraction]],
    complex_structure: RationalMatrix,
) -> sp.Matrix:
    complex_dimension = len(adapted_basis) // 2
    matrix = sp.zeros(complex_dimension)
    for source_index in range(complex_dimension):
        source = adapted_basis[2 * source_index]
        partner = adapted_basis[2 * source_index + 1]
        image = stabilizer._matrix_vector(domain, source)
        partner_image = stabilizer._matrix_vector(domain, partner)
        expected_partner_image = stabilizer._matrix_vector(complex_structure, image)
        _require(partner_image == expected_partner_image, "stabilizer action fails to commute with J")
        coordinates = stabilizer._coordinates(adapted_basis, image)
        for target_index in range(complex_dimension):
            real_coefficient = coordinates[2 * target_index]
            imaginary_coefficient = coordinates[2 * target_index + 1]
            matrix[target_index, source_index] = _sympy_rational(real_coefficient) + sp.I * _sympy_rational(
                imaginary_coefficient
            )
    return matrix


def _derived_basis(stabilizer_domains: Sequence[RationalMatrix]) -> tuple[RationalMatrix, ...]:
    commutators = [
        symmetry._matrix_commutator(stabilizer_domains[first], stabilizer_domains[second])
        for first in range(len(stabilizer_domains))
        for second in range(first + 1, len(stabilizer_domains))
    ]
    independent = stabilizer._independent_vectors([_flatten(matrix) for matrix in commutators])
    return tuple(_matrix_from_flat(vector) for vector in independent)


def _casimir(
    derived_domains: Sequence[RationalMatrix],
    adapted_basis: Sequence[Sequence[Fraction]],
    complex_structure: RationalMatrix,
) -> tuple[sp.Matrix, sp.Matrix]:
    represented = [_fiber_matrix(domain, adapted_basis, complex_structure) for domain in derived_domains]
    killing = stabilizer._killing_matrix(derived_domains)
    killing_inverse = killing.inv()
    complex_dimension = len(adapted_basis) // 2
    casimir = sp.zeros(complex_dimension)
    for row, left in enumerate(represented):
        for column, right in enumerate(represented):
            casimir += killing_inverse[row, column] * left * right
    return sp.simplify(casimir), killing


def _commutant_basis(representation: Sequence[sp.Matrix]) -> list[sp.Matrix]:
    complex_dimension = representation[0].rows
    variables = sp.symbols(f"x:{complex_dimension * complex_dimension}")
    candidate = sp.Matrix(complex_dimension, complex_dimension, variables)
    equations: list[sp.Expr] = []
    for generator in representation:
        equations.extend(generator * candidate - candidate * generator)
    coefficient_matrix, _right_hand_side = sp.linear_eq_to_matrix(equations, variables)
    return [sp.Matrix(complex_dimension, complex_dimension, vector) for vector in coefficient_matrix.nullspace()]


def _representation_commutators_match(
    stabilizer_domains: Sequence[RationalMatrix],
    fiber_matrices: Sequence[sp.Matrix],
    adapted_basis: Sequence[Sequence[Fraction]],
    complex_structure: RationalMatrix,
) -> bool:
    complex_dimension = len(adapted_basis) // 2
    return all(
        sp.simplify(
            fiber_matrices[first] * fiber_matrices[second]
            - fiber_matrices[second] * fiber_matrices[first]
            - _fiber_matrix(
                symmetry._matrix_commutator(stabilizer_domains[first], stabilizer_domains[second]),
                adapted_basis,
                complex_structure,
            )
        )
        == sp.zeros(complex_dimension)
        for first in range(len(stabilizer_domains))
        for second in range(first + 1, len(stabilizer_domains))
    )


def _casimir_spectrum(casimir: sp.Matrix) -> dict[str, int]:
    return {sp.sstr(eigenvalue): multiplicity for eigenvalue, multiplicity in casimir.eigenvals().items()}


def _su2_certificate(casimir: sp.Matrix, expected_doublets: int) -> dict[str, Any]:
    complex_dimension = casimir.rows
    expected_standard_dimension = 2 * expected_doublets
    spectrum = casimir.eigenvals()
    matches = spectrum == {sp.Integer(0): 2, sp.Rational(3, 8): expected_standard_dimension}
    trivial_projector = sp.simplify(sp.eye(complex_dimension) - sp.Rational(8, 3) * casimir)
    standard_projector = sp.simplify(sp.Rational(8, 3) * casimir)
    zero_matrix = sp.zeros(complex_dimension)
    projector_checks = (
        sp.simplify(trivial_projector * trivial_projector - trivial_projector) == zero_matrix
        and sp.simplify(standard_projector * standard_projector - standard_projector) == zero_matrix
        and sp.simplify(trivial_projector * standard_projector) == zero_matrix
        and sp.simplify(trivial_projector + standard_projector) == sp.eye(complex_dimension)
        and trivial_projector.rank() == 2
        and standard_projector.rank() == expected_standard_dimension
    )
    return {
        "decomposition": f"2 V_0 + {expected_doublets} V_1",
        "trivial_lines": 2,
        "standard_doublets": expected_doublets,
        "casimir_spectrum": _casimir_spectrum(casimir),
        "isotypic_projector_ranks": [trivial_projector.rank(), standard_projector.rank()],
        "pass": matches and projector_checks,
    }


def _invariant_symmetric_pairing(representation: Sequence[sp.Matrix]) -> tuple[sp.Matrix, int]:
    complex_dimension = representation[0].rows
    variables: list[sp.Symbol] = []
    positions: dict[tuple[int, int], int] = {}
    for row in range(complex_dimension):
        for column in range(row, complex_dimension):
            positions[row, column] = len(variables)
            positions[column, row] = len(variables)
            variables.append(sp.Symbol(f"b{len(variables)}"))
    candidate = sp.Matrix(
        complex_dimension,
        complex_dimension,
        lambda row, column: variables[positions[row, column]],
    )
    equations: list[sp.Expr] = []
    for generator in representation:
        equations.extend(generator.T * candidate + candidate * generator)
    coefficient_matrix, _right_hand_side = sp.linear_eq_to_matrix(equations, variables)
    nullspace = coefficient_matrix.nullspace()
    _require(bool(nullspace), "endpoint representation has no invariant symmetric pairing")
    pairing = candidate.subs(dict(zip(variables, nullspace[0], strict=True)))
    return sp.simplify(pairing), len(nullspace)


def _endpoint_certificate(representation: Sequence[sp.Matrix], casimir: sp.Matrix) -> dict[str, Any]:
    complex_dimension = casimir.rows
    commutant = _commutant_basis(representation)
    splitting = next(
        (
            candidate
            for candidate in commutant
            if len(candidate.eigenvals()) == 2 and sorted(candidate.eigenvals().values()) == [3, 3]
        ),
        None,
    )
    if splitting is None:
        raise RuntimeError("endpoint commutant has no three-plus-three splitting element")
    eigenvalues = list(splitting.eigenvals())
    first_eigenvalue, second_eigenvalue = eigenvalues
    identity = sp.eye(complex_dimension)
    first_projector = sp.simplify((splitting - second_eigenvalue * identity) / (first_eigenvalue - second_eigenvalue))
    second_projector = sp.simplify(identity - first_projector)
    zero_matrix = sp.zeros(complex_dimension)
    projectors_pass = (
        first_projector.rank() == 3
        and second_projector.rank() == 3
        and sp.simplify(first_projector * first_projector - first_projector) == zero_matrix
        and sp.simplify(second_projector * second_projector - second_projector) == zero_matrix
        and sp.simplify(first_projector * second_projector) == zero_matrix
        and all(
            sp.simplify(projector * generator - generator * projector) == zero_matrix
            for projector in (first_projector, second_projector)
            for generator in representation
        )
    )
    pairing, pairing_space_dimension = _invariant_symmetric_pairing(representation)
    dual_pairing_pass = (
        pairing.rank() == complex_dimension
        and sp.simplify(first_projector.T * pairing * first_projector) == zero_matrix
        and sp.simplify(second_projector.T * pairing * second_projector) == zero_matrix
    )
    casimir_pass = casimir.eigenvals() == {sp.Rational(4, 9): 6}
    return {
        "decomposition": "3 + conjugate(3)",
        "casimir_spectrum": _casimir_spectrum(casimir),
        "commutant_dimension": len(commutant),
        "irreducible_projector_ranks": [first_projector.rank(), second_projector.rank()],
        "invariant_symmetric_pairing_dimension": pairing_space_dimension,
        "invariant_symmetric_pairing_rank": pairing.rank(),
        "summands_are_pairwise_dual": dual_pairing_pass,
        "connected_group": "SU(3), because 3 + conjugate(3) is faithful on the center of the simply connected cover",
        "pass": casimir_pass and len(commutant) == 2 and projectors_pass and dual_pairing_pass,
    }


def _complex_structure() -> RationalMatrix:
    vector = [Fraction(0)] * DIMENSION
    vector[DIMENSION // 2] = Fraction(1)
    return tuple(tuple(row) for row in left_mult_matrix_exact(DIMENSION, vector))


def _fixture_task(task: tuple[int, str, Fraction, str]) -> dict[str, Any]:
    sign, orbit_type, imaginary_ratio, mutation = task
    point = aligned._aligned_point(sign, imaginary_ratio)
    compact = stabilizer._compact_triples()
    tangent_rank, _stabilizer_bases, coefficient_rows = aligned._stabilizer_data(point, "")
    coefficients = list(coefficient_rows)
    if mutation == "include_moving_direction":
        moving_index = next(
            index for index, (_name, triple) in enumerate(compact) if any(stabilizer._matrix_vector(triple[0], point))
        )
        coefficients[0] = tuple(Fraction(index == moving_index) for index in range(COMPACT_GENERATOR_COUNT))
    elif mutation not in ("", "perturb_fiber_action"):
        raise ValueError(f"unknown mutation {mutation!r}")

    base_generators = [triple[0] for _name, triple in compact]
    domain_generators = [triple[1] for _name, triple in compact]
    stabilizer_bases = [stabilizer._linear_combination(row, base_generators) for row in coefficients]
    stabilizer_domains = [stabilizer._linear_combination(row, domain_generators) for row in coefficients]
    point_fixed = [not any(stabilizer._matrix_vector(matrix, point)) for matrix in stabilizer_bases]
    if mutation == "include_moving_direction":
        return {
            "component": "V^a_+" if sign == 1 else "V^a_-",
            "orbit_type": orbit_type,
            "mutation": mutation,
            "point_fixed": point_fixed,
            "pass": all(point_fixed),
        }

    expected = {
        "collinear_endpoint": (12, 7, 8, "su(3)"),
        "principal": (12, 12, 3, "su(2)"),
        "null_boundary": (16, 11, 4, "su(2)+u(1)"),
    }[orbit_type]
    expected_nullity, expected_tangent_rank, expected_stabilizer_dimension, stabilizer_label = expected
    left_matrix = tuple(tuple(row) for row in left_mult_matrix_exact(DIMENSION, tuple(point)))
    complex_structure = _complex_structure()
    adapted_basis = _adapted_kernel_basis(left_matrix, complex_structure, expected_nullity)
    kernel_preserved = [
        all(
            not any(stabilizer._matrix_vector(left_matrix, stabilizer._matrix_vector(domain, vector)))
            for vector in adapted_basis
        )
        for domain in stabilizer_domains
    ]
    fiber_matrices = [_fiber_matrix(domain, adapted_basis, complex_structure) for domain in stabilizer_domains]
    if mutation == "perturb_fiber_action":
        fiber_matrices[0] = fiber_matrices[0].copy()
        fiber_matrices[0][0, 1] += 1
    commutators_match = _representation_commutators_match(
        stabilizer_domains,
        fiber_matrices,
        adapted_basis,
        complex_structure,
    )
    if mutation == "perturb_fiber_action":
        return {
            "component": "V^a_+" if sign == 1 else "V^a_-",
            "orbit_type": orbit_type,
            "mutation": mutation,
            "point_fixed": point_fixed,
            "kernel_preserved": kernel_preserved,
            "representation_commutators_match": commutators_match,
            "pass": commutators_match,
        }

    derived_domains = _derived_basis(stabilizer_domains)
    casimir, killing = _casimir(derived_domains, adapted_basis, complex_structure)
    derived_representation = [_fiber_matrix(domain, adapted_basis, complex_structure) for domain in derived_domains]
    if orbit_type == "collinear_endpoint":
        representation_certificate = _endpoint_certificate(derived_representation, casimir)
    else:
        expected_doublets = 2 if orbit_type == "principal" else 3
        representation_certificate = _su2_certificate(casimir, expected_doublets)
    coordinate_checks = aligned._aligned_coordinate_checks(point, sign)
    compact_semisimple = aligned._negative_definite(killing)
    row_pass = (
        tangent_rank == expected_tangent_rank
        and len(coefficients) == expected_stabilizer_dimension
        and len(derived_domains) == (8 if orbit_type == "collinear_endpoint" else 3)
        and compact_semisimple
        and all(point_fixed)
        and all(kernel_preserved)
        and commutators_match
        and representation_certificate["pass"]
    )
    return {
        "component": "V^a_+" if sign == 1 else "V^a_-",
        "sign": sign,
        "orbit_type": orbit_type,
        "canonical_u": f"e_1+i*({imaginary_ratio})*e_2",
        "rho_squared": coordinate_checks["rho_squared"],
        "mutation": mutation,
        "compact_tangent_rank": tangent_rank,
        "stabilizer_dimension": len(coefficients),
        "stabilizer_derived_dimension": len(derived_domains),
        "stabilizer_lie_algebra": stabilizer_label,
        "derived_killing_negative_definite": compact_semisimple,
        "real_kernel_dimension": len(adapted_basis),
        "complex_kernel_dimension": len(adapted_basis) // 2,
        "point_fixed": point_fixed,
        "kernel_preserved": kernel_preserved,
        "representation_commutators_match": commutators_match,
        "representation": representation_certificate,
        "pass": row_pass,
    }


def _load_inputs() -> tuple[dict[str, str], dict[str, Any]]:
    bindings = (
        (
            "aligned_orbit_moduli",
            ALIGNED_RESULT,
            ALIGNED_SCRIPT,
            "a5-aligned-nullity-twelve-orbit-moduli-v1",
        ),
        (
            "nullity_sixteen_stabilizer",
            NULLITY_SIXTEEN_RESULT,
            NULLITY_SIXTEEN_SCRIPT,
            "a5-nullity-sixteen-stabilizer-representation-v1",
        ),
    )
    digests: dict[str, str] = {}
    loaded: dict[str, Any] = {}
    for label, result_path, script_path, schema in bindings:
        result = json.loads(result_path.read_text(encoding="utf-8"))
        script_digest = hashlib.sha256(script_path.read_bytes()).hexdigest()
        _require(result.get("schema") == schema, f"{result_path.name} has an unexpected schema")
        _require(result.get("pass") is True, f"{result_path.name} does not pass")
        _require(result.get("script_sha256") == script_digest, f"{result_path.name} is stale against its producer")
        digests[f"{label}_result_sha256"] = hashlib.sha256(result_path.read_bytes()).hexdigest()
        digests[f"{label}_script_sha256"] = script_digest
        loaded[label] = result
    return digests, loaded


def _row_signature(row: dict[str, Any]) -> tuple[Any, ...]:
    representation = row["representation"]
    return (
        row["stabilizer_lie_algebra"],
        row["complex_kernel_dimension"],
        representation["decomposition"],
        tuple(sorted(representation["casimir_spectrum"].items())),
    )


def representation_checks(mutation: str = "") -> dict[str, Any]:
    if mutation not in ("", "include_moving_direction", "perturb_fiber_action"):
        raise ValueError(f"unknown mutation {mutation!r}")
    input_digests, inputs = _load_inputs()
    if mutation:
        rows = [_fixture_task((1, "principal", Fraction(1, 2), mutation))]
        return {
            "mutation": mutation,
            "input_digests": input_digests,
            "rows": rows,
            "pass": all(row["pass"] for row in rows),
        }

    tasks = [
        (sign, orbit_type, imaginary_ratio, "")
        for sign in (1, -1)
        for orbit_type, imaginary_ratio in (
            ("collinear_endpoint", Fraction(0)),
            ("principal", Fraction(1, 3)),
            ("principal", Fraction(1, 2)),
            ("principal", Fraction(2, 3)),
            ("null_boundary", Fraction(1)),
        )
    ]
    rows = symmetry.parallel.ordered_map(_fixture_task, tasks, min_items=1)
    principal_rows = [row for row in rows if row["orbit_type"] == "principal"]
    endpoint_rows = [row for row in rows if row["orbit_type"] == "collinear_endpoint"]
    boundary_rows = [row for row in rows if row["orbit_type"] == "null_boundary"]
    principal_constant = len({_row_signature(row) for row in principal_rows}) == 1
    endpoints_agree = len({_row_signature(row) for row in endpoint_rows}) == 1
    boundary_restriction = {"trivial_lines": 2, "standard_doublets": 3}
    committed_rows = inputs["nullity_sixteen_stabilizer"]["stabilizer_representation"]["rows"]
    committed_boundary_matches = all(row["su2_restriction"] == boundary_restriction for row in committed_rows)
    computed_boundary_matches = all(
        row["representation"]["trivial_lines"] == 2 and row["representation"]["standard_doublets"] == 3
        for row in boundary_rows
    )
    boundary_comparison = {
        "principal_restriction": {"trivial_lines": 2, "standard_doublets": 2},
        "nullity_sixteen_restriction": boundary_restriction,
        "jump": "one standard SU(2) doublet is added at rho=0",
        "committed_result_matches": committed_boundary_matches,
        "computed_boundary_matches": computed_boundary_matches,
        "pass": committed_boundary_matches and computed_boundary_matches,
    }
    return {
        "mutation": mutation,
        "input_digests": input_digests,
        "rows": rows,
        "principal_representation": "2 V_0 + 2 V_1 on every 0<rho<1 orbit",
        "principal_constancy_argument": (
            "the canonical stabilizer is the fixed SU(2) that fixes e_1 and e_2; its isotypic multiplicities in the "
            "constant-rank kernel vary continuously and hence stay constant on the connected interval 0<rho<1"
        ),
        "endpoint_representation": "3 + conjugate(3) of SU(3)",
        "principal_rows_equivalent": principal_constant,
        "endpoint_components_equivalent": endpoints_agree,
        "boundary_comparison": boundary_comparison,
        "pass": all(row["pass"] for row in rows)
        and principal_constant
        and endpoints_agree
        and boundary_comparison["pass"],
    }


def build_result() -> dict[str, Any]:
    result = representation_checks()
    return {
        "schema": "a5-aligned-nullity-twelve-stabilizer-representation-v1",
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "aligned_stabilizer_representation": result,
        "pass": result["pass"],
    }


def self_test() -> None:
    baseline = representation_checks()
    if not baseline["pass"]:
        raise RuntimeError("baseline aligned stabilizer-representation check failed")
    moving_mutation = representation_checks("include_moving_direction")
    if moving_mutation["pass"] or all(moving_mutation["rows"][0]["point_fixed"]):
        raise RuntimeError("moving-generator mutation survived the point-stabilizer check")
    fiber_mutation = representation_checks("perturb_fiber_action")
    if fiber_mutation["pass"] or fiber_mutation["rows"][0]["representation_commutators_match"]:
        raise RuntimeError("fiber-action mutation survived the bracket check")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--self-test", action="store_true")
    arguments = parser.parse_args()
    if arguments.self_test:
        self_test()
        print("PASS: aligned stabilizer-representation self-test")
    if arguments.out is not None:
        result = build_result()
        arguments.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"wrote {arguments.out}")
    if not arguments.self_test and arguments.out is None:
        parser.error("choose --self-test or --out")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
