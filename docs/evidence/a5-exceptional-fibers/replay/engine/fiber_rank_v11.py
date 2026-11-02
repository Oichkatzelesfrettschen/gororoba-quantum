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

Block products (quotient mode). A generator of character chi maps character block b to block b + chi, so its
multiplication matrix is stored as one dense matrix per block, |b| x |b + chi|, about D^2 / 4 entries for four
balanced blocks, and filled by the order-ideal walk through the per-block sparse variable tables. Generators run in
ascending order and, within one, degrees run upward, so each prefix exists when needed and each generator's matrices
are built once and freed before the next. Each product is kept as its block and its coordinates there. The closure
multiplies by the per-block sparse variable tables directly. A generator whose normal form spans several characters
is replaced by its character components, which lie in span(G) because the sign group preserves it and together span
it; --k2-receipt indexes the original generators and refuses such a generator.

The quotient export does not depend on d. One Singular process computes the standard basis and writes it; then one
process per variable table (or per standard-monomial range of it, --export-chunks) and one for the generators run in
parallel, each reading the basis back and publishing its output only when its own kbase equals qB.txt. The parsed
export equals that of engine v8's single serial export (test_split_export_equals_serial in
tests/test_a5_fiber_rank_v9.py, where Singular is installed). --export-dir keeps them under a manifest of prime,
variables, N and the sha256 of J and G plus a sha256 record per file, so later runs at any degree, or tables computed
on another host and copied in with their .sha256 sidecars, are reused; a recomputed standard basis is published only
when its kbase equals the existing qB.txt. --adopt-export admits files without a record, copied from an engine v8
serial export, after checking its script, recomputing every adopted table at 64 evenly spaced rows and recomputing
the adopted generator normal forms; a byte change outside those rows passes adoption, so copy only files the producer
has closed. --export-only stops after the export, the barrier before a products stage. The --max-gb preflight (block
generator matrices, walk temporaries, product rows, echelon bases) runs once the basis is known, before any table.

Representatives (--k2-receipt, quotient mode). A degree-2 membership receipt of the fiber-cone driver certifies that
every quadric q of its relation file K2 satisfies q(G) in J + m * P_2 for this header and prime. Then y^b * q(y)
evaluated at G lies in J + m * P_d for every monomial y^b of degree d - 2, so each degree-d monomial in G is congruent
modulo J + m * P_d to a combination of the degree-d standard monomials of k[y]/K2 (dp standard basis of K2 in
Singular). Iterating over m * P_d shows m * P_d lies in m * span(standard products) + J, so the products restricted to
the standard monomials give the same W_N and the same r_N as all products. The standard monomials form an order ideal,
so the prefix of each one (its tuple without the largest index) is standard and the restricted products are built from
restricted prefixes. Every run also inserts nonstandard degree-d products after the rank and requires that no rank
grows: one multiple of each leading monomial of the standard basis of K2, so every basis element is probed, and an
evenly strided sample of --checks more; a mismatch of receipt, relation file, prime or generator order shows there.

Every generator of span(J) and span(G) is preserved by the diagonal sign group found by exhaustive search, so the
ideal and the product span split into character blocks: a vector's projection onto a character lies in the same
ideal. Each block is echelonized separately; multiplication by t_k maps block chi to chi + chi(t_k). In quotient mode
the reduced standard basis of the invariant ideal J + m^N consists of character eigenvectors, so the multiplication
tables respect the blocks; the code checks every table entry and stops if one crosses blocks. --no-split runs one
block, as a check on the split.

Exactness: entries live in [0, p); every product X @ B, dense or sparse, runs in float64 and checks its own inner
dimension k against k * (p - 1)^2 < 2^53 before it runs, so BLAS returns the exact integer before the reduction
modulo p. FLINT's nmod_mat.rref echelonizes the residual rows. The modulus must be an odd prime, because the
character projectors divide by the group order.

Input boundary: every polynomial must match the expanded signed-monomial grammar (signed integer coefficients, `*`
between factors, `^` before exponents, variable names from the ring line); any other string stops the run. Singular's
`write` emits that form only with `short=0` set in the current ring, which the quotient export sets before each write.

Usage: fiber_rank_v11.py HEADER D N [--no-split] [--direct] [--quotient] [--chunk ROWS] [--export-dir DIR]
    [--export-chunks C] [--adopt-export] [--export-only] [--max-gb G] [--k2-receipt RECEIPT] [--checks C]
HEADER is a Singular file with lines `ring r=P,(vars),dp;`, `ideal J=...;` and `ideal G=...;`.
Prints one JSON object.
"""

from __future__ import annotations

import argparse
import bisect
import fcntl
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
from typing import NamedTuple

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
# reduced standard basis back from s.txt and marks it with attrib(s, "isSB", 1), the documented assertion that kbase
# and reduce consult; the attribute certifies nothing about the bytes, which the sha256 records bind. Every process
# writes its own kbase, and its output is published only when that text equals qB.txt, so table rows pair with basis
# entries index for index. Default reduce returns the fully reduced normal form, unique for a standard basis in a
# global ordering, so a row range of a table equals the same rows of the whole table.
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
short=0; write(":w {basis}",B);
"""

TABLE_SCRIPT = """ideal Bh=B[{lo}..{hi}];
ideal Mk=reduce(var({k})*Bh,s);
if(ncols(Mk)!={hi}-{lo}+1){{ "? table length", ncols(Mk); quit; }}
short=0; write(":w {part}",Mk);
"RESULT table";
quit;
"""

SPOT_SCRIPT = """ideal Bh={rows};
ideal Mk=reduce(var({k})*Bh,s);
short=0; write(":w {part}",Mk);
"RESULT spot";
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
# Rows of an adopted table recomputed and compared, evenly spaced over the basis.
ADOPTION_SPOT_ROWS = 64
EXPORT_FILE = re.compile(r"^(s|qB|qG|qM\d+(\.r\d+-\d+)?)\.txt$")


class Step(NamedTuple):
    """One Singular export process. final None leaves the output staged at part for the caller to compare."""

    singular: str
    script: str
    script_path: str
    part: str
    final: str | None
    marker: str
    basis: str | None = None
    expect_basis: str | None = None
    identity: str = ""
    owner: str = ""


def read_list(path: str, names: list[str], p: int) -> list[Poly]:
    text = Path(path).read_text().replace("\n", "")
    return [parse_poly(x, names, p) if x.strip() != "0" else {} for x in text.split(",")]


def flat_text(path: str) -> str:
    return Path(path).read_text().replace("\n", "")


def file_sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def write_sidecar(source: str, final: str, identity: str) -> None:
    """final.sha256: the sha256 of source's bytes and the sha256 of the export identity."""
    with open(final + ".sha256.part", "w") as f:
        f.write(f"{file_sha256(source)} {identity}")
    os.replace(final + ".sha256.part", final + ".sha256")


def publish(part: str, final: str, identity: str) -> None:
    """Rename part to final after writing its sidecar, so every published export file has a record."""
    write_sidecar(part, final, identity)
    os.replace(part, final)


def run_singular(step: Step) -> tuple[str, float]:
    """Run one export script; publish its output only on its exact RESULT line, no diagnostic, and a matching kbase.

    The step takes a shared lock on the export directory and hands the locked descriptor to Singular, so the lock lasts
    until both the step and its Singular process have exited; a step whose owner token is no longer the directory's
    belongs to a superseded run and does nothing.
    """
    out = os.path.dirname(step.part)
    with open(os.path.join(out, ".lock"), "a") as lock:
        fcntl.flock(lock, fcntl.LOCK_SH)
        if step.owner and Path(out, ".owner").read_text() != step.owner:
            raise RuntimeError(f"Singular export step {step.part}: superseded by a later run")
        return _run_singular_locked(step, lock.fileno())


def _run_singular_locked(step: Step, lock_fd: int) -> tuple[str, float]:
    for stale in (step.part, step.basis):
        if stale and os.path.exists(stale):
            os.remove(stale)
    Path(step.script_path).write_text(step.script)
    t = time.time()
    res = subprocess.run(
        [step.singular, "-q", "--no-rc", step.script_path],
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        check=True,
        pass_fds=(lock_fd,),
    )
    lines = [ln.strip() for ln in (res.stdout + "\n" + res.stderr).splitlines()]
    ok = any(ln == step.marker or ln.startswith(step.marker + " ") for ln in lines)
    if not ok or any(ln.startswith("?") for ln in lines) or not os.path.exists(step.part):
        raise RuntimeError(f"Singular export step {step.part} failed: " + res.stdout[-500:] + res.stderr[-500:])
    if step.basis is not None and step.expect_basis is not None:
        same = flat_text(step.basis) == flat_text(step.expect_basis)
        os.remove(step.basis)
        if not same:
            raise RuntimeError(f"Singular export step {step.part}: kbase differs from {step.expect_basis}")
    if step.final is not None:
        publish(step.part, step.final, step.identity)
    return os.path.basename(step.final or step.part), time.time() - t


def run_step(step: Step) -> tuple[str, float, str | None]:
    """run_singular returning its failure instead of raising, so the caller waits for every step before it raises."""
    try:
        return (*run_singular(step), None)
    except (RuntimeError, OSError, subprocess.CalledProcessError) as e:
        return os.path.basename(step.part), 0.0, f"{type(e).__name__}: {e}"


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
        "option(redSB);",
        f"ideal s=std(J+maxideal({N}));",
    ]
    if not all(x in text for x in needed):
        raise SystemExit("--adopt-export: q.sing does not name this header's ring, J, G, redSB and N")


def identity_sha256(ident: dict) -> str:
    return hashlib.sha256(json.dumps(ident, sort_keys=True).encode()).hexdigest()


def write_manifest(mpath: str, record: dict) -> None:
    with open(mpath + ".part", "w") as f:
        json.dump(record, f)
    os.replace(mpath + ".part", mpath)


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
    variables, N, sha256 of J and G) and a sha256 record per file, and a later run at any degree reuses every finished
    file whose bytes match their record; a file computed on another host joins by being copied in with its .sha256
    sidecar. One process at a time holds the directory. preflight runs on the basis before any table is computed.
    """
    if export_dir is None:
        with tempfile.TemporaryDirectory() as tmp:
            return quotient_data(header_text, names, p, N, singular, tmp, False, chunks, preflight)
    out = os.path.abspath(export_dir)
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, ".lock"), "a") as lock:
        # Exclusive admission, then a shared hold beside the shared locks of this run's steps and their Singular
        # processes: a later run's exclusive request fails while any of them is alive. The owner token, written under
        # the exclusive lock, turns away a step of an interrupted run that starts after a later run's admission.
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise SystemExit(f"another process holds {out}") from None
        owner = f"{os.getpid()}.{time.time_ns()}"
        with open(os.path.join(out, ".owner.part"), "w") as f:
            f.write(owner)
        os.replace(os.path.join(out, ".owner.part"), os.path.join(out, ".owner"))
        fcntl.flock(lock, fcntl.LOCK_SH)
        return _quotient_data_locked(header_text, names, p, N, singular, out, adopt, chunks, preflight, owner)


def _quotient_data_locked(
    header_text: dict[str, str],
    names: list[str],
    p: int,
    N: int,
    singular: str,
    out: str,
    adopt: bool,
    chunks: int,
    preflight: Callable[[list[Monomial]], None] | None,
    owner: str = "",
) -> tuple[list[Monomial], list[list[Poly]], list[Poly], dict]:
    path = functools.partial(os.path.join, out)
    for blocker in ("qB.rejected.txt", "qB.prior.txt"):
        if os.path.exists(path(blocker)):
            raise SystemExit(
                f"{blocker} in --export-dir: an earlier recomputed kbase differed or its run stopped mid-check"
            )
    ident = export_identity(header_text, names, p, N)
    mpath = path(EXPORT_MANIFEST)
    recorded: dict = json.loads(Path(mpath).read_text()) if os.path.exists(mpath) else {}
    if recorded and {k: recorded.get(k) for k in ident} != ident:
        raise SystemExit(f"{EXPORT_MANIFEST} in --export-dir names another header, prime or N")
    files: dict[str, str] = dict(recorded.get("files", {}))
    present = sorted(f for f in os.listdir(out) if EXPORT_FILE.match(f))
    # A file without a record stays pending, out of the manifest, until its recomputation agrees, so every retry
    # verifies it again.
    pending = []
    identity = identity_sha256(ident)
    for f in present:
        sidecar = path(f + ".sha256")
        want = files.get(f)
        if want is None and os.path.exists(sidecar):
            want, _, producer = Path(sidecar).read_text().strip().partition(" ")
            if producer != identity:
                raise SystemExit(f"{f}.sha256 in --export-dir names another header, prime or N")
        got = file_sha256(path(f))
        if want is None:
            pending.append(f)
        elif got != want:
            raise SystemExit(f"{f} in --export-dir differs from its recorded sha256")
        else:
            files[f] = got
    if pending:
        if not adopt:
            raise SystemExit(f"--export-dir holds export files without a sha256 record {pending}; check them and pass "
                             "--adopt-export")  # fmt: skip
        if "s.txt" in pending or ("qB.txt" in pending and os.path.exists(path("s.txt"))):
            raise SystemExit("--adopt-export verifies qB.txt by recomputing s.txt, so s.txt cannot be adopted")
        if any(re.match(r"qM\d+\.r", f) for f in pending):
            raise SystemExit("--adopt-export admits whole engine v8 tables; a row-range file needs its .sha256 sidecar")
        adopt_serial_export(out, header_text, names, p, N)
    write_manifest(mpath, {**ident, "files": files, "adopted": recorded.get("adopted", [])})
    adopted = sorted(set(pending) | set(recorded.get("adopted", [])))
    nv, base = len(names), {"p": p, "names": ",".join(names), "out": out}
    computed: dict[str, float] = {}
    reused = [f for f in present if not re.match(r"qM\d+\.r", f)]
    if os.path.exists(path("s.txt")) and not os.path.exists(path("qB.txt")):
        raise SystemExit("--export-dir holds s.txt without qB.txt")
    if not os.path.exists(path("s.txt")):
        std_step = Step(singular, STD_SCRIPT.format(J=header_text["J"], N=N, **base), path("std.sing"),
                    path("s.txt.part"), None, "RESULT std", owner=owner)  # fmt: skip
        computed["s.txt"] = round(run_singular(std_step)[1], 1)
        if os.path.exists(path("qB.txt")):
            # A recomputed standard basis must reproduce the basis the existing files were written against.
            if flat_text(path("qB.txt.part")) != flat_text(path("qB.txt")):
                os.replace(path("qB.txt.part"), path("qB.rejected.txt"))
                os.remove(path("s.txt.part"))
                raise SystemExit("recomputed kbase differs from the qB.txt in --export-dir (kept as qB.rejected.txt)")
            publish(path("qB.txt.part"), path("qB.txt"), identity)
            pending = [f for f in pending if f != "qB.txt"]
        else:
            publish(path("qB.txt.part"), path("qB.txt"), identity)
        publish(path("s.txt.part"), path("s.txt"), identity)
        reused = [f for f in reused if f != "s.txt"]
    basis = [next(iter(q)) for q in read_list(path("qB.txt"), names, p)]
    D = len(basis)
    if preflight is not None:
        preflight(basis)

    def load(tag: str) -> str:
        return LOAD_SCRIPT.format(basis=path(tag + ".kbase.part"), **base)

    def checked(script: str, tag: str, final: str | None, marker: str) -> Step:
        return Step(singular, script, path(tag + ".sing"), path(tag + ".txt.part"), final, marker,
                    path(tag + ".kbase.part"), path("qB.txt"), identity, owner)  # fmt: skip

    jobs, joins, checks = [], [], []
    bounds = [(1 + i * D // chunks, (i + 1) * D // chunks) for i in range(chunks)]
    bounds = [(lo, hi) for lo, hi in bounds if lo <= hi]
    spots = sorted({1 + i * (D - 1) // (ADOPTION_SPOT_ROWS - 1) for i in range(ADOPTION_SPOT_ROWS)}) if D > 1 else [1]
    for k in range(1, nv + 1):
        final = path(f"qM{k}.txt")
        if os.path.exists(final):
            if f"qM{k}.txt" in pending:
                rows = ",".join(f"B[{i}]" for i in spots)
                script = load(f"qM{k}.spot") + SPOT_SCRIPT.format(k=k, rows=rows, part=path(f"qM{k}.spot.txt.part"))
                jobs.append(checked(script, f"qM{k}.spot", None, "RESULT spot"))
                checks.append((k, path(f"qM{k}.spot.txt.part")))
            continue
        # A part's name carries its row bounds, so a rerun with another chunk count reuses only identical ranges.
        parts = [path(f"qM{k}.r{lo}-{hi}.txt") if chunks > 1 else final for lo, hi in bounds]
        for (lo, hi), part in zip(bounds, parts, strict=True):
            if not os.path.exists(part):
                stem = part[:-4]
                script = load(stem) + TABLE_SCRIPT.format(k=k, lo=lo, hi=hi, part=part + ".part")
                jobs.append(Step(singular, script, stem + ".sing", part + ".part", part, "RESULT table",
                                 stem + ".kbase.part", path("qB.txt"), identity, owner))  # fmt: skip
        if chunks > 1:
            joins.append((final, parts))
    gen_check = None
    if not os.path.exists(path("qG.txt")):
        script = load("qG") + GENERATOR_SCRIPT.format(G=header_text["G"], N=N, part=path("qG.txt.part"))
        jobs.append(checked(script, "qG", path("qG.txt"), "RESULT generators"))
    elif "qG.txt" in pending:
        gen_check = path("qG.check.txt.part")
        script = load("qG.check") + GENERATOR_SCRIPT.format(G=header_text["G"], N=N, part=gen_check)
        jobs.append(checked(script, "qG.check", None, "RESULT generators"))
    # Every step finishes before any failure raises, so no worker still writes once the directory lock is released.
    failures = []
    for name, seconds, error in parallel.ordered_map(run_step, jobs, min_items=2):
        if error is None:
            computed[name] = round(seconds, 1)
        else:
            failures.append(f"{name}: {error}")
    if failures:
        raise RuntimeError("Singular export steps failed: " + "; ".join(failures))
    for final, parts in joins:
        with open(final + ".part", "w") as joined:
            joined.write(",".join(flat_text(q) for q in parts))
        publish(final + ".part", final, identity)
        for q in parts:
            os.remove(q)
            os.remove(q + ".sha256")
    tables = [read_list(path(f"qM{k + 1}.txt"), names, p) for k in range(nv)]
    gens = read_list(path("qG.txt"), names, p)
    # The reader pairs table rows with basis entries by index, so each table keeps its zero normal forms in place.
    if any(len(tab) != D for tab in tables):
        raise RuntimeError("Singular quotient export: a multiplication table length differs from the basis size")
    for k, spot in checks:
        if read_list(spot, names, p) != [tables[k - 1][i - 1] for i in spots]:
            raise SystemExit(f"adopted qM{k}.txt differs from recomputed rows {spots[0]}..{spots[-1]}")
        os.remove(spot)
    if gen_check is not None:
        if read_list(gen_check, names, p) != gens:
            raise SystemExit("adopted qG.txt differs from the recomputed generator normal forms")
        os.remove(gen_check)
    for f in pending:
        write_sidecar(path(f), path(f), identity)
    names_out = ["s.txt", "qB.txt", "qG.txt"] + [f"qM{k}.txt" for k in range(1, nv + 1)]
    files = {f: file_sha256(path(f)) for f in names_out}
    write_manifest(mpath, {**ident, "files": files, "adopted": adopted})
    info = {"reused": reused, "computed_seconds": computed, "chunks": chunks, "adopted": adopted,
            "adoption_spot_rows": len(spots) if checks else 0,
            "files_sha256_16": {f: h[:16] for f, h in files.items()}}  # fmt: skip
    return basis, tables, gens, info


def sparse_mod_matmul(X: np.ndarray, S: sp.csr_matrix, p: int) -> np.ndarray:
    """X @ S mod p for dense X and sparse S with entries in [0, p); each output sums at most S.shape[0] products below
    p^2, exact in float64 under the same inner-dimension guard as exact_mod_matmul."""
    if S.shape[0] * (p - 1) ** 2 >= 2**53:
        raise ValueError(f"sparse product not exact in float64: inner dimension {S.shape[0]} at p = {p}")
    if X.shape[0] == 0 or S.shape[1] == 0:
        return np.zeros((X.shape[0], S.shape[1]))
    return np.mod(np.asarray((S.T @ X.T).T), p)


class Blocks(NamedTuple):
    """Character-block layout of the standard monomials: block of each monomial, its position inside the block, the
    members of each block, and the sparse variable tables Mb[k][b] from block b to block b ^ var_char[k]."""

    block_of: np.ndarray
    pos: np.ndarray
    cols: dict[int, np.ndarray]
    var_char: list[int]
    Mb: list[dict[int, sp.csr_matrix]]


def block_tables(
    tables: list[list[Poly]],
    bidx: dict[Monomial, int],
    lay_block_of: np.ndarray,
    var_char: list[int],
    blocks: list[int],
) -> Blocks:
    """Split each variable's multiplication table into per-block sparse maps; stop if an entry crosses blocks."""
    D = len(lay_block_of)
    cols = {b: np.flatnonzero(lay_block_of == b) for b in blocks}
    pos = np.empty(D, dtype=np.int64)
    for b in blocks:
        pos[cols[b]] = np.arange(len(cols[b]))
    Mb = []
    for k, table in enumerate(tables):
        trip: dict[int, tuple[list[int], list[int], list[int]]] = {b: ([], [], []) for b in blocks}
        for i, poly in enumerate(table):
            bi = int(lay_block_of[i])
            for m, c in poly.items():
                j = bidx[m]
                if int(lay_block_of[j]) != bi ^ var_char[k]:
                    raise RuntimeError("a multiplication table crosses character blocks; rerun with --no-split")
                trip[bi][0].append(int(pos[i]))
                trip[bi][1].append(int(pos[j]))
                trip[bi][2].append(c)
        Mb.append(
            {
                b: sp.csr_matrix(
                    (np.array(trip[b][2], dtype=np.float64), (trip[b][0], trip[b][1])),
                    shape=(len(cols[b]), len(cols[b ^ var_char[k]])),
                )
                for b in blocks
            }
        )
    return Blocks(lay_block_of, pos, cols, var_char, Mb)


def order_walk(basis: list[Monomial], lay: Blocks) -> list[tuple[int, int, np.ndarray, np.ndarray]]:
    """Fill order for generator matrices: groups (k, block b, kid positions in b, parent positions in b ^ var_char[k]).

    The standard monomials of a dp standard basis form an order ideal, so every B != 1 has a parent B / t_k in the
    basis; groups are listed level by level in total degree, so each parent row is filled before its kids."""
    idx = {m: i for i, m in enumerate(basis)}
    one = tuple(0 for _ in basis[0])
    if one not in idx:
        raise RuntimeError("the constant monomial is not standard")
    levels: dict[int, list[int]] = {}
    for i, m in enumerate(basis):
        levels.setdefault(sum(m), []).append(i)
    walk = []
    for deg in sorted(levels):
        if deg == 0:
            continue
        groups: dict[tuple[int, int], tuple[list[int], list[int]]] = {}
        for i in levels[deg]:
            m = basis[i]
            k = next(k for k, e in enumerate(m) if e and tuple(x - (j == k) for j, x in enumerate(m)) in idx)
            parent = idx[tuple(x - (j == k) for j, x in enumerate(m))]
            g = groups.setdefault((k, int(lay.block_of[i])), ([], []))
            g[0].append(int(lay.pos[i]))
            g[1].append(int(lay.pos[parent]))
        for (k, b), (kids, parents) in groups.items():
            walk.append((k, b, np.array(kids, dtype=np.int64), np.array(parents, dtype=np.int64)))
    return walk


def generator_blocks(
    g: np.ndarray, chi: int, one_pos: int, walk: list[tuple[int, int, np.ndarray, np.ndarray]], lay: Blocks, p: int
) -> dict[int, np.ndarray]:
    """Multiplication by a generator of character chi, per block: L[b] has row i = coordinates (in block b ^ chi) of
    g * (i-th standard monomial of block b); row-vector convention, x @ L[b] = x * g for x supported in block b.

    Row(B) = row(B / t_k) @ M_k, with the parent in block b ^ var_char[k] and the table restricted from block
    b ^ var_char[k] ^ chi to block b ^ chi."""
    L = {b: np.zeros((len(lay.cols[b]), len(lay.cols[b ^ chi]))) for b in lay.cols}
    L[0][one_pos] = g[lay.cols[chi]]
    for k, b, kids, parents in walk:
        pb = b ^ lay.var_char[k]
        L[b][kids] = sparse_mod_matmul(L[pb][parents], lay.Mb[k][pb ^ chi], p)
    return L


def block_products(
    gvecs: np.ndarray,
    gchar: list[int],
    one_pos: int,
    walk: list[tuple[int, int, np.ndarray, np.ndarray]],
    lay: Blocks,
    d: int,
    p: int,
    wanted: dict[int, set[tuple[int, ...]]] | None = None,
) -> dict[tuple[int, ...], tuple[int, np.ndarray]]:
    """Degree-d monomials in the generators as (block, coordinates in that block), one generator matrix at a time.

    A monomial is a sorted index tuple; its row is the row of its prefix (the tuple without its last, largest index f)
    times generator f's block matrix. Generators run in ascending order and, within one generator, degrees run upward,
    so every prefix exists when it is needed and each generator's block matrices are built exactly once. wanted maps
    each degree 1..d to the tuples to build (all when None); each wanted tuple's prefix must be wanted one degree
    lower. Degree zero is the single product 1."""
    n = len(gvecs)
    if d == 0:
        one = np.zeros(len(lay.cols[0]))
        one[one_pos] = 1
        return {(): (0, one)}

    def keep(t: tuple[int, ...]) -> bool:
        return wanted is None or t in wanted[len(t)]

    rows: dict[tuple[int, ...], tuple[int, np.ndarray]] = {}
    for f in range(n):
        if keep((f,)):
            rows[(f,)] = (gchar[f], gvecs[f][lay.cols[gchar[f]]].copy())
    for f in range(n):
        if d == 1:
            break
        L: dict[int, np.ndarray] | None = None
        for level in range(1, d):
            prefixes = [t for t in rows if len(t) == level and t[-1] <= f and keep(t + (f,))]
            if not prefixes:
                continue
            if L is None:
                L = generator_blocks(gvecs[f], gchar[f], one_pos, walk, lay, p)
            by_block: dict[int, list[tuple[int, ...]]] = {}
            for t in prefixes:
                by_block.setdefault(rows[t][0], []).append(t)
            for beta, ts in by_block.items():
                X = exact_mod_matmul(np.array([rows[t][1] for t in ts]), L[beta], p)
                for t, r in zip(ts, X, strict=True):
                    rows[t + (f,)] = (beta ^ gchar[f], r)
        del L
    return {t: v for t, v in rows.items() if len(t) == d}


class Representatives(NamedTuple):
    wanted: dict[int, set[tuple[int, ...]]]
    reps: list[tuple[int, ...]]
    checks: list[tuple[int, ...]]
    record: dict


def exps_to_tuple(e: list[int]) -> tuple[int, ...]:
    return tuple(i for i, x in enumerate(e) for _ in range(x))


def load_receipt(path: str, header: str, p: int, ngens: int) -> tuple[str, dict]:
    """The relation file of a degree-2 membership receipt that certifies this header at this prime, and the receipt."""
    rec = json.loads(Path(path).read_text())
    # Retained receipts record relation_file either beside the receipt or relative to the repository root; the file
    # sits beside the receipt in both spellings.
    rel = os.path.join(os.path.dirname(path), os.path.basename(rec["relation_file"]))
    want = {
        "status": "degree-certified",
        "degree": 2,
        "prime": p,
        "generator_count": ngens,
        "input_sha256": hashlib.sha256(Path(header).read_bytes()).hexdigest(),
        "relation_sha256": hashlib.sha256(Path(rel).read_bytes()).hexdigest(),
    }
    bad = {k: (rec.get(k), v) for k, v in want.items() if rec.get(k) != v}
    if bad:
        raise SystemExit(f"receipt {path} does not certify this run: {bad}")
    return rel, rec


def standard_monomials(
    rel: str, rec: dict, ngens: int, p: int, d: int, singular: str
) -> tuple[dict[int, list[list[int]]], list[list[int]]]:
    """Exponent vectors of the standard monomials of degrees 1..d of k[y]/K2 and of the leading monomials of degree at
    most d of its reduced dp standard basis, from Singular."""
    body = Path(rel).read_text().strip().rstrip(",")
    with tempfile.TemporaryDirectory(prefix="k2kb-") as tmp:
        script = os.path.join(tmp, "kb.sing")
        out = os.path.join(tmp, "kb.txt")
        Path(script).write_text(
            f"ring Y={p},(y(1..{ngens})),dp;\noption(redSB);\nideal K={body};\n"
            f'if (ncols(K) != {rec["relation_count"]}) {{ ERROR("relation count"); }}\n'
            "K=std(K);\nint e; int i; ideal kb; string s;\n"
            f"for (e=1; e<={d}; e++) {{ kb=kbase(K,e); for (i=1; i<=ncols(kb); i++) {{ if (kb[i] != 0) {{ "
            f's = s + string(e) + ":" + string(leadexp(kb[i])) + newline; }} }} }}\n'
            f"for (i=1; i<=ncols(K); i++) {{ if (K[i] != 0 && deg(K[i]) <= {d}) {{ "
            's = s + "L:" + string(leadexp(K[i])) + newline; } }\n'
            f'write(":w {out}", s);\nprint("K2KB-DONE");\nquit;\n'
        )
        res = subprocess.run(
            [singular, "-q", "--no-rc", script], stdin=subprocess.DEVNULL, capture_output=True, text=True, check=True
        )
        lines = [ln.strip() for ln in (res.stdout + "\n" + res.stderr).splitlines()]
        if "K2KB-DONE" not in lines or any(ln.startswith("?") for ln in lines):
            raise RuntimeError("Singular kbase of K2 failed: " + res.stdout[-500:] + res.stderr[-500:])
        levels: dict[int, list[list[int]]] = {e: [] for e in range(1, d + 1)}
        leads: list[list[int]] = []
        for ln in Path(out).read_text().split():
            e, exps = ln.split(":")
            v = [int(x) for x in exps.split(",")]
            if e == "L":
                if len(v) != ngens or not 1 <= sum(v) <= d:
                    raise RuntimeError(f"leading-monomial line {ln!r} is not a monomial of degree 1..{d}")
                leads.append(v)
                continue
            if len(v) != ngens or sum(v) != int(e):
                raise RuntimeError(f"kbase line {ln!r} is not a degree-{e} monomial in {ngens} variables")
            levels[int(e)].append(v)
    return levels, leads


def combo_rank(t: tuple[int, ...], n: int) -> int:
    """Position of the nondecreasing tuple t in itertools.combinations_with_replacement(range(n), len(t))."""
    d, m = len(t), n + len(t) - 1
    r, prev = 0, -1
    for i, x in enumerate(t):
        s = x + i
        r += sum(math.comb(m - 1 - v, d - 1 - i) for v in range(prev + 1, s))
        prev = s
    return r


def combo_unrank(r: int, n: int, d: int) -> tuple[int, ...]:
    """Inverse of combo_rank."""
    m = n + d - 1
    out, v = [], 0
    for i in range(d):
        while math.comb(m - 1 - v, d - 1 - i) <= r:
            r -= math.comb(m - 1 - v, d - 1 - i)
            v += 1
        out.append(v - i)
        v += 1
    return tuple(out)


def nonstandard_at(j: int, std_ranks: list[int]) -> int:
    """Rank of the j-th (from 0) tuple outside the sorted standard ranks: the least fixed point of r = j + #{s <= r}."""
    r = j
    while True:
        nxt = j + bisect.bisect_right(std_ranks, r)
        if nxt == r:
            return r
        r = nxt


def representatives(a: argparse.Namespace, p: int, ngens: int) -> Representatives:
    """Standard-monomial product tuples of k[y]/K2 for degrees 1..d, plus the nonstandard check products.

    The checks are one product per leading monomial of the standard basis of K2 (that monomial times the lowest
    variable to degree d), so each basis element is probed, followed by an evenly strided sample of --checks others.
    """
    rel, rec = load_receipt(a.k2_receipt, a.header, p, ngens)
    levels, leads = standard_monomials(rel, rec, ngens, p, a.d, a.singular)
    std_sets = {e: {exps_to_tuple(v) for v in vs} for e, vs in levels.items()}
    for e in range(2, a.d + 1):
        for t in std_sets[e]:
            if t[:-1] not in std_sets[e - 1]:
                raise RuntimeError(f"standard monomial {t} has a nonstandard prefix: kbase is not an order ideal")
    reps = sorted(std_sets[a.d])
    std_ranks = sorted(combo_rank(t, ngens) for t in std_sets[a.d])
    nonstd_count = math.comb(ngens + a.d - 1, a.d) - len(std_ranks)
    targeted = sorted({tuple(sorted(exps_to_tuple(v) + (0,) * (a.d - sum(v)))) for v in leads})
    if any(t in std_sets[a.d] for t in targeted):
        raise RuntimeError("a multiple of a leading monomial of K2 is standard: kbase and lead disagree")
    take = min(a.checks, nonstd_count)
    strided = [combo_unrank(nonstandard_at((i * nonstd_count) // take, std_ranks), ngens, a.d) for i in range(take)]
    checks = targeted + [t for t in dict.fromkeys(strided) if t not in set(targeted)]
    wanted = {e: set(std_sets[e]) for e in std_sets}
    for t in checks:
        for e in range(1, a.d + 1):
            wanted[e].add(t[:e])
    record = {
        "receipt_sha256": hashlib.sha256(Path(a.k2_receipt).read_bytes()).hexdigest(),
        "relation_sha256": rec["relation_sha256"],
        "generator_order_sha256": rec["generator_order_sha256"],
        "standard_counts": {str(e): len(std_sets[e]) for e in sorted(std_sets)},
        "built_rows": {str(e): len(wanted[e]) for e in sorted(wanted)},
        "nonstandard": nonstd_count,
        "checks_targeted": len(targeted),
        "checks_strided": len(checks) - len(targeted),
    }
    return Representatives(wanted, reps, checks, record)


def quotient_rank(a: argparse.Namespace, p: int, names: list[str], gens: list[np.ndarray]) -> dict:
    """r_N computed in k[t]/(J + m^N) with the basis of standard monomials of a dp standard basis."""
    n = len(names)
    htext = header_text(a.header)
    ngens = len(parse_header(a.header)[3])
    rset = representatives(a, p, ngens) if a.k2_receipt else None
    nprod = len(rset.reps) + len(rset.checks) if rset else math.comb(ngens + a.d - 1, a.d)
    var_char = [int(sum((int(g[k]) % 2) << i for i, g in enumerate(gens))) for k in range(n)]
    blocks = list(range(2 ** len(gens)))

    def block_layout(basis: list[Monomial]) -> np.ndarray:
        if not gens:
            return np.zeros(len(basis), dtype=np.int64)
        exps = np.array(basis, dtype=np.int64)
        chars = np.stack([(exps @ g) % 2 for g in gens], axis=1)
        return chars @ np.array([2**i for i in range(len(gens))], dtype=np.int64)

    def estimate(basis: list[Monomial]) -> dict[str, int]:
        sizes = np.bincount(block_layout(basis), minlength=len(blocks))
        widest = int(sizes.max())
        gen_blocks = max(sum(int(sizes[b]) * int(sizes[b ^ c]) for b in blocks) for c in blocks)
        rows = nprod + sum(len(v) for e, v in rset.wanted.items() if e < a.d) if rset else 2 * nprod
        return {
            "generator_blocks": 8 * gen_blocks,
            "walk_temporaries": 2 * 8 * gen_blocks // len(blocks),
            "product_rows": 2 * 8 * rows * widest,
            "echelon_bases": 2 * 8 * sum(int(sizes[b]) ** 2 for b in blocks),
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
    if a.export_only:
        return {
            "mode": "quotient-export",
            "dim_quotient": D,
            "export": export,
            "seconds": {"singular": round(t_sing, 1)},
        }
    bidx = {m: i for i, m in enumerate(basis)}
    block_of = block_layout(basis)
    cols = {b: np.flatnonzero(block_of == b) for b in blocks}
    pos = np.empty(D, dtype=np.int64)
    for b in blocks:
        pos[cols[b]] = np.arange(len(cols[b]))
    preflight_bytes = sum(estimate(basis).values())
    t_p0 = time.time()
    lay = block_tables(tables, bidx, block_of, var_char, blocks)
    del tables
    gvecs = np.zeros((len(gpolys), D))
    for f, poly in enumerate(gpolys):
        for m, c in poly.items():
            gvecs[f, bidx[m]] = c
    del gpolys
    # The sign group preserves span(G), so each character component of a generator lies in span(G) and the components
    # span it; products of the components span the products of G. A receipt indexes the original generators, so a
    # restricted run needs every generator to be a single character.
    comps: list[tuple[np.ndarray, int]] = []
    for f in range(len(gvecs)):
        found = sorted(set(block_of[np.flatnonzero(gvecs[f])].tolist())) or [0]
        if len(found) > 1 and rset:
            raise SystemExit(f"generator {f + 1} spans character blocks {found}: --k2-receipt needs pure characters")
        for c in found:
            v = np.zeros(D)
            v[cols[c]] = gvecs[f][cols[c]]
            comps.append((v, c))
    gvecs = np.array([v for v, _ in comps])
    gchar = [c for _, c in comps]
    one_pos = int(lay.pos[bidx[tuple(0 for _ in basis[0])]])
    walk = order_walk(basis, lay)
    built = block_products(gvecs, gchar, one_pos, walk, lay, a.d, p, rset.wanted if rset else None)
    del walk

    def stack(built: dict[tuple[int, ...], tuple[int, np.ndarray]], ts: list[tuple[int, ...]], b: int) -> np.ndarray:
        Y = np.array([built[t][1] for t in ts if built[t][0] == b]).reshape(-1, len(cols[b]))
        return Y[np.any(Y != 0, axis=1)]

    rep_tuples = rset.reps if rset else sorted(built)
    nproducts = len(rep_tuples)
    Q = {b: stack(built, rep_tuples, b) for b in blocks}
    C = {b: stack(built, rset.checks, b) for b in blocks} if rset else {}
    del built
    t_prod = time.time() - t_p0
    dense_bytes = 8 * sum(m.shape[0] * m.shape[1] for mk in lay.Mb for m in mk.values())
    dense_closure = dense_bytes <= a.dense_tables_gb * 2**30
    mats: list[dict[int, np.ndarray | sp.csr_matrix]] = (
        [{b: m.toarray() for b, m in mk.items()} for mk in lay.Mb] if dense_closure else list(lay.Mb)
    )

    def table_mul(X: np.ndarray, T: np.ndarray | sp.csr_matrix) -> np.ndarray:
        return exact_mod_matmul(X, T, p) if isinstance(T, np.ndarray) else sparse_mod_matmul(X, T, p)

    t0 = time.time()
    W = {b: Echelon(len(cols[b]), p) for b in blocks}
    for b in blocks:
        for k in range(n):
            tb = b ^ var_char[k]
            if len(Q[b]):
                W[tb].insert(table_mul(Q[b], mats[k][b]), a.chunk)
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
                    X = table_mul(rows[s0 : s0 + a.chunk], mats[k][b])
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
    checks = None
    if rset:
        grown = {}
        for b in blocks:
            before = len(W[b].piv)
            W[b].insert(C[b], a.chunk)
            if len(W[b].piv) != before:
                grown[str(b)] = len(W[b].piv) - before
        checks = {"count": len(rset.checks), "rank_growth": grown}
        if grown:
            raise SystemExit(f"nonstandard products raise the rank in blocks {grown}: the receipt does not hold here")
    return {
        "mode": "quotient",
        "representatives": rset.record if rset else None,
        "checks": checks,
        "dim_quotient": D,
        "products": nproducts,
        "generator_components": len(gchar),
        "preflight_bytes": preflight_bytes,
        "blocks": len(blocks),
        "closure_rounds": rounds,
        "closure_tables": "dense" if dense_closure else "sparse",
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
        "--max-gb",
        type=float,
        default=0.0,
        help="quotient mode: after the Singular export, stop before the products when the selected-array estimate "
        "(block generator matrices, walk temporaries, product rows, echelon bases) exceeds this many GiB "
        "(0: no limit); "
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
        "--export-only",
        action="store_true",
        help="quotient mode: finish and verify the export in --export-dir, then stop before the products",
    )
    ap.add_argument(
        "--direct",
        action="store_true",
        help="enumerate every monomial multiple of every generator instead of the closure",
    )
    ap.add_argument(
        "--dense-tables-gb",
        type=float,
        default=0.0,
        help="quotient mode: densify the per-block variable tables for the closure when they fit in this many GiB "
        "(dense BLAS products); otherwise the closure multiplies by the sparse tables",
    )
    ap.add_argument("--quotient", action="store_true", help="work in k[t]/(J + m^N) from a Singular dp standard basis")
    ap.add_argument(
        "--k2-receipt",
        help="quotient mode: degree-2 membership receipt (receipt-d2.json beside its relation file); build only the "
        "products indexed by the standard monomials of k[y]/K2",
    )
    ap.add_argument(
        "--checks",
        type=int,
        default=64,
        help="with --k2-receipt: evenly strided nonstandard degree-d products inserted after the rank beside one "
        "multiple of each leading monomial of K2; none may raise it",
    )
    ap.add_argument("--singular", default=os.environ.get("SINGULAR", "Singular"))
    a = ap.parse_args()
    t0 = time.time()
    p, names, j_txt, g_txt = parse_header(a.header)
    n = len(names)
    if not is_odd_prime(p):
        raise SystemExit(f"modulus {p} is not an odd prime: the character projectors need an invertible 2")
    if a.d < 0 or a.N < 1 or a.chunk < 1 or a.export_chunks < 1:
        raise SystemExit("need d >= 0, N >= 1, --chunk >= 1 and --export-chunks >= 1")
    if (a.export_dir or a.adopt_export or a.export_chunks > 1 or a.export_only) and not a.quotient:
        raise SystemExit("--export-dir, --export-chunks, --adopt-export and --export-only need --quotient")
    if a.k2_receipt and not a.quotient:
        raise SystemExit("--k2-receipt needs --quotient")
    if a.k2_receipt and (a.d < 1 or a.checks < 0):
        raise SystemExit("--k2-receipt needs d >= 1 and --checks >= 0")
    if a.export_only and not a.export_dir:
        raise SystemExit("--export-only needs --export-dir")
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
