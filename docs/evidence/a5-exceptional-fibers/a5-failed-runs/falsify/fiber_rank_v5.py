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
the normal forms of the products, and the same closure runs in that smaller space; it serves non-principal J, whose
truncated monomial space is too large to hold densely.

Every generator of span(J) and span(G) is preserved by the diagonal sign group found by exhaustive search, so the
ideal and the product span split into character blocks: a vector's projection onto a character lies in the same
ideal. Each block is echelonized separately; multiplication by t_k maps block chi to chi + chi(t_k). In quotient mode
the reduced standard basis of the invariant ideal J + m^N consists of character eigenvectors, so the multiplication
tables respect the blocks; the code checks every table entry and stops if one crosses blocks. --no-split runs one
block, as a check on the split.

Exactness: entries live in [0, p); every product X @ B runs in float64 with partial sums below (inner dimension) * p^2,
which stays below 2^53 for p < 2^15.5 and inner dimension < 8.6e6, so BLAS returns the exact integer before the
reduction modulo p. FLINT's nmod_mat.rref echelonizes the residual rows.

Usage: fiber_rank.py HEADER D N [--no-split] [--direct] [--quotient] [--chunk ROWS]
HEADER is a Singular file with lines `ring r=P,(vars),dp;`, `ideal J=...;` and `ideal G=...;`.
Prints one JSON object.
"""

from __future__ import annotations

import argparse
import functools
import hashlib
import itertools
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from collections.abc import Iterator
from pathlib import Path

import flint
import numpy as np

sys.path.insert(
    0, os.environ.get("GOROROBA_PARALLEL_DIR", str(Path(__file__).resolve().parents[3] / "gororoba_quantum"))
)
import parallel  # noqa: E402

ENGINE_SHA = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()[:16]
TERM = re.compile(r"([+-]?)([^+-]+)")


def header_text(path: str) -> dict[str, str]:
    text = open(path).read().replace("\n", "")
    j_text = re.search(r"ideal J=([^;]*);", text)
    g_text = re.search(r"ideal G=([^;]*);", text)
    if j_text is None or g_text is None:
        raise SystemExit("no ideal J or G")
    return {"J": j_text.group(1), "G": g_text.group(1)}


def parse_header(path: str) -> tuple[int, list[str], list[str], list[str]]:
    text = open(path).read().replace("\n", "")
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


def parse_poly(text: str, names: list[str], p: int) -> dict[tuple[int, ...], int]:
    idx = {v: i for i, v in enumerate(names)}
    out: dict[tuple[int, ...], int] = {}
    for sign, body in TERM.findall(text.replace(" ", "")):
        coef, e = 1, [0] * len(names)
        for f in body.split("*"):
            if f.isdigit():
                coef *= int(f)
            elif f:
                v, _, k = f.partition("^")
                e[idx[v]] += int(k) if k else 1
        key = tuple(e)
        out[key] = (out.get(key, 0) + (-coef if sign == "-" else coef)) % p
    return {k: c for k, c in out.items() if c}


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
        self.blocks = sorted(set(self.block_of.tolist()))
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
        return np.mod(X - np.mod(X[:, self.piv] @ self.B, self.p), self.p)

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
                self.B = np.mod(self.B - np.mod(self.B[:, q] @ Xr, self.p), self.p)
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


QUOTIENT_SCRIPT = """short=0;
ring r={p},({names}),dp;
ideal J={J};
ideal G={G};
option(redSB);
int t0=rtimer;
ideal s=std(J+maxideal({N}));
ideal B=kbase(s);
write(":w {out}/qB.txt",B);
int i; int k; int f; int e;
for(k=1;k<=nvars(r);k++){{ ideal Mk; for(i=1;i<=ncols(B);i++){{ Mk[i]=reduce(var(k)*B[i],s); }}
  write(":w {out}/qM"+string(k)+".txt",Mk); kill Mk; }}
for(i=1;i<=ncols(G);i++){{ G[i]=reduce(G[i],s); }}
int n=ncols(G);
ring Y={p},(y(1..n)),dp;
ideal kb=maxideal({d});
int c=ncols(kb);
setring r; ideal P; poly q; intvec ev;
for(i=1;i<=c;i++){{ setring Y; ev=leadexp(kb[i]); setring r; q=1;
  for(f=1;f<=n;f++){{ for(e=1;e<=ev[f];e++){{ q=reduce(q*G[f],s); }} }} P[i]=q; }}
write(":w {out}/qP.txt",P);
"RESULT quotient", ncols(B), c, rtimer-t0;
quit;
"""


def read_list(path: str, names: list[str], p: int) -> list[Poly]:
    text = open(path).read().replace("\n", "")
    return [parse_poly(x, names, p) if x.strip() != "0" else {} for x in text.split(",")]


def quotient_data(
    header_text: dict[str, str], names: list[str], p: int, N: int, d: int, singular: str
) -> tuple[list[Monomial], list[list[Poly]], list[Poly], float]:
    """Standard monomials of std(J + m^N) in dp, the multiplication tables of the variables, the reduced products."""
    with tempfile.TemporaryDirectory() as out:
        script = QUOTIENT_SCRIPT.format(
            p=p, names=",".join(names), J=header_text["J"], G=header_text["G"], N=N, d=d, out=out
        )
        path = os.path.join(out, "q.sing")
        open(path, "w").write(script)
        t = time.time()
        res = subprocess.run([singular, "-q", "--no-rc", path], capture_output=True, text=True, check=True)
        if "RESULT quotient" not in res.stdout:
            raise RuntimeError("Singular quotient export failed: " + res.stdout[-500:] + res.stderr[-500:])
        basis = [next(iter(q)) for q in read_list(os.path.join(out, "qB.txt"), names, p)]
        tables = [read_list(os.path.join(out, f"qM{k + 1}.txt"), names, p) for k in range(len(names))]
        prods = read_list(os.path.join(out, "qP.txt"), names, p)
        return basis, tables, prods, time.time() - t


def quotient_rank(a: argparse.Namespace, p: int, names: list[str], gens: list[np.ndarray]) -> dict:
    """r_N computed in k[t]/(J + m^N) with the basis of standard monomials of a dp standard basis."""
    n = len(names)
    basis, tables, prods, t_sing = quotient_data(header_text(a.header), names, p, a.N, a.d, a.singular)
    D = len(basis)
    bidx = {m: i for i, m in enumerate(basis)}
    exps = np.array(basis, dtype=np.int64)
    if gens:
        chars = np.stack([(exps @ g) % 2 for g in gens], axis=1)
        block_of = chars @ np.array([2**i for i in range(len(gens))], dtype=np.int64)
    else:
        block_of = np.zeros(D, dtype=np.int64)
    blocks = sorted(set(block_of.tolist()))
    cols = {b: np.flatnonzero(block_of == b) for b in blocks}
    pos = np.empty(D, dtype=np.int64)
    for b in blocks:
        pos[cols[b]] = np.arange(len(cols[b]))
    var_char = [int(sum((int(g[k]) % 2) << i for i, g in enumerate(gens))) for k in range(n)]
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

    def dense(polys: list[Poly], b: int) -> np.ndarray:
        rows = []
        for poly in polys:
            r = np.zeros(len(cols[b]))
            for m, c in poly.items():
                j = bidx[m]
                if int(block_of[j]) == b:
                    r[pos[j]] = c
            if r.any():
                rows.append(r)
        return np.array(rows) if rows else np.zeros((0, len(cols[b])))

    t0 = time.time()
    W = {b: Echelon(len(cols[b]), p) for b in blocks}
    Q = {b: dense(prods, b) for b in blocks}
    for b in blocks:
        for k in range(n):
            tb = b ^ var_char[k]
            if len(Q[b]):
                W[tb].insert(np.mod(Q[b] @ mats[k][b], p), a.chunk)
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
                    X = np.mod(rows[s0 : s0 + a.chunk] @ mats[k][b], p)
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
        "products": len(prods),
        "blocks": len(blocks),
        "closure_rounds": rounds,
        "r_N": total,
        "per_block": per_block,
        "seconds": {"singular": round(t_sing, 1), "closure": round(t_close, 1)},
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("header")
    ap.add_argument("d", type=int)
    ap.add_argument("N", type=int)
    ap.add_argument("--no-split", action="store_true")
    ap.add_argument("--chunk", type=int, default=4000)
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
    if p * p * 8.6e6 >= 2**53:
        raise SystemExit("prime too large for exact float64 reduction")
    J = [parse_poly(s, names, p) for s in j_txt]
    G = [parse_poly(s, names, p) for s in g_txt]
    group = [] if a.no_split else sign_group([J, G], n, p)
    gens = independent_generators(group, n)
    if a.quotient:
        res = quotient_rank(a, p, names, gens)
        res.update(
            check="fiber-rank-linear-algebra",
            engine_sha256_16=ENGINE_SHA,
            header_sha256_16=hashlib.sha256(open(a.header, "rb").read()).hexdigest()[:16],
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
    Jsp = [space.sparse(q) for q in J]

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
                "header_sha256_16": hashlib.sha256(open(a.header, "rb").read()).hexdigest()[:16],
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
