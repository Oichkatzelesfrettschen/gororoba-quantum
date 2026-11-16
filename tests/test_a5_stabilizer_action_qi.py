"""Action of the base-point stabilizer on the fiber-cone generators: parsing, the exact solve and the record rules."""

from __future__ import annotations

import json
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "docs" / "evidence" / "a5-kernel-attachments"))

import stabilizer_action_qi as action  # noqa: E402
import symmetry_algebra_qi as qi  # noqa: E402


def _same(found: object, expected: object) -> None:
    if found != expected:
        raise AssertionError((found, expected))


def test_singular_polynomials_parse_to_gaussian_coefficients() -> None:
    table = action.parse_polynomial("(2*i-1)*s1^2*s9+(-1/2)*s2")
    expected = {
        (2, 0, 0, 0, 0, 0, 0, 0, 1): qi.Gauss(-1, 2),
        (0, 1, 0, 0, 0, 0, 0, 0, 0): qi.Gauss(qi.fmpq(-1, 2), 0),
    }
    _same(table, expected)
    _same(action.parse_polynomial("0"), {})


def test_action_matrix_solves_on_the_span_and_refuses_a_form_outside_it() -> None:
    generators = [action.parse_polynomial(text) for text in ("s1", "s2+(i)*s3")]
    inside = [action.parse_polynomial(text) for text in ("(3*i)*s1+2*s2+(2*i)*s3", "0")]
    matrix = action.action_matrix(generators, inside)
    if matrix is None:
        raise AssertionError("a derivative in the span has no matrix")
    _same(matrix.rows(), [[qi.Gauss(0, 3), qi.Gauss(2, 0)], [qi.ZERO, qi.ZERO]])
    # s2 alone is outside the span of s1 and s2 + i s3.
    _same(action.action_matrix(generators, [action.parse_polynomial("s2"), action.parse_polynomial("0")]), None)


def test_the_fourth_pfaffian_index_follows_the_loop_order_of_the_producer() -> None:
    _same(
        (action.PFAFFIAN_INDEX[0], action.PFAFFIAN_INDEX[1], action.PFAFFIAN_INDEX[-1]),
        ((1, 2, 3, 4), (1, 2, 3, 5), (6, 7, 8, 9)),
    )
    _same(len(action.PFAFFIAN_INDEX), 126)


def test_retained_record_passes_its_rules_and_each_mutation_fails_them() -> None:
    record = json.loads(action.RECORD.read_text(encoding="utf-8"))
    _same((record["pass"], action.verdict(record), len(record["rows"])), (True, [], 8))
    _same([entry["dimension"] for entry in record["stabilizers"]], [9, 9])
    expected = {"W8": 26, "E8bar": 34, "Iso": 17, "X": 23}
    for row in record["rows"]:
        source = row["incidence"].split("->")[0].rstrip("+-")
        _same((row["image_plus_radical_dimension"], row["image_dimension"]), (expected[source], 9))
    changes: dict[str, Callable[[dict[str, Any]], Any]] = {
        "normal forms": lambda r: r.update(generator_normal_forms_rank=1),
        "missing matrix": lambda r: r.update(elements_with_a_matrix=8),
        "outside g": lambda r: r.update(elements_in_symmetry_algebra=8),
        "brackets": lambda r: r.update(bracket_signs=["minus", "plus"]),
        "grading": lambda r: r.update(grading_image_minus_weights=None, grading_image_plus_weights=None),
        "off-diagonal grading": lambda r: r.update(grading_image_is_diagonal=False),
        "control": lambda r: r.update(control_diagonal_has_a_matrix=True),
        "moving": lambda r: r.update(moving_in_symmetry_algebra=True),
        "span": lambda r: r.update(image_plus_radical_dimension=1),
        "stabilizer dimension": lambda r: r.update(stabilizer_dimension=8, elements_with_a_matrix=8),
        "injectivity": lambda r: r.update(image_dimension=8),
        "levi": lambda r: r.update(grading_zero_image_modulo_radical=2),
        "unipotent": lambda r: r.update(grading_nonzero_image_in_radical=False),
    }
    for name, change in changes.items():
        mutated = json.loads(json.dumps(record))
        change(mutated["rows"][0])
        if action.verdict(mutated) == []:
            raise AssertionError(f"a record mutated at {name} passes")
