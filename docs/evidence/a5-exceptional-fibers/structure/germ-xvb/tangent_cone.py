"""Emit a Singular script computing the tangent cone of J at the origin by the normal-cone deformation.

Each generator f becomes f(u t) / u^ord(f) in k[t, u]; saturating by u and setting u = 0 gives the ideal of initial
forms (global dp ordering throughout). The script prints the cone's Hilbert series numerator, minimal generator
degrees, the dimension of the span of its linear forms, the projective dimension and degree of its singular locus and
the (dimension, degree) of each minimal prime. Usage: tangent_cone.py HEADER TAG > script.sing
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


def field(pattern: str, text: str) -> str:
    m = re.search(pattern, text)
    if m is None:
        raise ValueError(f"header lacks {pattern}")
    return m.group(1)


def lowest_degree(poly: str) -> int:
    degs = []
    for _sign, body in re.findall(r"([+-]?)([^+-]+)", poly):
        deg = 0
        for f in body.split("*"):
            if not re.fullmatch(r"\d+", f):
                _v, _, e = f.partition("^")
                deg += int(e) if e else 1
        degs.append(deg)
    return min(degs)


def main() -> None:
    t = Path(sys.argv[1]).read_text()
    tag = sys.argv[2]
    p = field(r"ring r=(\d+),", t)
    names = field(r"ring r=\d+,\(([^)]*)\)", t)
    J = [g.replace("\n", "").replace(" ", "") for g in field(r"ideal J=([^;]*);", t).split(",")]
    subst = ",".join(f"{v}*u" for v in names.split(","))
    lines = [
        f"ring R={p},({names},u),dp;",
        'LIB "elim.lib"; LIB "primdec.lib"; LIB "sing.lib";',
        f"map phi=R,{subst};",
        "ideal F;",
    ]
    for i, g in enumerate(J, 1):
        lines.append(f"poly f{i}={g}; F[{i}]=phi(f{i})/u^{lowest_degree(g)};")
    lines += [
        'def S0=sat(F,u); ideal K; if(typeof(S0)=="list"){ K=S0[1]; } else { K=S0; }',
        '"RESULT check generators_in", ncols(F), "saturated", ncols(K);',
        "ideal C=std(subst(K,u,0));",
        f"ring S={p},({names}),dp;",
        "ideal C=imap(R,C); C=std(C);",
        "ideal mC=minbase(C);",
        "intvec dg; int i; for(i=1;i<=ncols(mC);i++){ dg[i]=deg(mC[i]); }",
        f'"RESULT {tag} mingens_degrees", dg;',
        f'"RESULT {tag} linear_forms", size(jet(mC,1));',
        f'"RESULT {tag} hilb", hilb(C,1);',
        f'"RESULT {tag} dim", dim(C), "mult", mult(C);',
        "ideal Sg=std(C+minor(jacob(mC),nvars(S)-dim(C)));",
        f'"RESULT {tag} singular_locus dim", dim(Sg), "mult", mult(Sg);',
        "list mp=minAssChar(C);",
        f'"RESULT {tag} minimal_primes", size(mp);',
        "for(i=1;i<=size(mp);i++){ ideal q=std(mp[i]); "
        f'"RESULT {tag} prime", i, "dim", dim(q), "mult", mult(q), "linear", size(jet(minbase(q),1)); }}',
        "quit;",
    ]
    print("\n".join(lines))


if __name__ == "__main__":
    main()
