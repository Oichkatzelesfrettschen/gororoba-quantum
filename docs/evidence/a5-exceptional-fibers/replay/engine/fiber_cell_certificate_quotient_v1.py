"""Hilbert-cell certificate export (schema a5-hilbert-cell-certificate-v1) for one quotient-mode cell.

The module reuses the fiber_rank_v8 quotient pipeline unchanged (quotient_data, table_products, Echelon, the character
blocks and the closure of W under the variables) and writes, for one header, one degree d and one truncation N, the
quotient module Q' = Q/W with Q = F_p[t]/(J + m^N) and W the image of the ideal m P_d in Q.

Basis construction. The standard monomials of the Singular dp standard basis of J + m^N form the coordinates of the
engine tables, and a dp normal form of t_k b may lower the degree, so the strict level increase of the checker fails
on them. The exporter therefore rebases Q'. It forms the m-adic flag F_0 = Q', F_(j+1) = sum_k M_k F_j by echelon
elimination, and picks the basis by degree: sel_0 = {1}, and sel_j holds, among the monomials t_k * alpha with alpha in
sel_(j-1), the first dim F_j - dim F_(j+1) whose classes are independent modulo F_(j+1). The class of a monomial is
M^alpha e, so the span of sel_i for i >= j is F_j, and t_k * b for b in sel_j lies in F_(j+1), which the basis
vectors of level at least j + 1 span. The level of b is the degree of its monomial, the basis lists the monomials, and
the matrices M_k are the engine matrices conjugated by the change of basis; the exporter asserts the strict increase
before it writes.

Conventions of the checker hold unchanged: every field element is an integer in [0, p), M_k[row, col] is the
coefficient of basis[row] in t_k * basis[col] in Q', the class of a polynomial g is g(M) e, and left_inverse[i][c]
satisfies sum_c left_inverse[i][c] * v_j[c] = delta_ij for the class vectors v_j of the selected products.

Usage: fiber_cell_certificate_quotient_v1.py HEADER D N OUT.json --ledger-id ID --fiber NAME --h-claimed H
       [--header-path PATH] [--record ENGINE_RECORD.json] [--singular PATH]
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
import json
import math
import platform
import subprocess
import sys
import time
from pathlib import Path
from types import ModuleType

import flint
import numpy as np
import scipy.sparse as sp

SCHEMA = "a5-hilbert-cell-certificate-v1"
HERE = Path(__file__).resolve().parent
CONSTRUCTION = (
    "quotient: Singular dp standard monomials of J + m^N; W = closure of m P_d in Q; basis of Q/W by the m-adic flag "
    "F_(j+1) = sum_k M_k F_j: level j holds the first dim F_j - dim F_(j+1) monomials t_k * alpha, alpha of level "
    "j - 1, whose classes M^alpha e are independent modulo F_(j+1); M_k = T^-1 M_k(dp) T with T the matrix of the "
    "classes M^alpha e"
)


def load_engine() -> ModuleType:
    spec = importlib.util.spec_from_file_location("fiber_rank_v8", HERE / "fiber_rank_v8.py")
    if spec is None or spec.loader is None:
        raise SystemExit("cannot load fiber_rank_v8.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["fiber_rank_v8"] = mod
    spec.loader.exec_module(mod)
    return mod


def pivot_columns(mat: flint.nmod_mat, rank: int, ncols: int) -> list[int]:
    """First nonzero column of each of the first rank rows of a reduced row echelon matrix."""
    ent = [int(x) for x in mat.entries()]
    out = []
    for i in range(rank):
        row = ent[i * ncols : (i + 1) * ncols]
        out.append(next(c for c, x in enumerate(row) if x))
    return out


def independent_columns(vectors: np.ndarray, p: int) -> list[int]:
    """Indices of the leftmost maximal independent subset of the rows of vectors over F_p."""
    m, q = vectors.shape
    mat = flint.nmod_mat(q, m, vectors.astype(np.int64).T.ravel().tolist(), p)
    red, rk = mat.rref()
    return pivot_columns(red, rk, m)


def to_array(mat: flint.nmod_mat, rows: int, cols: int) -> np.ndarray:
    return np.array([int(x) for x in mat.entries()], dtype=np.float64).reshape(rows, cols)


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
    ap.add_argument("--record", default=None, help="engine record whose block sizes and r_N the run must reproduce")
    ap.add_argument("--singular", default="Singular")
    ap.add_argument("--table-cache-gb", type=float, default=4.0)
    ap.add_argument("--chunk", type=int, default=4000)
    a = ap.parse_args()
    eng = load_engine()
    t0 = time.time()
    p, names, j_txt, g_txt = eng.parse_header(a.header)
    n, N, d = len(names), a.N, a.d
    if not eng.is_odd_prime(p):
        raise SystemExit(f"modulus {p} is not an odd prime")
    if d < 1 or N < 1:
        raise SystemExit("need d >= 1 and N >= 1")
    J = [eng.parse_poly(s, names, p) for s in j_txt]
    G = [eng.parse_poly(s, names, p) for s in g_txt]
    group = eng.sign_group([J, G], n, p)
    gens = eng.independent_generators(group, n)

    # engine quotient pipeline: dp standard monomials of J + m^N, tables, reduced generators, products, closure
    basis, tables, gpolys, t_sing = eng.quotient_data(eng.header_text(a.header), names, p, N, d, a.singular)
    D = len(basis)
    bidx = {m: i for i, m in enumerate(basis)}
    exps = np.array(basis, dtype=np.int64)
    chars = np.stack([(exps @ g) % 2 for g in gens], axis=1)
    block_of = chars @ np.array([2**i for i in range(len(gens))], dtype=np.int64)
    blocks = list(range(2 ** len(gens)))
    cols = {b: np.flatnonzero(block_of == b) for b in blocks}
    pos = np.empty(D, dtype=np.int64)
    for b in blocks:
        pos[cols[b]] = np.arange(len(cols[b]))
    var_char = [int(sum((int(g[k]) % 2) << i for i, g in enumerate(gens))) for k in range(n)]
    Msp = []
    for k in range(n):
        ri, cj, vv = [], [], []
        for i, poly in enumerate(tables[k]):
            for m, c in poly.items():
                ri.append(i)
                cj.append(bidx[m])
                vv.append(c)
        Msp.append(sp.csr_matrix((np.array(vv, dtype=np.float64), (ri, cj)), shape=(D, D)))
    gvecs = np.zeros((len(gpolys), D))
    for f, poly in enumerate(gpolys):
        for m, c in poly.items():
            gvecs[f, bidx[m]] = c
    prod_rows = eng.table_products(gvecs, basis, Msp, d, p, int(a.table_cache_gb * 2**30))
    prod_tuples = sorted(itertools.combinations_with_replacement(range(len(gpolys)), d))
    if len(prod_tuples) != len(prod_rows):
        raise SystemExit("product count differs from the multiset count")
    mats: list[dict[int, np.ndarray]] = []
    for k in range(n):
        mk = {b: np.zeros((len(cols[b]), len(cols[b ^ var_char[k]]))) for b in blocks}
        for i, poly in enumerate(tables[k]):
            bi = int(block_of[i])
            for m, c in poly.items():
                j = bidx[m]
                if int(block_of[j]) != bi ^ var_char[k]:
                    raise SystemExit("a multiplication table crosses character blocks")
                mk[bi][pos[i], pos[j]] = c
        mats.append(mk)
    W = {b: eng.Echelon(len(cols[b]), p) for b in blocks}
    Qb = {}
    for b in blocks:
        Y = prod_rows[:, cols[b]]
        Qb[b] = Y[np.any(Y != 0, axis=1)]
    for b in blocks:
        for k in range(n):
            tb = b ^ var_char[k]
            if len(Qb[b]):
                W[tb].insert(eng.exact_mod_matmul(Qb[b], mats[k][b], p), a.chunk)
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
                    X = eng.exact_mod_matmul(rows[s0 : s0 + a.chunk], mats[k][b], p)
                    X = X[np.any(X != 0, axis=1)]
                    if len(X):
                        W[tb].insert(X, a.chunk)
        new = {b: W[b].B[[i for i, c in enumerate(W[b].piv.tolist()) if c not in start[b]]] for b in blocks}
    rank_w = {b: len(W[b].piv) for b in blocks}

    # coordinates of Q' = Q/W: non-pivot columns per block, blocks in increasing index
    free_cols = {b: np.setdiff1d(np.arange(len(cols[b])), W[b].piv) for b in blocks}
    row_of_piv = {b: {int(c): i for i, c in enumerate(W[b].piv.tolist())} for b in blocks}
    idx0: dict[int, int] = {}
    for b in blocks:
        for f in free_cols[b].tolist():
            idx0[int(cols[b][f])] = len(idx0)
    q = len(idx0)
    free_lists = {b: [(int(f), idx0[int(cols[b][f])]) for f in free_cols[b].tolist()] for b in blocks}
    unit_cache: dict[int, list[tuple[int, int]]] = {}

    def class_of_unit(i: int) -> list[tuple[int, int]]:
        if i in unit_cache:
            return unit_cache[i]
        b, c = int(block_of[i]), int(pos[i])
        if c not in row_of_piv[b]:
            out = [(idx0[i], 1)]
        else:
            row = W[b].B[row_of_piv[b][c]]
            out = [(g, (-int(row[f])) % p) for f, g in free_lists[b] if row[f]]
        unit_cache[i] = out
        return out

    M0 = []
    for k in range(n):
        acc: dict[tuple[int, int], int] = {}
        for i0, i in ((v, u) for u, v in idx0.items()):
            for m, c in tables[k][i].items():
                for row, val in class_of_unit(bidx[m]):
                    key = (row, i0)
                    acc[key] = (acc.get(key, 0) + c * val) % p
        keys = [kk for kk, v in acc.items() if v]
        M0.append(
            sp.csr_matrix(
                (
                    np.array([acc[kk] for kk in keys], dtype=np.float64),
                    ([kk[0] for kk in keys], [kk[1] for kk in keys]),
                ),
                shape=(q, q),
            )
        )
    one_i = bidx[(0,) * n]
    e0 = np.zeros(q)
    for row, val in class_of_unit(one_i):
        e0[row] = val
    if not e0.any():
        raise SystemExit("the class of 1 is zero: the ideal is the unit ideal")
    V0 = np.zeros((len(prod_rows), q))
    for b in blocks:
        red = W[b].reduce(prod_rows[:, cols[b]])
        for f, g in free_lists[b]:
            V0[:, g] = red[:, f]

    # m-adic flag of Q'
    def apply_all(B: np.ndarray) -> np.ndarray:
        return np.vstack([np.mod(M0[k] @ B.T, p).T for k in range(n)])

    flag = [np.eye(q)]
    while len(flag[-1]):
        E = eng.Echelon(q, p)
        X = apply_all(flag[-1])
        E.insert(X[np.any(X != 0, axis=1)], a.chunk)
        flag.append(E.B.copy())
    dims = [len(F) for F in flag]
    top = len(flag) - 2
    # basis by level: first dims[j] - dims[j+1] monomials t_k * alpha independent modulo F_(j+1)
    levels: list[list[tuple[tuple[int, ...], np.ndarray]]] = []
    for j in range(top + 1):
        need = dims[j] - dims[j + 1]
        cand: list[tuple[tuple[int, ...], np.ndarray]] = []
        if j == 0:
            cand.append(((0,) * n, e0))
        else:
            seen: set[tuple[int, ...]] = set()
            for alpha, vec in levels[j - 1]:
                for k in range(n):
                    mono = tuple(x + (1 if i == k else 0) for i, x in enumerate(alpha))
                    if mono in seen:
                        continue
                    seen.add(mono)
                    v = np.mod(M0[k] @ vec, p)
                    if v.any():
                        cand.append((mono, v))
        E = eng.Echelon(q, p)
        E.insert(flag[j + 1], a.chunk)
        kept: list[tuple[tuple[int, ...], np.ndarray]] = []
        for s0 in range(0, len(cand), 256):
            if len(kept) == need:
                break
            chunk = cand[s0 : s0 + 256]
            R = E.reduce(np.array([v for _, v in chunk]))
            nz = np.flatnonzero(np.any(R != 0, axis=1))
            if not len(nz):
                continue
            pick = [int(nz[i]) for i in independent_columns(R[nz], p)][: need - len(kept)]
            E.insert(np.array([chunk[i][1] for i in pick]), a.chunk)
            kept.extend(chunk[i] for i in pick)
        if len(kept) != need:
            raise SystemExit(f"level {j}: {len(kept)} independent monomial classes, need {need}")
        levels.append(kept)
    if sum(len(x) for x in levels) != q:
        raise SystemExit("the module is not cyclic: the levels do not fill Q'")
    order = [mv for lvl in levels for mv in lvl]
    lev = [j for j, lvl in enumerate(levels) for _ in lvl]
    basis_exps = [list(m) for m, _ in order]
    T = np.stack([v for _, v in order], axis=1)
    Tinv = to_array(flint.nmod_mat(q, q, T.astype(np.int64).ravel().tolist(), p).inv(), q, q)
    Mn = []
    Mout: list[list[list[int]]] = []
    for k in range(n):
        Xk = eng.exact_mod_matmul(Tinv, np.mod(M0[k] @ T, p), p)
        r_i, c_i = np.nonzero(Xk)
        if len(r_i) and not all(lev[r] > lev[c] for r, c in zip(r_i.tolist(), c_i.tolist(), strict=True)):
            raise SystemExit("level increase fails on the rebased matrices")
        Mn.append(sp.csr_matrix(Xk))
        Mout.append([[int(rr), int(cc), int(Xk[rr, cc])] for rr, cc in zip(r_i.tolist(), c_i.tolist(), strict=True)])
    nnz = [len(x) for x in Mout]
    e_new = eng.exact_mod_matmul(Tinv, e0.reshape(q, 1), p)[:, 0]
    if int(e_new[0]) != 1 or np.count_nonzero(e_new) != 1:
        raise SystemExit("the class of 1 is not the first basis vector")
    V = eng.exact_mod_matmul(V0, Tinv.T, p)

    # raw-mode selection and left inverse, on the rebased class vectors
    sel = independent_columns(V, p)
    r = len(sel)
    S = flint.nmod_mat(r, q, [int(x) for j in sel for x in V[j]], p)
    Rs, rk = S.rref()
    cols_c = pivot_columns(Rs, rk, q)
    Amat = flint.nmod_mat(r, r, [int(V[sel[i], c]) for i in range(r) for c in cols_c], p)
    Linv = to_array(Amat.transpose().inv(), r, r)
    Lm = np.zeros((r, q))
    for j, c in enumerate(cols_c):
        Lm[:, c] = Linv[:, j]
    ident = eng.exact_mod_matmul(Lm, V[sel].T, p)
    if not np.array_equal(ident, np.eye(r)):
        raise SystemExit("left inverse times selected products is not the identity")

    # J(M) e = 0 by explicit evaluation on the emitted module
    memo: dict[tuple[int, ...], np.ndarray] = {(0,) * n: e_new}

    def monomial_class(mono: tuple[int, ...]) -> np.ndarray:
        if mono not in memo:
            k = next(i for i, x in enumerate(mono) if x)
            parent = tuple(x - (1 if i == k else 0) for i, x in enumerate(mono))
            memo[mono] = np.mod(Mn[k] @ monomial_class(parent), p)
        return memo[mono]

    j_in_w = True
    for poly in J:
        tot = np.zeros(q)
        for mono, c in poly.items():
            tot = np.mod(tot + c * monomial_class(mono), p)
        if tot.any():
            j_in_w = False

    # gate against the retained engine record
    gate = None
    if a.record:
        rec = json.loads(Path(a.record).read_text())
        want = {str(b): (len(cols[b]), rank_w[b]) for b in blocks}
        got = {k: (v["cols"], v["rank_W"]) for k, v in rec["per_block"].items()}
        problems = []
        if rec.get("dim_quotient") != D:
            problems.append(f"dim_quotient {D} vs record {rec.get('dim_quotient')}")
        if want != got:
            problems.append(f"block sizes {want} vs record {got}")
        if rec["r_N"] != r:
            problems.append(f"r {r} vs record r_N {rec['r_N']}")
        if problems:
            raise SystemExit("engine record mismatch: " + "; ".join(problems))
        gate = "dim_quotient, per-block cols and rank_W, and r_N equal the engine record"

    def table(polys: list[dict]) -> list:
        return [[[int(c), list(m)] for m, c in sorted(poly.items())] for poly in polys]

    header_bytes = Path(a.header).read_bytes()
    basis_block = [int(sum(((int(g @ np.array(m)) % 2) << i) for i, g in enumerate(gens))) for m in basis_exps]
    result = {
        "schema": SCHEMA,
        "cell_mode": "quotient",
        "ledger_id": a.ledger_id,
        "fiber": a.fiber,
        "prime": p,
        "d": d,
        "h_claimed": a.h_claimed,
        "header": {
            "path": a.header_path or Path(a.header).name,
            "sha256": hashlib.sha256(header_bytes).hexdigest(),
            "vars": names,
            "J": table(J),
            "G": table(G),
        },
        "truncation": {"N": N, "dim_V": math.comb(N - 1 + n, n), "dim_quotient": D},
        "J_in_W": j_in_w,
        "J_in_W_method": "J(M) e = 0 evaluated on the emitted module: every generator of J, every monomial by "
        "repeated application of the M_k to e",
        "module": {
            "q": q,
            "basis": basis_exps,
            "basis_order": "levels ascending; within a level, the selection order of the construction",
            "construction": CONSTRUCTION,
            "block_of_basis": basis_block,
            "lev": lev,
            "e": 0,
            "M_convention": "M[k] lists [row, col, val]: t_(k+1) * basis[col] = sum val * basis[row] in V/W",
            "M": Mout,
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
            "left_inverse": [[int(x) for x in row] for row in Lm],
        },
        "upper": {"k2_table": None, "reduction_table": None},
        "producer": {
            "engine_file": "fiber_rank_v8.py",
            "engine_sha256_16": eng.ENGINE_SHA,
            "exporter_sha256_16": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()[:16],
            "sign_group": [[names[i] for i in fl] for fl in group],
            "closure_rounds": rounds,
            "flag_dims": dims[:-1],
            "nnz_per_M": nnz,
            "record_gate": gate,
            "seconds": round(time.time() - t0, 2),
            "singular_seconds": round(t_sing, 1),
            "tool_versions": {
                "python": platform.python_version(),
                "numpy": np.__version__,
                "python-flint": flint.__version__,
                "machine": platform.machine(),
                "singular": subprocess.run(
                    [a.singular, "--version"], capture_output=True, text=True, stdin=subprocess.DEVNULL, check=False
                ).stdout.splitlines()[0:1],
            },
        },
    }
    Path(a.out).write_text(json.dumps(result, separators=(",", ":")) + "\n")
    print(json.dumps({"q": q, "r": r, "J_in_W": j_in_w, "nnz_per_M": nnz, "seconds": result["producer"]["seconds"]}))


if __name__ == "__main__":
    main()
