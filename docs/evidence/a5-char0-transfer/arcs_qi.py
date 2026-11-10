"""The arc families of the Iso, W8 and same-sign X slices over Q(i): order of G and rank of the limit map.

The modular arc certificates (`../a5-exceptional-fibers/structure/arcs-iso-w8/blowup-arcs`,
`../a5-exceptional-fibers/arcs-x-same`) substitute an arc with rational coefficients into the header's J and G. Here
the same arcs are substituted into the J and G of the Q(i) producer (`reduction_check._script`, the producer whose
good reduction A5-247 checks), with the arc parameters as ring variables over Q(i). Each case reports whether J
vanishes on the arc (identically, or through the truncation order for the W8 power series), the order nu of G with
every lower coefficient identically zero, the number of nonzero entries of the limit vector F, and the rank of
[dF | F] at the two parameter points of the modular certificates. A rank r over Q(i) shows that the cone of arc
limits, hence the fiber cone F(I), has dimension at least r in characteristic 0; with K2 in L over Q(i) (known for
X- -> N-, A5-248) it has dimension exactly r where dim V(K2) = r. The mutated arc leaves V(J) and is the control for
the J test. The series variable is x, since the producer script names a ring s. Writes arcs-qi.json beside this
file.

Run from the repository root: "$PYTHON" docs/evidence/a5-char0-transfer/arcs_qi.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import reduction_check as rc  # noqa: E402

import parallel  # noqa: E402

ORDER = 12
POINTS = ((2, 3, 5, 7, 11), (13, 4, 9, 6, 17))
SERIES = (
    "proc inv(poly f, int n) { poly c=jet(f,0,sw); poly g=1/c; poly q=1-f*g; poly acc=1; poly pw=1; int i;"
    " for (i=1;i<=n;i++) { pw=jet(pw*q,n,sw); acc=acc+pw; } return(jet(acc*g,n,sw)); }"
)
ISO = (
    "poly aQ=2*b; poly aT=2*c; poly U2=b*V*x; poly aR=b^2*V*x+b*A*x^2; poly aP=(aR*aT-({square}))/(2*b);",
    {"t2": "x*U2", "t3": "x", "t4": "x*(aQ+aP)/2", "t5": "x*(aT+aR)/2", "t6": "x*(aQ-aP)/2", "t7": "x*(aT-aR)/2"},
)
W8 = (
    "poly aQ=2*b; poly aT=2*c; poly U2=V*x; poly aR=b*V*x+A*x^2; poly aP=c*V*x+B*x^2;"
    " poly aN=-({square})-aP*aQ+aR*aT; poly U9=0; int it;"
    " for (it=1;it<=NN;it++) {{ U9=jet((aN-2*x*U9+2*x*U9^2+x^2*U9^2)/4,NN,sw); }}",
    {
        "t1": "x",
        "t2": "x*U2",
        "t4": "x*(aQ+aP)/2",
        "t5": "x*(aT+aR)/2",
        "t6": "x*(aQ-aP)/2",
        "t7": "x*(aT-aR)/2",
        "t9": "({sign})*x*U9",
    },
)
XS = (
    "poly w=W*x^2; poly rho=Rh*x; poly sig=Sg*x; poly a=A*x; poly m=1+w; poly u=inv(m,NN);"
    " poly T9=jet(-(w^2)*u/2,NN,sw); poly T1=a-T9; poly T2=jet(a*w*(w+2)*u*({factor})/2,NN,sw);",
    {
        "t1": "T1",
        "t2": "T2",
        "t4": "(m*rho+sig)/2",
        "t5": "(m*rho-sig)/2",
        "t6": "(m*sig+rho)/2",
        "t7": "(rho-m*sig)/2",
        "t9": "({sign})*T9",
    },
)
# slug: (arc definition, images, parameter names, sign of t9, whether J(arc) = 0 is an identity)
CASES: dict[str, tuple[tuple[str, dict[str, str]], tuple[str, ...], int, bool]] = {
    "iso-nm": (ISO, ("b", "c", "V", "A"), 1, True),
    "iso-np": (ISO, ("b", "c", "V", "A"), 1, True),
    "w8-nm": (W8, ("b", "c", "V", "A", "B"), 1, False),
    "w8-np": (W8, ("b", "c", "V", "A", "B"), -1, False),
    "xm-nm": (XS, ("W", "Rh", "Sg", "A"), 1, False),
    "xp-np": (XS, ("W", "Rh", "Sg", "A"), -1, False),
}


def _arc(slug: str, variables: list[str], mutate: bool) -> str:
    (definition, images), names, sign, _ = CASES[slug]
    square = "0" if mutate else "U2^2"
    factor = "2" if mutate else "1"
    text = definition.format(square=square, factor=factor).replace("NN", str(ORDER))
    mapped = ",".join(images.get(v, "0").format(sign=sign) for v in variables)
    return f"{text} map phi=R0,{mapped};"


def _singular(slug: str, variables: list[str], mutate: bool) -> str:
    names = CASES[slug][1]
    body = rc._script(slug, None, rc.rees.MODULAR_PRIME, extra=False).replace("\nquit;\n", "\n")
    points = [",".join(("0", *(str(v) for v in point[: len(names)]))) for point in POINTS]
    return (
        body
        + "\n".join(
            (
                "def R0=basering;",
                'LIB "matrix.lib";',
                f"ring S=(0,I),(x,{','.join(names)}),dp;minpoly=I2+1;",
                "intvec sw=1" + ",0" * len(names) + ";",
                SERIES,
                _arc(slug, variables, mutate),
                f"ideal Js=jet(phi(ReducedJ),{ORDER - 2},sw); ideal Gs=jet(phi(ReducedG),{ORDER - 3},sw);",
                '"RESULT j_nonzero",size(simplify(Js,2));',
                "int j; int k; int nu=-1;",
                "for (k=0;k<=9 and nu<0;k++) { for (j=1;j<=ncols(Gs);j++) { if (jet(Gs[j],k,sw)!=0) { nu=k; } } }",
                "ideal Fl; for (j=1;j<=ncols(Gs);j++) { Fl[j]=subst(jet(Gs[j],nu,sw)-jet(Gs[j],nu-1,sw),x,1); }",
                "matrix Mj=concat(jacob(Fl),transpose(matrix(Fl)));",
                f"map p1=S,{points[0]}; map p2=S,{points[1]};",
                '"RESULT nu",nu; "RESULT generators",ncols(Gs); "RESULT limit_nonzero",size(simplify(Fl,2));',
                '"RESULT rank_1",rank(p1(Mj)); "RESULT rank_2",rank(p2(Mj));',
                "quit;",
            )
        )
        + "\n"
    )


def certify(slug: str) -> dict[str, Any]:
    probe = rc.rees._run_singular(
        rc._script(slug, None, rc.rees.MODULAR_PRIME, extra=False).replace("\nquit;\n", "\n")
        + '"RESULT vs",varstr(basering);\nquit;\n',
        "arcs_qi_vars",
        rc.TIMEOUT_SECONDS,
    )
    if probe.status != "completed":
        raise SystemExit(f"{slug} variable probe: {probe.status} {probe.diagnostic}")
    variables = probe.results["vs"].split(",")
    row: dict[str, Any] = {"slug": slug, "parameters": list(CASES[slug][1]), "j_is_identity": CASES[slug][3]}
    for label, mutate in (("arc", False), ("mutated", True)):
        outcome = rc.rees._run_singular(_singular(slug, variables, mutate), f"arcs_qi_{label}", 8 * rc.TIMEOUT_SECONDS)
        if outcome.status != "completed":
            raise SystemExit(f"{slug} {label}: {outcome.status} {outcome.diagnostic}")
        res = outcome.results
        row[label] = {
            "j_nonzero": int(res["j_nonzero"]),
            "order_of_G": int(res["nu"]),
            "generators": int(res["generators"]),
            "limit_nonzero": int(res["limit_nonzero"]),
            "ranks": [int(res["rank_1"]), int(res["rank_2"])],
            "wall_seconds": round(outcome.wall_nanoseconds / 1e9, 1),
            "peak_rss_kib": outcome.peak_rss_kib,
        }
    return row


EXPECTED = {"iso-nm": (4, 5), "iso-np": (4, 5), "w8-nm": (4, 6), "w8-np": (4, 6), "xm-nm": (5, 4), "xp-np": (5, 4)}


def main() -> None:
    rows = parallel.ordered_map(certify, list(CASES), min_items=2)
    holds = all(
        r["arc"]["j_nonzero"] == 0
        and r["mutated"]["j_nonzero"] > 0
        and (r["arc"]["order_of_G"], min(r["arc"]["ranks"])) == EXPECTED[r["slug"]]
        for r in rows
    )
    result = {
        "field": "Q(i)",
        "order": ORDER,
        "points": [list(p) for p in POINTS],
        "rows": rows,
        "verdict": "survives" if holds else "refuted",
    }
    (HERE / "arcs-qi.json").write_text(json.dumps(result, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=1))


if __name__ == "__main__":
    main()
