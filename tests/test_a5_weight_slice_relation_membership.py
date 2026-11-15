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


def test_the_retained_record_passes_its_checker() -> None:
    record = _record()
    _same(membership.problems(record), [])
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


def test_the_relations_fill_the_kernel_of_the_normal_form_matrix_in_every_cell() -> None:
    """Rank plus nullity: 858 relations in all, and for E8-bar the rank 83 is the dimension of (S/K)_2."""
    cells = _record()["cells"]
    _same(sum(cell["relations"] for cell in cells), 858)
    for cell in cells:
        _same(cell["spanning_normal_form_rank"] + cell["relations"], cell["spanning_products"])
        _same(cell["spanning_relation_rank"], cell["relations"])
        _same(cell["selection_failures"], 0)
        if cell["source"] == "e8":
            _same(cell["spanning_normal_form_rank"], 83)


def test_the_stage_reduces_the_unreduced_products_modulo_the_producer_basis() -> None:
    for fragment in (
        "G[IX[ub][1]]*G[IX[ub][2]]",
        "reduce(f,sQ)",
        "tmax(f)>pmax",
        "thomog(G[ua])",
        "std(J+TR+m*PF+G)",
        "rank(M)",
    ):
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
    "a truncation monomial at the bound": (_set("N-", "w8", "truncation_min_weight", 16), "one weight above"),
    "a truncation generator with two terms": (_set("N+", "iso", "truncation_non_monomials", 1), "non_monomials"),
    "a boolean in an integer slot": (_set("N-", "e8", "membership_failures", False), "not an integer"),
    "a truncation monomial far above the bound": (_set("N+", "e8", "truncation_min_weight", 999), "one weight above"),
    "a Pfaffian outside the selected generators": (_set("N-", "w8", "selection_failures", 2), "selection_failures"),
    "an inhomogeneous Pfaffian": (_set("N+", "iso", "pfaffians_inhomogeneous", 1), "pfaffians_inhomogeneous"),
    "a relation missing from the kernel": (_set("N-", "e8", "spanning_normal_form_rank", 82), "do not fill the kernel"),
    "dependent relations": (_set("N+", "w8", "spanning_relation_rank", 143), "linearly dependent"),
    "a relation count of another source": (_set("N-", "iso", "relations", 69), "relation count is not"),
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


def _constructed_cell(index: int, orbit: str, source: str) -> dict[str, Any]:
    relations = membership.RELATIONS[source][-1]
    cell: dict[str, Any] = {key: 0 for key in membership.ZERO_KEYS}
    cell.update(
        orbit=orbit,
        source=source,
        relations_sha256=f"{index + 1:064x}",
        relations=relations,
        truncation_bound=16,
        truncation_min_weight=17,
        control_single_product_rejected=1,
        selection_truncation_bound=10,
        selection_truncation_min_weight=11,
        spanning_products=relations + 1,
        spanning_normal_form_rank=1,
        spanning_relation_rank=relations,
    )
    return cell


def _constructed_record(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    """A passing record and the weight-slice record it matches, one characteristic-0 cell per membership cell."""
    cells = [_constructed_cell(index, orbit, source) for index, (orbit, source) in enumerate(membership.CELLS)]
    slice_cells = [
        {
            "orbit": cell["orbit"],
            "source": cell["source"],
            "characteristic": 0,
            "relations_sha256": cell["relations_sha256"],
            "relation_count": cell["relations"],
            "product_max_weight": cell["truncation_bound"],
        }
        for cell in cells
    ]
    slice_cells.append({"orbit": "N-", "source": "w8", "characteristic": 32009, "relations_sha256": "f" * 64})
    fixture = tmp_path / "weight-slice.json"
    fixture.write_text(json.dumps({"cells": slice_cells}), encoding="utf-8")
    monkeypatch.setattr(membership, "WEIGHT_SLICE", fixture)
    return {
        "schema": membership.SCHEMA,
        "field": "Q(i)",
        "inputs": {name: hashlib.sha256((ATTACH / name).read_bytes()).hexdigest() for name in membership.INPUTS},
        "weight_slice_record_sha256": hashlib.sha256(fixture.read_bytes()).hexdigest(),
        "cells": cells,
        "pass": True,
    }


def test_the_slice_comparison_rejects_other_relations_counts_and_bounds(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    record = _constructed_record(tmp_path, monkeypatch)
    _same(membership.slice_problems(record), [])
    record["cells"][0]["relations_sha256"] = "0" * 64
    record["cells"][1]["relations"] = 147
    record["cells"][2]["truncation_bound"] = 11
    found = membership.slice_problems(record)
    _same(len(found), 3)
    for fragment in ("relations differ", "relation count differs", "truncation bound differs"):
        if not any(fragment in problem for problem in found):
            raise AssertionError((fragment, found))


def test_the_full_validator_reports_a_changed_input_digest(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    record = _constructed_record(tmp_path, monkeypatch)
    _same(membership.check_problems(record), [])
    record["inputs"]["weight_slice_fiber_relations.py"] = "0" * 64
    _same(membership.check_problems(record), ["input digest of weight_slice_fiber_relations.py differs"])
    record["weight_slice_record_sha256"] = "0" * 64
    _same(len(membership.check_problems(record)), 2)


@pytest.mark.audit
def test_the_retained_record_binds_the_current_input_digests() -> None:
    record = _record()
    _same(membership.slice_problems(record), [])
    _same(sorted(record["inputs"]), sorted(membership.INPUTS))
    for name in membership.INPUTS:
        _same(record["inputs"][name], hashlib.sha256((ATTACH / name).read_bytes()).hexdigest())
    _same(record["weight_slice_record_sha256"], hashlib.sha256(membership.WEIGHT_SLICE.read_bytes()).hexdigest())
