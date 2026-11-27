"""The linear map that the slice change induces between the two presentations of the fiber cone of same-sign X.

For X- -> N- and X+ -> N+ the header slice (nullity16_basepoints) and the weight slice (weight_slice_fiber_relations)
each take 15 generators among the 126 principal 4-Pfaffians of a Schur form of C(z). The construction is the one of
"../e8-induced-slice-map/induced_slice_map.py" (ledger row A5-598) with the closure equations of X in place of those
of E8-bar: the header frame's 15 selected Pfaffians, restricted to the weight slice, are written as constant
combinations of the 15 weight-slice generators modulo J + m I over Q(i), in k[s1..s9, v] / (v u - 1) with u the
product of the two pivot Pfaffians on the weight-zero axis. The Singular stages, the header frame and the readers are
imported from that module, whose bytes its own digest list binds; this module holds the parts that name the source.

--emit SOURCE CHAR ROOT [map|relations|high] writes a Singular script (SOURCE xm or xp, CHAR 0 for Q(i));
--collect MAP_LOG RELATION_LOG SOURCE OUT.json reads the outputs;
--check OUT.json PRIME ROOT HEADER_REL writes to stdout a Singular script that reduces the Q(i) record at (PRIME, ROOT)
and compares the transported ideal with a retained header relation file;
--run writes and runs every script of the retained record in this directory: the six Q(i) scripts, then the six
reductions and the six reductions at the other root of -1, each stage through parallel.ordered_map.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "e8-induced-slice-map"))

import induced_slice_map as base  # noqa: E402

FIBERS = HERE.parents[2]
# Source key of the weight-slice producer -> the basepoint of its same-sign incidence.
SOURCES = {"xm": "N-", "xp": "N+"}
MODES = ("map", "relations", "high")
# (prime, the root of -1 of the header files at that prime); the other root is the control.
ROOTS = ((32009, 10754), (32029, 9115), (32057, 8059))
# The retained header relation files of same-sign X, under a5-exceptional-fibers/.
HEADERS = {
    ("xm", 32009): "working/distribute/out/a5-xm-d4/xm_p1/d2/relations-upto-d2.rel",
    ("xm", 32029): "working/distribute/out/a5-p2-small/xm_p2/d2/relations-upto-d2.rel",
    ("xm", 32057): "third-prime/relations/xm-nm/d2/relations-upto-d2.rel",
    ("xp", 32009): "working/distribute/out/a5-xp-p1-d2/xp_p1/d2/relations-upto-d2.rel",
    ("xp", 32029): "working/distribute/out/a5-p2-small/xp_p2/d2/relations-upto-d2.rel",
    ("xp", 32057): "third-prime/relations/xp-np/d2/relations-upto-d2.rel",
}
REMAINDERS = re.compile(r"^RESULT transported modulo header (\d+) header modulo transported (\d+)$")


def incidence(source: str) -> str:
    import weight_slice_fiber_relations as ws

    return ws.incidence_name(SOURCES[source], source)


def counts(source: str) -> tuple[int, int]:
    """(generators, quadrics) of the cell, from the table of the weight-slice producer."""
    import weight_slice_fiber_relations as ws

    return ws.EXPECTED_COUNTS[(SOURCES[source], source)]


def cone(source: str) -> tuple[int, int]:
    """(affine dimension, multiplicity) of the quadric ring, from the retained nullity-8 import record."""
    import weight_slice_fiber_relations as ws

    fiber = ws.retained_fibers()[incidence(source)]
    base._require(
        (fiber["generators"], fiber["quadrics"]) == counts(source), "the import record and the count table disagree"
    )
    return fiber["projective_dimension"] + 1, fiber["degree"]


def header_selected(source: str) -> list[int]:
    rows = json.loads(base.REES_RECORD.read_text(encoding="utf-8"))["incidences"]
    found = [row for row in rows if row["incidence"] == incidence(source) and base.HEADER_SELECTED_KEY in row]
    base._require(len(found) == 1, f"no single header selection for {incidence(source)}")
    selected = [int(value) for value in found[0][base.HEADER_SELECTED_KEY]]
    base._require(len(selected) == counts(source)[0], "the header record does not list the generators of the cell")
    return selected


def emit(source: str, characteristic: int, root: int, mode: str = "map") -> str:
    """mode map: the induced map; relations: the weight-slice producer's own script; high: the map script stopped
    after a membership test of the high-weight components of the header Pfaffians."""
    import weight_slice_fiber_relations as ws

    piece = ws.orbit_task(SOURCES[source])
    base._require(mode in ("map", "relations", "high"), f"unknown mode {mode}")
    if mode == "relations":
        return ws.fiber_script(piece, source, characteristic, root)
    positive = tuple(position + 1 for position, weight in enumerate(piece.grading) if weight > 0)
    base._require(positive == base.POSITIVE, "the weight-zero axis is not s2")
    _pivot, frame = base.header_frame(piece.boundary_point)
    entries = "\n".join(
        f"FH[{row + 1},{column + 1}]={base._gaussian_text(frame[row][column])};"
        for row in range(15)
        for column in range(15)
        if frame[row][column] != (0, 0)
    )
    axis = "\n".join(f"pBH0=subst(pBH0,s{k},0); pBW0=subst(pBW0,s{k},0);" for k in positive)
    quadruples = list(itertools.combinations(range(1, 10), 4))
    pfaffians = "\n".join(
        "hq++; HP[hq]=reduce(pf4(NHm,{},{},{},{}),J);".format(*quadruples[index - 1])
        for index in header_selected(source)
    )
    grading = piece.grading
    ordering = ",".join(str(max(weight, 1)) for weight in grading) + ",1"
    variables = ",".join(f"s{position}" for position in range(1, 10)) + ",v"
    stage = ws.PFAFFIAN_STAGE.replace(
        "ideal m=maxideal(1);", "ideal m=" + ",".join(f"s{k}" for k in range(1, 10)) + ";"
    )
    base._require("ideal m=s1" in stage, "the maximal ideal line of the Pfaffian stage changed")
    return ws.SCRIPT.substitute(
        ring=ws._ring(characteristic, root, variables, f"wp({ordering})"),
        matrix_lines=piece.matrix_lines + "\n" + base.FRAME_LINES.substitute(entries=entries, axis=axis),
        weights=",".join(str(weight) for weight in grading),
        procedures=ws.PROCEDURES,
        equations=",".join(piece.equations[source]),
        component_step=ws.COMPONENT_STEP + "J=std(J+ideal(v*u0-1));\n",
        pfaffian_stage=stage,
        tail=ws.SELECTION_STAGE
        + base.HEADER_TAIL.substitute(header_pfaffians=pfaffians, high_test=base.HIGH_TEST if mode == "high" else ""),
    )


def collect(log: Path, relation_log: Path, source: str) -> dict[str, Any]:
    generators, quadrics = counts(source)
    values, lines = base._read(log)
    relation_values, relation_lines = base._read(relation_log)
    rows = [line.removeprefix("MAPROW ").split(" ") for line in lines if line.startswith("MAPROW ")]
    relations = sorted(line for line in relation_lines if line.startswith("RELATION "))
    retained = json.loads(base.WEIGHT_RECORD.read_text(encoding="utf-8"))
    cell = next(
        cell for cell in retained["cells"] if cell["incidence"] == incidence(source) and cell["field"] == "Q(i)"
    )
    record = {
        "schema": "a5-x-induced-slice-map-v1",
        "source": source,
        "incidence": incidence(source),
        "values": {key: value for key, value in values.items() if key != "component"},
        "selected_weight": [int(token) for token in values["selected"][0].split(",")],
        "selected_weight_retained": cell["selected_pfaffians_one_based"],
        "selected_header": header_selected(source),
        "map": rows,
        "relations": relations,
        "relations_sha256": hashlib.sha256(("\n".join(relations) + "\n").encode("utf-8")).hexdigest(),
        "relations_sha256_retained": cell["relations_sha256"],
    }
    problems: list[str] = []
    expected = {
        "header_adjugate_identity": "1",
        "weight_pivot_square": "1",
        "weight_pivot_on_axis": "1",
        "pivot_units_at_origin": "1 1",
        "coefficient_split": "0",
        "header_outside_span": "0",
        "lift_residual": "0",
        "lift_shape": f"{generators} {generators} 0",
        "lift_determinant_nonzero": "1",
        "generators": str(generators),
    }
    if relation_values.get("relations") != [str(quadrics)] or relation_values.get("selected") != values.get("selected"):
        problems.append("the relation run differs from the map run in selection or relation count")
    for key, value in expected.items():
        if values.get(key) != [value]:
            problems.append(f"{key} reads {values.get(key)}, expected {value}")
    if values.get("control_nonmember_residual") in (None, ["0"]):
        problems.append("the non-member control was accepted")
    if record["selected_weight"] != record["selected_weight_retained"]:
        problems.append("the weight-slice selection differs from the retained record")
    if record["relations_sha256"] != record["relations_sha256_retained"]:
        problems.append("the weight-slice relation digest differs from the retained record")
    if len(rows) != generators or any(len(row) != generators for row in rows):
        problems.append(f"the map is not {generators} x {generators}")
    record["problems"] = problems
    record["pass"] = problems == []
    return record


def check_script(record: dict[str, Any], prime: int, root: int, header_rel: Path) -> str:
    import weight_slice_fiber_relations as ws

    source = record["source"]
    generators, quadrics = counts(source)
    dimension, multiplicity = cone(source)
    base._require(pow(root, 2, prime) == prime - 1, "the root is not a square root of -1")
    polynomials = [
        "+".join(
            f"{base._reduce(coefficient, prime, root)}*y({key[0]})*y({key[1]})"
            for key, coefficient in ws.parse_relation(line)
        )
        for line in record["relations"]
    ]
    images = [
        "+".join(f"{base._reduce(entry, prime, root)}*y({column + 1})" for column, entry in enumerate(row))
        for row in record["map"]
    ]
    header = header_rel.read_text(encoding="utf-8").strip()
    if header.startswith("ideal"):
        header = header.split("=", 1)[1].rstrip().rstrip(";")
    lines = [
        f"ring r={prime},(y(1..{generators})),dp; option(redSB);",
        "ideal KW=" + ",\n".join(polynomials) + ";",
        "ideal KH=" + header.rstrip(",") + ";",
        "map f=r," + ",\n".join(images) + ";",
        "ideal mx=maxideal(1); ideal img=f(mx); matrix Jf=jacob(img); poly dt=det(Jf);",
        "ideal fK=f(KW); ideal sF=std(fK); ideal sH=std(KH); ideal sW=std(KW);",
        "int a1=size(reduce(fK,sH)); int a2=size(reduce(KH,sF));",
        "int c1=size(reduce(KW,sH)); int c2=size(reduce(KH,sW));",
        "ideal img2=img; img2[1]=img2[1]+y(1); map g=r,img2; ideal gK=g(KW); ideal sG=std(gK);",
        "int d1=size(reduce(gK,sH)); int d2=size(reduce(KH,sG));",
        "ideal swp=mx; swp[1]=y(2); swp[2]=y(1); map sw=r,swp; ideal wK=sw(fK); ideal sS=std(wK);",
        "int s1=size(reduce(wK,sH)); int s2=size(reduce(KH,sS));",
        '"RESULT transported modulo header",a1,"header modulo transported",a2;',
        '"RESULT generators",size(minbase(fK)),"dim",dim(sF),"mult",mult(sF),"det nonzero",dt!=0;',
        '"RESULT header generators",size(minbase(KH)),"dim",dim(sH),"mult",mult(sH);',
        '"RESULT control identity",c1,c2,"control perturbed",d1,d2,"control header generators 1 and 2 swapped",s1,s2;',
        f"int good=(a1==0 and a2==0 and size(minbase(fK))=={quadrics} and dim(sF)=={dimension}"
        f" and mult(sF)=={multiplicity} and dt!=0 and (c1>0 or c2>0) and (d1>0 or d2>0) and (s1>0 or s2>0));",
        f'string hv="INDUCED VERDICT p {prime} root {root} ";',
        'if(good){hv+"PASS";}else{hv+"FAIL";}',
        '"EXIT 0"; quit;',
    ]
    return "\n".join(lines) + "\n"


def _singular(script: Path) -> list[str]:
    """Run one script with stdin from /dev/null, write its output beside it as .log and return the lines."""
    process = subprocess.run(
        ["Singular", "-q", "--no-warn", "--no-rc", str(script)],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    script.with_suffix(".log").write_text(process.stdout, encoding="utf-8")
    lines = process.stdout.splitlines()
    base._require(
        process.returncode == 0 and not any(line.lstrip().startswith("?") for line in lines),
        f"Singular failed on {script.name}",
    )
    return lines


def stage(item: tuple[str, str]) -> bool:
    """One Q(i) script of (source, mode); the high mode must find no high-weight part outside J + m I."""
    source, mode = item
    script = HERE / f"{mode}-{source}-qi.sing"
    script.write_text(emit(source, 0, 0, mode), encoding="utf-8")
    lines = _singular(script)
    return mode != "high" or "RESULT header_high_weight_outside 0" in lines


def reduction(item: tuple[str, str, int, int]) -> bool:
    """One reduction of (kind, source, prime, root): a check must pass, and a control, at the other root of -1, must
    fail with nonzero remainders in both directions."""
    kind, source, prime, root = item
    record = json.loads((HERE / f"induced-{source}.json").read_text(encoding="utf-8"))
    script = HERE / f"{kind}-{source}-p{prime}-r{root}.sing"
    script.write_text(check_script(record, prime, root, FIBERS / HEADERS[(source, prime)]), encoding="utf-8")
    lines = _singular(script)
    found = [match for match in map(REMAINDERS.match, lines) if match is not None]
    base._require(len(found) == 1, f"{script.name}: no single line of remainders")
    remainders = (int(found[0].group(1)), int(found[0].group(2)))
    if kind == "check":
        return remainders == (0, 0) and f"INDUCED VERDICT p {prime} root {root} PASS" in lines
    return min(remainders) > 0 and f"INDUCED VERDICT p {prime} root {root} FAIL" in lines


def reductions() -> list[tuple[str, str, int, int]]:
    items = [("check", source, prime, root) for source in SOURCES for prime, root in ROOTS]
    return items + [("control", source, prime, prime - root) for source in SOURCES for prime, root in ROOTS]


def run() -> int:
    import weight_slice_fiber_relations as ws

    stages = [(source, mode) for source in SOURCES for mode in MODES]
    done = ws.parallel.ordered_map(stage, stages, min_items=1)
    failed: list[tuple[Any, ...]] = [item for item, good in zip(stages, done, strict=True) if not good]
    for source in SOURCES:
        record = collect(HERE / f"map-{source}-qi.log", HERE / f"relations-{source}-qi.log", source)
        (HERE / f"induced-{source}.json").write_text(
            json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8"
        )
        print("COLLECT", source, "PASS" if record["pass"] else f"FAIL {record['problems']}")
        if not record["pass"]:
            failed.append((source, "collect"))
    if not failed:
        items = reductions()
        results = ws.parallel.ordered_map(reduction, items, min_items=1)
        failed += [item for item, good in zip(items, results, strict=True) if not good]
    for item in failed:
        print("FAILED", *item, file=sys.stderr)
    print("run_x_induced:", "FAIL" if failed else "PASS")
    return 1 if failed else 0


def main() -> None:
    arguments = sys.argv[1:]
    if arguments == ["--run"]:
        raise SystemExit(run())
    if arguments[:1] == ["--emit"] and arguments[1] in SOURCES:
        mode = arguments[4] if len(arguments) > 4 else "map"
        sys.stdout.write(emit(arguments[1], int(arguments[2]), int(arguments[3]), mode))
    elif arguments[:1] == ["--collect"] and arguments[3] in SOURCES:
        record = collect(Path(arguments[1]), Path(arguments[2]), arguments[3])
        Path(arguments[4]).write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        print("COLLECT", arguments[3], "PASS" if record["pass"] else f"FAIL {record['problems']}")
        if not record["pass"]:
            raise SystemExit(1)
    elif arguments[:1] == ["--check"]:
        record = json.loads(Path(arguments[1]).read_text(encoding="utf-8"))
        sys.stdout.write(check_script(record, int(arguments[2]), int(arguments[3]), Path(arguments[4])))
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
