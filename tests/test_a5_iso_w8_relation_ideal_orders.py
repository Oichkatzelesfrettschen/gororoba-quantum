"""Weighted order functions on the Iso and W8 slice germs over Q(i) whose limit ideals are the minimal primes."""

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

import iso_w8_relation_ideal_orders as orders  # noqa: E402


def _same(found: object, expected: object) -> None:
    if found != expected:
        raise AssertionError((found, expected))


def _record() -> dict[str, Any]:
    record: dict[str, Any] = json.loads(orders.RECORD.read_text(encoding="utf-8"))
    return record


def _cell(record: dict[str, Any], orbit: str, source: str) -> dict[str, Any]:
    cell: dict[str, Any] = next(c for c in record["cells"] if (c["orbit"], c["source"]) == (orbit, source))
    return cell


def test_the_retained_record_passes_and_agrees_with_the_weight_slice_record() -> None:
    record = _record()
    _same(orders.problems(record), [])
    _same(orders.slice_problems(record), [])
    _same(record["pass"], True)
    _same([(cell["orbit"], cell["source"]) for cell in record["cells"]], list(orders.CELLS))


def test_each_limit_family_has_the_dimension_of_its_prime_and_positive_order_on_the_slice() -> None:
    for cell in _record()["cells"]:
        for name, function in cell["order_functions"].items():
            _same(function["initial_jacobian_rank"], function["target"][0])
            _same(function["target_nonzero_on_initial_forms"], 0)
            _same(function["maximal_ideal_order"] >= 1, True)
            if cell["source"] == "w8":
                _same(function["other_prime_nonzero_on_initial_forms"] > 0, True)
            else:
                _same(name, "prime23")


def test_the_degrees_of_the_w8_primes_sum_to_the_degree_of_the_quadric_ideal() -> None:
    primes = orders.PRIMES["w8"]
    _same(primes["P20"][1] + primes["P30"][1], orders.EXPECTED["w8"]["ideal"][1])
    _same({prime[0] for prime in primes.values()}, {orders.EXPECTED["w8"]["ideal"][0]})


def test_the_map_at_n_plus_exchanges_two_pairs_of_slice_coordinates() -> None:
    for source in ("iso", "w8"):
        minus, plus = orders.parametrization("N-", source), orders.parametrization("N+", source)
        _same((plus[3], plus[4], plus[6], plus[7]), (minus[4], minus[3], minus[7], minus[6]))
        _same([plus[index] for index in (0, 1, 2, 5, 8)], [minus[index] for index in (0, 1, 2, 5, 8)])
        _same(len(minus), 9)
    with pytest.raises(ValueError):
        orders.parametrization("N", "iso")


def test_the_second_slice_coordinate_carries_the_twist_and_the_weights_fit_the_parameters() -> None:
    for source in ("iso", "w8"):
        _same(orders.PARAMETRIZATION_MINUS[source][1], "qx*qb/2-qt")
        for weights, _, _ in orders.ORDER_FUNCTIONS[source].values():
            _same(len(weights), len(orders.PARAMETERS[source]))
        _same(len(orders.DEFICIENT_WEIGHTS[source]), len(orders.PARAMETERS[source]))


def test_the_singular_stage_names_each_order_function_and_the_control() -> None:
    for source in ("iso", "w8"):
        stage = orders.order_stage("N-", source)
        for name in (*orders.ORDER_FUNCTIONS[source], "deficient"):
            _same(stage.count(f"RESULT {name}.initial_jacobian_rank"), 1)
        _same(stage.count("RESULT deficient.target_nonzero_on_initial_forms"), 0)
        _same(",".join(orders.parametrization("N+", source)) in stage, True)


def _set(orbit: str, source: str, key: str, value: object) -> Callable[[dict[str, Any]], None]:
    def mutate(record: dict[str, Any]) -> None:
        _cell(record, orbit, source)[key] = value

    return mutate


def _function(orbit: str, source: str, name: str, key: str, value: object) -> Callable[[dict[str, Any]], None]:
    def mutate(record: dict[str, Any]) -> None:
        _cell(record, orbit, source)["order_functions"][name][key] = value

    return mutate


def _control(orbit: str, source: str, name: str, key: str, value: object) -> Callable[[dict[str, Any]], None]:
    def mutate(record: dict[str, Any]) -> None:
        _cell(record, orbit, source)["controls"][name][key] = value

    return mutate


MUTATIONS: dict[str, tuple[Callable[[dict[str, Any]], None], str]] = {
    "iso family of dimension 4": (
        _function("N-", "iso", "prime23", "initial_jacobian_rank", 4),
        "prime23 initial_jacobian_rank",
    ),
    "iso prime nonzero on the initial forms": (
        _function("N+", "iso", "prime23", "target_nonzero_on_initial_forms", 1),
        "prime23 target prime",
    ),
    "w8 family of dimension 5": (
        _function("N-", "w8", "prime30", "initial_jacobian_rank", 5),
        "prime30 initial_jacobian_rank",
    ),
    "w8 prime nonzero on the initial forms": (
        _function("N+", "w8", "prime20", "target_nonzero_on_initial_forms", 3),
        "prime20 target prime",
    ),
    "w8 families in one prime": (
        _function("N-", "w8", "prime20", "other_prime_nonzero_on_initial_forms", 0),
        "prime20 other prime",
    ),
    "slice coordinate of order zero": (
        _function("N-", "iso", "prime23", "maximal_ideal_order", 0),
        "prime23 maximal_ideal_order",
    ),
    "weights changed": (_function("N+", "w8", "prime30", "weights", [1, 1, 0, 0, 0, 1]), "prime30 weights"),
    "generator orders above the ideal order": (
        _function("N-", "w8", "prime20", "generator_orders", [3] * 24),
        "prime20 generator orders",
    ),
    "germ ideal nonzero on the map": (_set("N-", "iso", "germ_nonzero_on_parametrization", 1), "germ_nonzero"),
    "map of the other basepoint recorded": (
        lambda record: _cell(record, "N+", "w8").update(parametrization=_cell(record, "N-", "w8")["parametrization"]),
        "parametrization differs",
    ),
    "quadric ideal not radical": (_set("N+", "w8", "radical", False), "radical differs"),
    "iso with two minimal primes": (_set("N-", "iso", "minimal_primes", [[5, 11], [5, 12]]), "minimal_primes"),
    "deficient control reaches the dimension": (
        _control("N-", "iso", "deficient_weights", "initial_jacobian_rank", 5),
        "reaches the dimension",
    ),
    "other map satisfies the germ ideal": (
        _control("N+", "iso", "other_basepoint_parametrization", "germ_nonzero", 0),
        "other basepoint satisfies",
    ),
    "an order function removed": (
        lambda record: _cell(record, "N-", "w8")["order_functions"].pop("prime30"),
        "not those of the producer",
    ),
    "a cell removed": (lambda record: record["cells"].pop(), "four cells"),
    "pass flag cleared": (lambda record: record.update({"pass": False}), "pass flag"),
    "schema changed": (lambda record: record.update(schema="gororoba.a5.iso-w8-relation-ideal-orders/0"), "schema"),
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
    _same(orders.slice_problems(record), ["iso N-: the relations differ from those of the weight-slice record"])


@pytest.mark.audit
def test_the_retained_record_binds_the_current_input_digests() -> None:
    record = _record()
    _same(sorted(record["inputs"]), sorted(orders.INPUTS))
    for name in orders.INPUTS:
        _same(record["inputs"][name], hashlib.sha256((ATTACH / name).read_bytes()).hexdigest())
    _same(record["weight_slice_record_sha256"], hashlib.sha256(orders.WEIGHT_SLICE.read_bytes()).hexdigest())
