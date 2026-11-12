"""Saturation, initial ideal and nilpotent coordinates of every retained quadric ideal K2.

For each retained relation file (the sources of ../k2_hilbert.py: five fibers, both primes, both headers where
retained) one Singular run in a dp ordering reports

- whether K2 : m = K2 for the irrelevant ideal m (K2 saturated, so its nilpotents live on V_+(K2));
- whether the initial ideal in_dp(K2) is squarefree. A squarefree initial ideal proves K2 radical; the initial
  ideal is a flat degeneration that keeps the Hilbert function, dimension and multiplicity of K2 and nothing about
  reducedness in the other direction;
- the coordinates y_i with y_i^2 or y_i^3 in K2, which are nilpotent on V_+(K2) when y_i is outside K2, and whether
  the square of the ideal N they generate lies in K2;
- the number of generators of in_dp(K2) by degree.

    $PYTHON docs/evidence/a5-exceptional-fibers/quadric-census/k2_scheme_census.py OUT.jsonl
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parents[3] / "gororoba_quantum"))

import k2_hilbert  # noqa: E402

import parallel  # noqa: E402

SCRIPT = """option(redSB);
ring Y={p},(y(1..{n})),dp;
execute("ideal K="+read("{rel}")+";");
ideal S=std(K);
"RESULT quadrics", size(K), "dim", dim(S), "mult", mult(S);
"RESULT saturated", size(simplify(reduce(std(quotient(S,maxideal(1))),S),2))==0;
ideal In=lead(S); int i; int sq=1; intvec e; int j;
for(i=1;i<=size(In);i++){{ e=leadexp(In[i]); for(j=1;j<=nvars(basering);j++){{ if(e[j]>1){{ sq=0; }} }} }}
"RESULT initial squarefree", sq, "generators", size(In), "max degree", deg(In[size(In)]);
ideal N; string nil="";
for(i=1;i<=nvars(basering);i++){{
  if(reduce(var(i)^2,S)==0 or reduce(var(i)^3,S)==0){{ N=N,var(i); nil=nil+string(i)+" "; }}
}}
N=simplify(N,2);
"RESULT nilpotent coordinates", size(N), ":", nil;
if(size(N)>0){{ "RESULT N squared in K2", size(simplify(reduce(N^2,S),2))==0; }}
quit;
"""


def census(source: tuple[str, int, int, str]) -> dict[str, Any]:
    fiber, prime, n, relations = source
    path = k2_hilbert.W / relations
    with tempfile.TemporaryDirectory() as tmp:
        script = Path(tmp, "k.sing")
        script.write_text(SCRIPT.format(p=prime, n=n, rel=path), encoding="utf-8")
        run = subprocess.run(  # noqa: S603
            [os.environ.get("SINGULAR", "Singular"), "-q", "--no-warn", str(script)],
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            check=True,
            timeout=1800,
        )
    if any(line.lstrip().startswith("? ") for line in run.stdout.splitlines()):
        raise RuntimeError(f"Singular error on {relations}: {run.stdout[-400:]}")
    row: dict[str, Any] = {"fiber": fiber, "prime": prime, "generators": n, "relations": relations}
    for line in run.stdout.splitlines():
        f = line.split()
        if f[:2] == ["RESULT", "quadrics"]:
            row.update({"quadrics": int(f[2]), "dim": int(f[4]), "mult": int(f[6])})
        elif f[:2] == ["RESULT", "saturated"]:
            row["saturated"] = f[2] == "1"
        elif f[:2] == ["RESULT", "initial"]:
            row.update(
                {"initial_squarefree": f[3] == "1", "initial_generators": int(f[5]), "initial_max_degree": int(f[8])}
            )
        elif f[:2] == ["RESULT", "nilpotent"]:
            row["nilpotent_coordinates"] = [int(v) for v in f[5:]]
        elif f[:2] == ["RESULT", "N"]:
            row["nilpotents_square_to_zero"] = f[5] == "1"
    row["relations_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    return row


def main() -> None:
    rows = parallel.ordered_map(census, list(k2_hilbert.SOURCES), min_items=2)
    Path(sys.argv[1]).write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    for r in rows:
        print(json.dumps({k: v for k, v in r.items() if k not in ("relations", "relations_sha256")}))


if __name__ == "__main__":
    main()
