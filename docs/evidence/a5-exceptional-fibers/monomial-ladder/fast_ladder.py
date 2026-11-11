"""Truncated ranks A_d, B_d and r = A_d - B_d of the monomial ladder by a batched float64 echelon over F_p.

The slugs xm-nm and xp-np (same-sign X slice, x_same_ladder.py) and e8-nm and e8-np (E8-bar, e8_ladder.py) are
supported, for a prime p < 2^15. For the requested degree d and order N the script builds A_d, the image of I^d, and
B_d, the image of m_R I^d, in the ambient space modulo n^N, and reports dim A_d, dim B_d and r = A_d - B_d. It needs
torch (CPU), numpy and scipy.

    $PYTHON docs/evidence/a5-exceptional-fibers/monomial-ladder/fast_ladder.py --slug xm-nm --prime 32009 \
        --degree 3 --order 14 [--batch 1024] [--threads N] [--out record.json]

The spaces and ranks are those of x_same_ladder.py and e8_ladder.py. An element of the ambient space is a tuple of
polynomials (one for X; (p, q) standing for p + q b for E8-bar), written on the monomials below the order of its part.
Multiplication by a generator is a sparse matrix on that basis. The echelon form E is a dense float64 matrix in
reduced row echelon form with pivot columns P: a batch X is reduced by X - X[:, P] E, its residual is echelonized in
leaves of 64 rows, and E is updated by E - E[:, P_new] X_new. Entries are integers below p < 2^15, products are below
2^30 and a sum has fewer than 2^17 terms, so every float64 value is an exact integer below 2^47 before reduction.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
import scipy.sparse as sp
import torch


def load(root: Path, name: str) -> Any:
    path = root / "docs/evidence/a5-exceptional-fibers/monomial-ladder" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Monomials:
    """The monomials in nvars variables of degree below order, with a lookup table."""

    def __init__(self, nvars: int, order: int) -> None:
        order = max(order, 0)
        grid = np.indices((order,) * nvars, dtype=np.int16).reshape(nvars, -1).T
        self.exponents = grid[grid.sum(axis=1) < order].astype(np.int64)
        self.order = order
        self.table = np.full((order,) * nvars, -1, dtype=np.int64)
        self.table[tuple(self.exponents.T)] = np.arange(len(self.exponents))

    def __len__(self) -> int:
        return len(self.exponents)


class Space:
    """Tuples of polynomials, part i truncated at order + offsets[i]."""

    def __init__(self, nvars: int, order: int, offsets: tuple[int, ...]) -> None:
        self.parts = [Monomials(nvars, order + o) for o in offsets]
        self.starts = np.cumsum([0] + [len(p) for p in self.parts])
        self.size = int(self.starts[-1])

    def vector(self, element: tuple[Any, ...]) -> np.ndarray:
        out = np.zeros(self.size, dtype=np.float64)
        for part, start, poly in zip(self.parts, self.starts[:-1], element, strict=True):
            for exponents, coefficient in poly.to_dict().items():
                e = tuple(int(v) for v in exponents)
                if sum(e) < part.order:
                    out[start + part.table[e]] = int(coefficient)
        return out


def block(poly: Any, source: Monomials, target: Monomials) -> sp.coo_matrix:
    """Rows on the target, columns on the source: the matrix of x -> x * poly truncated to the target order."""
    rows, cols, vals = [], [], []
    base = np.arange(len(source))
    degrees = source.exponents.sum(axis=1)
    for exponents, coefficient in poly.to_dict().items():
        shift = np.array([int(v) for v in exponents], dtype=np.int64)
        keep = degrees + int(shift.sum()) < target.order
        if not keep.any():
            continue
        moved = source.exponents[keep] + shift
        cols.append(base[keep])
        rows.append(target.table[tuple(moved.T)])
        vals.append(np.full(len(moved), float(int(coefficient))))
    if not rows:
        return sp.coo_matrix((len(target), len(source)))
    return sp.coo_matrix(
        (np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))), shape=(len(target), len(source))
    )


def multiplication(blocks: dict[tuple[int, int], Any], source: Space, target: Space) -> torch.Tensor:
    """blocks[i, k] is the polynomial that carries part i of the element into part k of the product."""
    n = len(source.parts)
    grid = [[None] * n for _ in range(n)]
    for (i, k), poly in blocks.items():
        grid[k][i] = block(poly, source.parts[i], target.parts[k])
    for k in range(n):
        for i in range(n):
            if grid[k][i] is None:
                grid[k][i] = sp.coo_matrix((len(target.parts[k]), len(source.parts[i])))
    matrix = sp.bmat(grid, format="csr")
    return torch.sparse_csr_tensor(
        torch.from_numpy(matrix.indptr.astype(np.int64)),
        torch.from_numpy(matrix.indices.astype(np.int64)),
        torch.from_numpy(matrix.data),
        size=matrix.shape,
        dtype=torch.float64,
    )


def leaf_rref(rows: torch.Tensor, prime: int) -> tuple[torch.Tensor, torch.Tensor]:
    """Reduced row echelon form of a short block by row operations; returns the nonzero rows and their pivots."""
    rows = rows.clone()
    pivots: list[int] = []
    used: list[int] = []
    for i in range(len(rows)):
        nonzero = torch.nonzero(rows[i])
        if not len(nonzero):
            continue
        c = int(nonzero[0])
        rows[i] = torch.remainder(rows[i] * pow(int(rows[i, c]), -1, prime), prime)
        factors = rows[:, c].clone()
        factors[i] = 0
        rows.addr_(factors, rows[i].clone(), alpha=-1).remainder_(prime)
        pivots.append(c)
        used.append(i)
    return rows[used], torch.tensor(pivots, dtype=torch.int64)


class Echelon:
    LEAF = 64

    def __init__(self, columns: int, prime: int, capacity: int = 256) -> None:
        self.prime = prime
        self.columns = columns
        self.buffer = torch.zeros((capacity, columns), dtype=torch.float64)
        self.rank = 0
        self.pivots = torch.zeros(0, dtype=torch.int64)

    @property
    def rows(self) -> torch.Tensor:
        return self.buffer[: self.rank]

    def reduce(self, batch: torch.Tensor) -> torch.Tensor:
        """Reduces the batch in place."""
        if self.rank:
            batch.addmm_(batch[:, self.pivots], self.rows, alpha=-1)
        return batch.remainder_(self.prime)

    def append(self, new: torch.Tensor, new_pivots: torch.Tensor) -> None:
        count = len(new_pivots)
        if not count:
            return
        if self.rank:
            view = self.rows
            view.addmm_(view[:, new_pivots], new, alpha=-1).remainder_(self.prime)
        if self.rank + count > len(self.buffer):
            grown = torch.zeros((max(self.rank + count, len(self.buffer) * 3 // 2), self.columns), dtype=torch.float64)
            grown[: self.rank] = self.rows
            self.buffer = grown
        self.buffer[self.rank : self.rank + count] = new
        self.rank += count
        self.pivots = torch.cat([self.pivots, new_pivots])

    def insert(self, batch: torch.Tensor) -> None:
        batch = self.reduce(batch)
        batch = batch[batch.any(dim=1)]
        if not len(batch):
            return
        local = Echelon(self.columns, self.prime, capacity=len(batch))
        for begin in range(0, len(batch), self.LEAF):
            chunk = local.reduce(batch[begin : begin + self.LEAF].clone())
            chunk = chunk[chunk.any(dim=1)]
            if len(chunk):
                local.append(*leaf_rref(chunk, self.prime))
        self.append(local.rows, local.pivots)


def x_model(root: Path, slug: str, prime: int, order: int) -> dict[str, Any]:
    lad = load(root, "x_same_ladder")
    ctx = lad.nmod_mpoly_ctx.get(lad.NAMES, ordering=lad.Ordering.degrevlex, modulus=prime)
    gens = lad.generators(slug, prime, order)
    return {
        "nvars": 4,
        "offsets": (0,),
        "low": int(min(min(sum(e) for e in g.to_dict()) for g in gens)),
        "blocks": lambda current: [{(0, 0): lad.truncate(ctx, g, current)} for g in gens],
        "basis": lambda start, maximal: [(b,) for b in lad.ring_basis(ctx, start, maximal)],
        "count": len(gens),
    }


def e8_model(root: Path, slug: str, prime: int, order: int) -> dict[str, Any]:
    lad = load(root, "e8_ladder")
    ring = lad.Ring(prime, order)
    gens = lad.generators(slug, ring)

    def weight(x: Any) -> int:
        return min([sum(e) for e in x[0].to_dict()] + [sum(e) + 1 for e in x[1].to_dict()], default=order)

    def blocks(current: int) -> list[dict[tuple[int, int], Any]]:
        out = []
        for g0, g1 in gens:
            # (x0 + x1 b)(g0 + g1 b) = x0 g0 + x1 g1 F + (x0 g1 + x1 g0) b, with b^2 = F.
            out.append(
                {
                    (0, 0): ring.cut(g0, current),
                    (1, 0): ring.cut(ring.cut(g1, current - 2) * ring.f, current),
                    (0, 1): ring.cut(g1, current - 1),
                    (1, 1): ring.cut(g0, current - 1),
                }
            )
        return out

    return {
        "nvars": 5,
        "offsets": (0, -1),
        "low": int(min(weight(g) for g in gens)),
        "blocks": blocks,
        "basis": lambda start, maximal: lad.ring_basis(ring, start, maximal),
        "count": len(gens),
    }


def ladder(root: Path, slug: str, prime: int, degree: int, order: int, batch: int) -> dict[str, Any]:
    started = time.time()
    timing = {"generators": 0.0, "maps": 0.0, "products": 0.0, "echelon": 0.0}
    model = (e8_model if slug.startswith("e8") else x_model)(root, slug, prime, order)
    timing["generators"] = time.time() - started
    low = model["low"]
    start = order - low * degree
    if start < 2:
        raise SystemExit(f"order {order} is below {low * degree + 2}")
    source = Space(model["nvars"], start, model["offsets"])
    spaces = {
        key: torch.from_numpy(np.array([source.vector(b) for b in model["basis"](start, key == "B")]))
        for key in ("A", "B")
    }
    ranks = []
    for d in range(1, degree + 1):
        current = start + low * d
        target = Space(model["nvars"], current, model["offsets"])
        clock = time.time()
        maps = [multiplication(blocks, source, target) for blocks in model["blocks"](current)]
        timing["maps"] += time.time() - clock
        row = {"degree": d, "order": current, "columns": target.size, "map_nnz": int(sum(m._nnz() for m in maps))}
        for key in ("A", "B"):
            echelon = Echelon(target.size, prime, capacity=max(256, len(spaces[key])))
            space = spaces[key]
            for matrix in maps:
                for begin in range(0, len(space), batch):
                    clock = time.time()
                    product = (matrix @ space[begin : begin + batch].T).T.contiguous()
                    timing["products"] += time.time() - clock
                    clock = time.time()
                    echelon.insert(product)
                    timing["echelon"] += time.time() - clock
            spaces[key] = echelon.rows.clone()
            row[key] = echelon.rank
            del echelon
        row["r"] = row["A"] - row["B"]
        row["seconds"] = round(time.time() - started, 1)
        print(json.dumps(row), flush=True)
        ranks.append(row)
        source = target
    return {
        "slug": slug,
        "prime": prime,
        "order": order,
        "generators": model["count"],
        "generator_order": low,
        "engine": "float64-batched-echelon",
        "batch": batch,
        "threads": torch.get_num_threads(),
        "rows": ranks,
        "timing": {k: round(v, 1) for k, v in timing.items()},
        "seconds": round(time.time() - started, 1),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--slug", default="xm-nm")
    parser.add_argument("--prime", type=int, default=32009)
    parser.add_argument("--degree", type=int, required=True)
    parser.add_argument("--order", type=int, required=True)
    parser.add_argument("--batch", type=int, default=1024)
    parser.add_argument("--threads", type=int, default=0)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    sys.path.insert(0, str(root / "gororoba_quantum"))
    sys.path.insert(0, str(root / "docs/evidence/a5-exceptional-fibers/kernel-limits"))
    if args.threads:
        torch.set_num_threads(args.threads)
    record = ladder(root, args.slug, args.prime, args.degree, args.order, args.batch)
    if args.out:
        args.out.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(record))


if __name__ == "__main__":
    main()
