"""Nilpotent and idempotent counts of the Cayley-Dickson algebra over F_p on bounded fixtures."""

from __future__ import annotations

import a5_nilpotent_idempotent_counts as record
import pytest


def require(condition: bool) -> None:
    if not condition:
        raise AssertionError


def test_a2_over_f3_counts_match_the_formulas() -> None:
    row = record.run_case(2, 3, False)
    require((row["nil2"], row["nil4"], row["idempotents"]) == (9, 9, 12))
    require((row["identity_failures"], row["predicate_mismatches"]) == (0, 0))


def test_a3_over_f3_counts_match_the_formulas() -> None:
    row = record.run_case(3, 3, False)
    require((row["nil2"], row["idempotents"]) == (729, 756))
    require(row["nil2"] == row["formula_nil2"] and row["idempotents"] == row["formula_idempotents"])


def test_one_negated_sign_breaks_the_identity_and_the_predicate() -> None:
    row = record.run_case(2, 3, True)
    require((row["identity_failures"], row["predicate_mismatches"], row["nil2"]) == (36, 8, 1))


def test_the_complex_numbers_over_f3_lie_outside_the_idempotent_formula() -> None:
    row = record.run_case(1, 3, False)
    require(row["idempotents"] == 0 and row["formula_idempotents"] == 2)


def test_validate_rejects_one_changed_count(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(record, "CASES", ((2, 3),))
    result = {"cases": [record.run_case(2, 3, False)], "controls": [record.run_case(1, 3, False)]}
    record.validate(result)
    result["cases"][0]["nil2"] += 1
    with pytest.raises(RuntimeError, match="nilpotent count"):
        record.validate(result)
