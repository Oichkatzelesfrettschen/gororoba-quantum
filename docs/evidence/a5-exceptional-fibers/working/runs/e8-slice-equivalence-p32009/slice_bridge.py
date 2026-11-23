"""Linear equivalence test of two quadric ideals through the maximal tori of their linear symmetry algebras.

Usage: slice_bridge.py CELL KA.sing KH.sing OUT.json   (prime 32009, 21 generators)

Both ideals are spans of 148 quadrics in y(1..21) over F_p. For each span the script computes the Lie algebra g of
matrices A whose derivation y_i -> sum_j A_ij y_j preserves the span, the centralizer c of a pseudo-random element of
g (a Cartan subalgebra where its dimension is the torus rank, 6 for these ideals by A5-424), joint eigen-coordinates
of c, and the grading of the span by the weights of c.

Where the two centralizers are the Lie algebras of split maximal tori that are conjugate under the symmetry group, a
linear map carrying one span onto the other can be composed with a symmetry so that it carries one torus to the
other; it is then a permutation of the eigen-coordinates times a diagonal matrix. The script does not establish
those conditions: the search is a way of finding a map, and a found map is its own evidence. A search that finds no
map decides nothing.

The script searches the permutations that preserve the weight partition of the quadratic monomials and the rank of
the span on each class, solves the diagonal entries from the echelon bases of the classes through discrete logarithms
and a Hermite normal form over Z, and accepts a map only when the transported span has the rank of the header span
and their joint rank is the same.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

import numpy as np
from flint import fmpz_mat, nmod_mat, nmod_poly

P = 32009
N = 21
MONS = [(a, b) for a in range(N) for b in range(a, N)]
MIDX = {m: k for k, m in enumerate(MONS)}
TERM = re.compile(r"([+-]?\d+)\*((?:y\(\d+\)(?:\^2)?\*?)+)")
VAR = re.compile(r"y\((\d+)\)(\^2)?")
INV2 = pow(2, -1, P)


class HashStream:
    """Residues read from sha256 of a label and a counter. They pick an element of the symmetry algebra and of its
    centralizer; the verdict depends on no such choice, since a found map is verified by a rank and by Singular."""

    def __init__(self, label: str) -> None:
        self.label, self.count = label, 0

    def next(self) -> int:
        self.count += 1
        digest = hashlib.sha256(f"{self.label}:{self.count}".encode()).digest()
        return int.from_bytes(digest[:8], "big") % P


def parse(path: Path) -> np.ndarray:
    text = path.read_text()
    body = text[text.index("=") + 1 :].rstrip().rstrip(";")
    rows = []
    for line in body.split(","):
        line = line.strip()
        if not line:
            continue
        row = np.zeros(len(MONS), dtype=np.int64)
        seen = 0
        for coefficient, monomial in TERM.findall(line):
            idx: list[int] = []
            for var, square in VAR.findall(monomial):
                idx += [int(var) - 1] * (2 if square else 1)
            if len(idx) != 2:
                raise ValueError(f"not a quadratic term: {monomial}")
            row[MIDX[(min(idx), max(idx))]] += int(coefficient)
            seen += 1
        if seen == 0 or TERM.sub("", line).strip("+ ") != "":
            raise ValueError(f"unparsed generator: {line[:60]}")
        rows.append(row % P)
    return np.array(rows, dtype=np.int64)


def nm(a: np.ndarray) -> nmod_mat:
    a = np.atleast_2d(a) % P
    return nmod_mat(a.shape[0], a.shape[1], [int(v) for v in a.ravel()], P)


def arr(m: nmod_mat) -> np.ndarray:
    return np.array([[int(v) for v in row] for row in m.tolist()], dtype=np.int64).reshape(m.nrows(), m.ncols())


def rref(a: np.ndarray) -> tuple[np.ndarray, list[int]]:
    if a.size == 0:
        return a.reshape(0, a.shape[1] if a.ndim == 2 else 0), []
    m, rank = nm(a).rref()
    out = arr(m)[:rank]
    pivots = [int(np.nonzero(row)[0][0]) for row in out]
    return out, pivots


def rank(a: np.ndarray) -> int:
    return 0 if a.size == 0 else nm(a).rank()


def kernel(a: np.ndarray) -> np.ndarray:
    """Rows spanning {x : a x = 0}."""
    x, nullity = nm(a).nullspace()
    return arr(x).T[:nullity]


def stabilizer(k: np.ndarray) -> np.ndarray:
    ann = kernel(k)  # 83 x 231, functionals vanishing on the span
    if ann.shape[0] != len(MONS) - rank(k):
        raise ValueError("annihilator dimension")
    blocks = []
    for q in k:
        t = np.zeros((N * N, len(MONS)), dtype=np.int64)
        for col in np.nonzero(q)[0]:
            a, b = MONS[col]
            c = int(q[col])
            for j in range(N):
                if a == b:
                    t[a * N + j, MIDX[(min(a, j), max(a, j))]] += 2 * c
                else:
                    t[a * N + j, MIDX[(min(b, j), max(b, j))]] += c
                    t[b * N + j, MIDX[(min(a, j), max(a, j))]] += c
        blocks.append(((t % P) @ ann.T % P).T)
    system = np.concatenate(blocks, axis=0) % P
    return kernel(system).reshape(-1, N, N)


def derive_exact(q: np.ndarray, a: np.ndarray) -> np.ndarray:
    """q(y) -> sum_i (dq/dy_i) (A y)_i, by the symmetric matrix of q."""
    s = sym(q)
    return unsym((a.T @ s + s @ a) % P)


def sym(q: np.ndarray) -> np.ndarray:
    s = np.zeros((N, N), dtype=np.int64)
    for col in np.nonzero(q)[0]:
        a, b = MONS[col]
        if a == b:
            s[a, a] = q[col]
        else:
            s[a, b] = s[b, a] = int(q[col]) * INV2 % P
    return s


def unsym(s: np.ndarray) -> np.ndarray:
    q = np.zeros(len(MONS), dtype=np.int64)
    for col, (a, b) in enumerate(MONS):
        q[col] = s[a, a] if a == b else (s[a, b] + s[b, a])
    return q % P


def torus_frame(k: np.ndarray, label: str) -> dict:
    g = stabilizer(k)
    span = rref(k)[0]
    for a in g:
        for q in span[:: max(1, len(span) // 12)]:
            if rank(np.vstack([span, derive_exact(q, a)])) != len(span):
                raise ValueError("stabilizer element leaves the span")
    stream = HashStream(label)
    x = sum(stream.next() * a for a in g) % P
    comm = np.array([((x @ a - a @ x) % P).ravel() for a in g]).T
    coeff = kernel(comm)
    cartan = np.array([sum(int(c) * a for c, a in zip(row, g, strict=True)) % P for row in coeff])
    for a in cartan:
        for b in cartan:
            if np.any((a @ b - b @ a) % P):
                return {"stabilizer_dim": int(len(g)), "centralizer_dim": int(len(cartan)), "frame": False}
    t = sum(stream.next() * a for a in cartan) % P
    roots = nmod_poly([int(v) for v in nm(t).charpoly().coeffs()], P).roots()
    eig = sorted(int(r) for r, _ in roots)
    info: dict[str, Any] = {
        "stabilizer_dim": int(len(g)),
        "centralizer_dim": int(len(cartan)),
        "distinct_eigenvalues_in_Fp": len(eig),
    }
    if len(eig) != N:
        info["frame"] = False
        return info
    rows = []
    for lam in eig:
        v = kernel(((t - lam * np.eye(N, dtype=np.int64)) % P).T)
        if len(v) != 1:
            raise ValueError("eigenspace dimension")
        rows.append(v[0])
    vmat = np.array(rows) % P
    umat = arr(nm(vmat).inv())
    weights = np.zeros((N, len(cartan)), dtype=np.int64)
    for index, c in enumerate(cartan):
        image = vmat @ c % P
        for kk in range(N):
            piv = int(np.nonzero(vmat[kk])[0][0])
            lam = int(image[kk, piv]) * pow(int(vmat[kk, piv]), -1, P) % P
            if np.any((image[kk] - lam * vmat[kk]) % P):
                raise ValueError("not a joint eigenvector")
            weights[kk, index] = lam
    kz = np.array([unsym(umat.T @ sym(q) @ umat % P) for q in k]) % P
    classes: dict[tuple[int, ...], list[int]] = {}
    for col, (a, b) in enumerate(MONS):
        classes.setdefault(tuple(int(v) for v in (weights[a] + weights[b]) % P), []).append(col)
    cls: list[dict[str, Any]] = []
    total = 0
    for cols in classes.values():
        basis, pivots = rref(kz[:, cols])
        total += len(basis)
        cls.append({"cols": cols, "rank": len(basis), "basis": basis, "pivots": pivots})
    info.update(
        frame=True, graded_rank_sum=total, classes=len(cls), distinct_weights=len({tuple(w) for w in weights.tolist()})
    )
    info["class_profile"] = sorted([len(c["cols"]), c["rank"]] for c in cls)
    return {"info": info, "V": vmat, "U": umat, "kz": kz, "cls": cls}


def class_table(frame: dict) -> tuple[np.ndarray, list[tuple[int, int]]]:
    table = np.zeros((N, N), dtype=np.int64)
    meta = []
    for cid, c in enumerate(frame["cls"]):
        meta.append((len(c["cols"]), c["rank"]))
        for col in c["cols"]:
            a, b = MONS[col]
            table[a, b] = table[b, a] = cid
    return table, meta


def matchings(fw: dict, fh: dict, cap: int) -> tuple[list[list[int]], bool]:
    tw, mw = class_table(fw)
    th, mh = class_table(fh)
    sig_w = [tuple(sorted((mw[tw[a, b]], a == b) for b in range(N))) for a in range(N)]
    sig_h = [tuple(sorted((mh[th[a, b]], a == b) for b in range(N))) for a in range(N)]
    order = sorted(range(N), key=lambda a: sum(1 for s in sig_h if s == sig_w[a]))
    out: list[list[int]] = []
    perm = [-1] * N
    used = [False] * N
    cmap: dict[int, int] = {}
    rmap: dict[int, int] = {}

    def place(depth: int) -> bool:
        if len(out) >= cap:
            return True
        if depth == N:
            out.append(perm.copy())
            return False
        a = order[depth]
        for x in range(N):
            if used[x] or sig_h[x] != sig_w[a]:
                continue
            added = []
            ok = True
            perm[a] = x
            for b in order[: depth + 1]:
                cw, ch = int(tw[a, b]), int(th[x, perm[b]])
                if mw[cw] != mh[ch] or cmap.get(cw, ch) != ch or rmap.get(ch, cw) != cw:
                    ok = False
                    break
                if cw not in cmap:
                    cmap[cw], rmap[ch] = ch, cw
                    added.append((cw, ch))
            if ok:
                used[x] = True
                if place(depth + 1):
                    return True
                used[x] = False
            for cw, ch in added:
                del cmap[cw], rmap[ch]
            perm[a] = -1
        return False

    capped = place(0)
    return out, capped


def primitive_root() -> int:
    factors = [2, 4001]
    for g in range(2, P):
        if all(pow(g, (P - 1) // f, P) != 1 for f in factors):
            return g
    raise ValueError("no primitive root")


GEN = primitive_root()
DLOG = {}
_v = 1
for _e in range(P - 1):
    DLOG[_v] = _e
    _v = _v * GEN % P


def solve_scalars(fw: dict, fh: dict, perm: list[int]) -> list[int] | None:
    """Exponents x with z_W(a) -> GEN^x[perm[a]] z_H(perm[a]) carrying each W class basis onto the H class basis."""
    th, _ = class_table(fh)
    hcls = fh["cls"]
    eqs: dict[tuple[int, ...], int] = {}
    for c in fw["cls"]:
        if c["rank"] in (0, len(c["cols"])):
            continue
        a0, b0 = MONS[c["cols"][0]]
        target = hcls[int(th[perm[a0], perm[b0]])]
        position = {col: k for k, col in enumerate(target["cols"])}
        moved = np.zeros((c["rank"], len(target["cols"])), dtype=np.int64)
        for k, col in enumerate(c["cols"]):
            a, b = MONS[col]
            image = MIDX[(min(perm[a], perm[b]), max(perm[a], perm[b]))]
            moved[:, position[image]] = c["basis"][:, k]
        basis, pivots = rref(moved)
        if pivots != target["pivots"]:
            return None
        if np.any((basis != 0) != (target["basis"] != 0)):
            return None
        for r, piv in enumerate(pivots):
            pa, pb = MONS[target["cols"][piv]]
            for k in np.nonzero(basis[r])[0]:
                if k == piv:
                    continue
                ma, mb = MONS[target["cols"][k]]
                row = [0] * N
                row[ma] += 1
                row[mb] += 1
                row[pa] -= 1
                row[pb] -= 1
                ratio = int(target["basis"][r, k]) * pow(int(basis[r, k]), -1, P) % P
                key = tuple(row)
                if eqs.setdefault(key, DLOG[ratio]) != DLOG[ratio]:
                    return None
    if not eqs:
        return [0] * N
    rows = list(eqs)
    e = len(rows)
    gmat = [[rows[k][v] for k in range(e)] for v in range(N)] + [
        [(P - 1) if k == j else 0 for k in range(e)] for j in range(e)
    ]
    h, t = fmpz_mat(gmat).hnf(True)
    hl, tl = h.tolist(), t.tolist()
    rest = [eqs[r] for r in rows]
    comb = [0] * (N + e)
    for r in range(N + e):
        lead = next((k for k in range(e) if hl[r][k] != 0), None)
        if lead is None:
            continue
        piv = lead
        quotient, remainder = divmod(int(rest[piv]), int(hl[r][piv]))
        if remainder:
            return None
        comb[r] = quotient
        rest = [int(rest[k]) - quotient * int(hl[r][k]) for k in range(e)]
    if any(rest):
        return None
    x = [sum(comb[r] * int(tl[r][v]) for r in range(N + e)) % (P - 1) for v in range(N)]
    return x


def transport(fw: dict, fh: dict, perm: list[int], x: list[int], sign: int) -> np.ndarray | None:
    d = [pow(GEN, sign * x[perm[a]] % (P - 1), P) for a in range(N)]
    moved = np.zeros_like(fw["kz"])
    for col, (a, b) in enumerate(MONS):
        image = MIDX[(min(perm[a], perm[b]), max(perm[a], perm[b]))]
        moved[:, image] = fw["kz"][:, col] * (d[a] * d[b] % P) % P
    if rank(moved) != rank(fh["kz"]) or rank(np.vstack([moved, fh["kz"]])) != rank(fh["kz"]):
        return None
    dp = np.zeros((N, N), dtype=np.int64)
    for a in range(N):
        dp[a, perm[a]] = d[a]
    return fw["U"] @ dp % P @ fh["V"] % P


def main() -> int:
    cell, ka_path, kh_path, out_path = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4])
    ka, kh = parse(ka_path), parse(kh_path)
    record: dict = {
        "cell": cell,
        "prime": P,
        "generators": N,
        "primitive_root": GEN,
        "weight_file_sha256": hashlib.sha256(ka_path.read_bytes()).hexdigest(),
        "header_file_sha256": hashlib.sha256(kh_path.read_bytes()).hexdigest(),
        "rank_weight": rank(ka),
        "rank_header": rank(kh),
        "rank_union_identity": rank(np.vstack([ka, kh])),
    }
    frames = []
    for side, k in (("weight", ka), ("header", kh)):
        frame: dict = {}
        tries = 0
        for tries in range(1, 65):
            frame = torus_frame(k, f"{cell}:{side}:{tries}")
            if "info" in frame:
                break
        record[side] = frame["info"] if "info" in frame else frame
        record[side]["torus_attempts"] = tries
        frames.append(frame)
    fw, fh = frames
    verdict = "no_frame"
    if "info" in fw and "info" in fh:
        record["class_profiles_equal"] = fw["info"]["class_profile"] == fh["info"]["class_profile"]
        perms, capped = matchings(fw, fh, 50000)
        record["matchings"], record["matchings_capped"] = len(perms), capped
        verdict = "no_matching" if not perms else "no_scalars"
        solved = 0
        for perm in perms:
            x = solve_scalars(fw, fh, perm)
            if x is None:
                continue
            solved += 1
            for sign in (1, -1):
                g = transport(fw, fh, perm, x, sign)
                if g is not None:
                    record.update(
                        map=g.tolist(), permutation=perm, exponents=x, sign=sign, map_det_nonzero=int(nm(g).det()) != 0
                    )
                    verdict = "map_found"
                    break
            if verdict == "map_found":
                break
        record["scalar_systems_solved"] = solved
    record["verdict"] = verdict
    out_path.write_text(json.dumps(record, indent=1) + "\n")
    print(
        "BRIDGE",
        cell,
        "stabilizer",
        record["weight"].get("stabilizer_dim"),
        record["header"].get("stabilizer_dim"),
        "centralizer",
        record["weight"].get("centralizer_dim"),
        record["header"].get("centralizer_dim"),
        "profiles_equal",
        record.get("class_profiles_equal"),
        "matchings",
        record.get("matchings"),
        "verdict",
        verdict,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
