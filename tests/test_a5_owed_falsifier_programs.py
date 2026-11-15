"""Bounded checks of the programs behind A5-024, A5-548, A5-559 and A5-560, on fixtures built here.

No Singular runs: each test feeds a program's pure verdict function a fixture assembled from that program's tables
and the constants of quadric_and_germ_probes.py, and every mutation of a deciding field must be reported. The
retained records replay on demand by running the programs themselves (their READMEs give the commands).
"""

import copy
import importlib.util
import sys
from math import comb
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

A5 = Path(__file__).resolve().parents[1] / "docs/evidence/a5-exceptional-fibers"


def load(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(name)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def _same(found: object, expected: object) -> None:
    if found != expected:
        raise AssertionError((found, expected))


def _reported(problems: list[str], mutation: object) -> None:
    if not problems:
        raise AssertionError(f"the mutation {mutation} passed")


rio = load("a5_relation_ideal_orders", A5 / "arcs/relation_ideal_orders.py")
qr = load("a5_third_prime_quadric_rings", A5 / "third-prime/quadric_rings.py")
qi = load("a5_npm_map_qi", A5 / "structure/sign-symmetry/npm_map_qi.py")


def radical_numerator() -> list[int]:
    """N_R = N_K - N_A + (1 - t)^21, the numerator the Hilbert identity of A5-547 fixes."""
    width = max(len(rio.qp.NUM_K_E8), len(rio.qp.NUM_A_E8), 22)
    k = rio.qp.NUM_K_E8 + [0] * (width - len(rio.qp.NUM_K_E8))
    a = rio.qp.NUM_A_E8 + [0] * (width - len(rio.qp.NUM_A_E8))
    unit = [(-1) ** i * comb(21, i) if i <= 21 else 0 for i in range(width)]
    out = [k[i] - a[i] + unit[i] for i in range(width)]
    while out and out[-1] == 0:
        out.pop()
    return out


def passing_rows() -> list[dict[str, Any]]:
    rows = []
    nil = [{"form": f"y({j})", "vanishes_on_limit": True, "next_coefficient_nonzero": True} for j in (14, 12, 7, 6, 4)]
    for t in rio.TARGETS:
        rows.append({"target": t, "family": "scroll", "mode": "plain", "x0_zero": True, "P2NONVAN": 0, "RANK5": 4,
                     "JNONVAN": 0})  # fmt: skip
        rows.append({"target": t, "family": "top", "mode": "plain", "x0_zero": True, "P1NONVAN": 0, "RANK5": 5,
                     "JNONVAN": 0})  # fmt: skip
        rows.append({
            "target": t, "family": "embedded", "mode": "structure", "x0_zero": True, "ANONVAN": 0, "RANK5": 4,
            "JNONVAN": 0, "annihilator": [4, 2], "radical_is_P1_meet_P2": True, "nu": 4, "EMIN": 2,
            "primary": [[5, 11, 11, 1, 0, 0], [4, 4, 4, 0, 1, 0], [4, 2, 4, 0, 0, 1]], "decomposition_complete": True,
            "nilpotent_count": 5, "nilpotent": copy.deepcopy(nil), "numK": list(rio.qp.NUM_K_E8),
            "numR": radical_numerator(), "numA": list(rio.qp.NUM_A_E8),
        })  # fmt: skip
        rows.append({"target": t, "family": "scroll", "mode": "control", "ANONVAN": 5, "JCORRUPT": 2, "JNONVAN": 0})
    return rows


def test_the_built_record_passes() -> None:
    _same(rio.problems(passing_rows()), [])


MUTATIONS = [
    ("embedded", "structure", "ANONVAN", 1),
    ("embedded", "structure", "RANK5", 3),
    ("embedded", "structure", "EMIN", 1),
    ("embedded", "structure", "decomposition_complete", False),
    ("embedded", "structure", "annihilator", [4, 4]),
    ("embedded", "structure", "primary", [[5, 11, 11, 1, 0, 0], [4, 4, 4, 0, 1, 0]]),
    ("embedded", "structure", "numA", [1]),
    ("top", "plain", "P1NONVAN", 2),
    ("scroll", "plain", "P2NONVAN", 2),
    ("scroll", "plain", "RANK5", 3),
    ("scroll", "plain", "JNONVAN", 1),
    ("scroll", "control", "ANONVAN", 0),
    ("scroll", "control", "JCORRUPT", 0),
]


@pytest.mark.parametrize(("family", "mode", "field", "value"), MUTATIONS)
def test_each_mutation_is_reported(family: str, mode: str, field: str, value: Any) -> None:
    rows = passing_rows()
    target = next(iter(rio.TARGETS))
    row = next(r for r in rows if (r["target"], r["family"], r["mode"]) == (target, family, mode))
    row[field] = value
    _reported(rio.problems(rows), (family, mode, field))


def test_a_nilpotent_form_at_order_nu_plus_e_is_reported() -> None:
    rows = passing_rows()
    target = next(iter(rio.TARGETS))
    row = next(r for r in rows if (r["target"], r["family"], r["mode"]) == (target, "embedded", "structure"))
    row["nilpotent"][2]["next_coefficient_nonzero"] = False
    _reported(rio.problems(rows), "nilpotent order")


P = 32057


def test_squarefree_characteristic_polynomial_decides_reducedness() -> None:
    diagonal = {1: [2, 0, 0], 2: [0, 5, 0], 3: [0, 0, 11]}
    repeated = {1: [3, 0, 0], 2: [0, 3, 0], 3: [0, 0, 7]}
    nilpotent = {1: [0, 1, 0], 2: [0, 0, 1], 3: [0, 0, 0]}
    _same(qr.squarefree_charpoly(diagonal, P), True)
    _same(qr.squarefree_charpoly(repeated, P), False)
    _same(qr.squarefree_charpoly(nilpotent, P), False)


def test_the_verdict_needs_cohen_macaulay_for_reduced_and_a_certificate_for_nonreduced() -> None:
    chart = {"chart": [0, 23, 23], "squarefree_charpoly_bases": [7]}
    _same(qr.verdict({"cohen_macaulay": True}, chart)["reduced"], True)
    _same(qr.verdict({"cohen_macaulay": False}, chart)["reduced"], None)
    nil = {**chart, "nilpotent": [3, 1, 1]}
    _same(qr.verdict({"cohen_macaulay": False}, nil)["hypothesis_holds"], True)
    _same(qr.verdict({"cohen_macaulay": True}, nil)["hypothesis_holds"], False)
    short = {"chart": [0, 22, 23], "squarefree_charpoly_bases": [7]}
    _same(qr.verdict({"cohen_macaulay": True}, short)["reduced"], None)
    none_squarefree = {"chart": [0, 23, 23], "squarefree_charpoly_bases": []}
    _same(qr.verdict({"cohen_macaulay": True}, none_squarefree)["reduced"], None)


def test_gaussian_rationals_parse_and_multiply() -> None:
    _same(qi.gauss("(2*I+1)/3"), qi.Gauss(qi.Fraction(1, 3), qi.Fraction(2, 3)))
    _same(qi.gauss("(-I)") * qi.gauss("I"), qi.Gauss(1))
    _same(qi.gauss("I^2"), qi.Gauss(-1))
    with pytest.raises(ValueError):
        qi.gauss("__import__('os')")


def test_the_identity_is_a_signed_bijection_and_rejects_a_bent_coefficient() -> None:
    one, minus = qi.Gauss(1), qi.Gauss(-1)
    t8 = (0,) * 7 + (1, 0)
    t9 = (0,) * 8 + (1,)
    t1 = (1,) + (0,) * 8
    plus = [{t8: one, t1: one}, {t9: one}]
    moved = [{t9: minus}, {t8: minus, t1: one}]
    hit = qi.identity(plus, moved, qi.SIGMA)
    _same(hit["bijection_by_units"], True)
    _same(hit["map"], [[2, "1"], [1, "1"]])
    bent = [{t8: qi.Gauss(2), t1: one}, {t9: one}]
    _same(qi.identity(bent, moved, qi.SIGMA)["bijection_by_units"], False)


def passing_quadric_record() -> dict[str, Any]:
    return {"defect_problems": [], "undecided_cells": [], "hypothesis_holds_on_every_decided_cell": True}


def test_a_passing_quadric_record_exits_zero() -> None:
    _same(qr.exit_status(passing_quadric_record()), 0)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("defect_problems", ["e8-colon: colon ideal differs"]),
        ("undecided_cells", ["W8 -> N-"]),
        ("hypothesis_holds_on_every_decided_cell", False),
    ],
)
def test_a_falsified_or_undecided_quadric_record_exits_one(field: str, value: Any) -> None:
    record = passing_quadric_record()
    record[field] = value
    _same(qr.exit_status(record), 1)


def test_a_radical_ideal_that_is_not_cohen_macaulay_falsifies_the_hypothesis() -> None:
    cm_row = {"cohen_macaulay": False}
    red = {"chart": [0, 15, 12], "squarefree_charpoly_bases": [7], "nilpotent": [0, 1, 1], "radical_equal": [1]}
    found = qr.verdict(cm_row, red)
    _same((found["reduced"], found["hypothesis_holds"]), (True, False))
