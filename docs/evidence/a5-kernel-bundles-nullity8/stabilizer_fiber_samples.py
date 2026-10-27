"""Exact connected stabilizers and rank-four fiber representations on nullity-eight fixtures."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections.abc import Sequence
from fractions import Fraction
from pathlib import Path
from typing import Any, TypeAlias, cast

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

import aligned_orbit_moduli as aligned  # noqa: E402
import aligned_stabilizer_representation as aligned_representation  # noqa: E402
import compact_orbit_ranks as ranks  # noqa: E402
import kernel_symmetry as symmetry  # noqa: E402
import stabilizer_representation as stabilizer  # noqa: E402
import verify_regularity_independent as independent  # noqa: E402

import parallel  # noqa: E402
from cd_core import left_mult_matrix_exact  # noqa: E402

SCHEMA = "a5-kernel-bundles-nullity8-stabilizer-fiber-samples-v1"
MUTATIONS = ("", "include_moving_direction", "perturb_fiber_action")
COMPACT_GENERATOR_COUNT = 15
REAL_FIBER_DIMENSION = 8
COMPLEX_FIBER_DIMENSION = 4
SOURCE_PATHS = (
    HERE / "stabilizer_fiber_samples.py",
    HERE / "compact_orbit_ranks.py",
    KERNEL_BUNDLES / "kernel_symmetry.py",
    KERNEL_BUNDLES / "stabilizer_representation.py",
    KERNEL_BUNDLES / "aligned_orbit_moduli.py",
    KERNEL_BUNDLES / "aligned_stabilizer_representation.py",
    REGULARITY / "verify_regularity_independent.py",
)

RationalMatrix: TypeAlias = tuple[tuple[Fraction, ...], ...]
GaussianPoint: TypeAlias = tuple[independent.Gq, ...]
PointTask = tuple[str, str, tuple[Fraction, ...], str]


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _mostow_x_core_split(orbit_name: str) -> GaussianPoint:
    """Return an explicit Mostow-adapted X core point in split coordinates."""
    if orbit_name not in ("X+", "X-"):
        raise ValueError(f"the Mostow-adapted core is defined only for an X branch, not {orbit_name!r}")
    imaginary_unit = independent.Gq(Fraction(0), Fraction(1))
    original = [independent.Gq() for _index in range(15)]
    original[0] = independent.Gq(1)
    original[1] = -imaginary_unit
    original[2] = independent.Gq(1)
    if orbit_name == "X+":
        original[8] = -imaginary_unit
        original[9] = independent.Gq(-1)
        original[10] = imaginary_unit
    else:
        original[8] = imaginary_unit
        original[9] = independent.Gq(1)
        original[10] = -imaginary_unit
    return tuple(
        value * independent.i_pow(-independent.popcount(index)) for index, value in enumerate(original, start=1)
    )


def _gaussian_split_from_rational(point: Sequence[Fraction]) -> GaussianPoint:
    return tuple(independent.Gq(value) for value in point)


def _real_from_gaussian_split(point: Sequence[independent.Gq]) -> tuple[Fraction, ...]:
    _require(len(point) == 15, "a split point needs fifteen coordinates")
    real_point = [Fraction(0)] * 32
    for index, value in enumerate(point, start=1):
        original = independent.i_pow(independent.popcount(index)) * value
        real_point[index] = original.re
        real_point[16 + index] = original.im
    return tuple(real_point)


def _matrix_rank(matrix: Sequence[Sequence[Fraction]]) -> int:
    return symmetry.equations.qrank(matrix) if matrix else 0


def _compact_data(
    point: Sequence[Fraction], mutation: str
) -> tuple[int, tuple[tuple[Fraction, ...], ...], tuple[RationalMatrix, ...], tuple[RationalMatrix, ...]]:
    compact = stabilizer._compact_triples()
    tangent_rank, _base_stabilizers, coefficient_rows = aligned._stabilizer_data(point, "")
    coefficients = list(coefficient_rows)
    if mutation == "include_moving_direction":
        _require(bool(coefficients), "moving-direction mutation requires a positive-dimensional stabilizer")
        moving_index = next(
            index for index, (_name, triple) in enumerate(compact) if any(stabilizer._matrix_vector(triple[0], point))
        )
        coefficients[0] = tuple(Fraction(index == moving_index) for index in range(COMPACT_GENERATOR_COUNT))
    elif mutation not in ("", "perturb_fiber_action"):
        raise ValueError(f"unknown mutation {mutation!r}")
    base_generators = [triple[0] for _name, triple in compact]
    domain_generators = [triple[1] for _name, triple in compact]
    base_stabilizers = tuple(
        stabilizer._linear_combination(coefficient_row, base_generators) for coefficient_row in coefficients
    )
    domain_stabilizers = tuple(
        stabilizer._linear_combination(coefficient_row, domain_generators) for coefficient_row in coefficients
    )
    return tangent_rank, tuple(coefficients), base_stabilizers, domain_stabilizers


def _highest_weight(casimir_eigenvalue: sp.Expr) -> int:
    for highest_weight in range(COMPLEX_FIBER_DIMENSION):
        expected = sp.Rational(highest_weight * (highest_weight + 2), 8)
        if sp.simplify(casimir_eigenvalue - expected) == 0:
            return highest_weight
    raise ArithmeticError(f"unrecognized su(2) Casimir eigenvalue {casimir_eigenvalue}")


def _su2_decomposition(casimir: sp.Matrix) -> tuple[list[dict[str, Any]], bool]:
    decomposition = []
    total_dimension = 0
    for eigenvalue, eigenspace_dimension in sorted(
        casimir.eigenvals().items(), key=lambda item: sp.default_sort_key(item[0])
    ):
        highest_weight = _highest_weight(eigenvalue)
        irreducible_dimension = highest_weight + 1
        _require(
            eigenspace_dimension % irreducible_dimension == 0,
            "a Casimir eigenspace is not a sum of equal su(2) irreducibles",
        )
        multiplicity = eigenspace_dimension // irreducible_dimension
        total_dimension += eigenspace_dimension
        decomposition.append(
            {
                "highest_weight": highest_weight,
                "irreducible_dimension": irreducible_dimension,
                "multiplicity": multiplicity,
                "joint_dimension": eigenspace_dimension,
                "casimir_eigenvalue": sp.sstr(eigenvalue),
            }
        )
    return decomposition, total_dimension == COMPLEX_FIBER_DIMENSION


def _decomposition_label(decomposition: Sequence[dict[str, Any]]) -> str:
    return " + ".join(
        f"{row['multiplicity']} V_{row['highest_weight']}" if row["multiplicity"] != 1 else f"V_{row['highest_weight']}"
        for row in decomposition
    )


def _representation_data(
    domain_stabilizers: Sequence[RationalMatrix],
    fiber_matrices: Sequence[sp.Matrix],
    adapted_basis: Sequence[Sequence[Fraction]],
    complex_structure: RationalMatrix,
) -> dict[str, Any]:
    stabilizer_dimension = len(domain_stabilizers)
    if stabilizer_dimension == 0:
        decomposition = [
            {
                "highest_weight": 0,
                "irreducible_dimension": 1,
                "multiplicity": COMPLEX_FIBER_DIMENSION,
                "joint_dimension": COMPLEX_FIBER_DIMENSION,
                "casimir_eigenvalue": "0",
            }
        ]
        return {
            "connected_group": "trivial",
            "decomposition": _decomposition_label(decomposition),
            "irreducible_decomposition": decomposition,
            "casimir_spectrum": {"0": COMPLEX_FIBER_DIMENSION},
            "derived_killing_matrix": [],
            "derived_killing_negative_definite": True,
            "pass": True,
        }

    center_dimension = aligned._center_dimension(domain_stabilizers)
    derived_domains = aligned_representation._derived_basis(domain_stabilizers)
    casimir, killing = aligned_representation._casimir(derived_domains, adapted_basis, complex_structure)
    decomposition, dimension_matches = _su2_decomposition(casimir)
    compact_semisimple = aligned._negative_definite(killing)
    odd_highest_weight_occurs = any(cast(int, row["highest_weight"]) % 2 == 1 for row in decomposition)
    return {
        "connected_group": "SU(2)" if odd_highest_weight_occurs else "SU(2) or SO(3) unresolved by the fiber",
        "decomposition": _decomposition_label(decomposition),
        "irreducible_decomposition": decomposition,
        "casimir_spectrum": {sp.sstr(value): multiplicity for value, multiplicity in casimir.eigenvals().items()},
        "derived_killing_matrix": [[sp.sstr(value) for value in row] for row in killing.tolist()],
        "derived_killing_negative_definite": compact_semisimple,
        "pass": (
            stabilizer_dimension == 3
            and center_dimension == 0
            and len(derived_domains) == 3
            and compact_semisimple
            and dimension_matches
        ),
    }


def _direct_tangent_rank_real(point: Sequence[Fraction]) -> int:
    tangent_vectors = [ranks._direct_derivation_tangent(derivation, point) for derivation in ranks.COMPACT_DERIVATIONS]
    tangent_vectors.append(ranks._phase_tangent(point))
    return symmetry.equations.qrank(tangent_vectors)


def _analyze_point(
    orbit_name: str,
    move_name: str,
    split_point: GaussianPoint,
    point: tuple[Fraction, ...],
    mutation: str,
) -> dict[str, Any]:
    tangent_rank, coefficient_rows, base_stabilizers, domain_stabilizers = _compact_data(point, mutation)
    point_fixed = parallel.ordered_map(
        _point_fixed_task,
        [(matrix, point) for matrix in base_stabilizers],
        min_items=1,
    )
    independent_tangent_rank = _direct_tangent_rank_real(point)
    if mutation == "include_moving_direction":
        return {
            "orbit": orbit_name,
            "move": move_name,
            "mutation": mutation,
            "compact_tangent_rank": tangent_rank,
            "independent_compact_tangent_rank": independent_tangent_rank,
            "stabilizer_dimension": len(coefficient_rows),
            "point_fixed": point_fixed,
            "pass": all(point_fixed),
        }

    left_matrix = tuple(tuple(row) for row in left_mult_matrix_exact(32, point))
    left_nullity = 32 - _matrix_rank(left_matrix)
    complex_structure = aligned_representation._complex_structure()
    adapted_basis = aligned_representation._adapted_kernel_basis(
        left_matrix,
        complex_structure,
        REAL_FIBER_DIMENSION,
    )
    kernel_preserved = parallel.ordered_map(
        _kernel_preserved_task,
        [(left_matrix, domain, adapted_basis) for domain in domain_stabilizers],
        min_items=1,
    )
    fiber_matrices = parallel.ordered_map(
        _fiber_matrix_task,
        [(domain, adapted_basis, complex_structure) for domain in domain_stabilizers],
        min_items=1,
    )
    if mutation == "perturb_fiber_action":
        _require(bool(fiber_matrices), "fiber-action mutation requires a positive-dimensional stabilizer")
        fiber_matrices[0] = fiber_matrices[0].copy()
        fiber_matrices[0][0, 1] += 1
    commutators_match = aligned_representation._representation_commutators_match(
        domain_stabilizers,
        fiber_matrices,
        adapted_basis,
        complex_structure,
    )
    if mutation == "perturb_fiber_action":
        return {
            "orbit": orbit_name,
            "move": move_name,
            "mutation": mutation,
            "compact_tangent_rank": tangent_rank,
            "stabilizer_dimension": len(coefficient_rows),
            "point_fixed": point_fixed,
            "kernel_preserved": kernel_preserved,
            "representation_commutators_match": commutators_match,
            "pass": commutators_match,
        }

    stabilizer_dimension = len(coefficient_rows)
    if stabilizer_dimension:
        center_dimension = aligned._center_dimension(base_stabilizers)
        derived_bases = aligned._derived_basis(base_stabilizers)
        killing = stabilizer._killing_matrix(derived_bases)
        compact_semisimple = aligned._negative_definite(killing)
        lie_algebra = aligned._lie_algebra_label(
            stabilizer_dimension,
            center_dimension,
            len(derived_bases),
            compact_semisimple,
        )
    else:
        center_dimension = 0
        derived_bases = ()
        compact_semisimple = True
        lie_algebra = "zero"
    representation = _representation_data(
        domain_stabilizers,
        fiber_matrices,
        adapted_basis,
        complex_structure,
    )
    row_pass = (
        independent_tangent_rank == tangent_rank
        and stabilizer_dimension == COMPACT_GENERATOR_COUNT - tangent_rank
        and left_nullity == REAL_FIBER_DIMENSION
        and independent.pattern(split_point) == independent.pattern(independent.REPS[orbit_name])
        and all(point_fixed)
        and all(kernel_preserved)
        and commutators_match
        and lie_algebra in ("zero", "su(2)")
        and representation["pass"]
    )
    return {
        "orbit": orbit_name,
        "move": move_name,
        "mutation": None,
        "nullity_Ly": left_nullity,
        "same_open_orbit": independent.pattern(split_point) == independent.pattern(independent.REPS[orbit_name]),
        "compact_tangent_rank": tangent_rank,
        "independent_compact_tangent_rank": independent_tangent_rank,
        "stabilizer_dimension": stabilizer_dimension,
        "stabilizer_center_dimension": center_dimension,
        "stabilizer_derived_dimension": len(derived_bases),
        "stabilizer_lie_algebra": lie_algebra,
        "derived_killing_negative_definite": compact_semisimple,
        "point_fixed": point_fixed,
        "complex_kernel_dimension": len(adapted_basis) // 2,
        "kernel_preserved": kernel_preserved,
        "representation_commutators_match": commutators_match,
        "representation": representation,
        "pass": row_pass,
    }


def _row(task: PointTask) -> dict[str, Any]:
    orbit_name, move_name, rational_split_point, mutation = task
    split_point = _gaussian_split_from_rational(rational_split_point)
    point = tuple(symmetry.equations.y_from_split(rational_split_point))
    return _analyze_point(orbit_name, move_name, split_point, point, mutation)


def _mostow_core_row(orbit_name: str) -> dict[str, Any]:
    split_point = _mostow_x_core_split(orbit_name)
    point = _real_from_gaussian_split(split_point)
    return _analyze_point(orbit_name, "Mostow-adapted core", split_point, point, "")


def _point_fixed_task(task: tuple[RationalMatrix, tuple[Fraction, ...]]) -> bool:
    matrix, point = task
    return not any(stabilizer._matrix_vector(matrix, point))


def _kernel_preserved_task(
    task: tuple[RationalMatrix, RationalMatrix, tuple[tuple[Fraction, ...], ...]],
) -> bool:
    left_matrix, domain, adapted_basis = task
    return all(
        not any(stabilizer._matrix_vector(left_matrix, stabilizer._matrix_vector(domain, vector)))
        for vector in adapted_basis
    )


def _fiber_matrix_task(
    task: tuple[RationalMatrix, tuple[tuple[Fraction, ...], ...], RationalMatrix],
) -> sp.Matrix:
    domain, adapted_basis, complex_structure = task
    return aligned_representation._fiber_matrix(domain, adapted_basis, complex_structure)


def _normal_tasks() -> list[PointTask]:
    return ranks._point_tasks("")


def _mutation_task(mutation: str) -> PointTask:
    representative = next(task for task in ranks._move_fixtures("W8") if task[1] == "representative")
    return representative[0], representative[1], representative[2], mutation


def _row_signature(row: dict[str, Any]) -> tuple[Any, ...]:
    return (
        row["stabilizer_lie_algebra"],
        row["representation"]["decomposition"],
        tuple(sorted(row["representation"]["casimir_spectrum"].items())),
    )


def build_record(mutation: str = "") -> dict[str, Any]:
    if mutation not in MUTATIONS:
        raise ValueError(f"unknown mutation {mutation!r}")
    if mutation:
        rows = [_row(_mutation_task(mutation))]
        return {
            "schema": SCHEMA,
            "mutation": mutation,
            "inputs": {str(path.relative_to(ROOT)): _sha256(path) for path in SOURCE_PATHS},
            "rows": rows,
            "pass": all(row["pass"] for row in rows),
        }

    rows = parallel.ordered_map(_row, _normal_tasks(), min_items=1)
    core_rows = parallel.ordered_map(_mostow_core_row, ["X+", "X-"], min_items=1)
    positive_rows = [row for row in rows if row["stabilizer_dimension"] > 0]
    trivial_rows = [row for row in rows if row["stabilizer_dimension"] == 0]
    signatures = sorted({_row_signature(row) for row in positive_rows}, key=str)
    return {
        "schema": SCHEMA,
        "mutation": None,
        "inputs": {str(path.relative_to(ROOT)): _sha256(path) for path in SOURCE_PATHS},
        "rows": rows,
        "mostow_adapted_core_rows": core_rows,
        "summary": {
            "fixtures": len(rows),
            "mostow_adapted_core_fixtures": len(core_rows),
            "trivial_connected_stabilizer_fixtures": len(trivial_rows),
            "positive_dimensional_stabilizer_fixtures": len(positive_rows),
            "positive_dimensional_representation_signatures": [list(signature) for signature in signatures],
            "positive_dimensional_signatures_constant": len(signatures) == 1,
        },
        "scope": (
            "The rows classify the connected stabilizers and fiber representations at the recorded representative "
            "and three exact noncompact moves per complex orbit. The two additional core rows compute the X fiber "
            "at explicit Mostow-adapted points. They do not by themselves prove that these are all compact "
            "stabilizer strata."
        ),
        "pass": (
            all(row["pass"] for row in rows)
            and all(row["pass"] and row["representation"]["decomposition"] == "2 V_0 + V_1" for row in core_rows)
            and bool(positive_rows)
            and bool(trivial_rows)
        ),
    }


def _build_record_task(mutation: str) -> dict[str, Any]:
    return build_record(mutation)


def self_test() -> None:
    normal, moving_mutation, fiber_mutation = parallel.ordered_map(
        _build_record_task,
        list(MUTATIONS),
        min_items=1,
    )
    _require(normal["pass"], "normal stabilizer and fiber sample record failed")
    _require(
        all(
            row["move"] == "Mostow-adapted core" and row["representation"]["decomposition"] == "2 V_0 + V_1"
            for row in normal["mostow_adapted_core_rows"]
        ),
        "a Mostow-adapted X core has the wrong fiber representation",
    )
    _require(not moving_mutation["pass"], "moving-direction mutation survived")
    _require(
        not all(moving_mutation["rows"][0]["point_fixed"]),
        "moving-direction mutation changed no downstream point-fixing check",
    )
    _require(not fiber_mutation["pass"], "fiber-action mutation survived")
    _require(
        not fiber_mutation["rows"][0]["representation_commutators_match"],
        "fiber-action mutation changed no downstream bracket check",
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
