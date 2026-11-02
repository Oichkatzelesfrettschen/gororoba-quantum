"""Cohen-Macaulay test of the quadric rings k[y]/K2 by a general linear system of parameters.

For a standard graded quotient A = k[y]/K2 of Krull dimension a and degree e, a general set of a linear forms is a
system of parameters, and A is Cohen-Macaulay exactly when it is regular, that is when the Artinian quotient has
length e; any choice with length above e proves A not Cohen-Macaulay, since every system of parameters of a
Cohen-Macaulay ring is regular. The forms use Vandermonde coefficients ((i + 2)^j + 17 i j) mod p, independent by
construction and drawn from no random source. Each row records a, e, the length, the h-vector of the Artinian quotient
and the sha256 of the relation file; for E8-bar -> VB it also records the minimal primes, their linear spans and
whether the components meet exactly where their spans meet (a linearly joined union in the sense of Eisenbud, Green,
Hulek and Popescu, arXiv math/0404517, Theorem 0.4).

Usage: k2_cm.py OUT.jsonl; run from this directory, Singular on PATH or in $SINGULAR.
"""

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from k2_hilbert import SOURCES, W  # noqa: E402

SCRIPT = """LIB "primdec.lib";
ring r={p},(y(1..{n})),dp;
execute("ideal K="+read("{rel}")+";");
ideal sK=std(K); int a=dim(sK); int e=mult(sK);
ideal Lf; int i; int j; int c; poly g;
for(i=1;i<=a;i++){{g=0; c=1;
  for(j=1;j<=nvars(r);j++){{c=(c*(i+2)) mod {p}; g=g+((c+17*j*i) mod {p})*var(j);}}
  Lf[i]=g;}}
ideal Q=std(K+Lf);
"RESULT cm",a,e,dim(Q),vdim(Q);
bigintvec hv=hilb(Q,2); int t; for(t=1;t<=size(hv);t++){{ "RESULT h",hv[t]; }}
{join}
quit;
"""

JOIN = """list P=minAssChar(K); int s;
for(s=1;s<=size(P);s++){{ ideal Ps=std(P[s]); ideal Ls=std(jet(Ps,1));
  "RESULT component",dim(Ps)-1,mult(Ps),{n}-1-size(Ls); kill Ps; kill Ls; }}
if(size(P)==2){{ ideal S1=std(jet(std(P[1]),1)); ideal S2=std(jet(std(P[2]),1));
  ideal Sint=std(S1+S2); ideal Cint=radical(std(P[1]+P[2]));
  "RESULT join",dim(Sint)-1,dim(std(Cint))-1,
    size(reduce(Sint,std(Cint)))==0 && size(reduce(Cint,Sint))==0,
    size(reduce(intersect(P[1],P[2]),sK))==0; }}"""


def test(item: tuple[str, int, int, str]) -> dict:
    fiber, p, n, rel = item
    path = W / rel
    join = JOIN.format(n=n) if fiber == "E8-bar -> VB" else ""
    singular = os.environ.get("SINGULAR", "Singular")
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp, "k.sing")
        src.write_text(SCRIPT.format(p=p, n=n, rel=path, join=join))
        res = subprocess.run(
            [singular, "-q", "--no-rc", str(src)], stdin=subprocess.DEVNULL, capture_output=True, text=True, check=True
        )
    if any(ln.lstrip().startswith("?") for ln in res.stdout.splitlines()):
        raise RuntimeError(f"Singular error on {rel}: {res.stdout[-400:]}")
    rec: dict = {"check": "k2-cohen-macaulay", "fiber": fiber, "prime": p, "relations": rel, "h_vector": []}
    for ln in res.stdout.splitlines():
        f = ln.split()
        if f[:2] == ["RESULT", "cm"]:
            a, e, d0, length = (int(x) for x in f[2:6])
            if d0 != 0:
                raise RuntimeError(f"{rel}: the linear forms are not a system of parameters (dim {d0})")
            rec.update({"krull_dim": a, "degree": e, "length": length, "cohen_macaulay": length == e})
        elif f[:2] == ["RESULT", "h"]:
            rec["h_vector"].append(int(f[2]))
        elif f[:2] == ["RESULT", "component"]:
            rec.setdefault("components", []).append({"projdim": int(f[2]), "degree": int(f[3]), "span": int(f[4])})
        elif f[:2] == ["RESULT", "join"]:
            rec["join"] = {"spans_meet_projdim": int(f[2]), "components_meet_projdim": int(f[3]),
                           "meet_equals_span_meet": f[4] == "1", "K2_is_intersection": f[5] == "1"}  # fmt: skip
    if "length" not in rec or not rec["h_vector"]:
        raise RuntimeError(f"{rel}: incomplete Singular output")
    if fiber == "E8-bar -> VB" and "join" not in rec:
        raise RuntimeError(f"{rel}: the linear-join record is missing")
    while len(rec["h_vector"]) > 1 and rec["h_vector"][-1] == 0:
        rec["h_vector"].pop()
    if sum(rec["h_vector"]) != rec["length"]:
        raise RuntimeError(f"{rel}: the h-vector sums to {sum(rec['h_vector'])}, not the length {rec['length']}")
    rec["relations_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    return rec


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    for parent in HERE.parents:
        if (parent / "gororoba_quantum" / "parallel.py").is_file():
            sys.path.insert(0, str(parent / "gororoba_quantum"))
            break
    import parallel

    rows = parallel.ordered_map(test, list(SOURCES), min_items=1)
    Path(sys.argv[1]).write_text("".join(json.dumps(r) + "\n" for r in rows))
    for r in rows:
        print(r["fiber"], r["prime"], r["krull_dim"], r["degree"], r["length"], r["cohen_macaulay"], r.get("join", ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
