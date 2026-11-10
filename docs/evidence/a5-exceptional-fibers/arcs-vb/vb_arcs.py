"""Arcs on the slice of E8-bar -> VB that are dense in each component of V(K2).

The slice V(J) (header `e8-vb.sing`, 17 generators in t1, ..., t8) is the image of

    Phi(w, rho, sig, k):  t3 = -(m rho + sig)/2,  t4 = (m sig + rho)/2,  t5 = (m rho - sig)/2,  t6 = (rho - m sig)/2,
                          t8 = -w^2/(2 m),  t1 = (k^2 a1 - a2)/(4 m^2 (1 + k^2)),  t7 = k w (w + 2)/(m (1 + k^2)),
                          t2 = (t1 w (w + 2) + 2 w^2)/(m^2 + 1),

with m = 1 + w, a1 = w^4 - 6 w^2 - 4 w and a2 = w^4 + 8 w^3 + 18 w^2 + 12 w. The first block is the rank-one
parametrization of ../arcs-x; given it, t2 is linear in t1 and (t1, t7) lies on the conic
4 m^2 (m^2 + 1)^2 t7^2 = (a1 - 4 m^2 t1)(a2 + 4 m^2 t1), which k parametrizes through its point t7 = 0. Phi contracts
the line w = rho = sig = 0 to the origin, so an arc through a point (0, 0, 0, k0) of that line maps to an arc of V(J)
through the origin.

Two families, with their parameters as ring variables:

- `generic`: w = W s, rho = R s, sig = S s, k = K constant. v stands for 1/(1 + K^2) and every statement is taken
  modulo v (1 + K^2) = 1; the K-column of the Jacobian is dF/dK - 2 K v^2 dF/dv.
- `special`: k = -9 + K s, w = W s^2, rho = R s, sig = S s, the arcs through the point k0 = -9 of the line, where the
  coefficient matrix of (w rho, w sig) in the order-2 parts of the generators drops to rank 1.

Each script reports J(Phi) = 0 modulo the unit relations, the order nu of G on the arc with the lower coefficients
identically zero, the number of generators of K2, of the degree-3 prime P1 and of the degree-4 prime P2 (the two
minimal primes of K2, computed in the script) that do not vanish on the limit vector F, and the rank of [dF | F] at
two parameter points. Controls: the mutated generic arc doubles t7 and the mutated special arc doubles t8, so each
leaves V(J); the `neighbor` case runs the special arc at k0 = -8, a point of the line with no rank drop. The `scan`
case lists nu, the rank and the component tests for the 81 weight vectors (orders 1 to 3 of k + 9, w, rho, sig) at
k0 = -9.

    $PYTHON docs/evidence/a5-exceptional-fibers/arcs-vb/vb_arcs.py [--check]
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
W = "docs/evidence/a5-exceptional-fibers/working"
ROOTS = {32009: 10754, 32029: 9115}
# prime: (K2 relation file, generator list of its run; a .sing source holds the list as its `ideal G=` line)
K2 = {
    32009: (f"{W}/runs/e8vb_a2/k2.rel", f"{W}/runs/e8vb_a2/input.sing"),
    32029: (
        f"{W}/distribute/out/a5-p2-small/vb_p2/d2/relations-upto-d2.rel",
        f"{W}/distribute/out/a5-p2-small/vb_p2/d2/gens.txt",
    ),
}
SPECIAL_K = -9
# Two hand-chosen parameter points (W, R, S, K); a rank at any point bounds the generic rank from below.
POINTS = ((2, 3, 5, 7), (13, 4, 9, 6))
ORDER = 14
SIGNS = (
    "intvec eps; int jj; for (jj=1;jj<=ncols(G);jj++) { if (Grun[jj]==G[jj]) { eps[jj]=1; } else {"
    ' if (Grun[jj]==-G[jj]) { eps[jj]=-1; } else { ERROR("generator "+string(jj)+" is not +-G"); } } }'
)
# The run input lists its generators before reduction, so they equal the header's only modulo J.
SIGNS_MODULO_J = (
    "ideal sJ=std(J); intvec eps; int jj; for (jj=1;jj<=ncols(G);jj++) {"
    " if (reduce(Grun[jj]-G[jj],sJ)==0) { eps[jj]=1; } else { if (reduce(Grun[jj]+G[jj],sJ)==0) { eps[jj]=-1; }"
    ' else { ERROR("generator "+string(jj)+" is not +-G modulo J"); } } }'
)
PRIMES_OF_K2 = (
    'list L=minAssGTZ(K2); if (size(L)!=2) { ERROR("K2 has "+string(size(L))+" minimal primes"); }',
    "ideal P1; ideal P2; int ii; for (ii=1;ii<=2;ii++) { if (mult(std(L[ii]))==3) { P1=L[ii]; } else { P2=L[ii]; } }",
    "if (dim(std(P1))!=4 or mult(std(P1))!=3 or dim(std(P2))!=4 or mult(std(P2))!=4) {"
    ' ERROR("the minimal primes of K2 are not of dimension 4 and degrees 3 and 4"); }',
    '"RESULT K2 generators", size(K2), "P1 dimension degree generators", dim(std(P1)), mult(std(P1)), size(P1),'
    ' "P2", dim(std(P2)), mult(std(P2)), size(P2);',
)
INVERSE = (
    "proc inv(poly f, int n) { poly c=jet(f,0,sw); poly g=1/c; poly q=1-f*g; poly acc=1; poly pw=1; int i;"
    " for (i=1;i<=n;i++) { pw=jet(pw*q,n,sw); acc=acc+pw; } return(jet(acc*g,n,sw)); }"
)
PHI = "T1,T2,-(m*rho+sig)/2,(m*sig+rho)/2,(m*rho-sig)/2,(rho-m*sig)/2,{t7}*T7,T8"
LIMIT = (
    "proc lowest(ideal Gs) { int j; int k; for (k=0;k<=11;k++) { for (j=1;j<=ncols(Gs);j++) {"
    " if (jet(Gs[j],k,sw)!=0) { return(k); } } } return(-1); }",
    "proc limit(ideal Gs, int nu) { ideal F; int j; for (j=1;j<=ncols(Gs);j++) {"
    " F[j]=eps[j]*subst(jet(Gs[j],nu,sw)-jet(Gs[j],nu-1,sw),s,1); } return(F); }",
)
TESTS = (
    '"RESULT K2 nonzero on the limit", size(simplify({reduce}(back(K2){rel}),2)), "P1", '
    'size(simplify({reduce}(back(P1){rel}),2)), "of", ncols(back(P1)), "P2", '
    'size(simplify({reduce}(back(P2){rel}),2)), "of", ncols(back(P2));'
)


def head(prime: int, title: str) -> list[str]:
    header = (ROOT / W / "build" / "inputs" / f"p{prime}-r{ROOTS[prime]}" / "e8-vb.sing").read_text().strip()
    relations, generators = K2[prime]
    if generators.endswith(".sing"):
        lines = (ROOT / generators).read_text().splitlines()
        (run_line,) = [line for line in lines if line.startswith("ideal G=")]
        signs = [run_line.replace("ideal G=", "ideal Grun=", 1), SIGNS_MODULO_J]
    else:
        signs = [f'execute("ideal Grun="+read("{generators}")+";");', SIGNS]
    return [
        f"// {title} on the E8-bar -> VB slice at p = {prime}",
        "option(redSB);",
        'LIB "matrix.lib"; LIB "primdec.lib";',
        header,
        *signs,
        '"RESULT signs of the run generators against the header", eps;',
        f'execute("ring Y={prime},(y(1..10)),dp;");',
        f'execute("ideal K2="+read("{relations}")+";");',
        *PRIMES_OF_K2,
    ]


def identity(prime: int, mutate: bool) -> list[str]:
    t7 = "2" if mutate else "1"
    return [
        f"ring E={prime},(w,rho,sig,k,u,v,z),dp;",
        "poly m=1+w; poly a1=w^4-6*w^2-4*w; poly a2=w^4+8*w^3+18*w^2+12*w;",
        "poly T1=(k^2*a1-a2)*(u^2)*v/4; poly T2=(T1*w*(w+2)+2*w^2)*z; poly T7=k*w*(w+2)*u*v; poly T8=-(w^2)*u/2;",
        f"map phiE=r,{PHI.format(t7=t7)};",
        '"RESULT generators of J nonzero on Phi modulo the unit relations", '
        'size(simplify(reduce(phiE(J),std(ideal(u*m-1,v*(1+k^2)-1,z*(m^2+1)-1))),2)), "of", ncols(phiE(J));',
    ]


def generic(prime: int, mutate: bool) -> str:
    t7 = "2" if mutate else "1"
    points = [",".join(("0", *(str(x) for x in point), str(pow(1 + point[3] ** 2, -1, prime)))) for point in POINTS]
    lines = [
        *head(prime, "arcs at a generic point of the line" + (", mutated" if mutate else "")),
        *identity(prime, mutate),
        f"ring S={prime},(s,W,R,Sg,K,v),dp;",
        "intvec sw=1,0,0,0,0,0;",
        "ideal rel=std(ideal(v*(1+K^2)-1));",
        INVERSE,
        *LIMIT,
        f"int n={ORDER}; poly w=W*s; poly rho=R*s; poly sig=Sg*s; poly m=1+w; poly u=inv(m,n); poly z=inv(m^2+1,n);",
        "poly a1=w^4-6*w^2-4*w; poly a2=w^4+8*w^3+18*w^2+12*w;",
        "poly T1=jet((K^2*a1-a2)*(u^2)*v/4,n,sw); poly T2=jet((T1*w*(w+2)+2*w^2)*z,n,sw);",
        "poly T7=jet(K*w*(w+2)*u*v,n,sw); poly T8=jet(-(w^2)*u/2,n,sw);",
        f"map phi=r,{PHI.format(t7=t7)};",
        "ideal Gs=reduce(jet(phi(G),n-3,sw),rel); int nu=lowest(Gs); ideal F=limit(Gs,nu);",
        "matrix M[10][5]; int j;",
        "for (j=1;j<=10;j++) { M[j,1]=diff(F[j],W); M[j,2]=diff(F[j],R); M[j,3]=diff(F[j],Sg);"
        " M[j,4]=diff(F[j],K)-2*K*v^2*diff(F[j],v); M[j,5]=F[j]; }",
        f"map p1=S,{points[0]}; map p2=S,{points[1]}; map back=Y,F;",
        '"RESULT weights 1 1 1 with K constant: nu", nu, "nonzero limit entries", size(simplify(F,2));',
        TESTS.format(reduce="reduce", rel=",rel"),
        '"RESULT rank of [dF | F] at two points", rank(p1(M)), rank(p2(M));',
        "quit;",
        "",
    ]
    return "\n".join(lines)


def special_arc(k0: int, mutate: bool) -> list[str]:
    t8 = "" if mutate else "/2"
    return [
        "proc arc(int d, int ew, int er, int es) {"
        f" int n={ORDER}; poly k={k0}+K*s^d; poly w=W*s^ew; poly rho=R*s^er; poly sig=Sg*s^es; poly m=1+w;"
        " poly u=inv(m,n); poly z=inv(m^2+1,n); poly v=inv(1+k^2,n);"
        " poly a1=w^4-6*w^2-4*w; poly a2=w^4+8*w^3+18*w^2+12*w;"
        " poly T1=jet((k^2*a1-a2)*(u^2)*v/4,n,sw); poly T2=jet((T1*w*(w+2)+2*w^2)*z,n,sw);"
        f" poly T7=jet(k*w*(w+2)*u*v,n,sw); poly T8=jet(-(w^2)*u{t8},n,sw);"
        f" map phi=r,{PHI.format(t7=1)};"
        ' "RESULT generators of J nonzero on the arc through order", n-2, size(simplify(jet(phi(J),n-2,sw),2));'
        " return(jet(phi(G),n-3,sw)); }",
    ]


def special(prime: int, mode: str) -> str:
    mutate = mode == "mutated"
    k0 = SPECIAL_K + 1 if mode == "neighbor" else SPECIAL_K
    points = [",".join(("0", *(str(x) for x in point))) for point in POINTS]
    lines = [
        *head(prime, f"arcs through the point k = {k0} of the line" + (", mutated" if mutate else "")),
        *identity(prime, False),
        f"ring S={prime},(s,W,R,Sg,K),dp;",
        "intvec sw=1,0,0,0,0;",
        INVERSE,
        *LIMIT,
        *special_arc(k0, mutate),
        f"map p1=S,{points[0]}; map p2=S,{points[1]};",
    ]
    if mode == "scan":
        lines += [
            "int d; int x; int y; int q; ideal Gx; ideal Fx; matrix Mx; int nx; map bx;",
            "for (d=1;d<=3;d++) { for (x=1;x<=3;x++) { for (y=1;y<=3;y++) { for (q=1;q<=3;q++) {"
            " Gx=arc(d,x,y,q); nx=lowest(Gx); Fx=limit(Gx,nx); Mx=concat(jacob(Fx),transpose(matrix(Fx))); bx=Y,Fx;"
            ' "RESULT scan orders of k+9, w, rho, sig", d, x, y, q, "nu", nx, "rank", rank(p1(Mx)), rank(p2(Mx)),'
            ' "K2 P1 P2 nonzero", size(simplify(bx(K2),2)), size(simplify(bx(P1),2)),'
            " size(simplify(bx(P2),2)); } } } }",
        ]
    else:
        lines += [
            "ideal Gs=arc(1,2,1,1); int nu=lowest(Gs); ideal F=limit(Gs,nu);",
            "matrix M=concat(jacob(F),transpose(matrix(F))); map back=Y,F;",
            f'"RESULT k = {k0} + K s, w = W s^2, rho = R s, sig = S s: nu", nu, "nonzero limit entries", '
            "size(simplify(F,2));",
            TESTS.format(reduce="", rel=""),
            '"RESULT rank of [dF | F] at two points", rank(p1(M)), rank(p2(M));',
        ]
    return "\n".join((*lines, "quit;", ""))


def scripts() -> dict[str, str]:
    out = {}
    for prime in ROOTS:
        out[f"vb-generic-p{prime}.sing"] = generic(prime, False)
        out[f"vb-generic-p{prime}-mutated.sing"] = generic(prime, True)
        for mode in ("certificate", "mutated", "neighbor", "scan"):
            suffix = "" if mode == "certificate" else f"-{mode}"
            out[f"vb-special-p{prime}{suffix}.sing"] = special(prime, mode)
    return out


def main() -> None:
    check = "--check" in sys.argv[1:]
    stale = []
    for name, text in scripts().items():
        path = HERE / name
        if check:
            if not path.exists() or path.read_text() != text:
                stale.append(name)
        else:
            path.write_text(text)
    if stale:
        raise SystemExit(f"stale: {stale}")


if __name__ == "__main__":
    main()
