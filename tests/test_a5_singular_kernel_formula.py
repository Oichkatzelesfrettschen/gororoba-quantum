"""Kernel formula at the singular points of V(G): the vectors, the point rows, the point set and the record rules."""

from __future__ import annotations

import json
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "docs" / "evidence" / "a5-kernel-bundles-residuals"))

import singular_kernel_formula as formula  # noqa: E402

import cd_core  # noqa: E402

Mutation = tuple[str, Callable[[dict[str, Any]], Any]]
E1 = (1, 0, 0, 0, 0, 0, 0)
E2 = (0, 1, 0, 0, 0, 0, 0)


def _same(found: object, expected: object) -> None:
    if found != expected:
        raise AssertionError((found, expected))


def test_kernel_vectors_annihilate_the_point_under_the_cd_core_product() -> None:
    # At (a, b) = (e_1, e_2) the sedenion product z k has zero imaginary part for each k = k(e_j), by cd_core.
    point = [0, *E1, 0, *E2]
    vectors = formula.kernel_vectors(E1, E2)
    _same(len(vectors), 7)
    nonzero = 0
    for vector in vectors:
        _same((vector[0], vector[8]), (0, 0))
        product = [int(x) for x in cd_core.cd_multiply_exact(16, point, [0, *vector[1:]])]
        _same(product[1:], [0] * 15)
        nonzero += any(vector)
    # The associator [a, b, e_j] vanishes for e_j in span(e_1, e_2, e_3) and is nonzero on the complement.
    _same(nonzero, 4)
    _same(formula.formula_holds(E1, E2), True)


def test_point_rows_on_and_off_the_locus_modulo_three() -> None:
    # Norm 1: every statement holds, also modulo 3, 5 and 7.
    _same(formula.point_row((E1, E2)), [True, True, True, [True] * 3, [True] * 3, [True] * 3])
    # Norm 3: modulo 3 the pair leaves the locus, so its modular statements are not counted.
    first, second = (1, 1, 1, 0, 0, 0, 0), (1, -1, 0, 1, 0, 0, 0)
    _same(formula.point_row((first, second)), [True, True, True, [False] * 3, [True] * 3, [True] * 3])


def test_formula_fails_off_the_locus() -> None:
    _same(formula.formula_holds(*formula.CONTROL_PAIR), False)
    # Equal norms with N(a, b) nonzero, and N(a, b) = 0 with unequal norms.
    _same(formula.formula_holds((1, 1, 0, 0, 0, 0, 0), (1, 0, 1, 0, 0, 0, 0)), False)
    _same(formula.formula_holds((1, 1, 0, 0, 0, 0, 0), (0, 0, 1, 0, 0, 0, 0)), False)


def test_pairs_lie_on_the_locus_with_the_pinned_norms_and_signs() -> None:
    pairs = formula.pairs()
    _same(len(pairs), formula.POINTS["points"])
    _same(len(set(pairs)), len(pairs))
    for first, second in pairs[::97]:
        norm = sum(x * x for x in first)
        _same(norm in formula.NORMS and norm == sum(x * x for x in second), True)
        _same(sum(x * y for x, y in zip(first, second, strict=True)), 0)
        _same(next(x for x in first if x) > 0 and next(x for x in second if x) > 0, True)


@pytest.mark.audit
def test_point_counts_are_recomputed() -> None:
    _same(formula.point_record(), (formula.POINTS, formula.MODULAR))


def test_retained_record_passes_its_rules_and_each_mutation_fails_them() -> None:
    text = formula.RECORD.read_text(encoding="utf-8")
    _same(formula.verdict(json.loads(text)), [])
    _same(text, formula._serialized(formula.expected_record()))

    def put(path: tuple[Any, ...], value: Any) -> Callable[[dict[str, Any]], Any]:
        def change(found: dict[str, Any]) -> None:
            target: Any = found
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = value

        return change

    mutations: list[Mutation] = [
        ("the kernel formula, the span dimension or the rank fails", put(("points", "formula_holds"), 6523)),
        ("the kernel formula, the span dimension or the rank fails", put(("points", "rank_ten"), 6523)),
        ("modulo a prime differs", put(("modular", "3", "span_dimension_five"), 923)),
        ("modulo a prime differs", put(("modular", "7", "rank_ten"), 0)),
        ("the control pair off the locus differs", put(("control", "formula_holds"), True)),
        ("the input digests differ", put(("inputs", "gororoba_quantum/cd_core.py"), "0" * 64)),
        ("the record states that it fails", put(("pass",), False)),
        ("the record differs from the record the constants determine", put(("norms", 0), 4)),
        ("other fields or value types", put(("points", "points"), True)),
        ("other fields or value types", put(("extra",), 1)),
    ]
    for message, change in mutations:
        mutated = json.loads(text)
        change(mutated)
        problems = formula.verdict(mutated)
        if not any(message in problem for problem in problems):
            raise AssertionError((message, problems))
