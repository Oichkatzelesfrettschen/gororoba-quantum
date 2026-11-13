"""Equivariance of the holomorphic kernel map z -> ker C_z under a unipotent G_2 automorphism and the boost.

C_z is linear in z in the original coordinates z_k = i^popcount(k) z'_k of holomorphic_kernel_lemma.py. A matrix g of
the 15-dimensional representation acts on the kernel bundle when C_(g z) = rho^(-T) C_z rho^(-1) for one matrix rho,
since then ker C_(g z) = rho ker C_z, and rho = g gives ker C_(g z) = g ker C_z. For the selected unipotent G_2
automorphism of incidence_census.py, written in original coordinates, g^T g = I and the identity holds with rho = g
on the 15 basis directions, hence for every z by linearity. The same identity with the split-coordinate matrix as
rho, which omits the phase conjugation, leaves a nonzero residual; that is the mutation control. For the rational
boost b(c, s) of verify_regularity_independent.py no candidate rho satisfies the identity, and ker C_(b z) differs from
b ker C_z at six of the twelve canonical points, with the smallest witness at the canonical VB point.

The Lie-algebra level solves C_(X e_k) + R^T C_k + C_k R = 0 over Q for the pairs (X, R) of 15 x 15 matrices; its
solution space has dimension 15, projects isomorphically onto the X coordinates, contains the 14 G_2 derivations and
the scaling, and excludes the boost generator. The final table compares the orbit dimension of each canonical point
with the rank of the tangent vectors that the equivariant span produces there.
"""

from __future__ import annotations

import argparse
import functools
import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

import flint

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "a5-strata-regularity"))
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import holomorphic_kernel_lemma as kernel_lemma  # noqa: E402
import incidence_census  # noqa: E402
import verify_regularity_independent as regularity  # noqa: E402

import parallel  # noqa: E402

SCHEMA = "a5-kernel-attachments-kernel-equivariance-v1"
SOURCE_PATHS = (
    HERE / "kernel_equivariance.py",
    HERE / "holomorphic_kernel_lemma.py",
    HERE / "incidence_census.py",
    HERE.parent / "a5-strata-regularity" / "verify_regularity_independent.py",
    ROOT / "gororoba_quantum" / "cd_core.py",
    ROOT / "gororoba_quantum" / "parallel.py",
)
ZERO = kernel_lemma.ZERO
ONE = kernel_lemma.ONE
DIMENSION = 15
OCTONION_DIMENSION = 7
CANONICAL_POINTS = ("B9", "V", "VB", "Va+", "Va-", "N+", "N-", "W8", "E8bar", "Iso", "X+", "X-")
EQUATION_COUNT = DIMENSION * DIMENSION * DIMENSION
UNKNOWN_COUNT = 2 * DIMENSION * DIMENSION
WITNESS_POINTS = ("VB", "B9", "V")
SMALLEST_WITNESS = "VB"
G2_DERIVATION_COUNT = 14

Gaussian = kernel_lemma.Gaussian
GaussianVector = kernel_lemma.GaussianVector
GaussianMatrix = kernel_lemma.GaussianMatrix


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _hash_path(path: Path) -> tuple[str, str]:
    return path.relative_to(ROOT).as_posix(), hashlib.sha256(path.read_bytes()).hexdigest()


def _gaussian_rational(value: Fraction | int) -> Gaussian:
    return (Fraction(value), Fraction(0))


def multiply_matrices(left: GaussianMatrix, right: GaussianMatrix) -> GaussianMatrix:
    """The product of two Gaussian-rational matrices with exact arithmetic."""
    inner = len(right)
    return tuple(
        tuple(
            kernel_lemma._gaussian_sum(kernel_lemma._gaussian_multiply(row[k], right[k][j]) for k in range(inner))
            for j in range(len(right[0]))
        )
        for row in left
    )


def identity_matrix() -> GaussianMatrix:
    return tuple(tuple(ONE if i == j else ZERO for j in range(DIMENSION)) for i in range(DIMENSION))


def to_original_coordinates(split_matrix: GaussianMatrix) -> GaussianMatrix:
    """D M D^(-1) for the diagonal phase matrix D of the coordinate change z_k = i^popcount(k) z'_k."""
    return tuple(
        tuple(
            kernel_lemma._gaussian_multiply(
                kernel_lemma._gaussian_multiply(kernel_lemma._phase((i + 1).bit_count()), split_matrix[i][j]),
                kernel_lemma._gaussian_conjugate(kernel_lemma._phase((j + 1).bit_count())),
            )
            for j in range(DIMENSION)
        )
        for i in range(DIMENSION)
    )


def split_matrix_of_automorphism(octonion_block: tuple[tuple[Fraction, ...], ...]) -> GaussianMatrix:
    """The 15 x 15 split-coordinate matrix diag(g, 1, g) of a 7 x 7 automorphism g."""
    rows = [[ZERO] * DIMENSION for _ in range(DIMENSION)]
    for i in range(OCTONION_DIMENSION):
        for j in range(OCTONION_DIMENSION):
            rows[i][j] = _gaussian_rational(octonion_block[i][j])
            rows[8 + i][8 + j] = _gaussian_rational(octonion_block[i][j])
    rows[7][7] = ONE
    return tuple(map(tuple, rows))


def split_matrix_of_derivation(octonion_block: list[list[Fraction]]) -> GaussianMatrix:
    """The 15 x 15 split-coordinate matrix diag(d, 0, d) of a 7 x 7 derivation d."""
    rows = [[ZERO] * DIMENSION for _ in range(DIMENSION)]
    for i in range(OCTONION_DIMENSION):
        for j in range(OCTONION_DIMENSION):
            rows[i][j] = _gaussian_rational(octonion_block[i][j])
            rows[8 + i][8 + j] = _gaussian_rational(octonion_block[i][j])
    return tuple(map(tuple, rows))


def split_matrix_of_boost(cosh: Fraction, sinh: Fraction) -> GaussianMatrix:
    """The split-coordinate matrix of the boost mixing u_k with v_k and fixing the middle coordinate."""
    rows = [[ZERO] * DIMENSION for _ in range(DIMENSION)]
    for k in range(OCTONION_DIMENSION):
        rows[k][k] = rows[k + 8][k + 8] = _gaussian_rational(cosh)
        rows[k][k + 8] = rows[k + 8][k] = _gaussian_rational(sinh)
    rows[7][7] = ONE
    return tuple(map(tuple, rows))


def split_matrix_of_boost_generator() -> GaussianMatrix:
    """The derivative at the identity of the boost: swap u_k and v_k."""
    rows = [[ZERO] * DIMENSION for _ in range(DIMENSION)]
    for k in range(OCTONION_DIMENSION):
        rows[k][k + 8] = rows[k + 8][k] = ONE
    return tuple(map(tuple, rows))


def basis_vector(index: int) -> GaussianVector:
    return tuple(ONE if position == index else ZERO for position in range(DIMENSION))


def congruence_residual(rho: GaussianMatrix, matrix: GaussianMatrix) -> int:
    """The nonzero entry count of rho^T C_(M e_k) rho - C_(e_k), summed over the 15 basis directions k."""
    transposed = kernel_lemma._transpose(rho)
    nonzero = 0
    for k in range(DIMENSION):
        moved = kernel_lemma._c_matrix(kernel_lemma._matrix_vector(matrix, basis_vector(k)))
        lhs = multiply_matrices(multiply_matrices(transposed, moved), rho)
        rhs = kernel_lemma._c_matrix(basis_vector(k))
        nonzero += sum(1 for i in range(DIMENSION) for j in range(DIMENSION) if lhs[i][j] != rhs[i][j])
    return nonzero


def kernel_transport(split_point: list[Fraction], matrix: GaussianMatrix) -> tuple[int, int, bool, int]:
    """Kernel dimensions of C_z and C_(Mz), whether M ker C_z equals ker C_(Mz), and dim(M ker C_z meet ker C_(Mz))."""
    z = kernel_lemma._original_z_from_split(tuple(split_point))
    kernel = kernel_lemma._nullspace(kernel_lemma._c_matrix(z))
    moved_kernel = kernel_lemma._nullspace(kernel_lemma._c_matrix(kernel_lemma._matrix_vector(matrix, z)))
    mapped = [kernel_lemma._matrix_vector(matrix, vector) for vector in kernel]
    equal = len(kernel) == len(moved_kernel) and kernel_lemma._spans_equal(mapped, list(moved_kernel))
    total = kernel_lemma._columns_rank(mapped + list(moved_kernel))
    return len(kernel), len(moved_kernel), equal, len(mapped) + len(moved_kernel) - total


@functools.cache
def unipotent_matrices() -> tuple[GaussianMatrix, GaussianMatrix]:
    """The selected unipotent G_2 automorphism in split and in original coordinates."""
    split = split_matrix_of_automorphism(incidence_census._unipotent_automorphism())
    return split, to_original_coordinates(split)


@functools.cache
def boost_matrices() -> tuple[GaussianMatrix, GaussianMatrix, GaussianMatrix, GaussianMatrix]:
    """The boost b and b with s -> -s, each in split and original coordinates."""
    cosh, sinh = regularity.BOOST
    forward = split_matrix_of_boost(cosh, sinh)
    inverse = split_matrix_of_boost(cosh, -sinh)
    return forward, to_original_coordinates(forward), inverse, to_original_coordinates(inverse)


def residual_task(name: str) -> tuple[str, int]:
    """The congruence residual of one named candidate rho against its group element."""
    unipotent_split, unipotent_original = unipotent_matrices()
    boost_split, boost_original, _, boost_inverse_original = boost_matrices()
    candidates = {
        "unipotent_rho_equals_g_original": (unipotent_original, unipotent_original),
        "unipotent_rho_equals_g_split": (unipotent_split, unipotent_original),
        "boost_rho_equals_b_original": (boost_original, boost_original),
        "boost_rho_equals_b_original_inverse": (boost_inverse_original, boost_original),
        "boost_rho_equals_b_split": (boost_split, boost_original),
        "boost_rho_equals_identity": (identity_matrix(), boost_original),
    }
    rho, matrix = candidates[name]
    return name, congruence_residual(rho, matrix)


def point_task(name: str) -> dict[str, Any]:
    """Kernel transport of both group elements at one canonical point, with the split-coordinate controls."""
    _, unipotent_original = unipotent_matrices()
    unipotent_split, _ = unipotent_matrices()
    boost_split, boost_original, _, _ = boost_matrices()
    cosh, sinh = regularity.BOOST
    split_point = regularity.REPS[name]
    z = kernel_lemma._original_z_from_split(tuple(split_point))
    unipotent_dim, unipotent_moved_dim, unipotent_equal, _ = kernel_transport(split_point, unipotent_original)
    boost_dim, boost_moved_dim, boost_equal, intersection_dimension = kernel_transport(split_point, boost_original)
    split_unipotent_equal = kernel_transport(split_point, unipotent_split)[2]
    split_boost_equal = kernel_transport(split_point, boost_split)[2]
    moved_by_unipotent = regularity.act_g2(incidence_census._unipotent_automorphism(), split_point)
    moved_by_boost = regularity.act_boost(cosh, sinh, split_point)
    return {
        "point": name,
        "support_size_in_split_coordinates": sum(1 for value in split_point if value != 0),
        "kernel_dimension": unipotent_dim,
        "unipotent": {
            "moved_kernel_dimension": unipotent_moved_dim,
            "g_ker_equals_ker_of_gz": unipotent_equal,
            "moved_point_equals_g_original_z": kernel_lemma._original_z_from_split(tuple(moved_by_unipotent))
            == kernel_lemma._matrix_vector(unipotent_original, z),
            "split_matrix_control_g_ker_equals_ker_of_gz": split_unipotent_equal,
        },
        "boost": {
            "moved_kernel_dimension": boost_moved_dim,
            "b_ker_equals_ker_of_bz": boost_equal,
            "dimension_of_b_ker_meet_ker_of_bz": intersection_dimension,
            "moved_point_equals_b_original_z": kernel_lemma._original_z_from_split(tuple(moved_by_boost))
            == kernel_lemma._matrix_vector(boost_original, z),
            "split_matrix_control_b_ker_equals_ker_of_bz": split_boost_equal,
        },
    }


def _fmpq(value: Fraction) -> flint.fmpq:
    return flint.fmpq(value.numerator, value.denominator)


def _flatten(matrix: GaussianMatrix, part: int) -> list[Fraction]:
    return [entry[part] for row in matrix for entry in row]


def equivariance_system() -> tuple[int, int, list[GaussianMatrix]]:
    """Solve C_(X e_k) + R^T C_k + C_k R = 0 over Q: solution dimension, X-projection rank and an X-basis."""
    basis_c = []
    for k in range(DIMENSION):
        matrix = kernel_lemma._c_matrix(basis_vector(k))
        _require(all(entry[1] == 0 for row in matrix for entry in row), "C_(e_k) has a non-rational entry")
        basis_c.append([[int(entry[0]) for entry in row] for row in matrix])
    rows = []
    for k in range(DIMENSION):
        for i in range(DIMENSION):
            for j in range(DIMENSION):
                row = [0] * UNKNOWN_COUNT
                for m in range(DIMENSION):
                    row[m * DIMENSION + k] += basis_c[m][i][j]
                for p in range(DIMENSION):
                    row[DIMENSION * DIMENSION + p * DIMENSION + i] += basis_c[k][p][j]
                    row[DIMENSION * DIMENSION + p * DIMENSION + j] += basis_c[k][i][p]
                rows.append(row)
    _require(len(rows) == EQUATION_COUNT, "the equivariance system has the wrong number of equations")
    solutions, nullity = flint.fmpz_mat(rows).nullspace()
    columns = [[int(solutions[r, c]) for r in range(UNKNOWN_COUNT)] for c in range(nullity)]
    projections: list[GaussianMatrix] = [
        tuple(tuple(_gaussian_rational(column[i * DIMENSION + j]) for j in range(DIMENSION)) for i in range(DIMENSION))
        for column in columns
    ]
    rank = flint.fmpz_mat([column[: DIMENSION * DIMENSION] for column in columns]).rank()
    return nullity, rank, projections


def in_complex_span(basis: list[GaussianMatrix], target: GaussianMatrix) -> bool:
    """Whether target lies in the complex span of a rational basis (real and imaginary parts in its rational span)."""
    base = flint.fmpq_mat([[_fmpq(v) for v in _flatten(matrix, 0)] for matrix in basis]).rank()
    for part in (0, 1):
        augmented = [[_fmpq(v) for v in _flatten(matrix, 0)] for matrix in basis]
        augmented.append([_fmpq(v) for v in _flatten(target, part)])
        if flint.fmpq_mat(augmented).rank() != base:
            return False
    return True


def tangent_rank(generators: list[GaussianMatrix], z: GaussianVector) -> int:
    """The rank of {X z} over the generators X."""
    return kernel_lemma._columns_rank([kernel_lemma._matrix_vector(matrix, z) for matrix in generators])


def orbit_task(
    task: tuple[str, list[GaussianMatrix], list[GaussianMatrix], list[GaussianMatrix], GaussianMatrix],
) -> dict[str, Any]:
    """The orbit dimension at one canonical point against the tangent rank of each generating family."""
    name, nilpotent, derivations, equivariant, boost_generator = task
    split_point = regularity.REPS[name]
    z = kernel_lemma._original_z_from_split(tuple(split_point))
    return {
        "point": name,
        "recorded_orbit_dimension": regularity.DIMS[name],
        "recomputed_orbit_dimension": regularity.orbit_dim(split_point),
        "tangent_rank_nilpotent_derivations": tangent_rank(nilpotent, z),
        "tangent_rank_g2_derivations": tangent_rank(derivations, z),
        "tangent_rank_equivariant_span": tangent_rank(equivariant, z),
        "tangent_rank_equivariant_span_with_boost_generator": tangent_rank([*equivariant, boost_generator], z),
    }


def build_record() -> dict[str, Any]:
    residual_names = (
        "unipotent_rho_equals_g_original",
        "unipotent_rho_equals_g_split",
        "boost_rho_equals_b_original",
        "boost_rho_equals_b_original_inverse",
        "boost_rho_equals_b_split",
        "boost_rho_equals_identity",
    )
    residuals = dict(parallel.ordered_map(residual_task, residual_names, min_items=1))
    points = parallel.ordered_map(point_task, CANONICAL_POINTS, min_items=1)
    _, unipotent_original = unipotent_matrices()
    orthogonality = multiply_matrices(kernel_lemma._transpose(unipotent_original), unipotent_original)
    orthogonal = orthogonality == identity_matrix()

    nullity, projection_rank, projections = equivariance_system()
    derivations = [to_original_coordinates(split_matrix_of_derivation(derivation)) for derivation in regularity.DERS]
    derivations_in_span = [in_complex_span(projections, matrix) for matrix in derivations]
    scaling_in_span = in_complex_span(projections, identity_matrix())
    boost_generator = to_original_coordinates(split_matrix_of_boost_generator())
    boost_generator_in_span = in_complex_span(projections, boost_generator)
    nilpotent = [
        to_original_coordinates(split_matrix_of_derivation(derivation))
        for derivation in regularity.nilpotent_derivations()
    ]
    orbit_rows = parallel.ordered_map(
        orbit_task,
        [(name, nilpotent, derivations, projections, boost_generator) for name in CANONICAL_POINTS],
        min_items=1,
    )

    unipotent_equal = all(point["unipotent"]["g_ker_equals_ker_of_gz"] for point in points)
    unipotent_consistent = all(point["unipotent"]["moved_point_equals_g_original_z"] for point in points)
    boost_failures = [point["point"] for point in points if not point["boost"]["b_ker_equals_ker_of_bz"]]
    witnesses = {
        point["point"]: {
            "support_size_in_split_coordinates": point["support_size_in_split_coordinates"],
            "kernel_dimension": point["kernel_dimension"],
            "dimension_of_b_ker_meet_ker_of_bz": point["boost"]["dimension_of_b_ker_meet_ker_of_bz"],
        }
        for point in points
        if point["point"] in WITNESS_POINTS
    }
    controls_fail = all(not point["unipotent"]["split_matrix_control_g_ker_equals_ker_of_gz"] for point in points)
    mutation_detected = residuals["unipotent_rho_equals_g_split"] > 0 and controls_fail
    baseline_pass = (
        orthogonal
        and residuals["unipotent_rho_equals_g_original"] == 0
        and unipotent_equal
        and unipotent_consistent
        and all(point["boost"]["moved_point_equals_b_original_z"] for point in points)
        and all(residuals[name] > 0 for name in residual_names if name.startswith("boost_"))
        and len(boost_failures) == 6
        and witnesses[SMALLEST_WITNESS]["dimension_of_b_ker_meet_ker_of_bz"] == 6
        and nullity == DIMENSION
        and projection_rank == DIMENSION
        and len(derivations) == G2_DERIVATION_COUNT
        and all(derivations_in_span)
        and scaling_in_span
        and not boost_generator_in_span
        and all(row["recorded_orbit_dimension"] == row["recomputed_orbit_dimension"] for row in orbit_rows)
    )
    return {
        "schema": SCHEMA,
        "inputs": dict(parallel.ordered_map(_hash_path, SOURCE_PATHS, min_items=1)),
        "tools": {"python_flint": flint.__version__},
        "scope": {
            "statement": (
                "the holomorphic kernel C_z of the 15-dimensional representation in original coordinates, the "
                "selected unipotent G_2 automorphism of incidence_census.py, the rational boost of "
                "verify_regularity_independent.py, and the twelve canonical points of that module"
            ),
            "claim_boundary": (
                "The finite checks cover the 15 basis directions, the twelve canonical points and four candidate "
                "matrices rho for the boost; the Lie-algebra solve is exact over Q. A rho outside the candidates is "
                "excluded only by the inference listed under inferred."
            ),
        },
        "unipotent_g2": {
            "g_transpose_g_equals_identity_in_original_coordinates": orthogonal,
            "identity": "C_(g z) = g^(-T) C_z g^(-1), tested as g^T C_(g e_k) g = C_(e_k)",
            "basis_direction_count": DIMENSION,
            "residual_nonzero_entries": residuals["unipotent_rho_equals_g_original"],
            "kernel_transport_at_twelve_points": unipotent_equal,
            "moved_points_agree_with_original_coordinate_action": unipotent_consistent,
        },
        "boost": {
            "parameters_cosh_sinh": [str(value) for value in regularity.BOOST],
            "residual_nonzero_entries": {
                name.removeprefix("boost_rho_equals_"): residuals[name]
                for name in residual_names
                if name.startswith("boost_")
            },
            "points_where_b_ker_differs_from_ker_of_bz": boost_failures,
            "witnesses": witnesses,
            "smallest_witness": SMALLEST_WITNESS,
        },
        "points": points,
        "infinitesimal": {
            "system": "C_(X e_k) + R^T C_k + C_k R = 0 for k = 0..14, unknowns (X, R) in two 15 x 15 blocks",
            "equation_count": EQUATION_COUNT,
            "unknown_count": UNKNOWN_COUNT,
            "solution_dimension": nullity,
            "x_projection_dimension": projection_rank,
            "g2_derivation_count": len(derivations),
            "g2_derivations_in_x_projection": sum(derivations_in_span),
            "scaling_in_x_projection": scaling_in_span,
            "boost_generator_in_x_projection": boost_generator_in_span,
        },
        "orbit_table": orbit_rows,
        "computed": [
            "the congruence residual for the unipotent automorphism with rho = g is zero on 15 basis directions",
            "g^T g = I in original coordinates",
            "g ker C_z = ker C_(g z) at the twelve canonical points",
            "the residual of four candidate rho for the boost is nonzero",
            "b ker C_z differs from ker C_(b z) at six canonical points",
            "the dimension of the solution space of the infinitesimal system and the membership tests",
            "the tangent ranks of the table",
        ],
        "inferred": [
            "the identity for every z follows from linearity of z -> C_z in the basis directions",
            "no matrix rho of any kind satisfies C_(b z) = rho^(-T) C_z rho^(-1) for the boost: a rational "
            "representation rho of the one-parameter group would differentiate to a solution (beta, R) of the "
            "infinitesimal system, and beta lies outside its X-projection (algebraic-group step, not computed)",
        ],
        "mutation_control": {
            "name": "split_coordinate_matrix_as_rho",
            "input_change": "use the split-coordinate matrix of g in place of its original-coordinate matrix as rho",
            "residual_nonzero_entries": residuals["unipotent_rho_equals_g_split"],
            "kernel_transport_lost_at_points": [
                point["point"]
                for point in points
                if not point["unipotent"]["split_matrix_control_g_ker_equals_ker_of_gz"]
            ],
            "detected": mutation_detected,
        },
        "falsifier": (
            "The unipotent congruence residual is nonzero, g^T g differs from I, or g ker C_z differs from "
            "ker C_(g z) at a canonical point; the boost residual vanishes for a candidate rho or b ker C_z equals "
            "ker C_(b z) at the smallest witness; the infinitesimal solution space has a dimension other than 15, "
            "omits a G_2 derivation or the scaling, or contains the boost generator; or the split-coordinate matrix "
            "leaves a zero residual."
        ),
        "pass": baseline_pass and mutation_detected,
    }


def _record_bytes(record: dict[str, Any]) -> bytes:
    return (json.dumps(record, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _self_test(record: dict[str, Any]) -> None:
    _require(bool(record["pass"]), "the kernel-equivariance record failed")
    _require(bool(record["mutation_control"]["detected"]), "the split-coordinate matrix left a zero residual")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="write the deterministic JSON record")
    parser.add_argument("--check", type=Path, help="compare a deterministic record byte for byte")
    parser.add_argument("--self-test", action="store_true", help="run the baseline and mutation checks")
    arguments = parser.parse_args()
    if sum((arguments.out is not None, arguments.check is not None, arguments.self_test)) != 1:
        parser.error("select exactly one of --out, --check, or --self-test")
    record = build_record()
    _self_test(record)
    rendered = _record_bytes(record)
    if arguments.out is not None:
        arguments.out.write_bytes(rendered)
    elif arguments.check is not None:
        _require(arguments.check.read_bytes() == rendered, f"{arguments.check} differs from the regenerated record")


if __name__ == "__main__":
    main()
