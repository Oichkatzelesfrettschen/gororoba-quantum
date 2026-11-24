"""Emit a Singular script on the ten-Pfaffians of the 15 x 15 kernel-coordinate matrix C(z).

Arguments: the kernel-attachments directory, the prime (0 for Q(i)), the root of -1, then an optional mode.
No mode: stability of the degree-5 Pfaffian span under linear vector fields, alone and modulo each source closure.
alg [closures]: the linear vector fields that stabilize each closure ideal and each (closure, Pfaffian) pair.
rad: equidimensional hull, radical and minimal primes of the E8-bar closure ideal.
"""

import itertools
import re
import sys
from pathlib import Path

import sympy as sp

ATT = Path(sys.argv[1])
P, ROOT = int(sys.argv[2]), int(sys.argv[3])
sys.path.insert(0, str(ATT))
sys.path.insert(0, str(ATT.parent / "a5-strata-regularity"))
import verify_regularity_independent as ind  # noqa: E402
import weight_slice_fiber_relations as ws  # noqa: E402

basis = ws._c_basis()
RING = f"ring r={P},(z(1..15)),dp; number I={ROOT};" if P else "ring r=(0,I),(z(1..15)),dp; minpoly=I^2+1;"
PFN = (
    "proc pfn(matrix A){ int nn=nrows(A); if(nn==0){return(poly(1));} if(nn==2){return(A[1,2]);} poly acc=0;"
    " int jj; int kk; intvec keep; int sg=1; int cnt; for(jj=2;jj<=nn;jj++){ keep=0; cnt=0;"
    " for(kk=2;kk<=nn;kk++){ if(kk!=jj){cnt++; keep[cnt]=kk;} }"
    " acc=acc+sg*A[1,jj]*pfn(submat(A,keep,keep)); sg=-sg; } return(acc); }"
)
out = [RING + ' option(redSB); LIB "matrix.lib";', PFN, "matrix CZ[15][15];"]
for r in range(15):
    for c in range(r + 1, 15):
        terms = []
        for k in range(15):
            e = basis[k][r, c]
            if e != 0:
                real, imag = e.as_real_imag()
                ph = ("1", "I", "-1", "-I")[(k + 1).bit_count() % 4]
                terms.append(f"(({real})+({imag})*I)*({ph})*z({k + 1})")
        if terms:
            out.append(f"CZ[{r + 1},{c + 1}]={'+'.join(terms)}; CZ[{c + 1},{r + 1}]=-CZ[{r + 1},{c + 1}];")
out.append("ideal P; int q=0; intvec S;")
for subset in itertools.combinations(range(1, 16), 10):
    out.append(f"S={','.join(map(str, subset))}; q++; P[q]=pfn(submat(CZ,S,S));")
out.append('"RESULT pfaffians",ncols(P),size(P); degBound=5; ideal sP=std(P); "RESULT span_dimension",size(sP);')
out.append(
    "proc stab(matrix M, string name){ ideal Z=maxideal(1); matrix V=M*transpose(matrix(Z)); ideal D; int a;"
    " int b; poly acc; for(a=1;a<=ncols(P);a++){ acc=0; for(b=1;b<=15;b++){ acc=acc+diff(P[a],z(b))*V[b,1]; }"
    " D[a]=acc; } ideal N=reduce(D,sP); ideal sA=std(P+D);"
    ' print("RESULT stable "+name+" outside "+string(size(N))+" nonzero_derivatives "+string(size(D))'
    '+" joint_span "+string(size(sA))); }'
)


def mat(name: str, matrix: sp.Matrix) -> None:
    """Declare one 15 x 15 vector-field matrix and test it."""
    out.append(f"matrix M{name}[15][15];")
    for r in range(15):
        for c in range(15):
            v = sp.nsimplify(matrix[r, c])
            if v != 0:
                real, imag = v.as_real_imag()
                out.append(f"M{name}[{r + 1},{c + 1}]=({real})+({imag})*I;")
    out.append(f'stab(M{name},"{name}");')


mat("identity", sp.eye(15))
mat("g2_1", ws._derivation_matrix(0))
mat("g2_7", ws._derivation_matrix(6))
mat("g2_13", ws._derivation_matrix(12))
mat("boost", ws._boost_matrix())
rot = sp.zeros(15, 15)
for k in range(7):
    rot[k, k + 8] = 1
    rot[k + 8, k] = -1
mat("rotation", rot)
neg = ws._boost_matrix()
neg[0, 8] = 2
mat("boost_perturbed", neg)
half = sp.zeros(15, 15)
for k in range(7):
    half[k, k] = 1
mat("scale_u_only", half)

zs = sp.symbols("z1:16")
left, middle, right = list(zs[0:7]), zs[7], list(zs[8:15])
total = [a + b for a, b in zip(left, right, strict=True)]
diffv = [a - b for a, b in zip(left, right, strict=True)]
el, er, ec = ind.eta2(left, left), ind.eta2(right, right), ind.eta2(left, right)
quad = el - middle * middle - er
delta = ec * ec - el * er
rows = sp.Matrix([left, right, ind.cross(left, right)])
closure = [quad, delta] + [rows[:, list(c)].det() for c in itertools.combinations(range(7), 3)]
table = {
    "w8": [middle, ind.eta2(total, total), ind.eta2(diffv, diffv)],
    "iso": [middle, el, er, ec],
    "e8": closure,
    "xp": [*closure, middle, ind.eta2(diffv, diffv)],
    "xm": [*closure, middle, ind.eta2(total, total)],
}


def sing(e: sp.Expr) -> str:
    """One sympy polynomial in Singular syntax."""
    return "(" + re.sub(r"z(\d+)", r"z(\1)", str(sp.expand(e)).replace("**", "^")) + ")"


def equations(name: str) -> str:
    """The nonzero closure equations of one source, comma separated."""
    return ",".join(sing(e) for e in table[name] if sp.expand(e) != 0)


out.append(
    "proc dv(ideal F, matrix M){ ideal Z=maxideal(1); matrix V=M*transpose(matrix(Z)); ideal D; int a; int b;"
    " poly acc; for(a=1;a<=ncols(F);a++){ acc=0; for(b=1;b<=15;b++){ acc=acc+diff(F[a],z(b))*V[b,1]; }"
    " D[a]=acc; } return(D); }"
)
out.append("ideal DB=dv(P,Mboost); ideal DR=dv(P,Mrotation); ideal DG=dv(P,Mg2_1); ideal Y; ideal sY; ideal sPY;")
for name in table:
    out.append("Y=" + equations(name) + ";")
    out.append("degBound=0; sY=std(Y);")
    out.append(
        f'print("RESULT closure {name} generators "+string(size(Y))+" dim "+string(dim(sY))+" mult "'
        '+string(mult(sY))+" boost_moves "+string(size(reduce(dv(Y,Mboost),sY)))+" rotation_moves "'
        '+string(size(reduce(dv(Y,Mrotation),sY)))+" g2_moves "+string(size(reduce(dv(Y,Mg2_1),sY))));'
    )
    out.append("degBound=5; sPY=std(P+Y);")
    out.append(
        f'print("RESULT modulo {name} pfaffians_outside_closure "+string(size(reduce(P,sY)))+" boost_outside "'
        '+string(size(reduce(DB,sPY)))+" rotation_outside "+string(size(reduce(DR,sPY)))+" g2_outside "'
        "+string(size(reduce(DG,sPY))));"
    )
out.append('"RESULT done 1"; quit;')
if len(sys.argv) > 4 and sys.argv[4] == "alg":
    cut = next(k for k, line in enumerate(out) if line.startswith("proc stab("))
    out = out[:cut]
    out.append(f"ring r2={P},(z(1..15),c(1..225)),(dp(15),dp(225)); number I={ROOT}; option(redSB);")
    out.append(
        'ideal P=imap(r,P); ideal sP=imap(r,sP); attrib(sP,"isSB",1); poly zall=1; int a; int b; int k;'
        " for(a=1;a<=15;a++){zall=zall*z(a);}"
    )
    out.append(
        "proc gfield(poly f){ poly acc=0; int a; int b; for(a=1;a<=15;a++){ poly d=diff(f,z(a)); if(d!=0){"
        " for(b=1;b<=15;b++){ acc=acc+c((a-1)*15+b)*z(b)*d; } } kill d; } return(acc); }"
    )
    out.append(
        "proc cons(ideal F, ideal sG){ ideal L; int k; int j; poly n; matrix cf; for(k=1;k<=ncols(F);k++){"
        " n=reduce(gfield(F[k]),sG); if(n!=0){ cf=coef(n,zall); for(j=1;j<=ncols(cf);j++){ L[size(L)+1]=cf[2,j]; }"
        " L=interred(L); } } return(L); }"
    )
    out.append("ideal Pk; for(k=1;k<=3003;k=k+13){ Pk[size(Pk)+1]=P[k]; }")
    out.append('ideal Lg=cons(Pk,sP); print("RESULT algebra global dimension "+string(225-size(std(Lg))));')
    out.append("ideal cb; for(a=1;a<=225;a++){cb[a]=0;} for(a=1;a<=7;a++){ cb[(a-1)*15+a+8]=1; cb[(a+8-1)*15+a]=1; }")
    out.append("ideal zc=maxideal(1); ideal Y; ideal sY; ideal sPY; ideal LY; ideal LA; ideal bt; map ev;")
    only = sys.argv[5].split(",") if len(sys.argv) > 5 else list(table)
    for name in table:
        if name not in only:
            continue
        out.append("Y=" + equations(name) + ";")
        out.append("degBound=0; sY=std(Y); degBound=5; sPY=std(P+Y); degBound=0;")
        out.append("LY=std(cons(Y,sY)); LA=std(LY+cons(Pk,sPY));")
        out.append("for(a=1;a<=15;a++){zc[a]=z(a);} for(a=1;a<=225;a++){zc[15+a]=cb[a];} ev=r2,zc; bt=ev(LA);")
        out.append(
            f'print("RESULT algebra {name} closure_stabilizer "+string(225-size(LY))+" pair_stabilizer "'
            '+string(225-size(LA))+" boost_inside "+string(size(bt)==0));'
        )
        out.append(f'for(k=1;k<=size(LA);k++){{ print("CONSTRAINT {name} "+string(LA[k])); }}')
    out.append('"RESULT done 1"; quit;')
elif len(sys.argv) > 4:
    out = [
        RING + ' option(redSB); LIB "primdec.lib"; LIB "elim.lib";',
        "ideal Y=" + equations("e8") + ";",
        'ideal sY=std(Y); "RESULT e8 dim",dim(sY),"mult",mult(sY);',
        'ideal E=equidimMax(Y); "RESULT equidimMax_equal",size(reduce(E,sY))==0, size(E);',
        'ideal Rd=radical(Y); "RESULT radical_equal",size(reduce(Rd,sY))==0, size(Rd); ideal sR=std(Rd);'
        ' "RESULT radical dim",dim(sR),"mult",mult(sR);',
        'int k; for(k=1;k<=size(Rd);k++){ if(reduce(Rd[k],sY)!=0){ "EXTRA deg",deg(Rd[k]); } }',
        'list L=minAssGTZ(Y); "RESULT components",size(L);'
        ' for(k=1;k<=size(L);k++){ sR=std(L[k]); "RESULT component",dim(sR),mult(sR),size(sR); }',
        '"RESULT done 1"; quit;',
    ]
print("\n".join(out))
