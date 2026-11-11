"""Exact local frames and Grassmann coordinates on deterministic nullity-four fixtures.

The nullity-four kernel has complex rank two under the transport
``psi(ker L_y) = ker A(z, conjugate(z))``.  A nonzero principal order-fourteen
Pfaffian gives the Schur frame ``[-B^-1 C; I_2]``.  Its two-by-two minors are
the Plucker coordinates of the kernel Gauss map into ``Gr(2, C^16)``.

This producer evaluates the 66 exact grid fixtures retained by
``probes/nullity4_orbit_ranks.py``.  It is a chart and coordinate certificate
on those fixtures, not a classification of the nine- and eleven-dimensional
moduli spaces and not a global trivialization.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from collections import Counter
from collections.abc import Sequence
from fractions import Fraction
from functools import cache, lru_cache
from pathlib import Path
from typing import Any

import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BUNDLES = HERE.parent / "a5-kernel-bundles"
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(BUNDLES))

import kernel_frames as frames  # noqa: E402

import parallel  # noqa: E402
from cd_core import left_mult_matrix_exact  # noqa: E402

RESULT = HERE / "nullity4-kernel-gauss-result.json"
PROBE = HERE / "probes" / "nullity4_orbit_ranks.py"
MATRIX_RANK = 14
KERNEL_RANK = 2
PLUCKER_ORDER = tuple(itertools.combinations(range(frames.BORDERED_DIMENSION), KERNEL_RANK))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


@lru_cache(maxsize=1)
def _closure_ideals() -> dict[str, Any]:
    return frames.regularity.closure_ideals()


def _fixtures() -> tuple[tuple[Fraction, ...], ...]:
    points = [frames.regularity.split_point({1: 1}, 3, {1: 5, 3: 3})]
    for a, mu, b, c, d in itertools.product(range(0, 3), range(0, 4), range(-2, 4), range(0, 4), range(0, 3)):
        points.append(frames.regularity.split_point({1: 1, 2: a}, mu, {1: b, 3: c, 5: d}))
    rows: list[tuple[Fraction, ...]] = []
    seen: set[tuple[Fraction, ...]] = set()
    for point in points:
        exact_point = tuple(Fraction(value) for value in point)
        if exact_point in seen:
            continue
        seen.add(exact_point)
        if frames.regularity.eq.point_nullity([value.numerator for value in exact_point]) == 4:
            rows.append(exact_point)
    return tuple(rows)


def _stratum(point: Sequence[Fraction]) -> str:
    ideals = _closure_ideals()
    if any(value.denominator != 1 for value in point):
        raise ValueError("the retained nullity-four grid must have integral split coordinates")
    integral_point = tuple(value.numerator for value in point)
    in_q = frames.regularity.member(ideals["VQ"], integral_point)
    in_g = frames.regularity.member(ideals["VG"], integral_point)
    if in_q and in_g:
        return "V(Q) intersect V(G)"
    if in_q:
        return "V(Q) minus V(G)"
    if in_g:
        return "V(G) minus V(Q)"
    raise RuntimeError("nullity-four fixture lies outside both recorded components")


def _plucker_coordinates(frame: sp.Matrix) -> tuple[sp.Expr, ...]:
    coordinates = tuple(sp.expand(frame.extract(pair, (0, 1)).det()) for pair in PLUCKER_ORDER)
    leading = next((value for value in coordinates if value != 0), None)
    _require(leading is not None, "rank-two frame has no nonzero Plucker coordinate")
    return tuple(sp.simplify(value / leading) for value in coordinates)


def _numeric_pfaffian(matrix: sp.Matrix) -> sp.Expr:
    """Pfaffian of one exact numeric skew matrix, memoized by principal submatrix."""
    if matrix.rows != matrix.cols or matrix.rows % 2:
        raise ValueError("Pfaffian input must be an even square matrix")

    @cache
    def expand(indices: tuple[int, ...]) -> sp.Expr:
        if not indices:
            return sp.Integer(1)
        first = indices[0]
        total = sp.Integer(0)
        for position in range(1, len(indices)):
            second = indices[position]
            remaining = indices[1:position] + indices[position + 1 :]
            term = matrix[first, second] * expand(remaining)
            total = total + term if position % 2 else total - term
        return sp.expand(total)

    return expand(tuple(range(matrix.rows)))


def _principal_frame(matrix: sp.Matrix, pivot: Sequence[int]) -> tuple[sp.Matrix, sp.Expr, sp.Expr]:
    free = tuple(index for index in range(frames.BORDERED_DIMENSION) if index not in pivot)
    block = matrix.extract(pivot, pivot)
    upper_right = matrix.extract(pivot, free)
    determinant = sp.expand(block.det())
    if determinant == 0:
        raise ValueError("principal chart denominator vanishes")
    pfaffian = _numeric_pfaffian(block)
    frame = sp.zeros(frames.BORDERED_DIMENSION, len(free))
    pivot_rows = -block.inv() * upper_right
    for row_position, row in enumerate(pivot):
        for column in range(len(free)):
            frame[row, column] = pivot_rows[row_position, column]
    for row_position, row in enumerate(free):
        frame[row, row_position] = 1
    return frame, determinant, pfaffian


def _plucker_relations_hold(coordinates: Sequence[sp.Expr]) -> bool:
    values = {pair: value for pair, value in zip(PLUCKER_ORDER, coordinates, strict=True)}
    for i, j, k, ell in itertools.combinations(range(frames.BORDERED_DIMENSION), 4):
        relation = values[i, j] * values[k, ell] - values[i, k] * values[j, ell] + values[i, ell] * values[j, k]
        if sp.expand(relation) != 0:
            return False
    return True


def _nullspace_plucker(bordered: sp.Matrix) -> tuple[sp.Expr, ...]:
    """Normalized Plucker coordinates of ker(bordered) from sympy's nullspace, independent of the Schur frame."""
    basis = bordered.nullspace()
    _require(len(basis) == KERNEL_RANK, "bordered kernel is not two-dimensional")
    return _plucker_coordinates(sp.Matrix.hstack(*basis))


def _fixture_row(point: tuple[Fraction, ...]) -> dict[str, Any]:
    z = frames._original_z_from_split(point)
    bordered = frames._bordered_matrix(z)
    _require(bordered.T == -bordered, "bordered matrix is not skew")
    pivot = frames._find_principal_pivot(bordered, MATRIX_RANK)
    frame, determinant, pfaffian = _principal_frame(bordered, pivot)
    free = tuple(index for index in range(frames.BORDERED_DIMENSION) if index not in pivot)
    coordinates = _plucker_coordinates(frame)
    y = frames._real_coordinates_from_z(z)
    left_nullity = frames.regularity.eq.nullity(y)
    left_matrix = sp.Matrix(left_mult_matrix_exact(32, y))
    real_frame = frames._real_kernel_frame(frame)
    checks = {
        "bordered_rank_is_14": pfaffian != 0 and left_nullity == 4,
        "principal_determinant_is_pfaffian_square": sp.expand(determinant - pfaffian * pfaffian) == 0,
        "principal_pfaffian_nonzero": pfaffian != 0,
        "schur_frame_is_in_bordered_kernel": bordered * frame == sp.zeros(16, KERNEL_RANK),
        "free_rows_are_identity": frame.extract(free, range(KERNEL_RANK)) == sp.eye(KERNEL_RANK),
        "left_nullity_is_4": left_nullity == 4,
        "realified_frame_spans_left_kernel": left_matrix * real_frame == sp.zeros(32, 4) and real_frame.rank() == 4,
        "plucker_relations_hold": _plucker_relations_hold(coordinates),
        "plucker_equals_independent_nullspace": coordinates == _nullspace_plucker(bordered),
    }
    return {
        "split_point": [str(value) for value in point],
        "stratum": _stratum(point),
        "pivot_indices": list(pivot),
        "free_indices": list(free),
        "pivot_pfaffian": sp.sstr(pfaffian),
        "normalized_plucker_coordinates": [sp.sstr(value) for value in coordinates],
        "nonzero_plucker_coordinates": sum(value != 0 for value in coordinates),
        "checks": checks,
        "pass": all(checks.values()),
    }


def _mutations_rejected(point: tuple[Fraction, ...], row: dict[str, Any]) -> dict[str, int]:
    """Counts of wrong coordinate vectors that the comparison with the independent nullspace rejects.

    The vectors are the 120 single-coordinate shifts by one and the decomposable vector (1, 0, ..., 0), which
    satisfies every Plucker quadric and names a different plane.
    """
    reference = _nullspace_plucker(frames._bordered_matrix(frames._original_z_from_split(point)))
    coordinates = [sp.sympify(value) for value in row["normalized_plucker_coordinates"]]
    shifted = 0
    for index in range(len(coordinates)):
        mutated = coordinates.copy()
        mutated[index] += 1
        shifted += tuple(mutated) != reference
    constant = (sp.Integer(1),) + (sp.Integer(0),) * (len(coordinates) - 1)
    return {
        "single_coordinate_shifts": len(coordinates),
        "single_coordinate_shifts_rejected": shifted,
        "constant_decomposable_vector_satisfies_quadrics": int(_plucker_relations_hold(constant)),
        "constant_decomposable_vector_rejected": int(constant != reference),
    }


def _mutation_task(item: tuple[tuple[Fraction, ...], dict[str, Any]]) -> dict[str, int]:
    return _mutations_rejected(*item)


def build_result() -> dict[str, Any]:
    fixtures = _fixtures()
    rows = parallel.ordered_map(_fixture_row, fixtures, min_items=1)
    stratum_counts = Counter(row["stratum"] for row in rows)
    # One fixture per stratum, the first in grid order, carries the mutation control.
    first = {row["stratum"]: index for index, row in reversed(list(enumerate(rows)))}
    chosen = [first[name] for name in sorted(first)]
    controls = parallel.ordered_map(_mutation_task, [(fixtures[i], rows[i]) for i in chosen], min_items=1)
    mutation_control = {
        "mutation": (
            "each of the 120 single-coordinate shifts by one, and the decomposable vector (1, 0, ..., 0), "
            "compared with the Plucker coordinates of an independently computed nullspace"
        ),
        "fixtures": [
            {"fixture_index": i, "stratum": rows[i]["stratum"], **c} for i, c in zip(chosen, controls, strict=True)
        ],
        "detected": bool(controls)
        and all(
            c["single_coordinate_shifts_rejected"] == c["single_coordinate_shifts"]
            and c["constant_decomposable_vector_rejected"] == 1
            for c in controls
        ),
    }
    result: dict[str, Any] = {
        "schema": "a5-nullity-four-kernel-gauss-fixtures-v1",
        "scope": (
            "exact principal-Pfaffian frames and kernel-Gauss coordinates on the retained 66-point integer grid; "
            "not a global atlas, moduli classification, transition-function classification, or bundle class"
        ),
        "complex_kernel_rank": KERNEL_RANK,
        "bordered_matrix_rank": MATRIX_RANK,
        "chart_count": len(PLUCKER_ORDER),
        "chart_indexing": "all order-fourteen principal pivot sets, equivalently their two free indices",
        "frame_formula": "F_I=[-B_I^(-1) C_I; I_2] in pivot/free order",
        "transition_formula": "on U_I intersect U_J, T_IJ is F_J restricted to the I-free rows and F_I T_IJ=F_J",
        "plucker_coordinate_order": [list(pair) for pair in PLUCKER_ORDER],
        "fixture_count": len(rows),
        "stratum_counts": dict(sorted(stratum_counts.items())),
        "mutation_control": mutation_control,
        "fixtures": rows,
        "input_sha256": {
            "kernel_frames.py": hashlib.sha256((BUNDLES / "kernel_frames.py").read_bytes()).hexdigest(),
            "nullity4_orbit_ranks.py": hashlib.sha256(PROBE.read_bytes()).hexdigest(),
            **{
                path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                for path in (
                    ROOT / "gororoba_quantum" / "cd_core.py",
                    ROOT / "docs/evidence/a5-strata-regularity/strata_regularity.py",
                    ROOT / "docs/evidence/a5-rank-strata-equations/rederive_strata_equations.py",
                )
            },
        },
    }
    result["pass"] = len(rows) == 66 and all(row["pass"] for row in rows) and result["mutation_control"]["detected"]
    result["script_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    return result


def self_test() -> None:
    result = build_result()
    if not result["pass"]:
        raise RuntimeError("baseline nullity-four kernel-Gauss fixture check failed")
    if not result["mutation_control"]["detected"]:
        raise RuntimeError("Plucker-coordinate mutation escaped detection")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    arguments = parser.parse_args()
    selected = sum((arguments.out is not None, arguments.check, arguments.self_test))
    if selected > 1:
        parser.error("choose only one of --out, --check, or --self-test")
    if arguments.self_test:
        self_test()
        print("nullity4_kernel_gauss: self-test pass")
        return 0
    result = build_result()
    if not result["pass"]:
        raise RuntimeError("nullity-four kernel-Gauss fixture check failed")
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if arguments.check:
        if RESULT.read_bytes() != payload.encode():
            raise SystemExit("nullity4_kernel_gauss: result differs from the retained record")
        print("nullity4_kernel_gauss: retained result reproduces")
    elif arguments.out is not None:
        arguments.out.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
