"""Hilbert function of k[y]/K2 from the retained degree-2 relation files.

K2 is the ideal of the quadratic relations among the G generators. Since K2 lies in the kernel L of
k[y] -> F(I), HF(k[y]/K2, d) is an upper bound on h_d = dim I^d/mI^d; a truncated rank r_N equal to it certifies h_d.
Each row recomputes HF(k[y]/K2, d) for d = 1..DMAX with Singular in a dp ordering and binds it to the sha256 of the
relation file. Usage: k2_hilbert.py OUT.jsonl [DMAX]; run from this directory, Singular on PATH or in $SINGULAR.
"""

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

W = Path(__file__).resolve().parent / "working"
OUT = W / "distribute" / "out"

# (fiber, prime, number of G generators, relation file under working/)
SOURCES = [
    ("X-", 32009, 15, "distribute/out/a5-xm-d4/xm_p1/d2/relations-upto-d2.rel"),
    ("X-", 32029, 15, "distribute/out/a5-p2-small/xm_p2/d2/relations-upto-d2.rel"),
    ("X+", 32029, 15, "distribute/out/a5-p2-small/xp_p2/d2/relations-upto-d2.rel"),
    ("E8-bar -> VB", 32009, 10, "runs/e8vb_a2/k2.rel"),
    ("E8-bar -> VB", 32029, 10, "distribute/out/a5-p2-small/vb_p2/d2/relations-upto-d2.rel"),
    ("Iso", 32009, 17, "distribute/out/a5-iso-d4/iso_p1/d2/relations-upto-d2.rel"),
    ("Iso", 32009, 17, "runs/s3/iso_k2.rel"),
    ("Iso", 32029, 17, "distribute/out/a5-p2-iso/iso_p2/d2/relations-upto-d2.rel"),
    ("E8-bar -> N-", 32009, 21, "distribute/out/a5-e8-d2/e8nm_p1/d2/relations-upto-d2.rel"),
    ("E8-bar -> N-", 32029, 21, "distribute/out/a5-e8-d2/e8nm_p2/d2/relations-upto-d2.rel"),
    ("E8-bar -> N+", 32029, 21, "distribute/out/a5-e8-d2/e8np_p2/d2/relations-upto-d2.rel"),
    ("E8-bar -> N+", 32009, 21, "runs/e8_a2/e8_k2.rel"),
    ("W8 -> N-", 32009, 24, "runs/w8_a2/w8_k2.rel"),
    ("W8 -> N-", 32029, 24, "distribute/out/a5-p2-w8/w8_p2/d2/relations-upto-d2.rel"),
]

SCRIPT = """ring Y={p},(y(1..{n})),dp;
execute("ideal K="+read("{rel}")+";");
"RESULT quadrics", size(K), "maxdeg", deg(K[1]);
ideal sK=std(K); int d;
"RESULT projdim", dim(sK)-1, "degree", mult(sK);
for(d=1;d<={dmax};d++){{ "RESULT h", d, size(kbase(sK,d)); }}
quit;
"""


def hilbert(item: tuple[str, int, int, str, int]) -> dict:
    fiber, p, n, rel, dmax = item
    path = W / rel
    singular = os.environ.get("SINGULAR", "Singular")
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp, "k.sing")
        src.write_text(SCRIPT.format(p=p, n=n, rel=path, dmax=dmax))
        res = subprocess.run(
            [singular, "-q", "--no-rc", str(src)], stdin=subprocess.DEVNULL, capture_output=True, text=True, check=True
        )
    if any(ln.startswith("? ") for ln in res.stdout.splitlines()):
        raise RuntimeError(f"Singular error on {rel}: {res.stdout[-400:]}")
    h: dict[str, int] = {}
    rec: dict = {"check": "k2-hilbert-function", "fiber": fiber, "prime": p, "generators": n, "relations": rel}
    for ln in res.stdout.splitlines():
        f = ln.split()
        if f[:2] == ["RESULT", "h"]:
            h[f[2]] = int(f[3])
        elif f[:2] == ["RESULT", "quadrics"]:
            rec["quadrics"] = int(f[2])
        elif f[:2] == ["RESULT", "projdim"]:
            rec["projdim"], rec["degree"] = int(f[2]), int(f[4])
    if len(h) != dmax:
        raise RuntimeError(f"incomplete Hilbert function for {rel}: {res.stdout[-400:]}")
    rec["h"] = h
    rec["relations_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    return rec


def main() -> int:
    out = Path(sys.argv[1])
    dmax = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "gororoba_quantum" / "parallel.py").is_file():
            sys.path.insert(0, str(parent / "gororoba_quantum"))
            break
    import parallel

    rows = parallel.ordered_map(hilbert, [(*s, dmax) for s in SOURCES], min_items=1)
    out.write_text("".join(json.dumps(r) + "\n" for r in rows))
    for r in rows:
        print(r["fiber"], r["prime"], r["quadrics"], [r["h"][str(d)] for d in range(1, dmax + 1)])
    return 0


if __name__ == "__main__":
    sys.exit(main())
