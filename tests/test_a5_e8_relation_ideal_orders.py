"""Three weighted order functions on the E8-bar slice germ over Q(i) and the record that binds their limit ideals."""

from __future__ import annotations

import copy
import hashlib
import json
import re
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
ATTACH = ROOT / "docs" / "evidence" / "a5-kernel-attachments"
sys.path.insert(0, str(ATTACH))

import e8_relation_ideal_orders as orders  # noqa: E402


def _same(found: object, expected: object) -> None:
    if found != expected:
        raise AssertionError((found, expected))


def _record() -> dict[str, Any]:
    record: dict[str, Any] = json.loads(orders.RECORD.read_text(encoding="utf-8"))
    return record


def test_the_retained_record_passes_and_agrees_with_the_weight_slice_record() -> None:
    record = _record()
    _same(orders.problems(record), [])
    _same(orders.slice_problems(record), [])
    _same(record["pass"], True)
    _same([cell["orbit"] for cell in record["cells"]], ["N-", "N+"])


def test_every_nilpotent_form_has_order_strictly_between_the_two_bounds() -> None:
    """Under (2, 2, 1, 2, 1) the ideal has order 4, the maximal ideal order 2, and the five forms order 5."""
    for cell in _record()["cells"]:
        embedded = cell["order_functions"]["embedded"]
        _same(embedded["nilpotent_orders"], [5, 5, 5, 5, 5])
        _same((embedded["ideal_order"], embedded["maximal_ideal_order"]), (4, 2))
        _same(len(cell["linear_forms"]), 5)


def test_strictly_between_excludes_both_bounds_and_the_empty_list() -> None:
    _same(orders.strictly_between([5, 5], 4, 2), True)
    _same(orders.strictly_between([4], 4, 2), False)
    _same(orders.strictly_between([6], 4, 2), False)
    _same(orders.strictly_between([5, 6], 4, 2), False)
    _same(orders.strictly_between([], 4, 2), False)
    # Integer orders leave no room when the maximal ideal has order 1, the case of the equal-weights control.
    _same(orders.strictly_between([4], 3, 1), False)


def test_each_limit_ideal_has_the_dimension_of_its_target_prime() -> None:
    primes = {"prime5": [5, 11], "prime4": [4, 4], "embedded": [4, 2]}
    for cell in _record()["cells"]:
        for name, target in primes.items():
            function = cell["order_functions"][name]
            _same(function["target"], target)
            _same(function["initial_jacobian_rank"], target[0])
            _same(function["target_nonzero_on_initial_forms"], 0)
            _same(function["other_prime_nonzero_on_initial_forms"] > 0, True)
            _same(function["maximal_ideal_order"] >= 1, True)


def _conjugate(text: str) -> str:
    return re.sub(r"\((-?)i\)", lambda match: "(i)" if match.group(1) else "(-i)", text)


def test_the_map_at_one_basepoint_is_the_conjugate_of_the_other_with_two_pairs_exchanged() -> None:
    minus, plus = orders.PARAMETRIZATION["N-"], orders.PARAMETRIZATION["N+"]
    exchanged = [minus[index] for index in (0, 1, 2, 4, 3, 5, 7, 6, 8)]
    _same(tuple(_conjugate(entry) for entry in exchanged), plus)
    _same(len(minus), 9)
    _same(_conjugate("(i)*pl^2"), "(-i)*pl^2")
    _same(_conjugate("pl*(2*pz+(-i)*(pm^2)/8)"), "pl*(2*pz+(i)*(pm^2)/8)")


def test_the_singular_stage_names_each_order_function_and_both_controls() -> None:
    stage = orders.order_stage("N-")
    for name in (*orders.ORDER_FUNCTIONS, "equal"):
        _same(stage.count(f"RESULT {name}.ideal_order"), 1)
    for name in orders.ORDER_FUNCTIONS:
        _same(stage.count(f"RESULT {name}.initial_jacobian_rank"), 1)
    _same(stage.count("RESULT equal.initial_jacobian_rank"), 0)
    _same(",".join(orders.PARAMETRIZATION["N-"]) in stage, True)
    _same(",".join(orders.PARAMETRIZATION["N+"]) in stage, True)


def _cell(orbit: str, record: dict[str, Any]) -> dict[str, Any]:
    cell: dict[str, Any] = next(cell for cell in record["cells"] if cell["orbit"] == orbit)
    return cell


def _set(orbit: str, key: str, value: object) -> Callable[[dict[str, Any]], None]:
    def mutate(record: dict[str, Any]) -> None:
        _cell(orbit, record)[key] = value

    return mutate


def _set_function(orbit: str, name: str, key: str, value: object) -> Callable[[dict[str, Any]], None]:
    def mutate(record: dict[str, Any]) -> None:
        _cell(orbit, record)["order_functions"][name][key] = value

    return mutate


def _set_control(orbit: str, name: str, key: str, value: object) -> Callable[[dict[str, Any]], None]:
    def mutate(record: dict[str, Any]) -> None:
        _cell(orbit, record)["controls"][name][key] = value

    return mutate


MUTATIONS: dict[str, tuple[Callable[[dict[str, Any]], None], str]] = {
    "a nilpotent form of order nu": (
        _set_function("N-", "embedded", "nilpotent_orders", [5, 5, 4, 5, 5]),
        "embedded nilpotent_orders",
    ),
    "a nilpotent form of order nu + e": (
        _set_function("N+", "embedded", "nilpotent_orders", [5, 5, 5, 6, 5]),
        "embedded nilpotent_orders",
    ),
    "a nilpotent order missing": (
        _set_function("N-", "embedded", "nilpotent_orders", [5, 5, 5, 5]),
        "embedded nilpotent_orders",
    ),
    "five copies of one form": (_set("N-", "linear_forms", ["y(1)"] * 5), "differ from the five"),
    "a nilpotent form replaced": (
        _set("N+", "linear_forms", ["2*y(12)+(-i)*y(13)+(-i)*y(17)", "y(7)", "y(8)", "y(5)", "y(3)"]),
        "differ from the five",
    ),
    "maximal ideal of order 1": (
        _set_function("N-", "embedded", "maximal_ideal_order", 1),
        "embedded maximal_ideal_order",
    ),
    "embedded prime nonzero on the initial forms": (
        _set_function("N+", "embedded", "target_nonzero_on_initial_forms", 1),
        "embedded target prime",
    ),
    "limit family of dimension 3": (
        _set_function("N-", "embedded", "initial_jacobian_rank", 3),
        "embedded initial_jacobian_rank",
    ),
    "degree-11 prime nonzero on the initial forms": (
        _set_function("N-", "prime5", "target_nonzero_on_initial_forms", 2),
        "prime5 target prime",
    ),
    "degree-4 limit family of dimension 3": (
        _set_function("N+", "prime4", "initial_jacobian_rank", 3),
        "prime4 initial_jacobian_rank",
    ),
    "substitution blind to the primes": (
        _set_function("N-", "prime4", "other_prime_nonzero_on_initial_forms", 0),
        "prime4 other prime",
    ),
    "weights changed": (_set_function("N-", "prime5", "weights", [1, 1, 1, 1, 1]), "prime5 weights"),
    "generator orders above the ideal order": (
        _set_function("N+", "prime4", "generator_orders", [3] * 21),
        "prime4 generator orders",
    ),
    "germ ideal nonzero on the map": (_set("N-", "germ_nonzero_on_parametrization", 3), "germ_nonzero"),
    "map of the other basepoint recorded": (
        lambda record: record["cells"][1].update(parametrization=record["cells"][0]["parametrization"]),
        "parametrization differs",
    ),
    "embedded prime of degree 4": (_set("N+", "annihilator", [4, 4]), "annihilator differs"),
    "annihilator not prime": (_set("N-", "annihilator_is_prime", False), "annihilator_is_prime"),
    "third minimal prime": (_set("N-", "minimal_primes", [[4, 2], [4, 4], [5, 11]]), "minimal_primes"),
    "equal weights separate the forms": (
        _set_control("N-", "equal_weights", "maximal_ideal_order", 2),
        "equal-weights control separates",
    ),
    "other map satisfies the germ ideal": (
        _set_control("N+", "other_basepoint_parametrization", "germ_nonzero", 0),
        "other basepoint satisfies",
    ),
    "an order function removed": (
        lambda record: record["cells"][0]["order_functions"].pop("prime4"),
        "not the three",
    ),
    "a cell removed": (lambda record: record["cells"].pop(), "N- and N+"),
    "pass flag cleared": (lambda record: record.update({"pass": False}), "pass flag"),
    "schema changed": (lambda record: record.update(schema="gororoba.a5.e8-relation-ideal-orders/0"), "schema"),
    "field changed": (lambda record: record.update(field="Q"), "field"),
}


@pytest.mark.parametrize("name", sorted(MUTATIONS))
def test_the_checker_rejects_each_mutation_of_the_retained_record(name: str) -> None:
    mutate, fragment = MUTATIONS[name]
    record = copy.deepcopy(_record())
    mutate(record)
    found = orders.problems(record)
    if not any(fragment in problem for problem in found):
        raise AssertionError((name, found))


def test_the_slice_comparison_rejects_other_relations() -> None:
    record = copy.deepcopy(_record())
    record["cells"][0]["relations_sha256"] = "0" * 64
    _same(orders.slice_problems(record), ["N-: the relations differ from those of the weight-slice record"])


def test_the_retained_record_binds_the_current_input_digests() -> None:
    record = _record()
    _same(sorted(record["inputs"]), sorted(orders.INPUTS))
    for name in orders.INPUTS:
        _same(record["inputs"][name], hashlib.sha256((ATTACH / name).read_bytes()).hexdigest())
    _same(record["weight_slice_record_sha256"], hashlib.sha256(orders.WEIGHT_SLICE.read_bytes()).hexdigest())
