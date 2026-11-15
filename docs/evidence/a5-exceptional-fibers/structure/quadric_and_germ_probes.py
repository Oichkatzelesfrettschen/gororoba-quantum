"""Exact probes of the germ ideals and of three quadric schemes of the fiber track.

Three kinds of row, each one Singular run in the global ordering dp on retained inputs:

- `germ-prime`: the germ ideal J and the generators G of a retained input, a p = 32009 text
  (`working/runs/k2struct/<name>_J.sing`, `working/build/inputs/p32009-r10754/e8-nm.sing`) or the canonical p = 32029
  header `working/distribute/out/<cell>/d2/d2-products.sing`. The row records whether J is radical, the number of its
  minimal primes, whether the first passes through the origin, whether the pivot generator lies in J and, at 32029,
  whether J equals the ideal of the 32009 text read modulo 32029. A prime J makes every element outside it a
  nonzerodivisor.
- `vb-components`: the two minimal primes of the quadric ideal K2 of E8-bar -> VB. Each prime is cut by three
  linear forms with the Vandermonde coefficients of k2_cm.py at four bases; a reduced section with an F_p-point puts a
  Frobenius-fixed point on exactly one geometric component, so a prime over F_p with such a section is absolutely
  prime. The row also records the scheme where the components meet and the Hilbert functions of K2, of the two
  primes and of the meet for d = 1..7.
- `x-colon`: the quadric ideal K2 of same-sign X with its minimal prime P and A = K2 : P. The row records the
  sections of P by three linear forms (absolute primality as for `vb-components`), the linear forms of A, whether
  K2 : A = P, and the first Hilbert numerators of K2, P and A; the identity N_K2 - N_P = N_A - (1 - t)^15 states
  dim (P / K2)_d = dim (k[y] / A)_d for every d >= 1.

No random source enters: the linear forms are fixed by their base. check() compares every field of a record with the
expected value, row by row in the order of the job list, so a missing, relabeled or altered row is reported, and
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
# fiber: (32009 input, 32029 input, pivot index in the order of G or None, generators of J, dim J, generators G)
GERM_TABLE: dict[str, tuple[str, str, int | None, int, int, int]] = {
    "X- -> N-": ("runs/k2struct/xm_J.sing", "distribute/out/a5-p2-small/xm_p2/d2/d2-products.sing", 11, 12, 4, 15),
    "E8-bar -> VB": ("runs/k2struct/e8vb_J.sing", "distribute/out/a5-p2-small/vb_p2/d2/d2-products.sing", 3, 17, 4, 10),
    "Iso -> N-": ("runs/k2struct/iso_J.sing", "distribute/out/a5-p2-iso/iso_p2/d2/d2-products.sing", 16, 1, 5, 17),
    "W8 -> N-": ("runs/k2struct/w8nm_J.sing", "distribute/out/a5-p2-w8/w8_p2/d2/d2-products.sing", None, 1, 6, 24),
    "E8-bar -> N+": ("runs/k2struct/e8np_J.sing", "distribute/out/a5-e8-d2/e8np_p2/d2/d2-products.sing", 19, 16, 5, 21),
    "E8-bar -> N-": (
        "build/inputs/p32009-r10754/e8-nm.sing",
        "distribute/out/a5-e8-d2/e8nm_p2/d2/d2-products.sing",
        19,
        16,
        5,
        21,
    ),
}
# (fiber, prime, input under working/, 32009 input to compare with or None, pivot index or None)
GERMS: list[tuple[str, int, str, str | None, int | None]] = [
    *((fiber, P1, row[0], None, row[2]) for fiber, row in GERM_TABLE.items()),
    *((fiber, P2, row[1], row[0], row[2]) for fiber, row in GERM_TABLE.items()),
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
proc orbits(ideal P, int n, int off, int p)
{{ ideal sP=std(P); int a=dim(sP)-1; ideal Lf; int i; int j; int c; poly g;
  for(i=1;i<=a;i++){{g=0;c=1; for(j=1;j<=n;j++){{c=(c*(i+off)) mod p; g=g+((c+17*j*i) mod p)*var(j);}} Lf[i]=g;}}
  ideal Q=std(P+Lf); list M=minAssGTZ(Q); int s; string out="";
  for(s=1;s<=size(M);s++){{ out=out+" "+string(vdim(std(M[s]+ideal(var(n)-1)))); }}
  return(string(dim(Q)-1)+" "+string(mult(Q))+" "+string(size(reduce(radical(Q),Q))==0)+out); }}
ring r={p},(y(1..15)),dp;
execute("ideal K="+read("{rel}")+";");
ideal sK=std(K); list M=minAssChar(K); ideal R=std(M[1]);
"RESULT primes",size(M); "RESULT prime_ideal",dim(R),mult(R),size(reduce(K,R))==0;
int off; for(off=2;off<=5;off++){{ "RESULT section",off,orbits(M[1],15,off,{p}); }}
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
        old = header_ideal((W / legacy).read_text(), "J")
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
    rec["sections"] = {}
    for f in singular(X_SING.format(p=p, rel=W / rel)):
        if f[0] == "section":
            v = [int(x) for x in f[1:]]
            rec["sections"][str(v[0])] = {
                "projdim": v[1],
                "degree": v[2],
                "reduced": v[3] == 1,
                "orbits": sorted(v[4:]),
            }
        elif f[0] == "form":
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


# The 12 linear forms of K2 : P in the order Singular returns them; SIGN is - for X- -> N- and + for X+ -> N+.
PLANE_FORMS = (
    "y(14)",
    "y(13)",
    "y(12)",
    "y(11)",
    "y(9)",
    "y(8)",
    "y(7)",
    "y(6)",
    "y(5)",
    "y(3)SIGNy(10)",
    "y(2)SIGNy(15)",
    "y(1)",
)
NUM_K = [1, 0, -69, 477, -1695, 3894, -6325, 7623, -7029, 5060, -2871, 1275, -429, 102, -15, 1]
NUM_P = [1, -3, -30, 242, -825, 1683, -2244, 1980, -1089, 275, 66, -78, 25, -3]
NUM_A = [(-1) ** i * comb(12, i) for i in range(13)]
MEET = {"projdim": 2, "degree": 1, "reduced": True, "linear": 7, "generators": 7}


def section_problems(sections: Any, degree: int) -> list[str]:
    """Departures of the four sections of one prime from: zero-dimensional, of the degree, with an F_p-point."""
    if not isinstance(sections, dict) or sorted(sections) != [str(b) for b in BASES]:
        return ["the sections are not those of the four bases"]
    bad: list[str] = []
    for base, s in sections.items():
        orbits = s.get("orbits")
        sound = isinstance(orbits, list) and all(isinstance(o, int) and o >= 1 for o in orbits)
        if not sound or (s.get("projdim"), s.get("degree"), sum(orbits)) != (0, degree, degree):
            bad.append(f"the section at base {base} is not {degree} points")
    if not bad and not any(s["reduced"] is True and 1 in s["orbits"] for s in sections.values()):
        bad.append("no reduced section has an F_p-point")
    return bad


def expected_germ(item: tuple[str, int, str, str | None, int | None]) -> dict[str, Any]:
    fiber, p, source_path, legacy, pivot = item
    gens, dim, generators = GERM_TABLE[fiber][3:]
    rec: dict[str, Any] = {"check": "germ-prime", "fiber": fiber, "prime": p, "input": source_path}
    if legacy is not None:
        rec["equals_32009_text"] = 1
    rec.update({"gens": gens, "dim": dim, "radical": 1, "minimal_primes": 1, "through_origin": 1})
    rec["generators"] = generators
    if pivot is not None:
        rec["pivot_in_J"] = 0
    rec["pivot"] = pivot
    return rec


def check(rows: list[dict[str, Any]]) -> list[str]:
    """The departures of a record from the retained findings; an empty list for the retained record.

    Rows are compared in the order of the job list. A germ row equals its expected row field for field; a component
    or colon row carries its identity, its fixed values and the section condition.
    """
    if len(rows) != len(GERMS) + len(VB) + len(XS):
        return [f"{len(rows)} rows, expected {len(GERMS) + len(VB) + len(XS)}"]
    bad: list[str] = []
    for r, item in zip(rows, GERMS, strict=False):
        if r != expected_germ(item):
            bad.append(f"germ-prime {item[0]} {item[1]}: the row differs from a prime J with the pivot outside it")
    for r, (p, rel) in zip(rows[len(GERMS) :], VB, strict=False):
        tag = f"vb-components {p}"
        identity = {"check": "vb-components", "fiber": "E8-bar -> VB", "prime": p, "relations": rel, "primes": 2}
        if {k: r.get(k) for k in identity} != identity or set(r) != {*identity, "components", "hf", "meet"}:
            bad.append(f"{tag}: identity or fields")
            continue
        components = r["components"]
        if [(c.get("projdim"), c.get("degree")) for c in components] != [(3, 3), (3, 4)]:
            bad.append(f"{tag}: components")
            continue
        for c in components:
            bad += [
                f"{tag}: degree-{c['degree']} component: {x}" for x in section_problems(c.get("sections"), c["degree"])
            ]
        if r["meet"] != MEET:
            bad.append(f"{tag}: the components do not meet in one reduced plane")
        closed = {
            str(d): [7 * comb(d + 2, 3) + comb(d + 2, 2), 3 * comb(d + 2, 3) + comb(d + 2, 2),
                     4 * comb(d + 2, 3) + comb(d + 2, 2), comb(d + 2, 2)]
            for d in range(1, 8)
        }  # fmt: skip
        if r["hf"] != closed:
            bad.append(f"{tag}: Hilbert functions")
    for r, (fiber, p, rel) in zip(rows[len(GERMS) + len(VB) :], XS, strict=False):
        tag = f"x-colon {fiber} {p}"
        sign = "-" if fiber == "X- -> N-" else "+"
        fixed = {
            "check": "x-colon", "fiber": fiber, "prime": p, "relations": rel, "primes": [1], "prime_ideal": [4, 12, 1],
            "colon": [3, 1, 12, 12, 1], "forms": [f.replace("SIGN", sign) for f in PLANE_FORMS], "bicolon": [1],
            "numK": NUM_K, "numP": NUM_P, "numA": NUM_A,
        }  # fmt: skip
        if {k: r.get(k) for k in fixed} != fixed or set(r) != {*fixed, "sections"}:
            bad.append(f"{tag}: the row differs from one minimal prime P with K2 : P the plane and K2 : (K2 : P) = P")
            continue
        if not numerator_identity(r):
            bad.append(f"{tag}: N_K2 - N_P differs from N_A - (1 - t)^15")
        bad += [f"{tag}: minimal prime: {x}" for x in section_problems(r["sections"], 12)]
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
