"""Hilbert-cell certificate export (schema a5-hilbert-cell-certificate-v1) for one raw-mode cell.

The module reuses the fiber_rank_v8 raw-mode pipeline unchanged (Space, Echelon, parse_poly, sign_group,
extend_products) and writes, for one header, one degree d and one truncation N, the data of the quotient module
Q = V/W with V = F_p[t]/m^N and W the image of the ideal (J, m P_d): the basis of Q, the matrix M_k of
multiplication by t_k, the class e of 1, a level function, and r selected degree-d product classes with a left
inverse.

Conventions. Every field element is an integer in [0, p). A vector of Q is a column over the global basis. M_k[row, col]
is the coefficient of basis[row] in t_k * basis[col] reduced modulo W. The class of a polynomial g is g(M) e, with e the
class of 1. The basis lists, block by block in increasing character-block index, the non-pivot columns of the reduced
row echelon form of W in the engine's column order (degree ascending, then Space order). A row of W pivots on its
lowest column, so a reduced term of t_k * b lies in a column of degree at least deg b + 1, and level = degree strictly
increases along every nonzero entry. left_inverse[i][c] satisfies sum_c left_inverse[i][c] * v_j[c] = delta_ij for the
class vectors v_j of the selected products.

Usage: fiber_cell_certificate_v1.py HEADER D N OUT.json --ledger-id ID --fiber NAME --h-claimed H [--header-path PATH]
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
import json
import platform
import sys
import time
from pathlib import Path

import flint
import numpy as np

SCHEMA = "a5-hilbert-cell-certificate-v1"
HERE = Path(__file__).resolve().parent


def load_engine():
    spec = importlib.util.spec_from_file_location("fiber_rank_v8", HERE / "fiber_rank_v8.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["fiber_rank_v8"] = mod
    spec.loader.exec_module(mod)
    return mod


def reduce_rows(W, b, rows, p):
    """Reduce dense rows of block b against the reduced echelon form of W[b]."""
    return W[b].reduce(np.array(rows, dtype=np.float64).reshape(-1, W[b].ncols))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("header")
    ap.add_argument("d", type=int)
    ap.add_argument("N", type=int)
    ap.add_argument("out")
    ap.add_argument("--ledger-id", required=True)
    ap.add_argument("--fiber", required=True)
    ap.add_argument("--h-claimed", type=int, required=True)
    ap.add_argument("--header-path", default=None, help="repository-relative path recorded in the file")
    ap.add_argument("--chunk", type=int, default=4000)
    a = ap.parse_args()
    eng = load_engine()
    t0 = time.time()
    p, names, j_txt, g_txt = eng.parse_header(a.header)
    n = len(names)
    if not eng.is_odd_prime(p):
        raise SystemExit(f"modulus {p} is not an odd prime")
    J = [eng.parse_poly(s, names, p) for s in j_txt]
    G = [eng.parse_poly(s, names, p) for s in g_txt]
    group = eng.sign_group([J, G], n, p)
    space = eng.Space(n, a.N, eng.independent_generators(group, n))
    N = a.N
    # all degree-d products as jets, nondecreasing index tuples, in the engine's order
    gens_jet = [{m: c for m, c in g.items() if sum(m) < N} for g in G]
    level = [((), *eng.pack({(0,) * n: 1}, N))]
    for _ in range(a.d):
        nxt = []
        for item in level:
            nxt.extend(eng.extend_products(item, gens_jet, tuple(names), p, N))
        level = nxt
    level.sort(key=lambda item: item[0])
    prod_tuples = [item[0] for item in level]
    Psp = [(space.index_keys(keys), coefs) for _, keys, coefs in level]
    Jsp = [s for s in (space.sparse(q) for q in J) if len(s[0])]

    def base_generators():
        yield from Jsp
        for k in range(n):
            for idx, coef in Psp:
                tgt = space.shift[k][idx]
                ok = tgt >= 0
                if ok.any():
                    yield tgt[ok], coef[ok]

    W = {b: eng.Echelon(len(space.cols[b]), p) for b in space.blocks}
    new = {}
    for b in space.blocks:
        buf = []
        for g in itertools.chain(base_generators(), [None]):
            if g is not None and (space.block_of[g[0]] == b).any():
                buf.append(g)
            if len(buf) >= a.chunk or (g is None and buf):
                W[b].insert(space.dense_rows(buf, b), a.chunk)
                buf = []
        new[b] = W[b].B.copy()
    rounds = 0
    while any(len(v) for v in new.values()):
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
    # global quotient basis: non-pivot columns per block, blocks in increasing index
    basis_mon: list[int] = []
    basis_of_mon: dict[int, int] = {}
    free_cols = {}
    for b in space.blocks:
        free = np.setdiff1d(np.arange(len(space.cols[b])), W[b].piv)
        free_cols[b] = free
        for c in free.tolist():
            mi = int(space.cols[b][c])
            basis_of_mon[mi] = len(basis_mon)
            basis_mon.append(mi)
    q = len(basis_mon)
    row_of_piv = {b: {int(c): i for i, c in enumerate(W[b].piv.tolist())} for b in space.blocks}

    def class_of_unit(mi: int) -> list[tuple[int, int]]:
        """Class of the monomial with Space index mi as (basis index, value) pairs."""
        b, c = int(space.block_of[mi]), int(space.pos[mi])
        if c not in row_of_piv[b]:
            return [(basis_of_mon[mi], 1)]
        row = W[b].B[row_of_piv[b][c]]
        out = []
        for f in free_cols[b].tolist():
            v = int(row[f])
            if v:
                out.append((basis_of_mon[int(space.cols[b][f])], (-v) % p))
        return out

    M = []
    for k in range(n):
        ent = []
        for col, mi in enumerate(basis_mon):
            tgt = int(space.shift[k][mi])
            if tgt < 0:
                continue
            for row, val in class_of_unit(tgt):
                ent.append([row, col, val])
        M.append(ent)
    lev = [int(space.deg[mi]) for mi in basis_mon]
    one = int(space.index(np.zeros((1, n), dtype=np.int64))[0])
    if one not in basis_of_mon:
        raise SystemExit("the class of 1 is zero: the ideal is the unit ideal")
    e_idx = basis_of_mon[one]

    # class vector of every product: reduce the whole jet against W, block by block
    def class_vector(idx, coef):
        v = [0] * q
        for b in space.blocks:
            sel = space.block_of[idx] == b
            if not sel.any():
                continue
            row = np.zeros(len(space.cols[b]))
            row[space.pos[idx[sel]]] = coef[sel]
            red = W[b].reduce(row.reshape(1, -1))[0]
            for f in free_cols[b].tolist():
                if red[f]:
                    v[basis_of_mon[int(space.cols[b][f])]] = int(red[f])
        return v

    vecs = [class_vector(idx, coef) for idx, coef in Psp]
    # greedy selection of independent rows
    sel: list[int] = []
    cur = 0
    for i in range(len(vecs)):
        trial = flint.nmod_mat(len(sel) + 1, q, [x for j in sel + [i] for x in vecs[j]], p)
        if trial.rank() > cur:
            sel.append(i)
            cur += 1
    r = len(sel)
    S = flint.nmod_mat(r, q, [x for j in sel for x in vecs[j]], p)  # r x q, rows = selected class vectors
    R, rk = S.rref()
    cols_c = []
    for i in range(r):
        for c in range(q):
            if int(R[i, c]) != 0:
                cols_c.append(c)
                break
    A = flint.nmod_mat(r, r, [int(S[i, c]) for i in range(r) for c in cols_c], p)  # A[i][j] = S[i, cols_c[j]]
    # want L (r x q), supported on cols_c, with L S^T = I: L_C A^T = I, L_C = (A^T)^-1
    Linv = (A.transpose()).inv()
    L = [[0] * q for _ in range(r)]
    for i in range(r):
        for j, c in enumerate(cols_c):
            L[i][c] = int(Linv[i, j])

    # raw-mode W contains the truncation of J: every term-truncated generator of J times every monomial of degree
    # < N - (lowest term degree) reduces to zero against the reduced echelon form of W
    j_in_w = True
    checked = 0
    for g in J:
        jet = {m: c for m, c in g.items() if sum(m) < N}
        if not jet:
            continue
        low = min(sum(m) for m in jet)
        for deg in range(N - low):
            for mono in eng.exps_of_degree(n, deg):
                shifted = {tuple(x + y for x, y in zip(m, mono, strict=True)): c for m, c in jet.items()}
                shifted = {m: c for m, c in shifted.items() if sum(m) < N}
                if not shifted:
                    continue
                idx = space.index(np.array(list(shifted.keys()), dtype=np.int64))
                coef = np.array(list(shifted.values()), dtype=np.float64)
                if any(class_vector(idx, coef)):
                    j_in_w = False
                checked += 1

    def table(polys):
        return [[[int(c), list(m)] for m, c in sorted(poly.items())] for poly in polys]

    header_bytes = Path(a.header).read_bytes()
    result = {
        "schema": SCHEMA,
        "ledger_id": a.ledger_id,
        "fiber": a.fiber,
        "prime": p,
        "d": a.d,
        "h_claimed": a.h_claimed,
        "header": {
            "path": a.header_path or Path(a.header).name,
            "sha256": hashlib.sha256(header_bytes).hexdigest(),
            "vars": names,
            "J": table(J),
            "G": table(G),
        },
        "truncation": {"N": N, "dim_V": int(len(space.exps))},
        "J_in_W": j_in_w,
        "J_in_W_method": (
            f"every term-truncated generator of J times every monomial of degree < N - lowest term degree "
            f"({checked} products) reduces to zero against the reduced echelon form of W"
        ),
        "module": {
            "q": q,
            "basis": [[int(x) for x in space.exps[mi]] for mi in basis_mon],
            "basis_order": (
                "character blocks in increasing block index; within a block, non-pivot columns of the reduced "
                "row echelon form of W in the engine's column order (degree ascending, then Space order)"
            ),
            "block_of_basis": [int(space.block_of[mi]) for mi in basis_mon],
            "lev": lev,
            "e": e_idx,
            "M_convention": "M[k] lists [row, col, val]: t_(k+1) * basis[col] = sum val * basis[row] in V/W",
            "M": M,
        },
        "products": {
            "mode": "all",
            "count": len(prod_tuples),
            "tuples": [list(t) for t in prod_tuples],
            "selected": sel,
            "r": r,
            "left_inverse_convention": (
                "left_inverse[i][c]: sum_c left_inverse[i][c] * class(product sel[j])[c] = delta_ij"
            ),
            "left_inverse": L,
        },
        "upper": {"k2_table": None, "reduction_table": None},
        "producer": {
            "engine_file": "fiber_rank_v8.py",
            "engine_sha256_16": eng.ENGINE_SHA,
            "exporter_sha256_16": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()[:16],
            "sign_group": [[names[i] for i in fl] for fl in group],
            "closure_rounds": rounds,
            "seconds": round(time.time() - t0, 2),
            "tool_versions": {
                "python": platform.python_version(),
                "numpy": np.__version__,
                "python-flint": flint.__version__,
                "machine": platform.machine(),
            },
        },
    }
    Path(a.out).write_text(json.dumps(result, separators=(",", ":")) + "\n")
    print(json.dumps({"q": q, "r": r, "J_in_W": j_in_w, "seconds": result["producer"]["seconds"]}))


if __name__ == "__main__":
    main()
