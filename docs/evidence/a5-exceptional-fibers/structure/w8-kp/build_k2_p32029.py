"""Point sections of the whole W8 -> N- quadric scheme V(K2) at p = 32029, from ANU QRNG coefficients.

K2 at 32029 (`relations-upto-d2.rel` of the a5-p2-w8 run) has projective dimension 5, degree 50 and a Cohen-Macaulay
quotient (`k2-cm.jsonl`). Each section adds five QRNG forms, the chart l0 = 1 for a sixth and t = u for a seventh. A
squarefree eliminant of degree 50 = vdim makes the section reduced, which lifts to K2 radical, and its factor degrees
are Frobenius orbits that refine the degrees of the F_p-components of V(K2).

    $PYTHON docs/evidence/a5-exceptional-fibers/structure/w8-kp/build_k2_p32029.py COUNT DRAW_JSON...
"""

import json
import sys
from pathlib import Path

P = 32029
NV = 24
PER = 7 * NV  # L1..L5, l0, u
D = Path("docs/evidence/a5-exceptional-fibers/structure/w8-kp")
REL = "docs/evidence/a5-exceptional-fibers/working/distribute/out/a5-p2-w8/w8_p2/d2/relations-upto-d2.rel"


def main() -> None:
    count = int(sys.argv[1])
    vals: list[tuple[str, int, int]] = []
    for draw in sys.argv[2:]:
        v = json.load(open(draw))["values"]
        vals += [(draw, i, x) for i, x in enumerate(v) if x < P]
    if len(vals) < count * PER:
        raise SystemExit(f"{len(vals)} usable values, {count * PER} needed")
    sections: list[dict[str, object]] = []
    ledger = {
        "rule": "uint16 values < 32029 in draw order then index order, each used once; indices zero-based",
        "draws": sys.argv[2:],
        "sections": sections,
    }
    for s in range(count):
        chunk = vals[s * PER : (s + 1) * PER]
        forms = ["+".join(f"{c[2]}*y({j + 1})" for j, c in enumerate(chunk[k * NV : (k + 1) * NV])) for k in range(7)]
        sections.append(
            {
                "section": s + 1,
                "first": [chunk[0][0], chunk[0][1]],
                "last": [chunk[-1][0], chunk[-1][1]],
                "forms": forms,
            }
        )
        L = ",".join(forms[:5])
        (D / f"k2-p32029-section{s + 1}.sing").write_text(
            'LIB "general.lib"; option(redSB); system("--ticks-per-sec",1); int t0=rtimer;\n'
            f'ring Y={P},(y(1..{NV}),t),dp; execute("ideal Q="+read("{REL}")+";");\n'
            f"ideal A=std(Q+ideal({L})+ideal({forms[5]}-1)+ideal(t-({forms[6]})));\n"
            f'"RESULT k2 p32029 section {s + 1} dim", dim(A), "vdim", vdim(A), "s", rtimer-t0;\n'
            'poly e=eliminate(A, product(maxideal(1))/t)[1]; list F=factorize(e); string fd=""; int j;\n'
            'for (j=2;j<=size(F[1]);j++) { fd=fd+" "+string(deg(F[1][j]))+"^"+string(F[2][j]); }\n'
            f'"RESULT k2 p32029 section {s + 1} eliminant deg", deg(e), '
            '"factor degree^multiplicity", fd, "s", rtimer-t0;\n'
            "quit;\n"
        )
    (D / "coefficients-k2-p32029.json").write_text(json.dumps(ledger, indent=1))
    print("sections", count, "values used", count * PER, "of", len(vals))


if __name__ == "__main__":
    main()
