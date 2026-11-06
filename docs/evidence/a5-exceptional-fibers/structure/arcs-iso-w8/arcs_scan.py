"""Arc families on the Iso -> N- and W8 -> N- slices and the rank of their limit maps.

Both slices carry the split quadric t2^2 + t4^2 = a b with a = t2 + i t4, b = t2 - i t4 and t5^2 + t6^2 = c d with
c = t5 + i t6, d = t5 - i t6, so J = g - a b + c d - t7^2 with g = 0 (Iso) or g = t1^2 t9^2 - 2 t1^2 t9 + 2 t1 t9^2
- 4 t1 t9 (W8, after the sign of J). A family sets a = s^alpha and every other free coordinate to one parameter times
a power of s, and b = (g + c d - t7^2) / s^alpha, a polynomial when every term of the numerator has s-order at least
alpha; each script checks J = 0 on the arc identically. The limit vector F is the coefficient of s^nu in G(x(s)) at
the least order nu, a vector of polynomials in the parameters. Each script reports nu, the rank of [dF | F] at two
fixed parameter points (a rank at a point bounds the generic rank, which is the dimension of the cone of limits, from
below), and whether K2 and the generators of each component vanish on F identically.

    $PYTHON docs/evidence/a5-exceptional-fibers/structure/arcs-iso-w8/arcs_scan.py
"""

import itertools
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
W = "docs/evidence/a5-exceptional-fibers/working"
S = "docs/evidence/a5-exceptional-fibers/structure"
ROOTS = {32009: 10754, 32029: 9115}
POINTS = ((2, 3, 5, 7, 11), (13, 4, 9, 6, 17))

# fiber -> (header per prime, K2 per prime, components per prime as (name, file or None), free coordinates)
FIBERS: dict[str, dict[str, Any]] = {
    "iso": {
        "header": {p: f"{W}/build/inputs/p{p}-r{r}/iso-nm.sing" for p, r in ROOTS.items()},
        "k2": {32009: f"{W}/runs/s3/iso_k2.rel", 32029: f"{W}/distribute/out/a5-p2-iso/iso_p2/d2/relations-d2.rel"},
        # generator lists of the K2 runs; runs/s3 uses the same list as a5-iso-d4
        "gens": {
            32009: f"{W}/distribute/out/a5-iso-d4/iso_p1/d2/gens.txt",
            32029: f"{W}/distribute/out/a5-p2-iso/iso_p2/d2/gens.txt",
        },
        "ngen": 17,
        "free": ["c", "d", "t7", "t3"],
        "components": {},
    },
    "w8": {
        "header": {p: f"{W}/build/inputs/p{p}-r{r}/w8-nm.sing" for p, r in ROOTS.items()},
        "k2": {
            32009: f"{W}/runs/w8_a2/w8_k2.rel",
            32029: f"{W}/distribute/out/a5-p2-w8/w8_p2/d2/relations-upto-d2.rel",
        },
        "gens": {
            32009: f"{W}/distribute/out/a5-w8-receipt-p1/w8_p1/d2/gens.txt",
            32029: f"{W}/distribute/out/a5-p2-w8/w8_p2/d2/gens.txt",
        },
        "ngen": 24,
        "free": ["c", "d", "t7", "t1", "t9"],
        # P at 32009 from check.sing; Lam = the nine linear forms of P with the prime's root of -1 (V(K2 + Lam) has
        # top-dimensional part the degree-20 component at both primes, w8-kp/README.md)
        "components": {32009: {"P": f"{S}/w8-kp/P-p32009.txt"}},
        "lam": True,
    },
}


def weight_vectors(fiber: str) -> list[tuple[int, ...]]:
    """(alpha, weights of the free coordinates) with b(0) = 0: min(w_c + w_d, 2 w_t7[, w_t1 + w_t9]) > alpha."""
    n = len(FIBERS[fiber]["free"])
    out = []
    for alpha in range(1, 4):
        for w in itertools.product(range(1, 4), repeat=n):
            orders = [w[0] + w[1], 2 * w[2]] + ([w[3] + w[4]] if fiber == "w8" else [])
            if min(orders) > alpha:
                out.append((alpha, *w))
    return out


def script(fiber: str, p: int, families: list[tuple[int, ...]]) -> str:
    f = FIBERS[fiber]
    header = (ROOT / f["header"][p]).read_text().strip()
    free = f["free"]
    params = [x.upper() if x in "cd" else {"t7": "T", "t3": "Z", "t1": "U", "t9": "V"}[x] for x in free]
    n = f["ngen"]
    lines = [
        f"// arc families on the {fiber} -> N- slice at p = {p}",
        "option(redSB);",
        'LIB "matrix.lib";',
        header,
        # y_j of the K2 file is the j-th generator of its run, which equals eps_j G_j of the header with eps_j = +-1
        f'execute("ideal Grun="+read("{f["gens"][p]}")+";");',
        "intvec eps; int jj; for (jj=1;jj<=ncols(G);jj++) { if (Grun[jj]==G[jj]) { eps[jj]=1; } else {"
        ' if (Grun[jj]==-G[jj]) { eps[jj]=-1; } else { ERROR("generator "+string(jj)+" is not +-G"); } } }',
        '"RESULT signs of the run generators against the header", eps;',
        f'execute("ring Y={p},(y(1..{n})),dp;");',
        f'execute("ideal K="+read("{f["k2"][p]}")+";");',
    ]
    comps = f["components"].get(p, {})
    for name, path in comps.items():
        lines.append(f'execute("ideal C{name}="+read("{path}")+";");')
    if f.get("lam"):
        r = ROOTS[p]
        lam = f"y(22),y(19)+y(21),y(18),y(13)-y(23),y(11)+{r}*y(23),y(8)+y(24),y(4)+y(12)-y(24),y(3),y(2)+{r}*y(24)"
        lines.append(f"ideal CLam={lam};")
        comps = {**comps, "Lam": ""}
    lines += [
        f"ring R={p},(s,{','.join(params)}),dp;",
        "number I=imap(r,I);",
        "intvec sw=1" + ",0" * len(params) + ";",
        "proc lowest(ideal Gs, intvec sw) { int k; int j; for (k=0;k<=60;k++) { for (j=1;j<=ncols(Gs);j++) {"
        " if (jet(Gs[j],k,sw)!=0) { return(k); } } } return(-1); }",
    ]
    for fam in families:
        alpha, *w = fam
        val = dict(zip(free, (f"{q}*s^{e}" for q, e in zip(params, w, strict=True)), strict=True))
        g = "0"
        if fiber == "w8":
            t1, t9 = f"({val['t1']})", f"({val['t9']})"
            g = f"{t1}^2*{t9}^2-2*{t1}^2*{t9}+2*{t1}*{t9}^2-4*{t1}*{t9}"
        tag = "a" + str(alpha) + "_" + "_".join(f"{x}{e}" for x, e in zip(free, w, strict=True))
        lines += [
            f"poly A=s^{alpha}; poly Cc={val['c']}; poly Dd={val['d']}; poly T7={val['t7']};",
            f"poly num={g}+Cc*Dd-T7^2; poly B=num/A;",
        ]
        if fiber == "iso":
            lines.append(f"map phi=r,(A+B)/2,{val['t3']},(A-B)/(2*I),(Cc+Dd)/2,(Cc-Dd)/(2*I),T7;")
        else:
            lines.append(f"map phi=r,{val['t1']},(A+B)/2,(A-B)/(2*I),(Cc+Dd)/2,(Cc-Dd)/(2*I),T7,{val['t9']};")
        pts = [",".join(["0", *[str(v) for v in pt[: len(params)]]]) for pt in POINTS]
        lines += [
            "ideal Gs=phi(G); int nu=lowest(Gs,sw); ideal F; int j;",
            "for (j=1;j<=ncols(Gs);j++) { F[j]=subst(jet(Gs[j],nu,sw)-jet(Gs[j],nu-1,sw),s,1); }",
            "matrix M=concat(jacob(F),transpose(matrix(F)));",
            f"map p1=R,{pts[0]}; map p2=R,{pts[1]};",
            "ideal Fr; for (j=1;j<=ncols(F);j++) { Fr[j]=eps[j]*F[j]; } map back=Y,Fr; ideal kk=back(K);",
        ]
        comp_checks = " ".join(f'"{name}", size(simplify(back(C{name}),2))==0,' for name in comps)
        lines += [
            f'"RESULT {tag} J", phi(J)==0, "nu", nu, "rank", rank(p1(M)), rank(p2(M)), '
            f'"K2", size(simplify(kk,2))==0, {comp_checks} "zeroF", size(simplify(F,2))==0;',
            "kill A,Cc,Dd,T7,num,B,phi,Gs,nu,F,Fr,j,M,p1,p2,back,kk;",
        ]
    lines.append("quit;")
    return "\n".join(x for x in lines if x) + "\n"


def main() -> None:
    # the certificate of V(P) inside the fiber over the origin of W8: the linear family a = s, c = C s, d = D s,
    # t7 = T s, t1 = U s, t9 = V s at both primes
    for p in ROOTS:
        out = HERE / f"cert-w8-P-p{p}.sing"
        out.write_text(script("w8", p, [(1, 1, 1, 1, 1, 1)]))
        print(out.relative_to(ROOT))
    for fiber in FIBERS:
        fams = weight_vectors(fiber)
        for p in ROOTS:
            out = HERE / f"scan-{fiber}-p{p}.sing"
            out.write_text(script(fiber, p, fams))
            print(out.relative_to(ROOT), len(fams), "families")


if __name__ == "__main__":
    main()
