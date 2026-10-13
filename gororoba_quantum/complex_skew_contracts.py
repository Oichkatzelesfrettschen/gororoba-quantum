"""Independent exact controls for the complex annihilator representation."""

from __future__ import annotations

import json
from dataclasses import replace
from fractions import Fraction
from itertools import combinations
from typing import Any, cast

import sympy as sp

from complex_skew import (
    chart_transition,
    cleared_pair_residual,
    complex_operator,
    kernel_chart,
    kernel_to_real,
    pfaffian,
    pivot_cover,
    principal_pfaffians,
    real_rank_equations,
    realify,
    symbolic_operator,
    verify_kernel_chart,
)
from parallel import ordered_map
from rank_charts import multiplication_matrix
from rank_polynomials import evaluate_rank_polynomials


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def coefficient_control(dimension: int) -> dict[str, int]:
    half = dimension // 2
    conjugation = sp.diag(1, *([-1] * (half - 1)))
    change = sp.diag(sp.eye(half), conjugation)
    complex_conjugation = sp.diag(sp.eye(half), -sp.eye(half))
    for coordinate in range(dimension):
        if coordinate in (0, half):
            continue
        values = tuple(int(index == coordinate) for index in range(dimension))
        full = sp.Matrix(multiplication_matrix(values))
        operator = complex_operator(values)
        require(operator.T == -operator, "complex skew identity fails")
        require(change * full * change == realify(operator) * complex_conjugation, "intertwiner fails")
    symbols, matrix = symbolic_operator(dimension)
    require(matrix.T == -matrix, "symbolic skew identity fails")
    for first, second in pivot_cover(dimension):
        require(matrix[first, second] == -symbols[second] + sp.I * symbols[half + second], "cover entry differs")
    return {"dimension": dimension, "coefficient_operators": dimension - 2, "cover_domains": half - 1}


def point_control(task: tuple[str, dict[int, Fraction | int], int]) -> dict[str, Any]:
    label, entries, expected_nullity = task
    values = tuple(Fraction(entries.get(index, 0)) for index in range(32))
    operator = complex_operator(values)
    full = sp.Matrix(multiplication_matrix(values))
    spectral = evaluate_rank_polynomials(values)
    pfaffian_value = pfaffian(operator)
    pfaffian_norm = sp.expand(pfaffian_value * sp.conjugate(pfaffian_value))
    require(
        pfaffian_norm == spectral.norm_squared * spectral.elementary[-1],
        "Pfaffian norm and Newton determinant factor differ",
    )
    require(32 - len(full.to_DM().to_field().rref()[1]) == expected_nullity, "independent real rank differs")
    charts = [kernel_chart(values)]
    for order in (tuple(reversed(range(16))), tuple(range(1, 16)) + (0,)):
        selected = operator[:, list(order)].to_DM().to_field().rref()[1]
        charts.append(kernel_chart(values, tuple(order[index] for index in selected)))
    for chart in charts:
        require(chart.real_rank == 32 - expected_nullity, "complex/real rank relation fails")
        require(
            len(chart.real_frame.to_DM().to_field().rref()[1]) == expected_nullity, "transported kernel is incomplete"
        )
        require(chart.real_frame.T * chart.real_frame == realify(chart.hermitian_metric), "real kernel metric differs")
        require(
            sp.expand(
                pfaffian(operator.extract(chart.pivot_indices, chart.pivot_indices)) ** 2
                - operator.extract(chart.pivot_indices, chart.pivot_indices).det(method="domain-ge")
            )
            == 0,
            "Pfaffian square fails",
        )
    for source in charts:
        for target in charts:
            transport = chart_transition(source, target)
            inverse = chart_transition(target, source)
            require((inverse * transport).applyfunc(sp.simplify) == sp.eye(source.frame.cols), "overlap inverse fails")
            require(target.real_frame * realify(transport) == source.real_frame, "real transition fails")
            require(
                (transport.H * target.hermitian_metric * transport).applyfunc(sp.simplify) == source.hermitian_metric,
                "Hermitian metric transport fails",
            )
            for last in charts:
                require(
                    (chart_transition(target, last) * transport).applyfunc(sp.simplify)
                    == chart_transition(source, last),
                    "overlap cocycle fails",
                )
    return {
        "label": label,
        "coordinates": [str(value) for value in values],
        "real_nullity": expected_nullity,
        "pfaffian_norm_squared": str(pfaffian_norm),
        "newton_factor_identity": True,
        "complex_rank": charts[0].real_rank // 2,
        "pivot_indices": [list(chart.pivot_indices) for chart in charts],
        "overlap_pairs": 9,
        "overlap_triples": 27,
    }


def polynomial_controls() -> dict[str, int]:
    entries = sp.symbols("s0:15", real=True)
    generic = sp.zeros(6)
    for value, (row, column) in zip(entries, combinations(range(6), 2), strict=True):
        generic[row, column] = value
        generic[column, row] = -value
    require(
        sp.expand(pfaffian(generic) ** 2 - generic.det(method="domain-ge")) == 0, "generic Pfaffian determinant fails"
    )
    require(pfaffian(sp.zeros(0)) == 1 and pfaffian(sp.zeros(3)) == 0, "empty/odd conventions fail")
    require(len(list(principal_pfaffians(generic, 4))) == 15, "principal enumeration is incomplete")
    require(list(real_rank_equations(4, 4)) == [], "full rank bound must have no equations")
    equations = list(real_rank_equations(4, 0))
    require(
        len(equations) == 1 and equations[0][1:] == (-sp.Symbol("x1", real=True), sp.Symbol("x3", real=True)),
        "rank-zero real polynomial splitting fails",
    )
    _, matrix = symbolic_operator(32)
    checked = 0
    for index in range(1, 16):
        pivot, cleared = cleared_pair_residual(32, index)
        free = tuple(position for position in range(16) if position not in (0, index))
        require(pivot == matrix[0, index], "cleared pivot differs")
        for row, column in combinations(range(14), 2):
            indices = (0, index, free[row], free[column])
            require(
                sp.expand(cleared[row, column] - pfaffian(matrix.extract(indices, indices))) == 0,
                "cleared residual/Pfaffian identity fails",
            )
            checked += 1
    return {"generic_skew_order": 6, "dimension32_cover_domains": 15, "cleared_pfaffian_identities": checked}


def negative_controls() -> dict[str, int]:
    values = tuple(int(index in (1, 18)) for index in range(32))
    chart = kernel_chart(values)
    changed = sp.MutableDenseMatrix(chart.frame)
    changed[0, 0] += 1
    mutations = (
        replace(chart, coordinates=tuple(value * 2 for value in chart.coordinates)),
        replace(chart, pivot_pfaffian=chart.pivot_pfaffian + 1),
        replace(chart, frame=sp.ImmutableMatrix(changed)),
        replace(chart, real_frame=kernel_to_real(chart.frame.conjugate())),
        replace(chart, hermitian_metric=chart.hermitian_metric + sp.eye(chart.frame.cols)),
        replace(chart, pivot_indices=tuple(reversed(chart.pivot_indices))),
    )
    # The conjugation mutant must actually change a non-real frame.
    require(chart.frame != chart.frame.conjugate(), "conjugation negative control is vacuous")
    for mutant in mutations:
        require(not verify_kernel_chart(mutant), "mutated chart passes verification")
    rejected = 0
    for callback in (
        lambda: complex_operator(cast(Any, (0, 1.0, 0, 0))),
        lambda: complex_operator((1, 0, 0, 0)),
        lambda: complex_operator((0, 0, 1, 0)),
        lambda: symbolic_operator(12),
        lambda: kernel_chart(values, (0, 1)),
        lambda: kernel_chart(values, (0, 0)),
        lambda: pfaffian(sp.eye(2)),
        lambda: pfaffian(sp.Matrix([[0, 1.0], [-1.0, 0]])),
        lambda: list(principal_pfaffians(sp.zeros(4), 3)),
        lambda: list(real_rank_equations(32, 6)),
        lambda: cleared_pair_residual(32, 0),
        lambda: chart_transition(chart, kernel_chart(tuple(2 * value for value in values))),
    ):
        try:
            callback()
        except ValueError:
            rejected += 1
        else:
            raise RuntimeError("out-of-domain input passes")
    return {"chart_mutations_rejected": len(mutations), "invalid_inputs_rejected": rejected}


def audit() -> dict[str, Any]:
    coefficient_checks = ordered_map(coefficient_control, [4, 8, 16, 32, 64], min_items=2)
    tasks: list[tuple[str, dict[int, Fraction | int], int]] = [
        ("nullity4", {1: 1, 10: Fraction(1, 4), 18: Fraction(5, 8), 25: Fraction(1, 8)}, 4),
        ("nullity8", {1: 1, 10: 1}, 8),
        ("nullity12", {1: 1, 18: 1}, 12),
        ("nullity16", {1: 1, 10: 1, 18: 1, 25: -1}, 16),
        ("dense_invertible", {index: Fraction(index + 1, 31) for index in range(32) if index not in (0, 16)}, 0),
        ("origin", {}, 32),
    ]
    return {
        "schema": "complex-skew-certificate-v1",
        "coefficient_checks": coefficient_checks,
        "point_checks": ordered_map(point_control, tasks, min_items=2),
        "polynomial_checks": polynomial_controls(),
        "negative_controls": negative_controls(),
        "qpu_executed": False,
        "scope": (
            "All-stage written coordinate and chart identities; executable exact point API through dimension 256; "
            "finite controls through dimension 64. Rank components, smooth strata "
            "and unrestricted attachments remain open."
        ),
    }


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2, sort_keys=True))
