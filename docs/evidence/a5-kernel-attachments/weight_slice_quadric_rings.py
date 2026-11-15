"""Cohen-Macaulay and reducedness of the quadric rings Q(i)[y]/K on the weight slice (the test of A5-548 over Q(i)).

Ledger row A5-548 states the hypothesis that a quadric ring k[y]/K of the fiber track is Cohen-Macaulay exactly when
K is radical. Its falsifier is a reduced ring that is not Cohen-Macaulay, or a Cohen-Macaulay ring that is not
reduced. This program decides both properties over Q(i) for the eight cells with relations at the N+ and N-
basepoints (same-sign X, Iso, W8, E8-bar), on the degree-2 relations that `weight_slice_fiber_relations.py`
regenerates and A5-474 places inside the relation ideal. Each cell's relation digest must equal the one the retained
weight-slice record binds.

- Cohen-Macaulay: for A = Q(i)[y]/K of Krull dimension a and degree e, linear forms l_1, ..., l_a with
  dim A/(l) = 0 are a system of parameters, and A is Cohen-Macaulay exactly when the Artinian quotient has length e
  (every system of parameters of a Cohen-Macaulay ring is regular; a length above e proves A not Cohen-Macaulay).
  The forms are chosen greedily from a fixed list of sparse forms (the variables, then y_j + y_l, y_j - y_l,
  y_j + 2 y_l, then y_j + y_l + y_m and y_j + 2 y_l + 3 y_m, then two dense forms with coefficients 1 to 5): a
  candidate is kept when it lowers the dimension by one. The computed dimension 0 is what makes them a system of
  parameters. Sparse forms keep the Q(i) coefficients small: on X- -> N- the dense forms with coefficients near
  32003 left one Singular call running past 3600 s, and the sparse forms decide the cell in seconds.
- Reduced, for a Cohen-Macaulay ring: l_1, ..., l_a is then a regular sequence, A_1 = A/(l_1, ..., l_{a-1}) is
  Cohen-Macaulay of dimension 1 and every point of Proj A_1 lies in the chart l_a = 1. When the chart ideal Z is
  radical of length e, Proj A_1 is reduced, A_1 has no embedded prime, so A_1 is reduced, and a graded ring with a
  homogeneous nonzerodivisor of positive degree and reduced quotient is reduced. A chart that is not radical decides
  nothing for one choice of forms, and the radical probe then decides the ring.
- Radical probe, on every ring the chart leaves undecided (each ring the Cohen-Macaulay test rejects, and a
  Cohen-Macaulay ring whose chart is not radical): R = rad K. R = K decides the ring reduced; a generator of R
  outside K decides it not reduced. The linear part of R and whether its square lies in K are recorded.

The probes follow the computed values and never the predicted ones. Four calibration ideals with known answers run
first in every run, one for each pair of answers: the twisted cubic (Cohen-Macaulay, reduced), the double plane
y1^2 (Cohen-Macaulay, not reduced), two planes meeting in a point (reduced, not Cohen-Macaulay) and (y1^2, y1 y2)
(neither). The program exits 1 when a calibration answer departs, a cell stays undecided, a cell falsifies the
hypothesis or a relation digest differs from the retained record.

Usage, from the repository root: "$PYTHON" docs/evidence/a5-kernel-attachments/weight_slice_quadric_rings.py
--out OUT.json [--steps DIR] [--cells xm:N-,iso:N-]; `--steps DIR` keeps each finished step as one JSON file and
reads it back on a rerun, so an interrupted run resumes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import weight_slice_fiber_relations as ws  # noqa: E402

SCHEMA = "gororoba.a5.weight-slice-quadric-rings/1"
WEIGHT_SLICE = HERE / "weight-slice-fiber-relations-result.json"
# (source, orbit): the cells of the weight-slice record that carry degree-2 relations.
CELLS: tuple[tuple[str, str], ...] = (
    ("xm", "N-"),
    ("xp", "N+"),
    ("iso", "N-"),
    ("iso", "N+"),
    ("w8", "N-"),
    ("w8", "N+"),
    ("e8", "N-"),
    ("e8", "N+"),
)
# name -> (variables, generators, Cohen-Macaulay, reduced)
CALIBRATION: dict[str, tuple[int, tuple[str, ...], bool, bool]] = {
    "twisted cubic": (4, ("y(1)*y(3)-y(2)^2", "y(1)*y(4)-y(2)*y(3)", "y(2)*y(4)-y(3)^2"), True, True),
    "double plane": (3, ("y(1)^2",), True, False),
    "two planes meeting in a point": (4, ("y(1)*y(3)", "y(1)*y(4)", "y(2)*y(3)", "y(2)*y(4)"), False, True),
    "line with an embedded point": (2, ("y(1)^2", "y(1)*y(2)"), False, False),
}

HEAD = """LIB "primdec.lib";
ring r=(0,i),(y(1..{n})),dp; minpoly=i^2+1;
ideal K=
{polynomials};
ideal sK=std(K); int a=dim(sK); int e=mult(sK);
"""

CM_SCRIPT = (
    HEAD
    + """ideal Lf; int d=a; int j; int l; int m; int k; int nv=nvars(r); ideal T; poly s; list C;
for(j=1;j<=nv;j++){{ C=insert(C,var(j),size(C)); }}
for(j=1;j<=nv;j++){{ for(l=j+1;l<=nv;l++){{
  C=insert(C,var(j)+var(l),size(C)); C=insert(C,var(j)-var(l),size(C)); C=insert(C,var(j)+2*var(l),size(C)); }}}}
for(j=1;j<=nv;j++){{ for(l=j+1;l<=nv;l++){{ for(m=l+1;m<=nv;m++){{
  C=insert(C,var(j)+var(l)+var(m),size(C)); C=insert(C,var(j)+2*var(l)+3*var(m),size(C)); }}}}}}
s=0; for(j=1;j<=nv;j++){{ s=s+((j mod 3)+1)*var(j); }} C=insert(C,s,size(C));
s=0; for(j=1;j<=nv;j++){{ s=s+((j*j mod 5)+1)*var(j); }} C=insert(C,s,size(C));
for(j=1;j<=size(C) && d>0;j++){{ T=std(sK+Lf+ideal(C[j])); if(dim(T)==d-1){{ Lf=Lf+ideal(C[j]); d=d-1; }} }}
print("RESULT forms "+string(Lf));
ideal Q=std(sK+Lf);
print("RESULT cm "+string(a)+" "+string(e)+" "+string(dim(Q))+" "+string(vdim(Q)));
ideal L1; for(k=1;k<a;k++){{ L1[k]=Lf[k]; }}
ideal Z=std(sK+L1+ideal(Lf[a]-1));
ideal RZ=std(radical(Z));
print("RESULT chart "+string(dim(Z))+" "+string(vdim(Z))+" "+string(vdim(RZ)));
print("RESULT done 1");
quit;
"""
)

RADICAL_SCRIPT = (
    HEAD
    + """ideal R=std(radical(sK)); ideal N=simplify(jet(R,1),2);
print("RESULT radical_equal "+string(size(reduce(R,sK))==0));
print("RESULT linear "+string(size(N))+" "+string(size(reduce(N*N,sK))==0)+" "+string(size(reduce(N,sK))==size(N)));
print("RESULT radical "+string(dim(R))+" "+string(mult(R)));
print("RESULT done 1");
quit;
"""
)


def polynomials(lines: list[str]) -> list[str]:
    """The relation lines of the producer as polynomials in y(1), ..., y(g)."""
    found = []
    for line in lines:
        terms = [
            f"({coefficient})*{'*'.join(f'y({index})' for index in key)}"
            for key, coefficient in ws.parse_relation(line)
        ]
        found.append("+".join(terms))
    return found


def cm_row(values: dict[str, list[str]]) -> dict[str, Any]:
    a, e, section_dim, length = (int(token) for token in values["cm"][0].split())
    chart_dim, chart_length, chart_radical_length = (int(token) for token in values["chart"][0].split())
    if section_dim != 0:
        raise RuntimeError(f"the linear forms are not a system of parameters (dimension {section_dim})")
    if length < e:
        raise RuntimeError(f"the Artinian length {length} is below the degree {e}")
    return {
        "krull_dim": a,
        "degree": e,
        "length": length,
        "cohen_macaulay": length == e,
        "parameter_forms": values["forms"][0],
        "chart": {"dim": chart_dim, "length": chart_length, "radical_length": chart_radical_length},
    }


def radical_row(values: dict[str, list[str]]) -> dict[str, Any]:
    count, square_in_k, outside_k = values["linear"][0].split()
    dimension, degree = (int(token) for token in values["radical"][0].split())
    return {
        "radical_equal": values["radical_equal"][0] == "1",
        "linear_forms": int(count),
        "linear_square_in_K": square_in_k == "1",
        "linear_outside_K": outside_k == "1",
        "radical_dim": dimension,
        "radical_degree": degree,
    }


def chart_decides(cm: dict[str, Any]) -> bool:
    """The chart certificate: only for a Cohen-Macaulay ring, and only when the chart is radical of length e."""
    chart = cm["chart"]
    return bool(
        cm["cohen_macaulay"]
        and chart["dim"] == 0
        and chart["length"] == cm["degree"]
        and chart["radical_length"] == cm["degree"]
    )


def verdict(cm: dict[str, Any], radical: dict[str, Any] | None) -> dict[str, Any]:
    """Reducedness and the hypothesis for one ring; `reduced` is None while no certificate decides it."""
    reduced: bool | None = None
    basis = "undecided"
    if chart_decides(cm):
        reduced, basis = True, "Cohen-Macaulay with a radical chart of length e"
    elif radical is not None:
        reduced = radical["radical_equal"]
        basis = "rad K = K" if reduced else "rad K contains an element outside K"
    holds = None if reduced is None else cm["cohen_macaulay"] == reduced
    return {"reduced": reduced, "reduced_basis": basis, "hypothesis_holds": holds}


def decide(name: str, n: int, polys: list[str], steps: Path | None) -> dict[str, Any]:
    """Both steps of one ring; a finished step is written before the next starts and read back on a rerun."""
    text = ",\n".join(polys)
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()

    def step(kind: str, template: str) -> dict[str, Any] | None:
        path = None if steps is None else steps / f"{name.replace(' ', '_').replace('>', '')}.{kind}.json"
        script = template.format(n=n, polynomials=text)
        script_digest = hashlib.sha256(script.encode("utf-8")).hexdigest()
        if path is not None and path.is_file():
            kept = json.loads(path.read_text(encoding="utf-8"))
            if kept.get("script_sha256") == script_digest:
                return dict(kept)
        started, load = time.monotonic(), os.getloadavg()[0]
        try:
            values = ws.run_singular(script)["values"]
        except RuntimeError as error:
            # The producer raises RuntimeError past its time limit; the ring then stays undecided.
            if "exceeded" not in str(error):
                raise
            return None
        row = {
            "ideal_sha256": digest,
            "script_sha256": script_digest,
            "values": values,
            "seconds": round(time.monotonic() - started, 1),
            "load_1min": load,
        }
        if path is not None:
            path.write_text(json.dumps(row, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        return row

    first = step("cm", CM_SCRIPT)
    if first is None:
        return {"ring": name, "variables": n, "generators": len(polys), "krull_dim": None, "degree": None,
                "length": None, "cohen_macaulay": None, "chart": None, "radical": None, "reduced": None,
                "reduced_basis": "undecided: the Cohen-Macaulay step reached the Singular time limit",
                "hypothesis_holds": None, "measurements": {}}  # fmt: skip
    cm = cm_row(first["values"])
    measurements = {"cm": {"seconds": first["seconds"], "load_1min": first["load_1min"]}}
    radical = None
    if not chart_decides(cm):
        second = step("radical", RADICAL_SCRIPT)
        if second is not None:
            radical = radical_row(second["values"])
            measurements["radical"] = {"seconds": second["seconds"], "load_1min": second["load_1min"]}
    return {"ring": name, "variables": n, "generators": len(polys), **cm, "radical": radical, **verdict(cm, radical),
            "measurements": measurements}  # fmt: skip


def calibration(steps: Path | None) -> list[dict[str, Any]]:
    rows = []
    for name, (n, polys, cm_known, reduced_known) in CALIBRATION.items():
        row = decide(name, n, list(polys), steps)
        row |= {"known_cohen_macaulay": cm_known, "known_reduced": reduced_known}
        row["reproduced"] = row["cohen_macaulay"] is cm_known and row["reduced"] is reduced_known
        rows.append(row)
    return rows


def cell(source: str, orbit: str, retained: dict[str, str], steps: Path | None) -> dict[str, Any]:
    name = ws.incidence_name(orbit, source)
    run = ws.run_singular(ws.fiber_script(ws.orbit_task(orbit), source, 0, 0))
    summary = ws.summarize_fiber_run(run)
    row = decide(name, summary["generator_count"], polynomials(sorted(run["relations"])), steps)
    row |= {
        "relations_sha256": summary["relations_sha256"],
        "relations_match_retained": summary["relations_sha256"] == retained.get(name),
    }
    return row


def problems(record: dict[str, Any]) -> list[str]:
    found = [f"calibration: {row['ring']} gives {row['cohen_macaulay']}, {row['reduced']}"
             for row in record["calibration"] if not row["reproduced"]]  # fmt: skip
    for row in record["cells"]:
        if not row["relations_match_retained"]:
            found.append(f"{row['ring']}: the relations differ from the retained weight-slice record")
        if row["hypothesis_holds"] is None:
            found.append(f"{row['ring']}: reducedness is undecided")
        elif not row["hypothesis_holds"]:
            found.append(f"{row['ring']}: Cohen-Macaulay {row['cohen_macaulay']}, reduced {row['reduced']}")
    return found


def comparable(record: dict[str, Any]) -> dict[str, Any]:
    """The record without its timings and load readings."""
    kept = json.loads(json.dumps(record))
    for row in kept["calibration"] + kept["cells"]:
        row.pop("measurements", None)
    return dict(kept)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, required=True, help="write the JSON record")
    parser.add_argument("--steps", type=Path, help="directory of per-step results, written as each step ends")
    parser.add_argument("--cells", help="comma-separated source:orbit pairs (default: all eight)")
    parser.add_argument("--check", type=Path, help="compare the computed record with this retained one")
    args = parser.parse_args()
    if args.steps is not None:
        args.steps.mkdir(parents=True, exist_ok=True)
    wanted = None if args.cells is None else {tuple(item.split(":")) for item in args.cells.split(",")}
    chosen = tuple(pair for pair in CELLS if wanted is None or pair in wanted)
    if wanted is not None and len(chosen) != len(wanted):
        raise SystemExit(f"unknown cell in {args.cells}")
    retained = {
        item["incidence"]: item["relations_sha256"]
        for item in json.loads(WEIGHT_SLICE.read_text(encoding="utf-8"))["cells"]
        if item["characteristic"] == 0
    }
    banner, version = ws.singular_version()
    record: dict[str, Any] = {
        "schema": SCHEMA,
        "field": "Q(i)",
        "tools": {"singular": banner, "singular_version": version},
        "calibration": calibration(args.steps),
        "cells": [],
    }
    calibrated = all(row["reproduced"] for row in record["calibration"])
    if calibrated:
        record["cells"] = [cell(source, orbit, retained, args.steps) for source, orbit in chosen]
    record["problems"] = problems(record)
    record["complete"] = calibrated and len(record["cells"]) == len(CELLS)
    record["hypothesis_holds_on_every_cell"] = calibrated and record["problems"] == []
    args.out.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    for row in record["calibration"] + record["cells"]:
        print(row["ring"], row["krull_dim"], row["degree"], row["length"], row["cohen_macaulay"], row["reduced"])
    for line in record["problems"]:
        print("PROBLEM", line, file=sys.stderr)
    if args.check is not None:
        kept = json.loads(args.check.read_text(encoding="utf-8"))
        if comparable(kept) != comparable(record):
            print("PROBLEM the computed record differs from the retained one", file=sys.stderr)
            return 1
    return 0 if record["problems"] == [] else 1


if __name__ == "__main__":
    sys.exit(main())
