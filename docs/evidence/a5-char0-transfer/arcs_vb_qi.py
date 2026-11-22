"""Arc certificate of E8-bar -> VB over Q(i): both components of V(K2) lie in the fiber, and L = K2.

    $PYTHON docs/evidence/a5-char0-transfer/arcs_vb_qi.py OUT.sing     (then: Singular -q --no-warn OUT.sing)

The modular certificate ../a5-exceptional-fibers/arcs-vb substitutes two arc families with rational coefficients
into the header's J and G. This script writes one Singular script that repeats it in characteristic 0 on the J and
G of the Q(i) producer (reduction_check._script, slug e8-vb):

1. the degree-2 relations {q : q(G) in J + m I^2} over Q(i), by the Singular stage of quadric_lift.py, as an ideal
   K2 of Q(i)[y(1..10)]; each relation lies in the ideal L of the fiber cone;
2. the minimal primes of K2 over Q(i) (dimension 4, degrees 3 and 4), and K2 = P1 n P2;
3. the generic arc family (limits in V(P2)) and the special family through k = -9 (limits in V(P1)), each with the
   order of G, the generators of K2, P1 and P2 that do not vanish on the limit vector F, and the rank of [dF | F] at
   two rational parameter points; a mutated arc of each family leaves V(J) and is the known-bad control.

A limit vector of an arc of V(J) through the origin is a point of V(L); rank 4 at a point makes the family dominant
onto a component of dimension 4. With both components in V(L), L lies in the radical of K2, which is K2.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import quadric_lift  # noqa: E402
import reduction_check as rc  # noqa: E402

ORDER = 14
SPECIAL_K = -9
POINTS = ((2, 3, 5, 7), (13, 4, 9, 6))
IMAGES = {
    "t1": "T1",
    "t2": "T2",
    "t3": "-(m*rho+sig)/2",
    "t4": "(m*sig+rho)/2",
    "t5": "(m*rho-sig)/2",
    "t6": "(rho-m*sig)/2",
    "t7": "{t7}*T7",
    "t8": "T8",
}
PROCS = (
    "proc inv(poly f, int n) { poly c=jet(f,0,sw); poly g=1/c; poly q=1-f*g; poly acc=1; poly pw=1; int i;"
    " for (i=1;i<=n;i++) { pw=jet(pw*q,n,sw); acc=acc+pw; } return(jet(acc*g,n,sw)); }",
    "proc lowest(ideal Gs) { int j; int k; for (k=0;k<=11;k++) { for (j=1;j<=ncols(Gs);j++) {"
    " if (jet(Gs[j],k,sw)!=0) { return(k); } } } return(-1); }",
    "proc limit(ideal Gs, int nu) { ideal F; int j; for (j=1;j<=ncols(Gs);j++) {"
    " F[j]=subst(jet(Gs[j],nu,sw)-jet(Gs[j],nu-1,sw),x,1); } return(F); }",
)
# The producer script holds a ring s and integers i, k, n and others, so the series variable is x and the arc
# parameter k of ../a5-exceptional-fibers/arcs-vb is kpar; the inverses of 1 + k^2 and m^2 + 1 are vinv and zinv.
POLYS = "poly aq1=w^4-6*w^2-4*w; poly aq2=w^4+8*w^3+18*w^2+12*w;"


def images(t7: str) -> str:
    """Singular statements that build the map of the producer ring R0 by variable name (others go to 0)."""
    tests = " ".join(f'if (vn=="{name}") {{ IM[vi]={image.format(t7=t7)}; }}' for name, image in IMAGES.items())
    loop = f"for (vi=1;vi<=nvars(R0);vi++) {{ vn=varstr(R0,vi); IM[vi]=0; {tests} }}"
    return f"ideal IM; int vi; string vn; {loop} map phi=R0,IM;"


def quadric_stage() -> list[str]:
    stage = quadric_lift.singular_script("e8-vb").rsplit("\nquit;\n", 1)[0]
    return [
        stage,
        '"RESULT producer variables", varstr(R0);',
        "matrix SM=matrix(S); int nrel=size(S);",
        'ring Y=(0,I),(y(1..10)),dp; minpoly=I2+1; LIB "primdec.lib"; LIB "matrix.lib";',
        "ideal kb=kbase(std(ideal(0)),2); matrix SM=imap(R0,SM); ideal K2; int a; int b; poly kq;",
        "for (a=1;a<=ncols(SM);a++) { kq=0; for (b=1;b<=nrows(SM);b++) { kq=kq+SM[b,a]*kb[b]; } K2[a]=kq; }",
        "ideal sK=std(K2);",
        '"RESULT K2 generators", size(minbase(K2)), "dimension", dim(sK), "multiplicity", mult(sK);',
        'list L=minAssGTZ(K2); "RESULT minimal primes of K2", size(L);',
        "ideal P1; ideal P2; int ii; for (ii=1;ii<=size(L);ii++) {"
        " if (mult(std(L[ii]))==3) { P1=L[ii]; } else { P2=L[ii]; } }",
        '"RESULT P1 dimension degree generators", dim(std(P1)), mult(std(P1)), size(P1),'
        ' "P2", dim(std(P2)), mult(std(P2)), size(P2);',
        "ideal PP=intersect(P1,P2);",
        '"RESULT K2 equals P1 n P2: K2 modulo intersection", size(reduce(K2,std(PP))),'
        ' "intersection modulo K2", size(reduce(PP,sK));',
        "ideal K2drop; for (a=2;a<=ncols(K2);a++) { K2drop[a-1]=K2[a]; }",
        '"RESULT control K2 without its first quadric: intersection modulo it", size(reduce(PP,std(K2drop)));',
    ]


def identity(label: str, t7: str) -> list[str]:
    return [
        f"ring E{label}=(0,I),(w,rho,sig,kpar,u,vinv,zinv),dp; minpoly=I2+1;",
        "poly m=1+w; " + POLYS,
        "poly T1=(kpar^2*aq1-aq2)*(u^2)*vinv/4; poly T2=(T1*w*(w+2)+2*w^2)*zinv;"
        " poly T7=kpar*w*(w+2)*u*vinv; poly T8=-(w^2)*u/2;",
        images(t7),
        f'"RESULT {label} generators of J nonzero on Phi modulo the unit relations", '
        "size(simplify(reduce(phi(ReducedJ),std(ideal(u*m-1,vinv*(1+kpar^2)-1,zinv*(m^2+1)-1))),2)), "
        '"of", ncols(phi(ReducedJ));',
    ]


def tests(label: str, reduce: str, rel: str) -> str:
    return (
        f'"RESULT {label} K2 nonzero on the limit", size(simplify({reduce}(back(K2){rel}),2)), "P1", '
        f'size(simplify({reduce}(back(P1){rel}),2)), "of", ncols(back(P1)), "P2", '
        f'size(simplify({reduce}(back(P2){rel}),2)), "of", ncols(back(P2));'
    )


def generic(label: str, mutate: bool) -> list[str]:
    t7 = "2" if mutate else "1"
    points = [",".join(("0", *(str(x) for x in point), f"1/{1 + point[3] ** 2}")) for point in POINTS]
    return [
        *identity(label, t7),
        f"ring S{label}=(0,I),(x,W,Rh,Sg,K,vinv),dp; minpoly=I2+1;",
        "intvec sw=1,0,0,0,0,0;",
        "ideal rel=std(ideal(vinv*(1+K^2)-1));",
        f"int n={ORDER}; poly w=W*x; poly rho=Rh*x; poly sig=Sg*x; poly m=1+w; poly u=inv(m,n);"
        " poly zinv=inv(m^2+1,n);",
        POLYS,
        "poly T1=jet((K^2*aq1-aq2)*(u^2)*vinv/4,n,sw); poly T2=jet((T1*w*(w+2)+2*w^2)*zinv,n,sw);",
        "poly T7=jet(K*w*(w+2)*u*vinv,n,sw); poly T8=jet(-(w^2)*u/2,n,sw);",
        images(t7),
        f'"RESULT {label} generators of J nonzero on the arc through order", n-2,'
        " size(simplify(reduce(jet(phi(ReducedJ),n-2,sw),rel),2));",
        "ideal Gs=reduce(jet(phi(ReducedG),n-3,sw),rel); int nu=lowest(Gs); ideal F=limit(Gs,nu);",
        "matrix M[10][5]; int j;",
        "for (j=1;j<=10;j++) { M[j,1]=diff(F[j],W); M[j,2]=diff(F[j],Rh); M[j,3]=diff(F[j],Sg);"
        " M[j,4]=diff(F[j],K)-2*K*vinv^2*diff(F[j],vinv); M[j,5]=F[j]; }",
        f"map p1=S{label},{points[0]}; map p2=S{label},{points[1]}; map back=Y,F;",
        f'"RESULT {label} weights 1 1 1 with K constant: nu", nu, "nonzero limit entries", size(simplify(F,2));',
        tests(label, "reduce", ",rel"),
        f'"RESULT {label} rank of [dF | F] at two points", rank(p1(M)), rank(p2(M));',
    ]


def special(label: str, mutate: bool) -> list[str]:
    t8 = "" if mutate else "/2"
    points = [",".join(("0", *(str(x) for x in point))) for point in POINTS]
    return [
        f"ring S{label}=(0,I),(x,W,Rh,Sg,K),dp; minpoly=I2+1;",
        "intvec sw=1,0,0,0,0;",
        f"int n={ORDER}; poly kpar={SPECIAL_K}+K*x; poly w=W*x^2; poly rho=Rh*x; poly sig=Sg*x; poly m=1+w;",
        "poly u=inv(m,n); poly zinv=inv(m^2+1,n); poly vinv=inv(1+kpar^2,n);",
        POLYS,
        "poly T1=jet((kpar^2*aq1-aq2)*(u^2)*vinv/4,n,sw); poly T2=jet((T1*w*(w+2)+2*w^2)*zinv,n,sw);",
        f"poly T7=jet(kpar*w*(w+2)*u*vinv,n,sw); poly T8=jet(-(w^2)*u{t8},n,sw);",
        images("1"),
        f'"RESULT {label} generators of J nonzero on the arc through order", n-2,'
        " size(simplify(jet(phi(ReducedJ),n-2,sw),2));",
        "ideal Gs=jet(phi(ReducedG),n-3,sw); int nu=lowest(Gs); ideal F=limit(Gs,nu);",
        "matrix M=concat(jacob(F),transpose(matrix(F)));"
        f" map p1=S{label},{points[0]}; map p2=S{label},{points[1]}; map back=Y,F;",
        f'"RESULT {label} k = {SPECIAL_K} + K x, w = W x^2, rho = Rh x, sig = Sg x: nu", nu,'
        ' "nonzero limit entries", size(simplify(F,2));',
        tests(label, "", ""),
        f'"RESULT {label} rank of [dF | F] at two points", rank(p1(M)), rank(p2(M));',
    ]


def script() -> str:
    lines = [
        *quadric_stage(),
        *PROCS,
        *generic("generic", False),
        *generic("genericmutated", True),
        *special("special", False),
        *special("specialmutated", True),
        '"EXIT 0";',
        "quit;",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    _ = rc
    Path(sys.argv[1]).write_text(script(), encoding="utf-8")


if __name__ == "__main__":
    main()
