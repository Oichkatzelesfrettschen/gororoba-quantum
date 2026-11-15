"""Exact probes of the germ ideals and of three quadric schemes of the fiber track.

Three kinds of row, each one Singular run in the global ordering dp on retained inputs:

- `germ-prime`: the germ ideal J and the generators G of a retained input, the p = 32009 text
  `working/runs/k2struct/<name>_J.sing` or the canonical p = 32029 header
  `working/distribute/out/<cell>/d2/d2-products.sing`. The row records whether J is radical, the number of its
  minimal primes, whether the first passes through the origin, whether the pivot generator lies in J and, at 32029,
  whether J equals the ideal of the 32009 text read modulo 32029. A prime J makes every element outside it a
  nonzerodivisor.
- `vb-components`: the two minimal primes of the quadric ideal K2 of E8-bar -> VB. Each prime is cut by three
  linear forms with the Vandermonde coefficients of k2_cm.py at four bases; a reduced section with an F_p-point puts a
  Frobenius-fixed point on exactly one geometric component, so a prime over F_p with such a section is absolutely
  prime. The row also records the scheme where the components meet and the Hilbert functions of K2, of the two
  primes and of the meet for d = 1..7.
- `x-colon`: the quadric ideal K2 of same-sign X with its minimal prime P and A = K2 : P. The row records the
  linear forms of A, whether K2 : A = P, and the first Hilbert numerators of K2, P and A; the identity
  N_K2 - N_P = N_A - (1 - t)^15 states dim (P / K2)_d = dim (k[y] / A)_d for every d >= 1.

No random source enters: the linear forms are fixed by their base. check() holds the retained values, and
tests/test_a5_quadric_and_germ_probes.py applies it to the record and to mutated copies.

Usage: quadric_and_germ_probes.py OUT.jsonl; run from any directory, Singular on PATH or in $SINGULAR.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
from math import comb
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
W = HERE.parent / "working"
P2 = 32029

P1 = 32009
ROOT_OF_MINUS_ONE = {P1: 10754, P2: 9115}
# (fiber, prime, input under working/, 32009 text to compare with or None, pivot index in the order of G or None)
GERMS: list[tuple[str, int, str, str | None, int | None]] = [
    ("X- -> N-", P1, "runs/k2struct/xm_J.sing", None, 11),
    ("E8-bar -> VB", P1, "runs/k2struct/e8vb_J.sing", None, 3),
    ("Iso -> N-", P1, "runs/k2struct/iso_J.sing", None, 16),
    ("W8 -> N-", P1, "runs/k2struct/w8nm_J.sing", None, None),
    ("E8-bar -> N+", P1, "runs/k2struct/e8np_J.sing", None, 19),
    ("X- -> N-", P2, "distribute/out/a5-p2-small/xm_p2/d2/d2-products.sing", "xm_J", 11),
    ("E8-bar -> VB", P2, "distribute/out/a5-p2-small/vb_p2/d2/d2-products.sing", "e8vb_J", 3),
    ("Iso -> N-", P2, "distribute/out/a5-p2-iso/iso_p2/d2/d2-products.sing", "iso_J", 16),
    ("W8 -> N-", P2, "distribute/out/a5-p2-w8/w8_p2/d2/d2-products.sing", "w8nm_J", None),
    ("E8-bar -> N+", P2, "distribute/out/a5-e8-d2/e8np_p2/d2/d2-products.sing", "e8np_J", 19),
    ("E8-bar -> N-", P2, "distribute/out/a5-e8-d2/e8nm_p2/d2/d2-products.sing", None, 19),
]
VB: list[tuple[int, str]] = [
    (32009, "runs/e8vb_a2/k2.rel"),
    (P2, "distribute/out/a5-p2-small/vb_p2/d2/relations-upto-d2.rel"),
]
XS: list[tuple[str, int, str]] = [
    ("X- -> N-", 32009, "distribute/out/a5-xm-d4/xm_p1/d2/relations-upto-d2.rel"),
    ("X- -> N-", P2, "distribute/out/a5-p2-small/xm_p2/d2/relations-upto-d2.rel"),
    ("X+ -> N+", P2, "distribute/out/a5-p2-small/xp_p2/d2/relations-upto-d2.rel"),
]
BASES = (2, 3, 4, 5)

GERM_SING = """LIB "primdec.lib";
ring r={p},({ring}),dp; number I={root};
ideal J={j};
ideal G={g};
ideal sJ=std(J);
{text}
"RESULT gens",size(J); "RESULT dim",dim(sJ); "RESULT radical",size(reduce(radical(J),sJ))==0;
list P=minAssChar(J); "RESULT minimal_primes",size(P);
"RESULT through_origin",size(reduce(P[1],std(maxideal(1))))==0;
"RESULT generators",size(G);
{pivot}
quit;
"""

VB_SING = """LIB "primdec.lib";
proc orbits(ideal P, int n, int off, int p)
{{ ideal sP=std(P); int a=dim(sP)-1; ideal Lf; int i; int j; int c; poly g;
  for(i=1;i<=a;i++){{g=0;c=1; for(j=1;j<=n;j++){{c=(c*(i+off)) mod p; g=g+((c+17*j*i) mod p)*var(j);}} Lf[i]=g;}}
  ideal Q=std(P+Lf); list M=minAssGTZ(Q); int s; string out="";
  for(s=1;s<=size(M);s++){{ out=out+" "+string(vdim(std(M[s]+ideal(var(n)-1)))); }}
  return(string(dim(Q)-1)+" "+string(mult(Q))+" "+string(size(reduce(radical(Q),Q))==0)+out); }}
ring r={p},(y(1..10)),dp;
execute("ideal K="+read("{rel}")+";");
ideal sK=std(K); list P=minAssChar(K); int s; int off;
"RESULT primes",size(P);
for(s=1;s<=size(P);s++){{ "RESULT component",s,dim(std(P[s]))-1,mult(std(P[s]));
  for(off=2;off<=5;off++){{ "RESULT section",s,off,orbits(P[s],10,off,{p}); }} }}
ideal C=std(P[1]+P[2]); ideal R=std(radical(C));
"RESULT meet",dim(C)-1,mult(C),size(reduce(R,C))==0,size(jet(R,1)),size(R);
int d; for(d=1;d<=7;d++){{ "RESULT hf",d,size(kbase(sK,d)),size(kbase(std(P[1]),d)),size(kbase(std(P[2]),d)),
  size(kbase(C,d)); }}
quit;
"""

X_SING = """LIB "primdec.lib";
ring r={p},(y(1..15)),dp;
execute("ideal K="+read("{rel}")+";");
ideal sK=std(K); list M=minAssChar(K); ideal R=std(M[1]);
"RESULT primes",size(M); "RESULT prime_ideal",dim(R),mult(R),size(reduce(K,R))==0;
ideal A=std(quotient(sK,R));
"RESULT colon",dim(A),mult(A),size(A),size(jet(A,1)),size(reduce(std(radical(A)),A))==0;
int i; for(i=1;i<=size(A);i++){{ "RESULT form",A[i]; }}
ideal B=std(quotient(sK,A)); "RESULT bicolon",size(reduce(B,R))==0 && size(reduce(R,B))==0;
"RESULT numK",hilb(sK,1); "RESULT numP",hilb(R,1); "RESULT numA",hilb(A,1);
quit;
"""


def singular(source: str) -> list[list[str]]:
    exe = os.environ.get("SINGULAR", "Singular")
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp, "probe.sing")
        src.write_text(source)
        res = subprocess.run(
            [exe, "-q", "--no-rc", str(src)], stdin=subprocess.DEVNULL, capture_output=True, text=True, check=True
        )
    if any(ln.lstrip().startswith("?") for ln in res.stdout.splitlines()):
        raise RuntimeError(f"Singular error: {res.stdout[-400:]}")
    return [ln.split()[1:] for ln in res.stdout.splitlines() if ln.startswith("RESULT ")]


def header_ideal(text: str, name: str) -> str:
    found = re.search(rf"ideal {name}=([^;]*);", text)
    if found is None:
        raise RuntimeError(f"no ideal {name} in the header")
    return found.group(1)


def germ(item: tuple[str, int, str, str | None, int | None]) -> dict[str, Any]:
    fiber, p, source_path, legacy, pivot = item
    text = (W / source_path).read_text()
    ring = re.search(rf"ring \w+={p},\(([^)]*)\)", text)
    if ring is None:
        raise RuntimeError(f"{source_path}: no ring over F_{p}")
    compare = ""
    if legacy is not None:
        old = header_ideal((W / "runs" / "k2struct" / f"{legacy}.sing").read_text(), "J")
        compare = (
            f'ideal J1={old}; ideal s1=std(J1); "RESULT equals_32009_text",'
            "size(reduce(J1,sJ))==0 && size(reduce(J,s1))==0;"
        )
    pivot_line = "" if pivot is None else f'"RESULT pivot_in_J",reduce(G[{pivot}],sJ)==0;'
    source = GERM_SING.format(
        p=p,
        ring=ring.group(1),
        root=ROOT_OF_MINUS_ONE[p],
        j=header_ideal(text, "J"),
        g=header_ideal(text, "G"),
        text=compare,
        pivot=pivot_line,
    )
    rec: dict[str, Any] = {"check": "germ-prime", "fiber": fiber, "prime": p, "input": source_path}
    rec.update({f[0]: int(f[1]) for f in singular(source)})
    rec["pivot"] = pivot
    return rec


def vb_components(item: tuple[int, str]) -> dict[str, Any]:
    p, rel = item
    rec: dict[str, Any] = {"check": "vb-components", "fiber": "E8-bar -> VB", "prime": p, "relations": rel}
    rec.update({"components": [], "hf": {}})
    for f in singular(VB_SING.format(p=p, rel=W / rel)):
        v = [int(x) for x in f[1:]]
        if f[0] == "primes":
            rec["primes"] = v[0]
        elif f[0] == "component":
            rec["components"].append({"projdim": v[1], "degree": v[2], "sections": {}})
        elif f[0] == "section":
            rec["components"][v[0] - 1]["sections"][str(v[1])] = {
                "projdim": v[2], "degree": v[3], "reduced": v[4] == 1, "orbits": sorted(v[5:])
            }  # fmt: skip
        elif f[0] == "meet":
            rec["meet"] = {"projdim": v[0], "degree": v[1], "reduced": v[2] == 1, "linear": v[3], "generators": v[4]}
        elif f[0] == "hf":
            rec["hf"][str(v[0])] = v[1:]
    return rec


def x_colon(item: tuple[str, int, str]) -> dict[str, Any]:
    fiber, p, rel = item
    rec: dict[str, Any] = {"check": "x-colon", "fiber": fiber, "prime": p, "relations": rel, "forms": []}
    for f in singular(X_SING.format(p=p, rel=W / rel)):
        if f[0] == "form":
            rec["forms"].append("".join(f[1:]))
        elif f[0] in ("numK", "numP", "numA"):
            rec[f[0]] = [int(x) for x in "".join(f[1:]).split(",")][:-1]
        else:
            rec[f[0]] = [int(x) for x in f[1:]]
    return rec


def run(job: tuple[str, Any]) -> dict[str, Any]:
    kind, item = job
    if kind == "germ-prime":
        return germ(item)
    if kind == "vb-components":
        return vb_components(item)
    return x_colon(item)


def numerator_identity(rec: dict[str, Any]) -> bool:
    """N_K2 - N_P = N_A - (1 - t)^15, coefficient by coefficient."""
    width = 16 + max(len(rec["numK"]), len(rec["numP"]), len(rec["numA"]))
    pad = {k: rec[k] + [0] * (width - len(rec[k])) for k in ("numK", "numP", "numA")}
    unit = [(-1) ** i * comb(15, i) if i <= 15 else 0 for i in range(width)]
    return all(pad["numK"][i] - pad["numP"][i] == pad["numA"][i] - unit[i] for i in range(width))


def check(rows: list[dict[str, Any]]) -> list[str]:
    """The departures of a record from the retained findings; an empty list for the retained record."""
    bad: list[str] = []
    kinds = [r["check"] for r in rows]
    if (kinds.count("germ-prime"), kinds.count("vb-components"), kinds.count("x-colon")) != (11, 2, 3):
        bad.append(f"row kinds {kinds}")
    for r in rows:
        tag = f"{r['check']} {r['fiber']} {r['prime']}"
        if r["check"] == "germ-prime":
            if (r["radical"], r["minimal_primes"], r["through_origin"]) != (1, 1, 1):
                bad.append(f"{tag}: J is not a prime through the origin")
            if r.get("equals_32009_text", 1) != 1:
                bad.append(f"{tag}: J differs from the 32009 text read modulo {P2}")
            if r["pivot"] is not None and r.get("pivot_in_J") != 0:
                bad.append(f"{tag}: the pivot lies in J or was not tested")
        elif r["check"] == "vb-components":
            if r["primes"] != 2 or [(c["projdim"], c["degree"]) for c in r["components"]] != [(3, 3), (3, 4)]:
                bad.append(f"{tag}: components")
            for c in r["components"]:
                sections = c["sections"].values()
                if any(s["projdim"] != 0 or s["degree"] != c["degree"] or sum(s["orbits"]) != c["degree"]
                       for s in sections):  # fmt: skip
                    bad.append(f"{tag}: a section of the degree-{c['degree']} component is not {c['degree']} points")
                if not any(s["reduced"] and 1 in s["orbits"] for s in sections):
                    bad.append(f"{tag}: no reduced section of the degree-{c['degree']} component has an F_p-point")
            if r["meet"] != {"projdim": 2, "degree": 1, "reduced": True, "linear": 7, "generators": 7}:
                bad.append(f"{tag}: the components do not meet in one reduced plane")
            for d in range(1, 8):
                k2, small, large, plane = r["hf"][str(d)]
                closed = (3 * comb(d + 2, 3) + comb(d + 2, 2), 4 * comb(d + 2, 3) + comb(d + 2, 2), comb(d + 2, 2))
                if (small, large, plane) != closed or k2 != small + large - plane:
                    bad.append(f"{tag}: Hilbert functions in degree {d}")
        elif r["check"] == "x-colon":
            if r["primes"] != [1] or r["prime_ideal"] != [4, 12, 1]:
                bad.append(f"{tag}: minimal prime")
            if r["colon"] != [3, 1, 12, 12, 1] or len(r["forms"]) != 12:
                bad.append(f"{tag}: K2 : P is not a plane ideal of 12 linear forms")
            if r["bicolon"] != [1]:
                bad.append(f"{tag}: K2 : (K2 : P) differs from P")
            if not numerator_identity(r):
                bad.append(f"{tag}: N_K2 - N_P differs from N_A - (1 - t)^15")
        else:
            bad.append(f"{tag}: unknown row kind")
    return bad


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    for parent in HERE.parents:
        if (parent / "gororoba_quantum" / "parallel.py").is_file():
            sys.path.insert(0, str(parent / "gororoba_quantum"))
            break
    import parallel

    jobs = [("germ-prime", g) for g in GERMS] + [("vb-components", v) for v in VB] + [("x-colon", x) for x in XS]
    rows = parallel.ordered_map(run, jobs, min_items=1)
    Path(sys.argv[1]).write_text("".join(json.dumps(r) + "\n" for r in rows))
    problems = check(rows)
    for line in problems:
        print(line)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
