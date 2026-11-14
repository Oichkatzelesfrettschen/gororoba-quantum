"""Kernel product as a Pfaffian tensor: the Pfaffian, the sign, the tensor, the gradients, grids, points and rules."""

from __future__ import annotations

import itertools
import json
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "docs" / "evidence" / "a5-kernel-bundles-residuals"))

import kernel_product_pfaffian_tensor as tensor  # noqa: E402
from nullity4_gauss_image import STRATA, _fixture_splits  # noqa: E402
from sympy import QQ_I  # noqa: E402
from sympy.polys.matrices import DomainMatrix  # noqa: E402

import cd_core  # noqa: E402

Mutation = tuple[str, Callable[[dict[str, Any]], Any]]


def _same(found: object, expected: object) -> None:
    if found != expected:
        raise AssertionError((found, expected))


def _skew(entries: list[int], size: int) -> list[list[Any]]:
    matrix = [[QQ_I.zero] * size for _ in range(size)]
    for value, (r, c) in zip(entries, itertools.combinations(range(size), 2), strict=True):
        matrix[r][c], matrix[c][r] = QQ_I.convert(value), QQ_I.convert(-value)
    return matrix


def test_pfaffian_matches_the_order_four_formula_and_squares_to_the_determinant() -> None:
    _same(tensor.pfaffian(_skew([1, 2, 3, 4, 5, 6], 4)), QQ_I.convert(1 * 6 - 2 * 5 + 3 * 4))
    # A zero in the first pivot position forces the simultaneous swap.
    swapped = _skew([0, 2, 3, 4, 5, 6], 4)
    _same(tensor.pfaffian(swapped), QQ_I.convert(0 * 6 - 2 * 5 + 3 * 4))
    six = _skew([3, -1, 4, 1, -5, 9, 2, -6, 5, 3, 5, -8, 9, 7, -9], 6)
    value = tensor.pfaffian(six)
    _same(bool(value), True)
    _same(value * value, DomainMatrix(six, (6, 6), QQ_I).det())
    # A skew matrix with a zero first row has Pfaffian 0.
    _same(tensor.pfaffian(_skew([0, 0, 0, 4, 5, 6], 4)), QQ_I.zero)


def test_complement_sign_is_the_sign_of_the_shuffle() -> None:
    for triple in tensor.TRIPLES:
        order = [*triple, *(k for k in range(15) if k not in triple)]
        inversions = sum(order[i] > order[j] for i in range(15) for j in range(i + 1, 15))
        _same(tensor.complement_sign(triple), -1 if inversions % 2 else 1)


def test_product_tensor_of_a_basis_three_vector_is_the_cyclic_sum_of_products() -> None:
    # tau(e_2 ^ e_5 ^ e_11) = Im(e_2 e_5) (x) e_11 + Im(e_5 e_11) (x) e_2 + Im(e_11 e_2) (x) e_5, from cd_core.
    triple = (1, 4, 10)
    found = tensor.product_tensor({triple: QQ_I.one})
    expected = [[QQ_I.zero] * 15 for _ in range(15)]
    for x, y, w in ((0, 1, 2), (1, 2, 0), (2, 0, 1)):
        first, second = [0] * 16, [0] * 16
        first[triple[x] + 1], second[triple[y] + 1] = 1, 1
        product = [int(v) for v in cd_core.cd_multiply_exact(16, first, second)][1:]
        for row, value in enumerate(product):
            expected[row][triple[w]] = expected[row][triple[w]] + QQ_I.convert(value)
    _same(found, expected)


def test_grid_rows_on_each_family() -> None:
    # Fields: the gradient identity, rank 12, Q = 0, G = 0, T = 0.
    # FQ at (A, B) = (1, 2): a rank-12 point of V(Q) minus V(G). (2, 2): s = 0, so G = 0 and T = 0.
    _same(tensor.grid_row(("FQ", 1, 2)), [True, True, True, False, False])
    diagonal = tensor.grid_row(("FQ", 2, 2))
    _same([diagonal[0], *diagonal[2:]], [True, True, True, True])
    # FG+ and FG- at (m, u) = (1, 2): rank-12 points of V(G) minus V(Q), where T = -Q grad G (x) z is nonzero.
    _same(tensor.grid_row(("FG+", 1, 2)), [True, True, False, True, False])
    _same(tensor.grid_row(("FG-", 1, 2)), [True, True, False, True, False])
    # FG- at m = 2 u: s = 0, so Q = G = 0, the rank is below 12 and T = 0.
    _same(tensor.grid_row(("FG-", 2, 1)), [True, False, True, True, True])


def test_gradients_match_finite_differences_of_the_invariants() -> None:
    # grad G and grad(Q G) against the exact difference quotient of a polynomial of degree at most 6 on a line:
    # the derivative at 0 of f(z + h e_k) from the values at h = -3, ..., 3 by the central seven-point stencil.
    point = [QQ_I.convert(x) for x in (3, -1, 4, 1, -5, 9, 2, 6, -5, 3, 5, -8, 9, 7, -9)]
    weights = {1: (3, 4), 2: (-3, 20), 3: (1, 60)}

    def derivative(function: Callable[[list[Any]], Any], index: int) -> Any:
        total = QQ_I.zero
        for step, (numerator, denominator) in weights.items():
            up, down = list(point), list(point)
            up[index], down[index] = up[index] + step, down[index] - step
            total = total + QQ_I.convert(numerator) / QQ_I.convert(denominator) * (function(up) - function(down))
        return total

    for index in range(15):
        _same(tensor.quartic_gradient(point)[index], derivative(lambda z: tensor.invariants(z)[1], index))
        _same(
            tensor.product_gradient(point)[index],
            derivative(lambda z: tensor.invariants(z)[0] * tensor.invariants(z)[1], index),
        )


def test_special_and_singular_points_are_recomputed() -> None:
    for strings, facts in zip(tensor.SPECIAL_POINTS, tensor.SPECIAL_POINT_FACTS, strict=True):
        _same(tensor.special_point_record(strings), {"point": list(strings), **facts})
    for strings, singular in zip(tensor.SINGULAR_POINTS, tensor.SINGULAR_POINT_FACTS, strict=True):
        _same(tensor.singular_point_record(strings), {"point": list(strings), **singular})


def test_general_point_satisfies_the_identity_with_the_identity_matrix_term() -> None:
    # One rank-14 point off V(Q) u V(G): T = -grad(Q G) (x) z - Q G I; the second point is in the audit test.
    _same(
        tensor.general_point_record(tensor.GENERAL_POINTS[0]),
        {"point": list(tensor.GENERAL_POINTS[0]), **tensor.GENERAL_POINT_FACTS[0]},
    )


def test_pfaffian_rejects_a_matrix_that_is_not_skew() -> None:
    matrix = _skew([1, 2, 3, 4, 5, 6], 4)
    matrix[0][1] = QQ_I.convert(7)
    with pytest.raises(RuntimeError, match="not skew"):
        tensor.pfaffian(matrix)


def test_calibration_is_recomputed() -> None:
    _same(tensor.calibration_record(), tensor.CALIBRATION)


def test_fixture_rows_at_the_first_fixture_of_each_stratum() -> None:
    expected = {STRATA[0]: [True, True, False, True, True, True], STRATA[1]: [False, True, False, True, True, False]}
    expected[STRATA[2]] = [True, True, True, True, True, True]
    for stratum in STRATA:
        job = next(job for job in _fixture_splits() if job[1] == stratum)
        _same(tensor.fixture_row(job), [stratum, *expected[stratum]])


def test_three_vector_is_not_the_kernel_three_vector_off_rank_twelve() -> None:
    # A general point has rank 14 and a one-dimensional kernel, so `spans_kernel` is False.
    point = [QQ_I.convert(x) for x in (3, -1, 4, 1, -5, 9, 2, 6, -5, 3, 5, -8, 9, 7, -9)]
    facts = tensor.point_facts(point)
    _same((facts["kernel_dimension"], facts["three_vector_spans_kernel"], facts["identity_holds"]), (1, False, False))
    _same(facts["gradient_identity_holds"], False)


@pytest.mark.audit
def test_grid_fixture_and_general_point_records_are_recomputed() -> None:
    _same(tensor.grid_record(), tensor.GRID_COUNTS)
    _same(tensor.fixture_record(), tensor.FIXTURE_COUNTS)
    for strings, general in zip(tensor.GENERAL_POINTS, tensor.GENERAL_POINT_FACTS, strict=True):
        _same(tensor.general_point_record(strings), {"point": list(strings), **general})
    # At an integer point every coordinate of P is an integer: the identity is one of integer polynomials.
    point = [QQ_I.convert(int(x)) for x in tensor.GENERAL_POINTS[0]]
    for value in tensor.three_vector(point).values():
        _same((value.x.denominator, value.y), (1, 0))


def test_retained_record_passes_its_rules_and_each_mutation_fails_them(monkeypatch: pytest.MonkeyPatch) -> None:
    record = json.loads(tensor.RECORD.read_text(encoding="utf-8"))
    # The rules run against the digests the record retains; the on-demand gate compares them with the live sources.
    retained_inputs = dict(record["inputs"])
    monkeypatch.setattr(tensor, "_inputs", lambda: dict(retained_inputs))
    _same(tensor.verdict(record), [])
    _same(tensor.RECORD.read_text(encoding="utf-8"), tensor._serialized(tensor.expected_record()))

    def put(path: tuple[Any, ...], value: Any) -> Callable[[dict[str, Any]], Any]:
        def change(found: dict[str, Any]) -> None:
            target: Any = found
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = value

        return change

    mutations: list[Mutation] = [
        ("the Pfaffian routine fails its calibration", put(("calibration", "pfaffian_4x4"), "-8")),
        ("the Pfaffian routine fails its calibration", put(("calibration", "pfaffian_squared_is_determinant"), False)),
        ("the identity T = -grad(Q G) (x) z does not hold", put(("grids", "FQ", "gradient_identity_holds"), 48)),
        ("the identity T = -grad(Q G) (x) z does not hold", put(("grids", "FG+", "gradient_identity_holds"), 90)),
        ("the identity T = -grad(Q G) (x) z does not hold", put(("grids", "FG-", "tensor_zero"), 4)),
        ("a point with N1(z) = 0 differs", put(("special_points", 0, "tensor_zero"), True)),
        ("a point with N1(z) = 0 differs", put(("special_points", 2, "N1"), "1")),
        ("a singular point of V(G) differs", put(("singular_points", 0, "kernel_dimension"), 3)),
        ("a singular point of V(G) differs", put(("singular_points", 2, "quartic_gradient_zero"), False)),
        ("the fixture tallies differ", put(("fixtures", STRATA[1], "gradient_identity_holds"), 51)),
        ("fails at a general point", put(("general_points", 0, "global_identity_holds"), False)),
        ("fails at a general point", put(("general_points", 1, "Q"), "0")),
        ("the fixture tallies differ", put(("fixtures", STRATA[0], "tensor_zero"), 1)),
        ("the fixture tallies differ", put(("fixtures", STRATA[2], "kernel_is_null"), 1)),
        ("the input digests differ", put(("inputs", "gororoba_quantum/cd_core.py"), "0" * 64)),
        ("the record states that it fails", put(("pass",), False)),
        ("the record differs from the record the constants determine", put(("constant",), -3)),
        ("other fields or value types", put(("grids", "FQ", "points"), True)),
        ("other fields or value types", put(("extra",), 1)),
    ]
    for message, change in mutations:
        mutated = json.loads(tensor.RECORD.read_text(encoding="utf-8"))
        change(mutated)
        problems = tensor.verdict(mutated)
        if not any(message in problem for problem in problems):
            raise AssertionError((message, problems))
