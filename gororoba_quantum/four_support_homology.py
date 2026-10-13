"""Integral cellular certificate for the fixed four-support unit-pair space.

The geometric CW identification and orientations appear in the accompanying
proof note. Exact integer chain generation and independently replayed unit
cancellations certify homology. A preserved top-factor grading transports the
same finite matrices to every ordinary zero-padding stage.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from collections.abc import Callable, Sequence
from copy import deepcopy
from dataclasses import dataclass
from itertools import product
from typing import Any

import sympy as sp

import parallel
from four_support_doubling import DoublingModel
from four_support_geometry import BLOCK_NAMES, Stratum, closure_contains, enumerate_strata
from integral_homology import integral_homology

SparseMatrix = dict[tuple[int, int], int]
ChainMaps = dict[int, SparseMatrix]
ChainRanks = dict[int, int]
MAX_CONCRETE_STAGE = 4096


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


@dataclass(frozen=True)
class Cell:
    base: int
    states: tuple[int, ...]

    @property
    def top_factors(self) -> tuple[int, ...]:
        return tuple(index for index, value in enumerate(self.states) if value == 4)


def base_chains() -> tuple[tuple[Stratum, ...], tuple[dict[int, int], ...]]:
    """Orient coordinate simplices and determinant-zero squares explicitly."""
    base = tuple(stratum for stratum in enumerate_strata() if stratum.nullity)
    indices = {stratum.signs: index for index, stratum in enumerate(base)}
    _require(len(indices) == len(base), "positive-nullity sign labels must be unique")
    boundaries = []
    for source in base:
        active = [index for index, sign in enumerate(source.signs) if sign]
        terms: dict[int, int] = {}
        if source.dimension in (1, 2) and len(active) <= 3:
            for offset, removed in enumerate(active):
                signs = tuple(0 if index == removed else sign for index, sign in enumerate(source.signs))
                terms[indices[signs]] = (-1) ** offset
        elif source.dimension == 2 and len(active) == 4:
            # The du wedge dv square boundary visits q, r, p, s, q.
            cycle = (1, 2, 0, 3, 1)
            for start, end in zip(cycle[:-1], cycle[1:], strict=True):
                signs = tuple(sign if index in (start, end) else 0 for index, sign in enumerate(source.signs))
                terms[indices[signs]] = 1 if start < end else -1
        else:
            _require(source.dimension == 0, "unidentified positive-nullity base characteristic map")
        for target in terms:
            _require(base[target].dimension == source.dimension - 1, "base incidence has the wrong degree")
            _require(closure_contains(source, base[target]), "base incidence escapes its geometric closure")
            _require(set(source.kernel_slots) <= set(base[target].kernel_slots), "kernel inclusion fails")
        boundaries.append(terms)
    for source_boundary in boundaries:
        squared: dict[int, int] = defaultdict(int)
        for middle, coefficient in source_boundary.items():
            for target, previous in boundaries[middle].items():
                squared[target] += coefficient * previous
        _require(not any(squared.values()), "base boundary squared is nonzero")
    return base, tuple(boundaries)


def fiber_states(blocks: Sequence[int]) -> tuple[tuple[int, ...], ...]:
    """Use shifted degrees absent=0, point=1, top=4 in fixed block order."""
    result = []
    for choices in product((0, 1, 4), repeat=len(blocks)):
        if not any(choices):
            continue
        states = [0] * len(BLOCK_NAMES)
        for block, choice in zip(blocks, choices, strict=True):
            states[block] = choice
        result.append(tuple(states))
    return tuple(result)


def fiber_boundary(states: tuple[int, ...]) -> dict[tuple[int, ...], int]:
    """Apply the augmented join differential and discard the empty face."""
    result = {}
    preceding = 0
    for index, value in enumerate(states):
        if value == 1 and sum(states) > 1:
            target = tuple(0 if slot == index else state for slot, state in enumerate(states))
            result[target] = (-1) ** preceding
        preceding += value
    return result


def incidence_chains(
    *,
    omit_product_sign: bool = False,
) -> tuple[tuple[Stratum, ...], dict[int, tuple[Cell, ...]], ChainMaps]:
    """Generate oriented product chains from the geometric stratum labels."""
    base, base_boundary = base_chains()
    generated: dict[int, list[Cell]] = defaultdict(list)
    for index, stratum in enumerate(base):
        blocks = sorted({slot // 4 for slot in stratum.kernel_slots})
        for states in fiber_states(blocks):
            generated[stratum.dimension + sum(states) - 1].append(Cell(index, states))
    cells = {degree: tuple(values) for degree, values in sorted(generated.items())}
    indices = {degree: {cell: index for index, cell in enumerate(values)} for degree, values in cells.items()}
    matrices: ChainMaps = {}
    for degree, values in cells.items():
        matrix: SparseMatrix = {}
        for column, source in enumerate(values):
            for target, coefficient in base_boundary[source.base].items():
                row = indices[degree - 1][Cell(target, source.states)]
                matrix[row, column] = coefficient
            sign = 1 if omit_product_sign else (-1) ** base[source.base].dimension
            for states, coefficient in fiber_boundary(source.states).items():
                row = indices[degree - 1][Cell(source.base, states)]
                matrix[row, column] = coefficient * sign
        matrices[degree] = matrix
    return base, cells, matrices


def _multiply(first: SparseMatrix, second: SparseMatrix) -> SparseMatrix:
    rows: dict[int, list[tuple[int, int]]] = defaultdict(list)
    for (middle, column), value in second.items():
        rows[middle].append((column, value))
    result: SparseMatrix = defaultdict(int)
    for (row, middle), left in first.items():
        for column, right in rows[middle]:
            result[row, column] += left * right
    return {key: value for key, value in result.items() if value}


def validate_chains(ranks: ChainRanks, matrices: ChainMaps) -> None:
    for degree, rank in ranks.items():
        _require(type(degree) is int and degree >= 0 and type(rank) is int and rank >= 0, "invalid chain rank")
    for degree, matrix in matrices.items():
        for (row, column), value in matrix.items():
            _require(type(value) is int and value != 0, "sparse chain entries require nonzero integers")
            _require(0 <= row < ranks.get(degree - 1, 0), "chain row exceeds its declared rank")
            _require(0 <= column < ranks.get(degree, 0), "chain column exceeds its declared rank")
        _require(not _multiply(matrices.get(degree - 1, {}), matrix), "product boundary squared is nonzero")


def verify_top_grading(cells: dict[int, tuple[Cell, ...]], matrices: ChainMaps) -> None:
    for degree, matrix in matrices.items():
        for row, column in matrix:
            _require(
                cells[degree - 1][row].top_factors == cells[degree][column].top_factors,
                "boundary changes the complete top-factor subset",
            )


def verify_cancellation_grading(cells: dict[int, tuple[Cell, ...]], operations: Sequence[dict[str, Any]]) -> None:
    """Bind every pivot and shear vector to one fixed top-factor summand."""
    for operation in operations:
        degree, row, column = (operation[key] for key in ("degree", "row", "column"))
        tops = cells[degree][column].top_factors
        _require(cells[degree - 1][row].top_factors == tops, "pivot crosses top-factor summands")
        for source, _ in operation["row_vector"]:
            _require(cells[degree][source].top_factors == tops, "column shear crosses top-factor summands")
        for target, _ in operation["column_vector"]:
            _require(cells[degree - 1][target].top_factors == tops, "row shear crosses top-factor summands")


def orientation_facets() -> int:
    """Derive the shifted sign from the oriented characteristic domains."""
    checked = 0
    for states in fiber_states(tuple(range(len(BLOCK_NAMES)))):
        ordinary = tuple(value - 1 for value in states if value)
        alpha = sum((len(ordinary) - 1 - index) * degree for index, degree in enumerate(ordinary))
        for position, degree in enumerate(ordinary):
            if degree:
                continue
            target = ordinary[:position] + ordinary[position + 1 :]
            beta = sum((len(target) - 1 - index) * value for index, value in enumerate(target))
            characteristic_sign = (-1) ** (position + alpha - beta)
            shifted_sign = (-1) ** sum(value + 1 for value in ordinary[:position])
            _require(characteristic_sign == shifted_sign, "characteristic orientation disagrees with join sign")
            checked += 1
    return checked


def _vectors(matrix: SparseMatrix, row: int, column: int) -> tuple[dict[int, int], dict[int, int]]:
    row_vector = {col: value for (target, col), value in matrix.items() if target == row and col != column}
    column_vector = {target: value for (target, col), value in matrix.items() if col == column and target != row}
    return row_vector, column_vector


def _update(matrix: SparseMatrix, key: tuple[int, int], delta: int) -> None:
    value = matrix.get(key, 0) + delta
    if value:
        matrix[key] = value
    else:
        matrix.pop(key, None)


def generate_cancellations(ranks: ChainRanks, boundaries: ChainMaps) -> list[dict[str, Any]]:
    """Choose deterministic unit pivots and record every pre-pivot vector."""
    validate_chains(ranks, boundaries)
    matrices = deepcopy(boundaries)
    operations = []
    for degree in sorted(matrices):
        matrix = matrices[degree]
        while True:
            row_counts = Counter(row for row, _ in matrix)
            column_counts = Counter(column for _, column in matrix)
            units = [key for key, value in matrix.items() if abs(value) == 1]
            if not units:
                break
            row, column = min(units, key=lambda key: (row_counts[key[0]] * column_counts[key[1]], key))
            unit = matrix[row, column]
            row_vector, column_vector = _vectors(matrix, row, column)
            operations.append(
                {
                    "degree": degree,
                    "row": row,
                    "column": column,
                    "unit": unit,
                    "row_vector": [list(item) for item in sorted(row_vector.items())],
                    "column_vector": [list(item) for item in sorted(column_vector.items())],
                }
            )
            for target, left in column_vector.items():
                for source, right in row_vector.items():
                    _update(matrix, (target, source), -left * right * unit)
            matrices[degree] = matrix = {
                key: value for key, value in matrix.items() if key[0] != row and key[1] != column
            }
            matrices[degree - 1] = {key: value for key, value in matrices.get(degree - 1, {}).items() if key[1] != row}
            matrices[degree + 1] = {
                key: value for key, value in matrices.get(degree + 1, {}).items() if key[0] != column
            }
    return operations


def replay_cancellations(
    ranks: ChainRanks, boundaries: ChainMaps, operations: Sequence[dict[str, Any]], *, require_zero: bool = True
) -> tuple[dict[int, set[int]], ChainMaps]:
    """Replay elementary unimodular shears on all three adjacent maps.

    The replay does not use the generator's Schur-complement update. Every
    row shear multiplies the preceding map by its inverse, and every column
    shear multiplies the following map by its inverse. The two deleted
    adjacent vectors must vanish exactly before the acyclic pair is removed.
    """
    validate_chains(ranks, boundaries)
    matrices = deepcopy(boundaries)
    remaining = {degree: set(range(rank)) for degree, rank in ranks.items()}
    for operation in operations:
        degree, row, column, unit = (operation[key] for key in ("degree", "row", "column", "unit"))
        _require(all(type(value) is int for value in (degree, row, column, unit)), "pivot data require integers")
        _require(unit in (-1, 1), "cancellation pivot must be an integral unit")
        _require(row in remaining.get(degree - 1, ()) and column in remaining.get(degree, ()), "pivot is unavailable")
        matrix = matrices[degree]
        _require(matrix.get((row, column)) == unit, "recorded pivot differs from chain entry")
        row_vector, column_vector = _vectors(matrix, row, column)
        _require(operation["row_vector"] == [list(item) for item in sorted(row_vector.items())], "pivot row mismatch")
        _require(
            operation["column_vector"] == [list(item) for item in sorted(column_vector.items())],
            "pivot column mismatch",
        )
        previous, following = matrices.setdefault(degree - 1, {}), matrices.setdefault(degree + 1, {})
        # U clears the pivot column; previous U^-1 preserves the chain map.
        for target, value in column_vector.items():
            multiplier = value * unit
            for source, coefficient in {column: unit, **row_vector}.items():
                _update(matrix, (target, source), -multiplier * coefficient)
            for (target_row, target_column), coefficient in tuple(previous.items()):
                if target_column == target:
                    _update(previous, (target_row, row), multiplier * coefficient)
        _require(all(key[0] == row for key in matrix if key[1] == column), "row shear fails to isolate column")
        # V clears the pivot row; V^-1 following preserves the next map.
        for source, value in row_vector.items():
            multiplier = value * unit
            _update(matrix, (row, source), -multiplier * unit)
            for (target_row, target_column), coefficient in tuple(following.items()):
                if target_row == source:
                    _update(following, (column, target_column), multiplier * coefficient)
        _require(all(key[1] == column for key in matrix if key[0] == row), "column shear fails to isolate row")
        _require(all(key[1] != row for key in previous), "preceding transformed vector is nonzero")
        _require(all(key[0] != column for key in following), "following transformed vector is nonzero")
        del matrix[row, column]
        remaining[degree - 1].remove(row)
        remaining[degree].remove(column)
        validate_chains(ranks, matrices)
    if require_zero:
        _require(not any(matrices.values()), "residual integral boundary requires further torsion analysis")
    return remaining, matrices


def characteristic_identities() -> dict[str, object]:
    """Check map identities algebraically; positivity/injectivity use the proof."""
    first, second = sp.symbols("u v", real=True)
    magnitudes = (first * second, (1 - first) * (1 - second), first * (1 - second), (1 - first) * second)
    _require(sp.expand(sum(magnitudes) - 1) == 0, "square barycentric sum")
    _require(sp.expand(magnitudes[0] * magnitudes[1] - magnitudes[2] * magnitudes[3]) == 0, "square determinant")
    _require(sp.expand(magnitudes[0] + magnitudes[2] - first) == 0, "square row inverse")
    _require(sp.expand(magnitudes[0] + magnitudes[3] - second) == 0, "square column inverse")
    corners = ((0, 0, 1), (1, 0, 2), (1, 1, 0), (0, 1, 3))
    for u_value, v_value, coordinate in corners:
        _require(
            tuple(value.subs({first: u_value, second: v_value}) for value in magnitudes)
            == tuple(int(index == coordinate) for index in range(4)),
            "square oriented corner mismatch",
        )
    radius = sp.Symbol("t", real=True)
    denominator = radius + (1 - radius) ** 2
    _require(
        sp.expand(denominator - ((radius - sp.Rational(1, 2)) ** 2 + sp.Rational(3, 4))) == 0, "positive denominator"
    )
    _require(
        sp.expand(4 * (1 - radius) ** 2 * radius + (radius - (1 - radius) ** 2) ** 2 - denominator**2) == 0,
        "sphere characteristic norm identity",
    )
    _require((radius - (1 - radius) ** 2).subs(radius, 1) == denominator.subs(radius, 1), "sphere boundary pole")
    return {"square_sum_determinant_inverse_and_orientation": True, "sphere_norm_positive_denominator_boundary": True}


def _sphere_fixture(block_count: int) -> dict[str, object]:
    states = fiber_states(tuple(range(block_count)))
    by_degree = {
        degree: tuple(state for state in states if sum(state) - 1 == degree)
        for degree in sorted({sum(s) - 1 for s in states})
    }
    indices = {degree: {state: index for index, state in enumerate(values)} for degree, values in by_degree.items()}
    matrices = {
        degree: {
            (indices[degree - 1][target], column): coefficient
            for column, source in enumerate(values)
            for target, coefficient in fiber_boundary(source).items()
        }
        for degree, values in by_degree.items()
    }
    ranks = {degree: len(values) for degree, values in by_degree.items()}
    remaining, _ = replay_cancellations(ranks, matrices, generate_cancellations(ranks, matrices))
    groups = {degree: len(values) for degree, values in remaining.items() if values}
    _require(groups == {0: 1, 4 * block_count - 1: 1}, "join fiber fails its sphere homology fixture")
    if block_count <= 2:
        smith = integral_homology(
            ranks,
            {
                degree: sp.SparseMatrix(ranks.get(degree - 1, 0), ranks[degree], matrix)
                for degree, matrix in matrices.items()
            },
        )
        smith_groups = {row["degree"]: row["free_rank"] for row in smith["homology"] if row["free_rank"]}
        _require(smith_groups == groups, "independent Smith fiber homology differs")
        _require(
            all(not row["torsion_invariant_factors"] for row in smith["homology"]), "unexpected Smith fiber torsion"
        )
    return {"blocks": block_count, "cells": len(states), "homology": groups, "independent_smith": block_count <= 2}


def _reject(function: Callable[[], object], label: str) -> str:
    try:
        function()
    except ValueError:
        return label
    raise RuntimeError(f"negative control escapes rejection: {label}")


def cup_degree_certificate(bigrading: dict[tuple[int, int], int]) -> list[dict[str, object]]:
    """Exclude supported positive-degree products uniformly for even h>=4."""
    positive = sorted(key for key in bigrading if key != (0, 0))
    certificate = []
    for first_index, first in enumerate(positive):
        for second in positive[first_index:]:
            for target in positive:
                slope = first[0] + second[0] - target[0]
                intercept = first[1] + second[1] - target[1]
                if slope == 0:
                    _require(intercept != 0, "positive cup product degree is supported for all h")
                    root: str | None = None
                else:
                    candidate = sp.Rational(-intercept, slope)
                    _require(
                        not (candidate.is_Integer and candidate >= 4 and candidate % 2 == 0),
                        "positive cup degree is supported",
                    )
                    root = str(candidate)
                certificate.append(
                    {
                        "first": first,
                        "second": second,
                        "target": target,
                        "slope": slope,
                        "intercept": intercept,
                        "only_possible_h": root,
                    }
                )
    return certificate


def stage_homology_descriptor(bigrading: dict[tuple[int, int], int], stage: int) -> dict[str, Any]:
    """Record every stage's degree formulas without constructing powers of two."""
    model = DoublingModel(stage)
    return {
        "stage": stage,
        "groups": [
            {
                "degree": {"power_of_two_exponent": model.block_exponent, "multiplier": tops, "offset": offset},
                "free_rank": rank,
                "torsion_invariant_factors": [],
            }
            for (tops, offset), rank in sorted(bigrading.items())
        ],
    }


def stage_homology(bigrading: dict[tuple[int, int], int], stage: int) -> dict[int, int]:
    """Expand exact integer degrees through stage 4096, checking before shifts.

    stage_homology_descriptor retains exponent expressions for every larger
    stage. The concrete expansion bound controls integer storage and JSON size.
    """
    if type(stage) is not int or not 5 <= stage <= MAX_CONCRETE_STAGE:
        raise ValueError(f"concrete degree stage must be an integer in [5,{MAX_CONCRETE_STAGE}]")
    width = 1 << DoublingModel(stage).block_exponent
    groups: dict[int, int] = defaultdict(int)
    for (top_count, offset), multiplicity in bigrading.items():
        groups[width * top_count + offset] += multiplicity
    return dict(sorted(groups.items()))


def audit_four_support_homology() -> dict[str, Any]:
    characteristic = characteristic_identities()
    characteristic["oriented_point_facets"] = orientation_facets()
    base, cells, matrices = incidence_chains()
    ranks = {degree: len(values) for degree, values in cells.items()}
    validate_chains(ranks, matrices)
    verify_top_grading(cells, matrices)
    operations = generate_cancellations(ranks, matrices)
    verify_cancellation_grading(cells, operations)
    remaining, residual = replay_cancellations(ranks, matrices, operations)
    bigrading: dict[tuple[int, int], int] = Counter()
    top_summands: dict[tuple[int, ...], Counter[int]] = defaultdict(Counter)
    for degree, indices in remaining.items():
        for index in sorted(indices):
            top_factors = cells[degree][index].top_factors
            offset = degree - 4 * len(top_factors)
            bigrading[len(top_factors), offset] += 1
            top_summands[top_factors][offset] += 1
    _require(sum(ranks.values()) - 2 * len(operations) == sum(bigrading.values()), "cancellation generator accounting")
    _require(
        sum((-1) ** degree * rank for degree, rank in ranks.items())
        == sum((1 if offset % 2 == 0 else -1) * count for (_, offset), count in bigrading.items()),
        "Euler characteristic mismatch",
    )
    controls = []
    missing_cells = dict(ranks)
    missing_cells[0] -= 1
    controls.append(_reject(lambda: validate_chains(missing_cells, matrices), "missing_chain_generator"))
    bad_grading = deepcopy(matrices)
    for degree, matrix in bad_grading.items():
        if not matrix:
            continue
        row, column = next(iter(matrix))
        changed = next(
            (
                index
                for index, cell in enumerate(cells[degree])
                if cell.top_factors != cells[degree - 1][row].top_factors
            ),
            None,
        )
        if changed is not None:
            matrix[row, changed] = 1
            break
    controls.append(_reject(lambda: verify_top_grading(cells, bad_grading), "changed_top_factor_subset"))
    bad_product = incidence_chains(omit_product_sign=True)[2]
    controls.append(_reject(lambda: validate_chains(ranks, bad_product), "omitted_product_orientation"))
    bad_sign = deepcopy(matrices)
    key = next(iter(bad_sign[1]))
    bad_sign[1][key] *= -1
    controls.append(_reject(lambda: validate_chains(ranks, bad_sign), "flipped_incidence_sign"))
    bad_pivot = deepcopy(operations)
    bad_pivot[0]["unit"] *= -1
    controls.append(_reject(lambda: replay_cancellations(ranks, matrices, bad_pivot), "changed_pivot_unit"))
    bad_vector = deepcopy(operations)
    bad_vector[0]["row_vector"].append([-1, 1])
    controls.append(_reject(lambda: replay_cancellations(ranks, matrices, bad_vector), "changed_pivot_vector"))
    controls.append(_reject(lambda: replay_cancellations(ranks, matrices, operations[:-1]), "truncated_reduction"))
    torsion_ranks, torsion_maps = {0: 1, 1: 1}, {1: {(0, 0): 2}}
    controls.append(_reject(lambda: replay_cancellations(torsion_ranks, torsion_maps, []), "nonunit_torsion_residual"))
    torsion = integral_homology(torsion_ranks, {1: sp.Matrix([[2]])})
    _require(torsion["homology"][0]["torsion_invariant_factors"] == [2], "independent torsion witness")
    # The degree-one pivot exercises V^-1 on the following differential.
    shear_ranks = {0: 1, 1: 2, 2: 1}
    shear_maps = {1: {(0, 0): 1, (0, 1): -2}, 2: {(0, 0): 12, (1, 0): 6}}
    _, shear_residual = replay_cancellations(
        shear_ranks, shear_maps, generate_cancellations(shear_ranks, shear_maps), require_zero=False
    )
    _require(shear_residual[2] == {(1, 0): 6}, "integer basis shear loses torsion")
    # The degree-two pivot exercises U^-1 on the preceding differential.
    preceding_maps = {1: {(0, 0): 12, (0, 1): 6}, 2: {(0, 0): 1, (1, 0): -2}}
    _, preceding_residual = replay_cancellations(
        shear_ranks, preceding_maps, generate_cancellations(shear_ranks, preceding_maps), require_zero=False
    )
    _require(preceding_residual[1] == {(0, 1): 6}, "preceding inverse shear loses torsion")
    for invalid_stage, label in (
        (4, "stage_below_minimum"),
        (True, "boolean_stage"),
        (MAX_CONCRETE_STAGE + 1, "stage_above_concrete_limit"),
        (10**100, "huge_concrete_stage"),
    ):

        def invalid_stage_call(value: int = invalid_stage) -> object:
            return stage_homology(bigrading, value)

        controls.append(_reject(invalid_stage_call, label))
    descriptor = stage_homology_descriptor(bigrading, 10**100)
    _require(
        all(row["degree"]["power_of_two_exponent"] == 10**100 - 3 for row in descriptor["groups"]),
        "symbolic stage descriptor expands or changes its exponent",
    )
    fibers = parallel.ordered_map(_sphere_fixture, (1, 2, 3, 4), min_items=1)
    return {
        "schema": "four-support-integral-cellular-homology-v1",
        "scope": "Normalized first operand in span(e1,e10,e18,e25); unrestricted unit partner in each ambient algebra.",
        "proof_boundary": (
            "Geometric identification uses the explicit characteristic maps and "
            "global kernel-frame homeomorphism in the cited proof notes."
        ),
        "qpu_executed": False,
        "sympy_version": sp.__version__,
        "characteristic_map_identities": characteristic,
        "base_cells_by_dimension": dict(sorted(Counter(stratum.dimension for stratum in base).items())),
        "base_cells": [
            {
                "signs": stratum.signs,
                "cone_sign": stratum.cone_sign,
                "dimension": stratum.dimension,
                "kernel_blocks": sorted({slot // 4 for slot in stratum.kernel_slots}),
            }
            for stratum in base
        ],
        "cellular_generators": {
            degree: [{"base": cell.base, "states": cell.states} for cell in values] for degree, values in cells.items()
        },
        "chain_ranks": ranks,
        "boundaries": {
            degree: [[row, column, value] for (row, column), value in sorted(matrix.items())]
            for degree, matrix in matrices.items()
        },
        "boundary_squared_zero": True,
        "complete_top_factor_grading_preserved": True,
        "unit_cancellations": operations,
        "cancellation_count": len(operations),
        "remaining_boundary_entries": sum(map(len, residual.values())),
        "survivors": {degree: sorted(indices) for degree, indices in remaining.items() if indices},
        "survivor_bigrading": [
            {"top_count": top_count, "degree_offset": offset, "multiplicity": count}
            for (top_count, offset), count in sorted(bigrading.items())
        ],
        "top_factor_summands": [
            {"top_factors": tops, "survivor_offsets": dict(sorted(offsets.items()))}
            for tops, offsets in sorted(top_summands.items())
        ],
        "stage_5_integral_homology": stage_homology(bigrading, 5),
        "all_stage_rule": {
            "minimum_stage": 5,
            "block_width": "h=4*2^(n-5)",
            "degree": "h*top_count+degree_offset",
            "integer_boundary_independent_of_stage": True,
        },
        "large_stage_degree_regression": stage_homology(bigrading, 128),
        "concrete_degree_expansion_maximum_stage": MAX_CONCRETE_STAGE,
        "huge_stage_symbolic_descriptor": descriptor,
        "concrete_limit_degree_bit_lengths": [
            degree.bit_length() for degree in stage_homology(bigrading, MAX_CONCRETE_STAGE)
        ],
        "torsion_invariant_factors": [],
        "positive_cup_products": "zero by exhaustive symbolic degree exclusion for every even h>=4",
        "cup_degree_exclusion": cup_degree_certificate(bigrading),
        "fiber_fixture_results": fibers,
        "negative_controls": controls,
        "independent_torsion_fixture": torsion,
        "following_inverse_shear_residual": [
            [row, column, value] for (row, column), value in sorted(shear_residual[2].items())
        ],
        "preceding_inverse_shear_residual": [
            [row, column, value] for (row, column), value in sorted(preceding_residual[1].items())
        ],
        "homotopy_type_claimed": False,
    }


def main() -> int:
    print(json.dumps(audit_four_support_homology(), indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
