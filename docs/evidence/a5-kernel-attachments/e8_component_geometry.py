"""The three associated primes of the E8-bar quadric ideal over Q(i): how they meet, and the singular locus of each.

The quadric ideal K of E8-bar (148 quadrics on 21 generators, `weight_slice_fiber_relations.py`) has two minimal
primes and one embedded prime (A5-451, A5-454). This producer regenerates the quadrics at N- and N+ and computes over
Q(i) in Singular:

- the embedded prime A = K : rad K: its linear forms, the rank of its quadric modulo them and its vertex;
- the minimal prime of dimension 4 (the scroll prime): generator degrees, Betti table and singular locus;
- the minimal prime of dimension 5 (the main prime): linear forms, quadrics, second Hilbert numerator, Betti table;
- the three pairwise sums, with the containments among them;
- the singular locus of the main prime. With the linear forms eliminated the main prime is an ideal of quadrics in
  nf free variables and codimension cd. A set that contains the singular locus comes from chosen cd x cd minors of
  the Jacobian matrix (every minor vanishes on the singular locus, so any subset bounds it from outside). On each
  component W of that set the singular locus is cut out exactly by the Fitting ideal of the Jacobian cokernel modulo
  W, which Singular computes from a pruned presentation; the union over the components is the singular locus. Each
  resulting component Z carries a two-sided bound of the generic Jacobian rank on Z, valid when Z is linear, which
  the checker requires (degree 1): the entries of the Jacobian reduced modulo Z then lie in the free coordinates of
  Z, so values for those coordinates give a point of Z; the rank there bounds the generic rank from below, and nf
  minus the rank there of the syzygy module of the reduced Jacobian bounds it from above. On a nonlinear component
  entrywise reduction would not give a point of the component, and the bound would not hold;
- the vertex space of the main prime (the common zeros of all partial derivatives of its quadrics), the 2 x 4 matrix
  of linear forms whose minors are the six quadrics of the scroll prime, with the ratio of its two rows on the
  meeting of the components, and the multiplicity of the tangent cone of the main prime at one point of the singular
  line, of the singular plane and of the meeting.

Run from the repository root: "$PYTHON" docs/evidence/a5-kernel-attachments/e8_component_geometry.py [--check]
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

RECORD = HERE / "e8-component-geometry-result.json"
SCHEMA = "gororoba.a5.e8-component-geometry/1"
INPUTS = ("e8_component_geometry.py", "weight_slice_fiber_relations.py")
WEIGHT_SLICE = HERE / "weight-slice-fiber-relations-result.json"
ORBITS = ("N-", "N+")
GENERATORS = 21
# What every cell holds. Pairs are (dimension, degree) of the affine cone. A singular component is
# (dimension, degree, generic Jacobian rank from below, from above, inside the main prime, inside the sum of the two
# minimal primes, inside the embedded prime, equal to the vertex of the embedded prime), sorted.
EXPECTED: dict[str, Any] = {
    "minimal_primes": 2,
    "scroll_prime": [4, 4],
    "main_prime": [5, 11],
    "embedded_prime": [4, 2],
    "embedded_contains_main": True,
    "embedded_contains_scroll": False,
    "scroll_meets_main": [3, 1],
    "scroll_meets_main_is_linear": True,
    "scroll_meets_main_contains_embedded": True,
    "scroll_meets_embedded": [3, 1],
    "scroll_meets_embedded_equals_scroll_meets_main": True,
    "embedded_linear_forms": 16,
    "embedded_quadric_rank": 4,
    "embedded_vertex": [1, 1],
    "scroll_generator_degrees": [1] * 14 + [2] * 6,
    "scroll_betti": [[1, 0, 0, 0], [0, 6, 8, 3]],
    "scroll_singular_locus": 0,
    "main_linear_forms": 9,
    "main_residual_generator_degrees": [2] * 25,
    "main_hilbert_second": [1, 7, 3],
    "main_betti": [
        [1, 0, 0, 0, 0, 0, 0, 0],
        [0, 25, 91, 147, 119, 35, 6, 0],
        [0, 0, 0, 0, 0, 21, 14, 3],
    ],
    "main_free_variables": 12,
    "main_codimension": 7,
    # Each walk: (row family, minors tried so far, minors kept so far, dimension and degree of the bound after it).
    "walk": [[1, 198000, 1394, 3, 13], [2, 435600, 1657, 3, 4]],
    # Each component of the outer bound: (dimension, degree, dimension of its singular part).
    "bound_components": 8,
    "bound_component_dimensions": [
        [2, 1, 0],
        [2, 1, 0],
        [2, 1, 1],
        [2, 1, 1],
        [2, 1, 1],
        [3, 1, 1],
        [3, 1, 1],
        [3, 1, 2],
    ],
    "bound_components_with_smooth_points": 8,
    "smooth_rank": [7, 7],
    "singular_locus": [2, 1],
    "singular_components": [
        [1, 1, 4, 4, True, True, True, True],
        [2, 1, 6, 6, True, True, True, False],
    ],
    "main_vertex_space": 0,
    "scroll_is_linear_forms_plus_matrix_minors": True,
    "scroll_rows_proportional_on_meeting": True,
    # Tangent cones of the main prime: (dimension of the locus the point lies on, dimension, multiplicity).
    "tangent_cones": [[1, 5, 4], [2, 5, 2], [3, 5, 1]],
    "main_is_cohen_macaulay": True,
    "main_is_gorenstein": False,
    "main_is_normal": True,
}
# The minimal generators of the two components of the singular locus, as Singular prints them, the line first. The
# checker compares the lists, since dimensions and degrees alone would accept any line and any plane.
SINGULAR_GENERATORS: dict[str, tuple[str, ...]] = {
    "N-": (
        "y(21),y(20),y(19),y(18),y(17),y(15)+(i)*y(16),y(14),y(13),y(12),y(11)+(i)*y(16),y(10)+y(16),y(9),y(8),y(7),"
        "y(6),y(5),y(4),y(3),y(2),y(1)",
        "y(21),y(20),y(18)+(i)*y(19),y(17),y(16),y(15),y(13),y(12),y(11),y(10),y(9)+(i)*y(14),y(8),y(7),y(6),y(5),"
        "y(4),y(3),y(2),y(1)",
    ),
    "N+": (
        "y(21),y(20),y(19),y(18),y(17),y(15)+(-i)*y(16),y(14),y(13),y(12),y(11)+(-i)*y(16),y(10)+y(16),y(9),y(8),"
        "y(7),y(6),y(5),y(4),y(3),y(2),y(1)",
        "y(21),y(20),y(18)+(-i)*y(19),y(17),y(16),y(15),y(13),y(12),y(11),y(10),y(9)+(-i)*y(14),y(8),y(7),y(6),y(5),"
        "y(4),y(3),y(2),y(1)",
    ),
}
# The constant c with (second row) = c (first row) for the scroll matrix on the meeting of the two components.
SCROLL_ROW_RATIO: dict[str, str] = {"N-": "(-i)", "N+": "(i)"}
SCRIPT = r"""LIB "primdec.lib"; LIB "homolog.lib"; LIB "matrix.lib"; option(redSB);
int k; int j; int j2; int a; int s0; int q; int w; int ok; int fam; int n; int tried;
intvec pv=2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73;
proc ranks(ideal W, matrix M, intvec pv){ ideal sW=std(W); matrix Mw=reduce(M,sW); matrix Mp=Mw; int a;
  for(a=1;a<=nvars(basering);a++){ Mp=subst(Mp,var(a),pv[a]); }
  module Kz=syz(module(Mw)); matrix Kp=matrix(Kz); for(a=1;a<=nvars(basering);a++){ Kp=subst(Kp,var(a),pv[a]); }
  return(string(rank(Mp))+","+string(ncols(M)-rank(Kp))); }
proc bettirows(intmat B){ string s=""; int a; int b;
  for(a=1;a<=nrows(B);a++){ if(a>1){ s=s+";"; } for(b=1;b<=ncols(B);b++){ if(b>1){ s=s+","; } s=s+string(B[a,b]); } }
  return(s); }
list L=minAssGTZ(K); ideal P4; ideal P11; ideal comp;
for(k=1;k<=size(L);k++){ comp=std(L[k]); if(dim(comp)==4){ P4=L[k]; } if(dim(comp)==5){ P11=L[k]; } }
ideal R=intersect(P4,P11); ideal A=std(quotient(K,R));
ideal sP4=std(P4); ideal sP11=std(P11);
print("RESULT minimal_primes "+string(size(L)));
print("RESULT scroll_prime "+string(dim(sP4))+","+string(mult(sP4)));
print("RESULT main_prime "+string(dim(sP11))+","+string(mult(sP11)));
print("RESULT embedded_prime "+string(dim(A))+","+string(mult(A)));
print("RESULT embedded_contains_main "+string(size(reduce(P11,A))==0));
print("RESULT embedded_contains_scroll "+string(size(reduce(P4,A))==0));
ideal I12=std(P4+P11); print("RESULT scroll_meets_main "+string(dim(I12))+","+string(mult(I12)));
ideal mI12=minbase(I12); int lin12=1; for(k=1;k<=size(mI12);k++){ if(deg(mI12[k])!=1){ lin12=0; } }
print("RESULT scroll_meets_main_is_linear "+string(lin12));
print("RESULT scroll_meets_main_contains_embedded "+string(size(reduce(A,I12))==0));
ideal I1A=std(P4+A); print("RESULT scroll_meets_embedded "+string(dim(I1A))+","+string(mult(I1A)));
print("RESULT scroll_meets_embedded_equals_scroll_meets_main "
  +string(size(reduce(I1A,I12))==0 and size(reduce(I12,I1A))==0));
ideal mA=minbase(A); ideal linA; poly quadA;
for(k=1;k<=size(mA);k++){ if(deg(mA[k])==1){ linA=linA,mA[k]; } else { quadA=mA[k]; } }
linA=std(simplify(linA,2)); quadA=reduce(quadA,linA);
matrix HA=jacob(jacob(quadA)); print("RESULT embedded_linear_forms "+string(size(linA)));
print("RESULT embedded_quadric_rank "+string(rank(HA)));
ideal vertA=std(linA+jacob(quadA)); print("RESULT embedded_vertex "+string(dim(vertA))+","+string(mult(vertA)));
ideal m4=minbase(P4); intvec d4; for(k=1;k<=size(m4);k++){ d4[k]=deg(m4[k]); }
print("RESULT scroll_generator_degrees "+string(d4));
ideal lin4; ideal quad4;
for(k=1;k<=size(m4);k++){ if(deg(m4[k])==1){ lin4=lin4,m4[k]; } else { quad4=quad4,m4[k]; } }
lin4=std(simplify(lin4,2)); quad4=simplify(reduce(quad4,lin4),2);
resolution r4=mres(quad4,0); print("RESULT scroll_betti "+bettirows(intmat(betti(r4))));
ideal s4=std(lin4+quad4+minor(jacob(quad4),3)); print("RESULT scroll_singular_locus "+string(dim(s4)));
ideal m11=minbase(P11); ideal lin11; ideal Pc;
for(k=1;k<=size(m11);k++){ if(deg(m11[k])==1){ lin11=lin11,m11[k]; } else { Pc=Pc,m11[k]; } }
lin11=std(simplify(lin11,2)); Pc=simplify(reduce(Pc,lin11),2);
intvec d11; for(k=1;k<=size(Pc);k++){ d11[k]=deg(Pc[k]); }
print("RESULT main_linear_forms "+string(size(lin11)));
print("RESULT main_residual_generator_degrees "+string(d11));
print("RESULT main_hilbert_second "+string(hilb(sP11,2)));
resolution r11=mres(Pc,0); print("RESULT main_betti "+bettirows(intmat(betti(r11))));
intvec fv; n=0; for(a=1;a<=nvars(basering);a++){ if(reduce(var(a),lin11)==var(a)){ n++; fv[n]=a; } }
int nf=n; int cd=nf-dim(sP11); int m=size(Pc);
print("RESULT main_free_variables "+string(nf));
print("RESULT main_codimension "+string(cd));
matrix Jfull=jacob(Pc); matrix J[m][nf]; for(k=1;k<=m;k++){ for(a=1;a<=nf;a++){ J[k,a]=Jfull[k,fv[a]]; } }
ideal U=sP11; n=0; tried=0; intvec rr; intvec cc; poly d; int more;
for(fam=1;fam<=2;fam++){ for(a=1;a<=(m div 2);a++){ for(s0=0;s0<m;s0++){
  for(j=1;j<=cd;j++){ if(fam==1){ rr[j]=(s0+(j-1)*a) mod m + 1; }
    else { if(j<=4){ rr[j]=(s0+j-1) mod m + 1; } else { rr[j]=(s0+3+a+(j-5)*2) mod m + 1; } } }
  ok=1; for(j=1;j<=cd;j++){ for(j2=j+1;j2<=cd;j2++){ if(rr[j]==rr[j2]){ ok=0; } } }
  if(ok==1){ for(j=1;j<=cd;j++){ cc[j]=j; } more=1;
    while(more==1){
      d=det(submat(J,rr,cc)); tried++;
      if(d!=0){ if(reduce(d,U)!=0){ U=std(U,d); n++; } }
      j=cd; while(j>=1){ if(cc[j]<nf-cd+j){ break; } j--; }
      if(j<1){ more=0; } else { cc[j]=cc[j]+1; for(j2=j+1;j2<=cd;j2++){ cc[j2]=cc[j2-1]+1; } }
    } }
}}
print("RESULT walk "+string(fam)+","+string(tried)+","+string(n)+","+string(dim(U))+","+string(mult(U))); }
list MU=minAssGTZ(U); print("RESULT bound_components "+string(size(MU)));
ideal W; ideal F; ideal S; matrix Jr; module Mp; ideal acc=1; list LS; int smooth=0;
for(w=1;w<=size(MU);w++){ W=std(MU[w]); Jr=reduce(J,W); Mp=prune(module(transpose(Jr)));
  F=fitting(Mp,nf-cd); S=std(F+W);
  print("RESULT bound_component "+string(dim(W))+","+string(mult(W))+","+string(dim(S)));
  if(dim(S)<dim(W)){ smooth++; }
  if(dim(S)>=0){ LS=minAssGTZ(S); for(q=1;q<=size(LS);q++){ acc=intersect(acc,LS[q]); } } }
print("RESULT bound_components_with_smooth_points "+string(smooth));
acc=std(acc); print("RESULT singular_locus "+string(dim(acc))+","+string(mult(acc)));
list LA=minAssGTZ(acc); ideal Z;
for(q=1;q<=size(LA);q++){ Z=std(LA[q]);
  print("RESULT singular_component "+string(dim(Z))+","+string(mult(Z))+","+ranks(Z,J,pv)+","
    +string(size(reduce(P11,Z))==0)+","+string(size(reduce(I12,Z))==0)+","+string(size(reduce(A,Z))==0)+","
    +string(size(reduce(Z,vertA))==0 and size(reduce(vertA,Z))==0));
  print("RESULT singular_generators "+string(dim(Z))+" "+string(minbase(Z))); }
print("RESULT smooth_rank "+ranks(P4+P11,J,pv));
// a cone has a vertex where every partial derivative of every quadric vanishes
ideal vert11=std(lin11+ideal(jacob(Pc))); print("RESULT main_vertex_space "+string(dim(vert11)));
// the scroll: six quadrics that are the 2 x 2 minors of a 2 x 4 matrix of linear forms; its rows on the meeting
matrix B[2][4]=y(19),y(16),y(15),y(14),y(18),y(15),y(10),y(9);
print("RESULT scroll_is_linear_forms_plus_matrix_minors "
  +string(size(reduce(P4,std(lin4+minor(B,2))))==0 and size(reduce(minor(B,2),sP4))==0));
matrix Br=reduce(B,I12); number ratio=0; int piv=0; int prop=1;
for(j=1;j<=4;j++){ if(piv==0 and Br[1,j]!=0){ piv=j; ratio=leadcoef(Br[2,j])/leadcoef(Br[1,j]); } }
for(j=1;j<=4;j++){ if(Br[2,j]-ratio*Br[1,j]!=0){ prop=0; } }
print("RESULT scroll_rows_proportional_on_meeting "+string(piv>0 and prop==1 and ratio!=0));
print("RESULT scroll_row_ratio_on_meeting "+string(ratio));
// multiplicity of the tangent cone of the main prime at one point of each singular component and of the meeting
ideal sh; list shifts; intvec shiftdims; ideal Zs; poly co;
list PT=LA; PT[size(LA)+1]=ideal(I12);
for(q=1;q<=size(PT);q++){ Zs=std(PT[q]); sh=0;
  for(a=1;a<=nvars(basering);a++){ co=reduce(var(a),Zs);
    for(j=1;j<=nvars(basering);j++){ co=subst(co,var(j),pv[j]); }
    sh[a]=var(a)+co; }
  shifts[q]=sh; shiftdims[q]=dim(Zs); }
ring rl=(0,i),(y(1..21)),ds; minpoly=i^2+1;
ideal P11l=imap(r,P11); list shl=imap(r,shifts); map tr; ideal T;
for(q=1;q<=size(shl);q++){ tr=rl,ideal(shl[q]); T=std(tr(P11l));
  print("RESULT tangent_cone "+string(shiftdims[q])+","+string(dim(T))+","+string(mult(T))); }
setring r;
print("RESULT done 1");
quit;
"""


def _integers(text: str) -> list[int]:
    return [int(part) for part in text.split(",") if part.strip() != ""]


def _flag(values: dict[str, list[str]], key: str) -> bool:
    return values[key] == ["1"]


def _rows(text: str) -> list[list[int]]:
    return [_integers(row) for row in text.split(";")]


def derived(cell: dict[str, Any]) -> dict[str, bool]:
    """Cohen-Macaulay, Gorenstein and normal for the main prime, read from its Betti table and singular locus.

    The quotient by the quadrics in the free variables has projective dimension the length of the Betti table minus
    one; it is Cohen-Macaulay when that equals the codimension (Auslander-Buchsbaum), Gorenstein when moreover the
    last module has rank one, and normal when it is Cohen-Macaulay with a singular locus of codimension at least two
    (Serre's criterion).
    """
    betti = cell["main_betti"]
    last = sum(row[-1] for row in betti)
    cohen_macaulay = len(betti[0]) - 1 == cell["main_codimension"]
    return {
        "main_is_cohen_macaulay": cohen_macaulay,
        "main_is_gorenstein": cohen_macaulay and last == 1,
        "main_is_normal": cohen_macaulay and cell["main_prime"][0] - cell["singular_locus"][0] >= 2,
    }


def certify(orbit: str) -> dict[str, Any]:
    run = ws.run_singular(ws.fiber_script(ws.orbit_task(orbit), "e8", 0, 0))
    polynomials = ",\n".join(
        "+".join(f"({coefficient})*{'*'.join(f'y({index})' for index in key)}" for key, coefficient in relation)
        for relation in (ws.parse_relation(line) for line in run["relations"])
    )
    script = ws._ring(0, 0, f"y(1..{GENERATORS})", "dp") + f"\nideal K={polynomials};\n" + SCRIPT
    values = ws.run_singular(script)["values"]
    components = sorted(
        [*parts[:4], *(bool(part) for part in parts[4:])]
        for parts in (_integers(text) for text in values["singular_component"])
    )
    generators = [text.split(" ", 1)[1] for text in sorted(values["singular_generators"])]
    cell: dict[str, Any] = {
        "orbit": orbit,
        "relations_sha256": ws.summarize_fiber_run(run)["relations_sha256"],
        "minimal_primes": int(values["minimal_primes"][0]),
        "embedded_linear_forms": int(values["embedded_linear_forms"][0]),
        "embedded_quadric_rank": int(values["embedded_quadric_rank"][0]),
        "scroll_generator_degrees": sorted(_integers(values["scroll_generator_degrees"][0])),
        "scroll_betti": _rows(values["scroll_betti"][0]),
        "scroll_singular_locus": int(values["scroll_singular_locus"][0]),
        "main_linear_forms": int(values["main_linear_forms"][0]),
        "main_residual_generator_degrees": _integers(values["main_residual_generator_degrees"][0]),
        # Singular ends the second Hilbert series with a marker entry that is not a coefficient.
        "main_hilbert_second": _integers(values["main_hilbert_second"][0])[:-1],
        "main_betti": _rows(values["main_betti"][0]),
        "main_free_variables": int(values["main_free_variables"][0]),
        "main_codimension": int(values["main_codimension"][0]),
        "walk": [_integers(text) for text in values["walk"]],
        "bound_components": int(values["bound_components"][0]),
        "bound_component_dimensions": sorted(_integers(text) for text in values["bound_component"]),
        "bound_components_with_smooth_points": int(values["bound_components_with_smooth_points"][0]),
        "singular_components": components,
        "singular_generators": generators,
        "main_vertex_space": int(values["main_vertex_space"][0]),
        "scroll_row_ratio_on_meeting": values["scroll_row_ratio_on_meeting"][0],
        "tangent_cones": sorted(_integers(text) for text in values["tangent_cone"]),
    }
    for key in (
        "scroll_prime",
        "main_prime",
        "embedded_prime",
        "scroll_meets_main",
        "scroll_meets_embedded",
        "embedded_vertex",
        "smooth_rank",
        "singular_locus",
    ):
        cell[key] = _integers(values[key][0])
    for key in (
        "embedded_contains_main",
        "embedded_contains_scroll",
        "scroll_meets_main_is_linear",
        "scroll_meets_main_contains_embedded",
        "scroll_meets_embedded_equals_scroll_meets_main",
        "scroll_is_linear_forms_plus_matrix_minors",
        "scroll_rows_proportional_on_meeting",
    ):
        cell[key] = _flag(values, key)
    cell.update(derived(cell))
    return cell


def _bound_problems(cell: dict[str, Any]) -> list[str]:
    """The outer bound of the singular locus: its components, their singular parts and the locus they give."""
    orbit = cell["orbit"]
    parts = cell.get("bound_component_dimensions")
    if not isinstance(parts, list) or not parts or any(not isinstance(part, list) or len(part) != 3 for part in parts):
        return [f"{orbit}: the components of the outer bound are missing"]
    found: list[str] = []
    if cell.get("bound_components") != len(parts):
        found.append(f"{orbit}: the outer bound lists a number of components that differs from its count")
    smooth = sum(1 for dimension, _degree, singular in parts if singular < dimension)
    if cell.get("bound_components_with_smooth_points") != smooth:
        found.append(f"{orbit}: the count of bound components with smooth points differs from the list")
    if smooth != len(parts):
        found.append(f"{orbit}: a component of the outer bound lies inside the singular locus")
    locus = cell.get("singular_locus")
    if isinstance(locus, list) and locus and locus[0] != max(singular for _d, _e, singular in parts):
        found.append(f"{orbit}: the singular locus has a dimension that differs from the largest singular part")
    walk = cell.get("walk")
    if not isinstance(walk, list) or [row[0] for row in walk if isinstance(row, list) and row] != [1, 2]:
        found.append(f"{orbit}: the two minor walks are missing")
    return found


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
        orbit = cell["orbit"]
        for key, expected in EXPECTED.items():
            # A boolean equals the integer of the same value in Python; the JSON text tells them apart at every depth.
            if json.dumps(cell.get(key)) != json.dumps(expected):
                found.append(f"{orbit}: {key} differs from {expected}")
        if cell.get("singular_generators") != list(SINGULAR_GENERATORS[orbit]):
            found.append(f"{orbit}: the generators of the singular components differ from the line and the plane")
        if cell.get("scroll_row_ratio_on_meeting") != SCROLL_ROW_RATIO[orbit]:
            found.append(f"{orbit}: the ratio of the scroll matrix rows on the meeting differs")
        found += _bound_problems(cell)
        try:
            flags = derived(cell)
        except (KeyError, TypeError, IndexError):
            found.append(f"{orbit}: the Betti table, codimension or singular locus is missing")
            continue
        for key, value in flags.items():
            if cell.get(key) is not value:
                found.append(f"{orbit}: {key} differs from what the Betti table and the singular locus give")
    if record.get("pass") is not (found == []):
        found.append("the pass flag differs from the verdict")
    return found


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def slice_problems(record: dict[str, Any]) -> list[str]:
    """The relation digests against the E8-bar cells over Q(i) of the weight-slice record."""
    retained = {
        cell["orbit"]: cell["relations_sha256"]
        for cell in json.loads(WEIGHT_SLICE.read_text(encoding="utf-8"))["cells"]
        if cell["characteristic"] == 0 and cell["source"] == "e8"
    }
    return [
        f"{cell['orbit']}: the relations differ from those of the weight-slice record"
        for cell in record.get("cells", [])
        if cell.get("relations_sha256") != retained.get(cell.get("orbit"))
    ]


def check_problems(record: dict[str, Any]) -> list[str]:
    """Every check of a stored record: the claim, the weight-slice relations and the input digests."""
    found = problems(record) + slice_problems(record)
    inputs = record.get("inputs")
    for name in INPUTS:
        if not isinstance(inputs, dict) or inputs.get(name) != _digest(HERE / name):
            found.append(f"input digest of {name} differs")
    if record.get("weight_slice_record_sha256") != _digest(WEIGHT_SLICE):
        found.append("digest of the weight-slice record differs")
    return found


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
        found = check_problems(json.loads(RECORD.read_text(encoding="utf-8")))
        if found:
            raise SystemExit("\n".join(found))
        print("e8-component-geometry-result.json: pass")
        return
    record = build()
    found = check_problems(record)
    record["pass"] = found == []
    RECORD.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"pass": record["pass"], "problems": found}, indent=1))
    if found:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
