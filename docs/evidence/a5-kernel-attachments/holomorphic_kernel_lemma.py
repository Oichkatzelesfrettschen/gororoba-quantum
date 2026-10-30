"""Verify the holomorphic C_z kernel description on retained A_5 samples."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from collections import defaultdict
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from fractions import Fraction
from functools import partial
from pathlib import Path
from typing import Any, TypeAlias

import flint

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
NULLITY_EIGHT = HERE.parent / "a5-kernel-bundles-nullity8"
KERNEL_BUNDLES = HERE.parent / "a5-kernel-bundles"
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import parallel  # noqa: E402
from cd_core import cd_sign  # noqa: E402

SCHEMA = "a5-kernel-attachments-holomorphic-kernel-lemma-v1"
PATH_SUPPORTED_RESULT = HERE / "path-supported-basepoints-result.json"
BOUNDARY_RESULT = NULLITY_EIGHT / "boundary-specializations-result.json"
FRAMES_RESULT = KERNEL_BUNDLES / "frames-result.json"
SOURCE_PATHS = (
    HERE / "holomorphic_kernel_lemma.py",
    HERE / "path_supported_basepoints.py",
    PATH_SUPPORTED_RESULT,
    HERE / "partner_purity.py",
    HERE / "partner-purity-result.json",
    NULLITY_EIGHT / "boundary_specializations.py",
    BOUNDARY_RESULT,
    KERNEL_BUNDLES / "kernel_frames.py",
    FRAMES_RESULT,
    ROOT / "gororoba_quantum" / "cd_core.py",
)
COMPLEX_DIMENSION = 15
BORDERED_DIMENSION = COMPLEX_DIMENSION + 1
OPEN_SAMPLE_PARAMETERS = (1, 2, 3)
EXPECTED_C_RANK = {8: 10, 12: 8, 16: 6}
EXPECTED_BORDERED_RANK = {8: 12, 12: 10, 16: 8}

Gaussian: TypeAlias = tuple[Fraction, Fraction]
GaussianVector: TypeAlias = tuple[Gaussian, ...]
GaussianMatrix: TypeAlias = tuple[GaussianVector, ...]
RationalVector: TypeAlias = tuple[Fraction, ...]

ZERO: Gaussian = (Fraction(0), Fraction(0))
ONE: Gaussian = (Fraction(1), Fraction(0))
I_UNIT: Gaussian = (Fraction(0), Fraction(1))


@dataclass(frozen=True)
class SampleTask:
    kind: str
    name: str
    expected_real_nullity: int
    z: GaussianVector
    metadata: tuple[tuple[str, Any], ...]


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _hash_path(path: Path) -> tuple[str, str]:
    return str(path.relative_to(ROOT)), _sha256(path)


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    _require(isinstance(value, dict), f"{path.name} does not hold a JSON object")
    return value


def _gaussian_add(left: Gaussian, right: Gaussian) -> Gaussian:
    return left[0] + right[0], left[1] + right[1]


def _gaussian_negate(value: Gaussian) -> Gaussian:
    return -value[0], -value[1]


def _gaussian_subtract(left: Gaussian, right: Gaussian) -> Gaussian:
    return left[0] - right[0], left[1] - right[1]


def _gaussian_multiply(left: Gaussian, right: Gaussian) -> Gaussian:
    return left[0] * right[0] - left[1] * right[1], left[0] * right[1] + left[1] * right[0]


def _gaussian_conjugate(value: Gaussian) -> Gaussian:
    return value[0], -value[1]


def _gaussian_inverse(value: Gaussian) -> Gaussian:
    norm = value[0] * value[0] + value[1] * value[1]
    if norm == 0:
        raise ZeroDivisionError("cannot invert zero in Q(i)")
    return value[0] / norm, -value[1] / norm


def _gaussian_scale(value: Gaussian, scalar: Fraction | int) -> Gaussian:
    rational = Fraction(scalar)
    return rational * value[0], rational * value[1]


def _gaussian_sum(values: Iterable[Gaussian]) -> Gaussian:
    total = ZERO
    for value in values:
        total = _gaussian_add(total, value)
    return total


def _gaussian_text(value: Gaussian) -> list[str]:
    return [str(value[0]), str(value[1])]


def _coordinate_sha256(vector: GaussianVector) -> str:
    payload = json.dumps([_gaussian_text(value) for value in vector], separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _rref(matrix: GaussianMatrix) -> tuple[GaussianMatrix, tuple[int, ...]]:
    if not matrix:
        return (), ()
    width = len(matrix[0])
    _require(all(len(row) == width for row in matrix), "Gaussian matrix rows have inconsistent lengths")
    reduced = [list(row) for row in matrix]
    pivot_columns: list[int] = []
    pivot_row = 0
    for column in range(width):
        selected = next((row for row in range(pivot_row, len(reduced)) if reduced[row][column] != ZERO), None)
        if selected is None:
            continue
        reduced[pivot_row], reduced[selected] = reduced[selected], reduced[pivot_row]
        inverse = _gaussian_inverse(reduced[pivot_row][column])
        reduced[pivot_row] = [_gaussian_multiply(value, inverse) for value in reduced[pivot_row]]
        for row in range(len(reduced)):
            if row == pivot_row:
                continue
            coefficient = reduced[row][column]
            if coefficient != ZERO:
                reduced[row] = [
                    _gaussian_subtract(value, _gaussian_multiply(coefficient, pivot_value))
                    for value, pivot_value in zip(reduced[row], reduced[pivot_row], strict=True)
                ]
        pivot_columns.append(column)
        pivot_row += 1
        if pivot_row == len(reduced):
            break
    return tuple(tuple(row) for row in reduced), tuple(pivot_columns)


def _rank(matrix: GaussianMatrix) -> int:
    return len(_rref(matrix)[1])


def _nullspace(matrix: GaussianMatrix) -> tuple[GaussianVector, ...]:
    _require(bool(matrix), "nullspace input needs at least one row")
    width = len(matrix[0])
    reduced, pivot_columns = _rref(matrix)
    free_columns = tuple(column for column in range(width) if column not in pivot_columns)
    basis: list[GaussianVector] = []
    for free_column in free_columns:
        vector = [ZERO] * width
        vector[free_column] = ONE
        for row, pivot_column in enumerate(pivot_columns):
            vector[pivot_column] = _gaussian_negate(reduced[row][free_column])
        basis.append(tuple(vector))
    return tuple(basis)


def _matrix_vector(matrix: GaussianMatrix, vector: GaussianVector) -> GaussianVector:
    _require(all(len(row) == len(vector) for row in matrix), "matrix-vector dimensions disagree")
    return tuple(
        _gaussian_sum(_gaussian_multiply(value, coordinate) for value, coordinate in zip(row, vector, strict=True))
        for row in matrix
    )


def _columns_rank(columns: Sequence[GaussianVector]) -> int:
    if not columns:
        return 0
    height = len(columns[0])
    _require(all(len(column) == height for column in columns), "column heights disagree")
    rows = tuple(tuple(column[row] for column in columns) for row in range(height))
    return _rank(rows)


def _spans_equal(left: Sequence[GaussianVector], right: Sequence[GaussianVector]) -> bool:
    left_rank = _columns_rank(left)
    right_rank = _columns_rank(right)
    return left_rank == right_rank == _columns_rank((*left, *right))


def _linear_combination(columns: Sequence[GaussianVector], coefficients: GaussianVector) -> GaussianVector:
    _require(len(columns) == len(coefficients), "linear-combination coefficient count disagrees")
    height = len(columns[0])
    return tuple(
        _gaussian_sum(
            _gaussian_multiply(coefficient, column[row])
            for column, coefficient in zip(columns, coefficients, strict=True)
        )
        for row in range(height)
    )


def _hermitian_pair(left: GaussianVector, right: GaussianVector) -> Gaussian:
    _require(len(left) == len(right), "Hermitian-pairing dimensions disagree")
    return _gaussian_sum(
        _gaussian_multiply(_gaussian_conjugate(left_value), right_value)
        for left_value, right_value in zip(left, right, strict=True)
    )


def _realified_flint_rank(matrix: GaussianMatrix) -> int:
    row_count = len(matrix)
    column_count = len(matrix[0])
    rational_rows: list[list[flint.fmpq]] = []
    for row in matrix:
        rational_rows.append(
            [flint.fmpq(value[0].numerator, value[0].denominator) for value in row]
            + [flint.fmpq(-value[1].numerator, value[1].denominator) for value in row]
        )
    for row in matrix:
        rational_rows.append(
            [flint.fmpq(value[1].numerator, value[1].denominator) for value in row]
            + [flint.fmpq(value[0].numerator, value[0].denominator) for value in row]
        )
    real_rank = int(
        flint.fmpq_mat(2 * row_count, 2 * column_count, list(itertools.chain.from_iterable(rational_rows))).rank()
    )
    _require(real_rank % 2 == 0, "realified complex matrix has odd rational rank")
    return real_rank // 2


def _phase(power: int) -> Gaussian:
    return (ONE, I_UNIT, _gaussian_negate(ONE), _gaussian_negate(I_UNIT))[power % 4]


def _original_z_from_split(split_point: RationalVector) -> GaussianVector:
    _require(len(split_point) == COMPLEX_DIMENSION, "split point must have fifteen coordinates")
    return tuple(_gaussian_scale(_phase(index.bit_count()), value) for index, value in enumerate(split_point, start=1))


def _c_matrix(z: GaussianVector) -> GaussianMatrix:
    _require(len(z) == COMPLEX_DIMENSION, "z must have fifteen coordinates")
    rows: list[GaussianVector] = []
    for row in range(1, BORDERED_DIMENSION):
        values: list[Gaussian] = []
        for column in range(1, BORDERED_DIMENSION):
            product = row ^ column
            values.append(ZERO if product == 0 else _gaussian_scale(z[product - 1], cd_sign(16, product, column)))
        rows.append(tuple(values))
    return tuple(rows)


def _transpose(matrix: GaussianMatrix) -> GaussianMatrix:
    return tuple(tuple(matrix[row][column] for row in range(len(matrix))) for column in range(len(matrix[0])))


def _is_skew(matrix: GaussianMatrix) -> bool:
    transposed = _transpose(matrix)
    return all(
        _gaussian_add(matrix[row][column], transposed[row][column]) == ZERO
        for row in range(len(matrix))
        for column in range(len(matrix[0]))
    )


def _bordered_matrix(z: GaussianVector, c_matrix: GaussianMatrix) -> GaussianMatrix:
    top = (ZERO, *(_gaussian_negate(_gaussian_conjugate(value)) for value in z))
    lower = tuple((_gaussian_conjugate(z[row]), *c_matrix[row]) for row in range(COMPLEX_DIMENSION))
    return (top, *lower)


def _orthogonal_complement(
    kernel: Sequence[GaussianVector], pairing_vector: GaussianVector
) -> tuple[GaussianVector, ...]:
    pairing_row = tuple(_hermitian_pair(pairing_vector, basis_vector) for basis_vector in kernel)
    coordinate_kernel = _nullspace((pairing_row,))
    return tuple(_linear_combination(kernel, coefficients) for coefficients in coordinate_kernel)


def _independent_kernel_vector(z: GaussianVector, kernel: Sequence[GaussianVector]) -> tuple[int, GaussianVector]:
    selected = next(
        ((index, vector) for index, vector in enumerate(kernel) if _columns_rank((z, vector)) == 2),
        None,
    )
    if selected is None:
        raise RuntimeError("ker C_z contains no recorded vector independent of z")
    return selected


def _analyze_sample(task: SampleTask) -> dict[str, Any]:
    expected_c_rank = EXPECTED_C_RANK[task.expected_real_nullity]
    expected_bordered_rank = EXPECTED_BORDERED_RANK[task.expected_real_nullity]
    c_matrix = _c_matrix(task.z)
    bordered_matrix = _bordered_matrix(task.z, c_matrix)
    c_rank = _rank(c_matrix)
    c_flint_rank = _realified_flint_rank(c_matrix)
    bordered_rank = _rank(bordered_matrix)
    bordered_flint_rank = _realified_flint_rank(bordered_matrix)
    c_kernel = _nullspace(c_matrix)
    bordered_kernel = _nullspace(bordered_matrix)
    z_annihilated = all(value == ZERO for value in _matrix_vector(c_matrix, task.z))
    hermitian_norm = _hermitian_pair(task.z, task.z)
    pairing_row = tuple(_hermitian_pair(task.z, vector) for vector in c_kernel)
    pairing_rank = 0 if all(value == ZERO for value in pairing_row) else 1
    complement = _orthogonal_complement(c_kernel, task.z)
    embedded_complement = tuple((ZERO, *vector) for vector in complement)
    complement_annihilated = all(
        all(value == ZERO for value in _matrix_vector(bordered_matrix, vector)) for vector in embedded_complement
    )
    bordered_kernel_equals_complement = _spans_equal(bordered_kernel, embedded_complement)
    c_kernel_equals_direct_sum = _spans_equal(c_kernel, (task.z, *complement))
    direct_sum_rank = _columns_rank((task.z, *complement))
    bordered_kernel_scalar_zero = all(vector[0] == ZERO for vector in bordered_kernel)

    mutated_basis_index, mutated_pairing_vector = _independent_kernel_vector(task.z, c_kernel)
    mutated_complement = _orthogonal_complement(c_kernel, mutated_pairing_vector)
    mutated_embedded = tuple((ZERO, *vector) for vector in mutated_complement)
    mutated_matches_bordered_kernel = _spans_equal(bordered_kernel, mutated_embedded)
    mutation_detected = (
        _columns_rank((task.z, mutated_pairing_vector)) == 2
        and len(mutated_complement) == len(complement)
        and not mutated_matches_bordered_kernel
    )

    expected_c_kernel_dimension = COMPLEX_DIMENSION - expected_c_rank
    expected_bordered_kernel_dimension = BORDERED_DIMENSION - expected_bordered_rank
    passed = (
        _is_skew(c_matrix)
        and _is_skew(bordered_matrix)
        and c_rank == c_flint_rank == expected_c_rank
        and bordered_rank == bordered_flint_rank == expected_bordered_rank
        and len(c_kernel) == expected_c_kernel_dimension
        and len(bordered_kernel) == expected_bordered_kernel_dimension
        and z_annihilated
        and hermitian_norm[1] == 0
        and hermitian_norm[0] > 0
        and pairing_rank == 1
        and len(complement) == expected_bordered_kernel_dimension
        and complement_annihilated
        and bordered_kernel_equals_complement
        and c_kernel_equals_direct_sum
        and direct_sum_rank == expected_c_kernel_dimension
        and bordered_kernel_scalar_zero
        and mutation_detected
    )
    return {
        "kind": task.kind,
        "name": task.name,
        **dict(task.metadata),
        "expected_real_nullity": task.expected_real_nullity,
        "z_sha256": _coordinate_sha256(task.z),
        "hermitian_norm": _gaussian_text(hermitian_norm),
        "c_rank_gaussian_rref": c_rank,
        "c_rank_flint_realification": c_flint_rank,
        "expected_c_rank": expected_c_rank,
        "c_kernel_dimension": len(c_kernel),
        "z_in_c_kernel": z_annihilated,
        "pairing_restriction_rank": pairing_rank,
        "bordered_rank_gaussian_rref": bordered_rank,
        "bordered_rank_flint_realification": bordered_flint_rank,
        "expected_bordered_rank": expected_bordered_rank,
        "bordered_kernel_dimension": len(bordered_kernel),
        "bordered_kernel_scalar_coordinates_zero": bordered_kernel_scalar_zero,
        "hermitian_complement_dimension": len(complement),
        "hermitian_complement_annihilated_by_bordered_matrix": complement_annihilated,
        "bordered_kernel_equals_hermitian_complement": bordered_kernel_equals_complement,
        "c_kernel_equals_z_plus_bordered_kernel": c_kernel_equals_direct_sum,
        "direct_sum_rank": direct_sum_rank,
        "mutation_control": {
            "name": "replace_pairing_vector_by_independent_c_kernel_vector",
            "selected_c_kernel_basis_column": mutated_basis_index,
            "selected_vector_sha256": _coordinate_sha256(mutated_pairing_vector),
            "selected_vector_independent_of_z": _columns_rank((task.z, mutated_pairing_vector)) == 2,
            "mutated_complement_dimension": len(mutated_complement),
            "mutated_complement_equals_bordered_kernel": mutated_matches_bordered_kernel,
            "detected": mutation_detected,
        },
        "pass": passed,
    }


def _parse_vector(values: Sequence[str]) -> RationalVector:
    return tuple(Fraction(value) for value in values)


def _evaluate_coefficients(coefficients: Sequence[RationalVector], parameter: int) -> RationalVector:
    padded = (
        *coefficients,
        *(tuple(Fraction(0) for _index in range(COMPLEX_DIMENSION)) for _ in range(3 - len(coefficients))),
    )
    return tuple(
        padded[0][coordinate] + parameter * padded[1][coordinate] + parameter * parameter * padded[2][coordinate]
        for coordinate in range(COMPLEX_DIMENSION)
    )


def _basepoint_task(item: tuple[int, RationalVector, tuple[str, ...]]) -> SampleTask:
    index, point, incidences = item
    return SampleTask(
        kind="path_supported_basepoint",
        name=f"basepoint-{index + 1:02d}",
        expected_real_nullity=12,
        z=_original_z_from_split(point),
        metadata=(("incidences", list(incidences)), ("split_point", [str(value) for value in point])),
    )


def _path_sample_task(item: tuple[dict[str, Any], int]) -> SampleTask:
    path, parameter = item
    sample_parameters = tuple(int(value) for value in path["curve"]["open_sample_parameters"])
    _require(sample_parameters == OPEN_SAMPLE_PARAMETERS, f"{path['incidence']} {path['approach']} sample set changed")
    coefficients = tuple(_parse_vector(vector) for vector in path["split_path_coefficients"])
    point = _evaluate_coefficients(coefficients, parameter)
    return SampleTask(
        kind="retained_arc_sample",
        name=f"{path['incidence']}/{path['approach']}/t={parameter}",
        expected_real_nullity=8,
        z=_original_z_from_split(point),
        metadata=(
            ("incidence", path["incidence"]),
            ("approach", path["approach"]),
            ("parameter", parameter),
        ),
    )


def _nullity_sixteen_task(sign: int) -> SampleTask:
    w = (ONE, I_UNIT, *(ZERO for _index in range(5)))
    signed_i = _gaussian_scale(I_UNIT, sign)
    z = (*w, ZERO, *(_gaussian_multiply(signed_i, value) for value in w))
    orbit = "N_+" if sign == 1 else "N_-"
    return SampleTask(
        kind="nullity_sixteen_fixture",
        name=f"{orbit}/coordinate-isotropic-plane-1-2",
        expected_real_nullity=16,
        z=z,
        metadata=(("orbit", orbit), ("fixture", [1, 2])),
    )


def _path_rows(boundary_record: dict[str, Any]) -> tuple[dict[str, Any], ...]:
    return tuple(itertools.chain.from_iterable(incidence["approaches"] for incidence in boundary_record["incidences"]))


def _row_pass(row: dict[str, Any]) -> bool:
    return bool(row["pass"])


def _mutation_detected(row: dict[str, Any]) -> bool:
    return bool(row["mutation_control"]["detected"])


def _rows_of_kind(row: dict[str, Any], kind: str) -> dict[str, Any] | None:
    return row if row["kind"] == kind else None


def _rank_pair(row: dict[str, Any]) -> tuple[int, int]:
    return int(row["expected_real_nullity"]), int(row["c_rank_gaussian_rref"])


def _frame_fixture(row: dict[str, Any]) -> tuple[str, tuple[int, ...]]:
    return str(row["orbit"]), tuple(int(value) for value in row["representative"]["fixture"])


def build_record() -> dict[str, Any]:
    path_supported_record = _load_json(PATH_SUPPORTED_RESULT)
    boundary_record = _load_json(BOUNDARY_RESULT)
    frames_record = _load_json(FRAMES_RESULT)
    _require(path_supported_record.get("pass") is True, "path-supported basepoint input does not pass")
    _require(boundary_record.get("pass") is True, "boundary-specialization input does not pass")
    _require(frames_record.get("pass") is True, "kernel-frame input does not pass")
    retained_nullity_sixteen_fixtures = set(
        parallel.ordered_map(_frame_fixture, frames_record["nullity_sixteen"]["orbits"], min_items=1)
    )
    fixture_scope_verified = retained_nullity_sixteen_fixtures == {("N_+", (1, 2)), ("N_-", (1, 2))}
    _require(fixture_scope_verified, "retained nullity-sixteen representatives changed")

    path_rows = _path_rows(boundary_record)
    _require(len(path_rows) == 33, "retained path count differs from 33")
    selected_groups: dict[RationalVector, list[str]] = defaultdict(list)
    for incidence in path_supported_record["incidences"]:
        selected_groups[_parse_vector(incidence["selected_point"])].append(str(incidence["incidence"]))
    selected_points = tuple(sorted(selected_groups))
    path_endpoints = {_parse_vector(path["split_path_coefficients"][0]) for path in path_rows}
    basepoint_coverage_verified = set(selected_points) == path_endpoints
    _require(len(selected_points) == 9, "path-supported basepoint count differs from nine")
    _require(basepoint_coverage_verified, "retained path endpoints differ from the nine selected basepoints")

    basepoint_inputs = tuple(
        (index, point, tuple(sorted(selected_groups[point]))) for index, point in enumerate(selected_points)
    )
    basepoint_tasks = tuple(parallel.ordered_map(_basepoint_task, basepoint_inputs, min_items=1))
    path_sample_inputs = tuple(itertools.product(path_rows, OPEN_SAMPLE_PARAMETERS))
    path_sample_tasks = tuple(parallel.ordered_map(_path_sample_task, path_sample_inputs, min_items=1))
    nullity_sixteen_tasks = tuple(parallel.ordered_map(_nullity_sixteen_task, (-1, 1), min_items=1))
    tasks = (*basepoint_tasks, *path_sample_tasks, *nullity_sixteen_tasks)
    rows = tuple(parallel.ordered_map(_analyze_sample, tasks, min_items=1))

    basepoint_rows = tuple(
        filter(
            None,
            parallel.ordered_map(partial(_rows_of_kind, kind="path_supported_basepoint"), rows, min_items=1),
        )
    )
    arc_rows = tuple(
        filter(
            None,
            parallel.ordered_map(partial(_rows_of_kind, kind="retained_arc_sample"), rows, min_items=1),
        )
    )
    nullity_sixteen_rows = tuple(
        filter(
            None,
            parallel.ordered_map(partial(_rows_of_kind, kind="nullity_sixteen_fixture"), rows, min_items=1),
        )
    )
    pass_flags = parallel.ordered_map(_row_pass, rows, min_items=1)
    mutation_flags = parallel.ordered_map(_mutation_detected, rows, min_items=1)
    observed_rank_pairs = set(parallel.ordered_map(_rank_pair, rows, min_items=1))
    expected_rank_pairs = set(EXPECTED_C_RANK.items())
    input_rows = parallel.ordered_map(_hash_path, SOURCE_PATHS, min_items=1)
    passed = (
        basepoint_coverage_verified
        and fixture_scope_verified
        and len(basepoint_rows) == 9
        and len(arc_rows) == 99
        and len(nullity_sixteen_rows) == 2
        and observed_rank_pairs == expected_rank_pairs
        and all(pass_flags)
        and all(mutation_flags)
    )
    return {
        "schema": SCHEMA,
        "inputs": dict(input_rows),
        "tools": {"python_flint": flint.__version__},
        "scope": {
            "statement": (
                "For every retained sample, ker C_z is the orthogonal direct sum of C z and the bordered kernel, "
                "where orthogonality uses the positive Hermitian pairing."
            ),
            "sample_boundary": (
                "The record covers all nine path-supported nullity-twelve basepoints, parameters 1, 2, and 3 on "
                "all 33 retained nullity-eight arcs, and the coordinate-isotropic-plane representative of each "
                "nullity-sixteen orbit. It verifies the lemma on those exact samples rather than proving it on every "
                "point of the strata."
            ),
        },
        "summary": {
            "path_supported_basepoint_count": len(basepoint_rows),
            "retained_path_count": len(path_rows),
            "retained_arc_sample_count": len(arc_rows),
            "nullity_sixteen_fixture_count": len(nullity_sixteen_rows),
            "sample_count": len(rows),
            "basepoint_coverage_verified": basepoint_coverage_verified,
            "nullity_sixteen_fixture_scope_verified": fixture_scope_verified,
            "c_rank_by_real_nullity": {str(nullity): rank for nullity, rank in sorted(observed_rank_pairs)},
            "all_mutations_detected": all(mutation_flags),
        },
        "basepoints": list(basepoint_rows),
        "retained_arc_samples": list(arc_rows),
        "nullity_sixteen_fixtures": list(nullity_sixteen_rows),
        "mutation": {
            "input_change": (
                "At each sample, replace z in the Hermitian pairing by the first recorded vector of ker C_z that is "
                "linearly independent of z before recomputing the complement."
            ),
            "sample_count": len(rows),
            "detected_count": sum(bool(value) for value in mutation_flags),
            "all_detected": all(mutation_flags),
        },
        "falsifier": (
            "Any retained sample has the wrong C_z rank; C_z z is nonzero; ker A differs from the Hermitian "
            "complement of z in ker C_z; ker C_z differs from C z plus ker A; the Gaussian-rational and FLINT "
            "realification ranks disagree; or replacing z by an independent vector of ker C_z leaves the complement "
            "equal to ker A."
        ),
        "pass": passed,
    }


def _record_bytes(record: dict[str, Any]) -> bytes:
    return (json.dumps(record, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _self_test(record: dict[str, Any]) -> None:
    _require(bool(record["pass"]), "the holomorphic-kernel lemma record failed")
    _require(record["summary"]["path_supported_basepoint_count"] == 9, "basepoint count changed")
    _require(record["summary"]["retained_arc_sample_count"] == 99, "retained arc sample count changed")
    _require(record["summary"]["nullity_sixteen_fixture_count"] == 2, "nullity-sixteen fixture count changed")
    _require(record["summary"]["c_rank_by_real_nullity"] == {"8": 10, "12": 8, "16": 6}, "C_z ranks changed")
    _require(bool(record["mutation"]["all_detected"]), "a pairing-vector mutation survived")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="write the deterministic JSON record")
    parser.add_argument("--check", type=Path, help="compare a deterministic record byte for byte")
    parser.add_argument("--self-test", action="store_true", help="run the baseline and mutation checks")
    arguments = parser.parse_args()
    selected_modes = sum((arguments.out is not None, arguments.check is not None, arguments.self_test))
    if selected_modes != 1:
        parser.error("select exactly one of --out, --check, or --self-test")
    record = build_record()
    _self_test(record)
    rendered = _record_bytes(record)
    if arguments.out is not None:
        arguments.out.write_bytes(rendered)
    elif arguments.check is not None:
        retained = arguments.check.read_bytes()
        _require(
            retained == rendered,
            f"record mismatch: retained={hashlib.sha256(retained).hexdigest()} "
            f"fresh={hashlib.sha256(rendered).hexdigest()}",
        )


if __name__ == "__main__":
    main()
