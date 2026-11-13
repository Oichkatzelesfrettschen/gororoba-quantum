"""Two arc families of the W8 slice over Q(i), one into each component of the quadric locus.

The quadric ideal K of W8 over Q(i) is radical with two minimal primes of dimension 6: one of degree 20 containing 9
linear forms, so its variety lies in a 15-dimensional subspace, and one of degree 30 containing 4, whose variety
spans a 20-dimensional subspace (`../a5-kernel-attachments/weight-slice-fiber-relations-result.json`). The limits of
arcs lie in V(L) for the relation ideal L of the fiber cone, and L contains K. This producer substitutes two arc
families into the J and G of the Q(i) producer (`reduction_check._script`), with the arc parameters as ring
variables over Q(i), and reports for each: whether J vanishes on the arc, the order nu of G, the rank of [dF | F]
for the limit vector F at two rational parameter points, and the dimension of the linear span of the limits (the
rank of the coefficient vectors of the 24 entries of F).

- `linear`: the family of `../a5-exceptional-fibers/structure/arcs-iso-w8/cert-w8-P-p32009.sing`, whose
  coefficients carry the square root of -1; J vanishes identically.
- `series`: the power-series family of `arcs_qi.W8`; J vanishes through the truncation order.

A family of rank 6 has a 6-dimensional set of limits inside V(K), so its closure is one of the two components. Span
15 excludes the degree-30 component, whose variety spans 20 dimensions; span above 15 excludes the degree-20
component. With one family in each, L lies in both primes, hence in their intersection K, and L = K. The linear
family with the sign of its last coordinate reversed is the control: it leaves V(J).

Run from the repository root: "$PYTHON" docs/evidence/a5-char0-transfer/w8_component_arcs_qi.py [--check]
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import arcs_qi  # noqa: E402
import reduction_check as rc  # noqa: E402

import parallel  # noqa: E402

RECORD = HERE / "w8-component-arcs-qi.json"
SCHEMA = "gororoba.a5.w8-component-arcs-qi/1"
INPUTS = ("arcs_qi.py", "reduction_check.py")
LINEAR_PARAMETERS = ("C", "D", "T", "U", "V")
LINEAR = (
    "poly A=x; poly Cc=C*x; poly Dd=D*x; poly T7=T*x;"
    " poly num=(U*x)^2*(V*x)^2-2*(U*x)^2*(V*x)+2*(U*x)*(V*x)^2-4*(U*x)*(V*x)+Cc*Dd-T7^2; poly B=num/A;",
    {
        "t1": "U*x",
        "t2": "(A+B)/2",
        "t4": "(A-B)/(2*I)",
        "t5": "(Cc+Dd)/2",
        "t6": "(Cc-Dd)/(2*I)",
        "t7": "T7",
        "t9": "({sign})*V*x",
    },
)
# The coefficient vectors of the entries of F over the parameter monomials span the linear span of the limits.
SPAN = (
    "def S0=basering; int ng=ncols(Fl); list rl=ringlist(S0); int q;"
    ' for (q=1;q<=ng;q++) { rl[2]=rl[2]+list("z"+string(q)); }'
    ' rl[3]=list(list("dp",1:(nvars(S0)+ng)),list("C",0)); def SZ=ring(rl); setring SZ; ideal Fz=imap(S0,Fl);'
    " poly Hh=0; for (q=1;q<=ng;q++) { Hh=Hh+var(nvars(S0)+q)*Fz[q]; }"
    " poly pm=1; for (q=1;q<=nvars(S0);q++) { pm=pm*var(q); }"
    " matrix cf=coef(Hh,pm); ideal lin; for (q=1;q<=ncols(cf);q++) { lin[q]=cf[2,q]; }"
    ' "RESULT span",rank(jacob(lin)); setring S0;'
)
# (basepoint slug, family, sign of the last slice coordinate, control)
CASES: tuple[tuple[str, str, int, bool], ...] = (
    ("w8-nm", "linear", 1, False),
    ("w8-np", "linear", -1, False),
    ("w8-nm", "series", 1, False),
    ("w8-np", "series", -1, False),
    ("w8-nm", "linear", -1, True),
    ("w8-np", "linear", 1, True),
)
GENERATORS = 24
# family: (order of G, rank of [dF | F], span of the limits)
EXPECTED = {"linear": (2, 6, 15), "series": (4, 6, 20)}
# (dimension, degree, linear forms) of the minimal primes of K over Q(i) in the weight-slice record.
COMPONENTS = ((6, 20, 9), (6, 30, 4))


def _arc(slug: str, family: str, sign: int, variables: list[str]) -> tuple[tuple[str, ...], str]:
    if family == "series":
        if sign != arcs_qi.CASES[slug][2]:
            raise RuntimeError("the series family carries the sign of arcs_qi")
        return arcs_qi.CASES[slug][1], arcs_qi._arc(slug, variables, False)
    definition, images = LINEAR
    mapped = ",".join(images.get(variable, "0").format(sign=sign) for variable in variables)
    return LINEAR_PARAMETERS, f"{definition} map phi=R0,{mapped};"


def singular_script(slug: str, family: str, sign: int, variables: list[str]) -> str:
    names, arc = _arc(slug, family, sign, variables)
    order = arcs_qi.ORDER
    body = rc._script(slug, None, rc.rees.MODULAR_PRIME, extra=False).replace("\nquit;\n", "\n")
    points = [",".join(("0", *(str(value) for value in point[: len(names)]))) for point in arcs_qi.POINTS]
    return (
        body
        + "\n".join(
            (
                "def R0=basering;",
                'LIB "matrix.lib";',
                f"ring S=(0,I),(x,{','.join(names)}),dp;minpoly=I2+1;",
                "intvec sw=1" + ",0" * len(names) + ";",
                arcs_qi.SERIES,
                arc,
                f"ideal Js=jet(phi(ReducedJ),{order - 2},sw); ideal Gs=jet(phi(ReducedG),{order - 3},sw);",
                '"RESULT j_nonzero",size(simplify(Js,2));',
                '"RESULT j_identity",size(simplify(phi(ReducedJ),2))==0;' if family == "linear" else "",
                "int j; int k; int nu=-1;",
                "for (k=0;k<=9 and nu<0;k++) { for (j=1;j<=ncols(Gs);j++) { if (jet(Gs[j],k,sw)!=0) { nu=k; } } }",
                "ideal Fl; for (j=1;j<=ncols(Gs);j++) { Fl[j]=subst(jet(Gs[j],nu,sw)-jet(Gs[j],nu-1,sw),x,1); }",
                "matrix Mj=concat(jacob(Fl),transpose(matrix(Fl)));",
                f"map p1=S,{points[0]}; map p2=S,{points[1]};",
                '"RESULT nu",nu; "RESULT generators",ncols(Gs); "RESULT limit_nonzero",size(simplify(Fl,2));',
                '"RESULT rank_1",rank(p1(Mj)); "RESULT rank_2",rank(p2(Mj));',
                SPAN,
                "quit;",
            )
        )
        + "\n"
    )


def certify(case: tuple[str, str, int, bool]) -> dict[str, Any]:
    slug, family, sign, control = case
    probe = rc.rees._run_singular(
        rc._script(slug, None, rc.rees.MODULAR_PRIME, extra=False).replace("\nquit;\n", "\n")
        + '"RESULT vs",varstr(basering);\nquit;\n',
        "w8_component_arcs_vars",
        rc.TIMEOUT_SECONDS,
    )
    if probe.status != "completed":
        raise RuntimeError(f"{slug} variable probe: {probe.status} {probe.diagnostic}")
    variables = probe.results["vs"].split(",")
    outcome = rc.rees._run_singular(
        singular_script(slug, family, sign, variables), f"w8_component_arcs_{family}", 8 * rc.TIMEOUT_SECONDS
    )
    if outcome.status != "completed":
        raise RuntimeError(f"{slug} {family}: {outcome.status} {outcome.diagnostic}")
    results = outcome.results
    return {
        "slug": slug,
        "family": family,
        "control": control,
        "last_coordinate_sign": sign,
        "slice_variables": variables,
        "j_nonzero": int(results["j_nonzero"]),
        "j_is_identity": bool(int(results["j_identity"])) if family == "linear" else None,
        "order_of_G": int(results["nu"]),
        "generators": int(results["generators"]),
        "limit_nonzero": int(results["limit_nonzero"]),
        "ranks": [int(results["rank_1"]), int(results["rank_2"])],
        "span_of_limits": int(results["span"]),
        "wall_seconds": outcome.wall_nanoseconds // 10**9,
        "peak_rss_kib": outcome.peak_rss_kib,
    }


def problems(record: dict[str, Any]) -> list[str]:
    """Every way the record fails the claim; an empty list is a pass."""
    found: list[str] = []
    if record.get("schema") != SCHEMA:
        found.append("schema differs")
    rows = record.get("rows", [])
    keys = [(row["slug"], row["family"], row["last_coordinate_sign"], row["control"]) for row in rows]
    if keys != list(CASES):
        found.append("the rows are not the six cases in order")
        return found
    if tuple(tuple(component) for component in record.get("components", [])) != COMPONENTS:
        found.append("the component table differs")
    small, large = 24 - COMPONENTS[0][2], 24 - COMPONENTS[1][2]
    for row in rows:
        label = f"{row['slug']} {row['family']}{' control' if row['control'] else ''}"
        if row["control"]:
            if row["j_nonzero"] == 0 or row["j_is_identity"] is not False:
                found.append(f"{label}: the reversed sign stays on V(J)")
            continue
        order, rank, span = EXPECTED[row["family"]]
        if row["j_nonzero"] != 0:
            found.append(f"{label}: J does not vanish on the arc")
        if row["family"] == "linear" and row["j_is_identity"] is not True:
            found.append(f"{label}: J does not vanish identically")
        if row["generators"] != GENERATORS:
            found.append(f"{label}: generator count differs from {GENERATORS}")
        if row["order_of_G"] != order:
            found.append(f"{label}: order of G differs from {order}")
        if row["ranks"] != [rank, rank]:
            found.append(f"{label}: rank of the limit map differs from {rank}")
        if row["span_of_limits"] != span:
            found.append(f"{label}: span of the limits differs from {span}")
        if row["family"] == "linear" and not row["span_of_limits"] <= small < large:
            found.append(f"{label}: the span does not exclude the degree-{COMPONENTS[1][1]} component")
        if row["family"] == "series" and not small < row["span_of_limits"] <= large:
            found.append(f"{label}: the span does not exclude the degree-{COMPONENTS[0][1]} component")
    if record.get("pass") is not (found == []):
        found.append("the pass flag differs from the verdict")
    return found


def build() -> dict[str, Any]:
    rows = parallel.ordered_map(certify, list(CASES), min_items=2)
    record: dict[str, Any] = {
        "schema": SCHEMA,
        "field": "Q(i)",
        "order": arcs_qi.ORDER,
        "points": [list(point) for point in arcs_qi.POINTS],
        "components": [list(component) for component in COMPONENTS],
        "inputs": {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest() for name in INPUTS},
        "rows": rows,
        "pass": True,
    }
    record["pass"] = problems(record) == []
    return record


def main() -> None:
    if "--check" in sys.argv[1:]:
        record = json.loads(RECORD.read_text(encoding="utf-8"))
        found = problems(record)
        for name in INPUTS:
            if record["inputs"].get(name) != hashlib.sha256((HERE / name).read_bytes()).hexdigest():
                found.append(f"input digest of {name} differs")
        if found:
            raise SystemExit("\n".join(found))
        print("w8-component-arcs-qi.json: pass")
        return
    record = build()
    RECORD.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"pass": record["pass"], "problems": problems(record)}, indent=1))
    if not record["pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
