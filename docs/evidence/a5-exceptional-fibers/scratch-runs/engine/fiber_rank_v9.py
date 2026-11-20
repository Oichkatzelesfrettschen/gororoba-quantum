"""Truncated fiber-cone rank by linear algebra over F_p.

r_N = dim_k of the image of span(all degree-d products of G) in V_N / W_N, where V_N = k[t]/m^N is the space of
polynomials of degree < N and W_N is the image of the ideal (J, m * P_d) in V_N. W_N is computed as the closure of
the span of the truncated generators J and t_k * P under multiplication by the variables (semi-naive: each round
multiplies only the basis vectors whose pivots appeared in the previous round). Every polynomial is a jet: products
are truncated below degree N after each multiplication, which leaves their classes in V_N unchanged.

r_N <= h_d = dim I^d / m I^d for every N, r_N is nondecreasing in N, and r_N = h_d for N large (Krull intersection in
the localization). The products are all degree-d monomials in G, so the result depends on no previously computed
relation and no target basis.

Modes. The default (raw) mode works on the monomial basis of V_N, builds the product jets with FLINT multivariate
arithmetic and needs no standard basis. --direct replaces the closure by an explicit enumeration of every monomial
multiple of every generator, as a check on the closure. --quotient works in k[t]/(J + m^N) instead: Singular computes a
dp (global) standard basis of J + m^N, its standard monomials, the multiplication table of each variable on them and
the normal forms of the generators. The products are formed in that quotient from the tables: for each generator g the
matrix of multiplication by g has row g * B for each standard monomial B, built by walking the order ideal of standard
monomials (g * t_k B = (g * B) * t_k), and every degree-d product is its degree-(d-1) prefix times that matrix. The
same closure then runs in that smaller space; it serves non-principal J, whose
truncated monomial space is too large to hold densely.

The quotient export does not depend on d. One Singular process computes the standard basis and writes it; then one
process per variable table (or per standard-monomial range of it, --export-chunks) and one for the generators run in
parallel, each reading the basis back. The parsed export equals that of engine v8's single serial export
(test_split_export_equals_serial in tests/test_a5_fiber_rank_v9.py, where Singular is installed). --export-dir
keeps them under a manifest of prime, variables, N and the sha256 of J and G, so later runs at any degree, or tables
computed on another host and copied in, are reused; --adopt-export admits files copied from an engine v8 serial
export after checking its script. The --max-gb preflight runs once the basis is known, before any table.

Every generator of span(J) and span(G) is preserved by the diagonal sign group found by exhaustive search, so the
ideal and the product span split into character blocks: a vector's projection onto a character lies in the same
ideal. Each block is echelonized separately; multiplication by t_k maps block chi to chi + chi(t_k). In quotient mode
the reduced standard basis of the invariant ideal J + m^N consists of character eigenvectors, so the multiplication
tables respect the blocks; the code checks every table entry and stops if one crosses blocks. --no-split runs one
block, as a check on the split.

Exactness: entries live in [0, p); every product X @ B runs in float64 and checks its own inner dimension k against
k * (p - 1)^2 < 2^53 before it runs, so BLAS returns the exact integer before the reduction modulo p. FLINT's
nmod_mat.rref echelonizes the residual rows. The modulus must be an odd prime, because the character projectors divide
by the group order.

Input boundary: every polynomial must match the expanded signed-monomial grammar (signed integer coefficients, `*`
between factors, `^` before exponents, variable names from the ring line); any other string stops the run. Singular's
`write` emits that form only with `short=0` set in the current ring, which the quotient export sets before each write.

Usage: fiber_rank_v9.py HEADER D N [--no-split] [--direct] [--quotient] [--chunk ROWS] [--export-dir DIR]
    [--export-chunks C] [--adopt-export] [--max-gb G]
HEADER is a Singular file with lines `ring r=P,(vars),dp;`, `ideal J=...;` and `ideal G=...;`.
Prints one JSON object.
"""

from __future__ import annotations

import argparse
import functools
import hashlib
import itertools
import json
import math
import os
import re
import subprocess
import sys
import tempfile
import time
from collections.abc import Callable, Iterator
from pathlib import Path

import flint
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
import scipy.sparse as sp  # noqa: E402

import parallel  # noqa: E402

ENGINE_SHA = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()[:16]


def header_text(path: str) -> dict[str, str]:
    text = Path(path).read_text().replace("\n", "")
    j_text = re.search(r"ideal J=([^;]*);", text)
    g_text = re.search(r"ideal G=([^;]*);", text)
    if j_text is None or g_text is None:
        raise SystemExit("no ideal J or G")
    return {"J": j_text.group(1), "G": g_text.group(1)}


def parse_header(path: str) -> tuple[int, list[str], list[str], list[str]]:
    text = Path(path).read_text().replace("\n", "")
    m = re.search(r"ring r=(\d+),\(([^)]*)\)", text)
    if m is None:
        raise SystemExit("no ring r line")
    p, names = int(m.group(1)), m.group(2).split(",")
    j_text = re.search(r"ideal J=([^;]*);", text)
    g_text = re.search(r"ideal G=([^;]*);", text)
    if j_text is None or g_text is None:
        raise SystemExit("no ideal J or G")
    split = lambda s: [x for x in s.split(",") if x.strip()]  # noqa: E731
    return p, names, split(j_text.group(1)), split(g_text.group(1))


def term_grammar(names: list[str]) -> tuple[re.Pattern[str], re.Pattern[str]]:
    """Expanded signed-monomial grammar: term = [+-] (INT | INT*MON | MON), MON = VAR[^INT](*VAR[^INT])*."""
    var = "(?:" + "|".join(re.escape(v) for v in sorted(names, key=len, reverse=True)) + r")(?:\^[0-9]+)?"
    mon = var + r"(?:\*" + var + ")*"
    term = r"(?:[0-9]+(?:\*" + mon + ")?|" + mon + ")"
    return re.compile(r"[+-]?" + term + r"(?:[+-]" + term + ")*"), re.compile(r"([+-]?)(" + term + ")")


def parse_poly(text: str, names: list[str], p: int) -> dict[tuple[int, ...], int]:
    """Parse one expanded polynomial; any string outside the grammar raises ValueError."""
    whole, single = term_grammar(names)
    body_text = "".join(text.split())
    if not whole.fullmatch(body_text):
        raise ValueError(f"polynomial outside the expanded signed-monomial grammar: {body_text[:120]!r}")
    idx = {v: i for i, v in enumerate(names)}
    out: dict[tuple[int, ...], int] = {}
    for m in single.finditer(body_text):
        sign, body = m.group(1), m.group(2)
        coef, e = 1, [0] * len(names)
        for f in body.split("*"):
            if f.isdigit():
                coef *= int(f)
            else:
                v, _, k = f.partition("^")
                e[idx[v]] += int(k) if k else 1
        key = tuple(e)
        out[key] = (out.get(key, 0) + (-coef if sign == "-" else coef)) % p
    return {k: c for k, c in out.items() if c}


def exact_mod_matmul(A: np.ndarray, B: np.ndarray, p: int) -> np.ndarray:
    """A @ B mod p for residue matrices, refused when a float64 partial sum could exceed 2^53."""
    if A.shape[1] * (p - 1) ** 2 >= 2**53:
        raise RuntimeError(f"inner dimension {A.shape[1]} leaves the exact float64 range at p = {p}")
    return np.mod(A @ B, p)


def is_odd_prime(p: int) -> bool:
    return p > 2 and p % 2 == 1 and all(p % q for q in range(3, int(p**0.5) + 1, 2))


def sign_group(polys_by_ideal: list[list[dict]], n: int, p: int) -> list[tuple[int, ...]]:
    """Every diagonal sign vector (flip set) preserving the span of each listed polynomial family."""

    def rank(rows: list[dict]) -> int:
        cols: dict = {}
        mat = [{cols.setdefault(m, len(cols)): c for m, c in r.items()} for r in rows]
        if not cols:
            return 0
        a = flint.nmod_mat(len(mat), len(cols), p)
        for i, r in enumerate(mat):
            for j, c in r.items():
                a[i, j] = c
        return a.rank()

    def flip(poly: dict, fl: tuple[int, ...]) -> dict:
        return {m: c * (-1) ** sum(m[i] for i in fl) % p for m, c in poly.items()}

    base = [rank(fam) for fam in polys_by_ideal]
    group = []
    for k in range(1, n + 1):
        for fl in itertools.combinations(range(n), k):
            if all(rank(fam + [flip(q, fl) for q in fam]) == b for fam, b in zip(polys_by_ideal, base, strict=True)):
                group.append(fl)
    return group


def independent_generators(group: list[tuple[int, ...]], n: int) -> list[np.ndarray]:
    """A basis of the group as 0/1 vectors over F_2."""
    vecs = [np.array([1 if i in fl else 0 for i in range(n)], dtype=np.int64) for fl in group]
    basis: list[np.ndarray] = []
    for v in vecs:
        w = v.copy()
        for b in basis:
            piv = int(np.argmax(b))
            if w[piv]:
                w = (w + b) % 2
        if w.any():
            basis.append(w)
    return basis


class Space:
    """Monomials of degree < N in n variables, indexed, with character blocks and variable shifts."""

    def __init__(self, n: int, N: int, gens: list[np.ndarray]):
        mons = [e for deg in range(N) for e in exps_of_degree(n, deg)]
        self.n, self.N = n, N
        self.exps = np.array(mons, dtype=np.int64)
        self.deg = self.exps.sum(axis=1)
        self.radix = np.array([N**i for i in range(n)], dtype=np.int64)
        keys = self.exps @ self.radix
        order = np.argsort(keys)
        self.sorted_keys, self.sorted_idx = keys[order], order
        chars = np.stack([(self.exps @ g) % 2 for g in gens], axis=1) if gens else np.zeros((len(mons), 0), np.int64)
        self.block_of = chars @ np.array([2**i for i in range(chars.shape[1])], dtype=np.int64)
        self.blocks = list(range(2 ** len(gens)))
        self.cols = {b: np.flatnonzero(self.block_of == b) for b in self.blocks}
        self.pos = np.empty(len(mons), dtype=np.int64)
        for b in self.blocks:
            self.pos[self.cols[b]] = np.arange(len(self.cols[b]))
        self.var_char = [int(sum((int(g[k]) % 2) << i for i, g in enumerate(gens))) for k in range(n)]
        # shift[k][j]: index of t_k * monomial j, or -1 when the degree reaches N
        self.shift = []
        for k in range(n):
            e = self.exps.copy()
            e[:, k] += 1
            ok = e.sum(axis=1) < N
            tgt = np.full(len(mons), -1, dtype=np.int64)
            tgt[ok] = self.index(e[ok])
            self.shift.append(tgt)

    def index(self, exps: np.ndarray) -> np.ndarray:
        keys = exps @ self.radix
        loc = np.searchsorted(self.sorted_keys, keys)
        if np.any(loc >= len(self.sorted_keys)) or np.any(
            self.sorted_keys[np.minimum(loc, len(self.sorted_keys) - 1)] != keys
        ):
            raise RuntimeError("monomial outside the truncated space")
        return self.sorted_idx[loc]

    def index_keys(self, keys: np.ndarray) -> np.ndarray:
        """Indices (int32) of monomials given by mixed-radix keys; every key must lie in the truncated space."""
        loc = np.searchsorted(self.sorted_keys, keys)
        if np.any(loc >= len(self.sorted_keys)) or np.any(
            self.sorted_keys[np.minimum(loc, len(self.sorted_keys) - 1)] != keys
        ):
            raise RuntimeError("monomial outside the truncated space")
        return self.sorted_idx[loc].astype(np.int32)

    def sparse(self, poly: dict) -> tuple[np.ndarray, np.ndarray]:
        """Index and coefficient arrays of the terms of degree < N."""
        items = [(m, c) for m, c in poly.items() if sum(m) < self.N]
        if not items:
            return np.zeros(0, dtype=np.int64), np.zeros(0)
        idx = self.index(np.array([m for m, _ in items], dtype=np.int64))
        return idx, np.array([c for _, c in items], dtype=np.float64)

    def dense_rows(self, polys: list[tuple[np.ndarray, np.ndarray]], b: int) -> np.ndarray:
        """Dense rows of the projections of sparse polynomials onto character block b; zero projections dropped."""
        out = []
        for idx, coef in polys:
            sel = self.block_of[idx] == b
            if sel.any():
                r = np.zeros(len(self.cols[b]))
                r[self.pos[idx[sel]]] = coef[sel]
                out.append(r)
        return np.array(out) if out else np.zeros((0, len(self.cols[b])))


def exps_of_degree(n: int, deg: int) -> list[tuple[int, ...]]:
    out = []
    for combo in itertools.combinations_with_replacement(range(n), deg):
        e = [0] * n
        for i in combo:
            e[i] += 1
        out.append(tuple(e))
    return out


class Echelon:
    """Reduced row echelon basis over F_p of a subspace of one block, grown by inserting rows."""

    def __init__(self, ncols: int, p: int):
        self.p, self.ncols = p, ncols
        self.B = np.zeros((0, ncols))
        self.piv = np.zeros(0, dtype=np.int64)

    def reduce(self, X: np.ndarray) -> np.ndarray:
        if len(self.piv) == 0 or len(X) == 0:
            return np.mod(X, self.p)
        return np.mod(X - exact_mod_matmul(X[:, self.piv], self.B, self.p), self.p)

    def insert(self, X: np.ndarray, chunk: int) -> np.ndarray:
        """Insert rows; returns the indices (into self.B) of rows whose pivots are new."""
        start = set(self.piv.tolist())
        for s in range(0, len(X), chunk):
            Y = self.reduce(X[s : s + chunk])
            Y = Y[np.any(Y != 0, axis=1)]
            if len(Y) == 0:
                continue
            free = np.setdiff1d(np.arange(self.ncols), self.piv)
            Z = Y[:, free].astype(np.int64)
            M = flint.nmod_mat(Z.shape[0], Z.shape[1], Z.ravel().tolist(), self.p)
            R, rk = M.rref()
            if rk == 0:
                continue
            Rn = np.array([int(x) for x in R.entries()], dtype=np.float64).reshape(Z.shape)[:rk]
            Xr = np.zeros((rk, self.ncols))
            Xr[:, free] = Rn
            q = free[np.argmax(Rn != 0, axis=1)]
            if len(self.piv):
                self.B = np.mod(self.B - exact_mod_matmul(self.B[:, q], Xr, self.p), self.p)
            self.B = np.vstack([self.B, Xr])
            self.piv = np.concatenate([self.piv, q])
        return np.array([i for i, c in enumerate(self.piv.tolist()) if c not in start], dtype=np.int64)


Monomial = tuple[int, ...]
Poly = dict[Monomial, int]


Packed = tuple[tuple[int, ...], np.ndarray, np.ndarray]


def pack(poly: dict, N: int) -> tuple[np.ndarray, np.ndarray]:
    """Terms of degree < N as mixed-radix monomial keys (sum e_i N^i, int64) and coefficients (int32)."""
    if not poly:
        return np.zeros(0, dtype=np.int64), np.zeros(0, dtype=np.int32)
    exps = np.array(list(poly.keys()), dtype=np.int64)
    coefs = np.fromiter((int(c) for c in poly.values()), dtype=np.int64, count=len(poly))
    ok = exps.sum(axis=1) < N
    radix = N ** np.arange(exps.shape[1], dtype=np.int64)
    return exps[ok] @ radix, coefs[ok].astype(np.int32)


def unpack(keys: np.ndarray, coefs: np.ndarray, n: int, N: int) -> dict[Monomial, int]:
    exps = (keys[:, None] // (N ** np.arange(n, dtype=np.int64))[None, :]) % N
    return {tuple(e): int(c) for e, c in zip(exps.tolist(), coefs.tolist(), strict=True)}


def extend_products(item: Packed, gens: list[Poly], names: tuple[str, ...], p: int, N: int) -> list[Packed]:
    """Multiply one packed product jet by every generator of index >= its last factor, truncating below degree N."""
    t, keys, coefs = item
    ctx = flint.nmod_mpoly_ctx.get(names, modulus=p)
    q = ctx.from_dict(unpack(keys, coefs, len(names), N))
    out = []
    for f in range(t[-1] if t else 0, len(gens)):
        out.append((t + (f,), *pack((q * ctx.from_dict(gens[f])).to_dict(), N)))
    return out


# The export runs as one standard-basis process and then independent table processes. Each table process reads the
# reduced standard basis back from s.txt and marks it with attrib(s, "isSB", 1); without that attribute reduce treats
# s as a plain generating set and the normal forms differ. kbase of the marked basis reproduces qB.txt index for index,
# which the "? basis size" check enforces, so table rows stay paired with basis entries.
STD_SCRIPT = """ring r={p},({names}),dp;
ideal J={J};
option(redSB);
int t0=rtimer;
ideal s=std(J+maxideal({N}));
short=0; write(":w {out}/s.txt.part",s);
ideal B=kbase(s);
short=0; write(":w {out}/qB.txt.part",B);
"RESULT std", ncols(s), ncols(B), rtimer-t0;
quit;
"""

LOAD_SCRIPT = """ring r={p},({names}),dp;
option(redSB);
execute("ideal s=" + read("{out}/s.txt") + ";");
attrib(s,"isSB",1);
ideal B=kbase(s);
if(ncols(B)!={D}){{ "? basis size", ncols(B), {D}; quit; }}
"""

TABLE_SCRIPT = """ideal Bh=B[{lo}..{hi}];
ideal Mk=reduce(var({k})*Bh,s);
if(ncols(Mk)!={hi}-{lo}+1){{ "? table length", ncols(Mk); quit; }}
short=0; write(":w {part}",Mk);
"RESULT table";
quit;
"""

GENERATOR_SCRIPT = """ideal G={G};
int g0=ncols(G); G=reduce(jet(G,{N}-1),s);
if(ncols(G)!=g0){{ "? generator count", ncols(G), g0; quit; }}
short=0; write(":w {part}",G);
"RESULT generators";
quit;
"""

EXPORT_MANIFEST = "export.json"


def read_list(path: str, names: list[str], p: int) -> list[Poly]:
    text = Path(path).read_text().replace("\n", "")
    return [parse_poly(x, names, p) if x.strip() != "0" else {} for x in text.split(",")]


def file_sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def run_singular(job: tuple[str, str, str, str, str]) -> tuple[str, float]:
    """Run one export script; on its RESULT line, publish its output by renaming the .part file to the final name."""
    singular, script, script_path, part, final = job
    with open(script_path, "w") as f:
        f.write(script)
    t = time.time()
    res = subprocess.run(
        [singular, "-q", "--no-rc", script_path], stdin=subprocess.DEVNULL, capture_output=True, text=True, check=True
    )
    if "RESULT " not in res.stdout or any(ln.startswith("? ") for ln in res.stdout.splitlines()):
        raise RuntimeError(f"Singular export step {final} failed: " + res.stdout[-500:] + res.stderr[-500:])
    os.replace(part, final)
    return os.path.basename(final), time.time() - t


def export_identity(header_text: dict[str, str], names: list[str], p: int, N: int) -> dict:
    return {
        "prime": p,
        "vars": names,
        "N": N,
        "J_sha256": hashlib.sha256(header_text["J"].encode()).hexdigest(),
        "G_sha256": hashlib.sha256(header_text["G"].encode()).hexdigest(),
    }


def adopt_serial_export(out: str, header_text: dict[str, str], names: list[str], p: int, N: int) -> None:
    """Accept files copied from an engine v8 serial export when its q.sing script names this header, prime and N."""
    text = Path(out, "q.sing").read_text()
    needed = [
        f"ring r={p},({','.join(names)}),dp;",
        f"ideal J={header_text['J']};",
        f"ideal G={header_text['G']};",
        f"ideal s=std(J+maxideal({N}));",
    ]
    if not all(x in text for x in needed):
        raise SystemExit("--adopt-export: q.sing does not name this header's ring, J, G and N")


def quotient_data(
    header_text: dict[str, str],
    names: list[str],
    p: int,
    N: int,
    singular: str,
    export_dir: str | None = None,
    adopt: bool = False,
    chunks: int = 1,
    preflight: Callable[[list[Monomial]], None] | None = None,
) -> tuple[list[Monomial], list[list[Poly]], list[Poly], dict]:
    """Standard monomials of std(J + m^N) in dp, the multiplication tables of the variables, the reduced generators.

    The export does not depend on the degree d. With export_dir it persists there under a manifest of (prime,
    variables, N, sha256 of J and G), and a later run at any degree reuses every finished file; files computed on
    another host join by being copied into the directory. preflight runs on the basis before any table is computed.
    """
    if export_dir is None:
        with tempfile.TemporaryDirectory() as tmp:
            return quotient_data(header_text, names, p, N, singular, tmp, False, chunks, preflight)
    out = os.path.abspath(export_dir)
    os.makedirs(out, exist_ok=True)
    ident = export_identity(header_text, names, p, N)
    mpath = os.path.join(out, EXPORT_MANIFEST)
    if os.path.exists(mpath):
        recorded = json.loads(Path(mpath).read_text())
        if {k: recorded.get(k) for k in ident} != ident:
            raise SystemExit(f"{EXPORT_MANIFEST} in --export-dir names another header, prime or N")
        for f, h in recorded.get("files", {}).items():
            if os.path.exists(os.path.join(out, f)) and file_sha256(os.path.join(out, f)) != h:
                raise SystemExit(f"{f} in --export-dir differs from the sha256 its manifest records")
    elif any(f.startswith(("q", "s.")) and f.endswith(".txt") for f in os.listdir(out)):
        if not adopt:
            raise SystemExit("--export-dir holds export files without a manifest; check them and pass --adopt-export")
        adopt_serial_export(out, header_text, names, p, N)
    with open(mpath + ".part", "w") as f:
        json.dump(ident, f)
    os.replace(mpath + ".part", mpath)
    nv, base = len(names), {"p": p, "names": ",".join(names), "out": out}
    computed: dict[str, float] = {}
    reused = sorted(f for f in os.listdir(out) if f.startswith(("q", "s.")) and f.endswith(".txt"))
    path = functools.partial(os.path.join, out)
    if not os.path.exists(path("s.txt")):
        prior_basis = path("qB.txt") if os.path.exists(path("qB.txt")) else None
        if prior_basis:
            os.replace(prior_basis, path("qB.prior.txt"))
        job = (singular, STD_SCRIPT.format(J=header_text["J"], N=N, **base), path("std.sing"), path("s.txt.part"),
               path("s.txt"))  # fmt: skip
        computed["s.txt"] = round(run_singular(job)[1], 1)
        os.replace(path("qB.txt.part"), path("qB.txt"))
        if prior_basis:
            # A recomputed standard basis must reproduce the basis the existing tables were written against.
            if Path(path("qB.txt")).read_text().replace("\n", "") != Path(path("qB.prior.txt")).read_text().replace(
                "\n", ""
            ):
                raise SystemExit("recomputed kbase differs from the qB.txt already in --export-dir")
            os.remove(path("qB.prior.txt"))
        reused = [f for f in reused if f not in ("s.txt", "qB.txt")]
    basis = [next(iter(q)) for q in read_list(path("qB.txt"), names, p)]
    D = len(basis)
    if preflight is not None:
        preflight(basis)
    load = LOAD_SCRIPT.format(D=D, **base)
    jobs, joins = [], []
    bounds = [(1 + i * D // chunks, (i + 1) * D // chunks) for i in range(chunks)]
    for k in range(1, nv + 1):
        final = path(f"qM{k}.txt")
        if os.path.exists(final):
            continue
        parts = [path(f"qM{k}.c{i}.txt") if chunks > 1 else final for i in range(len(bounds))]
        for (lo, hi), part in zip(bounds, parts, strict=True):
            if lo <= hi and not os.path.exists(part):
                script = load + TABLE_SCRIPT.format(k=k, lo=lo, hi=hi, part=part + ".part")
                jobs.append((singular, script, part[:-4] + ".sing", part + ".part", part))
        if chunks > 1:
            joins.append((final, [q for (lo, hi), q in zip(bounds, parts, strict=True) if lo <= hi]))
    if not os.path.exists(path("qG.txt")):
        script = load + GENERATOR_SCRIPT.format(G=header_text["G"], N=N, part=path("qG.txt.part"))
        jobs.append((singular, script, path("qG.sing"), path("qG.txt.part"), path("qG.txt")))
    for name, seconds in parallel.ordered_map(run_singular, jobs, min_items=2):
        computed[name] = round(seconds, 1)
    for final, parts in joins:
        with open(final + ".part", "w") as f:
            f.write(",".join(Path(q).read_text().replace("\n", "") for q in parts))
        os.replace(final + ".part", final)
        for q in parts:
            os.remove(q)
    tables = [read_list(path(f"qM{k + 1}.txt"), names, p) for k in range(nv)]
    gens = read_list(path("qG.txt"), names, p)
    # The reader pairs table rows with basis entries by index, so each table keeps its zero normal forms in place.
    if any(len(tab) != D for tab in tables):
        raise RuntimeError("Singular quotient export: a multiplication table length differs from the basis size")
    files = {f: file_sha256(path(f)) for f in ["s.txt", "qB.txt", "qG.txt"] + [f"qM{k}.txt" for k in range(1, nv + 1)]}
    with open(mpath + ".part", "w") as f:
        json.dump({**ident, "files": files}, f)
    os.replace(mpath + ".part", mpath)
    info = {"reused": reused, "computed_seconds": computed, "chunks": chunks, "files_sha256_16": {
        f: h[:16] for f, h in files.items()}}  # fmt: skip
    return basis, tables, gens, info


def mult_matrix(g: np.ndarray, basis: list[Monomial], M: list[sp.csr_matrix], p: int) -> np.ndarray:
    """Matrix L with row i = coordinates of g * basis[i]; row-vector convention, so x @ L = x * g.

    The standard monomials of a dp standard basis form an order ideal, so every B != 1 has a parent B / t_k in the
    basis and row(B) = row(B / t_k) @ M_k. Rows are filled level by level in total degree, one sparse product per
    (level, k). Entries stay in [0, p); each sparse product sums at most D terms below p^2, exact in float64.
    """
    D = len(basis)
    if D * (p - 1) ** 2 >= 2**53:
        raise ValueError(f"sparse walk not exact in float64: D * (p - 1)^2 >= 2^53 at D = {D}, p = {p}")
    idx = {m: i for i, m in enumerate(basis)}
    L = np.zeros((D, D))
    one = tuple(0 for _ in basis[0])
    if one not in idx:
        raise RuntimeError("the constant monomial is not standard")
    L[idx[one]] = g
    levels: dict[int, list[int]] = {}
    for i, m in enumerate(basis):
        levels.setdefault(sum(m), []).append(i)
    for deg in sorted(levels):
        if deg == 0:
            continue
        by_k: dict[int, tuple[list[int], list[int]]] = {}
        for i in levels[deg]:
            m = basis[i]
            k = next(k for k, e in enumerate(m) if e and tuple(x - (j == k) for j, x in enumerate(m)) in idx)
            parent = idx[tuple(x - (j == k) for j, x in enumerate(m))]
            by_k.setdefault(k, ([], []))[0].append(i)
            by_k[k][1].append(parent)
        for k, (kids, parents) in by_k.items():
            L[kids] = np.mod(np.asarray(M[k].T @ L[parents].T).T, p)
    return L


def table_products(
    gvecs: np.ndarray, basis: list[Monomial], M: list[sp.csr_matrix], d: int, p: int, cache_bytes: int
) -> np.ndarray:
    """All degree-d monomials in the generators, as rows of quotient coordinates, from the multiplication matrices.

    A monomial is a sorted index tuple; its row is the row of the tuple without its last (largest) index times the
    matrix of that generator. Matrices are kept as uint16 for p < 2^16, uint32 otherwise, while their total size stays
    within cache_bytes, and rebuilt on each use otherwise. Degree zero is the single product 1.
    """
    n = len(gvecs)
    D = len(basis)
    if d == 0:
        one = np.zeros((1, D))
        one[0, basis.index(tuple(0 for _ in basis[0]))] = 1
        return one
    dtype = np.uint16 if p < 2**16 else np.uint32
    keep = cache_bytes >= n * D * D * np.dtype(dtype).itemsize
    cache: dict[int, np.ndarray] = {}

    def matrix(f: int) -> np.ndarray:
        if f in cache:
            return cache[f].astype(np.float64)
        L = mult_matrix(gvecs[f], basis, M, p)
        if keep:
            cache[f] = L.astype(dtype)
        return L

    rows: dict[tuple[int, ...], np.ndarray] = {(f,): gvecs[f] for f in range(n)}
    level: list[tuple[int, ...]] = [(f,) for f in range(n)]
    for _ in range(d - 1):
        nxt: dict[tuple[int, ...], np.ndarray] = {}
        for f in range(n):
            prefixes = [t for t in level if t[-1] <= f]
            if not prefixes:
                continue
            L = matrix(f)
            X = exact_mod_matmul(np.array([rows[t] for t in prefixes]), L, p)
            for t, r in zip(prefixes, X, strict=True):
                nxt[t + (f,)] = r
            del L
        rows, level = nxt, sorted(nxt)
    return np.array([rows[t] for t in sorted(rows)])


def quotient_rank(a: argparse.Namespace, p: int, names: list[str], gens: list[np.ndarray]) -> dict:
    """r_N computed in k[t]/(J + m^N) with the basis of standard monomials of a dp standard basis."""
    n = len(names)
    htext = header_text(a.header)
    ngens = len(parse_header(a.header)[3])
    var_char = [int(sum((int(g[k]) % 2) << i for i, g in enumerate(gens))) for k in range(n)]
    blocks = list(range(2 ** len(gens)))

    def block_layout(basis: list[Monomial]) -> np.ndarray:
        if not gens:
            return np.zeros(len(basis), dtype=np.int64)
        exps = np.array(basis, dtype=np.int64)
        chars = np.stack([(exps @ g) % 2 for g in gens], axis=1)
        return chars @ np.array([2**i for i in range(len(gens))], dtype=np.int64)

    def estimate(basis: list[Monomial]) -> dict[str, int]:
        D = len(basis)
        sizes = np.bincount(block_layout(basis), minlength=len(blocks))
        cache_full = ngens * D * D * (2 if p < 2**16 else 4)
        return {
            "generator_matrix": 8 * D * D,
            "level_temporaries": 2 * 8 * D * D,
            "cache": cache_full if cache_full <= int(a.table_cache_gb * 2**30) else 0,
            "products": 2 * 8 * math.comb(ngens + a.d - 1, a.d) * D,
            "closure_tables": 8 * sum(int(sizes[b]) * int(sizes[b ^ var_char[k]]) for k in range(n) for b in blocks),
        }

    def preflight(basis: list[Monomial]) -> None:
        est = estimate(basis)
        if a.max_gb and sum(est.values()) > a.max_gb * 2**30:
            raise SystemExit(f"preflight {sum(est.values()) / 2**30:.2f} GiB exceeds --max-gb {a.max_gb}: {est}")

    t_s0 = time.time()
    basis, tables, gpolys, export = quotient_data(
        htext, names, p, a.N, a.singular, a.export_dir, a.adopt_export, a.export_chunks, preflight
    )
    t_sing = time.time() - t_s0
    if len(gpolys) != ngens:
        raise RuntimeError("Singular quotient export: generator count differs from the header")
    D = len(basis)
    bidx = {m: i for i, m in enumerate(basis)}
    block_of = block_layout(basis)
    cols = {b: np.flatnonzero(block_of == b) for b in blocks}
    pos = np.empty(D, dtype=np.int64)
    for b in blocks:
        pos[cols[b]] = np.arange(len(cols[b]))
    preflight_bytes = sum(estimate(basis).values())
    t_p0 = time.time()
    M = []
    for k in range(n):
        r_i, c_j, v = [], [], []
        for i, poly in enumerate(tables[k]):
            for m, c in poly.items():
                r_i.append(i)
                c_j.append(bidx[m])
                v.append(c)
        M.append(sp.csr_matrix((np.array(v, dtype=np.float64), (r_i, c_j)), shape=(D, D)))
    gvecs = np.zeros((len(gpolys), D))
    for f, poly in enumerate(gpolys):
        for m, c in poly.items():
            gvecs[f, bidx[m]] = c
    prod_rows = table_products(gvecs, basis, M, a.d, p, int(a.table_cache_gb * 2**30))
    t_prod = time.time() - t_p0
    mats: list[dict[int, np.ndarray]] = []
    for k in range(n):
        mk = {b: np.zeros((len(cols[b]), len(cols[b ^ var_char[k]]))) for b in blocks}
        for i, poly in enumerate(tables[k]):
            bi = int(block_of[i])
            for m, c in poly.items():
                j = bidx[m]
                if int(block_of[j]) != bi ^ var_char[k]:
                    raise RuntimeError("a multiplication table crosses character blocks; rerun with --no-split")
                mk[bi][pos[i], pos[j]] = c
        mats.append(mk)

    def dense(X: np.ndarray, b: int) -> np.ndarray:
        Y = X[:, cols[b]]
        return Y[np.any(Y != 0, axis=1)]

    t0 = time.time()
    W = {b: Echelon(len(cols[b]), p) for b in blocks}
    Q = {b: dense(prod_rows, b) for b in blocks}
    for b in blocks:
        for k in range(n):
            tb = b ^ var_char[k]
            if len(Q[b]):
                W[tb].insert(exact_mod_matmul(Q[b], mats[k][b], p), a.chunk)
    new = {b: W[b].B.copy() for b in blocks}
    rounds = 0
    while any(len(v) for v in new.values()):
        rounds += 1
        start = {b: set(W[b].piv.tolist()) for b in blocks}
        for b, rows in new.items():
            for k in range(n):
                if not len(rows):
                    continue
                tb = b ^ var_char[k]
                for s0 in range(0, len(rows), a.chunk):
                    X = exact_mod_matmul(rows[s0 : s0 + a.chunk], mats[k][b], p)
                    X = X[np.any(X != 0, axis=1)]
                    if len(X):
                        W[tb].insert(X, a.chunk)
        new = {b: W[b].B[[i for i, c in enumerate(W[b].piv.tolist()) if c not in start[b]]] for b in blocks}
    t_close = time.time() - t0
    per_block = {}
    total = 0
    for b in blocks:
        before = len(W[b].piv)
        W[b].insert(Q[b], a.chunk)
        per_block[str(b)] = {"cols": len(cols[b]), "rank_W": before, "r_N": len(W[b].piv) - before}
        total += len(W[b].piv) - before
    return {
        "mode": "quotient",
        "dim_quotient": D,
        "products": len(prod_rows),
        "preflight_bytes": preflight_bytes,
        "blocks": len(blocks),
        "closure_rounds": rounds,
        "r_N": total,
        "per_block": per_block,
        "export": export,
        "seconds": {"singular": round(t_sing, 1), "products": round(t_prod, 1), "closure": round(t_close, 1)},
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("header")
    ap.add_argument("d", type=int)
    ap.add_argument("N", type=int)
    ap.add_argument("--no-split", action="store_true")
    ap.add_argument("--chunk", type=int, default=4000)
    ap.add_argument(
        "--table-cache-gb",
        type=float,
        default=4.0,
        help="quotient mode: memory for the generator multiplication-matrix cache (uint16 below 2^16, else uint32)",
    )
    ap.add_argument(
        "--max-gb",
        type=float,
        default=0.0,
        help="quotient mode: after the Singular export, stop before the products when the selected-array estimate "
        "(generator matrix, level temporaries, cache, products, closure tables) exceeds this many GiB (0: no limit); "
        "it runs after the standard basis and before the multiplication tables, and bounds neither the export nor "
        "total RSS",
    )
    ap.add_argument(
        "--export-dir",
        help="quotient mode: keep the degree-independent export here and reuse its finished files (default: a "
        "temporary directory)",
    )
    ap.add_argument(
        "--export-chunks",
        type=int,
        default=1,
        help="quotient mode: split each variable's multiplication table into this many standard-monomial ranges, one "
        "Singular process each",
    )
    ap.add_argument(
        "--adopt-export",
        action="store_true",
        help="quotient mode: accept export files in --export-dir that carry no manifest, after checking that their "
        "q.sing script names this header, prime and N",
    )
    ap.add_argument(
        "--direct",
        action="store_true",
        help="enumerate every monomial multiple of every generator instead of the closure",
    )
    ap.add_argument("--quotient", action="store_true", help="work in k[t]/(J + m^N) from a Singular dp standard basis")
    ap.add_argument("--singular", default=os.environ.get("SINGULAR", "Singular"))
    a = ap.parse_args()
    t0 = time.time()
    p, names, j_txt, g_txt = parse_header(a.header)
    n = len(names)
    if not is_odd_prime(p):
        raise SystemExit(f"modulus {p} is not an odd prime: the character projectors need an invertible 2")
    if a.d < 0 or a.N < 1 or a.chunk < 1 or a.export_chunks < 1:
        raise SystemExit("need d >= 0, N >= 1, --chunk >= 1 and --export-chunks >= 1")
    if (a.export_dir or a.adopt_export or a.export_chunks > 1) and not a.quotient:
        raise SystemExit("--export-dir, --export-chunks and --adopt-export need --quotient")
    if a.direct and a.quotient:
        raise SystemExit("--direct and --quotient are exclusive: quotient mode has no direct enumeration")
    J = [parse_poly(s, names, p) for s in j_txt]
    G = [parse_poly(s, names, p) for s in g_txt]
    group = [] if a.no_split else sign_group([J, G], n, p)
    gens = independent_generators(group, n)
    if a.quotient:
        res = quotient_rank(a, p, names, gens)
        res.update(
            check="fiber-rank-linear-algebra",
            engine_sha256_16=ENGINE_SHA,
            header_sha256_16=hashlib.sha256(Path(a.header).read_bytes()).hexdigest()[:16],
            prime=p,
            vars=names,
            d=a.d,
            N=a.N,
            generators=len(G),
            sign_group=[[names[i] for i in fl] for fl in group],
        )
        res["seconds"]["total"] = round(time.time() - t0, 1)
        print(json.dumps(res))
        return
    space = Space(n, a.N, gens)
    gens_jet = [{m: c for m, c in g.items() if sum(m) < a.N} for g in G]
    step = functools.partial(extend_products, gens=gens_jet, names=tuple(names), p=p, N=a.N)
    # all degree-d products as jets, built along nondecreasing index tuples, one level per parallel map
    level: list[Packed] = [((), *pack({(0,) * n: 1}, a.N))]
    for _ in range(a.d):
        level = [item for chunk in parallel.ordered_map(step, level, min_items=8) for item in chunk]
    level.sort(key=lambda item: item[0])
    t_prod = time.time() - t0
    nprod = len(level)
    # consume the packed level while indexing it, so the parent holds one copy of the products: 8 bytes per term
    Psp: list[tuple[np.ndarray, np.ndarray]] = []
    level.reverse()
    while level:
        _, keys, coefs = level.pop()
        Psp.append((space.index_keys(keys), coefs))
    Jsp = [sp for sp in (space.sparse(q) for q in J) if len(sp[0])]

    def base_generators() -> Iterator[tuple[np.ndarray, np.ndarray]]:
        yield from Jsp
        for k in range(n):
            for idx, coef in Psp:
                tgt = space.shift[k][idx]
                ok = tgt >= 0
                if ok.any():
                    yield tgt[ok], coef[ok]

    def generators() -> Iterator[tuple[np.ndarray, np.ndarray]]:
        if not a.direct:
            yield from base_generators()
            return
        for idx, coef in base_generators():
            if not len(idx):
                continue
            e = space.exps[idx]
            for deg in range(a.N - int(space.deg[idx].min())):
                for mono in exps_of_degree(n, deg):
                    f = e + np.array(mono, dtype=np.int64)
                    ok = f.sum(axis=1) < a.N
                    if ok.any():
                        yield space.index(f[ok]), coef[ok]

    W = {b: Echelon(len(space.cols[b]), p) for b in space.blocks}
    new = {}
    for b in space.blocks:
        buf: list[tuple[np.ndarray, np.ndarray]] = []
        for g in itertools.chain(generators(), [None]):
            if g is not None and (space.block_of[g[0]] == b).any():
                buf.append(g)
            if len(buf) >= a.chunk or (g is None and buf):
                W[b].insert(space.dense_rows(buf, b), a.chunk)
                buf = []
        new[b] = W[b].B.copy()
    del gens_jet
    rounds = 0
    while not a.direct and any(len(v) for v in new.values()):
        rounds += 1
        start = {b: set(W[b].piv.tolist()) for b in space.blocks}
        for b, rows in new.items():
            src = space.cols[b]
            for k in range(n):
                tgt = space.shift[k][src]
                ok = tgt >= 0
                if not len(rows) or not ok.any():
                    continue
                tb = b ^ space.var_char[k]
                cols_ok, cols_tgt = np.flatnonzero(ok), space.pos[tgt[ok]]
                for s0 in range(0, len(rows), a.chunk):
                    X = np.zeros((min(a.chunk, len(rows) - s0), len(space.cols[tb])))
                    X[:, cols_tgt] = rows[s0 : s0 + a.chunk][:, cols_ok]
                    X = X[np.any(X != 0, axis=1)]
                    if len(X):
                        W[tb].insert(X, a.chunk)
        new = {}
        for b in space.blocks:
            fresh = [i for i, c in enumerate(W[b].piv.tolist()) if c not in start[b]]
            new[b] = W[b].B[fresh]
    t_close = time.time() - t0 - t_prod
    per_block = {}
    total = 0
    for b in space.blocks:
        before = len(W[b].piv)
        W[b].insert(space.dense_rows(Psp, b), a.chunk)
        per_block[str(b)] = {"cols": len(space.cols[b]), "rank_W": before, "r_N": len(W[b].piv) - before}
        total += len(W[b].piv) - before
    print(
        json.dumps(
            {
                "check": "fiber-rank-linear-algebra",
                "engine_sha256_16": ENGINE_SHA,
                "header_sha256_16": hashlib.sha256(Path(a.header).read_bytes()).hexdigest()[:16],
                "prime": p,
                "vars": names,
                "d": a.d,
                "N": a.N,
                "generators": len(G),
                "products": nprod,
                "sign_group": [[names[i] for i in fl] for fl in group],
                "blocks": len(space.blocks),
                "dim_V": len(space.exps),
                "closure_rounds": rounds,
                "direct": a.direct,
                "r_N": total,
                "per_block": per_block,
                "seconds": {
                    "products": round(t_prod, 1),
                    "closure": round(t_close, 1),
                    "total": round(time.time() - t0, 1),
                },
            }
        )
    )


if __name__ == "__main__":
    sys.setrecursionlimit(10000)
    main()
