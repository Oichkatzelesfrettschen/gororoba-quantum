"""Regression suite for fiber_rank: an integer-only oracle on small rings plus the reviewed counterexamples.

The oracle builds product jets with Python integer dictionaries, enumerates every monomial multiple of J and of
t_k * P below degree N, and ranks them by its own sparse elimination with modular inverses; it shares no code with the
engine. Each case runs the engine as a subprocess and compares r_N, or checks that a malformed input stops the run.

Usage: fiber_rank_regressions.py ENGINE [--quick]
Prints one JSON object per check and a summary; exits 1 on any failure.
"""

from __future__ import annotations

import importlib.util
import itertools
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np


def _parallel_dir() -> str:
    """GOROROBA_PARALLEL_DIR, else the nearest ancestor's gororoba_quantum directory that holds parallel.py."""
    env = os.environ.get("GOROROBA_PARALLEL_DIR")
    if env:
        return env
    for parent in Path(__file__).resolve().parents:
        if (parent / "gororoba_quantum" / "parallel.py").is_file():
            return str(parent / "gororoba_quantum")
    raise RuntimeError("gororoba_quantum/parallel.py not found above this file; set GOROROBA_PARALLEL_DIR")


sys.path.insert(0, _parallel_dir())
import parallel  # noqa: E402

Mon = tuple[int, int]
Poly = dict[Mon, int]
P_TOY = 3


def mul(a: Poly, b: Poly, N: int, p: int) -> Poly:
    out: Poly = {}
    for x, c in a.items():
        for y, d in b.items():
            z = (x[0] + y[0], x[1] + y[1])
            if sum(z) < N:
                out[z] = (out.get(z, 0) + c * d) % p
    return {m: c for m, c in out.items() if c}


def rank(rows: list[Poly], p: int) -> int:
    piv: dict[Mon, Poly] = {}
    for row0 in rows:
        row = {m: c % p for m, c in row0.items() if c % p}
        while row:
            k = min(row)
            c = row[k]
            if k not in piv:
                inv = pow(c, -1, p)
                piv[k] = {m: v * inv % p for m, v in row.items()}
                break
            for m, v in piv[k].items():
                value = (row.get(m, 0) - c * v) % p
                if value:
                    row[m] = value
                else:
                    row.pop(m, None)
    return len(piv)


def oracle(J: list[Poly], G: list[Poly], d: int, N: int, p: int) -> int:
    mons = [(a, b) for a in range(N) for b in range(N - a)]
    P: list[Poly] = [{(0, 0): 1}]
    for _ in range(d):
        P = [mul(q, g, N, p) for q in P for g in G]
    base = J + [mul({v: 1}, q, N, p) for v in [(1, 0), (0, 1)] for q in P]
    W = [mul({m: 1}, g, N, p) for g in base for m in mons]
    return rank(W + P, p) - rank(W, p)


def text(q: Poly) -> str:
    terms = []
    for (a, b), c in q.items():
        factors = [str(c)] + [v + (f"^{k}" if k != 1 else "") for v, k in (("x", a), ("y", b)) if k]
        terms.append("*".join(factors))
    return "+".join(terms) or "0"


def run_engine(engine: str, header: str, args: list[str]) -> tuple[int, dict | None, str]:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "h.sing"
        path.write_text(header)
        env = dict(os.environ, GOROROBA_WORKERS="1")
        res = subprocess.run(
            [sys.executable, engine, str(path), *args],
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            env=env,
        )
    out = json.loads(res.stdout.strip().splitlines()[-1]) if res.returncode == 0 and res.stdout.strip() else None
    return res.returncode, out, res.stderr[-400:]


def family_case(item: tuple[str, tuple[int, ...]]) -> list[dict]:
    engine, values = item
    p = P_TOY
    G = [{m: c for m, c in zip([(1, 0), (0, 1), (2, 0), (1, 1), (0, 2)], [1, *values], strict=True) if c}, {(0, 2): 1}]
    J = [{m: c for m, c in {(2, 0): 1, (0, 2): 2, (1, 1): values[0]}.items() if c}]
    header = f"ring r={p},(x,y),dp; ideal J={','.join(map(text, J))}; ideal G={','.join(map(text, G))};"
    rows = []
    for N in (3, 4, 5):
        expected = oracle(J, G, 2, N, p)
        for flags in ([], ["--no-split"], ["--direct"], ["--quotient"]):
            rc, out, err = run_engine(engine, header, ["2", str(N), "--chunk", "1", *flags])
            observed = out["r_N"] if out else None
            rows.append(
                {
                    "family": values,
                    "N": N,
                    "flags": flags,
                    "expected": expected,
                    "observed": observed,
                    "rc": rc,
                    "ok": rc == 0 and observed == expected,
                    "stderr": "" if rc == 0 else err,
                }
            )
    return rows


def coordinate_case(item: tuple[str, int, int]) -> dict:
    """Quotient products and multiplication matrices against Singular's direct normal forms, entry by entry.

    J = x^2 + a x y + y^3 and G = (x + 2 y + x y, y + 3 x y + 1) over F_5 are nonhomogeneous, and G holds a unit, so
    ranks alone cannot see a transposed multiplication matrix; the coordinate arrays can. Applies to engines that
    build quotient products from multiplication tables (`table_products`, `mult_matrix`).
    """
    engine_path, a, N = item
    spec = importlib.util.spec_from_file_location("engine_under_test", engine_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {engine_path}")
    eng = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(eng)
    p, names = 5, ["x", "y"]
    header = {"J": f"x^2+{a}*x*y+y^3", "G": "x+2*y+x*y,y+3*x*y+1"}
    gens = header["G"].split(",")
    basis, tables, polys, _ = eng.quotient_data(header, names, p, N, 4, "Singular")
    index = {m: i for i, m in enumerate(basis)}
    D = len(basis)

    def coords(rows: list[dict]) -> np.ndarray:
        out = np.zeros((len(rows), D))
        for r, poly in enumerate(rows):
            for m, c in poly.items():
                out[r, index[m]] = c
        return out

    mats = [eng.sp.csr_matrix(coords(t)) for t in tables]
    vecs = coords(polys)

    def singular_nf(exprs: list[str]) -> np.ndarray:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "nf.txt"
            script = (
                f"ring r={p},(x,y),dp; option(redSB); ideal J={header['J']}; ideal s=std(J+maxideal({N})); "
                f'ideal P={",".join(exprs)}; P=reduce(P,s); short=0; write(":w {out}",P); quit;'
            )
            (Path(tmp) / "nf.sing").write_text(script)
            res = subprocess.run(
                ["Singular", "-q", "--no-rc", str(Path(tmp) / "nf.sing")],
                stdin=subprocess.DEVNULL,
                capture_output=True,
                text=True,
                check=True,
            )
            if any(ln.startswith("? ") for ln in res.stdout.splitlines()):
                raise RuntimeError(res.stdout[-300:])
            return coords(eng.read_list(str(out), names, p))

    ok = True
    for d in (0, 1, 2, 3, 4):
        combos = list(itertools.combinations_with_replacement(range(2), d))
        exprs = ["*".join(f"({gens[f]})" for f in c) or "1" for c in combos]
        want = singular_nf(exprs)
        for cache in (0, 10**8):
            ok &= bool(np.array_equal(eng.table_products(vecs, basis, mats, d, p, cache), want))
    rows = [
        f"({g})*" + ("*".join(f"{v}^{e}" for v, e in zip(names, m, strict=True) if e) or "1")
        for g in gens
        for m in basis
    ]
    target = singular_nf(rows)
    transpose_seen = False
    for f in range(2):
        L = eng.mult_matrix(vecs[f], basis, mats, p)
        want = target[f * D : (f + 1) * D]
        ok &= bool(np.array_equal(L, want))
        transpose_seen |= not np.array_equal(L.T, want)
    return {
        "check": "coordinate-oracle",
        "a": a,
        "N": N,
        "D": D,
        "ok": ok and transpose_seen,
        "transpose_distinguished": transpose_seen,
    }


def main() -> int:
    engine = str(Path(sys.argv[1]).resolve())
    quick = "--quick" in sys.argv
    checks: list[dict] = []
    families = list(itertools.product(range(P_TOY), repeat=4))
    if quick:
        families = families[::9]
    for rows in parallel.ordered_map(family_case, [(engine, v) for v in families], min_items=1):
        checks.extend(rows)
    fam_fail = [c for c in checks if not c["ok"]]
    print(json.dumps({"check": "oracle-families", "cases": len(checks), "failures": fam_fail[:20]}))

    def expect_reject(name: str, header: str, args: list[str], needle: str) -> dict:
        rc, out, err = run_engine(engine, header, args)
        return {"check": name, "rc": rc, "ok": rc != 0 and needle in err, "stderr": err[-200:]}

    def expect_rank(name: str, header: str, args: list[str], expected: int) -> dict:
        rc, out, err = run_engine(engine, header, args)
        observed = out["r_N"] if out else None
        return {
            "check": name,
            "rc": rc,
            "expected": expected,
            "observed": observed,
            "ok": observed == expected,
            "stderr": "" if rc == 0 else err[-200:],
        }

    xy = "ring r=32009,(x,y),dp;"
    cases = [
        expect_reject("unary-minus-inside-product", xy + " ideal J=x*-y; ideal G=x*y;", ["1", "3"], "grammar"),
        expect_reject("characteristic-2", "ring r=2,(x,y),dp; ideal J=0; ideal G=x+y;", ["1", "2"], "odd prime"),
        expect_reject(
            "direct-with-quotient", xy + " ideal J=x*y; ideal G=x,y;", ["1", "3", "--direct", "--quotient"], "exclusive"
        ),
        expect_rank(
            "one-letter-quotient",
            xy + " ideal J=x*y; ideal G=x,y;",
            ["2", "5", "--quotient", "--no-split"],
            oracle([{(1, 1): 1}], [{(1, 0): 1}, {(0, 1): 1}], 2, 5, 32009),
        ),
        expect_rank(
            "quotient-absent-block", "ring r=32009,(t1,t2),dp; ideal J=t1; ideal G=t2;", ["1", "3", "--quotient"], 1
        ),
        expect_rank("direct-empty-seed", "ring r=5,(x),dp; ideal J=x^3; ideal G=x;", ["1", "2", "--direct"], 1),
        expect_rank(
            "degree-zero-quotient",
            "ring r=5,(x,y),dp; ideal J=0; ideal G=x,y;",
            ["0", "4", "--quotient", "--no-split"],
            oracle([], [{(1, 0): 1}, {(0, 1): 1}], 0, 4, 5),
        ),
        expect_rank(
            "large-prime-quotient",
            "ring r=65537,(x,y),dp; ideal J=x*y; ideal G=x,y;",
            ["2", "4", "--quotient", "--no-split", "--table-cache-gb", "0"],
            oracle([{(1, 1): 1}], [{(1, 0): 1}, {(0, 1): 1}], 2, 4, 65537),
        ),
        expect_rank(
            "large-prime-quotient-cached",
            "ring r=65537,(x,y),dp; ideal J=x*y; ideal G=x,y;",
            ["2", "4", "--quotient", "--no-split"],
            oracle([{(1, 1): 1}], [{(1, 0): 1}, {(0, 1): 1}], 2, 4, 65537),
        ),
        expect_reject("negative-degree", "ring r=5,(x,y),dp; ideal J=0; ideal G=x,y;", ["-1", "4"], "d >= 0"),
    ]
    for bad in ["x-+y", "x--y", "x^", "x*", "x**2", "x^-1", "x+", "2x", "(x+y)", "x*-y", "y4+x2y"]:
        cases.append(expect_reject(f"parser-rejects {bad}", f"{xy} ideal J={bad}; ideal G=x;", ["1", "3"], "grammar"))
    iso = Path(__file__).resolve().parent.parent / "trunc" / "iso_d4" / "input.sing"
    if iso.exists():
        for flags in ([], ["--no-split"], ["--direct"], ["--quotient"]):
            cases.append(
                expect_rank(f"iso-d3-N9 {' '.join(flags) or 'split'}", iso.read_text(), ["3", "9", *flags], 216)
            )
    eng_src = Path(engine).read_text()
    if "def table_products(" in eng_src:
        items = [(engine, a, N) for a in range(5) for N in (3, 4, 5, 6)]
        if quick:
            items = items[::4]
        cases.extend(parallel.ordered_map(coordinate_case, items, min_items=1))
    for c in cases:
        print(json.dumps(c))
    failed = len(fam_fail) + sum(1 for c in cases if not c["ok"])
    print(json.dumps({"summary": {"oracle_cases": len(checks), "fixtures": len(cases), "failed": failed}}))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
