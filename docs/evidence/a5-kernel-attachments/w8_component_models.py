"""The two components of the W8 quadric ideal over Q(i) as linear images of two parametrized models.

The quadric ideal K of W8 (144 quadrics on 24 generators, `weight_slice_fiber_relations.py`) is the intersection of
two primes of dimension 6 and degrees 20 and 30 (A5-447). This producer regenerates the quadrics at N- and N+ and
checks in Singular over Q(i) that K equals the intersection of two explicit ideals, each a linear change of
coordinates applied to the kernel of a polynomial map from a domain:

- the model of degree 20 is the kernel of Q[s, w] -> Q[a, c] / (a1 c2 - a2 c1 + a3 c4 - a4 c3) with
  s_pq = a_p a_q (ten coordinates, p <= q in 1..4) and w_pq = a_p c_q - a_q c_p (six coordinates, p < q); it
  equals the ideal of the closure of {(a a^T, a ^ c)} in S^2 C^4 + L^2 C^4 plus the linear form w12 + w34, so
  its variety is that hyperplane section;
- the model of degree 30 is the kernel of Q[s, w, n] -> Q[a1, a2, a4, c, lam, nu] / (a1 c2 - a2 c1 - a4 c3) with
  s_pq = lam a_p a_q (six coordinates, p <= q in {1, 2, 4}), w_pq = a_p c_q - a_q c_p with a3 = 0 for pq in
  13, 14, 23, 24, 12 (five coordinates) and n_pqr = nu a_p a_q a_r (nine coordinates, every cubic monomial in
  a1, a2, a4 except a4^3).

Each target ring is a polynomial ring modulo an irreducible quadric of rank at least 6, a domain over every field
of characteristic 0, so each kernel is prime and stays prime over C. A prime of dimension 6 that contains K and is
one of two incomparable primes with intersection K is a minimal prime of K, so the two images are the two minimal
primes. The maps at N+ are the complex conjugates of the maps at N-.

Run from the repository root: "$PYTHON" docs/evidence/a5-kernel-attachments/w8_component_models.py [--check]
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import weight_slice_fiber_relations as ws  # noqa: E402

import parallel  # noqa: E402

RECORD = HERE / "w8-component-models-result.json"
SCHEMA = "gororoba.a5.w8-component-models/1"
INPUTS = ("w8_component_models.py", "weight_slice_fiber_relations.py")
WEIGHT_SLICE = HERE / "weight-slice-fiber-relations-result.json"
ORBITS = ("N-", "N+")
GENERATORS = 24

# A linear form is a tuple of terms ((real part, imaginary part), generator index) with Gaussian integer
# coefficients; the tables hold the forms at N-, and conjugation gives those at N+.
Term = tuple[tuple[int, int], int]
Form = tuple[Term, ...]

MODEL20_COORDINATES = ("s11", "s12", "s13", "s14", "s22", "s23", "s24", "s33", "s34", "s44") + (
    "w12",
    "w13",
    "w14",
    "w23",
    "w24",
    "w34",
)
MAP20: tuple[Form, ...] = (
    (((1, 0), 4),),
    (((0, 1), 8), ((0, -1), 17)),
    (((1, 0), 5),),
    (((1, 0), 6),),
    (((-4, 0), 20),),
    (((0, 2), 9),),
    (((0, 2), 19),),
    (((0, -2), 7),),
    (((0, -1), 8), ((0, -1), 17)),
    (((0, -2), 18),),
    (((-1, 0), 13),),
    (((0, -1), 10),),
    (((1, 0), 16),),
    (((0, -2), 15),),
    (((0, 2), 22),),
    (((1, 0), 13),),
)
LINEAR20: tuple[Form, ...] = (
    (((1, 0), 24),),
    (((1, 0), 23),),
    (((1, 0), 21), ((0, -1), 22)),
    (((1, 0), 14), ((0, -1), 15)),
    (((1, 0), 12), ((0, -1), 13)),
    (((1, 0), 11), ((0, -1), 16)),
    (((1, 0), 3),),
    (((1, 0), 2),),
    (((1, 0), 1),),
)
MODEL30_COORDINATES = ("s11", "s12", "s14", "s22", "s24", "s44", "w13", "w14", "w23", "w24", "w12") + (
    "n111",
    "n112",
    "n114",
    "n122",
    "n124",
    "n144",
    "n222",
    "n224",
    "n244",
)
MAP30: tuple[Form, ...] = (
    (((1, 0), 4),),
    (((1, 0), 17),),
    (((1, 0), 6),),
    (((1, 0), 20),),
    (((-1, 0), 19),),
    (((0, -2), 18),),
    (((1, 0), 10),),
    (((0, -2), 11),),
    (((1, 0), 14),),
    (((0, 2), 21),),
    (((-1, 0), 12),),
    (((1, 0), 1),),
    (((-1, 0), 3),),
    (((1, 0), 2),),
    (((0, -1), 14), ((-1, 0), 15)),
    (((0, 1), 12), ((1, 0), 13)),
    (((2, 0), 11), ((0, -2), 16)),
    (((-1, 0), 24),),
    (((1, 0), 23),),
    (((-2, 0), 21), ((0, 2), 22)),
)
LINEAR30: tuple[Form, ...] = (
    (((1, 0), 9),),
    (((1, 0), 8), ((1, 0), 17)),
    (((1, 0), 7),),
    (((1, 0), 5),),
)
# Each control replaces one form of one map; the quadric ideal must then leave the altered image.
CONTROLS: dict[str, tuple[int, int, Form]] = {
    "degree 20, s22 rescaled to -3 y20": (20, 4, (((-3, 0), 20),)),
    "degree 20, s34 with the sign of y8 flipped": (20, 8, (((0, 1), 8), ((0, -1), 17))),
    "degree 30, s44 with the opposite sign": (30, 5, (((0, 2), 18),)),
    "degree 30, w14 moved from y11 to y16": (30, 7, (((0, -2), 16),)),
}
# What every cell holds: (dimension, degree, minimal generators) of each model, (dimension, degree) of the closure
# before its hyperplane section and the equality of the section with the degree-20 model, the same pair for K and the
# two images, the rank of the linear forms of each change of coordinates, the two inclusions that make K the
# intersection, the two failed inclusions between the images, and the controls that leave K outside.
EXPECTED: dict[str, Any] = {
    "ideal": [6, 50],
    "model20": [6, 20, 37],
    "unconstrained20": [7, 20],
    "model20_is_hyperplane_section": True,
    "model30": [6, 30, 90],
    "image20": [6, 20],
    "image30": [6, 30],
    "coordinate_rank20": 24,
    "coordinate_rank30": 24,
    "ideal_in_intersection": True,
    "intersection_in_ideal": True,
    "image20_in_image30": False,
    "image30_in_image20": False,
    "controls_rejected": sorted(CONTROLS),
}
MODELS = """LIB "primdec.lib"; option(redSB);
ring A20=0,(a(1..4),c(1..4),s(1..10),w(1..6)),dp;
ideal G=a(1)*c(2)-a(2)*c(1)+a(3)*c(4)-a(4)*c(3); int p; int q; int k=0; int m=0;
for(p=1;p<=4;p++){ for(q=p;q<=4;q++){ k++; G=G,s(k)-a(p)*a(q); } }
for(p=1;p<=4;p++){ for(q=p+1;q<=4;q++){ m++; G=G,w(m)-(a(p)*c(q)-a(q)*c(p)); } }
ideal E=eliminate(G,a(1)*a(2)*a(3)*a(4)*c(1)*c(2)*c(3)*c(4));
ideal G0=G[2..ncols(G)]; ideal E0=eliminate(G0,a(1)*a(2)*a(3)*a(4)*c(1)*c(2)*c(3)*c(4));
ring T20=0,(s(1..10),w(1..6)),dp; ideal M20=std(imap(A20,E));
print("RESULT model20 "+string(dim(M20))+","+string(mult(M20))+","+string(ncols(minbase(M20))));
ideal Z=std(imap(A20,E0)); ideal H=std(Z+ideal(w(1)+w(6)));
print("RESULT unconstrained20 "+string(dim(Z))+","+string(mult(Z)));
print("RESULT model20_is_hyperplane_section "+string(size(reduce(H,M20))+size(reduce(M20,H))==0));
ring A30=0,(a1,a2,a4,c1,c2,c3,c4,lam,nu,s11,s12,s14,s22,s24,s44,w13,w14,w23,w24,w12,
  n111,n112,n114,n122,n124,n144,n222,n224,n244),dp;
ideal G=(a1*c2-a2*c1)-a4*c3, s11-lam*a1*a1, s12-lam*a1*a2, s14-lam*a1*a4, s22-lam*a2*a2, s24-lam*a2*a4,
  s44-lam*a4*a4, w13-(a1*c3), w14-(a1*c4-a4*c1), w23-(a2*c3), w24-(a2*c4-a4*c2), w12-(a1*c2-a2*c1),
  n111-nu*a1^3, n112-nu*a1^2*a2, n114-nu*a1^2*a4, n122-nu*a1*a2^2, n124-nu*a1*a2*a4, n144-nu*a1*a4^2,
  n222-nu*a2^3, n224-nu*a2^2*a4, n244-nu*a2*a4^2;
ideal E=eliminate(G,a1*a2*a4*c1*c2*c3*c4*lam*nu);
ring T30=0,(s11,s12,s14,s22,s24,s44,w13,w14,w23,w24,w12,n111,n112,n114,n122,n124,n144,n222,n224,n244),dp;
ideal M30=std(imap(A30,E));
print("RESULT model30 "+string(dim(M30))+","+string(mult(M30))+","+string(ncols(minbase(M30))));
"""
CHECK = """option(redSB);
proc formrank(ideal F) { matrix D[ncols(F)][nvars(basering)]; int a; int b;
  for(a=1;a<=ncols(F);a++){ for(b=1;b<=nvars(basering);b++){ D[a,b]=diff(F[a],var(b)); } } return(rank(D)); }
ideal sK=std(K); print("RESULT ideal "+string(dim(sK))+","+string(mult(sK)));
map f20=T20,L20; ideal I20=std(f20(M20)+LIN20);
map f30=T30,L30; ideal I30=std(f30(M30)+LIN30);
print("RESULT image20 "+string(dim(I20))+","+string(mult(I20)));
print("RESULT image30 "+string(dim(I30))+","+string(mult(I30)));
print("RESULT coordinate_rank20 "+string(formrank(L20+LIN20)));
print("RESULT coordinate_rank30 "+string(formrank(L30+LIN30)));
ideal X=std(intersect(I20,I30));
print("RESULT ideal_in_intersection "+string(size(reduce(K,X))==0));
print("RESULT intersection_in_ideal "+string(size(reduce(X,sK))==0));
print("RESULT image20_in_image30 "+string(size(reduce(I20,I30))==0));
print("RESULT image30_in_image20 "+string(size(reduce(I30,I20))==0));
"""
CONTROL_STEP = """map g{number}=T{degree},C{number};
print("RESULT control {number},"+string(size(reduce(K,std(g{number}(M{degree})+LIN{degree})))==0));
"""


def conjugate(form: Form) -> Form:
    return tuple(((real, -imaginary), index) for (real, imaginary), index in form)


def forms_at(orbit: str, forms: tuple[Form, ...]) -> tuple[Form, ...]:
    """The forms at the named basepoint: the tables at N-, their complex conjugates at N+."""
    if orbit == "N-":
        return forms
    if orbit == "N+":
        return tuple(conjugate(form) for form in forms)
    raise ValueError(f"unknown basepoint {orbit}")


def render(form: Form) -> str:
    """A linear form in Singular syntax over Q(i)."""
    return "+".join(f"({real}{imaginary:+d}*i)*y({index})" for (real, imaginary), index in form)


def _ideal(name: str, forms: tuple[Form, ...]) -> str:
    return f"ideal {name}={','.join(render(form) for form in forms)};\n"


def control_script(orbit: str) -> str:
    """One altered map per control, in the sorted order of the control names."""
    tables = {20: MAP20, 30: MAP30}
    text = ""
    for number, name in enumerate(sorted(CONTROLS), start=1):
        degree, position, replacement = CONTROLS[name]
        altered = list(tables[degree])
        altered[position] = replacement
        text += _ideal(f"C{number}", forms_at(orbit, tuple(altered)))
        text += CONTROL_STEP.format(number=number, degree=degree)
    return text


def _pair(text: str) -> list[int]:
    return [int(part) for part in text.split(",")]


def certify(orbit: str) -> dict[str, Any]:
    run = ws.run_singular(ws.fiber_script(ws.orbit_task(orbit), "w8", 0, 0))
    polynomials = ",\n".join(
        "+".join(f"({coefficient})*{'*'.join(f'y({index})' for index in key)}" for key, coefficient in relation)
        for relation in (ws.parse_relation(line) for line in run["relations"])
    )
    script = (
        MODELS
        + ws._ring(0, 0, f"y(1..{GENERATORS})", "dp")
        + f"\nideal K={polynomials};\n"
        + _ideal("L20", forms_at(orbit, MAP20))
        + _ideal("LIN20", forms_at(orbit, LINEAR20))
        + _ideal("L30", forms_at(orbit, MAP30))
        + _ideal("LIN30", forms_at(orbit, LINEAR30))
        + CHECK
        + control_script(orbit)
        + 'print("RESULT done 1");\nquit;\n'
    )
    values = ws.run_singular(script)["values"]
    inside: dict[int, int] = {}
    for text in values["control"]:
        number, contained = _pair(text)
        inside[number] = contained
    names = sorted(CONTROLS)
    return {
        "orbit": orbit,
        "relations_sha256": ws.summarize_fiber_run(run)["relations_sha256"],
        "ideal": _pair(values["ideal"][0]),
        "model20": _pair(values["model20"][0]),
        "unconstrained20": _pair(values["unconstrained20"][0]),
        "model20_is_hyperplane_section": values["model20_is_hyperplane_section"] == ["1"],
        "model30": _pair(values["model30"][0]),
        "image20": _pair(values["image20"][0]),
        "image30": _pair(values["image30"][0]),
        "coordinate_rank20": int(values["coordinate_rank20"][0]),
        "coordinate_rank30": int(values["coordinate_rank30"][0]),
        "ideal_in_intersection": values["ideal_in_intersection"] == ["1"],
        "intersection_in_ideal": values["intersection_in_ideal"] == ["1"],
        "image20_in_image30": values["image20_in_image30"] == ["1"],
        "image30_in_image20": values["image30_in_image20"] == ["1"],
        "controls_rejected": [name for number, name in enumerate(names, start=1) if inside.get(number) == 0],
        "map20": dict(zip(MODEL20_COORDINATES, map(render, forms_at(orbit, MAP20)), strict=True)),
        "linear_forms20": [render(form) for form in forms_at(orbit, LINEAR20)],
        "map30": dict(zip(MODEL30_COORDINATES, map(render, forms_at(orbit, MAP30)), strict=True)),
        "linear_forms30": [render(form) for form in forms_at(orbit, LINEAR30)],
    }


def _map_problems(cell: dict[str, Any]) -> list[str]:
    """The recorded maps against the tables of this producer at the cell's basepoint."""
    orbit = cell["orbit"]
    expected: dict[str, Any] = {
        "map20": dict(zip(MODEL20_COORDINATES, map(render, forms_at(orbit, MAP20)), strict=True)),
        "linear_forms20": [render(form) for form in forms_at(orbit, LINEAR20)],
        "map30": dict(zip(MODEL30_COORDINATES, map(render, forms_at(orbit, MAP30)), strict=True)),
        "linear_forms30": [render(form) for form in forms_at(orbit, LINEAR30)],
    }
    return [
        f"{orbit}: {key} differs from the producer's table" for key, value in expected.items() if cell.get(key) != value
    ]


def problems(record: dict[str, Any]) -> list[str]:
    """Every way the record fails the claim; an empty list is a pass."""
    found: list[str] = []
    if record.get("schema") != SCHEMA:
        found.append("schema differs")
    if record.get("field") != "Q(i)":
        found.append("the field differs from Q(i)")
    cells = record.get("cells", [])
    if [cell.get("orbit") for cell in cells] != list(ORBITS):
        found.append("the cells are not N- and N+ in order")
        return found
    for cell in cells:
        for key, expected in EXPECTED.items():
            if cell.get(key) != expected:
                found.append(f"{cell['orbit']}: {key} differs from {expected}")
        found += _map_problems(cell)
    if record.get("pass") is not (found == []):
        found.append("the pass flag differs from the verdict")
    return found


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def slice_problems(record: dict[str, Any]) -> list[str]:
    """The relation digests against the W8 cells over Q(i) of the weight-slice record."""
    retained = {
        cell["orbit"]: cell["relations_sha256"]
        for cell in json.loads(WEIGHT_SLICE.read_text(encoding="utf-8"))["cells"]
        if cell["characteristic"] == 0 and cell["source"] == "w8"
    }
    return [
        f"{cell['orbit']}: the relations differ from those of the weight-slice record"
        for cell in record.get("cells", [])
        if cell.get("relations_sha256") != retained.get(cell["orbit"])
    ]


def build() -> dict[str, Any]:
    record: dict[str, Any] = {
        "schema": SCHEMA,
        "field": "Q(i)",
        "inputs": {name: _digest(HERE / name) for name in INPUTS},
        "weight_slice_record_sha256": _digest(WEIGHT_SLICE),
        "cells": parallel.ordered_map(certify, list(ORBITS), min_items=2),
        "pass": True,
    }
    record["pass"] = problems(record) == []
    return record


def main() -> None:
    if "--check" in sys.argv[1:]:
        record = json.loads(RECORD.read_text(encoding="utf-8"))
        found = problems(record) + slice_problems(record)
        for name in INPUTS:
            if record["inputs"].get(name) != _digest(HERE / name):
                found.append(f"input digest of {name} differs")
        if record.get("weight_slice_record_sha256") != _digest(WEIGHT_SLICE):
            found.append("digest of the weight-slice record differs")
        if found:
            raise SystemExit("\n".join(found))
        print("w8-component-models-result.json: pass")
        return
    record = build()
    found = problems(record) + slice_problems(record)
    RECORD.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"pass": record["pass"], "problems": found}, indent=1))
    if found:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
