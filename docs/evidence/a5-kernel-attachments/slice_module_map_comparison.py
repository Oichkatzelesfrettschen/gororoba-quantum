"""The module maps of the E8-bar quadric rings on the two slices agree under the map the slice change induces.

For E8-bar at the N+ and N- basepoints the nilradical module R / K of the quadric ring is isomorphic to the irrelevant
ideal of k[y] / (K : R) on the header slice modulo 32009, 32029 and 32057 (ledger row A5-638) and on the weight slice
over Q(i) and modulo the split primes (A5-640); each isomorphism is the one solution, up to a scalar, of a linear
system for a map theta from the coordinates of B = k[y] / (K : R) to the span N of the nilpotent linear forms. The
substitution G of the 21 generators that the change of slice induces (A5-598, retained over Q(i) in
"e8-induced-slice-map/induced-CELL.json") carries the weight-slice ideal K_w onto the header-slice ideal K_h at every
retained prime. This program reduces G and K_w at a prime and a root of -1, solves the system on both sides, and
tests the identity

    G(theta_w(x)) = c * theta_h(G(x) modulo the linear forms of K_h : R_h)   for the five coordinates x of B_w

with one nonzero scalar c. Each map carries the normalization of its retained record: the weight-slice map is divided
by the leading coefficient of its first image (A5-640) and the header-slice map has its free coordinate set to 1
(A5-638); the solved maps must equal the retained ones (the table of `weight_slice_module_map.py` with i sent to the
root, and `expected_map` of `quadric_and_germ_probes.py`), and between them the measured scalar is c = i / 2 on every
cell, i the root of -1 of the cell. The identity is forced: G carries R_w, N_w and K_w : R_w to their header
counterparts, so it carries a solution of one system to a solution of the other, and both solution spaces are
one-dimensional. The run is a confirmation that shares its inputs with A5-598 and A5-638 and adds no independent
evidence for either; a failure would refute one of them or expose a solver that does not compute the intrinsic map.

Controls, each of which must find no scalar: the weight-slice images of the first two coordinates exchanged; the map
G with the first header coordinate of B_h added to the image of the leading variable of the first weight-slice image;
and G followed by the exchange of the first two header coordinates of B_h. A change of G on a generator that occurs
in no coordinate of B_w and in no nilpotent form (y(1), say) leaves the test unchanged, since the test reads G on
those ten linear forms alone; the equality of the transported ideal with K_h binds the rest of G.

The cells with a retained header map and a retained reduction of G: N- at (32009, 10754), (32029, 9115) and
(32057, 8059), N+ at (32009, 10754) and (32029, 9115). Same-sign X has no retained slice map and is not covered.

Usage, from the repository root: "$PYTHON" docs/evidence/a5-kernel-attachments/slice_module_map_comparison.py
--out OUT.json [--check RETAINED.json]. Each cell is one Singular run of a few seconds.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
FIBERS = HERE.parent / "a5-exceptional-fibers"
INDUCED = FIBERS / "working" / "runs" / "e8-induced-slice-map"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(INDUCED))

sys.path.insert(0, str(FIBERS / "structure"))

import induced_slice_map as induced  # noqa: E402
import quadric_and_germ_probes as probes  # noqa: E402
import weight_slice_fiber_relations as ws  # noqa: E402
import weight_slice_module_map as weight_map  # noqa: E402

SCHEMA = "gororoba.a5.slice-module-map-comparison/1"
TIMEOUT_SECONDS = 1800
# (orbit, record tag, prime, root of -1, header relation file under a5-exceptional-fibers/)
CELLS: tuple[tuple[str, str, int, int, str], ...] = (
    ("N-", "nm", 32009, 10754, "working/distribute/out/a5-e8-d2/e8nm_p1/d2/relations-upto-d2.rel"),
    ("N-", "nm", 32029, 9115, "working/distribute/out/a5-e8-d2/e8nm_p2/d2/relations-upto-d2.rel"),
    ("N-", "nm", 32057, 8059, "third-prime/relations/e8-nm/d2/relations-upto-d2.rel"),
    ("N+", "np", 32009, 10754, "working/runs/e8_a2/e8_k2.rel"),
    ("N+", "np", 32029, 9115, "working/distribute/out/a5-e8-d2/e8np_p2/d2/relations-upto-d2.rel"),
)
# The first line of the comparison part of induced.check_script; the lines before it define KW, KH and the map f.
MARKER = "ideal mx=maxideal(1);"

TAIL = """ideal mx=maxideal(1); ideal imgf=f(mx);
proc side(ideal K)
{ ideal sK=std(K); ideal R=std(radical(sK)); ideal N=simplify(jet(R,1),2); ideal KN=std(sK+N);
  int gn=(size(reduce(R,KN))==0 && size(reduce(KN,R))==0);
  ideal A=std(quotient(sK,R)); ideal Al=std(simplify(jet(A,1),2)); ideal F; int m;
  for(m=1;m<=21;m++){ if(reduce(y(m),Al)==y(m)){ F[size(F)+1]=y(m); } }
  ideal Aq=simplify(reduce(A,Al),2);
  return(list(sK,N,Al,F,Aq,gn)); }
list SW=side(KW); list SH=side(KH);
ideal sKW=SW[1]; ideal NW=SW[2]; ideal AlW=SW[3]; ideal FW=SW[4]; ideal AqW=SW[5];
ideal sKH=SH[1]; ideal NH=SH[2]; ideal AlH=SH[3]; ideal FH=SH[4]; ideal AqH=SH[5];
"RESULT weight_side",size(NW),SW[6],size(FW),size(AlW),size(AqW);
"RESULT header_side",size(NH),SH[6],size(FH),size(AlH),size(AqH);
if(size(NW)!=5 || size(FW)!=5 || size(NH)!=5 || size(FH)!=5){ "RESULT abort 1"; quit; }
ideal fK=f(KW); ideal fAl=f(AlW); ideal fN=f(NW);
"RESULT transported",size(reduce(fK,sKH)),size(reduce(KH,std(fK)));
"RESULT linear_parts",size(reduce(fAl,AlH)),size(reduce(fN,std(NH)));
ring r1=@P@,(y(1..21),t(1..25)),(dp(21),dp(25));
proc collect(poly e, poly ymon)
{ ideal T; int c; if(e!=0){ matrix C=coef(e,ymon); for(c=1;c<=ncols(C);c++){ T[size(T)+1]=C[2,c]; } } return(T); }
proc solve(string tag, ideal sK, ideal N, ideal F, ideal Aq, int nrm)
{ int g=5; int m; int j; int k; int c; int sg; poly s; poly e; ideal TH; ideal IM; ideal T; ideal sT; int fr;
  matrix M[g][g]; number lc;
  poly ymon=1; for(m=1;m<=21;m++){ ymon=ymon*y(m); }
  for(j=1;j<=g;j++){ s=0; for(m=1;m<=g;m++){ s=s+t((j-1)*g+m)*N[m]; } TH[j]=s; }
  for(sg=-1;sg<=1;sg=sg+2){
    T=0;
    for(j=1;j<=g;j++){ for(k=j+1;k<=g;k++){ T=T+collect(reduce(F[j]*TH[k]+sg*F[k]*TH[j],sK),ymon); } }
    for(c=1;c<=size(Aq);c++){ e=0; for(j=1;j<=g;j++){ e=e+diff(Aq[c],F[j])*TH[j]; } T=T+collect(reduce(e,sK),ymon); }
    sT=std(T);
    if(sg==1){ print("RESULT "+tag+"_control_solutions "+string(g*g-size(sT))); }
    if(sg==-1){
      print("RESULT "+tag+"_solutions "+string(g*g-size(sT)));
      if(g*g-size(sT)==1){
        fr=0; for(m=1;m<=g*g;m++){ if(reduce(t(m),sT)==t(m)){ fr=m; } }
        for(j=1;j<=g;j++){ for(m=1;m<=g;m++){ M[j,m]=subst(reduce(t((j-1)*g+m),sT),t(fr),1); } }
        print("RESULT "+tag+"_det_nonzero "+string(det(M)!=0));
        for(j=1;j<=g;j++){ s=0; for(m=1;m<=g;m++){ s=s+M[j,m]*N[m]; } IM[j]=s; }
        if(nrm==1){ lc=leadcoef(IM[1]); IM=IM/lc; }
      }
    }
  }
  return(IM); }
ideal IMW=solve("weight",std(imap(r0,sKW)),imap(r0,NW),imap(r0,FW),imap(r0,AqW),1);
ideal IMH=solve("header",std(imap(r0,sKH)),imap(r0,NH),imap(r0,FH),imap(r0,AqH),0);
setring r0;
ideal IMW=imap(r1,IMW); ideal IMH=imap(r1,IMH);
if(size(IMW)!=5 || size(IMH)!=5){ "RESULT abort 2"; quit; }
int k; for(k=1;k<=5;k++){ "RESULT weight_image",FW[k],IMW[k]; }
for(k=1;k<=5;k++){ "RESULT header_image",FH[k],IMH[k]; }
proc prop(ideal L, ideal Rr)
{ int k; poly d; number c=0;
  for(k=1;k<=5;k++){ if(L[k]!=0){ d=diff(Rr[k],leadmonom(L[k])); if(d==0){ return("0 0"); }
    c=leadcoef(L[k])/leadcoef(d); break; } }
  if(c==0){ return("0 0"); }
  for(k=1;k<=5;k++){ if(L[k]-c*Rr[k]!=0){ return("0 0"); } }
  return("1 "+string(c)); }
proc compare(ideal img, ideal IMW, ideal FW, ideal AlH, ideal FH, ideal IMH)
{ map h=basering,img; ideal L; ideal Rr; poly v; poly s; poly x; int k; int j; matrix B[5][5];
  for(k=1;k<=5;k++){ x=FW[k]; v=reduce(h(x),AlH); s=0;
    for(j=1;j<=5;j++){ B[k,j]=diff(v,FH[j]); s=s+B[k,j]*IMH[j]; }
    x=IMW[k]; L[k]=h(x); Rr[k]=s; }
  return(string(det(B)!=0)+" "+prop(L,Rr)); }
"RESULT scalar",compare(imgf,IMW,FW,AlH,FH,IMH);
ideal IMX=IMW; IMX[1]=IMW[2]; IMX[2]=IMW[1];
"RESULT control_images_exchanged",compare(imgf,IMX,FW,AlH,FH,IMH);
proc vindex(poly v){ int m; for(m=1;m<=21;m++){ if(y(m)==v){ return(m); } } return(0); }
int i0=vindex(leadmonom(IMW[1])); int j1=vindex(FH[1]); int j2=vindex(FH[2]);
"RESULT control_indices",i0,j1,j2;
ideal img2=imgf; img2[i0]=img2[i0]+FH[1];
"RESULT control_map_perturbed",compare(img2,IMW,FW,AlH,FH,IMH);
ideal swp=maxideal(1); swp[j1]=y(j2); swp[j2]=y(j1); map sw=r0,swp; ideal img3=sw(imgf);
"RESULT control_generators_exchanged",compare(img3,IMW,FW,AlH,FH,IMH);
"RESULT done 1";
quit;
"""


def script(tag: str, prime: int, root: int, header: str) -> str:
    """The Singular text of one cell: KW, KH and f from the retained Q(i) record, then both systems and the test."""
    record = json.loads((INDUCED / f"induced-{tag}.json").read_text(encoding="utf-8"))
    if record.get("pass") is not True or record["relations_sha256"] != record["relations_sha256_retained"]:
        raise RuntimeError(f"induced-{tag}.json is not a passing record bound to the weight-slice digest")
    text = induced.check_script(record, prime, root, FIBERS / header, None)
    if text.count(MARKER) != 1 or not text.startswith(f"ring r={prime},(y(1..21)),dp;"):
        raise RuntimeError("the reduction script of induced_slice_map.py changed its layout")
    head = (
        text[: text.index(MARKER)].replace(f"ring r={prime},", f"ring r0={prime},", 1).replace("map f=r,", "map f=r0,")
    )
    if head.count("map f=r0,") != 1:
        raise RuntimeError("the reduction script of induced_slice_map.py changed its map line")
    return 'LIB "primdec.lib"; LIB "matrix.lib";\n' + head + TAIL.replace("@P@", str(prime))


def parse(stdout: str) -> dict[str, Any]:
    """The RESULT lines of one run as a row; an error line or a missing end raises."""
    lines = [ln.split()[1:] for ln in stdout.splitlines() if ln.startswith("RESULT ")]
    if any(ln.lstrip().startswith("?") for ln in stdout.splitlines()) or ["done", "1"] not in lines:
        raise RuntimeError(f"Singular error or incomplete run: {stdout[-400:]}")
    row: dict[str, Any] = {"weight_image": [], "header_image": []}
    for f in lines:
        if f[0] in ("weight_image", "header_image"):
            row[f[0]].append([f[1], "".join(f[2:])])
        elif f[0] != "done":
            row[f[0]] = [int(x) for x in f[1:]]
    return row


def cell(item: tuple[str, str, int, int, str]) -> dict[str, Any]:
    orbit, tag, prime, root, header = item
    with tempfile.TemporaryDirectory() as tmp:
        source = Path(tmp, "compare.sing")
        source.write_text(script(tag, prime, root, header), encoding="utf-8")
        command = ["prlimit", f"--as={ws.SINGULAR_ADDRESS_SPACE_BYTES}", "Singular", "-q", "--no-rc", str(source)]
        run = subprocess.run(
            command, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=TIMEOUT_SECONDS, check=True
        )
    return {"ring": f"E8-bar -> {orbit}", "prime": prime, "root": root, "header": header} | parse(run.stdout)


def expected(item: tuple[str, str, int, int, str]) -> dict[str, Any]:
    """The fields the finding fixes: both maps as their records retain them, and the scalar i / 2 between them."""
    orbit, _tag, prime, root, header = item
    retained = [row for row in probes.MAPS if row[0] == f"E8-bar -> {orbit}" and row[1] == prime]
    if len(retained) != 1:
        raise RuntimeError(f"no single module-map row of the header slice for E8-bar -> {orbit} at {prime}")
    return {
        "weight_image": weight_map.images("e8", orbit, prime, root),
        "header_image": probes.expected_map(retained[0])["images"],
        "ring": f"E8-bar -> {orbit}",
        "prime": prime,
        "root": root,
        "header": header,
        "weight_side": [5, 1, 5, 16, 1],
        "header_side": [5, 1, 5, 16, 1],
        "transported": [0, 0],
        "linear_parts": [0, 0],
        "weight_solutions": [1],
        "weight_det_nonzero": [1],
        "weight_control_solutions": [0],
        "header_solutions": [1],
        "header_det_nonzero": [1],
        "header_control_solutions": [0],
    }


# A scalar row reads [the map G(x) modulo the linear forms is invertible, one scalar relates the two maps, the scalar].
CONTROLS = ("control_images_exchanged", "control_map_perturbed", "control_generators_exchanged")


def problems(cells: list[dict[str, Any]]) -> list[str]:
    """The departures of the cells from the finding; an empty list for the retained record."""
    if len(cells) != len(CELLS):
        return [f"{len(cells)} cells, expected {len(CELLS)}"]
    found = []
    for row, item in zip(cells, CELLS, strict=True):
        want = expected(item)
        name = f"{want['ring']} at {want['prime']}"
        if {k: row.get(k) for k in want} != want:
            found.append(f"{name}: a side, the transport, a solution count or a retained map differs from the finding")
        scalar = row.get("scalar")
        half_root = want["root"] * pow(2, -1, want["prime"]) % want["prime"]
        if not (isinstance(scalar, list) and len(scalar) == 3 and scalar[:2] == [1, 1]) or (
            scalar[2] % want["prime"] != half_root
        ):
            found.append(f"{name}: the transported weight-slice map is not i / 2 times the header-slice map")
        for control in CONTROLS:
            value = row.get(control)
            if not (isinstance(value, list) and len(value) == 3 and value[1:] == [0, 0]):
                found.append(f"{name}: {control} found a scalar")
        indices = row.get("control_indices")
        if not (isinstance(indices, list) and len(indices) == 3 and min(indices) >= 1 and indices[1] != indices[2]):
            found.append(f"{name}: a control names no generator")
        if set(row) != {*want, "scalar", *CONTROLS, "control_indices"}:
            found.append(f"{name}: the row holds an unexpected or missing field")
    return found


def main() -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--out", type=Path, required=True, help="write the JSON record")
    parser.add_argument("--check", type=Path, help="compare the computed record with this retained one")
    args = parser.parse_args()
    banner, version = ws.singular_version()
    record: dict[str, Any] = {
        "schema": SCHEMA,
        "tools": {"singular": banner, "singular_version": version},
        "cells": [cell(item) for item in CELLS],
    }
    record["problems"] = problems(record["cells"])
    args.out.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    for row in record["cells"]:
        print(row["ring"], row["prime"], "scalar", row.get("scalar"), *(row.get(c) for c in CONTROLS))
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
