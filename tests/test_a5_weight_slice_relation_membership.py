"""Membership of every degree-2 relation of the weight-slice producer in J + m I^2, by the truncation lemma."""

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

import weight_slice_relation_membership as membership  # noqa: E402


def _same(found: object, expected: object) -> None:
    if found != expected:
        raise AssertionError((found, expected))


def _record() -> dict[str, Any]:
    record: dict[str, Any] = json.loads(membership.RECORD.read_text(encoding="utf-8"))
    return record


def test_the_retained_record_passes_and_agrees_with_the_weight_slice_record() -> None:
    record = _record()
    _same(membership.problems(record), [])
    _same(membership.slice_problems(record), [])
    _same(record["pass"], True)
    _same(len(record["cells"]), 10)


def test_every_truncation_monomial_lies_one_weight_above_the_largest_product() -> None:
    """The lemma needs each generator of T above the bound; the producer's truncation starts at the next weight."""
    for cell in _record()["cells"]:
        _same(cell["truncation_min_weight"], cell["truncation_bound"] + 1)
        _same(cell["relations_above_truncation"], 0)


def test_the_relation_counts_are_those_of_the_five_sources() -> None:
    counts = {(cell["orbit"], cell["source"]): cell["relations"] for cell in _record()["cells"]}
    for orbit in ("N-", "N+"):
        _same((counts[(orbit, "w8")], counts[(orbit, "e8")], counts[(orbit, "iso")]), (144, 148, 68))
    _same(sorted(counts[(orbit, source)] for orbit in ("N-", "N+") for source in ("xp", "xm")), [0, 0, 69, 69])


def test_the_stage_reduces_the_unreduced_products_modulo_the_producer_basis() -> None:
    for fragment in ("G[IX[ub][1]]*G[IX[ub][2]]", "reduce(f,sQ)", "tmax(f)>pmax", "thomog(G[ua])"):
        if fragment not in membership.STAGE:
            raise AssertionError(fragment)


def _set(orbit: str, source: str, key: str, value: object) -> Callable[[dict[str, Any]], None]:
    def mutate(record: dict[str, Any]) -> None:
        next(c for c in record["cells"] if (c["orbit"], c["source"]) == (orbit, source))[key] = value

    return mutate


MUTATIONS: dict[str, tuple[Callable[[dict[str, Any]], None], str]] = {
    "a relation outside the ideal": (_set("N-", "e8", "membership_failures", 1), "membership_failures"),
    "a relation above the truncation": (_set("N+", "w8", "relations_above_truncation", 2), "above_truncation"),
    "an inhomogeneous generator": (_set("N-", "iso", "generators_inhomogeneous", 1), "generators_inhomogeneous"),
    "an inhomogeneous germ generator": (_set("N+", "e8", "germ_inhomogeneous_generators", 1), "germ_inhomogeneous"),
    "a truncation monomial at the bound": (_set("N-", "w8", "truncation_min_weight", 16), "at most the bound"),
    "a truncation generator with two terms": (_set("N+", "iso", "truncation_non_monomials", 1), "non_monomials"),
    "the control accepted": (_set("N-", "xm", "control_single_product_rejected", 0), "control product"),
    "a cell removed": (lambda record: record["cells"].pop(), "ten cells"),
    "pass flag cleared": (lambda record: record.update({"pass": False}), "pass flag"),
    "schema changed": (lambda record: record.update(schema="gororoba.a5.weight-slice-relation-membership/0"), "schema"),
    "field changed": (lambda record: record.update(field="Q"), "field"),
}


@pytest.mark.parametrize("name", sorted(MUTATIONS))
def test_the_checker_rejects_each_mutation_of_the_retained_record(name: str) -> None:
    mutate, fragment = MUTATIONS[name]
    record = copy.deepcopy(_record())
    mutate(record)
    found = membership.problems(record)
    if not any(fragment in problem for problem in found):
        raise AssertionError((name, found))


def test_the_slice_comparison_rejects_other_relations_counts_and_bounds() -> None:
    record = copy.deepcopy(_record())
    record["cells"][0]["relations_sha256"] = "0" * 64
    record["cells"][1]["relations"] = 147
    record["cells"][2]["truncation_bound"] = 11
    found = membership.slice_problems(record)
    _same(len(found), 3)
    for fragment in ("relations differ", "relation count differs", "truncation bound differs"):
        if not any(fragment in problem for problem in found):
            raise AssertionError((fragment, found))


@pytest.mark.audit
def test_the_retained_record_binds_the_current_input_digests() -> None:
    record = _record()
    _same(sorted(record["inputs"]), sorted(membership.INPUTS))
    for name in membership.INPUTS:
        _same(record["inputs"][name], hashlib.sha256((ATTACH / name).read_bytes()).hexdigest())
    _same(record["weight_slice_record_sha256"], hashlib.sha256(membership.WEIGHT_SLICE.read_bytes()).hexdigest())
