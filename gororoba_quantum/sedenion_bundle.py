"""Construct local charts of the sedenion unit zero-divisor pair bundle.

For orthonormal imaginary octonions a,b, set q=a*b and H=span(1,a,b,q).
The base is x=(a,b)/sqrt(2). Its partners are (c,-q*c)/sqrt(2) for unit
c in H-perp. Projected coordinate vectors supply seven quaternion frames;
the overlap matrices are left quaternion multiplication, so right quaternion
multiplication defines the principal SU(2) action. The algebraic derivation
belongs to CLAIM_BOUNDARIES.md; finite checks here validate the implementation.
"""

from __future__ import annotations

import json
import math
import platform
from fractions import Fraction
from itertools import product

import numpy as np

import parallel
from cd_core import cd_multiply, cd_multiply_exact, cd_sign, sedenion_zero_divisor_corpus

# Fixed 8- and 16-coordinate products accumulate at most 256 signed terms.
# This budget exceeds that accumulation error while keeping invalid bases out.
NUMERIC_TOLERANCE = 4096 * np.finfo(float).eps
# Dividing a projection by its length amplifies cancellation. Restrict the
# numerical chart to lengths at least eps^(1/4), then check its residuals.
# The largest projection has length at least sqrt(4/7) for an exact base;
# floating-point bases also need the residual admission checks below.
MIN_PATCH_NORM = float(np.finfo(float).eps ** 0.25)
DENSE_SEED = 20261011
DENSE_CASES = 24
ExactVector = tuple[Fraction, ...]


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _real_vector(value: object, length: int, name: str) -> np.ndarray:
    raw = np.asarray(value)
    if raw.shape != (length,) or raw.dtype.kind not in "biuf":
        raise ValueError(f"{name} must contain {length} real coordinates")
    if not np.all(np.isfinite(raw)):
        raise ValueError(f"{name} must contain finite coordinates")
    float_limit = np.finfo(float).max
    if np.any(raw > float_limit) or np.any(raw < -float_limit):
        raise ValueError(f"{name} must contain float64-representable coordinates")
    vector = np.asarray(raw, dtype=float)
    return vector.copy()


def _unit_vector(value: object, length: int, name: str) -> np.ndarray:
    vector = _real_vector(value, length, name)
    if float(np.max(np.abs(vector))) > 1.0 + NUMERIC_TOLERANCE or abs(float(vector @ vector) - 1.0) > NUMERIC_TOLERANCE:
        raise ValueError(f"{name} must have unit norm")
    return vector


def _validated_base(first: object, second: object) -> tuple[np.ndarray, np.ndarray]:
    first_vector = _unit_vector(first, 8, "first octonion")
    second_vector = _unit_vector(second, 8, "second octonion")
    if abs(float(first_vector[0])) > NUMERIC_TOLERANCE or abs(float(second_vector[0])) > NUMERIC_TOLERANCE:
        raise ValueError("base octonions must be imaginary")
    if abs(float(first_vector @ second_vector)) > NUMERIC_TOLERANCE:
        raise ValueError("base octonions must be orthogonal")
    return first_vector, second_vector


def _multiply(first: np.ndarray, second: np.ndarray) -> np.ndarray:
    return np.asarray(cd_multiply(len(first), first.tolist(), second.tolist()))


def _left_matrix(vector: np.ndarray) -> np.ndarray:
    identity = np.eye(len(vector))
    return np.column_stack([_multiply(vector, column) for column in identity])


def _base_geometry(first: object, second: object) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    first_vector, second_vector = _validated_base(first, second)
    quaternion_unit = _multiply(first_vector, second_vector)
    quaternion_basis = np.column_stack((np.eye(8)[0], first_vector, second_vector, quaternion_unit))
    projector = np.eye(8) - quaternion_basis @ quaternion_basis.T
    return first_vector, second_vector, quaternion_unit, projector


def complement_projector(first: object, second: object) -> np.ndarray:
    """Project onto the four-dimensional real complement of span(1,a,b,a*b)."""
    return _base_geometry(first, second)[3]


def _kernel_lift(quaternion_unit: np.ndarray, complement_map: np.ndarray) -> np.ndarray:
    return np.vstack((complement_map, -_left_matrix(quaternion_unit) @ complement_map)) / math.sqrt(2)


def annihilator_projector(first: object, second: object) -> np.ndarray:
    """Orthogonal projector onto ker L_x for the unit sedenion x=(a,b)/sqrt(2)."""
    _, _, quaternion_unit, projector = _base_geometry(first, second)
    lift = _kernel_lift(quaternion_unit, projector)
    return lift @ lift.T


def _chart_residuals(
    first: np.ndarray,
    second: np.ndarray,
    quaternion_unit: np.ndarray,
    projector: np.ndarray,
    frame: np.ndarray,
) -> dict[str, float]:
    lift = _kernel_lift(quaternion_unit, frame)
    element = np.concatenate((first, second)) / math.sqrt(2)
    products = np.column_stack([_multiply(element, partner) for partner in lift.T])
    # Operator norms bound every unit fiber coordinate, including dense ones.
    return {
        "section_complement": float(np.linalg.norm(projector @ frame[:, 0] - frame[:, 0])),
        "frame_complement": float(np.linalg.norm(projector @ frame - frame, ord=2)),
        "frame_orthogonality": float(np.linalg.norm(frame.T @ frame - np.eye(4), ord=2)),
        "frame_projector": float(np.linalg.norm(frame @ frame.T - projector, ord=2)),
        "lift_orthogonality": float(np.linalg.norm(lift.T @ lift - np.eye(4), ord=2)),
        "lift_annihilation": float(np.linalg.norm(products, ord=2)),
    }


def chart_frame(first: object, second: object, chart: int) -> np.ndarray:
    """Return [c,a*c,b*c,(a*b)*c] on a numerically conditioned coordinate chart.

    Mathematical chart r has ||P e_r||>0. The floating-point evaluator rejects
    projections below MIN_PATCH_NORM and normalized frames whose complement,
    Gram, projector, or annihilator residual exceeds NUMERIC_TOLERANCE. The
    largest projection is best conditioned; accepted approximate bases still
    require residual admission. Coordinates are real quaternions.
    """
    if isinstance(chart, bool) or not isinstance(chart, int) or not 1 <= chart <= 7:
        raise ValueError("chart must be an imaginary coordinate index from 1 through 7")
    first_vector, second_vector, quaternion_unit, projector = _base_geometry(first, second)
    projected = projector[:, chart]
    norm = float(np.linalg.norm(projected))
    if norm < MIN_PATCH_NORM:
        raise ValueError("coordinate projection is degenerate or below the numerical chart conditioning bound")
    section = projected / norm
    frame = np.column_stack(
        (
            section,
            _multiply(first_vector, section),
            _multiply(second_vector, section),
            _multiply(quaternion_unit, section),
        )
    )
    residuals = _chart_residuals(first_vector, second_vector, quaternion_unit, projector, frame)
    failed = {name: value for name, value in residuals.items() if value > NUMERIC_TOLERANCE}
    if failed:
        raise ValueError(f"coordinate chart residuals exceed the numerical tolerance: {failed}")
    return frame


def quaternion_left_matrix(quaternion: object) -> np.ndarray:
    """Real 4x4 matrix for left multiplication by a unit quaternion."""
    scalar, first, second, third = _unit_vector(quaternion, 4, "quaternion")
    return np.asarray(
        [
            [scalar, -first, -second, -third],
            [first, scalar, -third, second],
            [second, third, scalar, -first],
            [third, -second, first, scalar],
        ]
    )


def chart_transition(first: object, second: object, source: int, target: int) -> np.ndarray:
    """Coordinates in target map to source by F_source.T @ F_target = L(h)."""
    source_frame = chart_frame(first, second, source)
    target_frame = chart_frame(first, second, target)
    return source_frame.T @ target_frame


def cayley_frame(first: object, second: object, section: object) -> np.ndarray:
    """Octonion automorphism with columns [1,a,b,a*b,c,a*c,b*c,(a*b)*c]."""
    first_vector, second_vector, quaternion_unit, projector = _base_geometry(first, second)
    unit_section = _unit_vector(section, 8, "Cayley frame section")
    if float(np.max(np.abs(projector @ unit_section - unit_section))) > NUMERIC_TOLERANCE:
        raise ValueError("Cayley frame section must lie in the quaternion complement")
    return np.column_stack(
        (
            np.eye(8)[0],
            first_vector,
            second_vector,
            quaternion_unit,
            unit_section,
            _multiply(first_vector, unit_section),
            _multiply(second_vector, unit_section),
            _multiply(quaternion_unit, unit_section),
        )
    )


def unit_zero_divisor_pair(
    first: object, second: object, chart: int, fiber_coordinates: object
) -> tuple[np.ndarray, np.ndarray]:
    """Evaluate one chart at a unit quaternion, returning real unit operands x,y with x*y=0."""
    first_vector, second_vector, quaternion_unit, _ = _base_geometry(first, second)
    coordinates = _unit_vector(fiber_coordinates, 4, "fiber coordinates")
    section = chart_frame(first_vector, second_vector, chart) @ coordinates
    element = np.concatenate((first_vector, second_vector)) / math.sqrt(2)
    partner = np.concatenate((section, -_multiply(quaternion_unit, section))) / math.sqrt(2)
    return element, partner


def right_fiber_action(first: object, second: object, partner: object, quaternion: object) -> np.ndarray:
    """Apply the chart-independent right unit-quaternion action to a real unit partner.

    On H-perp, g*(h*c)=(h*g)*c for g,h in H. Thus multiplying the octonion
    section on the left by g implements right multiplication of its chart
    coordinates. This order is essential to the action law.
    """
    first_vector, second_vector, quaternion_unit, projector = _base_geometry(first, second)
    unit_partner = _unit_vector(partner, 16, "partner")
    coordinates = _unit_vector(quaternion, 4, "quaternion")
    section = math.sqrt(2) * unit_partner[:8]
    expected = np.concatenate((section, -_multiply(quaternion_unit, section))) / math.sqrt(2)
    if (
        float(np.max(np.abs(expected - unit_partner))) > NUMERIC_TOLERANCE
        or float(np.max(np.abs(projector @ section - section))) > NUMERIC_TOLERANCE
    ):
        raise ValueError("partner must belong to the base element's real unit annihilator")
    acting_octonion = (
        coordinates[0] * np.eye(8)[0]
        + coordinates[1] * first_vector
        + coordinates[2] * second_vector
        + coordinates[3] * quaternion_unit
    )
    moved = _multiply(acting_octonion, section)
    return np.concatenate((moved, -_multiply(quaternion_unit, moved))) / math.sqrt(2)


def _exact_product(first: ExactVector, second: ExactVector) -> ExactVector:
    return cd_multiply_exact(len(first), first, second)


def _exact_inner(first: ExactVector, second: ExactVector) -> Fraction:
    return sum((left * right for left, right in zip(first, second, strict=True)), start=Fraction(0))


def _exact_rank(columns: list[ExactVector]) -> int:
    rows = [list(row) for row in zip(*columns, strict=True)]
    pivot_row = 0
    for column_index in range(len(columns)):
        pivot = next((index for index in range(pivot_row, len(rows)) if rows[index][column_index]), None)
        if pivot is None:
            continue
        rows[pivot_row], rows[pivot] = rows[pivot], rows[pivot_row]
        pivot_value = rows[pivot_row][column_index]
        rows[pivot_row] = [value / pivot_value for value in rows[pivot_row]]
        for row_index in range(pivot_row + 1, len(rows)):
            factor = rows[row_index][column_index]
            if factor:
                rows[row_index] = [
                    value - factor * pivot_value
                    for value, pivot_value in zip(rows[row_index], rows[pivot_row], strict=True)
                ]
        pivot_row += 1
        if pivot_row == len(rows):
            break
    return pivot_row


def _exact_fixture(kind: str) -> dict[str, object]:
    identity = [tuple(Fraction(int(row == column)) for row in range(8)) for column in range(8)]
    if kind == "dense_rational_householder":
        direction = tuple(Fraction(index) for index in range(1, 8))
        length_squared = _exact_inner(direction, direction)
        first = (Fraction(0),) + tuple(
            Fraction(int(index == 0)) - 2 * direction[index] * direction[0] / length_squared for index in range(7)
        )
        second = (Fraction(0),) + tuple(
            Fraction(int(index == 1)) - 2 * direction[index] * direction[1] / length_squared for index in range(7)
        )
    elif kind == "pythagorean_cayley_frame":
        first = tuple((3 * left + 4 * right) / 5 for left, right in zip(identity[1], identity[2], strict=True))
        second = identity[3]
    else:
        first, second = identity[1], identity[2]
    quaternion_unit = _exact_product(first, second)
    quaternion_basis = [identity[0], first, second, quaternion_unit]
    for row, column in product(range(4), repeat=2):
        _require(_exact_inner(quaternion_basis[row], quaternion_basis[column]) == int(row == column), "exact H basis")
    projected_columns = [
        tuple(
            coordinate - sum((_exact_inner(column, vector) * vector[index] for vector in quaternion_basis), Fraction(0))
            for index, coordinate in enumerate(column)
        )
        for column in identity
    ]
    section = (
        tuple((3 * left + 4 * right) / 5 for left, right in zip(identity[4], identity[5], strict=True))
        if kind == "pythagorean_cayley_frame"
        else next(column for column in projected_columns if any(column))
    )
    frame = [
        section,
        _exact_product(first, section),
        _exact_product(second, section),
        _exact_product(quaternion_unit, section),
    ]
    section_norm_squared = _exact_inner(section, section)
    cayley_columns = quaternion_basis + frame
    for left_index, right_index in product(range(8), repeat=2):
        scale = section_norm_squared if left_index >= 4 and right_index >= 4 else Fraction(1)
        expected = tuple(
            cd_sign(8, left_index, right_index) * scale * value for value in cayley_columns[left_index ^ right_index]
        )
        _require(
            _exact_product(cayley_columns[left_index], cayley_columns[right_index]) == expected,
            "exact scaled Cayley-frame multiplication table",
        )
    element = first + second
    partners = [column + tuple(-value for value in _exact_product(quaternion_unit, column)) for column in frame]
    for row, column in product(range(4), repeat=2):
        _require(
            _exact_inner(partners[row], partners[column]) == 2 * section_norm_squared * int(row == column),
            "exact annihilator frame Gram matrix",
        )
    for partner in partners:
        _require(_exact_product(element, partner) == (Fraction(0),) * 16, "exact zero product")
    basis_16 = [tuple(Fraction(int(row == column)) for row in range(16)) for column in range(16)]
    rank = _exact_rank([_exact_product(element, column) for column in basis_16])
    _require(rank == 12 and _exact_rank(partners) == 4, "exact kernel dimension")
    return {
        "fixture": kind,
        "first": [str(value) for value in first],
        "second": [str(value) for value in second],
        "section": [str(value) for value in section],
        "section_norm_squared": str(section_norm_squared),
        "element_norm_squared": "2",
        "partner_norm_squared": str(2 * section_norm_squared),
        "left_action_rank": rank,
        "kernel_dimension": 4,
        "cayley_basis_products_checked": 64,
        "cayley_frame_normalization": "divide last four columns by sqrt(section_norm_squared)",
        "arithmetic": "Fraction exact; unit normalization follows by positive scalar rescaling",
    }


def _numerical_fixture(case: tuple[int, list[float], list[float]]) -> dict[str, object]:
    case_index, first_values, second_values = case
    first, second, quaternion_unit, projector = _base_geometry(first_values, second_values)
    patches = [index for index in range(1, 8) if np.linalg.norm(projector[:, index]) >= MIN_PATCH_NORM]
    _require(bool(patches), "atlas coverage failed")
    _require(bool(abs(float(np.trace(projector)) - 4) < NUMERIC_TOLERANCE), "coverage trace identity")
    _require(
        bool(
            max(float(np.linalg.norm(projector[:, index])) for index in patches) >= math.sqrt(4 / 7) - NUMERIC_TOLERANCE
        ),
        "coverage lower bound",
    )
    frames = {index: chart_frame(first, second, index) for index in patches}
    element = np.concatenate((first, second)) / math.sqrt(2)
    action = _left_matrix(element)
    kernel_projector = annihilator_projector(first, second)
    _, singular_values, right_vectors = np.linalg.svd(action)
    _require(singular_values[11] > 0.5 and singular_values[12] < NUMERIC_TOLERANCE, "numerical rank gap")
    independent_projector = right_vectors[12:].T @ right_vectors[12:]
    residuals = {
        "projector_symmetry": float(np.max(np.abs(kernel_projector - kernel_projector.T))),
        "projector_idempotence": float(np.max(np.abs(kernel_projector @ kernel_projector - kernel_projector))),
        "projector_annihilation": float(np.max(np.abs(action @ kernel_projector))),
        "projector_svd_comparison": float(np.max(np.abs(kernel_projector - independent_projector))),
        "frame_orthogonality": 0.0,
        "frame_projector": 0.0,
        "pair_product": 0.0,
        "transition_su2": 0.0,
        "transition_api": 0.0,
        "transition_inverse": 0.0,
        "cocycle": 0.0,
        "right_action": 0.0,
        "right_action_law": 0.0,
        "pair_unit_norm": 0.0,
        "cayley_orthogonality": 0.0,
        "cayley_orientation": 0.0,
        "cayley_multiplication": 0.0,
    }
    coordinates = np.asarray([1.0, 2.0, 3.0, 4.0]) / math.sqrt(30)
    rotation = np.asarray([2.0, -1.0, 4.0, 3.0]) / math.sqrt(30)
    next_rotation = np.asarray([3.0, 4.0, -1.0, 2.0]) / math.sqrt(30)
    for index, frame in frames.items():
        automorphism = cayley_frame(first, second, frame[:, 0])
        residuals["cayley_orthogonality"] = max(
            residuals["cayley_orthogonality"], float(np.max(np.abs(automorphism.T @ automorphism - np.eye(8))))
        )
        residuals["cayley_orientation"] = max(
            residuals["cayley_orientation"], abs(float(np.linalg.det(automorphism)) - 1)
        )
        for left_index, right_index in product(range(8), repeat=2):
            expected_product = cd_sign(8, left_index, right_index) * automorphism[:, left_index ^ right_index]
            actual_product = _multiply(automorphism[:, left_index], automorphism[:, right_index])
            residuals["cayley_multiplication"] = max(
                residuals["cayley_multiplication"], float(np.max(np.abs(actual_product - expected_product)))
            )
        residuals["frame_orthogonality"] = max(
            residuals["frame_orthogonality"], float(np.max(np.abs(frame.T @ frame - np.eye(4))))
        )
        residuals["frame_projector"] = max(
            residuals["frame_projector"], float(np.max(np.abs(frame @ frame.T - projector)))
        )
        left, partner = unit_zero_divisor_pair(first, second, index, coordinates)
        residuals["pair_product"] = max(residuals["pair_product"], float(np.max(np.abs(_multiply(left, partner)))))
        residuals["pair_unit_norm"] = max(
            residuals["pair_unit_norm"], abs(float(left @ left) - 1), abs(float(partner @ partner) - 1)
        )
        moved = right_fiber_action(first, second, partner, rotation)
        expected = unit_zero_divisor_pair(first, second, index, _multiply(coordinates, rotation))[1]
        residuals["right_action"] = max(residuals["right_action"], float(np.max(np.abs(moved - expected))))
        composed = right_fiber_action(first, second, moved, next_rotation)
        combined = right_fiber_action(first, second, partner, _multiply(rotation, next_rotation))
        residuals["right_action_law"] = max(residuals["right_action_law"], float(np.max(np.abs(composed - combined))))
    transitions = {
        (source, target): chart_transition(first, second, source, target)
        for source, target in product(patches, repeat=2)
    }
    for (source, target), transition in transitions.items():
        independent_transition = frames[source].T @ frames[target]
        residuals["transition_api"] = max(
            residuals["transition_api"], float(np.max(np.abs(transition - independent_transition)))
        )
        quaternion = frames[source].T @ frames[target][:, 0]
        residuals["transition_su2"] = max(
            residuals["transition_su2"],
            float(np.max(np.abs(transition - quaternion_left_matrix(quaternion)))),
            abs(float(np.linalg.det(transition)) - 1),
        )
        residuals["transition_inverse"] = max(
            residuals["transition_inverse"], float(np.max(np.abs(transition @ transitions[target, source] - np.eye(4))))
        )
    for source, middle, target in product(patches, repeat=3):
        residuals["cocycle"] = max(
            residuals["cocycle"],
            float(
                np.max(np.abs(transitions[source, middle] @ transitions[middle, target] - transitions[source, target]))
            ),
        )
    _require(bool(max(residuals.values()) < NUMERIC_TOLERANCE), f"bundle fixture {case_index}: {residuals}")
    return {"case": case_index, "available_charts": patches, "residuals": residuals}


def _verify_chart_admission() -> list[dict[str, object]]:
    results = []
    identity = np.eye(8)
    fixtures = (
        ("accepted_base_norm_error", 0.0002, 1 + NUMERIC_TOLERANCE / 4),
        ("projection_roundoff", 0.000125, 1.0),
    )
    for name, separation, scale in fixtures:
        first = (math.sqrt(1 - separation**2) * identity[1] + separation * identity[4]) * scale
        second = identity[2]
        first, second, quaternion_unit, projector = _base_geometry(first, second)
        projection_norm = float(np.linalg.norm(projector[:, 1]))
        _require(projection_norm >= MIN_PATCH_NORM, "chart regression must pass the projection-length guard")
        section = projector[:, 1] / projection_norm
        candidate = np.column_stack(
            (section, _multiply(first, section), _multiply(second, section), _multiply(quaternion_unit, section))
        )
        rejected_residuals = _chart_residuals(first, second, quaternion_unit, projector, candidate)
        _require(bool(rejected_residuals["frame_complement"] > NUMERIC_TOLERANCE), "unstable chart fixture changed")
        try:
            chart_frame(first, second, 1)
        except ValueError as error:
            _require("residuals exceed" in str(error), "unstable chart must fail residual admission")
        else:
            raise RuntimeError("unstable normalized chart accepted")
        try:
            unit_zero_divisor_pair(first, second, 1, [1, 0, 0, 0])
        except ValueError as error:
            _require("residuals exceed" in str(error), "unstable pair must fail chart residual admission")
        else:
            raise RuntimeError("unstable chart pair accepted")
        accepted_chart = 1 + int(np.argmax(np.linalg.norm(projector[:, 1:], axis=0)))
        frame = chart_frame(first, second, accepted_chart)
        automorphism = cayley_frame(first, second, frame[:, 0])
        accepted_residuals = _chart_residuals(first, second, quaternion_unit, projector, frame)
        accepted_residuals["cayley_orthogonality"] = float(
            np.linalg.norm(automorphism.T @ automorphism - np.eye(8), ord=2)
        )
        accepted_residuals["pair_product"] = 0.0
        accepted_residuals["pair_unit_norm"] = 0.0
        accepted_residuals["right_action_identity"] = 0.0
        fiber_coordinates = [*np.eye(4), np.asarray([1, 2, 3, 4]) / math.sqrt(30)]
        for coordinates in fiber_coordinates:
            element, partner = unit_zero_divisor_pair(first, second, accepted_chart, coordinates)
            moved = right_fiber_action(first, second, partner, [1, 0, 0, 0])
            accepted_residuals["pair_product"] = max(
                accepted_residuals["pair_product"], float(np.linalg.norm(_multiply(element, partner)))
            )
            accepted_residuals["pair_unit_norm"] = max(
                accepted_residuals["pair_unit_norm"],
                abs(float(element @ element) - 1),
                abs(float(partner @ partner) - 1),
            )
            accepted_residuals["right_action_identity"] = max(
                accepted_residuals["right_action_identity"], float(np.linalg.norm(moved - partner))
            )
        _require(bool(max(accepted_residuals.values()) <= NUMERIC_TOLERANCE), "largest-projection chart residuals")
        results.append(
            {
                "fixture": name,
                "base_norm_squared_error": abs(float(first @ first) - 1),
                "rejected_chart": 1,
                "rejected_chart_projection_norm": projection_norm,
                "rejected_chart_residuals": rejected_residuals,
                "accepted_chart": accepted_chart,
                "accepted_chart_residuals": accepted_residuals,
                "consumer_checks": "Cayley frame and identity right action; four basis and one dense fiber coordinates",
            }
        )
    return results


def _verify_rejections_and_mutations() -> dict[str, object]:
    first, second = np.eye(8)[1:3]
    invalid_bases: list[tuple[object, object]] = [
        (first * 2, second),
        (first, first),
        (np.eye(8)[0], second),
        (np.full(8, np.nan), second),
        (first, np.full(8, np.inf)),
        (first.astype(complex) + 1j * second, second),
        (first[:7], second),
        (first * 1e300, second),
        (np.full(8, np.finfo(np.longdouble).max, dtype=np.longdouble), second),
    ]
    rejected = 0
    for left, right in invalid_bases:
        try:
            complement_projector(left, right)
        except ValueError:
            rejected += 1
        else:
            raise RuntimeError("invalid bundle base accepted")
    for index in (0, 8, -1, True, 1.5, 1):
        try:
            chart_frame(first, second, index)  # type: ignore[arg-type]
        except ValueError:
            rejected += 1
        else:
            raise RuntimeError("invalid or degenerate chart accepted")
    for coordinates in ([0, 0, 0, 0], [np.nan, 0, 0, 0], [1, 0, 0], [1j, 0, 0, 0]):
        try:
            unit_zero_divisor_pair(first, second, 4, coordinates)
        except ValueError:
            rejected += 1
        else:
            raise RuntimeError("invalid fiber coordinates accepted")
    try:
        right_fiber_action(first, second, np.eye(16)[0], [1, 0, 0, 0])
    except ValueError:
        rejected += 1
    else:
        raise RuntimeError("partner outside the annihilator accepted")
    element, partner = unit_zero_divisor_pair(first, second, 4, [1, 0, 0, 0])
    wrong_sign = partner.copy()
    wrong_sign[8:] *= -1
    sign_error = float(np.max(np.abs(_multiply(element, wrong_sign))))
    _require(sign_error > 0.5, "annihilator sign mutation escaped")
    first_transition = chart_transition(first, second, 4, 5)
    second_transition = chart_transition(first, second, 5, 6)
    direct_transition = chart_transition(first, second, 4, 6)
    order_error = float(np.max(np.abs(second_transition @ first_transition - direct_transition)))
    _require(order_error > 1, "reversed overlap order mutation escaped")
    _require(
        np.max(np.abs(first_transition @ second_transition - direct_transition)) < NUMERIC_TOLERANCE,
        "correct overlap order failed",
    )
    return {
        "rejected_inputs": rejected,
        "chart_admission_regressions": _verify_chart_admission(),
        "wrong_partner_sign_error": sign_error,
        "reversed_overlap_order_error": order_error,
    }


def audit_sedenion_bundle() -> dict[str, object]:
    """Validate the constructive formulas on exact fixtures and a bounded floating-point corpus."""
    generator = np.random.default_rng(DENSE_SEED)
    standard_bases = sorted({(first, second, sign) for first, second, sign, _, _, _ in sedenion_zero_divisor_corpus()})
    _require(len(standard_bases) == 84, "standard signed sedenion base count changed")
    cases = []
    for case_index, (first_index, second_index, sign) in enumerate(standard_bases):
        _require(1 <= first_index <= 7 and 9 <= second_index <= 15, "standard base half-coordinate convention")
        cases.append((case_index, np.eye(8)[first_index].tolist(), (sign * np.eye(8)[second_index - 8]).tolist()))
    for case_index in range(len(standard_bases), len(standard_bases) + DENSE_CASES):
        orthonormal, _ = np.linalg.qr(generator.normal(size=(7, 2)))
        first = np.concatenate(([0.0], orthonormal[:, 0]))
        second = np.concatenate(([0.0], orthonormal[:, 1]))
        cases.append((case_index, first.tolist(), second.tolist()))
    results = parallel.ordered_map(_numerical_fixture, cases, min_items=2)
    return {
        "schema": "sedenion-quaternion-bundle-atlas-v1",
        "qpu_executed": False,
        "versions": {"python": platform.python_version(), "numpy": np.__version__},
        "execution": "local exact rational arithmetic and NumPy; credential-free",
        "scope": "Finite implementation checks; the general bundle construction uses the algebraic derivation.",
        "base": "x=(a,b)/sqrt(2), (a,b) in V_2(R^7)",
        "fiber": "y=(c,-(a*b)*c)/sqrt(2), c in H-perp, ||c||=1",
        "atlas": "seven projected imaginary-coordinate charts; numerical conditioning guard recorded",
        "transition": "F_source^T F_target=L(h_source_target), acting on target coordinates",
        "action": "right unit-quaternion multiplication of fiber coordinates",
        "numeric_tolerance": NUMERIC_TOLERANCE,
        "minimum_numerical_patch_norm": MIN_PATCH_NORM,
        "numerical_chart_admission": (
            "projection length guard followed by section complement, frame complement, frame Gram, "
            "frame projector, lifted Gram, and lifted annihilation residual checks; "
            "matrix residuals use the spectral norm"
        ),
        "dense_seed": DENSE_SEED,
        "standard_signed_base_cases": len(standard_bases),
        "dense_cases": DENSE_CASES,
        "exact_fixtures": [
            _exact_fixture("coordinate_basis"),
            _exact_fixture("pythagorean_cayley_frame"),
            _exact_fixture("dense_rational_householder"),
        ],
        "numeric_fixtures": results,
        "falsifiers": _verify_rejections_and_mutations(),
    }


def main() -> int:
    print(json.dumps(audit_sedenion_bundle(), indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
