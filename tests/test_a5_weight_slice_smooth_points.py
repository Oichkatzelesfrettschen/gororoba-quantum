"""Smooth rational points on the minimal primes of the Iso, W8 and E8-bar quadric ideals over Q(i)."""

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

import weight_slice_smooth_points as smooth  # noqa: E402


def _same(found: object, expected: object) -> None:
    if found != expected:
        raise AssertionError((found, expected))


def _record() -> dict[str, Any]:
    record: dict[str, Any] = json.loads(smooth.RECORD.read_text(encoding="utf-8"))
    return record


def _cell(record: dict[str, Any], orbit: str, source: str) -> dict[str, Any]:
    cell: dict[str, Any] = next(c for c in record["cells"] if (c["orbit"], c["source"]) == (orbit, source))
    return cell


def test_the_retained_record_passes_and_agrees_with_the_weight_slice_record() -> None:
    record = _record()
    _same(smooth.problems(record), [])
    _same(smooth.slice_problems(record), [])
    _same(record["pass"], True)


def test_every_minimal_prime_holds_a_point_of_full_jacobian_rank_that_lies_on_it_alone() -> None:
    record = _record()
    for orbit, source in smooth.CELLS:
        cell = _cell(record, orbit, source)
        generators = smooth.GENERATORS[source]
        for number, (dimension, _) in enumerate(smooth.PRIMES[source], 1):
            ranks = [point["jacobian_rank"] for point in cell["points"] if point["primes_through"] == [number]]
            if generators - dimension not in ranks:
                raise AssertionError((orbit, source, number, ranks))


def test_the_coordinate_subspaces_are_the_maximal_sets_without_a_relation_monomial() -> None:
    """A path 1-2-3 with a square on 4: the maximal sets avoiding the pairs and the square are {1, 3} and {2}."""
    _same(smooth.coordinate_subspaces(4, {(1, 2), (2, 3), (4, 4)}), [[1, 3], [2]])
    _same(smooth.coordinate_subspaces(3, set()), [[1, 2, 3]])
    _same(smooth.coordinate_subspaces(2, {(1, 1), (2, 2)}), [[]])


def test_a_point_carries_the_first_primes_on_its_support() -> None:
    _same(smooth.point_of([2, 5], 6), [0, 2, 0, 0, 3, 0])
    with pytest.raises(RuntimeError, match="more coordinates"):
        smooth.point_of(list(range(1, 12)), 12)


def test_the_script_evaluates_the_jacobian_and_every_prime_at_each_point() -> None:
    script = smooth.singular_script(["RELATION 1,2:1 3,3:(i)"], 3, [[0, 0, 0], [2, 0, 0]])
    for fragment in ("ideal K=(1)*y(1)*y(2)+((i))*y(3)*y(3);", "map ev2=r,2,0,0;", "rank(ev2(Jm))", "minAssGTZ(K)"):
        if fragment not in script:
            raise AssertionError((fragment, script))


def _point(orbit: str, source: str, key: str, value: object) -> Callable[[dict[str, Any]], None]:
    def mutate(record: dict[str, Any]) -> None:
        for point in _cell(record, orbit, source)["points"]:
            point[key] = value

    return mutate


def _cell_value(orbit: str, source: str, key: str, value: object) -> Callable[[dict[str, Any]], None]:
    def mutate(record: dict[str, Any]) -> None:
        _cell(record, orbit, source)[key] = value

    return mutate


def _w8_points_on_one_prime(record: dict[str, Any]) -> None:
    for point in _cell(record, "N-", "w8")["points"]:
        point["primes_through"] = [2]


def _off_subspace(record: dict[str, Any]) -> None:
    point = _cell(record, "N+", "iso")["points"][0]
    point["coordinates"][point["coordinates"].index(0)] = 1


MUTATIONS: dict[str, tuple[Callable[[dict[str, Any]], None], str]] = {
    "iso rank lowered": (_point("N-", "iso", "jacobian_rank", 11), "no smooth rational point"),
    "w8 rank lowered": (_point("N+", "w8", "jacobian_rank", 17), "no smooth rational point"),
    "e8 rank lowered": (_point("N-", "e8", "jacobian_rank", 15), "no smooth rational point"),
    "w8 points all on one prime": (_w8_points_on_one_prime, "no smooth rational point on prime 1"),
    "points on both primes": (_point("N+", "e8", "primes_through", [1, 2]), "no smooth rational point"),
    "a point off V(K)": (_point("N-", "w8", "quadrics_nonzero", 1), "off V(K)"),
    "a point off its subspace": (_off_subspace, "leaves its coordinate subspace"),
    "primes changed": (_cell_value("N-", "w8", "primes", [[6, 50]]), "minimal primes differ"),
    "generator count changed": (_cell_value("N+", "iso", "generators", 16), "generator count"),
    "a cell removed": (lambda record: record["cells"].pop(), "six cells"),
    "pass flag cleared": (lambda record: record.update({"pass": False}), "pass flag"),
    "schema changed": (lambda record: record.update(schema="gororoba.a5.weight-slice-smooth-points/0"), "schema"),
    "field changed": (lambda record: record.update(field="Q"), "field"),
}


@pytest.mark.parametrize("name", sorted(MUTATIONS))
def test_the_checker_rejects_each_mutation_of_the_retained_record(name: str) -> None:
    mutate, fragment = MUTATIONS[name]
    record = copy.deepcopy(_record())
    mutate(record)
    found = smooth.problems(record)
    if not any(fragment in problem for problem in found):
        raise AssertionError((name, found))


def test_the_slice_comparison_rejects_other_relations_and_other_primes() -> None:
    record = copy.deepcopy(_record())
    _cell(record, "N-", "w8")["relations_sha256"] = "0" * 64
    _cell(record, "N+", "e8")["relation_count"] = 147
    found = smooth.slice_problems(record)
    for fragment in ("relations differ", "relation count differs"):
        if not any(fragment in problem for problem in found):
            raise AssertionError((fragment, found))


@pytest.mark.audit
def test_the_retained_record_binds_the_current_input_digests() -> None:
    record = _record()
    _same(sorted(record["inputs"]), sorted(smooth.INPUTS))
    for name in smooth.INPUTS:
        _same(record["inputs"][name], hashlib.sha256((ATTACH / name).read_bytes()).hexdigest())
    _same(record["weight_slice_record_sha256"], hashlib.sha256(smooth.WEIGHT_SLICE.read_bytes()).hexdigest())
