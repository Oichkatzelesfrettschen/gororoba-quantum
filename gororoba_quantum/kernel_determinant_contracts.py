"""Exact volume, complementary-minor, and boundary controls."""

from __future__ import annotations

import json
from dataclasses import replace
from fractions import Fraction
from itertools import combinations
from typing import Any

import sympy as sp

from complex_skew import chart_transition, complex_operator, kernel_chart, pfaffian, realify
from kernel_determinant import determinant_transition, kernel_plucker_coordinates, kernel_volume, unit_volume_frame
from parallel import ordered_map


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def point_control(task: tuple[int, dict[int, int | Fraction], int]) -> dict[str, Any]:
    dimension, entries, nullity = task
    values = tuple(Fraction(entries.get(index, 0)) for index in range(dimension))
    operator = complex_operator(values)
    half = dimension // 2
    charts = [kernel_chart(values)]
    for order in (tuple(reversed(range(half))), tuple(range(1, half)) + (0,)):
        selected = operator[:, list(order)].to_DM().to_field().rref()[1]
        charts.append(kernel_chart(values, tuple(order[index] for index in selected)))
    require(charts[0].frame.cols * 2 == nullity, "fixture nullity differs")
    factors = []
    for source in charts:
        for target in charts:
            factor = determinant_transition(source, target)
            factors.append(str(factor))
            transport = chart_transition(source, target)
            real_determinant = realify(transport).det(method="domain-ge")
            require(sp.cancel(real_determinant - factor * sp.conjugate(factor)) == 0, "real orientation identity fails")
            require(bool(real_determinant > 0), "real transition reverses orientation")
            if nullity:
                source_frame, target_frame = unit_volume_frame(source), unit_volume_frame(target)
                target_scale = sp.eye(nullity // 2)
                target_scale[0, 0] = kernel_volume(target)
                normalized = target_scale * source_frame.extract(target.free_indices, range(nullity // 2))
                require(
                    (target_frame * normalized - source_frame).applyfunc(sp.cancel).is_zero_matrix is True,
                    "normalized transition reconstructs the wrong frame",
                )
                require(
                    sp.cancel(normalized.det(method="domain-ge") - 1) == 0, "normalized determinant differs from one"
                )
    # Every complementary minor is checked on the small and corank-two fixtures.
    plucker_count = 0
    if dimension <= 16 or nullity in (0, 4, dimension):
        coefficients = list(kernel_plucker_coordinates(charts[0]))
        plucker_count = len(coefficients)
        require(any(value != 0 for _, value in coefficients), "determinant section vanishes at constant rank")
        require(coefficients == list(kernel_plucker_coordinates(charts[1])), "polynomial section depends on chart")
    return {
        "dimension": dimension,
        "real_nullity": nullity,
        "transition_determinants": factors,
        "complete_plucker_coordinates": plucker_count,
        "overlap_pairs": 9,
    }


def symbolic_control() -> dict[str, Any]:
    # A full four-dimensional rank-two chart has arbitrary complex cross entries.
    pivot, first, second, third, fourth = sp.symbols("p a b c d")
    block = sp.Matrix([[0, pivot], [-pivot, 0]])
    cross = sp.Matrix([[first, second], [third, fourth]])
    frame = (-block.inv() * cross).col_join(sp.eye(2))
    operator = block.row_join(cross).col_join((-cross.T).row_join(-cross.T * block.inv() * cross))
    require((operator * frame).is_zero_matrix is True, "symbolic kernel fails")
    checked = 0
    for free in combinations(range(4), 2):
        complement = tuple(index for index in range(4) if index not in free)
        inversions = sum(index - position for position, index in enumerate(complement))
        coefficient = (-1) ** inversions * pfaffian(operator.extract(complement, complement))
        require(
            sp.cancel(coefficient - pivot * frame.extract(free, (0, 1)).det()) == 0,
            "symbolic complementary-minor identity fails",
        )
        checked += 1
    # Scaling preserves the punctured kernel and makes every order-two coefficient vanish at zero.
    parameter = sp.Symbol("t", real=True)
    require(
        all(sp.cancel(value).subs(parameter, 0) == 0 for value in parameter * operator),
        "rank-drop polynomial section fails to vanish",
    )
    alternate = frame.extract((1, 3), (0, 1))
    require(sp.cancel(alternate.det() + first / pivot) == 0, "symbolic overlap volume ratio fails")
    require(alternate.det().subs({first: 2, pivot: 1}) == -2, "nonunit determinant control fails")
    skew_plane = sp.Matrix([[0, parameter], [-parameter, 0]])
    paths = (sp.diag(skew_plane, sp.zeros(2)), sp.diag(sp.zeros(2), skew_plane))
    persistent = (sp.eye(4)[:, 2:], sp.eye(4)[:, :2])
    for path, kernel in zip(paths, persistent, strict=True):
        require(path.subs(parameter, 0) == sp.zeros(4), "rank-drop endpoint differs")
        require(path * kernel == sp.zeros(4, 2), "persistent plane fails")
    require(
        persistent[0] * persistent[0].T != persistent[1] * persistent[1].T,
        "rank-drop paths fail to separate limiting planes",
    )
    return {
        "ambient_complex_dimension": 4,
        "complex_rank": 2,
        "independent_complex_parameters": 5,
        "complete_plucker_coordinates": checked,
        "domain": "p != 0",
        "rank_drop_vanishes": True,
        "symbolic_overlap_determinant": str(alternate.det()),
        "distinct_kernel_planes_at_same_endpoint": True,
    }


def negative_controls() -> dict[str, int]:
    chart = kernel_chart(tuple(int(index in (1, 18)) for index in range(32)))
    damaged = replace(chart, pivot_pfaffian=2 * chart.pivot_pfaffian)
    calls = [
        lambda: kernel_volume(damaged),
        lambda: unit_volume_frame(damaged),
        lambda: list(kernel_plucker_coordinates(damaged)),
        lambda: determinant_transition(chart, damaged),
        lambda: determinant_transition(chart, kernel_chart(tuple(2 * value for value in chart.coordinates))),
        lambda: unit_volume_frame(kernel_chart((0, 1, 0, 0))),
    ]
    for call in calls:
        try:
            call()
        except ValueError:
            continue
        raise RuntimeError("invalid determinant input is accepted")
    # A non-real ratio refutes dropping the distinction between complex and real determinant.
    transport = sp.diag(1 + sp.I, 1)
    require(transport.det() != realify(transport).det(), "complex determinant mutation escapes control")
    require(realify(transport).det() == 2, "real determinant norm is incorrect")
    return {"rejected_inputs": len(calls), "complex_real_determinant_counterexamples": 1}


def audit() -> dict[str, Any]:
    tasks: list[tuple[int, dict[int, int | Fraction], int]] = [
        (4, {}, 4),
        (4, {1: 1}, 0),
        (16, {1: 1, 10: 1}, 4),
        (32, {1: 1, 10: Fraction(1, 4), 18: Fraction(5, 8), 25: Fraction(1, 8)}, 4),
        (32, {1: 1, 10: 1}, 8),
        (32, {1: 1, 18: 1}, 12),
        (32, {1: 1, 10: 1, 18: 1, 25: -1}, 16),
        (32, {}, 32),
    ]
    return {
        "schema": "kernel-determinant-certificate-v1",
        "points": ordered_map(point_control, tasks, min_items=2),
        "symbolic": symbolic_control(),
        "negative_controls": negative_controls(),
        "qpu_executed": False,
        "scope": (
            "Written all-stage determinant-line trivialization; "
            "exact controls do not classify full bundles or attachments."
        ),
    }


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2, sort_keys=True))
