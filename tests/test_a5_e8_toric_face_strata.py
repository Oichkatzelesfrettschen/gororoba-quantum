"""The polytope of the 12 monomials of E8-bar and the faces that carry the singular strata (A5-543)."""

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
import e8_component_geometry as geometry  # noqa: E402
import e8_toric_face_strata as strata  # noqa: E402

FACETS = [
    ["a^3", "a^2 b", "a b^2", "b^3", "a^2 z", "a b z", "b^2 z", "a l", "b l", "z l"],
    ["a^3", "a^2 b", "a b^2", "b^3", "a^2 z", "a b z", "b^2 z", "a m", "b m"],
    ["a^3", "a^2 b", "a b^2", "b^3", "a l", "b l", "a m", "b m"],
    ["a^3", "a^2 z", "a l", "z l", "a m"],
    ["b^3", "b^2 z", "b l", "z l", "b m"],
    ["a^2 z", "a b z", "b^2 z", "z l", "a m", "b m"],
    ["a l", "b l", "z l", "a m", "b m"],
]
POLYTOPE = {
    "dimension": 4,
    "points": 12,
    "vertices": ["a^3", "b^3", "a^2 z", "b^2 z", "a l", "b l", "z l", "a m", "b m"],
    "facets": FACETS,
    "monomials_of_the_degree": 16,
    "lattice_points_outside": [],
    "faces": {"point": ["z l"], "line": ["a m", "b m"], "plane": ["z l", "a m", "b m"]},
}
TORIC = {
    "generators": 25,
    "generator_degrees": [2],
    "dimension": 5,
    "multiplicity": 11,
    "point": [4, 4],
    "line": [4, 2],
    "plane": [4, 1],
    "controls": {"smooth_vertex": [4, 1], "without_z_l": [5, 7]},
}
CELL = {
    "point_generators": 20,
    "line_generators": 19,
    "point_face_spans_the_point": True,
    "line_face_spans_the_line": True,
    "plane_face_rank": 3,
    "columns_on_the_point": ["z l"],
    "columns_on_the_line": ["a m", "b m"],
    "meeting_generators": 18,
    "plane_face_spans_the_meeting": True,
    "columns_on_the_meeting": ["z l", "a m", "b m"],
    "meeting": [3, 1],
    "meeting_is_linear": True,
}
# The digest of the quadrics is a label in the constructed records; no unmarked test regenerates the quadrics.
RELATIONS = {"N-": "1" * 64, "N+": "2" * 64}


def _same(found: object, expected: object) -> None:
    if found != expected:
        raise AssertionError((found, expected))


def _record() -> dict[str, Any]:
    """A record built from the numbers of the argument, so that no retained record enters the pull-request lane."""
    return {
        "schema": "gororoba.a5.e8-toric-face-strata/1",
        "fields": {"toric": "Q", "strata": "Q(i)"},
        "polytope": copy.deepcopy(POLYTOPE),
        "toric": copy.deepcopy(TORIC),
        "cells": [
            {
                "orbit": orbit,
                "forms_sha256": birational.fixture_digest(birational.FIXTURE[orbit]),
                **CELL,
                "relations_sha256": RELATIONS[orbit],
                "meeting_forms": strata.MEETING_GENERATORS[orbit],
            }
            for orbit in ("N-", "N+")
        ],
        "pass": True,
    }


def test_the_constructed_record_and_the_exact_checks_pass() -> None:
    _same(strata.problems(_record()), [])
    _same(strata.binding_problems(_record()), [])
    _same(strata.exact_problems(), [])


def test_the_hull_has_seven_facets_and_nine_vertices_and_holds_no_other_monomial() -> None:
    _same(strata.polytope(), POLYTOPE)
    _same(len(strata.polytope()["facets"]), 7)
    outside = [m for m in strata.degree_monomials() if m not in strata.MONOMIALS]
    # Exponents of (a, b, l, z, m): z m, z^3, b z^2 and a z^2.
    _same(outside, [(0, 0, 0, 1, 1), (0, 0, 0, 3, 0), (0, 1, 0, 2, 0), (1, 0, 0, 2, 0)])
    _same([strata.inside(m, strata.MONOMIALS) for m in outside], [False] * 4)
    _same(all(strata.inside(m, strata.MONOMIALS) for m in strata.MONOMIALS), True)


def test_the_three_faces_are_faces_and_their_neighbors_are_not() -> None:
    for face in (strata.POINT_FACE, strata.LINE_FACE, strata.PLANE_FACE):
        _same(strata.is_face(face, strata.MONOMIALS), True)
    # a b z lies inside a facet; a^3 and z l span no edge, where a^3 and a^2 z do; a^3, b^3, z l and a b z, z l
    # are not the points of a face.
    _same(strata.is_face((5,), strata.MONOMIALS), False)
    _same(strata.is_face((0, 9), strata.MONOMIALS), False)
    _same(strata.is_face((0, 4), strata.MONOMIALS), True)
    _same(strata.is_face((0, 3, 9), strata.MONOMIALS), False)
    _same(strata.is_face((5, 9), strata.MONOMIALS), False)


def test_a_thirteenth_monomial_changes_the_facets_and_the_triangle_stops_being_a_face() -> None:
    found = strata.polytope((*strata.MONOMIALS, (0, 0, 0, 1, 1)), (*strata.NAMES, "z m"))
    _same(len(found["vertices"]), 10)
    _same(found["facets"] == FACETS, False)
    _same(found["faces"], {"point": ["z l"], "line": ["a m", "b m"], "plane": None})


def test_a_missing_boundary_monomial_that_is_no_vertex_is_reported_as_a_lattice_point_outside_the_set() -> None:
    kept = [index for index in range(12) if index != 5]
    found = strata.polytope(
        tuple(strata.MONOMIALS[index] for index in kept), tuple(strata.NAMES[index] for index in kept)
    )
    _same(found["lattice_points_outside"], ["(1, 1, 0, 1, 0)"])
    _same(len(found["facets"]), 7)


def test_the_generator_lists_parse_into_linear_forms_over_the_gaussian_integers() -> None:
    _same(
        strata.linear_forms("y(21),y(15)+(i)*y(16),y(10)+y(16)"),
        [{21: (1, 0)}, {15: (1, 0), 16: (0, 1)}, {10: (1, 0), 16: (1, 0)}],
    )
    _same(strata.linear_forms("y(18)+(-i)*y(19),-y(2)"), [{18: (1, 0), 19: (0, -1)}, {2: (-1, 0)}])
    for text in ("y(1)*y(2)", "2*y(1)", "y(1)^2", "x(1)", "y(1)+y(1)", "y(2)+(i)*y(2)"):
        with pytest.raises(ValueError, match="summand"):
            strata.linear_forms(text)
    for orbit in strata.ORBITS:
        point, line = (strata.linear_forms(text) for text in geometry.SINGULAR_GENERATORS[orbit])
        _same((len(point), len(line)), (20, 19))


def test_the_faces_map_onto_the_singular_point_and_the_singular_line_at_both_basepoints() -> None:
    exact = {key: value for key, value in CELL.items() if key not in strata.MEETING_KEYS}
    for orbit in strata.ORBITS:
        _same(strata.strata(orbit), exact)
        columns = strata.columns(orbit)
        _same((len(columns), len(columns[0])), (12, 21))
        _same(birational.gaussian_rank(columns), 12)


def test_the_generators_of_the_other_basepoint_reject_the_faces() -> None:
    # The components at N+ are the conjugates of those at N-, and the columns of M are not real.
    found = strata.strata("N-", geometry.SINGULAR_GENERATORS["N+"])
    _same(found["point_face_spans_the_point"], False)
    _same(found["line_face_spans_the_line"], False)
    _same(found["columns_on_the_point"], [])
    problems = strata.strata_problems("N-", found)
    _same(any("point_face_spans_the_point" in problem for problem in problems), True)


def test_dependent_generators_reject_the_faces_although_they_vanish_on_the_columns() -> None:
    for orbit in strata.ORBITS:
        point, line = (text.split(",") for text in geometry.SINGULAR_GENERATORS[orbit])
        # Twenty forms of rank 19 cut out a plane, and nineteen of rank 18 a space of dimension 3.
        doubled_point = ",".join([point[0], point[1], point[0], *point[3:]])
        doubled_line = ",".join([line[0], line[1], line[0], *line[3:]])
        found = strata.strata(orbit, (doubled_point, ",".join(line)))
        _same((found["point_generators"], found["point_face_spans_the_point"]), (20, False))
        _same(found["line_face_spans_the_line"], True)
        found = strata.strata(orbit, (",".join(point), doubled_line))
        _same((found["line_generators"], found["line_face_spans_the_line"]), (19, False))
        _same(found["point_face_spans_the_point"], True)


def test_the_triangle_spans_the_meeting_and_other_forms_reject_it() -> None:
    for orbit, other in (("N-", "N+"), ("N+", "N-")):
        forms = strata.linear_forms(strata.MEETING_GENERATORS[orbit])
        _same(len(forms), 18)
        found = strata.strata(orbit, meeting_generators=strata.MEETING_GENERATORS[other])
        _same(found["plane_face_spans_the_meeting"], False)
        _same(found["columns_on_the_meeting"], [])
        # Without its last form the list cuts out a space of dimension 4 that holds the triangle.
        shorter = strata.MEETING_GENERATORS[orbit].rsplit(",", 1)[0]
        found = strata.strata(orbit, meeting_generators=shorter)
        _same((found["meeting_generators"], found["plane_face_spans_the_meeting"]), (17, False))
        parts = strata.MEETING_GENERATORS[orbit].split(",")
        doubled = ",".join([parts[0], parts[1], parts[0], *parts[3:]])
        found = strata.strata(orbit, meeting_generators=doubled)
        _same((found["meeting_generators"], found["plane_face_spans_the_meeting"]), (18, False))
        # The singular point and the singular line lie in the meeting: each form of the meeting is a combination of
        # the generators of either component, so the 20 and the 19 generators keep their ranks when it is added.
        for text in geometry.SINGULAR_GENERATORS[orbit]:
            component = strata.linear_forms(text)
            rows = [[form.get(index, (0, 0)) for index in range(1, 22)] for form in [*component, *forms]]
            _same(birational.gaussian_rank(rows), len(component))


def test_the_meeting_stage_cuts_the_component_geometry_script_after_the_sum_of_the_primes() -> None:
    script = strata.meeting_stage(["RELATION 1,2:1", "RELATION 3,3:2"])
    _same("ideal K=(1)*y(1)*y(2),\n(2)*y(3)*y(3);" in script, True)
    _same(script.count("minAssGTZ(K)"), 1)
    _same("ideal I12=std(P4+P11);" in script and "embedded_linear_forms" not in script, True)
    _same(script.count('print("RESULT meeting_generators "+string(mI12));'), 1)
    _same(script.count('print("RESULT done 1");'), 1)


def test_swapped_components_reject_the_faces() -> None:
    line_first = tuple(reversed(geometry.SINGULAR_GENERATORS["N-"]))
    found = strata.strata("N-", line_first)
    _same((found["point_generators"], found["line_generators"]), (19, 20))
    _same(found["point_face_spans_the_point"], False)
    _same(found["line_face_spans_the_line"], False)


def test_a_form_whose_z_l_term_moves_takes_the_vertex_off_the_singular_point() -> None:
    # Generator 16 at N- is a multiple of z l^2 alone; as a multiple of a l^2 its column leaves the point.
    forms = list(birational.FIXTURE["N-"])
    _same(forms[15], ((0, 67108864, (0, 0, 2, 1, 0)),))
    forms[15] = ((0, 67108864, (1, 0, 2, 0, 0)),)
    found = strata.strata("N-", forms=tuple(forms))
    _same(found["point_face_spans_the_point"], False)
    _same(found["columns_on_the_point"], [])


def test_the_singular_stages_name_the_charts_and_the_controls() -> None:
    _same(strata.local_stage("point", 9, (), 12).count("h*u("), 11)
    stage = strata.local_stage("line", 10, (11,), 12)
    _same("h*u(10),1,h*u(11)+1;" in stage, True)
    _same("ring Lline=0,(u(1..11),h),dp;" in stage, True)
    _same("sat(fline(J),h)" in stage and "subst(Tline,h,0)+ideal(h)" in stage, True)
    _same(",ds" in stage or ",ls" in stage or ",Ds" in stage, False)
    stage = strata.local_stage("plane", 9, (10, 11), 12)
    _same("h*u(9),1,h*u(10)+1,h*u(11)+1;" in stage, True)
    script = strata.toric_stage(strata.MONOMIALS, "toric", "")
    _same(
        "ideal mon=a^3,a^2*b^1,a^1*b^2,b^3,a^2*z^1,a^1*b^1*z^1,b^2*z^1,a^1*l^1,b^1*l^1,l^1*z^1,a^1*m^1,b^1*m^1;"
        in script,
        True,
    )
    _same(script.count('print("RESULT done 1");'), 1)


RECORD_MUTATIONS: dict[str, tuple[Callable[[dict[str, Any]], None], str]] = {
    "eight facets": (lambda record: record["polytope"]["facets"].append(["a^3"]), "polytope"),
    "a lattice point outside the set": (
        lambda record: record["polytope"].update(lattice_points_outside=["z m"]),
        "polytope",
    ),
    "the triangle is not a face": (lambda record: record["polytope"]["faces"].update(plane=None), "polytope"),
    "another edge": (lambda record: record["polytope"]["faces"].update(line=["a l", "b l"]), "polytope"),
    "a toric ideal of 24 quadrics": (lambda record: record["toric"].update(generators=24), "toric"),
    "a cubic generator": (lambda record: record["toric"].update(generator_degrees=[2, 3]), "toric"),
    "a toric multiplicity of 12": (lambda record: record["toric"].update(multiplicity=12), "toric"),
    "multiplicity 3 at the vertex": (lambda record: record["toric"].update(point=[4, 3]), "toric"),
    "multiplicity 1 on the edge": (lambda record: record["toric"].update(line=[4, 1]), "toric"),
    "multiplicity 2 on the triangle": (lambda record: record["toric"].update(plane=[4, 2]), "toric"),
    "a chart of dimension 5": (lambda record: record["toric"].update(point=[5, 4]), "toric"),
    "a singular control vertex": (
        lambda record: record["toric"]["controls"].update(smooth_vertex=[4, 2]),
        "toric",
    ),
    "the control variety of multiplicity 11": (
        lambda record: record["toric"]["controls"].update(without_z_l=[5, 11]),
        "toric",
    ),
    "the vertex off the point": (
        lambda record: record["cells"][0].update(point_face_spans_the_point=False),
        "point_face_spans_the_point",
    ),
    "the edge off the line": (
        lambda record: record["cells"][1].update(line_face_spans_the_line=False),
        "line_face_spans_the_line",
    ),
    "a triangle of rank 2": (lambda record: record["cells"][0].update(plane_face_rank=2), "plane_face_rank"),
    "a second column on the point": (
        lambda record: record["cells"][1].update(columns_on_the_point=["z l", "a l"]),
        "columns_on_the_point",
    ),
    "a third column on the line": (
        lambda record: record["cells"][0].update(columns_on_the_line=["z l", "a m", "b m"]),
        "columns_on_the_line",
    ),
    "a point ideal of 19 forms": (lambda record: record["cells"][0].update(point_generators=19), "point_generators"),
    "the triangle off the meeting": (
        lambda record: record["cells"][0].update(plane_face_spans_the_meeting=False),
        "plane_face_spans_the_meeting",
    ),
    "a meeting of 17 forms": (lambda record: record["cells"][1].update(meeting_generators=17), "meeting_generators"),
    "a fourth column on the meeting": (
        lambda record: record["cells"][0].update(columns_on_the_meeting=["a l", "z l", "a m", "b m"]),
        "columns_on_the_meeting",
    ),
    "a meeting of dimension 4": (lambda record: record["cells"][1].update(meeting=[4, 1]), "meeting differs"),
    "a meeting with a quadric": (
        lambda record: record["cells"][0].update(meeting_is_linear=False),
        "meeting_is_linear",
    ),
    "the meeting forms of the other basepoint": (
        lambda record: record["cells"][0].update(meeting_forms=strata.MEETING_GENERATORS["N+"]),
        "meeting_forms",
    ),
    "a cell removed": (lambda record: record["cells"].pop(), "N- and N+"),
    "pass flag cleared": (lambda record: record.update({"pass": False}), "pass flag"),
    "schema changed": (lambda record: record.update(schema="gororoba.a5.e8-toric-face-strata/0"), "schema"),
    "fields changed": (lambda record: record.update(fields={"toric": "Q(i)", "strata": "Q(i)"}), "fields"),
}


@pytest.mark.parametrize("name", sorted(RECORD_MUTATIONS))
def test_the_checker_rejects_each_mutation_of_a_record(name: str) -> None:
    mutate, fragment = RECORD_MUTATIONS[name]
    record = _record()
    mutate(record)
    found = strata.problems(record)
    if not any(fragment in problem for problem in found):
        raise AssertionError((name, found))


def test_a_changed_form_changes_the_digest_that_binds_the_record() -> None:
    record = _record()
    record["cells"][0]["forms_sha256"] = "0" * 64
    _same(strata.binding_problems(record), ["N-: forms_sha256 differs from the digest of the fixture"])


def _geometry_record(multiplicity_at_the_point: int = 4) -> dict[str, Any]:
    return {
        "cells": [
            {
                "orbit": orbit,
                "singular_generators": list(geometry.SINGULAR_GENERATORS[orbit]),
                "tangent_cones": [[1, 5, multiplicity_at_the_point], [2, 5, 2], [3, 5, 1]],
                "relations_sha256": RELATIONS[orbit],
                "scroll_meets_main": [3, 1],
            }
            for orbit in ("N-", "N+")
        ]
    }


def test_the_comparison_with_the_component_geometry_record_rejects_other_generators_and_multiplicities() -> None:
    _same(strata.geometry_problems(_record(), _geometry_record()), [])
    _same(
        strata.geometry_problems(_record(), _geometry_record(3)),
        [
            f"{orbit}: the multiplicity at the point differs from the component-geometry record"
            for orbit in ("N-", "N+")
        ],
    )
    other = _geometry_record()
    other["cells"][1]["singular_generators"] = list(geometry.SINGULAR_GENERATORS["N-"])
    _same(
        strata.geometry_problems(_record(), other),
        ["N+: the singular generators differ from those of the component-geometry record"],
    )
    other = _geometry_record()
    other["cells"][0]["relations_sha256"] = "3" * 64
    other["cells"][1]["scroll_meets_main"] = [4, 1]
    _same(
        strata.geometry_problems(_record(), other),
        [
            "N-: the quadrics differ from those of the component-geometry record",
            "N+: the meeting differs from that of the component-geometry record",
        ],
    )
    _same(len(strata.geometry_problems(_record(), {"cells": []})), 12)


def test_a_record_that_disagrees_with_the_component_geometry_record_is_written_as_failing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    retained = tmp_path / "geometry.json"
    retained.write_text(json.dumps(_geometry_record(3)), encoding="utf-8")
    written = tmp_path / "record.json"
    monkeypatch.setattr(strata, "GEOMETRY_RECORD", retained)
    monkeypatch.setattr(strata, "RECORD", written)
    monkeypatch.setattr(strata, "build", _record)
    monkeypatch.setattr(sys, "argv", ["e8_toric_face_strata.py"])
    with pytest.raises(SystemExit):
        strata.main()
    _same(json.loads(written.read_text(encoding="utf-8"))["pass"], False)


@pytest.mark.skipif(
    shutil.which("Singular") is None or shutil.which("prlimit") is None,
    reason="Singular 4.4 or prlimit is absent; the toric ideal and its local multiplicities need both",
)
def test_singular_finds_the_toric_invariants_and_the_three_multiplicities() -> None:
    _same(strata.toric(), TORIC)


@pytest.mark.audit
@pytest.mark.skipif(
    shutil.which("Singular") is None or shutil.which("prlimit") is None,
    reason="Singular 4.4 or prlimit is absent; the quadrics of the slice and their primes need both",
)
def test_singular_regenerates_the_meeting_forms_from_the_quadrics_of_the_slice() -> None:
    for orbit in strata.ORBITS:
        found = strata.meeting(orbit)
        _same(found["meeting_forms"], strata.MEETING_GENERATORS[orbit])
        _same((found["meeting"], found["meeting_is_linear"]), ([3, 1], True))


@pytest.mark.audit
def test_the_retained_record_passes_every_check_and_binds_the_current_inputs() -> None:
    record = json.loads(strata.RECORD.read_text(encoding="utf-8"))
    _same(strata.check(record), [])
    _same(record["pass"], True)
    _same(sorted(record["inputs"]), sorted(strata.INPUTS))
    for name in strata.INPUTS:
        _same(record["inputs"][name], hashlib.sha256((ATTACH / name).read_bytes()).hexdigest())
    _same(strata.geometry_problems(record), [])
