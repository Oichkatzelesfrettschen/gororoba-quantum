"""Base locus of the kernel-coordinate ideal near the boundary point, and its residual after the B9 component.

For an incidence Y -> Z the Schur-coordinate ideal F (126 principal four-Pfaffians of the rank-four Schur form for a
nullity-8 source) cuts out the nullity >= 12 locus of the source germ k[t]/J in the coordinate slice transverse to Z.
Each check pulls back the B9 and VB closure equations of the regularity record through the slice map and reports:

- the minimal primes of J + F through the origin, their dimension, and whether the unique one equals the minimal prime
  of J + B9-pullback through the origin;
- the residual Q = (J + F) : P_B9, its minimal primes through the origin and their dimension, and whether the unique
  one equals the VB-pullback prime (nullity-16 targets) or is the origin alone (m-primary residual, nullity-12 VB
  targets);
- the germ dimension of J.

FIELD is p32009, p32029 (the split primes of the fiber inputs, roots of -1 10754 and 9115) or q (Q(i), minpoly
I^2 + 1); every ring uses the global ordering dp. Usage, from the repository root:

    "$PYTHON" docs/evidence/a5-exceptional-fibers/structure/base_locus.py FIELD INCIDENCE...

with INCIDENCE among X+->N-, X-->N+, B9->N-, B9->N+ (nullity-16 targets, producer nullity16_rees_fibers) and X+->VB,
X-->VB, W8->VB, Iso->VB (producer nakayama_rees_fibers). Scripts land in sing/, logs in logs/, one RESULT line per
quantity.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT / "docs" / "evidence" / "a5-kernel-attachments"))
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import fiber_inputs as fi  # noqa: E402

import parallel  # noqa: E402

FIELDS = {"p32009": (32009, 10754), "p32029": (32029, 9115), "q": (32009, 10754)}
VB_TARGETS = ("X+->VB", "X-->VB", "W8->VB", "Iso->VB")
TIMEOUT_SECONDS = 1200


def _nakayama_task(incidence: str) -> tuple[Any, Any]:
    nakayama, rees = fi.nakayama, fi.rees
    first = nakayama._load_json(nakayama.FIRST_ORDER_RESULT)
    ideals = nakayama.regularity.closure_ideals()
    row = next(r for r in first["incidences"] if r["incidence"] == incidence)
    source = str(row["source_orbit"])
    closure = tuple(str(v) for v in ideals[nakayama.SOURCE_KEYS.get(source, source)])
    nd = nakayama.resolved._schur_polynomials(nakayama.resolved.IncidenceTask(row))
    shim = {
        "incidence": incidence,
        "passage": "8->12",
        "source_orbit": source,
        "boundary_orbit": row["boundary_orbit"],
        "source_nullity": 8,
        "census_point_key": f"{row['boundary_orbit']}:canonical",
        "boundary_point": [str(v) for v in row["boundary_point"]],
        "expected_germ_dimension_multiplicity_embedding_components": [0, 0, 0, 0],
    }
    data = SimpleNamespace(
        slice_names=tuple(nd.slice_names),
        slice_columns=tuple(int(v) for v in row["slice_columns_zero_based"]),
        coordinates=tuple(nd.coordinates),
    )
    return rees.RowTask(shim, closure), data


def _task(incidence: str) -> tuple[Any, Any]:
    if incidence in VB_TARGETS:
        return _nakayama_task(incidence)
    task = fi._task(incidence)
    return task, fi.basepoints._schur_coordinates(fi.rees._base_task(task))


def script(field: str, incidence: str) -> str:
    prime, root = FIELDS[field]
    rees = fi.rees
    task, data = _task(incidence)
    ideals = rees.regularity.closure_ideals()
    residual_target = "origin" if incidence in VB_TARGETS else "VB"
    lines = [
        *rees._local_germ_lines(root, task, data, prime),
        f"ideal FullF={rees._coordinate_text(data)};",
        "setring r;",
        "ideal B9c=" + ",".join(str(p) for p in ideals["B9"]) + ";",
        "ideal VBc=" + ",".join(str(p) for p in ideals["VB"]) + ";",
        "setring s;",
        "proc thru(ideal X){ list L=minAssGTZ(X); list T; int c=0; for(int i=1;i<=size(L);i++){"
        " if(size(reduce(L[i],std(maxideal(1))))==0){c++; T[c]=std(L[i]);} } return(T); }",
        "proc same(ideal A, ideal B){ return(size(reduce(A,B))==0 && size(reduce(B,A))==0); }",
        "list PB=thru(std(J+FullF)); list P9=thru(std(J+sliceMap(B9c))); list PV=thru(std(J+sliceMap(VBc)));",
        '"RESULT germ_dim", dim(J);',
        '"RESULT base_primes", size(PB);',
        "int bd=-1; for(int i=1;i<=size(PB);i++){ if(dim(PB[i])>bd){bd=dim(PB[i]);} }",
        '"RESULT base_dim", bd;',
        "int eq9=(size(PB)==1 && size(P9)==1); if(eq9){ eq9=same(PB[1],P9[1]); }",
        '"RESULT base_equals_b9", eq9;',
        "if(eq9){",
        "  list PQ=thru(std(quotient(J+FullF,P9[1]))); int qd=-1;",
        "  for(int i=1;i<=size(PQ);i++){ if(dim(PQ[i])>qd){qd=dim(PQ[i]);} }",
        '  "RESULT residual_primes", size(PQ); "RESULT residual_dim", qd;',
        "  int eqv=(size(PQ)==1 && size(PV)==1); if(eqv){ eqv=same(PQ[1],PV[1]); }",
        '  "RESULT residual_equals_vb", eqv;',
        "}",
        "quit;",
    ]
    text = "\n".join(lines) + "\n"
    if field == "q":
        text = re.sub(
            rf"ring (\w+)={prime},\(([^)]*)\),dp;\nnumber I={root};",
            r"ring \1=(0,I),(\2),dp; minpoly=I^2+1;",
            text,
        )
        if str(prime) in text:
            raise RuntimeError(f"{incidence}: the Q(i) script still names the prime")
    return f"// residual target: {residual_target}\n" + text


def _stem(field: str, incidence: str) -> str:
    return incidence.replace(">", "").replace("+", "p").replace("-", "m") + "_" + field


def run_one(job: tuple[str, str]) -> tuple[str, dict[str, str]]:
    field, incidence = job
    stem = _stem(field, incidence)
    sing = HERE / "sing" / f"{stem}.sing"
    sing.write_text(script(field, incidence), encoding="utf-8")
    # Run inside sing/ with a relative name so Singular's messages carry no host path.
    out = subprocess.run(
        ["Singular", "-q", "--no-rc", sing.name],
        capture_output=True,
        text=True,
        timeout=TIMEOUT_SECONDS,
        check=False,
        cwd=sing.parent,
    )
    (HERE / "logs" / f"{stem}.log").write_text(out.stdout + out.stderr, encoding="utf-8")
    bad = [line for line in out.stdout.splitlines() if line.startswith("?")]
    if out.returncode != 0 or bad:
        raise RuntimeError(f"{stem}: Singular exit {out.returncode}; {bad[:3]}")
    results = {}
    for line in out.stdout.splitlines():
        if line.startswith("RESULT "):
            key, value = line[len("RESULT ") :].split(" ", 1)
            results[key] = value.strip()
    return stem, results


def main() -> int:
    field, incidences = sys.argv[1], sys.argv[2:]
    if field not in FIELDS or not incidences:
        raise SystemExit(__doc__)
    (HERE / "sing").mkdir(exist_ok=True)
    (HERE / "logs").mkdir(exist_ok=True)
    for stem, results in parallel.ordered_map(run_one, [(field, inc) for inc in incidences], min_items=2):
        print(stem, " ".join(f"{k}={v}" for k, v in results.items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
