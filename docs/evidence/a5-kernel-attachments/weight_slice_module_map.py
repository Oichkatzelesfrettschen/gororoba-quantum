"""The nilradical module of the weight-slice quadric rings over Q(i) is the irrelevant ideal of a smaller cone.

For same-sign X and E8-bar at the N+ and N- basepoints, on the degree-2 relations K that
`weight_slice_fiber_relations.py` regenerates over Q(i) (ledger row A5-421): R is the radical of K (the intersection
of the minimal primes from minAssGTZ, the method of A5-447), N its g linear forms, A = K : R and B = Q(i)[y] / A,
whose g coordinates are the variables that the linear forms of A leave free. The program solves the linear system
for a Q(i)-linear map theta from the coordinates of B to the span of N with x_j theta(x_k) - x_k theta(x_j) in K
for every pair and, where A holds a quadric q, sum_j (dq/dx_j) theta(x_j) in K. These are the images of the
generating syzygies of the irrelevant ideal m of B (the Koszul relations; with the Euler relation of q over the
quadric hypersurface ring, where 2 is invertible), so a solution extends to a B-linear map m -> R / K. It is onto
when theta is invertible and R = K + N, and then an isomorphism when the two modules have one Hilbert function,
which the first Hilbert numerators decide: N_K - N_R = N_A - (1 - t)^n. The control system, with
x_j theta(x_k) + x_k theta(x_j), has the zero solution alone; a solver that dropped its equations would return g^2.

Each cell also runs modulo the split primes (32009, i = 10754) and (32029, i = 9115), on the relations the producer
regenerates there. Every map is normalized by the leading coefficient of its first image, which fixes the scalar the
one-dimensional solution space leaves free; the modular map must then equal the Q(i) map with i sent to the root.

The same system on the header slices modulo 32009, 32029 and 32057 is the `module-map` row kind of
`a5-exceptional-fibers/structure/quadric_and_germ_probes.py` (ledger row A5-638); the slices carry different
coordinates, and `slice_module_map_comparison.py` compares the E8-bar maps entry by entry under the induced slice map.

Usage, from the repository root: "$PYTHON" docs/evidence/a5-kernel-attachments/weight_slice_module_map.py
--out OUT.json [--check RETAINED.json]. The twelve runs (four cells over three fields) go through
parallel.ordered_map; each Singular call holds the address-space limit of the producer.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from math import comb
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[2] / "gororoba_quantum"))

import weight_slice_fiber_relations as ws  # noqa: E402
import weight_slice_quadric_rings as wq  # noqa: E402

import parallel  # noqa: E402

SCHEMA = "gororoba.a5.weight-slice-module-map/1"
TIMEOUT_SECONDS = 1800
# (source, orbit, number of nilpotent linear forms)
CELLS = (("xm", "N-", 3), ("xp", "N+", 3), ("e8", "N-", 5), ("e8", "N+", 5))

SCRIPT = """LIB "primdec.lib"; LIB "matrix.lib";
ring r0=@FIELD@,(y(1..@N@)),dp; @MINPOLY@
ideal K=
@POLYS@;
ideal sK=std(K); list P=minAssGTZ(K); ideal R=P[1]; int k; for(k=2;k<=size(P);k++){ R=intersect(R,P[k]); } R=std(R);
ideal N=simplify(jet(R,1),2); int g=size(N);
ideal KN=std(sK+N);
"RESULT generation",g,size(reduce(R,KN))==0 && size(reduce(KN,R))==0;
ideal A=std(quotient(sK,R)); ideal Al=std(simplify(jet(A,1),2));
ideal F; int j; int c; int m;
for(m=1;m<=@N@;m++){ if(reduce(y(m),Al)==y(m)){ F[size(F)+1]=y(m); } }
ideal Aq=simplify(reduce(A,Al),2);
"RESULT cone",size(F),size(Al),size(Aq);
"RESULT numK",hilb(sK,1); "RESULT numR",hilb(R,1); "RESULT numA",hilb(A,1);
if(size(F)!=@G@ || g!=@G@){ "RESULT abort 1"; quit; }
ring r1=@FIELD@,(y(1..@N@),t(1..@GG@)),(dp(@N@),dp(@GG@)); @MINPOLY@
ideal sK=std(imap(r0,sK)); ideal N=imap(r0,N); ideal F=imap(r0,F); ideal Aq=imap(r0,Aq);
int g=@G@; int m; int j; int k; int c; int sg;
poly ymon=1; for(m=1;m<=@N@;m++){ ymon=ymon*y(m); }
ideal TH; poly s; poly e;
for(j=1;j<=g;j++){ s=0; for(m=1;m<=g;m++){ s=s+t((j-1)*g+m)*N[m]; } TH[j]=s; }
proc collect(poly e, poly ymon)
{ ideal T; int c; if(e!=0){ matrix C=coef(e,ymon); for(c=1;c<=ncols(C);c++){ T[size(T)+1]=C[2,c]; } } return(T); }
for(sg=-1;sg<=1;sg=sg+2){
  ideal T;
  for(j=1;j<=g;j++){ for(k=j+1;k<=g;k++){ T=T+collect(reduce(F[j]*TH[k]+sg*F[k]*TH[j],sK),ymon); } }
  for(c=1;c<=size(Aq);c++){ e=0; for(j=1;j<=g;j++){ e=e+diff(Aq[c],F[j])*TH[j]; } T=T+collect(reduce(e,sK),ymon); }
  ideal sT=std(T);
  if(sg==1){ "RESULT control_solutions",g*g-size(sT); }
  if(sg==-1){
    "RESULT solutions",g*g-size(sT);
    if(g*g-size(sT)==1){
      int fr=0; for(m=1;m<=g*g;m++){ if(reduce(t(m),sT)==t(m)){ fr=m; } }
      matrix M[g][g]; for(j=1;j<=g;j++){ for(m=1;m<=g;m++){ M[j,m]=subst(reduce(t((j-1)*g+m),sT),t(fr),1); } }
      "RESULT det_nonzero",det(M)!=0;
      ideal IM; for(j=1;j<=g;j++){ s=0; for(m=1;m<=g;m++){ s=s+M[j,m]*N[m]; } IM[j]=s; }
      number lc=leadcoef(IM[1]);
      for(j=1;j<=g;j++){ "RESULT image",F[j],IM[j]/lc; }
    }
  }
  kill T; kill sT;
}
"RESULT done 1";
quit;
"""

# (characteristic, root of -1); characteristic 0 is Q(i)
FIELDS = ((0, 0), (32009, 10754), (32029, 9115))
# The map of each cell over Q(i), normalized by the leading coefficient of its first image, in the generator order
# of the weight-slice producer: variable -> terms (coefficient, variable), a coefficient an integer or "i". The sign
# of i is + for X at N- and E8-bar at N+, and - for X at N+ and E8-bar at N-.
X_MAP: list[tuple[int, list[tuple[int | str, int]]]] = [(7, [(1, 3)]), (10, [("i", 5)]), (12, [(1, 6)])]
E8_MAP: list[tuple[int, list[tuple[int | str, int]]]] = [
    (8, [(1, 3)]),
    (14, [(-1, 6)]),
    (16, [(-1, 5)]),
    (17, [(1, 7)]),
    (19, [(-2, 12), ("i", 13), ("i", 17)]),
]
# The relation digests of the modular cells, which the retained weight-slice record does not hold.
MODULAR_DIGESTS: dict[str, str] = {
    "X-->N- 32009": "49b09b286265c9e519e60f78503461e58e849acd09ac68d9f4e33a4c7e2091e6",
    "X+->N+ 32009": "885969840cd94d5e80e06d6ebee3da560a92bdfc453d59481fcef95b6a1eb0ba",
    "E8bar->N- 32009": "42b1d8ff03d4c505597b39fe303c52ac45fcdc4d35bbf01d0b8e7e23a97367d0",
    "E8bar->N+ 32009": "b9b7372bce35e7ce286aa572f9b1ebf656d1ac04ba0e63349c640efed88658ee",
    "X-->N- 32029": "5b950ee66306c05a1888d61b9f6a06d3bc8c30a47fcede139c30222a7261c9f9",
    "X+->N+ 32029": "e38b521b7c36ea231786b9d7dbcd82898b042afa18c5271716a4019d92e397b0",
    "E8bar->N- 32029": "bbbb4a5f8b178cc7e001c93bcaa790bd421a5b168bab2598d75fbef6e03b1f31",
    "E8bar->N+ 32029": "7c04530f75570b6e4e8eade28042a592b4029dfac983bc5c78a386680ffe105b",
}


def field_name(characteristic: int) -> str:
    return "Q(i)" if characteristic == 0 else f"F_{characteristic}"


def images(source: str, orbit: str, characteristic: int, root: int) -> list[list[str]]:
    """The expected normalized map as Singular prints it: over Q(i), or with i sent to the root over F_p."""
    sign = 1 if (source != "e8") == (orbit == "N-") else -1
    found = []
    for variable, terms in X_MAP if source != "e8" else E8_MAP:
        text = ""
        for coefficient, index in terms:
            if characteristic == 0 and coefficient == "i":
                piece = f"({'' if sign == 1 else '-'}i)*y({index})"
            else:
                value = sign * root if coefficient == "i" else int(coefficient)
                if characteristic:
                    value %= characteristic
                    value = value - characteristic if value > characteristic // 2 else value
                body = f"y({index})" if abs(value) == 1 else f"{abs(value)}*y({index})"
                piece = ("-" if value < 0 else "") + body
            text += piece if not text or piece.startswith("-") else "+" + piece
        found.append([f"y({variable})", text])
    return found


def numerator_identity(num_k: list[int], num_r: list[int], num_a: list[int], n: int) -> bool:
    """N_K - N_R = N_A - (1 - t)^n, coefficient by coefficient."""
    width = n + 1 + max(len(num_k), len(num_r), len(num_a))
    pad = [x + [0] * (width - len(x)) for x in (num_k, num_r, num_a)]
    unit = [(-1) ** d * comb(n, d) if d <= n else 0 for d in range(width)]
    return all(pad[0][d] - pad[1][d] == pad[2][d] - unit[d] for d in range(width))


def solve(n: int, g: int, characteristic: int, polynomials: list[str]) -> dict[str, Any]:
    """The RESULT lines of one Singular run of SCRIPT, as a row."""
    field, minpoly = ("(0,i)", "minpoly=i^2+1;") if characteristic == 0 else (str(characteristic), "")
    text = SCRIPT.replace("@N@", str(n)).replace("@GG@", str(g * g)).replace("@G@", str(g))
    text = text.replace("@FIELD@", field).replace("@MINPOLY@", minpoly).replace("@POLYS@", ",\n".join(polynomials))
    with tempfile.TemporaryDirectory() as tmp:
        source = Path(tmp, "map.sing")
        source.write_text(text, encoding="utf-8")
        command = ["prlimit", f"--as={ws.SINGULAR_ADDRESS_SPACE_BYTES}", "Singular", "-q", "--no-rc", str(source)]
        run = subprocess.run(
            command, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=TIMEOUT_SECONDS, check=True
        )
    lines = [ln.split()[1:] for ln in run.stdout.splitlines() if ln.startswith("RESULT ")]
    if any(ln.lstrip().startswith("?") for ln in run.stdout.splitlines()) or ["done", "1"] not in lines:
        raise RuntimeError(f"Singular error or incomplete run: {run.stdout[-400:]}")
    row: dict[str, Any] = {"images": []}
    numerators: dict[str, list[int]] = {}
    for f in lines:
        if f[0] == "image":
            row["images"].append([f[1], "".join(f[2:])])
        elif f[0] in ("numK", "numR", "numA"):
            numerators[f[0]] = [int(x) for x in "".join(f[1:]).split(",")][:-1]
        elif f[0] != "done":
            row[f[0]] = [int(x) for x in f[1:]]
    row["numerator_identity"] = len(numerators) == 3 and numerator_identity(
        numerators["numK"], numerators["numR"], numerators["numA"], n
    )
    return row


def retained_digest(name: str, characteristic: int, retained: dict[str, str]) -> str | None:
    """The digest that binds a cell's relations: the weight-slice record over Q(i), MODULAR_DIGESTS over F_p."""
    return retained.get(name) if characteristic == 0 else MODULAR_DIGESTS.get(f"{name} {characteristic}")


def cell(item: tuple[str, str, int, int, int, dict[str, str]]) -> dict[str, Any]:
    source, orbit, g, characteristic, root, retained = item
    name = ws.incidence_name(orbit, source)
    run = ws.run_singular(ws.fiber_script(ws.orbit_task(orbit), source, characteristic, root))
    summary = ws.summarize_fiber_run(run)
    n = summary["generator_count"]
    row = {"ring": name, "field": field_name(characteristic), "variables": n}
    row |= solve(n, g, characteristic, wq.polynomials(sorted(run["relations"])))
    row |= {
        "relations_sha256": summary["relations_sha256"],
        "relations_match_retained": summary["relations_sha256"] == retained_digest(name, characteristic, retained),
    }
    return row


def expected(source: str, orbit: str, g: int, characteristic: int, root: int) -> dict[str, Any]:
    """The fields of a cell that the findings fix; the relation digest is bound by relations_match_retained."""
    return {
        "ring": ws.incidence_name(orbit, source),
        "field": field_name(characteristic),
        "variables": 15 if g == 3 else 21,
        "images": images(source, orbit, characteristic, root),
        "generation": [g, 1],
        "cone": [3, 12, 0] if g == 3 else [5, 16, 1],
        "solutions": [1],
        "det_nonzero": [1],
        "control_solutions": [0],
        "numerator_identity": True,
        "relations_match_retained": True,
    }


def jobs() -> list[tuple[str, str, int, int, int]]:
    return [(source, orbit, g, characteristic, root) for characteristic, root in FIELDS for source, orbit, g in CELLS]


def problems(cells: list[dict[str, Any]]) -> list[str]:
    """The departures of the cells from the findings; an empty list for the retained record."""
    if len(cells) != len(jobs()):
        return [f"{len(cells)} cells, expected {len(jobs())}"]
    found = []
    for row, job in zip(cells, jobs(), strict=True):
        want = expected(*job)
        if {k: row.get(k) for k in want} != want or set(row) != {*want, "relations_sha256"}:
            found.append(
                f"{want['ring']} over {want['field']}: the row differs from one invertible map equal to the Q(i) map, "
                "an empty control and equal numerators"
            )
    return found


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, required=True, help="write the JSON record")
    parser.add_argument("--check", type=Path, help="compare the computed record with this retained one")
    args = parser.parse_args()
    retained = {
        item["incidence"]: item["relations_sha256"]
        for item in json.loads(wq.WEIGHT_SLICE.read_text(encoding="utf-8"))["cells"]
        if item["characteristic"] == 0
    }
    banner, version = ws.singular_version()
    record: dict[str, Any] = {
        "schema": SCHEMA,
        "tools": {"singular": banner, "singular_version": version},
        "cells": list(parallel.ordered_map(cell, [(*job, retained) for job in jobs()], min_items=1)),
    }
    record["problems"] = problems(record["cells"])
    args.out.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    for row in record["cells"]:
        print(
            row["ring"],
            row["field"],
            row["solutions"],
            row["det_nonzero"],
            row["control_solutions"],
            row["images"][-1][1],
        )
    for line in record["problems"]:
        print("PROBLEM", line, file=sys.stderr)
    if args.check is not None:
        kept = json.loads(args.check.read_text(encoding="utf-8"))
        if {k: v for k, v in kept.items() if k != "tools"} != {k: v for k, v in record.items() if k != "tools"}:
            print("PROBLEM the computed record differs from the retained one", file=sys.stderr)
            return 1
    return 0 if record["problems"] == [] else 1


if __name__ == "__main__":
    sys.exit(main())
