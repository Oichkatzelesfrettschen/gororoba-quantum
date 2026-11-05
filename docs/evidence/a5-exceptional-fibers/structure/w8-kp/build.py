"""Point sections of V(K2 : P) for W8 -> N- at p = 32009, from ANU QRNG coefficients.

K2 : P (quotient.txt, projective dimension 5, degree 30) is radical because K2 is. Each section adds five QRNG linear
forms L1..L5 and the affine chart l0 = 1 for a sixth QRNG form, then a QRNG separating form u through t = u. When
vdim = 30 and the eliminant of t has degree 30 and is squarefree, the section is 30 distinct points, each F_p-component
of V(K2 : P) of degree d contributes exactly d of them as a Frobenius-stable set, and the factor degrees of the
eliminant are the Frobenius orbits, which refine the component degrees. One orbit of size 30 proves K2 : P prime.

    $PYTHON docs/evidence/a5-exceptional-fibers/structure/w8-kp/build.py COUNT DRAW_JSON...
"""

import json
import sys
from pathlib import Path

P = 32009
NV = 24
PER = 7 * NV  # L1..L5, l0, u
D = Path("docs/evidence/a5-exceptional-fibers/structure/w8-kp")
Q = "docs/evidence/a5-exceptional-fibers/structure/w8-kp/quotient.txt"


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
        "rule": "uint16 values < 32009 in draw order then index order, each used once; indices zero-based",
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
        (D / f"section{s + 1}.sing").write_text(
            'LIB "general.lib"; option(redSB); system("--ticks-per-sec",1); int t0=rtimer;\n'
            f'ring Y={P},(y(1..{NV}),t),dp; execute("ideal Q="+read("quotient.txt")+";");\n'
            f"ideal A=std(Q+ideal({L})+ideal({forms[5]}-1)+ideal(t-({forms[6]})));\n"
            f'"RESULT section {s + 1} dim", dim(A), "vdim", vdim(A), "s", rtimer-t0;\n'
            'poly e=eliminate(A, product(maxideal(1))/t)[1]; list F=factorize(e); string fd=""; int j;\n'
            'for (j=2;j<=size(F[1]);j++) { fd=fd+" "+string(deg(F[1][j]))+"^"+string(F[2][j]); }\n'
            f'"RESULT section {s + 1} eliminant deg", deg(e), "factor degree^multiplicity", fd, "s", rtimer-t0;\n'
            "quit;\n"
        )
    (D / "coefficients.json").write_text(json.dumps(ledger, indent=1))
    print("sections", count, "values used", count * PER, "of", len(vals))


if __name__ == "__main__":
    main()
