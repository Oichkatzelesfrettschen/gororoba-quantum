"""The quadric rings k[y]/K2 of the fiber track at the third prime p = 32057: Cohen-Macaulay test, reducedness, defect.

Ledger row A5-548 states the hypothesis that k[y]/K2 is Cohen-Macaulay exactly when K2 is radical, and that where it
is not, the defect is a nilradical module of rank one over a smaller cone. Its falsifier names a reduced ring that is
not Cohen-Macaulay, or a nonreduced ring that is. This program decides both properties on the relation files that
`fiber_cone_driver.py` writes from the headers of `inputs/p32057-r8059/` (`fiber_inputs.py emit --prime 32057
--root 8059`; 32057 is `fiber_inputs.find_split_prime(32030, 1)`, the first prime 1 mod 4 above 32029).

- Cohen-Macaulay: `k2_cm.test` unchanged (Artinian length against degree after a linear system of parameters).
- Nonreduced: the radical R of K2 has a nonzero linear part N with N^2 in K2; K2 is generated in degree 2, so a
  linear form of R is a nilpotent outside K2.
- Reduced, for a Cohen-Macaulay ring A = k[y]/K2 of dimension a and degree e: the forms l_1, ..., l_a of the
  Cohen-Macaulay test are a regular sequence, so A_1 = A/(l_1, ..., l_{a-1}) is Cohen-Macaulay of dimension 1 and
  every point of Proj A_1 lies in the chart l_a = 1. The chart ring k[y]/Z = A_1/(l_a - 1) is reduced of length e
  when multiplication by one of four fixed linear forms u on it has a squarefree characteristic polynomial of degree
  e (the e eigenvalues over the closure are distinct; e is below p). Then Proj A_1 is e reduced points, A_1 has no
  embedded prime (depth 1), so A_1 is reduced, and a graded ring A with a homogeneous nonzerodivisor x of positive
  degree and A/xA reduced is reduced (a homogeneous nilpotent of least degree would be x times a nilpotent of
  smaller degree). A chart with no squarefree characteristic polynomial decides nothing for a special choice of
  forms, and the row then reports no verdict.
- Defect structure: the `x-colon`, `e8-colon` and `vb-components` rows of `structure/quadric_and_germ_probes.py`
  on the new files, judged by that module's own `check` with its job lists replaced by these rows.

E8-bar -> N+ and X+ -> N+ are the images of E8-bar -> N- and X- -> N- under the sign automorphism of A5-013, whose
coordinate change y_i -> c_i y_i carries K2, its radical and its colon ideals; X+ -> N+ runs as a control of that
transport and E8-bar -> N+ is not run.

Usage, from the repository root: "$PYTHON" docs/evidence/a5-exceptional-fibers/third-prime/quadric_rings.py OUT.json;
with `--calibrate OUT.json` the same verdicts run on retained 32009 cells whose answers the ledger proves, and the
program exits 1 on any departure.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
A5 = HERE.parent
sys.path.insert(0, str(A5))
sys.path.insert(0, str(A5 / "structure"))
sys.path.insert(0, str(A5.parents[2] / "gororoba_quantum"))

import flint  # noqa: E402
import k2_cm  # noqa: E402
import quadric_and_germ_probes as qp  # noqa: E402

import parallel  # noqa: E402

PRIME = 32057
# Known answers at 32009 on retained relation files under working/: (fiber, generators, file, Cohen-Macaulay,
# reduced), from A5-010 and A5-019 (Cohen-Macaulay), A5-303 and A5-312 (nonreduced), A5-058, A5-061 and the
# linearly joined primes of E8-bar -> VB (reduced).
CALIBRATION = (
    ("X- -> N-", 15, "distribute/out/a5-xm-d4/xm_p1/d2/relations-upto-d2.rel", False, False),
    ("E8-bar -> VB", 10, "runs/e8vb_a2/k2.rel", True, True),
    ("Iso", 17, "distribute/out/a5-iso-d4/iso_p1/d2/relations-upto-d2.rel", True, True),
    ("E8-bar -> N-", 21, "distribute/out/a5-e8-d2/e8nm_p1/d2/relations-upto-d2.rel", False, False),
    ("W8 -> N-", 24, "runs/w8_a2/w8_k2.rel", True, True),
)
CALIBRATION_PRIME = 32009
# (fiber, number of G generators, slug of the header and relation directory)
CELLS = (
    ("X- -> N-", 15, "xm-nm"),
    ("X+ -> N+", 15, "xp-np"),
    ("E8-bar -> VB", 10, "e8-vb"),
    ("Iso", 17, "iso-nm"),
    ("E8-bar -> N-", 21, "e8-nm"),
    ("W8 -> N-", 24, "w8-nm"),
)

REDUCED_SING = """LIB "primdec.lib";
ring r={p},(y(1..{n})),dp;
execute("ideal K="+read("{rel}")+";");
ideal sK=std(K); int a=dim(sK); int e=mult(sK);
ideal Lf; int i; int j; int c; poly g;
for(i=1;i<=a;i++){{g=0; c=1;
  for(j=1;j<=nvars(r);j++){{c=(c*(i+2)) mod {p}; g=g+((c+17*j*i) mod {p})*var(j);}}
  Lf[i]=g;}}
ideal L1; for(i=1;i<a;i++){{ L1[i]=Lf[i]; }}
option(redSB); ideal Z=std(K+L1+ideal(Lf[a]-1));
"RESULT chart",dim(Z),vdim(Z),e;
ideal B=kbase(Z); int eb=size(B); poly pv=1; for(i=1;i<=nvars(r);i++){{ pv=pv*var(i); }}
int base; poly u; matrix M; string row;
for(base=7;base<=10;base++){{ u=0; c=1;
  for(j=1;j<=nvars(r);j++){{ c=(c*base) mod {p}; u=u+((c+31*j) mod {p})*var(j); }}
  M=coeffs(reduce(u*B,Z),B,pv);
  for(i=1;i<=eb;i++){{ row=""; for(j=1;j<=eb;j++){{ row=row+string(M[i,j])+","; }} "RESULT mrow",base,i,row; }} }}
{nil}
quit;
"""

NIL = """ideal R=std(radical(sK)); ideal N=simplify(jet(R,1),2);
"RESULT nilpotent",size(N),size(reduce(N*N,sK))==0,size(reduce(N,sK))==size(N);"""


def relations(slug: str) -> Path:
    return HERE / "relations" / slug / "d2" / "relations-upto-d2.rel"


def label(path: Path) -> str:
    return path.relative_to(A5).as_posix()


def reducedness(item: tuple[str, int, int, Path, bool]) -> dict[str, Any]:
    fiber, p, n, path, nilpotent = item
    source = REDUCED_SING.format(p=p, n=n, rel=path, nil=NIL if nilpotent else "")
    rec: dict[str, Any] = {"fiber": fiber}
    rows: dict[int, dict[int, list[int]]] = {}
    for f in qp.singular(source):
        if f[0] == "mrow":
            rows.setdefault(int(f[1]), {})[int(f[2])] = [int(x) % p for x in "".join(f[3:]).split(",") if x != ""]
        else:
            rec[f[0]] = [int(x) for x in f[1:]]
    rec["squarefree_charpoly_bases"] = [base for base, m in sorted(rows.items()) if squarefree_charpoly(m, p)]
    rec["bases_tried"] = sorted(rows)
    return rec


def squarefree_charpoly(rows: dict[int, list[int]], p: int) -> bool:
    """Whether the characteristic polynomial of the multiplication matrix is squarefree over F_p.

    A squarefree characteristic polynomial of degree e = dim A gives e distinct eigenvalues of multiplication by u
    over the algebraic closure, so A is a product of e copies of the closure and is reduced; its degree is below p,
    so a zero derivative cannot hide a repeated factor.
    """
    e = len(rows)
    matrix = flint.nmod_mat([rows[i] for i in range(1, e + 1)], p)
    charpoly = matrix.charpoly()
    return charpoly.degree() == e and charpoly.gcd(charpoly.derivative()).degree() == 0


def cm(item: tuple[str, int, int, Path]) -> dict[str, Any]:
    fiber, p, n, path = item
    rec = k2_cm.test((fiber, p, n, "../" + label(path)))
    rec["relations"] = label(path)
    return rec


def run(job: tuple[str, Any]) -> dict[str, Any]:
    kind, item = job
    if kind == "cm":
        return cm(item)
    if kind == "reduced":
        return reducedness(item)
    return qp.run((kind, item))


def verdict(cm_row: dict[str, Any], red: dict[str, Any]) -> dict[str, Any]:
    dim0, length, degree = red["chart"]
    chart_reduced = dim0 == 0 and length == degree and bool(red["squarefree_charpoly_bases"])
    out: dict[str, Any] = {"chart_reduced": chart_reduced}
    if "nilpotent" in red:
        count, square, outside = red["nilpotent"]
        out["nilpotent_linear_forms"] = count
        out["nilpotent_certificate"] = count > 0 and square == 1 and outside == 1
    if out.get("nilpotent_certificate"):
        out["reduced"] = False
    elif cm_row["cohen_macaulay"] and chart_reduced:
        out["reduced"] = True
    else:
        out["reduced"] = None
    out["hypothesis_holds"] = None if out["reduced"] is None else out["reduced"] == cm_row["cohen_macaulay"]
    return out


def calibrate(out: Path) -> int:
    """Run the Cohen-Macaulay and reducedness verdicts on retained 32009 cells with known answers."""
    work = A5 / "working"
    jobs: list[tuple[str, Any]] = [("cm", (f, CALIBRATION_PRIME, n, work / rel)) for f, n, rel, _, _ in CALIBRATION]
    jobs += [("reduced", (f, CALIBRATION_PRIME, n, work / rel, not red)) for f, n, rel, _, red in CALIBRATION]
    rows = parallel.ordered_map(run, jobs, min_items=1)
    k = len(CALIBRATION)
    cells, bad = [], []
    for (fiber, _, _, want_cm, want_red), cm_row, red in zip(CALIBRATION, rows[:k], rows[k:], strict=True):
        cell = {**cm_row, "reducedness": red, **verdict(cm_row, red)}
        cells.append(cell)
        if (cell["cohen_macaulay"], cell["reduced"]) != (want_cm, want_red):
            bad.append(f"{fiber}: Cohen-Macaulay {cell['cohen_macaulay']}, reduced {cell['reduced']}")
    out.write_text(json.dumps({"check": "a5-548-calibration", "prime": CALIBRATION_PRIME, "cells": cells,
                               "problems": bad}, indent=1) + "\n", encoding="utf-8")  # fmt: skip
    for line in bad:
        print("calibration:", line)
    return 1 if bad else 0


def main() -> int:
    if len(sys.argv) == 3 and sys.argv[1] == "--calibrate":
        return calibrate(Path(sys.argv[2]))
    if len(sys.argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    rel = {slug: "../" + label(relations(slug)) for _, _, slug in CELLS}
    qp.GERMS = []
    qp.VB = [(PRIME, rel["e8-vb"])]
    qp.XS = [("X- -> N-", PRIME, rel["xm-nm"]), ("X+ -> N+", PRIME, rel["xp-np"])]
    qp.E8S = [("E8-bar -> N-", PRIME, rel["e8-nm"])]
    nil = {"xm-nm", "xp-np", "e8-vb", "e8-nm"}
    jobs: list[tuple[str, Any]] = [("cm", (f, PRIME, n, relations(s))) for f, n, s in CELLS]
    jobs += [("reduced", (f, PRIME, n, relations(s), s in nil)) for f, n, s in CELLS]
    jobs += [("vb-components", v) for v in qp.VB] + [("x-colon", x) for x in qp.XS] + [("e8-colon", e) for e in qp.E8S]
    rows = parallel.ordered_map(run, jobs, min_items=1)
    cms, reds, probes = rows[: len(CELLS)], rows[len(CELLS) : 2 * len(CELLS)], rows[2 * len(CELLS) :]
    cells = []
    for cm_row, red in zip(cms, reds, strict=True):
        cells.append({**cm_row, "reducedness": red, **verdict(cm_row, red)})
    problems = qp.check(probes)
    record = {
        "check": "a5-548-third-prime",
        "prime": PRIME,
        "root_of_minus_one": 8059,
        "cells": cells,
        "defect_probes": probes,
        "defect_problems": problems,
        "hypothesis_holds_on_every_decided_cell": all(c["hypothesis_holds"] is not False for c in cells),
        "undecided_cells": [c["fiber"] for c in cells if c["hypothesis_holds"] is None],
    }
    Path(sys.argv[1]).write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    for c in cells:
        print(
            c["fiber"],
            c["krull_dim"],
            c["degree"],
            c["length"],
            c["cohen_macaulay"],
            c["reduced"],
            c["hypothesis_holds"],
        )
    for line in problems:
        print("defect:", line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
