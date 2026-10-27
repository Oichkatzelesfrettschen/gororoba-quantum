"""Exact compact-orbit and topology classification of the aligned nullity-twelve pieces.

In original complex coordinates the two pieces ``V^a_+`` and ``V^a_-``
have the form ``z=(u,0,+/- i u)`` with ``u dot u != 0``.  This replay
checks the compact ``G_2 x U(1)`` tangent ranks and stabilizer Lie algebras
at the principal, collinear, and null-boundary orbit types.  It also records
the quadratic-link complement and its mapping-torus topology.
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

import kernel_symmetry as symmetry  # noqa: E402
import stabilizer_representation as stabilizer  # noqa: E402

DIMENSION = 32
COMPACT_ALGEBRA_DIMENSION = 15
KERNEL_SYMMETRY_SCRIPT = HERE / "kernel_symmetry.py"
KERNEL_SYMMETRY_RESULT = HERE / "result.json"
STABILIZER_SCRIPT = HERE / "stabilizer_representation.py"
STABILIZER_RESULT = HERE / "stabilizer-result.json"

RationalMatrix = symmetry.RationalMatrix
ComplexRational = tuple[Fraction, Fraction]


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _complex_add(first: ComplexRational, second: ComplexRational) -> ComplexRational:
    return first[0] + second[0], first[1] + second[1]


def _complex_multiply(first: ComplexRational, second: ComplexRational) -> ComplexRational:
    return first[0] * second[0] - first[1] * second[1], first[0] * second[1] + first[1] * second[0]


def _complex_scale_by_i(value: ComplexRational, sign: int) -> ComplexRational:
    return -sign * value[1], sign * value[0]


def _complex_norm_squared(value: ComplexRational) -> Fraction:
    return value[0] * value[0] + value[1] * value[1]


def _aligned_point(sign: int, imaginary_ratio: Fraction) -> tuple[Fraction, ...]:
    """Return the cone point with ``u=e_1+i*imaginary_ratio*e_2``."""
    if sign not in (-1, 1):
        raise ValueError("aligned-component sign must be +1 or -1")
    point = [Fraction(0)] * DIMENSION
    point[1] = Fraction(1)
    point[16 + 2] = imaginary_ratio
    point[16 + 8 + 1] = Fraction(sign)
    point[8 + 2] = -sign * imaginary_ratio
    return tuple(point)


def _complex_coordinates(point: Sequence[Fraction]) -> tuple[ComplexRational, ...]:
    _require(len(point) == DIMENSION, "A_5 point must have 32 real coordinates")
    return tuple((Fraction(point[index]), Fraction(point[16 + index])) for index in range(1, 16))


def _aligned_coordinate_checks(point: Sequence[Fraction], sign: int) -> dict[str, Any]:
    coordinates = _complex_coordinates(point)
    lower = coordinates[:7]
    middle = coordinates[7]
    upper = coordinates[8:]
    aligned = middle == (Fraction(0), Fraction(0)) and all(
        upper[index] == _complex_scale_by_i(lower[index], sign) for index in range(7)
    )
    bilinear_value = (Fraction(0), Fraction(0))
    hermitian_norm = Fraction(0)
    for coordinate in lower:
        bilinear_value = _complex_add(bilinear_value, _complex_multiply(coordinate, coordinate))
        hermitian_norm += _complex_norm_squared(coordinate)
    _require(hermitian_norm > 0, "aligned parameter u must be nonzero")
    rho_squared = _complex_norm_squared(bilinear_value) / (hermitian_norm * hermitian_norm)
    return {
        "aligned_original_coordinates": aligned,
        "u_bilinear_square": [str(value) for value in bilinear_value],
        "u_hermitian_norm_squared": str(hermitian_norm),
        "rho_squared": str(rho_squared),
        "inside_aligned_piece": bilinear_value != (Fraction(0), Fraction(0)),
    }


def _flatten(matrix: RationalMatrix) -> tuple[Fraction, ...]:
    return tuple(entry for row in matrix for entry in row)


def _matrix_from_flat(values: Sequence[Fraction]) -> RationalMatrix:
    _require(len(values) == DIMENSION * DIMENSION, "flattened matrix has the wrong size")
    return tuple(
        tuple(Fraction(values[row * DIMENSION + column]) for column in range(DIMENSION)) for row in range(DIMENSION)
    )


def _compact_triples(mutation: str) -> tuple[tuple[str, symmetry.LieTriple], ...]:
    compact = stabilizer._compact_triples()
    if mutation == "delete_phase_generator":
        compact = compact[:-1]
    return compact


def _stabilizer_data(
    point: Sequence[Fraction], mutation: str
) -> tuple[int, tuple[RationalMatrix, ...], tuple[tuple[Fraction, ...], ...]]:
    compact = _compact_triples(mutation)
    tangent_columns = [stabilizer._matrix_vector(triple[0], point) for _name, triple in compact]
    tangent_rank = symmetry._rank(tangent_columns)
    tangent_rows = [[tangent_columns[column][row] for column in range(len(compact))] for row in range(DIMENSION)]
    coefficients = tuple(tuple(row) for row in symmetry.equations.nullspace(tangent_rows))
    base_generators = [triple[0] for _name, triple in compact]
    stabilizer_bases = tuple(
        stabilizer._linear_combination(coefficient_row, base_generators) for coefficient_row in coefficients
    )
    return tangent_rank, stabilizer_bases, coefficients


def _derived_basis(stabilizer_bases: Sequence[RationalMatrix]) -> tuple[RationalMatrix, ...]:
    commutators = [
        symmetry._matrix_commutator(stabilizer_bases[first], stabilizer_bases[second])
        for first in range(len(stabilizer_bases))
        for second in range(first + 1, len(stabilizer_bases))
    ]
    independent = stabilizer._independent_vectors([_flatten(matrix) for matrix in commutators])
    return tuple(_matrix_from_flat(vector) for vector in independent)


def _center_dimension(stabilizer_bases: Sequence[RationalMatrix]) -> int:
    rows: list[list[Fraction]] = []
    for fixed in stabilizer_bases:
        commutators = [symmetry._matrix_commutator(candidate, fixed) for candidate in stabilizer_bases]
        flattened = [_flatten(matrix) for matrix in commutators]
        for coordinate in range(DIMENSION * DIMENSION):
            rows.append([matrix[coordinate] for matrix in flattened])
    return len(symmetry.equations.nullspace(rows))


def _negative_definite(matrix: sp.Matrix) -> bool:
    if matrix != matrix.T:
        return False
    for size in range(1, matrix.rows + 1):
        signed_minor = sp.factor((-1) ** size * matrix[:size, :size].det())
        if signed_minor.is_positive is not True:
            return False
    return True


def _lie_algebra_label(
    stabilizer_dimension: int, center_dimension: int, derived_dimension: int, compact_semisimple: bool
) -> str:
    signature = (stabilizer_dimension, center_dimension, derived_dimension, compact_semisimple)
    labels = {
        (3, 0, 3, True): "su(2)",
        (4, 1, 3, True): "su(2)+u(1)",
        (8, 0, 8, True): "su(3)",
    }
    return labels.get(signature, "unclassified")


def _fixture_task(task: tuple[int, str, Fraction, str]) -> dict[str, Any]:
    sign, orbit_type, imaginary_ratio, mutation = task
    point = _aligned_point(sign, imaginary_ratio)
    coordinate_checks = _aligned_coordinate_checks(point, sign)
    tangent_rank, stabilizer_bases, coefficients = _stabilizer_data(point, mutation)
    derived_bases = _derived_basis(stabilizer_bases)
    center_dimension = _center_dimension(stabilizer_bases)
    killing = stabilizer._killing_matrix(derived_bases)
    compact_semisimple = _negative_definite(killing)
    stabilizer_dimension = len(coefficients)
    lie_algebra = _lie_algebra_label(
        stabilizer_dimension,
        center_dimension,
        len(derived_bases),
        compact_semisimple,
    )
    nullity = symmetry.equations.nullity(point)
    expected = {
        "collinear_endpoint": {
            "rho_squared": "1",
            "inside_aligned_piece": True,
            "tangent_rank": 7,
            "nullity": 12,
            "lie_algebra": "su(3)",
        },
        "principal": {
            "rho_squared": "9/25",
            "inside_aligned_piece": True,
            "tangent_rank": 12,
            "nullity": 12,
            "lie_algebra": "su(2)",
        },
        "null_boundary": {
            "rho_squared": "0",
            "inside_aligned_piece": False,
            "tangent_rank": 11,
            "nullity": 16,
            "lie_algebra": "su(2)+u(1)",
        },
    }[orbit_type]
    row_pass = (
        mutation == ""
        and coordinate_checks["aligned_original_coordinates"]
        and coordinate_checks["rho_squared"] == expected["rho_squared"]
        and coordinate_checks["inside_aligned_piece"] is expected["inside_aligned_piece"]
        and tangent_rank == expected["tangent_rank"]
        and nullity == expected["nullity"]
        and lie_algebra == expected["lie_algebra"]
    )
    return {
        "component": "V^a_+" if sign == 1 else "V^a_-",
        "sign": sign,
        "orbit_type": orbit_type,
        "canonical_u": f"e_1+i*({imaginary_ratio})*e_2",
        **coordinate_checks,
        "compact_generator_count": len(_compact_triples(mutation)),
        "compact_tangent_rank": tangent_rank,
        "stabilizer_dimension": stabilizer_dimension,
        "stabilizer_center_dimension": center_dimension,
        "stabilizer_derived_dimension": len(derived_bases),
        "derived_killing_negative_definite": compact_semisimple,
        "stabilizer_lie_algebra": lie_algebra,
        "left_nullity": nullity,
        "pass": row_pass,
    }


def _gram_invariant_checks() -> dict[str, Any]:
    gram = sp.Matrix([[5, 3], [3, 5]])
    phase_rotation = sp.Matrix([[sp.Rational(3, 5), -sp.Rational(4, 5)], [sp.Rational(4, 5), sp.Rational(3, 5)]])
    rotated = sp.simplify(phase_rotation.T * gram * phase_rotation)

    def discriminant(matrix: sp.Matrix) -> sp.Expr:
        return sp.factor((matrix[0, 0] - matrix[1, 1]) ** 2 + 4 * matrix[0, 1] ** 2)

    trace_preserved = sp.trace(rotated) == sp.trace(gram)
    determinant_preserved = sp.factor(rotated.det() - gram.det()) == 0
    discriminant_preserved = sp.factor(discriminant(rotated) - discriminant(gram)) == 0
    canonical_eigenvalues = tuple(sorted(int(value) for value in gram.eigenvals()))
    return {
        "invariant": "rho=abs(u dot u)/(u^* dot u)",
        "real_gram_trace_preserved_by_phase": trace_preserved,
        "real_gram_determinant_preserved_by_phase": determinant_preserved,
        "real_gram_discriminant_preserved_by_phase": discriminant_preserved,
        "fixture_gram_eigenvalues": list(canonical_eigenvalues),
        "canonical_gram_eigenvalues_at_fixed_norm": ["h(1+rho)/2", "h(1-rho)/2"],
        "completeness": (
            "a phase makes u dot u nonnegative real; the real-imaginary Gram matrix then diagonalizes with the "
            "displayed eigenvalues, and G_2 transitivity on ordered orthonormal two-frames identifies equal-rho points"
        ),
        "pass": trace_preserved
        and determinant_preserved
        and discriminant_preserved
        and canonical_eigenvalues == (2, 8),
    }


def _topology_checks(mutation: str) -> dict[str, Any]:
    monodromy_degree = 1 if mutation == "trivialize_monodromy" else -1
    if monodromy_degree == -1:
        cohomology = {"0": "Z", "1": "Z", "7": "Z/2"}
    else:
        cohomology = {"0": "Z", "1": "Z", "6": "Z", "7": "Z"}
    topology_pass = mutation != "trivialize_monodromy" and cohomology == {"0": "Z", "1": "Z", "7": "Z/2"}
    return {
        "unit_section": "S^13 minus V_2(R^7), independently for V^a_+ and V^a_-",
        "quadratic_argument_fibration": "q/abs(q): S^13 minus {q=0} -> S^1, q(u)=u dot u",
        "fiber": "open tangent disk bundle of S^6, homotopy equivalent to S^6",
        "monodromy": "u -> -u; antipodal on the S^6 zero section",
        "monodromy_degree_on_h6": monodromy_degree,
        "fundamental_group": "Z",
        "integral_cohomology": cohomology,
        "alexander_duality_check": "H~^1=H_11(V_2)=Z and H~^7=H_5(V_2)=Z/2",
        "pass": topology_pass,
    }


def _load_inputs() -> dict[str, str]:
    bindings = (
        ("kernel_symmetry", KERNEL_SYMMETRY_RESULT, KERNEL_SYMMETRY_SCRIPT, "a5-kernel-symmetry-v3"),
        (
            "nullity_sixteen_stabilizer",
            STABILIZER_RESULT,
            STABILIZER_SCRIPT,
            "a5-nullity-sixteen-stabilizer-representation-v1",
        ),
    )
    digests: dict[str, str] = {}
    for label, result_path, script_path, schema in bindings:
        result = json.loads(result_path.read_text(encoding="utf-8"))
        script_digest = hashlib.sha256(script_path.read_bytes()).hexdigest()
        _require(result.get("schema") == schema, f"{result_path.name} has an unexpected schema")
        _require(result.get("pass") is True, f"{result_path.name} does not pass")
        _require(result.get("script_sha256") == script_digest, f"{result_path.name} is stale against its producer")
        digests[f"{label}_result_sha256"] = hashlib.sha256(result_path.read_bytes()).hexdigest()
        digests[f"{label}_script_sha256"] = script_digest
    return digests


def orbit_moduli_checks(mutation: str = "") -> dict[str, Any]:
    if mutation not in ("", "delete_phase_generator", "trivialize_monodromy"):
        raise ValueError(f"unknown mutation {mutation!r}")
    input_digests = _load_inputs()
    fixture_mutation = mutation if mutation == "delete_phase_generator" else ""
    tasks = [
        (sign, orbit_type, imaginary_ratio, fixture_mutation)
        for sign in (1, -1)
        for orbit_type, imaginary_ratio in (
            ("collinear_endpoint", Fraction(0)),
            ("principal", Fraction(1, 2)),
            ("null_boundary", Fraction(1)),
        )
    ]
    rows = symmetry.parallel.ordered_map(_fixture_task, tasks, min_items=1)
    gram_invariant = _gram_invariant_checks()
    topology = _topology_checks(mutation)
    baseline_rows_pass = all(row["pass"] for row in rows)
    signs_agree = all(
        rows[index][key] == rows[index + 3][key]
        for index in range(3)
        for key in (
            "rho_squared",
            "compact_tangent_rank",
            "stabilizer_dimension",
            "stabilizer_lie_algebra",
            "left_nullity",
        )
    )
    return {
        "mutation": mutation,
        "input_digests": input_digests,
        "original_coordinate_parameterization": "z=(u,0,+/- i u), u dot u != 0",
        "unit_norm_condition": "u^* dot u=1/2",
        "orbit_space": "0<rho<=1",
        "principal_orbits": "0<rho<1 with stabilizer Lie algebra su(2) and dimension 12",
        "singular_endpoint_orbit": "rho=1 with stabilizer Lie algebra su(3) and dimension 7",
        "nullity_sixteen_boundary": "rho=0 with stabilizer Lie algebra su(2)+u(1) and dimension 11",
        "earlier_rank_scope": "the rank-seven V^a representative is the rho=1 endpoint, not the principal orbit",
        "gram_invariant": gram_invariant,
        "rows": rows,
        "component_results_identical": signs_agree,
        "topology": topology,
        "pass": mutation == "" and baseline_rows_pass and signs_agree and gram_invariant["pass"] and topology["pass"],
    }


def build_result() -> dict[str, Any]:
    result = orbit_moduli_checks()
    return {
        "schema": "a5-aligned-nullity-twelve-orbit-moduli-v1",
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "aligned_orbit_moduli": result,
        "pass": result["pass"],
    }


def _self_test_mutation_task(mutation: str) -> tuple[str, dict[str, Any]]:
    """Build one independent orbit-moduli mutation for the parent self-test."""
    return mutation, orbit_moduli_checks(mutation)


def self_test() -> None:
    baseline = orbit_moduli_checks()
    if not baseline["pass"]:
        raise RuntimeError("baseline aligned-orbit moduli check failed")
    mutations = dict(
        symmetry.parallel.ordered_map(
            _self_test_mutation_task,
            ["delete_phase_generator", "trivialize_monodromy"],
            min_items=1,
        )
    )
    phase_mutation = mutations["delete_phase_generator"]
    principal_mutation_ranks = [
        row["compact_tangent_rank"] for row in phase_mutation["rows"] if row["orbit_type"] == "principal"
    ]
    if phase_mutation["pass"] or principal_mutation_ranks == [12, 12]:
        raise RuntimeError("phase-generator deletion survived the orbit-rank check")
    monodromy_mutation = mutations["trivialize_monodromy"]
    if monodromy_mutation["pass"] or monodromy_mutation["topology"]["integral_cohomology"].get("7") == "Z/2":
        raise RuntimeError("trivial-monodromy mutation survived the topology check")


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
        print("PASS: aligned nullity-twelve orbit-moduli self-test")
    if arguments.out is not None or arguments.check is not None:
        result = build_result()
        payload = (json.dumps(result, indent=2, sort_keys=True) + "\n").encode()
        if arguments.check is not None:
            if payload != arguments.check.read_bytes():
                raise SystemExit(f"aligned_orbit_moduli.py: fresh JSON differs byte-for-byte from {arguments.check}")
            print(f"aligned_orbit_moduli.py: fresh JSON matches {arguments.check}")
        else:
            arguments.out.write_bytes(payload)
            print(f"wrote {arguments.out}")
    if not arguments.self_test and arguments.out is None and arguments.check is None:
        parser.error("choose --self-test, --out, or --check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
