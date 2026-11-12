"""The Q(i) monomial certificate: every asserted invariant decides the verdict, on a constructed row and on the
retained record."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
CHAR0 = ROOT / "docs/evidence/a5-char0-transfer"
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(CHAR0))

import monomial_certificate_qi as cert  # noqa: E402


def _check(condition: bool) -> None:
    if not condition:
        raise AssertionError


def _row() -> dict[str, Any]:
    """A row whose every invariant meets EXPECTED, with one agreeing reduction."""
    row: dict[str, Any] = copy.deepcopy(cert.EXPECTED)
    count = row["l_generators"]
    row["i_equals_m"] = True
    row["reductions"] = [{"l_in_k2": True, "k2_in_l": True, "nonzero_generators": count}]
    return row


def test_a_row_meeting_every_invariant_is_certified() -> None:
    row = _row()
    _check(cert.invariant_failures(row) == {})
    _check(cert.verdict(row) == "certified")


def test_a_wrong_multiplicity_is_reported_and_fails_the_verdict() -> None:
    row = _row()
    row["l_mult"] = 11
    _check(cert.invariant_failures(row) == {"l_mult": {"expected": 12, "observed": 11}})
    _check(cert.verdict(row) == "failed")


def test_each_invariant_alone_fails_the_verdict() -> None:
    wrong: dict[str, Any] = {
        "l_generators": 68,
        "l_degrees": [2, 3],
        "l_dim": 3,
        "l_mult": 11,
        "l_hilbert_numerator": "1,11,-3,4,-1,1",
        "l_saturated": False,
        "y1_y5_y6_outside_l": 2,
        "y1_y5_y6_squared_in_l": False,
    }
    _check(set(wrong) == set(cert.EXPECTED))
    for key, value in wrong.items():
        row = _row()
        row[key] = value
        _check(set(cert.invariant_failures(row)) == {key})
        _check(cert.verdict(row) == "failed")


def test_a_failed_reduction_or_a_failed_nakayama_check_fails_the_verdict() -> None:
    row = _row()
    row["reductions"][0]["k2_in_l"] = False
    _check(cert.verdict(row) == "failed")
    row = _row()
    row["i_equals_m"] = False
    _check(cert.verdict(row) == "failed")


@pytest.mark.audit
def test_the_retained_record_has_no_failure_and_a_wrong_invariant_flips_it() -> None:
    record = json.loads((CHAR0 / "monomial-certificate-qi.json").read_text(encoding="utf-8"))
    _check(len(record["cases"]) == 2)
    for row in record["cases"]:
        _check(cert.invariant_failures(row) == row["invariant_failures"] == {})
        _check(cert.verdict(row) == row["verdict"] == "certified")
        broken = dict(row, l_mult=11)
        _check(set(cert.invariant_failures(broken)) == {"l_mult"})
        _check(cert.verdict(broken) == "failed")


def test_the_record_comparison_drops_run_measurements_and_keeps_every_polynomial() -> None:
    row = dict(_row(), wall_seconds=4.1, peak_rss_kib=107568, l_polynomials=["y1*y2", "y3^2"])
    row["reductions"][0]["wall_seconds"] = 0.3
    other = copy.deepcopy(row)
    other["wall_seconds"], other["peak_rss_kib"] = 9.9, 1
    other["reductions"][0]["wall_seconds"] = 7.0
    _check(cert.algebraic({"cases": [row]}) == cert.algebraic({"cases": [other]}))
    other["l_polynomials"][0] = "1"
    _check(cert.algebraic({"cases": [row]}) != cert.algebraic({"cases": [other]}))
