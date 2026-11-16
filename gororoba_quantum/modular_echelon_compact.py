"""Compact host storage for the growing echelon bases of `modular_echelon`, the successor used by fiber_rank_v14.

`modular_echelon.Echelon` keeps a float64 host basis (`flint`) or an int32 device basis (`gpu`). `CompactEchelon`
extends it with `backend="compact"`: pivot columns are implicit unit vectors and only nonpivot coefficients are
retained, as uint16 column panels of COMPACT_COLS columns. An insertion rebuilds one panel at a time and releases the
old panel before the next is touched, so neither removing newly promoted pivot columns nor growing the row count
copies the whole basis; the transient beyond the basis is a few panels (see `insert_panel_bytes`). Arithmetic runs
through float64 tiles of COMPACT_INNER inner columns whose sum is checked against the exact-integer bound. The row
space, pivot order and insertion order equal those of the `flint` backend. The prime range is the one every backend
shares, an odd prime p < PMAX = 2^15 (`check_modulus`); uint16 residues alone admit p <= 2^16 and a 4,096-term float64
tile admits p <= 1,482,911.

`modular_echelon.py` is a digest-pinned dependency of engine v12 and stays byte-identical; the `flint` and `gpu`
backends of `CompactEchelon` run its code unchanged. `new_indices` returns the indices of basis rows with a new pivot
without materializing them.
"""

from __future__ import annotations

import time
from typing import Literal

import numpy as np

from modular_echelon import Backend, Echelon, check_modulus, modular_matmul_exact_bound, rref_flint

StorageBackend = Literal["flint", "compact", "gpu"]

COMPACT_COLS = 1024
COMPACT_INNER = 4096
_ROW_TILE = 128
_RELEASED = np.zeros((0, 0), dtype=np.uint16)


def insert_panel_bytes(block_size: int, chunk: int) -> int:
    """Bytes live beyond the compact basis during one `insert` of at most `chunk` rows into a block of `block_size`
    columns.

    Rebuilding a panel holds the old panel (at most block_size rows), its column-selected copy and the grown panel
    (at most block_size + chunk rows), each of at most COMPACT_COLS uint16 columns. The reduction coefficients
    (block_size x chunk uint16) and the panels already rebuilt while old ones remain add at most block_size x chunk
    uint16 beyond the final basis: with r rows before, k new pivots and n columns, a mixed state holds at most
    (r + k)(n - r - k) + r k coefficients, and (r + k)(n - r - k) <= n^2 / 4. The float64 tiles of
    `_subtract_compact_product` (left cast, right cast and three output-tile arrays) are a fixed term."""
    tiles = 8 * (_ROW_TILE * COMPACT_INNER + COMPACT_INNER * COMPACT_COLS + 3 * _ROW_TILE * COMPACT_COLS)
    return 2 * COMPACT_COLS * (3 * block_size + chunk) + 4 * block_size * chunk + tiles


class CompactEchelon(Echelon):
    """`Echelon` with an additional `compact` backend; `flint` and `gpu` behave as in the base class."""

    def __init__(self, ncols: int, p: int, backend: StorageBackend = "flint"):
        if backend not in ("flint", "compact", "gpu"):
            raise ValueError(f"unknown backend {backend!r}")
        self.compact = backend == "compact"
        if self.compact:
            check_modulus(p)
        base: Backend = "gpu" if backend == "gpu" else "flint"
        super().__init__(ncols, p, base)
        self._compact_cols: list[np.ndarray] = []
        self._compact_parts: list[np.ndarray] = []
        if self.compact:
            self._compact_cols = [
                np.arange(i, min(i + COMPACT_COLS, ncols), dtype=np.int64) for i in range(0, ncols, COMPACT_COLS)
            ]
            self._compact_parts = [np.zeros((0, len(cols)), dtype=np.uint16) for cols in self._compact_cols]

    # ------------------------------------------------------------------ reading the basis
    def rows(self, idx: np.ndarray | list[int] | None) -> np.ndarray:
        """Copy of basis rows `idx`; compact storage materializes only the rows requested, as uint16."""
        if not self.compact:
            return super().rows(idx)
        take = np.arange(self._nrows, dtype=np.int64) if idx is None else np.asarray(idx, dtype=np.int64)
        out = np.zeros((len(take), self.ncols), dtype=np.uint16)
        if len(take):
            out[np.arange(len(take)), self.piv[take]] = 1
            for cols, part in zip(self._compact_cols, self._compact_parts, strict=True):
                out[:, cols] = part[take]
        return out

    def new_indices(self, start: set[int]) -> np.ndarray:
        """Indices of basis rows whose pivot column is not in `start`, without materializing those rows."""
        return np.array([i for i, c in enumerate(self.piv.tolist()) if c not in start], dtype=np.int64)

    def new_rows(self, start: set[int]) -> np.ndarray:
        """Basis rows whose pivot column is not in `start`, in basis order."""
        return self.rows(self.new_indices(start))

    # ------------------------------------------------------------------ reduction and insertion
    def reduce(self, x: np.ndarray) -> np.ndarray:
        """Rows of x reduced by the basis (zero in every pivot column); uint16 for compact storage."""
        return self._reduce_compact(x) if self.compact else super().reduce(x)

    def insert(self, x: np.ndarray, chunk: int) -> np.ndarray:
        """Insert rows; returns the indices (into the basis) of rows whose pivots are new."""
        if not self.compact:
            return super().insert(x, chunk)
        start = set(self.piv.tolist())
        t0 = time.perf_counter()
        for s in range(0, len(x), chunk):
            self._insert_compact(x[s : s + chunk])
        self.insert_seconds += time.perf_counter() - t0
        return self.new_indices(start)

    def _subtract_compact_product(self, out: np.ndarray, a: np.ndarray, b: np.ndarray) -> None:
        """Set uint16 `out` to out - a @ b mod p, with bounded exact float64 tiles."""
        if a.shape[1] != b.shape[0] or out.shape != (a.shape[0], b.shape[1]):
            raise ValueError("compact product shape mismatch")
        for r0 in range(0, len(out), _ROW_TILE):
            r1 = min(r0 + _ROW_TILE, len(out))
            for c0 in range(0, out.shape[1], COMPACT_COLS):
                c1 = min(c0 + COMPACT_COLS, out.shape[1])
                z = out[r0:r1, c0:c1].astype(np.float64)
                for k0 in range(0, a.shape[1], COMPACT_INNER):
                    k1 = min(k0 + COMPACT_INNER, a.shape[1])
                    if not modular_matmul_exact_bound(k1 - k0, self.p):
                        raise RuntimeError(f"inner tile {k1 - k0} leaves the exact float64 range at p = {self.p}")
                    z = np.mod(
                        z - a[r0:r1, k0:k1].astype(np.float64) @ b[k0:k1, c0:c1].astype(np.float64),
                        self.p,
                    )
                out[r0:r1, c0:c1] = z.astype(np.uint16)

    def _reduce_compact(self, x: np.ndarray) -> np.ndarray:
        out = np.mod(x, self.p).astype(np.uint16)
        if self._nrows == 0 or len(out) == 0:
            return out
        coef = out[:, self.piv].copy()
        out[:, self.piv] = 0
        for cols, part in zip(self._compact_cols, self._compact_parts, strict=True):
            panel = out[:, cols].copy()
            self._subtract_compact_product(panel, coef, part)
            out[:, cols] = panel
        return out

    def _insert_compact(self, x: np.ndarray) -> None:
        y = self._reduce_compact(x)
        y = y[np.any(y != 0, axis=1)]
        if len(y) == 0:
            return
        free = np.concatenate(self._compact_cols) if self._compact_cols else np.zeros(0, dtype=np.int64)
        rows, piv_rel = rref_flint(y[:, free].astype(np.int64), self.p)
        rk = len(rows)
        if rk == 0:
            return
        rows = rows.astype(np.uint16)
        q = free[piv_rel]
        pivot_at = {int(pos): i for i, pos in enumerate(piv_rel.tolist())}
        coef = np.zeros((self._nrows, rk), dtype=np.uint16)
        offset = 0
        for part in self._compact_parts:
            for j in range(part.shape[1]):
                slot = pivot_at.get(offset + j)
                if slot is not None and self._nrows:
                    coef[:, slot] = part[:, j]
            offset += part.shape[1]

        # Each old panel is dropped from the list before its replacement is built, so at most one old panel is live
        # beside the rebuilt ones and the basis never exists twice.
        old_cols, old_parts = self._compact_cols, self._compact_parts
        self._compact_cols, self._compact_parts = [], []
        offset = 0
        for index in range(len(old_cols)):
            cols, part = old_cols[index], old_parts[index]
            old_parts[index] = _RELEASED
            keep = np.array([offset + j not in pivot_at for j in range(len(cols))], dtype=bool)
            kept_cols = cols[keep]
            new_rows = rows[:, offset : offset + len(cols)][:, keep]
            grown = np.empty((self._nrows + rk, len(kept_cols)), dtype=np.uint16)
            if self._nrows:
                grown[: self._nrows] = part[:, keep]
                self._subtract_compact_product(grown[: self._nrows], coef, new_rows)
            grown[self._nrows :] = new_rows
            del part
            if len(kept_cols):
                self._compact_cols.append(kept_cols)
                self._compact_parts.append(grown)
            offset += len(cols)
        self._nrows += rk
        self.piv = np.concatenate([self.piv, q.astype(np.int64)])
