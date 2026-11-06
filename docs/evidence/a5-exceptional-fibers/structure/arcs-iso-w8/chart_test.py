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
