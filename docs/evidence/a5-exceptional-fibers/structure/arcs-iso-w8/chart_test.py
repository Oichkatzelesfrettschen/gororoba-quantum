"""One blowup chart decides whether the fiber over the origin of the blowup of I = (G) fills V(K2).

For a linear form l0 with QRNG coefficients and a0 = l0(G), the chart of Bl_I V(J) where a0 is a unit is
A = k[t, z]/((J, a0 z_i - G_i : i) : a0^infinity); its fiber over the origin is A/(t), an affine piece of
E0 = Proj F(I)_red. For Iso -> N-, K2 is prime and contains no linear form (h_1 = 17), so V(K2) meets every chart in a
dense open set: dim A/(t) = 4 means E0 = V(K2), hence L = K2 and F(I) = k[y]/K2; dim A/(t) <= 3 means dim E0 <= 3,
hence the analytic spread is at most 4 and F(I) is a proper quotient of k[y]/K2. The script reports the dimension of
the saturated chart (5 for a blowup of a 5-dimensional domain), the relation l0(z) = 1, and dim A/(t).

    $PYTHON docs/evidence/a5-exceptional-fibers/structure/arcs-iso-w8/chart_test.py FIBER PRIME DRAW_JSON
"""

import argparse
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
W = "docs/evidence/a5-exceptional-fibers/working"
GENS = {
    ("iso", 32009): f"{W}/distribute/out/a5-iso-d4/iso_p1/d2/gens.txt",
    ("iso", 32029): f"{W}/distribute/out/a5-p2-iso/iso_p2/d2/gens.txt",
    ("w8", 32009): f"{W}/distribute/out/a5-w8-receipt-p1/w8_p1/d2/gens.txt",
    ("w8", 32029): f"{W}/distribute/out/a5-p2-w8/w8_p2/d2/gens.txt",
}
K2 = {
    ("iso", 32009): f"{W}/runs/s3/iso_k2.rel",
    ("iso", 32029): f"{W}/distribute/out/a5-p2-iso/iso_p2/d2/relations-d2.rel",
    ("w8", 32009): f"{W}/runs/w8_a2/w8_k2.rel",
    ("w8", 32029): f"{W}/distribute/out/a5-p2-w8/w8_p2/d2/relations-upto-d2.rel",
}
HEADERS = {
    ("iso", 32009): f"{W}/build/inputs/p32009-r10754/iso-nm.sing",
    ("iso", 32029): f"{W}/build/inputs/p32029-r9115/iso-nm.sing",
    ("w8", 32009): f"{W}/build/inputs/p32009-r10754/w8-nm.sing",
    ("w8", 32029): f"{W}/build/inputs/p32029-r9115/w8-nm.sing",
}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("fiber", choices=["iso", "w8"])
    ap.add_argument("prime", type=int, choices=[32009, 32029])
    ap.add_argument("draw", help="ANU QRNG draw file; values below the prime are taken in index order")
    ap.add_argument(
        "--method",
        choices=["sat", "elim"],
        help="portfolio script: sat (iterated quotients) or elim (Rabinowitsch variable w); l0(z) - 1 added up front, "
        "option(noredTail), option(prot), every stage written to its own file",
    )
    ap.add_argument(
        "--coord",
        type=int,
        help="coordinate chart a0 = G_j, z_j = 1 (portfolio script, method sat); decides the case like the dense chart "
        "because K2 contains no linear form",
    )
    ap.add_argument(
        "--slice-draw",
        help="sliced chart: add l0(z) - 1 and four QRNG forms l1..l4(z) (from this draw) before saturating; "
        "the fiber over the origin is then finite and is compared with V(K2) cut by the same forms",
    )
    ap.add_argument(
        "--junk",
        action="store_true",
        help="with --slice-draw: saturate by one function per component of V(J + G) (t2 for L0, a generator nonzero at "
        "the origin for each other component) in place of a0; V(C) minus V(a0) is the graph and V(C) meets V(a0) only "
        "over V(J + G), so the saturation removes exactly the junk",
    )
    a = ap.parse_args()
    hdr = (ROOT / HEADERS[(a.fiber, a.prime)]).read_text()
    tvars = re.search(r"ring r=\d+,\((.*?)\)", hdr).group(1)  # type: ignore[union-attr]
    jtxt = re.search(r"ideal J=(.*?);", hdr, re.S).group(1)  # type: ignore[union-attr]
    gtxt = re.search(r"ideal G=(.*?);", hdr, re.S).group(1)  # type: ignore[union-attr]
    num = re.search(r"number I=(\d+);", hdr).group(1)  # type: ignore[union-attr]
    ngen = len([g for g in gtxt.split(",") if g.strip()])
    vals = json.loads((ROOT / a.draw).read_text())["values"]
    idx = [k for k, v in enumerate(vals) if v < a.prime][:ngen]
    coeffs = [vals[k] for k in idx]
    l0 = "+".join(f"{c}*G[{j + 1}]" for j, c in enumerate(coeffs))
    lz = "+".join(f"{c}*z({j + 1})" for j, c in enumerate(coeffs))
    if a.slice_draw:
        sv = json.loads((ROOT / a.slice_draw).read_text())["values"]
        sidx = [k for k, v in enumerate(sv) if v < a.prime][: 4 * ngen]
        forms = [
            "+".join(f"{sv[k]}*z({j + 1})" for j, k in enumerate(sidx[f * ngen : (f + 1) * ngen])) for f in range(4)
        ]
        tag = f"{a.fiber}-p{a.prime}-slice" + ("-junk" if a.junk else "")
        gens = GENS[(a.fiber, a.prime)]
        k2 = K2[(a.fiber, a.prime)]
        out = HERE / f"chart-{tag}.sing"
        out.write_text(
            f"// sliced blowup chart: a0 = l0(G) as chart-{a.fiber}-p{a.prime}.sing, plus l1..l4 from {a.slice_draw}\n"
            'LIB "elim.lib"; LIB "general.lib"; option(noredTail); option(prot); system("--ticks-per-sec",1);\n'
            "int t0=rtimer;\n"
            f"ring r={a.prime},({tvars},z(1..{ngen})),dp; number I={num};\n"
            f"ideal J={jtxt};\nideal G={gtxt};\n"
            f'execute("ideal Grun="+read("{gens}")+";");\n'
            "intvec eps; int jj; for (jj=1;jj<=ncols(G);jj++) { if (Grun[jj]==G[jj]) { eps[jj]=1; } else {"
            ' if (Grun[jj]==-G[jj]) { eps[jj]=-1; } else { ERROR("generator is not +-G"); } } }\n'
            f"poly a0={l0};\n"
            f"ideal Lam={lz}-1,{','.join(forms)};\n"
            # K2 in the header's coordinates: y_j of the run is eps_j G_j, so substitute y_j -> eps_j z_j
            f'ring Y={a.prime},(y(1..{ngen})),dp; execute("ideal K="+read("{k2}")+";");\n'
            "setring r; ideal epz; for (jj=1;jj<=ncols(G);jj++) { epz[jj]=eps[jj]*z(jj); } map toz=Y,epz;\n"
            "ideal Kz=toz(K);\n"
            f"ideal KS=std(Kz+Lam+ideal({tvars}));\n"
            f'"RESULT {tag} K2 slice: dim", dim(KS), "vdim", vdim(KS), "s", rtimer-t0;\n'
            "poly sepv=z(2); ideal els=eliminate(KS, product(maxideal(1))/sepv); list fs=factorize(els[1]); string fd;"
            ' for (jj=2;jj<=size(fs[1]);jj++) { fd=fd+" "+string(deg(fs[1][jj]))+"^"+string(fs[2][jj]); }\n'
            f'"RESULT {tag} K2 slice eliminant of z(2): deg", deg(els[1]), "factors", fd;\n'
            f"ideal C=J; int i; for (i=1;i<={ngen};i++) {{ C=C+(a0*z(i)-G[i]); }} C=C+Lam;\n"
            + (
                'LIB "primdec.lib"; list mp=minAssGTZ(J+G); ideal H; int q;\n'
                "for (q=1;q<=size(mp);q++) { if (size(reduce(mp[q],std(maxideal(1))))==0) {\n"
                "  if (size(reduce(ideal(t2),std(mp[q])))!=0) { "
                'ERROR("t2 does not vanish on the component through 0"); }\n'
                "  H=H+t2; } else { int g; int found=0; for (g=1;g<=ncols(mp[q]);g++) { if (found==0) {\n"
                "  if (jet(mp[q][g],0)!=0) { H=H+mp[q][g]; found=1; } } }\n"
                '  if (found==0) { ERROR("no generator nonzero at the origin"); } kill g,found; } }\n'
                f'"RESULT {tag} components of V(J+G)", size(mp), "saturating factors", ncols(H);\n'
                'ideal S=C; for (q=1;q<=ncols(H);q++) { def SQ=sat(S,ideal(H[q])); if (typeof(SQ)=="list") { S=SQ[1]; }'
                " else { S=SQ; } kill SQ;\n"
                f'  "RESULT {tag} saturated by factor", q, "s", rtimer-t0; }}\n'
                if a.junk
                else 'def SS=sat(C,ideal(a0)); ideal S; if (typeof(SS)=="list") { S=SS[1]; } else { S=SS; }\n'
            )
            + f'"RESULT {tag} saturation done s", rtimer-t0;\n'
            f'write(":w chart-sat-{tag}.txt", S);\n'
            f'S=std(S); "RESULT {tag} sliced chart dim", dim(S), "s", rtimer-t0;\n'
            f"ideal E=std(S+ideal({tvars}));\n"
            f'"RESULT {tag} fiber over the origin: dim", dim(E), "vdim", vdim(E), "s", rtimer-t0;\n'
            f'write(":w chart-fiber-{tag}.txt", E);\n'
            f'"RESULT {tag} K2 vanishes on the fiber", size(reduce(Kz,E))==0, "fiber inside the K2 slice",'
            ' size(reduce(KS,E))==0, "K2 slice inside the fiber", size(reduce(E,KS))==0;\n'
            "quit;\n"
        )
        ledger = {
            "draw": a.slice_draw,
            "rule": f"uint16 values < {a.prime} in index order, zero-based; l1..l4 in order",
            "coefficients": [[k, sv[k]] for k in sidx],
        }
        (HERE / f"chart-{tag}-coefficients.json").write_text(json.dumps(ledger, indent=1) + "\n")
        print(out.relative_to(ROOT))
        return
    if a.coord:
        j = a.coord
        tag = f"{a.fiber}-p{a.prime}-coord{j}"
        out = HERE / f"chart-{tag}.sing"
        out.write_text(
            f"// coordinate blowup chart a0 = G_{j}, z({j}) = 1, method sat\n"
            'LIB "elim.lib"; option(noredTail); option(prot); system("--ticks-per-sec",1); int t0=rtimer;\n'
            f"ring r={a.prime},({tvars},z(1..{ngen})),dp; number I={num};\n"
            f"ideal J={jtxt};\nideal G={gtxt};\n"
            f"poly a0=G[{j}];\n"
            f"ideal C=J; int i; for (i=1;i<={ngen};i++) {{ if (i!={j}) {{ C=C+(a0*z(i)-G[i]); }} }} C=C+(z({j})-1);\n"
            'def SS=sat(C,ideal(a0)); ideal S; if (typeof(SS)=="list") { S=SS[1]; } else { S=SS; }\n'
            f'"RESULT {tag} saturation done s", rtimer-t0;\n'
            f'write(":w chart-sat-{tag}.txt", S);\n'
            f'S=std(S); "RESULT {tag} chart dim", dim(S), "s", rtimer-t0;\n'
            f'write(":w chart-std-{tag}.txt", S);\n'
            f'ideal E=std(S+ideal({tvars})); "RESULT {tag} fiber over the origin in the chart: dim", dim(E), '
            '"degree", mult(E), "s", rtimer-t0;\n'
            f'write(":w chart-fiber-{tag}.txt", E);\nquit;\n'
        )
        print(out.relative_to(ROOT))
        return
    if a.method:
        out = HERE / f"chart-{a.fiber}-p{a.prime}-{a.method}.sing"
        tag = f"{a.fiber}-p{a.prime}-{a.method}"
        nall = len(tvars.split(",")) + ngen
        ring = (
            f"ring r={a.prime},({tvars},z(1..{ngen})),dp;"
            if a.method == "sat"
            else f"ring r={a.prime},(w,{tvars},z(1..{ngen})),(dp(1),dp({nall}));"
        )
        sat = (
            'def SS=sat(C,ideal(a0)); ideal S; if (typeof(SS)=="list") { S=SS[1]; } else { S=SS; }\n'
            if a.method == "sat"
            else "ideal S=eliminate(C+ideal(1-w*a0),w);\n"
        )
        out.write_text(
            f"// blowup chart a0 = l0(G), method {a.method}; "
            f"l0 coefficients in chart-{a.fiber}-p{a.prime}-coefficients.json\n"
            'LIB "elim.lib"; option(noredTail); option(prot); system("--ticks-per-sec",1); int t0=rtimer;\n'
            f"{ring} number I={num};\n"
            f"ideal J={jtxt};\nideal G={gtxt};\n"
            f"poly a0={l0};\n"
            f"ideal C=J; int i; for (i=1;i<={ngen};i++) {{ C=C+(a0*z(i)-G[i]); }} C=C+({lz}-1);\n"
            f"{sat}"
            f'"RESULT {tag} saturation done s", rtimer-t0;\n'
            f'write(":w chart-sat-{tag}.txt", S);\n'
            f"ring rr={a.prime},({tvars},z(1..{ngen})),dp; number I={num}; ideal S=imap(r,S);\n"
            f'S=std(S); "RESULT {tag} chart dim", dim(S), "s", rtimer-t0;\n'
            f'"RESULT {tag} l0(z) = 1 in the chart", reduce({lz}-1,S)==0;\n'
            f'write(":w chart-std-{tag}.txt", S);\n'
            f'ideal E=std(S+ideal({tvars})); "RESULT {tag} fiber over the origin in the chart: dim", dim(E), '
            '"degree", mult(E), "s", rtimer-t0;\n'
            f'write(":w chart-fiber-{tag}.txt", E);\nquit;\n'
        )
        print(out.relative_to(ROOT))
        return
    out = HERE / f"chart-{a.fiber}-p{a.prime}.sing"
    out.write_text(
        f"// blowup chart a0 = l0(G), l0 from {a.draw} zero-based indices {idx[0]}..{idx[-1]} (values < p in order)\n"
        'LIB "elim.lib"; option(redSB); system("--ticks-per-sec",1); int t0=rtimer;\n'
        f"ring r={a.prime},({tvars},z(1..{ngen})),dp; number I={num};\n"
        f"ideal J={jtxt};\nideal G={gtxt};\n"
        f"poly a0={l0};\n"
        f"ideal C=J; int i; for (i=1;i<={ngen};i++) {{ C=C+(a0*z(i)-G[i]); }}\n"
        'def SS=sat(C,ideal(a0)); ideal S; if (typeof(SS)=="list") { S=SS[1]; } else { S=SS; }\n'
        'S=std(S); "RESULT chart dim", dim(S), "s", rtimer-t0;\n'
        f'"RESULT l0(z) = 1 in the chart", reduce({lz}-1,S)==0;\n'
        f'ideal E=std(S+ideal({tvars})); "RESULT fiber over the origin in the chart: dim", dim(E), '
        '"degree", mult(E), "s", rtimer-t0;\n'
        'write(":w chart-sat.txt", S);\nquit;\n'
    )
    ledger = {
        "draw": a.draw,
        "rule": f"uint16 values < {a.prime} in index order, zero-based; l0 = sum c_j G_j",
        "coefficients": [[k, vals[k]] for k in idx],
    }
    (HERE / f"chart-{a.fiber}-p{a.prime}-coefficients.json").write_text(json.dumps(ledger, indent=1) + "\n")
    print(out.relative_to(ROOT), "indices", idx[0], "..", idx[-1])


if __name__ == "__main__":
    main()
