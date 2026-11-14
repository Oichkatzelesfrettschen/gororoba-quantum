"""Kernel-plane identities: the block, the null slice, derivations, counterexample, fixtures and the record rules."""

from __future__ import annotations

import json
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "docs" / "evidence" / "a5-kernel-bundles-residuals"))

import kernel_plane_identities as identities  # noqa: E402
from kernel_three_plane_zero_divisors import _exact_block, _exact_kernel  # noqa: E402
from nullity4_gauss_image import STRATA, _fixture_splits  # noqa: E402
from sympy import QQ_I, I, Symbol, sympify  # noqa: E402

import cd_core  # noqa: E402

Mutation = tuple[str, Callable[[dict[str, Any]], Any]]


def _same(found: object, expected: object) -> None:
    if found != expected:
        raise AssertionError((found, expected))


def _first_fixture(stratum: str) -> list[Any]:
    return next(identities._frame(split) for _, name, split in _fixture_splits() if name == stratum)


def test_block_is_the_imaginary_part_of_the_product_and_the_bordered_matrix() -> None:
    # M(z) v is the imaginary part of the sedenion product z v, and the block agrees with the bordered matrix of the
    # retained producer at an exact fixture of each stratum.
    first = [3, -1, 4, 1, -5, 9, 2, 6, -5, 3, 5, -8, 9, 7, -9]
    second = [2, 7, -1, 8, 2, -8, 1, 8, 2, -8, 4, 5, -9, 0, 4]
    product = [int(x) for x in cd_core.cd_multiply_exact(16, [0, *first], [0, *second])][1:]
    _same(identities.apply(identities.block(first, 0), second, 0), product)
    for stratum in STRATA:
        frame = _first_fixture(stratum)
        _same(identities.block(frame, QQ_I.zero), _exact_block(frame))


def test_zero_test_over_a_function_field_decides_rational_identities() -> None:
    field = QQ_I.frac_field("x")
    x = field.from_sympy(Symbol("x"))
    unit = field.convert(I)
    _same(bool((x**2 - 1) / (x - 1) - (x + 1)), False)
    _same(bool(x / (x + unit) - x * (x - unit) / (x**2 + 1)), False)
    _same(bool(x / (x + 1) - 1), True)


def test_null_slice_cuts_the_kernel_by_the_first_nonzero_pairing_with_the_point() -> None:
    zero = QQ_I.zero
    # N1(z) != 0 at a fixture of V(G) minus V(Q): the pairing is nonzero somewhere, so the slice has dimension 2.
    frame = _first_fixture(STRATA[1])
    kernel = _exact_kernel(_exact_block(frame))
    _same(len(kernel), 3)
    pairings = [identities.form(0, k, frame, zero) for k in kernel]
    _same(any(pairings), True)
    cut = identities.null_slice(kernel, frame, zero)
    _same(len(cut), 2)
    _same(all(not identities.form(0, k, frame, zero) for k in cut), True)
    # At the counterexample N1(., z) vanishes on K(z), no pivot exists and the slice is K(z).
    point = [QQ_I.from_sympy(sympify(x)) for x in identities.COUNTEREXAMPLE_POINT]
    plane = _exact_kernel(_exact_block(point))
    _same(identities.null_slice(plane, point, zero), plane)


def test_derivations_of_the_octonions_and_the_orbit_ranks() -> None:
    _same(identities.derivation_record(), identities.DERIVATIONS)


def test_counterexample_point_is_recomputed() -> None:
    _same(identities.counterexample_record(), identities.COUNTEREXAMPLE)


def test_fixture_counts_are_recomputed() -> None:
    _same(identities.fixture_record(), identities.FIXTURE_COUNTS)


def test_a_family_with_one_generator_is_recomputed() -> None:
    # FQG, the fastest family: the others take the same path through `family_record` over a field with more generators.
    _same(identities.family_record("FQG"), identities.expected_record()["families"]["FQG"])


def _change(value: Any) -> Any:
    """Another value of the same type, so that a rule that reads the field sees a difference and the shape does not."""
    if isinstance(value, bool):
        return not value
    if isinstance(value, int):
        return value + 1
    if isinstance(value, str):
        return value + "0"
    if isinstance(value, list):
        return [_change(value[0]), *value[1:]]
    raise TypeError(type(value))


def test_retained_record_passes_its_rules_and_each_mutation_fails_them(monkeypatch: pytest.MonkeyPatch) -> None:
    record = json.loads(identities.RECORD.read_text(encoding="utf-8"))
    # The digests of the live source files are compared by the on-demand replay gate; here the rule that compares
    # them is exercised against a fixed copy, so an edit of an input file leaves the required test lane green.
    retained_inputs = dict(record["inputs"])
    monkeypatch.setattr(identities, "_inputs", lambda: dict(retained_inputs))
    _same((record["pass"], identities.verdict(record)), (True, []))
    _same(sorted(record["families"]), sorted(identities.FAMILY_NAMES))

    def family(name: str, field: str) -> Callable[[dict[str, Any]], Any]:
        return lambda r: r["families"][name].update({field: _change(r["families"][name][field])})

    def falsify(name: str, field: str) -> Callable[[dict[str, Any]], Any]:
        return lambda r: r["families"][name].update({field: False})

    def alter(section: str, field: str) -> Callable[[dict[str, Any]], Any]:
        return lambda r: r[section].update({field: _change(r[section][field])})

    def alter_fixture(stratum: str, field: str) -> Callable[[dict[str, Any]], Any]:
        return lambda r: r["fixtures"][stratum].update({field: r["fixtures"][stratum][field] + 1})

    changes: dict[str, Mutation] = {
        "field": ("headed otherwise", lambda r: r.update(field="GF(2)")),
        "schema": ("headed otherwise", lambda r: r.update(schema="other")),
        "one input digest": ("input digests", lambda r: r["inputs"].update({next(iter(r["inputs"])): "0" * 64})),
        "stated failure": ("states that it fails", lambda r: r.update({"pass": False})),
        "any pinned value": (
            "differs from the record the constants determine",
            lambda r: r["counterexample"].update(point=r["counterexample"]["point"][::-1]),
        ),
    }
    for name in identities.FAMILY_NAMES:
        changes[f"{name} generators"] = (f"{name}: the generators differ", family(name, "generators"))
        changes[f"{name} Q"] = (f"{name}: Q differs", family(name, "Q"))
        changes[f"{name} G"] = (f"{name}: G differs", family(name, "G"))
        changes[f"{name} rank"] = (f"{name}: M(z) has another rank", family(name, "rank"))
        for field in identities.FAMILY_STATEMENTS[name]:
            changes[f"{name} {field}"] = (f"{name}: {identities.STATEMENT_RULES[field]}", falsify(name, field))
    for field, message in identities.DERIVATION_RULES.items():
        changes[f"derivations {field}"] = (message, alter("derivations", field))
    for field, message in identities.COUNTEREXAMPLE_RULES.items():
        changes[f"counterexample {field}"] = (message, alter("counterexample", field))
    for stratum in STRATA:
        for field, message in identities.FIXTURE_RULES.items():
            changes[f"{stratum} {field}"] = (f"{stratum}: {message}", alter_fixture(stratum, field))
    # A record with other fields or value types ends the verdict before a rule reads it: True == 1 and 15.0 == 15
    # under ==, and a missing or mistyped field would raise inside a rule.
    shape = "other fields or value types"
    first = STRATA[0]
    shapes: dict[str, Mutation] = {
        "inputs emptied": (shape, lambda r: r.update(inputs={})),
        "pass dropped": (shape, lambda r: r.pop("pass")),
        "added field": (shape, lambda r: r.update(note="")),
        "family dropped": (shape, lambda r: r["families"].pop("FQG")),
        "families as a list": (shape, lambda r: r.update(families=list(r["families"].values()))),
        "integer for a boolean in a family": (shape, lambda r: r["families"]["FQG"].update(product_zero=1)),
        "integer for a boolean at the counterexample": (
            shape,
            lambda r: r["counterexample"].update(point_in_kernel=1),
        ),
        "float for an integer": (shape, lambda r: r["derivations"].update(dimension=14.0)),
        "boolean for a count": (shape, lambda r: r["fixtures"][first].update(product_zero=True)),
        "statement dropped": (shape, lambda r: r["families"]["FQ"].pop("point_in_kernel")),
        "added statement": (shape, lambda r: r["families"]["FQG"].update(point_in_kernel=True)),
        "stratum dropped": (shape, lambda r: r["fixtures"].pop(STRATA[2])),
        "point shortened": (shape, lambda r: r["counterexample"]["point"].pop()),
    }
    for name, (fragment, change) in {**changes, **shapes}.items():
        mutated = json.loads(json.dumps(record))
        change(mutated)
        problems = identities.verdict(mutated)
        if not any(fragment in problem for problem in problems):
            raise AssertionError(f"a record mutated at {name} does not fail on {fragment!r}: {problems}")


def test_replay_comparison_separates_a_boolean_from_an_integer() -> None:
    # True == 1 in Python, so a comparison of parsed records accepts either; the replay compares the retained text.
    _same({"unit": True} == {"unit": 1}, True)
    _same(identities._serialized({"unit": True}) == identities._serialized({"unit": 1}), False)
