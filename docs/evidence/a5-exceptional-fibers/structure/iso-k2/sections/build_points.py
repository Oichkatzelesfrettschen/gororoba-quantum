"""Fourth QRNG linear form per section: cut V(K2) to 23 points; a coordinate whose eliminant has degree 23 and is
squarefree makes the point scheme k[t]/(e), reduced, and its factorization gives the Frobenius orbits over
F_32009 (usage: build_points.py DRAW_JSON)."""

import json
import sys
from pathlib import Path

D = Path("docs/evidence/a5-exceptional-fibers/structure/iso-k2/sections")
c = json.loads((D / "coefficients.json").read_text())
draw = sys.argv[1]
vals = json.load(open(draw))["values"]
idx = [i for i in range(len(vals)) if vals[i] < 32009][:34]
if len(idx) < 34:
    raise SystemExit(f"only {len(idx)} usable values")
v = [vals[i] for i in idx]
f4 = ["+".join(f"{a}*y({j + 1})" for j, a in enumerate(v[s * 17 : (s + 1) * 17])) for s in range(2)]
c["points_forms"] = {
    "draw": draw,
    "rule": "uint16 values < 32009 in index order",
    "indices_zero_based": idx,
    "section1_fourth": f4[0],
    "section2_fourth": f4[1],
}
c["indices_note"] = "all indices are zero-based"
(D / "coefficients.json").write_text(json.dumps(c, indent=1))
rel = Path("docs/evidence/a5-exceptional-fibers/working/runs/s3/iso_k2.rel").resolve()
for s in range(2):
    L = ",".join(c["sections"][s] + [f4[s]])
    (D / f"points{s + 1}.sing").write_text(
        'LIB "primdec.lib"; option(redSB); system("--ticks-per-sec",1); int t0=rtimer;\n'
        f'ring Y=32009,(y(1..17)),dp; execute("ideal K="+read("{rel}")+";");\n'
        f"ideal Z=std(K+ideal({L}));\n"
        f'"RESULT points {s + 1} dim", dim(Z), "deg", mult(Z), "s", rtimer-t0;\n'
        "ideal A=std(Z+ideal(y(1)-1));\n"
        f'"RESULT points {s + 1} affine vdim", vdim(A);\n'
        "int i; int j; string fd; for (i=2;i<=17;i++) { poly e=eliminate(A, product(maxideal(1))/y(i))[1]; "
        'list F=factorize(e); fd=""; for (j=2;j<=size(F[1]);j++) { '
        'fd=fd+" "+string(deg(F[1][j]))+"^"+string(F[2][j]); } '
        f'"RESULT points {s + 1} eliminant y("+string(i)+") deg", deg(e), '
        '"factor degree^multiplicity", fd, "s", rtimer-t0; kill e; kill F; }\n'
        "quit;\n"
    )
print("ok", idx[0], "..", idx[-1])
