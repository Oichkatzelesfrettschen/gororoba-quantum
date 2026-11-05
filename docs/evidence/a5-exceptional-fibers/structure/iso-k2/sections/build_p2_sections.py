"""Four further QRNG sections of the Iso K2 at p = 32029, each cut to 23 points (four forms), for the subset-sum
exclusion of F_p-component degree splits (usage: build_p2_sections.py FIRST_SECTION_NUMBER COUNT DRAW_JSON...)."""

import json
import sys
from pathlib import Path

D = Path("docs/evidence/a5-exceptional-fibers/structure/iso-k2/sections")
first, count, draws = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3:]
draw = ",".join(draws)
vals = [x for d in draws for x in json.load(open(d))["values"]]
need = 68 * count
idx = [i for i in range(len(vals)) if vals[i] < 32029][:need]
if len(idx) < need:
    raise SystemExit(f"only {len(idx)} usable values")
v = [vals[i] for i in idx]
rel = Path("docs/evidence/a5-exceptional-fibers/working/distribute/out/a5-p2-iso/iso_p2/d2/relations-d2.rel").resolve()
sections: list[list[str]] = []
rec = {"draw": draw, "rule": "uint16 values < 32029 in index order, zero-based", "indices": idx, "sections": sections}
for s in range(count):
    forms = [
        "+".join(f"{a}*y({j + 1})" for j, a in enumerate(v[(4 * s + f) * 17 : (4 * s + f + 1) * 17])) for f in range(4)
    ]
    sections.append(forms)
    (D / f"p2-section{s + first}.sing").write_text(
        'LIB "general.lib"; option(redSB); system("--ticks-per-sec",1); int t0=rtimer;\n'
        f'ring Y=32029,(y(1..17)),dp; execute("ideal K="+read("{rel}")+";");\n'
        f"ideal Z=std(K+ideal({','.join(forms)}));\n"
        f'"RESULT p32029 section {s + first} dim", dim(Z), "deg", mult(Z);\n'
        "ideal A=std(Z+ideal(y(1)-1));\n"
        f'"RESULT p32029 section {s + first} affine vdim", vdim(A);\n'
        "int j; string fd; poly e=eliminate(A, product(maxideal(1))/y(2))[1]; list F=factorize(e); "
        'for (j=2;j<=size(F[1]);j++) { fd=fd+" "+string(deg(F[1][j]))+"^"+string(F[2][j]); }\n'
        f'"RESULT p32029 section {s + first} eliminant y(2) deg", deg(e), '
        '"factor degree^multiplicity", fd, "s", rtimer-t0;\n'
        "quit;\n"
    )
(D / f"coefficients-p32029-s{first}.json").write_text(json.dumps(rec, indent=1))
print("ok", len(idx))
