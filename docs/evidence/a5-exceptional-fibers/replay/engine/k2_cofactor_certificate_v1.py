"""K2 cofactor certificate (schema a5-k2-cofactor-certificate-v1) for one fiber cone header.

The fiber cone of the ideal I = (G_1..G_n) over the germ ring F_p[t]/(J) is F_p[y]/L, y_a -> G_a. K2 is the ideal of
the quadrics q(y) with q(G) in J + m P_2, where m = (t_1..t_s) and P_2 is spanned by the products G_a G_b. For each
quadric q the producer writes cofactors with

    u * q(G) = sum_k a_k J_k + sum_{i, a <= b} b_{i,ab} t_i G_a G_b        (exact in F_p[t])

with u = 1 whenever Singular's lift in the global ordering dp solves the membership, which is stronger than the
local statement (u a unit of the local ring F_p[t]_m). The producer also writes the reduced Groebner basis of K2 in
dp (degree reverse lexicographic, y_1 > ... > y_n), each element's expression in the quadrics, and the Hilbert
function and first Hilbert numerator of F_p[y]/K2.

Conventions. Every coefficient is an integer in [0, p). A polynomial is a list of [coef, [e_1..e_v]] terms sorted by
exponent vector. The J terms index the generators of J from 0; the b entries list [i, a, b, terms] with i the index of
the s variable and a <= b the indices of the G pair, all from 0.

Usage: k2_cofactor_certificate_v1.py HEADER K2.rel OUT.json --header-path PATH --work DIR [--fiber NAME] [--dmax 8]
Singular 4 on PATH; GNU time at /usr/bin/time.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

SCHEMA = "a5-k2-cofactor-certificate-v1"
ULIMIT_KB = 16000000
TIMEOUT_S = 7200

LIFT_SCRIPT = """short=0;
< "header.sing";
int nJ=size(J); int nG=size(G); int ns=nvars(r);
ring Y=%(p)d,(y(1..%(n)d)),dp;
execute("ideal K="+read("k2.rel")+";");
setring r;
map phi=Y,G;
ideal Q=phi(K);
ideal M; int c=0; int i,a,b,k,j;
for(k=1;k<=nJ;k++){ c++; M[c]=J[k]; }
for(i=1;i<=ns;i++){ for(a=1;a<=nG;a++){ for(b=a;b<=nG;b++){ c++; M[c]=var(i)*G[a]*G[b]; } } }
"RESULT sizes", nJ, nG, size(Q), size(M), c;
matrix T=lift(M,Q);
"RESULT lift_done", nrows(T), ncols(T);
for(j=1;j<=ncols(T);j++){ for(k=1;k<=nrows(T);k++){ if(T[k,j]!=0){
  print("COF "+string(j)+" "+string(k)+" "+string(T[k,j])); } } }
"RESULT end";
quit;
"""

GB_SCRIPT = """short=0; option(redSB);
ring Y=%(p)d,(y(1..%(n)d)),dp;
execute("ideal K="+read("k2.rel")+";");
ideal sK=std(K);
"RESULT gb_size", size(sK), size(K);
matrix T=lift(K,sK);
int m,j,d;
for(m=1;m<=size(sK);m++){ print("GB "+string(m)+" "+string(sK[m])); }
for(m=1;m<=ncols(T);m++){ for(j=1;j<=nrows(T);j++){ if(T[j,m]!=0){
  print("GC "+string(m)+" "+string(j)+" "+string(T[j,m])); } } }
intvec hv=hilb(sK,1);
"RESULT hilb1 "+string(hv);
for(d=1;d<=%(dmax)d;d++){ "RESULT h", d, size(kbase(sK,d)); }
"RESULT end";
quit;
"""

TERM = re.compile(r"([+-]?)([^+-]+)")
VARTOK = re.compile(r"([A-Za-z]\w*(?:\(\d+\))?)(?:\^(\d+))?")


def parse_header(path: Path) -> tuple[int, list[str], list[str], list[str]]:
    text = path.read_text().replace("\n", "")
    m = re.search(r"ring r=(\d+),\(([^)]*)\)", text)
    j_text = re.search(r"ideal J=([^;]*);", text)
    g_text = re.search(r"ideal G=([^;]*);", text)
    if m is None or j_text is None or g_text is None:
        raise SystemExit("header has no ring line, ideal J or ideal G")
    split = lambda s: [x for x in s.split(",") if x.strip()]  # noqa: E731
    return int(m.group(1)), m.group(2).split(","), split(j_text.group(1)), split(g_text.group(1))


def parse_poly(text: str, index: dict[str, int], nvars: int, p: int) -> list[list]:
    """Parse an expanded polynomial into sorted [coef, exps] terms with coef in [1, p)."""
    acc: dict[tuple[int, ...], int] = {}
    body = "".join(text.split())
    if not body:
        return []
    pos = 0
    for m in TERM.finditer(body):
        if m.start() != pos:
            raise ValueError(f"unparsed text in polynomial near {body[pos : pos + 20]!r}")
        pos = m.end()
        coef = -1 if m.group(1) == "-" else 1
        exps = [0] * nvars
        for piece in m.group(2).split("*"):
            if piece.isdigit():
                coef *= int(piece)
                continue
            v = VARTOK.fullmatch(piece)
            if v is None or v.group(1) not in index:
                raise ValueError(f"unknown factor {piece!r}")
            exps[index[v.group(1)]] += int(v.group(2) or 1)
        key = tuple(exps)
        acc[key] = (acc.get(key, 0) + coef) % p
    if pos != len(body):
        raise ValueError("trailing text in polynomial")
    return [[c, list(e)] for e, c in sorted(acc.items()) if c]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_singular(name: str, work: Path) -> dict:
    """Run one Singular script under GNU time with a virtual-memory cap and a wall-clock timeout."""
    out, tfile = work / (name + ".out"), work / (name + ".time")
    cmd = [
        "/usr/bin/time", "-v", "-o", str(tfile), "timeout", str(TIMEOUT_S), "sh", "-c",
        f"ulimit -v {ULIMIT_KB}; exec Singular -q --no-rc {name}.sing",
    ]  # fmt: skip
    t0 = time.time()
    with open(out, "w") as fo:
        proc = subprocess.run(cmd, cwd=work, stdin=subprocess.DEVNULL, stdout=fo, stderr=subprocess.STDOUT)
    wall = time.time() - t0
    tt = tfile.read_text()
    rss = re.search(r"Maximum resident set size \(kbytes\): (\d+)", tt)
    if proc.returncode != 0:
        raise SystemExit(f"Singular step {name} exited {proc.returncode}")
    return {"wall_seconds": round(wall, 3), "peak_rss_kib": int(rss.group(1)) if rss else None, "output": out}


def hilbert_numerator(h: dict[int, int], n: int, dmax: int) -> list[int]:
    """First Hilbert numerator (1-t)^n * sum h_d t^d truncated at degree dmax."""
    series = [h[d] for d in range(dmax + 1)]
    binom = [1]
    for k in range(1, n + 1):
        binom.append(binom[-1] * (n - k + 1) // k)
    out = []
    for e in range(dmax + 1):
        out.append(sum((-1) ** k * binom[k] * series[e - k] for k in range(min(e, n) + 1)))
    while out and out[-1] == 0:
        out.pop()
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("header")
    ap.add_argument("rel")
    ap.add_argument("out")
    ap.add_argument("--header-path", required=True, help="repository-relative path recorded in the file")
    ap.add_argument("--rel-path", default=None)
    ap.add_argument("--work", required=True)
    ap.add_argument("--fiber", default="E8-bar -> VB")
    ap.add_argument("--dmax", type=int, default=8)
    a = ap.parse_args()
    t_start = time.time()
    work = Path(a.work).resolve()
    work.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(a.header, work / "header.sing")
    shutil.copyfile(a.rel, work / "k2.rel")
    p, snames, j_txt, g_txt = parse_header(Path(a.header))
    ns, n = len(snames), len(g_txt)
    sidx = {v: i for i, v in enumerate(snames)}
    yidx = {f"y({i + 1})": i for i in range(n)}
    J = [parse_poly(s, sidx, ns, p) for s in j_txt]
    G = [parse_poly(s, sidx, ns, p) for s in g_txt]
    rel_text = Path(a.rel).read_text().replace("\n", "")
    quad_txt = [x for x in rel_text.split(",") if x.strip()]
    quadrics = [parse_poly(s, yidx, n, p) for s in quad_txt]
    (work / "lift.sing").write_text(LIFT_SCRIPT % {"p": p, "n": n})
    (work / "gb.sing").write_text(GB_SCRIPT % {"p": p, "n": n, "dmax": a.dmax})

    lift = run_singular("lift", work)
    cof_a: list[list] = [[] for _ in quadrics]
    cof_b: list[list] = [[] for _ in quadrics]
    pairs = [(x, y) for x in range(n) for y in range(x, n)]
    nj = len(J)
    sizes = None
    with open(lift["output"]) as fh:
        for line in fh:
            if line.startswith("COF "):
                _, js, ks, txt = line.rstrip("\n").split(" ", 3)
                j, k = int(js) - 1, int(ks) - 1
                terms = parse_poly(txt, sidx, ns, p)
                if k < nj:
                    cof_a[j].append([k, terms])
                else:
                    i, r = divmod(k - nj, len(pairs))
                    cof_b[j].append([i, pairs[r][0], pairs[r][1], terms])
            elif line.startswith("RESULT sizes"):
                sizes = line.split()[2:]
            elif line.startswith("?"):
                raise SystemExit("Singular lift error: " + line)
    if sizes is None or [int(x) for x in sizes[:4]] != [nj, n, len(quadrics), nj + ns * len(pairs)]:
        raise SystemExit(f"unexpected sizes {sizes}")
    unit = [[1, [0] * ns]]

    gbr = run_singular("gb", work)
    gb: dict[int, list] = {}
    gc: dict[int, list] = {}
    h: dict[int, int] = {0: 1}
    hilb1 = None
    with open(gbr["output"]) as fh:
        for line in fh:
            if line.startswith("GB "):
                _, m, txt = line.rstrip("\n").split(" ", 2)
                gb[int(m)] = parse_poly(txt, yidx, n, p)
            elif line.startswith("GC "):
                _, m, jq, txt = line.rstrip("\n").split(" ", 3)
                gc.setdefault(int(m), []).append([int(jq) - 1, parse_poly(txt, yidx, n, p)])
            elif line.startswith("RESULT h "):
                _, _, d, v = line.split()
                h[int(d)] = int(v)
            elif line.startswith("RESULT hilb1"):
                hilb1 = [int(x) for x in "".join(line.split()[2:]).split(",") if x]
            elif line.startswith("?"):
                raise SystemExit("Singular gb error: " + line)
    order = sorted(gb)
    numerator = hilbert_numerator(h, n, a.dmax)
    sing_num = list(hilb1 or [])
    while sing_num and sing_num[-1] == 0:
        sing_num.pop()
    if sing_num and sing_num[: len(numerator)] != numerator and sing_num[:-1] != numerator:
        raise SystemExit(f"Hilbert numerator mismatch: python {numerator} singular {hilb1}")

    nterms = [sum(len(t) for _, t in cof_a[j]) + sum(len(e[3]) for e in cof_b[j]) for j in range(len(quadrics))]
    largest = max(len(e[3]) for j in range(len(quadrics)) for e in cof_b[j])
    doc = {
        "schema": SCHEMA,
        "fiber": a.fiber,
        "prime": p,
        "header": {"path": a.header_path, "sha256": sha256_file(Path(a.header))},
        "k2_relations": {"path": a.rel_path, "sha256": sha256_file(Path(a.rel))},
        "vars": {"s": snames, "y": [f"y{i + 1}" for i in range(n)]},
        "J": J,
        "G": G,
        "form": {
            "identity": "u * q(G) = sum_k a_k J_k + sum_{i, a<=b} b_{i,ab} t_i G_a G_b, exact in F_p[s]",
            "kind": "global",
            "truncation_N": None,
            "pair_order": "a <= b",
        },
        "quadrics": [
            {"q": quadrics[j], "u": unit, "a": cof_a[j], "b": cof_b[j], "terms": nterms[j]}
            for j in range(len(quadrics))
        ],
        "groebner": {
            "order": "dp",
            "variable_order": "y1 > y2 > ... > yn, degree reverse lexicographic",
            "basis": [gb[m] for m in order],
            "cofactors": [gc.get(m, []) for m in order],
            "hilbert": {
                "h": {str(d): h[d] for d in sorted(h) if d >= 1},
                "numerator": numerator,
                "singular_hilb1": hilb1,
            },
        },
        "stats": {"cofactor_terms_total": sum(nterms), "largest_b_cofactor_terms": largest},
        "producer": {
            "sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "seconds": {
                "lift_wall": lift["wall_seconds"],
                "groebner_wall": gbr["wall_seconds"],
                "total": round(time.time() - t_start, 3),
            },
            "peak_rss_kib": {"lift": lift["peak_rss_kib"], "groebner": gbr["peak_rss_kib"]},
            "tool_versions": {
                "singular": subprocess.run(
                    ["Singular", "--version"], capture_output=True, text=True, stdin=subprocess.DEVNULL
                ).stdout.split("\n")[0],
                "python": sys.version.split()[0],
                "machine": platform.machine(),
            },
            "limits": {"ulimit_v_kib": ULIMIT_KB, "timeout_seconds": TIMEOUT_S},
        },
    }
    with open(a.out, "w") as fo:
        json.dump(doc, fo, separators=(",", ":"))
    print(f"wrote {a.out} terms={sum(nterms)} h={doc['groebner']['hilbert']['h']} numerator={numerator}")


if __name__ == "__main__":
    main()
