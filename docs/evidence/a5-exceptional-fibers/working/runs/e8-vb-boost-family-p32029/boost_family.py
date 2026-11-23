"""The degree-2 relations of the fiber cone of E8-bar -> VB along the boost, over F_32029(w).

The boost u -> c u + s v, v -> s u + c v with c = (w^2 + 1) / (2 w), s = (w^2 - 1) / (2 w) moves the retained VB
basepoint along the one direction of its orbit that G_2(C) x C^* does not reach (w = 1 is the retained point; w = 2,
3 and 2/3 are the three boosts of boost_e8_vb_quadrics.py). This producer rewrites the Singular script of that
record with the basepoint as a function of w: the germ of the E8-bar closure on the retained slice columns, the
Schur form of the principal block of C(z) on the retained pivot, the Nakayama selection among its 21 entries and the
relations {q : q(G) in J + m I^2}, then the invariants of the quadric ideal K(w) and its image under the adapted
frame of the two component spans.

--emit generic writes the script over the function field F_32029(w); --emit NUMBER writes it over F_32029 with w
that number, where it also compares the Schur entries with the retained ones (equal at w = 1).
"""

from __future__ import annotations

import re
import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE.parents[3]
ATTACH = EVIDENCE / "a5-kernel-attachments"
sys.path.insert(0, str(ATTACH))

PRIME, ROOT = 32029, 9115
COSH, SINH = "((w^2+1)/(2*w))", "((w^2-1)/(2*w))"

SCHUR = """proc pfn(matrix A){ int nn=nrows(A); if(nn==0){return(poly(1));} if(nn==2){return(A[1,2]);}
  poly acc=0; int jj; int kk; intvec keep; int sg=1; int cnt;
  for(jj=2;jj<=nn;jj++){ keep=0; cnt=0; for(kk=2;kk<=nn;kk++){ if(kk!=jj){cnt++; keep[cnt]=kk;} }
    acc=acc+sg*A[1,jj]*pfn(submat(A,keep,keep)); sg=-sg; }
  return(acc); }
matrix CZ[15][15];
@CLINES@
intvec vp=@PIVOT@; intvec vf=@FREE@; int np=size(vp); int nf=size(vf);
matrix BH=submat(CZ,vp,vp); matrix XH=submat(CZ,vp,vf); matrix DH=submat(CZ,vf,vf);
poly pBH=pfn(BH);
matrix AH[np][np]; int h1; int h2; int h3; intvec hkeep; int hcnt; poly hcof;
for(h1=1;h1<=np;h1++){for(h2=h1+1;h2<=np;h2++){ hcnt=0; hkeep=0;
  for(h3=1;h3<=np;h3++){ if(h3!=h1 and h3!=h2){hcnt++; hkeep[hcnt]=h3;} }
  hcof=pfn(submat(BH,hkeep,hkeep)); if((h1+h2) mod 2==1){hcof=-hcof;}
  AH[h1,h2]=hcof; AH[h2,h1]=-hcof; }}
"RESULT adjugate_identity",size(ideal(BH*AH-pBH*unitmat(np)))==0;
"RESULT pivot_pfaffian_at_origin_nonzero",jet(pBH,0)!=0;
matrix NH=pBH*DH+transpose(XH)*AH*XH;
ideal FullF; int hq=0;
for(h1=1;h1<=nf;h1++){for(h2=h1+1;h2<=nf;h2++){ hq++; FullF[hq]=NH[h1,h2]; }}
"""

TAIL = """setring Y; module SY=imap(R0,S); ideal K; poly kq;
for(j=1;j<=size(SY);j++){ kq=0; for(b=1;b<=c;b++){ kq=kq+SY[j][b]*kb[b]; } K[j]=kq; }
option(redSB); ideal sK=std(K);
"RESULT k_generators",size(minbase(K)),"dim",dim(sK),"mult",mult(sK);
"RESULT k_numerator",hilb(sK,1);
LIB "primdec.lib"; list PL=minAssGTZ(K); ideal pc; ideal lin; int lc; ideal four;
for(i=1;i<=size(PL);i++){ pc=std(PL[i]); lin=0; lc=0;
  for(k=1;k<=size(pc);k++){ if(deg(pc[k])==1){ lc++; lin[lc]=pc[k]; } }
  "RESULT prime",dim(pc),mult(pc),lc;
  if(lc==4){ four=std(lin); } }
ideal allp=PL[1]; for(i=2;i<=size(PL);i++){ allp=intersect(allp,PL[i]); }
"RESULT prime_count",size(PL);
"RESULT radical",size(reduce(allp,sK))==0;
poly n1=reduce(y(1),four); poly n5=reduce(y(5),four); poly n2=reduce(y(2),four); poly n4=reduce(y(4),four);
number fa=-1/leadcoef(diff(n1,y(10))); number fb=-1/leadcoef(diff(n5,y(9)));
number fd=-fa*leadcoef(diff(n4,y(10)));
"RESULT frame_a",fa; "RESULT frame_b",fb; "RESULT frame_d",fd;
"RESULT frame_consistent",(n2+(1/fb)*y(8)==0) and (n1+(1/fa)*y(10)==0) and (n5+(1/fb)*y(9)==0);
map phi=Y,y(8),y(9),y(2),(y(3)-y(7)+fd*y(8))/2,y(10),(y(3)+y(7)-fd*y(8))/2,y(1),y(6)-fb*y(9),y(5)-fb*y(10),
  y(4)-(fd/2)*y(7)-fa*y(8);
ideal mx=maxideal(1); ideal pim=phi(mx);
"RESULT frame_determinant_nonzero",det(jacob(pim))!=0;
ideal NK=std(phi(K));
"RESULT normal_form_size",size(NK);
for(i=1;i<=size(NK);i++){"NORMALFORM "+string(NK[i]);}
ideal CK=std(K);
for(i=1;i<=size(CK);i++){"KBASIS "+string(CK[i]);}
"RESULT done 1";
quit;
"""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _moved(point: list[Fraction]) -> list[str]:
    left, middle, right = point[0:7], point[7], point[8:15]
    out = [f"({COSH}*({a})+{SINH}*({b}))" for a, b in zip(left, right, strict=True)]
    out.append(f"({middle})")
    out += [f"({SINH}*({a})+{COSH}*({b}))" for a, b in zip(left, right, strict=True)]
    return out


def emit(value: str) -> str:
    import boost_e8_vb_quadrics as bq
    import weight_slice_fiber_relations as ws

    generic = value == "generic"
    identity = (Fraction(1), Fraction(0))
    task, data, _candidates, _geometry = bq.moved_inputs(identity)
    text = bq.relation_script(identity, 2)
    point = [Fraction(entry) for entry in task.row["boundary_point"]]
    # The boost of the regularity verifier at (c, s) = (5/4, 3/4) fixes the convention of _moved.
    check = bq.boosts_record.independent.act_boost(Fraction(5, 4), Fraction(3, 4), point)
    mine = [Fraction(5, 4) * a + Fraction(3, 4) * b for a, b in zip(point[0:7], point[8:15], strict=True)]
    mine += [point[7]] + [Fraction(3, 4) * a + Fraction(5, 4) * b for a, b in zip(point[0:7], point[8:15], strict=True)]
    _require([Fraction(entry) for entry in check] == mine, "the boost convention differs from act_boost")
    moved = _moved(point)
    columns = tuple(data.slice_columns)
    split = [f"({moved[k]}+t{columns.index(k) + 1})" if k in columns else moved[k] for k in range(15)]
    schur = bq.nakayama.resolved
    boundary_c = schur.kernel_lemma._c_matrix(schur.kernel_lemma._original_z_from_split(tuple(point)))
    rank = schur.kernel_lemma._rank(boundary_c)
    pivot = tuple(schur._find_principal_pivot(boundary_c, rank))
    free = tuple(index for index in range(15) if index not in pivot)
    basis = ws._c_basis()
    lines = []
    for row in range(15):
        for column in range(row + 1, 15):
            terms = []
            for index in range(15):
                entry = basis[index][row, column]
                if entry != 0:
                    real, imaginary = entry.as_real_imag()
                    phase = ("1", "I", "-1", "-I")[(index + 1).bit_count() % 4]
                    terms.append(f"(({real})+({imaginary})*I)*({phase})*{split[index]}")
            if terms:
                upper, lower = f"CZ[{row + 1},{column + 1}]", f"CZ[{column + 1},{row + 1}]"
                lines.append(f"{upper}={'+'.join(terms)}; {lower}=-{upper};")
    block = (
        SCHUR.replace("@CLINES@", "\n".join(lines))
        .replace("@PIVOT@", ",".join(str(index + 1) for index in pivot))
        .replace("@FREE@", ",".join(str(index + 1) for index in free))
    )
    out = []
    for line in text.splitlines():
        if line.startswith(("ring r=", "ring s=", "ring Y=")):
            if generic:
                line = line.replace(f"={PRIME},", f"=({PRIME},w),", 1)
            else:
                line = line + f" number w={value};"
        if line.startswith("map sliceMap=r,"):
            line = "map sliceMap=r," + ",".join(split) + ";"
        if line.startswith("ideal FullF="):
            retained = line.removeprefix("ideal FullF=")
            line = block
            if not generic:
                line += "ideal FullR=" + retained + "\n"
                line += '"RESULT schur_matches_retained",size(ideal(matrix(FullF)-matrix(FullR)))==0;'
        if line.startswith("ideal F="):
            line = "ideal F=FullF;"
        if line == "quit;":
            line = TAIL
        out.append(line)
    script = "\n".join(out).rstrip("\n") + "\n"
    _require(
        script.count("map sliceMap=r,") == 1 and "ideal F=FullF;" in script and "NORMALFORM" in script, "surgery failed"
    )
    _require(re.search(r"ring s=[^\n]*\n(number I=[^\n]*)", script) is not None, "the ring s lines changed")
    return script


if __name__ == "__main__":
    _require(len(sys.argv) == 3 and sys.argv[1] == "--emit", __doc__ or "")
    sys.stdout.write(emit(sys.argv[2]))
