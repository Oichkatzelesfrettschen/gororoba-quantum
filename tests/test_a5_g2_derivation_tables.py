"""The 14 G_2 derivations of the sedenions as Gaussian-integer tables on the basis units, with the Leibniz rule."""

from __future__ import annotations

import copy
import hashlib
import json
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
ATTACH = ROOT / "docs" / "evidence" / "a5-kernel-attachments"
sys.path.insert(0, str(ATTACH))

import g2_derivation_tables as tables  # noqa: E402


def _same(found: object, expected: object) -> None:
    if found != expected:
        raise AssertionError((found, expected))


def _record() -> dict[str, Any]:
    record: dict[str, Any] = json.loads(tables.RECORD.read_text(encoding="utf-8"))
    return record


def test_the_retained_record_passes_and_equals_the_regenerated_tables() -> None:
    record = _record()
    _same(tables.problems(record), [])
    _same(record["pass"], True)
    _same(tables.tables_of(record), tables.regenerated())
    _same(tables.record_text(record), tables.RECORD.read_text(encoding="utf-8"))


def test_every_table_satisfies_the_leibniz_rule_is_skew_and_kills_e0() -> None:
    found = tables.tables_of(_record())
    _same(len(found), 14)
    for table in found:
        _same(tables.leibniz_failures(table), 0)
        _same(tables.is_skew(table), True)
        _same(table[0], [(0, 0)] * 16)
        _same(sum(entry != (0, 0) for image in table for entry in image), 8)
    _same(tables.span_rank(found), 14)


def test_the_split_coordinate_matrices_are_not_derivations_of_the_cd_core_product() -> None:
    """Without the phase map eleven of the 14 matrices break the Leibniz rule; the three that pass are real."""
    equivariance = tables.equivariance
    failures = [
        tables.leibniz_failures(tables.table_of(equivariance.split_matrix_of_derivation(derivation)))
        for derivation in equivariance.regularity.DERS
    ]
    _same(sorted(set(failures)), [0, 96])
    _same(failures.count(96), 11)
    real = [derivation["real"] for derivation in _record()["derivations"]]
    _same((real.count(True), real.count(False)), (6, 8))
    _same([count == 0 for count in failures], [flag and count == 0 for flag, count in zip(real, failures, strict=True)])


def test_the_identity_map_fails_the_leibniz_rule() -> None:
    identity = [[(int(row == column), 0) for row in range(16)] for column in range(16)]
    if tables.leibniz_failures(identity) == 0:
        raise AssertionError("the identity passes as a derivation")


def _entry(number: int, image: int, coordinate: int, value: list[Any]) -> Callable[[dict[str, Any]], None]:
    def mutate(record: dict[str, Any]) -> None:
        record["derivations"][number]["images"][image][coordinate] = value

    return mutate


def _first_nonzero(record: dict[str, Any], number: int) -> tuple[int, int]:
    images = record["derivations"][number]["images"]
    return next((k, j) for k, image in enumerate(images) for j, entry in enumerate(image) if entry != [0, 0])


def _negate_one_entry(record: dict[str, Any]) -> None:
    image, coordinate = _first_nonzero(record, 3)
    real, imaginary = record["derivations"][3]["images"][image][coordinate]
    record["derivations"][3]["images"][image][coordinate] = [-real, -imaginary]


def _repeat_a_derivation(record: dict[str, Any]) -> None:
    record["derivations"][5]["images"] = copy.deepcopy(record["derivations"][4]["images"])
    record["derivations"][5]["nonzero_entries"] = record["derivations"][4]["nonzero_entries"]


MUTATIONS: dict[str, tuple[Callable[[dict[str, Any]], None], str]] = {
    "one entry negated": (_negate_one_entry, "Leibniz rule fails"),
    "an image of e_0": (_entry(0, 0, 5, [1, 0]), "e_0 enters"),
    "a real flag flipped": (
        lambda record: record["derivations"][0].update(real=not record["derivations"][0]["real"]),
        "real flag differs",
    ),
    "a fractional coefficient": (_entry(0, 0, 0, [0.5, 0]), "not a pair of integers"),
    "a boolean coefficient": (_entry(2, 1, 1, [True, 0]), "not a pair of integers"),
    "an e_0 coordinate": (_entry(7, 9, 0, [0, 1]), "e_0 enters"),
    "a derivation repeated": (_repeat_a_derivation, "rank 13"),
    "a derivation removed": (lambda record: record["derivations"].pop(), "14 in order"),
    "an image removed": (lambda record: record["derivations"][2]["images"].pop(), "not 16 by 16"),
    "nonzero count changed": (lambda record: record["derivations"][1].update(nonzero_entries=7), "nonzero entries"),
    "convention changed": (lambda record: record.update(convention="rows"), "convention"),
    "ring changed": (lambda record: record.update(ring="Z"), "ring"),
    "pass flag cleared": (lambda record: record.update({"pass": False}), "pass flag"),
    "schema changed": (lambda record: record.update(schema="gororoba.a5.g2-derivation-tables/0"), "schema"),
}


@pytest.mark.parametrize("name", sorted(MUTATIONS))
def test_the_checker_rejects_each_mutation_of_the_retained_record(name: str) -> None:
    mutate, fragment = MUTATIONS[name]
    record = copy.deepcopy(_record())
    mutate(record)
    found = tables.problems(record)
    if not any(fragment in problem for problem in found):
        raise AssertionError((name, found))


@pytest.mark.audit
def test_the_retained_record_binds_the_current_input_digests() -> None:
    record = _record()
    _same(sorted(record["inputs"]), sorted(tables.INPUTS))
    for name in tables.INPUTS:
        _same(record["inputs"][name], hashlib.sha256((ROOT / name).read_bytes()).hexdigest())
