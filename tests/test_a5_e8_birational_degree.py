"""The weighted initial-form map of E8-bar has degree 5 and is birational onto the degree-11 component (A5-512)."""

from __future__ import annotations

import copy
import hashlib
import json
import shutil
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
ATTACH = ROOT / "docs" / "evidence" / "a5-kernel-attachments"
sys.path.insert(0, str(ATTACH))

import e8_birational_degree as birational  # noqa: E402
import weight_slice_fiber_relations as ws  # noqa: E402

GENERATOR_WEIGHTS = [5, 4, 7, 5, 6, 5, 7, 5, 3, 4, 4, 5, 5, 3, 4, 4, 5, 3, 3, 4, 5]
FIXTURE = birational.FIXTURE


def _same(found: object, expected: object) -> None:
    if found != expected:
        raise AssertionError((found, expected))


def _cell(orbit: str, shift: int) -> dict[str, Any]:
    return {
        "orbit": orbit,
        "forms_sha256": birational.fixture_digest(FIXTURE[orbit]),
        "generator_weights": GENERATOR_WEIGHTS,
        "change_of_variable": shift,
        "generators": 21,
        "nonzero_forms": 17,
        "zero_forms": [3, 5, 6, 7],
        "divisible_by_pl": 17,
        "monomials_before_change": 14,
        "monomials_after_change": 12,
        "rank": 12,
        "unsaturated_dimension": 8,
        "saturated_dimension": 5,
        "saturated_multiplicity": 5,
        "graphs_dimension": 5,
        "graphs_multiplicity": 5,
        "graph_ideal_in_saturation": True,
        "saturation_in_graph_ideal": True,
        "components": [[5, 1, True, True], [5, 4, True, True]],
        "controls": {
            "mutated_difference": {
                "dimension": 4,
                "graph_ideal_in_saturation": True,
                "saturation_in_graph_ideal": False,
            },
            "fourth_roots": {"graph_ideal_in_saturation": False, "saturation_in_graph_ideal": False},
        },
    }


def _record() -> dict[str, Any]:
    """A record built from the numbers of the argument, so that no retained record enters the pull-request lane."""
    return {
        "schema": "gororoba.a5.e8-birational-degree/1",
        "field": "Q(i)",
        "toric": {
            "quotient_degree": 3,
            "points": 12,
            "simplices": 11,
            "normalized_volume": 11,
            "difference_lattice_index": 1,
        },
        "cells": [_cell("N-", 4), _cell("N+", -4)],
        "pass": True,
    }


def test_the_constructed_record_passes_and_the_fixture_passes_steps_a_to_c() -> None:
    _same(birational.problems(_record()), [])
    _same(birational.binding_problems(_record()), [])
    _same(birational.all_fixture_problems(), [])
    _same(list(birational.ORBITS), ["N-", "N+"])


def test_each_basepoint_has_17_nonzero_forms_of_weight_5_that_pl_divides() -> None:
    for orbit, shift in (("N-", 4), ("N+", -4)):
        forms = FIXTURE[orbit]
        _same(len(forms), 21)
        _same([index for index, form in enumerate(forms, 1) if not form], [3, 5, 6, 7])
        for form in (form for form in forms if form):
            _same({sum(w * e for w, e in zip((1, 1, 2, 1, 2), term[2], strict=True)) for term in form}, {5})
            _same(all(term[2][2] >= 1 for term in form), True)
        stats = birational.fixture_stats(forms, shift)
        _same((stats["nonzero_forms"], stats["divisible_by_pl"]), (17, 17))


def test_the_change_of_variable_turns_14_monomials_into_the_12_of_rank_12() -> None:
    for orbit, shift in (("N-", 4), ("N+", -4)):
        stats = birational.fixture_stats(FIXTURE[orbit], shift)
        _same((stats["monomials_before_change"], stats["monomials_after_change"], stats["rank"]), (14, 12, 12))
        changed = birational.quotients(FIXTURE[orbit], shift)
        _same({key for q in changed for key in q}, set(birational.MONOMIALS))
    unchanged = {key for q in birational.quotients(FIXTURE["N-"], None) for key in q}
    _same(len(unchanged), 14)
    _same(unchanged - set(birational.MONOMIALS), {(0, 1, 0, 2, 0), (1, 0, 0, 2, 0)})


def test_the_change_of_variable_of_the_other_basepoint_leaves_14_monomials() -> None:
    for orbit, wrong in (("N-", -4), ("N+", 4)):
        found = birational.fixture_problems(orbit, FIXTURE[orbit], wrong)
        _same(found, [f"{orbit}: the changed quotients carry 14 monomials, not the set A"])


def test_the_rank_is_read_over_q_of_i() -> None:
    # The second row is i times the first, so the rank over Q(i) is 1.
    dependent = [[(1, 0), (0, 1)], [(0, 1), (-1, 0)]]
    independent = [[(1, 0), (0, 0)], [(0, 0), (0, 1)]]
    _same(birational.gaussian_rank(dependent), 1)
    _same(birational.gaussian_rank(independent), 2)
    _same(birational.gaussian_rank([[(0, 0), (0, 0)]]), 0)


def _form_mutation(orbit: str, index: int, form: birational.Form) -> Callable[[], list[str]]:
    def mutate() -> list[str]:
        forms = list(FIXTURE[orbit])
        forms[index] = form
        return birational.fixture_problems(orbit, tuple(forms))

    return mutate


def _forms_mutation(orbit: str, rebuild: Callable[[tuple[birational.Form, ...]], tuple[birational.Form, ...]]) -> Any:
    return lambda: birational.fixture_problems(orbit, rebuild(FIXTURE[orbit]))


FIXTURE_MUTATIONS: dict[str, tuple[Callable[[], list[str]], str]] = {
    "a term without pl": (_form_mutation("N-", 0, ((67108864, 0, (0, 3, 0, 2, 0)),)), "divisible_by_pl is 16"),
    "a term of weight 6": (_form_mutation("N+", 0, ((67108864, 0, (0, 3, 1, 1, 0)),)), "weighted degree [6]"),
    "a nonzero form zeroed": (_form_mutation("N-", 8, ()), "nonzero_forms is 16"),
    "a zero form made nonzero": (_form_mutation("N+", 2, ((1, 0, (0, 3, 1, 0, 0)),)), "zero_forms is"),
    "a repeated monomial": (
        _form_mutation("N-", 0, ((1, 0, (0, 3, 1, 0, 0)), (2, 0, (0, 3, 1, 0, 0)))),
        "repeats a monomial",
    ),
    "a zero coefficient": (_form_mutation("N+", 0, ((0, 0, (0, 3, 1, 0, 0)),)), "zero coefficient"),
    "a form dropped": (_forms_mutation("N-", lambda forms: forms[:-1]), "generators is 20"),
    "a monomial dropped from the quotients": (
        _form_mutation("N-", 20, ((-67108864, 0, (2, 1, 0, 0, 1)), (1, 0, (3, 0, 1, 0, 0)))),
        "divisible_by_pl is 16",
    ),
}


@pytest.mark.parametrize("name", sorted(FIXTURE_MUTATIONS))
def test_the_fixture_checker_rejects_each_mutation(name: str) -> None:
    mutate, fragment = FIXTURE_MUTATIONS[name]
    found = mutate()
    if not any(fragment in problem for problem in found):
        raise AssertionError((name, found))


def test_a_changed_coefficient_changes_the_digest_that_binds_the_record() -> None:
    forms = list(FIXTURE["N-"])
    forms[0] = ((134217728, 0, (0, 3, 1, 0, 0)),)
    changed = tuple(forms)
    # Steps A to C hold for this change, which keeps the monomials and the rank; the digest rejects it.
    _same(birational.fixture_problems("N-", changed), [])
    _same(birational.fixture_digest(changed) == birational.fixture_digest(FIXTURE["N-"]), False)
    record = _record()
    record["cells"][0]["forms_sha256"] = birational.fixture_digest(changed)
    _same(birational.binding_problems(record), ["N-: forms_sha256 differs from the digest of the fixture"])


def test_the_five_ratio_monomials_fix_the_coordinates_up_to_the_orbit() -> None:
    _same(birational.ratio_problems(), [])
    without_m = tuple(m for m in birational.MONOMIALS if m != (1, 0, 0, 0, 1))
    _same(len(birational.ratio_problems(without_m)), 1)
    _same("coordinate 4" in birational.ratio_problems(without_m)[0], True)
    without_a3 = tuple(m for m in birational.MONOMIALS if m != (3, 0, 0, 0, 0))
    _same(len(birational.ratio_problems(without_a3)) >= 1, True)


def test_the_triangulation_covers_the_hull_once_with_volume_11_and_edges_spanning_the_lattice() -> None:
    found, summary = birational.lattice_problems()
    _same(found, [])
    _same(summary["normalized_volume"], 11)
    _same(summary["difference_lattice_index"], 1)
    _same(summary["simplices"], 11)


def test_the_triangulation_check_rejects_a_missing_duplicate_or_misplaced_simplex() -> None:
    simplices = birational.TRIANGULATION
    missing, summary = birational.lattice_problems(simplices=simplices[:-1])
    _same(summary["normalized_volume"], 10)
    _same(any("does not support the hull" in problem or "lie on one side" in problem for problem in missing), True)
    duplicate, _ = birational.lattice_problems(simplices=(*simplices, simplices[0]))
    _same(any("lies in 3 simplices" in problem for problem in duplicate), True)
    # Two of the 12 points and three others span a degenerate simplex.
    degenerate, _ = birational.lattice_problems(simplices=(*simplices[:-1], (0, 1, 2, 3, 4)))
    _same(len(degenerate) > 0, True)
    off_plane = list(birational.MONOMIALS)
    off_plane[0] = (4, 0, 0, 0, 0)
    leaving, _ = birational.lattice_problems(monomials=tuple(off_plane))
    _same("a monomial of A leaves the hyperplane of weighted degree 3" in leaving, True)


def test_the_singular_stages_read_the_fixture_and_name_the_controls() -> None:
    for orbit in birational.ORBITS:
        stage = birational.ideal_stage(FIXTURE[orbit])
        script = stage.split("ideal I=", 1)[1].split(";\npoly h=", 1)[0]
        _same(len(script.split(",\n")), 17)
        _same("t^5-1" in stage and "t^4-1" in stage, True)
        _same("poly h=pa*pl*qa*ql;" in stage, True)
        _same("I3[3]=I3[3]+pa*pl*qa*qb*qz" in stage, True)
        for key in ("saturated", "graphs", "mutated_difference", "fourth_roots", "component"):
            _same(stage.count(f'RESULT {key} "'), 1)
        _same("RESULT done 1" in stage, True)
        extraction = birational.extraction_stage(orbit)
        _same(",".join(birational.orders.PARAMETRIZATION[orbit]) in extraction, True)
        _same("wv=1,1,2,1,2" in extraction and "jet(gp[k],5,wv)" in extraction, True)


def test_a_form_survives_the_round_trip_through_singular_syntax() -> None:
    _same(birational.parse_form("0"), ())
    _same(birational.parse_form("(33554432*i)*pb*pl^2"), ((0, 33554432, (0, 1, 2, 0, 0)),))
    _same(
        birational.parse_form("67108864*pb*pl*pz^2-16777216*pb*pl*pm"),
        ((67108864, 0, (0, 1, 1, 2, 0)), (-16777216, 0, (0, 1, 1, 0, 1))),
    )
    for orbit in birational.ORBITS:
        for form in FIXTURE[orbit]:
            if form:
                _same(birational.parse_form(birational._polynomial(form, birational.FIRST)), form)


RECORD_MUTATIONS: dict[str, tuple[Callable[[dict[str, Any]], None], str]] = {
    "a graph missing from the saturation": (
        lambda record: record["cells"][0].update(graph_ideal_in_saturation=False),
        "graph_ideal_in_saturation",
    ),
    "the saturation larger than the graphs": (
        lambda record: record["cells"][1].update(saturation_in_graph_ideal=False),
        "saturation_in_graph_ideal",
    ),
    "a saturation of dimension 6": (
        lambda record: record["cells"][0].update(saturated_dimension=6),
        "saturated_dimension",
    ),
    "a saturation of multiplicity 10": (
        lambda record: record["cells"][1].update(saturated_multiplicity=10),
        "saturated_multiplicity",
    ),
    "a component that dominates one factor only": (
        lambda record: record["cells"][0].update(components=[[5, 1, True, True], [5, 4, True, False]]),
        "components",
    ),
    "a third component": (
        lambda record: record["cells"][1].update(
            components=[[5, 1, True, True], [5, 2, True, True], [5, 2, True, True]]
        ),
        "components",
    ),
    "the mutated difference accepted": (
        lambda record: record["cells"][0]["controls"]["mutated_difference"].update(saturation_in_graph_ideal=True),
        "controls",
    ),
    "the fourth roots accepted": (
        lambda record: record["cells"][1]["controls"]["fourth_roots"].update(saturation_in_graph_ideal=True),
        "controls",
    ),
    "the fourth roots equal the saturation": (
        lambda record: record["cells"][0]["controls"]["fourth_roots"].update(graph_ideal_in_saturation=True),
        "controls",
    ),
    "a quotient rank of 11": (lambda record: record["cells"][0].update(rank=11), "rank"),
    "13 monomials": (lambda record: record["cells"][1].update(monomials_after_change=13), "monomials_after_change"),
    "the unchanged quotients with 12 monomials": (
        lambda record: record["cells"][0].update(monomials_before_change=12),
        "monomials_before_change",
    ),
    "16 forms divisible by pl": (lambda record: record["cells"][0].update(divisible_by_pl=16), "divisible_by_pl"),
    "the wrong change of variable": (
        lambda record: record["cells"][0].update(change_of_variable=-4),
        "change_of_variable",
    ),
    "a toric volume of 12": (lambda record: record["toric"].update(normalized_volume=12), "toric"),
    "a lattice of index 2": (lambda record: record["toric"].update(difference_lattice_index=2), "toric"),
    "a cell removed": (lambda record: record["cells"].pop(), "N- and N+"),
    "pass flag cleared": (lambda record: record.update({"pass": False}), "pass flag"),
    "schema changed": (lambda record: record.update(schema="gororoba.a5.e8-birational-degree/0"), "schema"),
    "field changed": (lambda record: record.update(field="Q"), "field"),
}


@pytest.mark.parametrize("name", sorted(RECORD_MUTATIONS))
def test_the_checker_rejects_each_mutation_of_a_record(name: str) -> None:
    mutate, fragment = RECORD_MUTATIONS[name]
    record = copy.deepcopy(_record())
    mutate(record)
    found = birational.problems(record)
    if not any(fragment in problem for problem in found):
        raise AssertionError((name, found))


def test_the_slice_comparison_rejects_other_generators(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    cells = [
        {
            "orbit": orbit,
            "characteristic": 0,
            "source": "e8",
            "generator_count": 21,
            "generator_weights": GENERATOR_WEIGHTS,
        }
        for orbit in ("N-", "N+")
    ]
    cells.append({"orbit": "N-", "characteristic": 0, "source": "w8", "generator_count": 24, "generator_weights": [1]})
    path = tmp_path / "slice.json"
    path.write_text(json.dumps({"cells": cells}), encoding="utf-8")
    monkeypatch.setattr(birational, "WEIGHT_SLICE", path)
    _same(birational.slice_problems(_record()), [])
    record = copy.deepcopy(_record())
    record["cells"][0]["generator_weights"] = [*GENERATOR_WEIGHTS[:-1], 6]
    record["cells"][1]["generators"] = 20
    _same(
        birational.slice_problems(record),
        [
            "N-: the generators differ from those of the weight-slice record",
            "N+: the generators differ from those of the weight-slice record",
        ],
    )


@pytest.mark.skipif(
    shutil.which("Singular") is None or shutil.which("prlimit") is None,
    reason="Singular 4.4 or prlimit is absent; the saturation test of step D needs both",
)
def test_singular_finds_the_five_graphs_and_rejects_both_controls() -> None:
    values = ws.run_singular(birational.ideal_stage(FIXTURE["N-"]))["values"]
    found = birational.ideal_record(values)
    expected = _cell("N-", 4)
    for key, value in found.items():
        _same(value, expected[key])


@pytest.mark.audit
def test_the_retained_record_passes_every_check_and_binds_the_current_inputs() -> None:
    record = json.loads(birational.RECORD.read_text(encoding="utf-8"))
    _same(birational.check(record), [])
    _same(record["pass"], True)
    _same(sorted(record["inputs"]), sorted(birational.INPUTS))
    for name in birational.INPUTS:
        _same(record["inputs"][name], hashlib.sha256((ATTACH / name).read_bytes()).hexdigest())
    _same(record["weight_slice_record_sha256"], hashlib.sha256(birational.WEIGHT_SLICE.read_bytes()).hexdigest())
    _same(birational.slice_problems(record), [])
