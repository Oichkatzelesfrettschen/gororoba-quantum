"""Compact uint16 echelon storage of gororoba_quantum/modular_echelon_compact.py against FLINT.

Every matrix is built by integer arithmetic, so no random draw is consumed.
"""

from __future__ import annotations

import tracemalloc

import numpy as np
import pytest

import modular_echelon as me
import modular_echelon_compact as mec

P = 32009


def _check(condition: bool, message: str = "") -> None:
    if not condition:
        raise AssertionError(message)


def _equal(a: np.ndarray, b: np.ndarray) -> None:
    if a.shape != b.shape or not np.array_equal(a, b):
        raise AssertionError(f"arrays differ: shapes {a.shape} and {b.shape}")


def _powers(nodes: np.ndarray, count: int, p: int) -> np.ndarray:
    """Rows (node^k mod p) for k < count; distinct nodes below p give full rank min(len(nodes), count)."""
    out = np.empty((len(nodes), count), dtype=np.int64)
    out[:, 0] = 1
    for k in range(1, count):
        out[:, k] = (out[:, k - 1] * nodes) % p
    return out


def _structured(rows: int, cols: int, rank: int, offset: int, p: int = P, zero_stride: int = 0) -> np.ndarray:
    """A deterministic residue matrix of rank `rank` (before zeroing columns) whose row space is spanned by the
    column powers x^offset .. x^(offset + rank - 1); disjoint exponent ranges give independent row spaces."""
    left = _powers(np.arange(rows, dtype=np.int64) + 1, rank, p)
    right = _powers(np.arange(cols, dtype=np.int64) + 1, offset + rank, p)[:, offset:].T.copy()
    if zero_stride:
        right[:, ::zero_stride] = 0
    return ((left @ right) % p).astype(np.float64)


def _vandermonde(first_node: int, count: int, cols: int, p: int = P) -> np.ndarray:
    """Rows (node^j mod p) for consecutive nodes; distinct nodes give full row rank up to `cols`."""
    return _powers(np.arange(first_node, first_node + count, dtype=np.int64) % p, cols, p).astype(np.float64)


def _equal_to_rref(ech: mec.CompactEchelon, stacked: np.ndarray, p: int) -> None:
    """The basis, ordered by pivot column, is the unique FLINT `nmod_mat.rref` of every row inserted."""
    rows, piv = me.rref_flint(stacked.astype(np.int64), p)
    order = np.argsort(ech.piv)
    _equal(ech.piv[order], piv)
    _equal(ech.B[order].astype(np.int64), rows)


def test_compact_equals_flint_insertion_sequence() -> None:
    cpu = mec.CompactEchelon(173, P)
    compact = mec.CompactEchelon(173, P, "compact")
    for offset, (k, count) in zip((0, 9, 31, 55), ((13, 47), (29, 61), (17, 38), (70, 83)), strict=True):
        x = _structured(count, 173, k, offset, zero_stride=offset % 5 + 4)
        _equal(compact.insert(x, chunk=19), cpu.insert(x, chunk=19))
        _equal(compact.piv, cpu.piv)
        _equal(compact.B, cpu.B)
        _equal(compact.reduce(x[:11]), cpu.reduce(x[:11]))
    start = {int(c) for c in cpu.piv[: len(cpu) // 2]}
    _equal(compact.new_indices(start), cpu.new_indices(start))
    _equal(compact.new_rows(start), cpu.new_rows(start))
    _check(compact.insert(cpu.B[:23], chunk=7).size == 0)


def test_compact_crosses_storage_panels() -> None:
    ncols = mec.COMPACT_COLS + 37
    a = _structured(42, ncols, 31, 3, zero_stride=5)
    want = mec.CompactEchelon(ncols, P)
    got = mec.CompactEchelon(ncols, P, "compact")
    want.insert(a, chunk=11)
    got.insert(a, chunk=11)
    _equal(got.piv, want.piv)
    _equal(got.B, want.B)


@pytest.mark.parametrize("p", [32769, 32771, 65521, 65537])
def test_compact_rejects_moduli_outside_the_shared_range(p: int) -> None:
    """uint16 residues and 4,096-term float64 tiles would admit more, but every backend shares p < PMAX = 2^15."""
    with pytest.raises(ValueError, match="odd prime below"):
        mec.CompactEchelon(8, p, "compact")
    me.Echelon(8, 65537)


def test_compact_tile_width_stays_inside_the_exact_float64_range_for_every_accepted_prime() -> None:
    """The tile width COMPACT_INNER and the largest accepted prime keep every float64 tile sum below 2^53."""
    _check(me.modular_matmul_exact_bound(mec.COMPACT_INNER, me.PMAX - 1))
    _check(not me.modular_matmul_exact_bound(2**24, me.PMAX - 1))


def test_compact_accepts_the_largest_prime_below_the_bound() -> None:
    p = 32749
    _check(me.is_odd_prime(p) and p < me.PMAX and not me.is_odd_prime(me.PMAX + 1))
    x = _structured(30, 60, 11, 4, p)
    cpu, compact = mec.CompactEchelon(60, p), mec.CompactEchelon(60, p, "compact")
    _equal(compact.insert(x, chunk=9), cpu.insert(x, chunk=9))
    _equal(compact.B, cpu.B)


def test_compact_tiles_inner_dimension_and_panels_against_flint_rref(monkeypatch: pytest.MonkeyPatch) -> None:
    """A tile width of 8 and a panel width of 16 put the basis rank (37) above one tile and across three panels."""
    monkeypatch.setattr(mec, "COMPACT_INNER", 8)
    monkeypatch.setattr(mec, "COMPACT_COLS", 16)
    ncols = 70
    batches = [_structured(30, ncols, k, offset) for offset, k in ((0, 11), (11, 19), (30, 7))]
    compact, cpu = mec.CompactEchelon(ncols, P, "compact"), mec.CompactEchelon(ncols, P)
    _check(len(compact._compact_cols) >= 4)
    for batch in batches:
        _equal(compact.insert(batch, chunk=10), cpu.insert(batch, chunk=10))
    _check(len(compact) > 3 * mec.COMPACT_INNER)
    _equal_to_rref(compact, np.vstack(batches), P)
    probe = _structured(25, ncols, 9, 5)
    _equal(compact.reduce(probe), cpu.reduce(probe))


def test_compact_rows_follow_the_requested_order(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(mec, "COMPACT_COLS", 16)
    x = _structured(40, 70, 25, 6)
    compact, cpu = mec.CompactEchelon(70, P, "compact"), mec.CompactEchelon(70, P)
    compact.insert(x, chunk=13)
    cpu.insert(x, chunk=13)
    take = np.array([7, 2, 20, 0, 2])
    _equal(compact.rows(take), cpu.rows(take).astype(np.uint16))
    _equal(compact.rows([]), cpu.rows(np.zeros(0, dtype=np.int64)).astype(np.uint16))


def test_compact_reduces_inputs_outside_the_residue_range() -> None:
    x = _structured(30, 64, 12, 7)
    compact, cpu = mec.CompactEchelon(64, P, "compact"), mec.CompactEchelon(64, P)
    for shift in (-2 * P, 5 * P, 0):
        _equal(compact.insert(x + shift, chunk=11), cpu.insert(x + shift, chunk=11))
        _equal(compact.B, cpu.B)
    _equal(compact.reduce(x - 3 * P), cpu.reduce(x - 3 * P))


def test_compact_refuses_an_inexact_tile(monkeypatch: pytest.MonkeyPatch) -> None:
    compact = mec.CompactEchelon(40, P, "compact")
    compact.insert(_structured(12, 40, 5, 8), chunk=6)
    monkeypatch.setattr(mec, "modular_matmul_exact_bound", lambda inner, p: False)
    with pytest.raises(RuntimeError, match="exact float64 range"):
        compact.reduce(np.ones((2, 40)))


def test_unknown_backend_is_refused() -> None:
    with pytest.raises(ValueError, match="unknown backend"):
        mec.CompactEchelon(4, P, "tpu")  # type: ignore[arg-type]


def test_flint_and_gpu_labels_run_the_base_class_code() -> None:
    """Only `compact` changes storage; the other labels keep the float64 host basis of modular_echelon."""
    x = _structured(20, 50, 9, 9)
    base, derived = me.Echelon(50, P), mec.CompactEchelon(50, P)
    _equal(derived.insert(x, chunk=7), base.insert(x, chunk=7))
    _equal(derived.B, base.B)
    _equal(derived.new_indices(set()), np.arange(len(base), dtype=np.int64))
    _equal(derived.new_indices(set(base.piv.tolist())), np.zeros(0, dtype=np.int64))


def test_insert_releases_each_old_panel_before_the_next_is_rebuilt(monkeypatch: pytest.MonkeyPatch) -> None:
    """Growing an 800-row basis by three rows leaves a transient far below one copy of the basis.

    Without the release every old panel stays alive while every grown panel is built, and the traced peak rises by
    one full basis."""
    monkeypatch.setattr(mec, "COMPACT_COLS", 8)
    ncols = 1600
    batches = [_vandermonde(1 + 200 * i, 200, ncols) for i in range(4)]
    second = _vandermonde(1001, 3, ncols)
    cpu = mec.CompactEchelon(ncols, P)
    for batch in batches:
        cpu.insert(batch, chunk=200)
    compact = mec.CompactEchelon(ncols, P, "compact")
    for batch in batches:
        compact.insert(batch, chunk=200)
    basis_bytes = sum(part.nbytes for part in compact._compact_parts)
    tracemalloc.start()
    try:
        # Copies made under tracing put the basis in the traced total, so freeing a panel lowers it.
        compact._compact_parts = [part.copy() for part in compact._compact_parts]
        before = tracemalloc.get_traced_memory()[0]
        tracemalloc.reset_peak()
        grown = compact.insert(second, chunk=3)
        peak = tracemalloc.get_traced_memory()[1] - before
    finally:
        tracemalloc.stop()
    _equal(grown, cpu.insert(second, chunk=3))
    _check(len(grown) == 3 and basis_bytes > 1_000_000, f"basis {basis_bytes} bytes, {len(grown)} new pivots")
    _check(peak < basis_bytes // 2, f"insert peaked {peak} bytes above a {basis_bytes}-byte basis")
    _equal_to_rref(compact, np.vstack([*batches, second]), P)


@pytest.mark.audit
def test_compact_crosses_the_default_inner_tile_against_flint_rref() -> None:
    """Rank 4,300 puts the reduction coefficients across the 4,096-term tile; FLINT rref is the reference."""
    first, second = _vandermonde(1, 4300, 4400), _vandermonde(5001, 200, 4400)
    compact = mec.CompactEchelon(4400, P, "compact")
    compact.insert(first, chunk=4300)
    compact.insert(second, chunk=200)
    _check(len(compact) > mec.COMPACT_INNER)
    _equal_to_rref(compact, np.vstack([first, second]), P)
