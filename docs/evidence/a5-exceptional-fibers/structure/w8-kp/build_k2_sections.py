"""Point sections of the whole W8 -> N- quadric scheme V(K2) at one prime, from ANU QRNG coefficients, and the check
that isolates its degree-20 part.

K2 has projective dimension 5, degree 50 and a Cohen-Macaulay quotient at both primes (`k2-cm.jsonl`). Each section
adds five QRNG forms L1..L5, the chart l0 = 1 for a sixth form and t = u for a seventh. A squarefree eliminant of
degree 50 = vdim makes the section reduced, which lifts to K2 radical, and its factor degrees are Frobenius orbits
that refine the degrees of the F_p-components of V(K2). `p-pP-check.sing` adds Lambda, the nine linear forms of P with
the prime's root of -1, to K2 and to the first section. The ledger records the draw file and zero-based index of
every coefficient.

    $PYTHON docs/evidence/a5-exceptional-fibers/structure/w8-kp/build_k2_sections.py PRIME COUNT DRAW_JSON...
"""

import json
import sys
from pathlib import Path

NV = 24
PER = 7 * NV  # L1..L5, l0, u
D = Path("docs/evidence/a5-exceptional-fibers/structure/w8-kp")
W = "docs/evidence/a5-exceptional-fibers/working"
REL = {32009: f"{W}/runs/w8_a2/w8_k2.rel", 32029: f"{W}/distribute/out/a5-p2-w8/w8_p2/d2/relations-upto-d2.rel"}
ROOT_OF_MINUS_ONE = {32009: 10754, 32029: 9115}


def main() -> None:
    p, count = int(sys.argv[1]), int(sys.argv[2])
    draws = sys.argv[3:]
    vals: list[tuple[str, int, int]] = []
    for draw in draws:
        v = json.load(open(draw))["values"]
        vals += [(draw, i, x) for i, x in enumerate(v) if x < p]
    if len(vals) < count * PER:
        raise SystemExit(f"{len(vals)} usable values, {count * PER} needed")
    sections: list[dict[str, object]] = []
    ledger = {
        "rule": f"uint16 values < {p} in draw order then index order, each used once; indices zero-based",
        "draws": draws,
        "sections": sections,
    }
    texts = []
    for s in range(count):
        chunk = vals[s * PER : (s + 1) * PER]
        forms = ["+".join(f"{c[2]}*y({j + 1})" for j, c in enumerate(chunk[k * NV : (k + 1) * NV])) for k in range(7)]
        sections.append(
            {
                "section": s + 1,
                "coefficients": [[[c[0], c[1], c[2]] for c in chunk[k * NV : (k + 1) * NV]] for k in range(7)],
                "forms": forms,
            }
        )
        L = ",".join(forms[:5])
        text = (
            'LIB "general.lib"; option(redSB); system("--ticks-per-sec",1); int t0=rtimer;\n'
            f'ring Y={p},(y(1..{NV}),t),dp; execute("ideal Q="+read("{REL[p]}")+";");\n'
            f"ideal A=std(Q+ideal({L})+ideal({forms[5]}-1)+ideal(t-({forms[6]})));\n"
            f'"RESULT k2 p{p} section {s + 1} dim", dim(A), "vdim", vdim(A), "s", rtimer-t0;\n'
            'poly e=eliminate(A, product(maxideal(1))/t)[1]; list F=factorize(e); string fd=""; int j;\n'
            'for (j=2;j<=size(F[1]);j++) { fd=fd+" "+string(deg(F[1][j]))+"^"+string(F[2][j]); }\n'
            f'"RESULT k2 p{p} section {s + 1} eliminant deg", deg(e), '
            '"factor degree^multiplicity", fd, "s", rtimer-t0;\n'
            "quit;\n"
        )
        (D / f"k2-p{p}-section{s + 1}.sing").write_text(text)
        texts.append(text)
    r = ROOT_OF_MINUS_ONE[p]
    lam = f"y(22),y(19)+y(21),y(18),y(13)-y(23),y(11)+{r}*y(23),y(8)+y(24),y(4)+y(12)-y(24),y(3),y(2)+{r}*y(24)"
    s1 = texts[0].splitlines()
    check = [
        s1[0],
        s1[1],
        f"ideal Lam={lam};",
        "ideal KL=std(Q+Lam);",
        '"RESULT K2+Lam projdim", dim(KL)-2, "degree", mult(KL);',
        s1[2].replace("std(Q+", "std(Q+Lam+"),
        '"RESULT K2+Lam section 1 dim", dim(A), "vdim", vdim(A), "s", rtimer-t0;',
        s1[4],
        s1[5],
        s1[6].replace(f"RESULT k2 p{p} section 1", "RESULT K2+Lam section 1"),
        "quit;",
    ]
    (D / f"p-p{p}-check.sing").write_text("\n".join(check) + "\n")
    (D / f"coefficients-k2-p{p}.json").write_text(json.dumps(ledger, indent=1))
    print("prime", p, "sections", count, "values used", count * PER, "of", len(vals))


if __name__ == "__main__":
    main()
