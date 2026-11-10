"""Arcs on the Iso -> N- and W8 -> N- slices through the points of P(L0) of the point blowup, and their limit maps.

Both slices carry the split quadric t2^2 + P Q - R T with P = t4 - t6, Q = t4 + t6, R = t5 - t7, T = t5 + t7:
J = t2^2 + P Q - R T on Iso, and J = g(t1, t9) - t2^2 - P Q + R T on W8 with g = t1^2 t9^2 - 2 t1^2 t9 + 2 t1 t9^2
- 4 t1 t9. Every generator of I vanishes on L0 = {t2 = 0, P = 0, R = 0} (W8: and t9 = 0). In the chart of the point
blowup where the remaining coordinate is s (t3 on Iso, t1 on W8) and t_k = s u_k, the arc

    Q = 2 b, T = 2 c, u2 = V s, R = b V s + A s^2, P = c V s + B s^2

leaves the point (b, c) of P(L0) along (u2, P, R) = V (1, c, b), the one transversal direction on which the linear
parts of all G' vanish (with P = kP s and R = kR s the coefficient of s^3 in every G_j lies in the span of kP - c V
and kR - b V; `probe` cases). On Iso J = 0 forces B = (2 c A - V^2) / (2 b), which the script clears by the
substitution V -> b V, A -> b A, so the Iso arc is polynomial with parameters (b, c, V, A). On W8, J = 0 determines
u9 as the unique power series solution of 4 u9 = -u2^2 - P Q + R T - 2 s u9 + 2 s u9^2 + s^2 u9^2, computed by
fixed-point iteration through order 8 in s, and the parameters are (b, c, V, A, B). The limit vector F of an arc is
the coefficient of the least power s^nu of G on it, which depends only on the jet of the arc of order nu - 1, so the
truncation of u9 does not enter it.

Each script takes the parameters as ring variables and reports: J on the arc (identically 0 on Iso, 0 through order
9 on W8); nu, with every lower coefficient identically zero; the number of K2 quadrics that do not vanish on F
identically; on W8 the same for the generators of the degree-20 component (P at 32009, the nine linear forms Lam at
both primes); the rank of [dF | F] at two parameter points, a lower bound for the dimension of the cone of limits.
The mutated arc drops the V^2 term of J, leaves V(J) and is the off control.

    $PYTHON docs/evidence/a5-exceptional-fibers/structure/arcs-iso-w8/blowup-arcs/blowup_arcs.py [--check]
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
sys.path.insert(0, str(HERE.parent))
from arcs_scan import FIBERS, ROOTS  # noqa: E402  # type: ignore[import-not-found]

# Two hand-chosen parameter points (b, c, V, A, B); a rank at any point bounds the generic rank from below.
POINTS = ((2, 3, 5, 7, 11), (13, 4, 9, 6, 17))
PARAMETERS = {"iso": ("b", "c", "V", "A"), "w8": ("b", "c", "V", "A", "B")}
SIGNS = (
    "intvec eps; int jj; for (jj=1;jj<=ncols(G);jj++) { if (Grun[jj]==G[jj]) { eps[jj]=1; } else {"
    ' if (Grun[jj]==-G[jj]) { eps[jj]=-1; } else { ERROR("generator "+string(jj)+" is not +-G"); } } }'
)


def arc(fiber: str, mutate: bool) -> list[str]:
    """Singular lines defining the map phi from the header ring to the arc ring."""
    square = "0" if mutate else "U2^2"
    if fiber == "iso":
        return [
            "poly Q=2*b; poly T=2*c; poly U2=b*V*s; poly R=b^2*V*s+b*A*s^2;",
            f"poly P=(R*T-({square}))/(2*b);",
            "map phi=r,s*U2,s,s*(Q+P)/2,s*(T+R)/2,s*(Q-P)/2,s*(T-R)/2;",
            '"RESULT J on the arc", size(simplify(phi(J),2))==0;',
        ]
    return [
        "poly Q=2*b; poly T=2*c; poly U2=V*s; poly R=b*V*s+A*s^2; poly P=c*V*s+B*s^2;",
        f"poly N=-({square})-P*Q+R*T; poly U9=0; int it;",
        "for (it=1;it<=9;it++) { U9=jet((N-2*s*U9+2*s*U9^2+s^2*U9^2)/4,8,sw); }",
        "map phi=r,s,s*U2,s*(Q+P)/2,s*(T+R)/2,s*(Q-P)/2,s*(T-R)/2,s*U9;",
        '"RESULT J on the arc through order 9", size(simplify(jet(phi(J),9,sw),2))==0;',
    ]


def script(fiber: str, prime: int, mutate: bool) -> str:
    spec = FIBERS[fiber]
    header = (ROOT / spec["header"][prime]).read_text().strip()
    names = PARAMETERS[fiber]
    count = spec["ngen"]
    components = dict(spec["components"].get(prime, {}))
    lines = [
        f"// blowup arcs on the {fiber} -> N- slice at p = {prime}" + (", mutated" if mutate else ""),
        "option(redSB);",
        'LIB "matrix.lib";',
        header,
        f'execute("ideal Grun="+read("{spec["gens"][prime]}")+";");',
        SIGNS,
        '"RESULT signs of the run generators against the header", eps;',
        f'execute("ring Y={prime},(y(1..{count})),dp;");',
        f'execute("ideal K="+read("{spec["k2"][prime]}")+";");',
        '"RESULT K2 generators", size(K);',
    ]
    for name, path in components.items():
        lines.append(f'execute("ideal C{name}="+read("{path}")+";");')
    if spec.get("lam"):
        r = ROOTS[prime]
        lines.append(
            f"ideal CLam=y(22),y(19)+y(21),y(18),y(13)-y(23),y(11)+{r}*y(23),y(8)+y(24),y(4)+y(12)-y(24),y(3),"
            f"y(2)+{r}*y(24);"
        )
        components["Lam"] = ""
    points = [",".join(("0", *(str(v) for v in point[: len(names)]))) for point in POINTS]
    lines += [
        f"ring S={prime},(s,{','.join(names)}),dp;",
        "intvec sw=1" + ",0" * len(names) + ";",
        *arc(fiber, mutate),
        "ideal Gs=phi(G); int j; int k; int nu=-1;",
        "for (k=0;k<=8 and nu<0;k++) { for (j=1;j<=ncols(Gs);j++) { if (jet(Gs[j],k,sw)!=0) { nu=k; } } }",
        "ideal F; for (j=1;j<=ncols(Gs);j++) { F[j]=subst(jet(Gs[j],nu,sw)-jet(Gs[j],nu-1,sw),s,1); }",
        "ideal Fr; for (j=1;j<=ncols(F);j++) { Fr[j]=eps[j]*F[j]; } map back=Y,Fr;",
        "matrix M=concat(jacob(F),transpose(matrix(F)));",
        f"map p1=S,{points[0]}; map p2=S,{points[1]};",
        '"RESULT nu", nu, "nonzero limit entries", size(simplify(F,2));',
        '"RESULT K2 nonzero on the limit", size(simplify(back(K),2));',
        *(
            f'"RESULT {name} generators nonzero on the limit", size(simplify(back(C{name}),2)), "of", '
            f"ncols(back(C{name}));"
            for name in components
        ),
        '"RESULT rank of [dF | F] at two points", rank(p1(M)), rank(p2(M));',
        "quit;",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    check = "--check" in sys.argv[1:]
    stale = []
    for fiber in PARAMETERS:
        for prime in ROOTS:
            for mutate in (False, True):
                path = HERE / f"{fiber}-blowup-arcs-p{prime}{'-mutated' if mutate else ''}.sing"
                text = script(fiber, prime, mutate)
                if check:
                    if not path.exists() or path.read_text() != text:
                        stale.append(path.name)
                else:
                    path.write_text(text)
    if stale:
        raise SystemExit(f"stale: {stale}")


if __name__ == "__main__":
    main()
