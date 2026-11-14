"""The rank matrices [dF | F] of the two W8 arc families over Q(i), with their ranks recomputed exactly."""

from __future__ import annotations

import copy
import hashlib
import json
import sys
from collections.abc import Callable
from fractions import Fraction
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
TRANSFER = ROOT / "docs" / "evidence" / "a5-char0-transfer"
sys.path.insert(0, str(TRANSFER))

import w8_component_arc_matrices_qi as matrices  # noqa: E402

ONE = (Fraction(1), Fraction(0))
IMAGINARY = (Fraction(0), Fraction(1))
MINUS_ONE = (Fraction(-1), Fraction(0))


def _same(found: object, expected: object) -> None:
    if found != expected:
        raise AssertionError((found, expected))


def _record() -> dict[str, Any]:
    record: dict[str, Any] = json.loads(matrices.RECORD.read_text(encoding="utf-8"))
    return record


def _matrix(record: dict[str, Any], name: str) -> dict[str, Any]:
    matrix: dict[str, Any] = next(m for m in record["matrices"] if m["id"] == name)
    return matrix


def test_the_retained_record_passes_and_agrees_with_the_arc_record() -> None:
    record = _record()
    _same(matrices.problems(record), [])
    _same(matrices.arc_record_problems(record), [])
    _same(record["pass"], True)
    _same(len(record["matrices"]), 8)


def test_every_matrix_has_24_rows_six_columns_and_rank_six_over_the_gaussian_rationals() -> None:
    for matrix in _record()["matrices"]:
        entries = matrices.entries_of(matrix)
        _same((len(entries), {len(row) for row in entries}), (24, {6}))
        _same(matrices.gaussian_rank(entries), 6)
        _same(matrices.gaussian_rank([row[:5] for row in entries]), 5)


def test_the_rank_is_taken_over_the_gaussian_rationals() -> None:
    """The rows (1, i) and (i, -1) are proportional by i, so the rank is 1; over Q they would read as rank 2."""
    _same(matrices.gaussian_rank([[ONE, IMAGINARY], [IMAGINARY, MINUS_ONE]]), 1)
    _same(matrices.gaussian_rank([[ONE, IMAGINARY], [IMAGINARY, ONE]]), 2)
    _same(matrices.gaussian_rank([[matrices.ZERO, ONE], [ONE, matrices.ZERO], [ONE, ONE]]), 2)
    _same(matrices.gaussian_rank([[matrices.ZERO, matrices.ZERO]]), 0)
    _same(matrices.gaussian_rank([]), 0)


def test_the_two_basepoints_carry_the_same_shape_of_limit() -> None:
    record = _record()
    for family in ("linear", "series"):
        for which in (1, 2):
            minus = _matrix(record, f"w8-nm-{family}-point{which}")
            plus = _matrix(record, f"w8-np-{family}-point{which}")
            _same(minus["point"], plus["point"])
            _same(minus["columns_meaning"], plus["columns_meaning"])
            _same(minus["order_of_G"], plus["order_of_G"])


def test_the_script_is_the_arc_script_with_the_entries_printed_before_quit() -> None:
    script = matrices.singular_script("w8-nm", "linear", 1, matrices.arcs.SLICE_VARIABLES)
    base = matrices.arcs.singular_script("w8-nm", "linear", 1, matrices.arcs.SLICE_VARIABLES)
    _same(script, base[: -len("quit;\n")] + matrices.DUMP + "\nquit;\n")
    for fragment in ("ring RT=0,(I),dp;", "parts(N1,1); parts(N2,2);", "RESULT x_column_nonzero"):
        if fragment not in script:
            raise AssertionError(fragment)


def _set(name: str, key: str, value: object) -> Callable[[dict[str, Any]], None]:
    def mutate(record: dict[str, Any]) -> None:
        _matrix(record, name)[key] = value

    return mutate


def _zero_limit_column(record: dict[str, Any]) -> None:
    for row in _matrix(record, "w8-nm-series-point1")["entries"]:
        row[-1] = {"re": "0", "im": "0"}


def _drop_a_row(record: dict[str, Any]) -> None:
    _matrix(record, "w8-np-linear-point2")["entries"].pop()


MUTATIONS: dict[str, tuple[Callable[[dict[str, Any]], None], str]] = {
    "limit column zero": (_zero_limit_column, "the rank of the entries is 5"),
    "claimed rank 5": (_set("w8-np-series-point2", "claimed_rank", 5), "claimed rank differs"),
    "a row dropped": (_drop_a_row, "shape"),
    "seven columns": (_set("w8-nm-linear-point1", "columns", 7), "shape"),
    "point changed": (_set("w8-nm-linear-point2", "point", {"C": 1}), "parameter point"),
    "columns renamed": (_set("w8-np-series-point1", "columns_meaning", ["F"]), "column meaning"),
    "ledger row changed": (_set("w8-nm-series-point2", "ledger_row", "A5-435"), "ledger row"),
    "a matrix removed": (lambda record: record["matrices"].pop(), "eight cases"),
    "pass flag cleared": (lambda record: record.update({"pass": False}), "pass flag"),
    "schema changed": (lambda record: record.update(schema="gororoba.a5.w8-component-arc-matrices-qi/0"), "schema"),
    "field changed": (lambda record: record.update(field="Q"), "field"),
}


@pytest.mark.parametrize("name", sorted(MUTATIONS))
def test_the_checker_rejects_each_mutation_of_the_retained_record(name: str) -> None:
    mutate, fragment = MUTATIONS[name]
    record = copy.deepcopy(_record())
    mutate(record)
    found = matrices.problems(record)
    if not any(fragment in problem for problem in found):
        raise AssertionError((name, found))


def test_the_comparison_with_the_arc_record_rejects_another_order_rank_or_limit() -> None:
    record = copy.deepcopy(_record())
    _matrix(record, "w8-nm-linear-point1")["order_of_G"] = 3
    _matrix(record, "w8-np-series-point1")["claimed_rank"] = 5
    limit = _matrix(record, "w8-nm-series-point2")["entries"]
    row = next(index for index, entries in enumerate(limit) if entries[-1] != {"re": "0", "im": "0"})
    limit[row][-1] = {"re": "0", "im": "0"}
    found = matrices.arc_record_problems(record)
    for fragment in ("order of G differs", "rank differs", "nonzero limit coordinates"):
        if not any(fragment in problem for problem in found):
            raise AssertionError((fragment, found))


def test_the_retained_record_binds_the_current_input_digests() -> None:
    record = _record()
    _same(sorted(record["inputs"]), sorted(matrices.INPUTS))
    for name in matrices.INPUTS:
        _same(record["inputs"][name], hashlib.sha256((TRANSFER / name).read_bytes()).hexdigest())
    _same(record["arc_record_sha256"], hashlib.sha256(matrices.arcs.RECORD.read_bytes()).hexdigest())
