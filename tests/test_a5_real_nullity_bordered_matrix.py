"""The bordered-matrix constructors, the left matrices, the transport and the record rules."""

from __future__ import annotations

import copy
import json
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "docs" / "evidence" / "a5-kernel-bundles-residuals"))

import real_nullity_bordered_matrix as module  # noqa: E402

Mutation = tuple[str, Callable[[dict[str, Any]], Any]]

MUTATIONS: list[Mutation] = [
    ("constructors", lambda record: record["identities"].__setitem__("constructors", False)),
    ("left matrices", lambda record: record["identities"].__setitem__("left_matrices", False)),
    ("transport", lambda record: record["identities"]["transport"].__setitem__(1, 29)),
    ("true as one", lambda record: record["identities"].__setitem__("constructors", 1)),
    ("digest", lambda record: record["inputs"].__setitem__(next(iter(record["inputs"])), "0" * 64)),
    ("pass", lambda record: record.__setitem__("pass", False)),
]


def _same(found: object, expected: object) -> None:
    if found != expected:
        raise AssertionError((found, expected))


def test_the_two_constructors_agree() -> None:
    _same(module.constructors_agree(), True)


def test_a_changed_sign_separates_the_constructors(monkeypatch: pytest.MonkeyPatch) -> None:
    signs = [list(row) for row in module.germs.SIGNS16]
    signs[3][5] = -signs[3][5]
    monkeypatch.setattr(module.germs, "SIGNS16", signs)
    _same(module.constructors_agree(), False)


@pytest.mark.parametrize("index", [0, 1, 16, 31])
def test_the_left_matrices_agree_at_a_basis_element(index: int) -> None:
    _same(module.left_matrix_agrees(index), True)


def test_record_rules_accept_the_pinned_record(monkeypatch: pytest.MonkeyPatch) -> None:
    _same(module.verdict(module.expected_record()), [])
    retained = json.loads(module.RECORD.read_text(encoding="utf-8"))
    retained_inputs = dict(retained["inputs"])
    monkeypatch.setattr(module, "_inputs", lambda: dict(retained_inputs))
    _same(module.verdict(retained), [])
    _same(module.RECORD.read_text(encoding="utf-8"), module._serialized(module.expected_record()))


@pytest.mark.parametrize("mutation", MUTATIONS, ids=[name for name, _ in MUTATIONS])
def test_record_rules_reject_a_mutated_record(mutation: Mutation) -> None:
    record = copy.deepcopy(module.expected_record())
    mutation[1](record)
    _same(module.verdict(record) != [], True)


@pytest.mark.audit
def test_the_record_replays() -> None:
    _same(module.verdict(module.compute()), [])
