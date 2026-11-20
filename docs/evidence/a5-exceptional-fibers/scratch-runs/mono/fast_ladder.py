"""Monomial ladder of the same-sign X fiber cone with a batched echelon over F_p in float64 matrix products.

Same spaces and ranks as x_same_ladder.py. The echelon form is kept as a dense float64 matrix E in reduced row echelon
form with pivot columns P. A batch X of rows is reduced by X - X[:, P] E, one matrix product; its residual is
echelonized by FLINT, and E is updated by E - E[:, P_new] X_new. Every entry is an integer below p < 2^15, a product is
below 2^30 and a sum has at most 2^16 terms, so each float64 result is an exact integer below 2^46 before reduction.
Multiplication by a generator is a sparse matrix on the monomial basis.
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
from flint import nmod_mat


def load(root: Path) -> Any:
    path = root / "docs/evidence/a5-exceptional-fibers/monomial-ladder/x_same_ladder.py"
    spec = importlib.util.spec_from_file_location("x_same_ladder", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Monomials:
    """The monomials of k[a, rho, sig, w] of degree below order, with a lookup table."""

    def __init__(self, order: int) -> None:
        grid = np.indices((order,) * 4).reshape(4, -1).T
        self.exponents = grid[grid.sum(axis=1) < order].astype(np.int64)
        self.order = order
        self.table = np.full((order,) * 4, -1, dtype=np.int64)
        self.table[tuple(self.exponents.T)] = np.arange(len(self.exponents))

    def __len__(self) -> int:
        return len(self.exponents)

    def vector(self, poly: Any) -> np.ndarray:
        out = np.zeros(len(self), dtype=np.float64)
        for exponents, coefficient in poly.to_dict().items():
            e = tuple(int(v) for v in exponents)
            if sum(e) < self.order:
                out[self.table[e]] = int(coefficient)
        return out


def multiplication(poly: Any, source: Monomials, target: Monomials) -> sp.csr_matrix:
    """The matrix M with (row vector on source) M = row vector of the product, truncated to the target order."""
    rows, cols, vals = [], [], []
    base = np.arange(len(source))
    for exponents, coefficient in poly.to_dict().items():
        shift = np.array([int(v) for v in exponents], dtype=np.int64)
        moved = source.exponents + shift
        keep = moved.sum(axis=1) < target.order
        rows.append(base[keep])
        cols.append(target.table[tuple(moved[keep].T)])
        vals.append(np.full(int(keep.sum()), float(int(coefficient))))
    matrix = sp.csr_matrix(
        (np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))), shape=(len(source), len(target))
    )
    return matrix


def leaf_rref(block: torch.Tensor, prime: int) -> tuple[torch.Tensor, torch.Tensor]:
    """Reduced row echelon form of a short block by row operations; returns the nonzero rows and their pivots."""
    block = block.clone()
    pivots: list[int] = []
    used: list[int] = []
    for i in range(len(block)):
        nonzero = torch.nonzero(block[i])
        if not len(nonzero):
            continue
        c = int(nonzero[0])
        block[i] = torch.remainder(block[i] * pow(int(block[i, c]), -1, prime), prime)
        factors = block[:, c].clone()
        factors[i] = 0
        block = torch.remainder(block.addr_(factors, block[i].clone(), alpha=-1), prime)
        pivots.append(c)
        used.append(i)
    return block[used], torch.tensor(pivots, dtype=torch.int64, device=block.device)


class Echelon:
    LEAF = 64

    def __init__(self, columns: int, prime: int, device: str) -> None:
        self.prime = prime
        self.columns = columns
        self.device = device
        self.rows = torch.zeros((0, columns), dtype=torch.float64, device=device)
        self.pivots = torch.zeros(0, dtype=torch.int64, device=device)

    @property
    def rank(self) -> int:
        return len(self.pivots)

    def reduce(self, batch: torch.Tensor) -> torch.Tensor:
        if not self.rank:
            return torch.remainder(batch, self.prime)
        return torch.remainder(batch.addmm_(batch[:, self.pivots], self.rows, alpha=-1), self.prime)

    def append(self, new: torch.Tensor, new_pivots: torch.Tensor) -> None:
        if not len(new_pivots):
            return
        if self.rank:
            self.rows = torch.remainder(self.rows.addmm_(self.rows[:, new_pivots], new, alpha=-1), self.prime)
        self.rows = torch.cat([self.rows, new])
        self.pivots = torch.cat([self.pivots, new_pivots])

    def insert(self, batch: torch.Tensor) -> None:
        batch = self.reduce(torch.remainder(batch, self.prime))
        batch = batch[batch.any(dim=1)]
        if not len(batch):
            return
        if len(batch) <= self.LEAF:
            self.append(*leaf_rref(batch, self.prime))
            return
        local = Echelon(self.columns, self.prime, self.device)
        for begin in range(0, len(batch), self.LEAF):
            chunk = local.reduce(batch[begin : begin + self.LEAF].clone())
            chunk = chunk[chunk.any(dim=1)]
            if len(chunk):
                local.append(*leaf_rref(chunk, self.prime))
        self.append(local.rows, local.pivots)


def ladder(root: Path, slug: str, prime: int, degree: int, order: int, batch: int, device: str) -> dict[str, Any]:
    lad = load(root)
    started = time.time()
    timing = {"generators": 0.0, "maps": 0.0, "products": 0.0, "echelon": 0.0}
    ctx = lad.nmod_mpoly_ctx.get(lad.NAMES, prime, lad.Ordering.degrevlex)
    gens = lad.generators(slug, prime, order)
    timing["generators"] = time.time() - started
    low = int(min(min(sum(e) for e in g.to_dict()) for g in gens))
    start = order - low * degree
    if start < 2:
        raise SystemExit(f"order {order} is below {low * degree + 2}")
    source = Monomials(start)
    spaces = {
        key: np.array([source.vector(b) for b in lad.ring_basis(ctx, start, key == "B")]) for key in ("A", "B")
    }
    ranks = []
    for d in range(1, degree + 1):
        current = start + low * d
        target = Monomials(current)
        clock = time.time()
        maps = [multiplication(lad.truncate(ctx, g, current), source, target).T.tocsr() for g in gens]
        timing["maps"] += time.time() - clock
        row = {"degree": d, "order": current}
        for key in ("A", "B"):
            echelon = Echelon(len(target), prime, device)
            space = spaces[key]
            for matrix in maps:
                for begin in range(0, len(space), batch):
                    clock = time.time()
                    block = np.ascontiguousarray((matrix @ space[begin : begin + batch].T).T)
                    timing["products"] += time.time() - clock
                    clock = time.time()
                    echelon.insert(torch.from_numpy(block).to(device))
                    timing["echelon"] += time.time() - clock
            spaces[key] = echelon.rows.cpu().numpy()
            row[key] = echelon.rank
        row["r"] = row["A"] - row["B"]
        row["seconds"] = round(time.time() - started, 1)
        print(json.dumps(row), flush=True)
        ranks.append(row)
        source = target
    return {
        "slug": slug,
        "prime": prime,
        "order": order,
        "generator_order": low,
        "engine": "float64-batched-echelon",
        "batch": batch,
        "device": device,
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
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--threads", type=int, default=0)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    sys.path.insert(0, str(args.root.resolve() / "gororoba_quantum"))
    if args.threads:
        torch.set_num_threads(args.threads)
    record = ladder(args.root.resolve(), args.slug, args.prime, args.degree, args.order, args.batch, args.device)
    if args.out:
        args.out.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(record))


if __name__ == "__main__":
    main()
