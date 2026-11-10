"""Arcs on the slices of the same-sign X incidences X- -> N- and X+ -> N+, and the rank of their limit map.

The slice V(J) of X- -> N- (header `xm-nm.sing`, 12 generators in t1, t2, t4, t5, t6, t7, t9) is the image of

    Phi(w, rho, sig, a):  t4 = (m rho + sig)/2,  t5 = (m rho - sig)/2,  t6 = (m sig + rho)/2,  t7 = (rho - m sig)/2,
                          t9 = s9 T9,  T9 = -w^2/(2 m),  t1 = a - T9,  t2 = a w (w + 2)/(2 m),  m = 1 + w,

with s9 = +1; the header of X+ -> N+ (`xp-np.sing`) is that of X- -> N- at -t9, so s9 = -1 there. The first block
is the rank-one parametrization of ../arcs-x; a = t1 + s9 t9 is the coordinate in which the remaining generators of
J are linear in (a, t2) with the one solution line above. Each script checks J(Phi) = 0 as an identity modulo
u m = 1, then takes the weighted arc w = W s^2, rho = R s, sig = S s, a = A s with W, R, S, A as ring variables and
reports: the order nu of G on the arc, with every lower coefficient identically zero; the number of K2 quadrics that
do not vanish identically on the limit vector F (the coefficient of s^nu); the rank of [dF | F] at two parameter
points, a lower bound for the dimension of the cone of limits. The mutated arc doubles t2, leaves V(J) and is the
off control (t9 has order 4 on this arc and does not enter F, so a reversed t9 is no control). The scan cases list nu
and the rank for the weights 1 to 3 of w, of (rho, sig) and of a.

    $PYTHON docs/evidence/a5-exceptional-fibers/arcs-x-same/x_same_arcs.py [--check]
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
W = "docs/evidence/a5-exceptional-fibers/working"
ROOTS = {32009: 10754, 32029: 9115}
# slug: (sign s9, {prime: directory of the K2 run with relations-upto-d2.rel and gens.txt})
CASES: dict[str, tuple[int, dict[int, str]]] = {
    "xm-nm": (
        1,
        {32009: f"{W}/distribute/out/a5-xm-d4/xm_p1/d2", 32029: f"{W}/distribute/out/a5-p2-small/xm_p2/d2"},
    ),
    "xp-np": (-1, {32029: f"{W}/distribute/out/a5-p2-small/xp_p2/d2"}),
}
# Two hand-chosen parameter points (W, R, S, A); a rank at any point bounds the generic rank from below.
POINTS = ((2, 3, 5, 7), (13, 4, 9, 6))
ORDER = 14
SIGNS = (
    "intvec eps; int jj; for (jj=1;jj<=ncols(G);jj++) { if (Grun[jj]==G[jj]) { eps[jj]=1; } else {"
    ' if (Grun[jj]==-G[jj]) { eps[jj]=-1; } else { ERROR("generator "+string(jj)+" is not +-G"); } } }'
)
PHI = "T1,T2,(m*rho+sig)/2,(m*rho-sig)/2,(m*sig+rho)/2,(rho-m*sig)/2,{sign}*T9"
ARC = (
    "proc arc(int ew, int er, int ea) {{ poly w=W*s^ew; poly rho=R*s^er; poly sig=Sg*s^er; poly a=A*s^ea;"
    " poly u=1; poly pw=1; int i; for (i=1;i<={order};i++) {{ pw=jet(-pw*w,{order},sw); u=u+pw; }}"
    " poly m=1+w; poly T9=jet(-w^2*u/2,{order},sw); poly T1=a-T9; poly T2=jet(a*w*(w+2)*u{factor},{order},sw);"
    " map phi=r,{phi}; return(jet(phi(G),{order}-2,sw)); }}"
)
LIMIT = (
    "proc lowest(ideal Gs) { int j; int k; for (k=0;k<=12;k++) { for (j=1;j<=ncols(Gs);j++) {"
    " if (jet(Gs[j],k,sw)!=0) { return(k); } } } return(-1); }",
    "proc limit(ideal Gs, int nu) { ideal F; int j; for (j=1;j<=ncols(Gs);j++) {"
    " F[j]=subst(jet(Gs[j],nu,sw)-jet(Gs[j],nu-1,sw),s,1); } return(F); }",
)


def script(slug: str, prime: int, mutate: bool) -> str:
    sign, runs = CASES[slug]
    header = (ROOT / W / "build" / "inputs" / f"p{prime}-r{ROOTS[prime]}" / f"{slug}.sing").read_text().strip()
    factor = "" if mutate else "/2"
    points = [",".join(("0", *(str(v) for v in point))) for point in POINTS]
    lines = [
        f"// arcs on the {slug} slice at p = {prime}" + (", mutated" if mutate else ""),
        "option(redSB);",
        'LIB "matrix.lib";',
        header,
        "ring E=" + str(prime) + ",(w,rho,sig,a,u),dp;",
        f"poly m=1+w; poly T9=-w^2*u/2; poly T1=a-T9; poly T2=a*w*(w+2)*u{factor};",
        f"map phiE=r,{PHI.format(sign=sign)};",
        '"RESULT generators of J nonzero on Phi modulo u m = 1", size(simplify(reduce(phiE(J),std(ideal(u*m-1))),2)),'
        ' "of", ncols(phiE(J));',
        "setring r;",
    ]
    if prime in runs:
        lines += [
            f'execute("ideal Grun="+read("{runs[prime]}/gens.txt")+";");',
            SIGNS,
            '"RESULT signs of the run generators against the header", eps;',
            f'execute("ring Y={prime},(y(1..15)),dp;");',
            f'execute("ideal K="+read("{runs[prime]}/relations-upto-d2.rel")+";");',
            '"RESULT K2 generators", size(K);',
        ]
    lines += [
        f"ring S={prime},(s,W,R,Sg,A),dp;",
        "intvec sw=1,0,0,0,0;",
        ARC.format(order=ORDER, phi=PHI.format(sign=sign), factor=factor),
        *LIMIT,
        "ideal Gs=arc(2,1,1); int nu=lowest(Gs); ideal F=limit(Gs,nu);",
        "matrix M=concat(jacob(F),transpose(matrix(F)));",
        f"map p1=S,{points[0]}; map p2=S,{points[1]};",
        '"RESULT weights 2 1 1 nu", nu, "nonzero limit entries", size(simplify(F,2));',
        '"RESULT rank of [dF | F] at two points", rank(p1(M)), rank(p2(M));',
    ]
    if prime in runs:
        lines += [
            "int j; ideal Fr; for (j=1;j<=ncols(F);j++) { Fr[j]=eps[j]*F[j]; } map back=Y,Fr;",
            '"RESULT K2 nonzero on the limit", size(simplify(back(K),2));',
        ]
    if not mutate:
        lines += [
            "int x; int y; int z; ideal Gx; ideal Fx; matrix Mx; int nx;",
            "for (x=1;x<=3;x++) { for (y=1;y<=3;y++) { for (z=1;z<=3;z++) { Gx=arc(x,y,z); nx=lowest(Gx);"
            " Fx=limit(Gx,nx); Mx=concat(jacob(Fx),transpose(matrix(Fx)));"
            ' "RESULT scan weights", x, y, z, "nu", nx, "rank", rank(p1(Mx)), rank(p2(Mx)); } } }',
        ]
    return "\n".join((*lines, "quit;", ""))


def main() -> None:
    check = "--check" in sys.argv[1:]
    stale = []
    for slug in CASES:
        for prime in ROOTS:
            for mutate in (False, True):
                path = HERE / f"{slug}-arcs-p{prime}{'-mutated' if mutate else ''}.sing"
                text = script(slug, prime, mutate)
                if check:
                    if not path.exists() or path.read_text() != text:
                        stale.append(path.name)
                else:
                    path.write_text(text)
    if stale:
        raise SystemExit(f"stale: {stale}")


if __name__ == "__main__":
    main()
