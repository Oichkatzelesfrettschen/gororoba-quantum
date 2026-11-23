"""The linear map that the slice change induces between the two presentations of the fiber cone of E8-bar -> N+-.

The header slice (nullity16_basepoints) and the weight slice (weight_slice_fiber_relations) are two nine-dimensional
affine slices through one basepoint z_0 in the fifteen complex coordinates, and each takes its 21 generators among the
126 principal 4-Pfaffians of a Schur form of C(z): the header in the frame of a principal pivot of C(z_0), the weight
slice in a frame of torus eigenvectors. Where the Pfaffian of a pivot block B is a unit, the 4-Pfaffians of the Schur
form of B generate the ideal of 10-Pfaffians of C(z), so both generator sets generate one ideal I of the local ring.
This producer restricts the header frame's 21 selected Pfaffians to the weight slice and writes each as a constant
combination of the weight-slice generators modulo J + m I, over Q(i). The coefficient matrix is the map that the
identification I_h / m I_h = I / m I = I_w / m I_w induces on generators.

The computation runs in k[s1..s9, v] / (v u - 1), u the product of the two pivot Pfaffians on the weight-zero axis, so
that both Pfaffians are invertible; the class of a header Pfaffian minus its combination is killed by s2 and vanishes
in the local ring at the origin, hence in this ring. The degree-2 relations of the weight slice come from the
script of the weight-slice producer itself (mode relations), and --check transports them by the map.

--emit ORBIT CHAR ROOT [map|relations] writes a Singular script (CHAR 0 for Q(i)); --collect MAP_LOG
RELATION_LOG ORBIT OUT.json reads the outputs;
--check OUT.json PRIME ROOT HEADER_REL [WEIGHT_KA] writes to stdout a Singular script that reduces the Q(i) record at
(PRIME, ROOT) and compares the transported ideal with a retained header relation file.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import sys
from fractions import Fraction
from pathlib import Path
from string import Template
from typing import Any

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE.parents[3]
ATTACH = EVIDENCE / "a5-kernel-attachments"
sys.path.insert(0, str(ATTACH))

GENERATORS = 21
RELATIONS = 148
HEADER_SELECTED_KEY = "chosen_coordinate_indices_one_based"
REES_RECORD = ATTACH / "nullity16-rees-fibers-result.json"
WEIGHT_RECORD = ATTACH / "weight-slice-fiber-relations-result.json"
POSITIVE = (1, 3, 4, 5, 6, 7, 8, 9)

HEADER_TAIL = Template(
    """
ideal T0=std(J+TR+m*PF);
ideal HP; int hq=0;
$header_pfaffians
ideal NWf=reduce(G,T0); ideal NHf=reduce(HP,T0);
print("RESULT header_normal_forms_nonzero "+string(size(NHf)));
ideal hmons; poly hh; ideal hall=NWf,NHf;
for(a=1;a<=ncols(hall);a++){ hh=hall[a]; while(hh!=0){ hmons=hmons,leadmonom(hh); hh=hh-lead(hh); } }
hmons=simplify(hmons,6);
matrix CW=coeffs(NWf,hmons); matrix CH=coeffs(NHf,hmons);
int hsplit=size(ideal(matrix(hmons)*CW-matrix(NWf)))+size(ideal(matrix(hmons)*CH-matrix(NHf)));
print("RESULT coefficient_split "+string(hsplit));
print("RESULT header_outside_span "+string(size(reduce(module(CH),std(module(CW))))));
matrix Lm=lift(module(CW),module(CH));
print("RESULT lift_residual "+string(size(ideal(CW*Lm-CH))));
int hdeg=0; for(a=1;a<=nrows(Lm);a++){for(b=1;b<=ncols(Lm);b++){ if(deg(Lm[a,b])>hdeg){hdeg=deg(Lm[a,b]);} }}
print("RESULT lift_shape "+string(nrows(Lm))+" "+string(ncols(Lm))+" "+string(hdeg));
print("RESULT lift_determinant_nonzero "+string(det(Lm)!=0));
matrix Gm=inverse(transpose(Lm));
string hrow;
for(a=1;a<=nrows(Gm);a++){ hrow=""; for(b=1;b<=ncols(Gm);b++){ hrow=hrow+" "+string(Gm[a,b]); } print("MAPROW"+hrow); }
poly hbad=HP[1]+s2; poly hbn=reduce(hbad,T0);
ideal hm2=hmons; hh=hbn; while(hh!=0){ hm2=hm2,leadmonom(hh); hh=hh-lead(hh); } hm2=simplify(hm2,6);
matrix CW2=coeffs(NWf,hm2); matrix CB2=coeffs(ideal(hbn),hm2);
print("RESULT control_nonmember_residual "+string(size(reduce(module(CB2),std(module(CW2))))));
"""
)

FRAME_LINES = Template(
    """proc pfn(matrix A){ int nn=nrows(A); if(nn==0){return(poly(1));} if(nn==2){return(A[1,2]);}
  poly acc=0; int jj; int kk; intvec keep; int sg=1;
  for(jj=2;jj<=nn;jj++){ keep=0; int cnt=0; for(kk=2;kk<=nn;kk++){ if(kk!=jj){cnt++; keep[cnt]=kk;} }
    acc=acc+sg*A[1,jj]*pfn(submat(A,keep,keep)); sg=-sg; kill cnt; }
  return(acc); }
matrix FH[15][15];
$entries
matrix TH=transpose(FH)*C*FH;
matrix BH[6][6]=submat(TH,ra,ra); matrix XH[6][9]=submat(TH,ra,rb); matrix DH[9][9]=submat(TH,rb,rb);
poly pBH=pfn(BH);
matrix AH[6][6]; int h1; int h2; int h3; intvec hkeep; int hcnt; poly hcof;
for(h1=1;h1<=6;h1++){for(h2=h1+1;h2<=6;h2++){ hcnt=0; hkeep=0;
  for(h3=1;h3<=6;h3++){ if(h3!=h1 and h3!=h2){hcnt++; hkeep[hcnt]=h3;} }
  hcof=pfn(submat(BH,hkeep,hkeep)); if((h1+h2) mod 2==1){hcof=-hcof;}
  AH[h1,h2]=hcof; AH[h2,h1]=-hcof; }}
print("RESULT header_adjugate_identity "+string(size(ideal(BH*AH-pBH*unitmat(6)))==0));
matrix NHm=pBH*DH+transpose(XH)*AH*XH;
poly pBW=pfn(B);
print("RESULT weight_pivot_square "+string(dB==pBW*pBW));
poly pBH0=pBH; poly pBW0=pBW;
$axis
print("RESULT weight_pivot_on_axis "+string(pBW==pBW0));
print("RESULT pivot_units_at_origin "+string(subst(pBW0,s2,0)!=0)+" "+string(subst(pBH0,s2,0)!=0));
poly u0=pBW0*pBH0;
print("RESULT axis_unit "+string(u0));
"""
)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _gaussian_text(value: tuple[Fraction, Fraction]) -> str:
    return f"({value[0]}+({value[1]})*i)"


def header_frame(boundary_point: tuple[str, ...]) -> tuple[tuple[int, ...], list[list[tuple[Fraction, Fraction]]]]:
    """The pivot and the 15 x 15 frame (complement columns, then kernel columns) of the header producer."""
    import nullity16_basepoints as basepoints

    schur = basepoints.schur
    point = tuple(Fraction(value) for value in boundary_point)
    boundary_c = schur.kernel_lemma._c_matrix(schur.kernel_lemma._original_z_from_split(point))
    pivot, kernel_frame, complement = schur._principal_frame(boundary_c, basepoints.BOUNDARY_C_RANK)
    frame = schur._transformation_matrix(complement, kernel_frame)
    return tuple(pivot), [list(row) for row in frame]


def header_selected(orbit: str) -> list[int]:
    rows = json.loads(REES_RECORD.read_text(encoding="utf-8"))["incidences"]
    row = next(row for row in rows if row["incidence"] == f"E8bar->{orbit}")
    selected = [int(value) for value in row[HEADER_SELECTED_KEY]]
    _require(len(selected) == GENERATORS, "the header record does not list 21 generators")
    return selected


def emit(orbit: str, characteristic: int, root: int, mode: str = "map") -> str:
    """mode map: the induced map; relations: the weight-slice producer's own script."""
    import weight_slice_fiber_relations as ws

    piece = ws.orbit_task(orbit)
    _require(mode in ("map", "relations"), f"unknown mode {mode}")
    if mode == "relations":
        return ws.fiber_script(piece, "e8", characteristic, root)
    _pivot, frame = header_frame(piece.boundary_point)
    entries = "\n".join(
        f"FH[{row + 1},{column + 1}]={_gaussian_text(frame[row][column])};"
        for row in range(15)
        for column in range(15)
        if frame[row][column] != (0, 0)
    )
    axis = "\n".join(f"pBH0=subst(pBH0,s{k},0); pBW0=subst(pBW0,s{k},0);" for k in POSITIVE)
    quadruples = list(itertools.combinations(range(1, 10), 4))
    selected = header_selected(orbit)
    pfaffians = "\n".join(
        "hq++; HP[hq]=reduce(pf4(NHm,{},{},{},{}),J);".format(*quadruples[index - 1]) for index in selected
    )
    grading = piece.grading
    ordering = ",".join(str(max(weight, 1)) for weight in grading) + ",1"
    variables = ",".join(f"s{position}" for position in range(1, 10)) + ",v"
    stage = ws.PFAFFIAN_STAGE.replace(
        "ideal m=maxideal(1);", "ideal m=" + ",".join(f"s{k}" for k in range(1, 10)) + ";"
    )
    _require("ideal m=s1" in stage, "the maximal ideal line of the Pfaffian stage changed")
    return ws.SCRIPT.substitute(
        ring=ws._ring(characteristic, root, variables, f"wp({ordering})"),
        matrix_lines=piece.matrix_lines + "\n" + FRAME_LINES.substitute(entries=entries, axis=axis),
        weights=",".join(str(weight) for weight in grading),
        procedures=ws.PROCEDURES,
        equations=",".join(piece.equations["e8"]),
        component_step=ws.COMPONENT_STEP + "J=std(J+ideal(v*u0-1));\n",
        pfaffian_stage=stage,
        tail=ws.SELECTION_STAGE + HEADER_TAIL.substitute(header_pfaffians=pfaffians),
    )


def _read(log: Path) -> tuple[dict[str, list[str]], list[str]]:
    import weight_slice_fiber_relations as ws

    lines = log.read_text(encoding="utf-8").splitlines()
    _require(not any(line.lstrip().startswith("?") for line in lines), f"{log.name} holds an error line")
    values: dict[str, list[str]] = {}
    for line in lines:
        match = ws.RESULT_LINE.match(line)
        if match is not None:
            values.setdefault(match.group(1), []).append((match.group(2) or "").strip())
    _require(values.get("done") == ["1"], f"the Singular script of {log.name} did not reach its end")
    return values, lines


def collect(log: Path, relation_log: Path, orbit: str) -> dict[str, Any]:
    values, lines = _read(log)
    relation_values, relation_lines = _read(relation_log)
    rows = [line.removeprefix("MAPROW ").split(" ") for line in lines if line.startswith("MAPROW ")]
    relations = sorted(line for line in relation_lines if line.startswith("RELATION "))
    retained = json.loads(WEIGHT_RECORD.read_text(encoding="utf-8"))
    cell = next(
        cell for cell in retained["cells"] if cell["incidence"] == f"E8bar->{orbit}" and cell["field"] == "Q(i)"
    )
    record = {
        "schema": "a5-e8-induced-slice-map-v1",
        "orbit": orbit,
        "values": {key: value for key, value in values.items() if key != "component"},
        "selected_weight": [int(token) for token in values["selected"][0].split(",")],
        "selected_weight_retained": cell["selected_pfaffians_one_based"],
        "selected_header": header_selected(orbit),
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
        "lift_shape": "21 21 0",
        "lift_determinant_nonzero": "1",
        "generators": "21",
    }
    if relation_values.get("relations") != ["148"] or relation_values.get("selected") != values.get("selected"):
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
    if len(rows) != GENERATORS or any(len(row) != GENERATORS for row in rows):
        problems.append("the map is not 21 x 21")
    record["problems"] = problems
    record["pass"] = problems == []
    return record


def _reduce(text: str, prime: int, root: int) -> int:
    import weight_slice_fiber_relations as ws

    real, imaginary = ws.parse_gaussian(text)
    for part in (real, imaginary):
        _require(part.denominator % prime != 0, f"{text} has no residue modulo {prime}")
    residue = real.numerator * pow(real.denominator, -1, prime) + root * imaginary.numerator * pow(
        imaginary.denominator, -1, prime
    )
    return residue % prime


def check_script(record: dict[str, Any], prime: int, root: int, header_rel: Path, weight_ka: Path | None) -> str:
    import weight_slice_fiber_relations as ws

    _require(pow(root, 2, prime) == prime - 1, "the root is not a square root of -1")
    quadrics = []
    for line in record["relations"]:
        quadrics.append(
            "+".join(
                f"{_reduce(coefficient, prime, root)}*y({key[0]})*y({key[1]})"
                for key, coefficient in ws.parse_relation(line)
            )
        )
    images = [
        "+".join(f"{_reduce(entry, prime, root)}*y({column + 1})" for column, entry in enumerate(row))
        for row in record["map"]
    ]
    header = header_rel.read_text(encoding="utf-8").strip()
    if header.startswith("ideal"):
        header = header.split("=", 1)[1].rstrip().rstrip(";")
    lines = [
        f"ring r={prime},(y(1..{GENERATORS})),dp; option(redSB);",
        "ideal KW=" + ",\n".join(quadrics) + ";",
        "ideal KH=" + header + ";",
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
        '"RESULT control identity",c1,c2,"control perturbed",d1,d2,"control header generators 1 and 2 swapped",s1,s2;',
        "int good=(a1==0 and a2==0 and size(minbase(fK))==148 and dim(sF)==5 and mult(sF)==11 and dt!=0"
        " and (c1>0 or c2>0) and (d1>0 or d2>0) and (s1>0 or s2>0));",
    ]
    if weight_ka is not None:
        retained = weight_ka.read_text(encoding="utf-8").strip().split("=", 1)[1].rstrip().rstrip(";")
        lines += [
            "ideal KA=" + retained + "; ideal sA=std(KA);",
            "int e1=size(reduce(KW,sA)); int e2=size(reduce(KA,sW));",
            '"RESULT reduced Q(i) weight relations against the retained modular file",e1,e2;',
            "good=(good and e1==0 and e2==0);",
        ]
    lines += [
        f'string hv="INDUCED VERDICT p {prime} root {root} ";',
        'if(good){hv+"PASS";}else{hv+"FAIL";}',
        '"EXIT 0"; quit;',
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    arguments = sys.argv[1:]
    if arguments[:1] == ["--emit"]:
        mode = arguments[4] if len(arguments) > 4 else "map"
        sys.stdout.write(emit(arguments[1], int(arguments[2]), int(arguments[3]), mode))
    elif arguments[:1] == ["--collect"]:
        record = collect(Path(arguments[1]), Path(arguments[2]), arguments[3])
        Path(arguments[4]).write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        print("COLLECT", arguments[3], "PASS" if record["pass"] else f"FAIL {record['problems']}")
        if not record["pass"]:
            raise SystemExit(1)
    elif arguments[:1] == ["--check"]:
        record = json.loads(Path(arguments[1]).read_text(encoding="utf-8"))
        weight = Path(arguments[5]) if len(arguments) > 5 else None
        sys.stdout.write(check_script(record, int(arguments[2]), int(arguments[3]), Path(arguments[4]), weight))
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
