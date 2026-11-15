"""The polytope of the E8-bar degree-11 component and the faces that carry its singular strata.

By A5-512 each initial form V_k of `e8_birational_degree.py` is pl times a row of a 21 x 12 matrix M of rank 12
applied to the 12 monomials of the set A, so the degree-11 component is the image under M of the toric fourfold X_A
in P^11 (A5-543). This module computes the convex polytope of A and matches three of its faces with the strata of
`e8_component_geometry.py`.

Polytope. In the lattice of the hyperplane of weighted degree 3 the convex hull of A has dimension 4, nine vertices
and seven facets, found by testing every four points of A for a supporting hyperplane in exact integers. Of the 16
monomials of weighted degree 3 the four outside A (a z^2, b z^2, z^3, z m) lie outside the hull, so A is the set of
lattice points of its hull. The vertex z l, the edge from a m to b m and the triangle they span are faces: each is
the intersection of the facets that contain it.

Strata. The column of M at z l spans the line through the origin that is the isolated singular point of A5-504, the
columns at a m and b m span its singular plane (a projective line), and no other column lies on either; the test
evaluates the minimal generators of the two components, held as constants by `e8_component_geometry.py`, on the
columns over Q(i).

Meeting. Singular regenerates the 148 quadrics of the slice, takes the two minimal primes of their ideal with the
script of `e8_component_geometry.py` cut after the sum of the primes, and prints the minimal generators of that sum:
18 linear forms, the linear space of dimension 3 where the degree-11 component meets the scroll (A5-501). The module
holds them as constants; they have rank 18 and vanish on the columns of M at z l, a m and b m, of rank 3, and on no
other column, so the meeting is the image of the triangle.

Tangent cones. Singular computes the toric ideal of A over Q (25 quadrics, dimension 5, multiplicity 11, the
invariants of A5-503) and the multiplicity of X_A at the torus-fixed point of z l (4), at the point of the edge with
both coordinates 1 (2) and at the point of the triangle with all three coordinates 1 (1): the multiplicities of
A5-511 at the three strata. Each comes from a standard basis in a local ordering of the affine chart, whose
dimension 4 is that of X_A. Two controls: the vertex a^3 is a smooth point (1), and the 11 monomials without z l
give a variety of multiplicity 7.

`--check` verifies the polytope, the faces, the strata and the meeting in exact arithmetic, binds the record to its
producers and compares the constants of `e8_component_geometry.py` used here with its retained record.
`--check --replay` reruns Singular and compares the record bit for bit. Without a flag the module writes the record.

Run from the repository root: "$PYTHON" docs/evidence/a5-kernel-attachments/e8_toric_face_strata.py [--check [--replay]]
"""

from __future__ import annotations

import functools
import hashlib
import itertools
import json
import re
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import e8_birational_degree as birational  # noqa: E402
import e8_component_geometry as geometry  # noqa: E402
import weight_slice_fiber_relations as ws  # noqa: E402

import parallel  # noqa: E402

Exponents = birational.Exponents
Gaussian = tuple[int, int]

RECORD = HERE / "e8-toric-face-strata-result.json"
SCHEMA = "gororoba.a5.e8-toric-face-strata/1"
INPUTS = (
    "e8_toric_face_strata.py",
    "e8_birational_degree.py",
    "e8_component_geometry.py",
    "weight_slice_fiber_relations.py",
)
GEOMETRY_RECORD = HERE / "e8-component-geometry-result.json"
ORBITS = birational.ORBITS
MONOMIALS = birational.MONOMIALS
NAMES = ("a^3", "a^2 b", "a b^2", "b^3", "a^2 z", "a b z", "b^2 z", "a l", "b l", "z l", "a m", "b m")
# Indices into MONOMIALS of the three faces: the vertex z l, the edge from a m to b m, the triangle they span.
POINT_FACE: tuple[int, ...] = (9,)
LINE_FACE: tuple[int, ...] = (10, 11)
PLANE_FACE: tuple[int, ...] = (9, 10, 11)
SMOOTH_VERTEX = 0
DROPPED_MONOMIAL = 9

EXPECTED_POLYTOPE: dict[str, Any] = {
    "dimension": 4,
    "points": 12,
    "vertices": ["a^3", "b^3", "a^2 z", "b^2 z", "a l", "b l", "z l", "a m", "b m"],
    "facets": [
        ["a^3", "a^2 b", "a b^2", "b^3", "a^2 z", "a b z", "b^2 z", "a l", "b l", "z l"],
        ["a^3", "a^2 b", "a b^2", "b^3", "a^2 z", "a b z", "b^2 z", "a m", "b m"],
        ["a^3", "a^2 b", "a b^2", "b^3", "a l", "b l", "a m", "b m"],
        ["a^3", "a^2 z", "a l", "z l", "a m"],
        ["b^3", "b^2 z", "b l", "z l", "b m"],
        ["a^2 z", "a b z", "b^2 z", "z l", "a m", "b m"],
        ["a l", "b l", "z l", "a m", "b m"],
    ],
    "monomials_of_the_degree": 16,
    "lattice_points_outside": [],
    "faces": {"point": ["z l"], "line": ["a m", "b m"], "plane": ["z l", "a m", "b m"]},
}
# The local entries are [dimension, multiplicity] of the local ring of the chart at the point.
EXPECTED_TORIC: dict[str, Any] = {
    "generators": 25,
    "generator_degrees": [2],
    "dimension": 5,
    "multiplicity": 11,
    "point": [4, 4],
    "line": [4, 2],
    "plane": [4, 1],
    "controls": {"smooth_vertex": [4, 1], "without_z_l": [5, 7]},
}
EXPECTED_CELL: dict[str, Any] = {
    "point_generators": 20,
    "line_generators": 19,
    "point_face_spans_the_point": True,
    "line_face_spans_the_line": True,
    "plane_face_rank": 3,
    "meeting_generators": 18,
    "plane_face_spans_the_meeting": True,
    "columns_on_the_meeting": ["z l", "a m", "b m"],
    "meeting": [3, 1],
    "meeting_is_linear": True,
    "columns_on_the_point": ["z l"],
    "columns_on_the_line": ["a m", "b m"],
}
# The minimal generators of the sum of the two minimal primes of the quadric ideal, as Singular prints them: the
# linear space where the degree-11 component meets the scroll.
MEETING_GENERATORS: dict[str, str] = {
    "N-": "y(21),y(20),y(18)+(i)*y(19),y(17),y(15)+(i)*y(16),y(13),y(12),y(11)+(i)*y(16),y(10)+y(16),"
    "y(9)+(i)*y(14),y(8),y(7),y(6),y(5),y(4),y(3),y(2),y(1)",
    "N+": "y(21),y(20),y(18)+(-i)*y(19),y(17),y(15)+(-i)*y(16),y(13),y(12),y(11)+(-i)*y(16),y(10)+y(16),"
    "y(9)+(-i)*y(14),y(8),y(7),y(6),y(5),y(4),y(3),y(2),y(1)",
}
# The keys of a cell that the Singular stage of the meeting supplies.
MEETING_KEYS = ("meeting", "meeting_is_linear")
# (dimension of the locus, multiplicity) of A5-511 against the toric keys.
TANGENT_CONES: dict[int, str] = {1: "point", 2: "line", 3: "plane"}

# ---------------------------------------------------------------------------------------------------------------------
# The polytope in exact integers


def _lattice(exponents: Exponents) -> list[int]:
    # The first coordinate has weight 1, so the other four are lattice coordinates on the hyperplane w . e = 3.
    return list(exponents[1:])


def _side(base: list[int], spanning: list[list[int]], point: list[int]) -> int:
    rows = [[x - y for x, y in zip(vertex, base, strict=True)] for vertex in spanning]
    rows.append([x - y for x, y in zip(point, base, strict=True)])
    return birational._determinant(rows)


def degree_monomials() -> list[Exponents]:
    """Every monomial of weighted degree 3 in the five parameters."""
    powers = range(birational.QUOTIENT_DEGREE + 1)
    return [
        exponents
        for exponents in itertools.product(powers, powers, powers, powers, powers)
        if birational.weighted_degree(exponents) == birational.QUOTIENT_DEGREE
    ]


@functools.cache
def facets(monomials: tuple[Exponents, ...]) -> list[tuple[tuple[int, ...], tuple[int, ...], int]]:
    """The facets of the hull as (points on it, four points that span it, sign of the side of the hull)."""
    points = [_lattice(m) for m in monomials]
    found: dict[tuple[int, ...], tuple[tuple[int, ...], int]] = {}
    for spanning in itertools.combinations(range(len(points)), 4):
        base, rest = points[spanning[0]], [points[index] for index in spanning[1:]]
        sides = [_side(base, rest, point) for point in points]
        signs = {side > 0 for side in sides if side != 0}
        if len(signs) != 1:
            continue
        on = tuple(index for index, side in enumerate(sides) if side == 0)
        found.setdefault(on, (spanning, 1 if signs == {True} else -1))
    return [(on, spanning, sign) for on, (spanning, sign) in sorted(found.items())]


def inside(exponents: Exponents, monomials: tuple[Exponents, ...]) -> bool:
    points = [_lattice(m) for m in monomials]
    return all(
        sign * _side(points[spanning[0]], [points[index] for index in spanning[1:]], _lattice(exponents)) >= 0
        for _, spanning, sign in facets(monomials)
    )


def is_face(face: tuple[int, ...], monomials: tuple[Exponents, ...]) -> bool:
    """A set of points of A is a face when it is the intersection of the facets that contain it."""
    containing = [set(on) for on, _, _ in facets(monomials) if set(face) <= set(on)]
    return containing != [] and set.intersection(*containing) == set(face)


def polytope(monomials: tuple[Exponents, ...] = MONOMIALS, names: tuple[str, ...] = NAMES) -> dict[str, Any]:
    points = [_lattice(m) for m in monomials]
    differences = [[(x - y, 0) for x, y in zip(point, points[0], strict=True)] for point in points[1:]]
    found = facets(monomials)
    name = dict(zip(monomials, names, strict=True))
    faces = {"point": POINT_FACE, "line": LINE_FACE, "plane": PLANE_FACE}
    return {
        "dimension": birational.gaussian_rank(differences),
        "points": len(monomials),
        "vertices": [names[index] for index in range(len(monomials)) if is_face((index,), monomials)],
        "facets": [[names[index] for index in on] for on, _, _ in found],
        "monomials_of_the_degree": len(degree_monomials()),
        "lattice_points_outside": [
            name.get(exponents, str(exponents))
            for exponents in degree_monomials()
            if exponents not in monomials and inside(exponents, monomials)
        ],
        "faces": {
            key: [names[index] for index in face] if is_face(face, monomials) else None for key, face in faces.items()
        },
    }


def polytope_problems() -> list[str]:
    found = polytope()
    return [
        f"polytope {key} is {found[key]}, not {expected}"
        for key, expected in EXPECTED_POLYTOPE.items()
        if found[key] != expected
    ]


# ---------------------------------------------------------------------------------------------------------------------
# The images of the faces against the singular strata, over Q(i)

_TERM = re.compile(r"(\(-?i\)\*|-)?y\((\d+)\)")
_COEFFICIENT: dict[str, Gaussian] = {"": (1, 0), "-": (-1, 0), "(i)*": (0, 1), "(-i)*": (0, -1)}


def linear_forms(text: str) -> list[dict[int, Gaussian]]:
    """The linear forms of one generator list of `e8_component_geometry.py`, as generator index -> coefficient."""
    forms: list[dict[int, Gaussian]] = []
    for part in text.split(","):
        form: dict[int, Gaussian] = {}
        for summand in part.split("+"):
            match = _TERM.fullmatch(summand)
            if match is None:
                raise ValueError(f"the summand {summand!r} is not a multiple of a generator by 1, -1, i or -i")
            if int(match.group(2)) in form:
                raise ValueError(f"the summand {summand!r} repeats a generator of its form")
            form[int(match.group(2))] = _COEFFICIENT[match.group(1) or ""]
        forms.append(form)
    return forms


def _times(first: Gaussian, second: Gaussian) -> Gaussian:
    return (first[0] * second[0] - first[1] * second[1], first[0] * second[1] + first[1] * second[0])


def _value(form: dict[int, Gaussian], vector: list[Gaussian]) -> Gaussian:
    total = (0, 0)
    for index, coefficient in form.items():
        product = _times(coefficient, vector[index - 1])
        total = (total[0] + product[0], total[1] + product[1])
    return total


def columns(orbit: str, forms: tuple[birational.Form, ...] | None = None) -> list[list[Gaussian]]:
    """The 12 columns of M: entry k of column j is the coefficient of monomial j in V_k / pl, zero forms included."""
    forms = birational.FIXTURE[orbit] if forms is None else forms
    changed = iter(birational.quotients(forms, birational.SHIFT[orbit]))
    rows = [next(changed) if form else {} for form in forms]
    return [[row.get(monomial, (0, 0)) for row in rows] for monomial in MONOMIALS]


def strata(
    orbit: str,
    generators: tuple[str, ...] | None = None,
    forms: tuple[birational.Form, ...] | None = None,
    meeting_generators: str | None = None,
) -> dict[str, Any]:
    """The faces against the two components of the singular locus and the meeting of one basepoint."""
    texts = geometry.SINGULAR_GENERATORS[orbit] if generators is None else generators
    point, line = (linear_forms(text) for text in texts)
    meeting = linear_forms(MEETING_GENERATORS[orbit] if meeting_generators is None else meeting_generators)
    matrix = columns(orbit, forms)

    def on(ideal: list[dict[int, Gaussian]], index: int) -> bool:
        return all(_value(form, matrix[index]) == (0, 0) for form in ideal)

    def rank(face: tuple[int, ...]) -> int:
        return birational.gaussian_rank([matrix[index] for index in face])

    def independent(ideal: list[dict[int, Gaussian]]) -> bool:
        rows = [[form.get(index, (0, 0)) for index in range(1, birational.GENERATORS + 1)] for form in ideal]
        return birational.gaussian_rank(rows) == len(ideal)

    return {
        "point_generators": len(point),
        "line_generators": len(line),
        # A space cut out by n independent forms in 21 variables that contains r independent vectors with
        # r = 21 - n is their span; the generator counts are those of spaces of dimension 1, 2 and 3.
        "point_face_spans_the_point": independent(point)
        and rank(POINT_FACE) == birational.GENERATORS - len(point)
        and all(on(point, index) for index in POINT_FACE),
        "line_face_spans_the_line": independent(line)
        and rank(LINE_FACE) == birational.GENERATORS - len(line)
        and all(on(line, index) for index in LINE_FACE),
        "plane_face_rank": rank(PLANE_FACE),
        "columns_on_the_point": [NAMES[index] for index in range(len(MONOMIALS)) if on(point, index)],
        "columns_on_the_line": [NAMES[index] for index in range(len(MONOMIALS)) if on(line, index)],
        "meeting_generators": len(meeting),
        "plane_face_spans_the_meeting": independent(meeting)
        and rank(PLANE_FACE) == birational.GENERATORS - len(meeting)
        and all(on(meeting, index) for index in PLANE_FACE),
        "columns_on_the_meeting": [NAMES[index] for index in range(len(MONOMIALS)) if on(meeting, index)],
    }


def strata_problems(orbit: str, found: dict[str, Any] | None = None) -> list[str]:
    found = strata(orbit) if found is None else found
    return [
        f"{orbit}: {key} is {found[key]}, not {expected}"
        for key, expected in EXPECTED_CELL.items()
        if key not in MEETING_KEYS and found[key] != expected
    ]


def exact_problems() -> list[str]:
    """The polytope and the strata of both basepoints; no Singular and no retained record."""
    found = polytope_problems()
    for orbit in ORBITS:
        found += strata_problems(orbit)
    return found


# ---------------------------------------------------------------------------------------------------------------------
# The toric ideal and its local multiplicities in Singular

TORIC_STAGE = """LIB "elim.lib"; option(redSB);
ring R=0,(a,b,l,z,m,y(1..$count)),dp;
ideal mon=$monomials; ideal G; int k;
for(k=1;k<=$count;k++){ G[k]=y(k)-mon[k]; }
ideal E=eliminate(G,a*b*l*z*m);
ring S=0,(y(1..$count)),dp; option(redSB);
ideal J=std(imap(R,E)); ideal B=minbase(J);
intvec degrees; for(k=1;k<=size(B);k++){ degrees[k]=deg(B[k]); }
print("RESULT $key "+string(size(B))+";"+string(degrees)+";"+string(dim(J))+","+string(mult(J)));
$locals
"""
LOCAL_STAGE = """ring L$name=0,(u(1..$others)),ds;
ideal sub$name=$images; map f$name=S,sub$name; ideal I$name=std(f$name(J));
print("RESULT $name "+string(dim(I$name))+","+string(mult(I$name)));
setring S;
"""


def _singular_monomial(exponents: Exponents) -> str:
    return "*".join(f"{name}^{power}" for name, power in zip("ablzm", exponents, strict=True) if power) or "1"


def local_stage(name: str, chart: int, ones: tuple[int, ...], count: int) -> str:
    """The chart where coordinate `chart` is 1, moved so that the point with coordinates 1 at `ones` is the origin."""
    others = [index for index in range(count) if index != chart]
    images = [
        "1" if index == chart else f"u({others.index(index) + 1})" + ("+1" if index in ones else "")
        for index in range(count)
    ]
    return LOCAL_STAGE.replace("$name", name).replace("$others", str(count - 1)).replace("$images", ",".join(images))


def toric_stage(monomials: tuple[Exponents, ...], key: str, local_stages: str) -> str:
    return (
        TORIC_STAGE.replace("$count", str(len(monomials)))
        .replace("$monomials", ",".join(_singular_monomial(m) for m in monomials))
        .replace("$key", key)
        .replace("$locals", local_stages)
        + 'print("RESULT done 1");\nquit;\n'
    )


def _global(text: str) -> tuple[int, list[int], list[int]]:
    count, degrees, invariants = text.split(";")
    return int(count), sorted({int(part) for part in degrees.split(",")}), [int(part) for part in invariants.split(",")]


def toric() -> dict[str, Any]:
    """The toric ideal of A, its three local multiplicities and the two controls."""
    count = len(MONOMIALS)
    local_stages = "".join(
        (
            local_stage("point", POINT_FACE[0], (), count),
            local_stage("line", LINE_FACE[0], LINE_FACE[1:], count),
            local_stage("plane", PLANE_FACE[0], PLANE_FACE[1:], count),
            local_stage("smooth", SMOOTH_VERTEX, (), count),
        )
    )
    values = ws.run_singular(toric_stage(MONOMIALS, "toric", local_stages))["values"]
    without = tuple(m for index, m in enumerate(MONOMIALS) if index != DROPPED_MONOMIAL)
    control = ws.run_singular(toric_stage(without, "toric", ""))["values"]
    generators, degrees, invariants = _global(values["toric"][0])

    def pair(key: str) -> list[int]:
        return [int(part) for part in values[key][0].split(",")]

    return {
        "generators": generators,
        "generator_degrees": degrees,
        "dimension": invariants[0],
        "multiplicity": invariants[1],
        "point": pair("point"),
        "line": pair("line"),
        "plane": pair("plane"),
        "controls": {"smooth_vertex": pair("smooth"), "without_z_l": _global(control["toric"][0])[2]},
    }


MEETING_END = 'print("RESULT scroll_meets_main_is_linear "+string(lin12));'
MEETING_STAGE = """
print("RESULT meeting_generators "+string(mI12));
print("RESULT done 1");
quit;
"""


def meeting_stage(relations: list[str]) -> str:
    """The script of `e8_component_geometry.py` through the sum of the two minimal primes, on the given quadrics."""
    if geometry.SCRIPT.count(MEETING_END) != 1:
        raise RuntimeError("the component-geometry script has no single line that ends the meeting")
    polynomials = ",\n".join(
        "+".join(f"({coefficient})*{'*'.join(f'y({index})' for index in key)}" for key, coefficient in relation)
        for relation in (ws.parse_relation(line) for line in relations)
    )
    head = geometry.SCRIPT.split(MEETING_END)[0] + MEETING_END
    ring = ws._ring(0, 0, f"y(1..{birational.GENERATORS})", "dp")
    return ring + f"\nideal K={polynomials};\n" + head + MEETING_STAGE


def meeting(orbit: str) -> dict[str, Any]:
    """The meeting of the two components of one basepoint, from the regenerated quadrics of the slice."""
    run = ws.run_singular(ws.fiber_script(ws.orbit_task(orbit), "e8", 0, 0))
    values = ws.run_singular(meeting_stage(run["relations"]))["values"]
    return {
        "relations_sha256": ws.summarize_fiber_run(run)["relations_sha256"],
        "meeting": [int(part) for part in values["scroll_meets_main"][0].split(",")],
        "meeting_is_linear": values["scroll_meets_main_is_linear"] == ["1"],
        "meeting_forms": values["meeting_generators"][0],
    }


def certify(orbit: str) -> dict[str, Any]:
    return {
        "orbit": orbit,
        "forms_sha256": birational.fixture_digest(birational.FIXTURE[orbit]),
        **strata(orbit),
        **meeting(orbit),
    }


# ---------------------------------------------------------------------------------------------------------------------
# The record and its checker


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def problems(record: dict[str, Any]) -> list[str]:
    """Every way the record fails the claim; an empty list is a pass."""
    found: list[str] = []
    if record.get("schema") != SCHEMA:
        found.append("schema differs")
    if record.get("fields") != {"toric": "Q", "strata": "Q(i)"}:
        found.append("the fields differ from Q for the toric ideal and Q(i) for the strata")
    if record.get("polytope") != EXPECTED_POLYTOPE:
        found.append(f"polytope differs from {EXPECTED_POLYTOPE}")
    if record.get("toric") != EXPECTED_TORIC:
        found.append(f"toric differs from {EXPECTED_TORIC}")
    cells = record.get("cells", [])
    if [cell.get("orbit") for cell in cells] != list(ORBITS):
        found.append("the cells are not N- and N+ in order")
        return found
    for cell in cells:
        for key, expected in EXPECTED_CELL.items():
            if cell.get(key) != expected:
                found.append(f"{cell['orbit']}: {key} differs from {expected}")
        if cell.get("meeting_forms") != MEETING_GENERATORS[cell["orbit"]]:
            found.append(f"{cell['orbit']}: meeting_forms differs from the generators this module holds")
    if record.get("pass") is not (found == []):
        found.append("the pass flag differs from the verdict")
    return found


def binding_problems(record: dict[str, Any]) -> list[str]:
    """The record against the fixture of the forms: the digest of each basepoint's forms."""
    return [
        f"{cell['orbit']}: forms_sha256 differs from the digest of the fixture"
        for cell in record.get("cells", [])
        if cell.get("forms_sha256") != birational.fixture_digest(birational.FIXTURE[cell["orbit"]])
    ]


def geometry_problems(record: dict[str, Any], retained: dict[str, Any] | None = None) -> list[str]:
    """The constants read from `e8_component_geometry.py` and the multiplicities against its retained record."""
    if retained is None:
        retained = json.loads(GEOMETRY_RECORD.read_text(encoding="utf-8"))
    found: list[str] = []
    cells = {cell["orbit"]: cell for cell in retained.get("cells", [])}
    for orbit in ORBITS:
        cell = cells.get(orbit, {})
        if cell.get("singular_generators") != list(geometry.SINGULAR_GENERATORS[orbit]):
            found.append(f"{orbit}: the singular generators differ from those of the component-geometry record")
        ours = {entry.get("orbit"): entry for entry in record.get("cells", [])}.get(orbit, {})
        if ours.get("relations_sha256") is None or ours.get("relations_sha256") != cell.get("relations_sha256"):
            found.append(f"{orbit}: the quadrics differ from those of the component-geometry record")
        if cell.get("scroll_meets_main") != ours.get("meeting"):
            found.append(f"{orbit}: the meeting differs from that of the component-geometry record")
        cones = {entry[0]: entry[2] for entry in cell.get("tangent_cones", [])}
        for dimension, key in TANGENT_CONES.items():
            if cones.get(dimension) != record.get("toric", {}).get(key, [None, None])[1]:
                found.append(f"{orbit}: the multiplicity at the {key} differs from the component-geometry record")
    return found


def build() -> dict[str, Any]:
    record: dict[str, Any] = {
        "schema": SCHEMA,
        "fields": {"toric": "Q", "strata": "Q(i)"},
        "inputs": {name: _digest(HERE / name) for name in INPUTS},
        "polytope": polytope(),
        "toric": toric(),
        "cells": parallel.ordered_map(certify, list(ORBITS), min_items=2),
        "pass": True,
    }
    record["pass"] = problems(record) == []
    return record


def check(record: dict[str, Any]) -> list[str]:
    found = problems(record) + binding_problems(record) + geometry_problems(record) + exact_problems()
    for name in INPUTS:
        if record.get("inputs", {}).get(name) != _digest(HERE / name):
            found.append(f"input digest of {name} differs")
    return found


def main() -> None:
    arguments = sys.argv[1:]
    if "--check" in arguments:
        record = json.loads(RECORD.read_text(encoding="utf-8"))
        found = check(record)
        if "--replay" in arguments and build() != record:
            found.append("a fresh run differs from the record")
        if found:
            raise SystemExit("\n".join(found))
        print("e8-toric-face-strata-result.json: pass")
        return
    record = build()
    found = problems(record) + binding_problems(record) + geometry_problems(record) + exact_problems()
    record["pass"] = found == []
    RECORD.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"pass": record["pass"], "problems": found}, indent=1))
    if found:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
