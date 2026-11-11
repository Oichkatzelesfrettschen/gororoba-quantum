"""Exact F_p echelon operations of gororoba_quantum/modular_echelon.py: the GPU backend against FLINT.

The flint-path tests run everywhere. The device tests need torch, CuPy and a CUDA device and skip otherwise.
"""

from __future__ import annotations

import flint
import numpy as np
import pytest

import modular_echelon as me

P = 32009
P2 = 32029
# ANU QRNG draw-2026-11-08T170257Z, indices 1002 to 1007, one per test matrix family.
TEST_SEEDS = (48017, 49253, 10309, 7251, 10621, 17687)

needs_gpu = pytest.mark.skipif(not me.gpu_available(), reason="no CUDA device with torch and CuPy")


def _check(condition: bool) -> None:
    if not condition:
        raise AssertionError


def _equal(a: np.ndarray, b: np.ndarray) -> None:
    if a.shape != b.shape or not np.array_equal(a, b):
        raise AssertionError(f"arrays differ: shapes {a.shape} and {b.shape}")


def _low_rank(rng: np.random.Generator, m: int, n: int, k: int, p: int, zero_cols: float = 0.0) -> np.ndarray:
    x = rng.integers(0, p, (m, k), dtype=np.int64)
    y = rng.integers(0, p, (k, n), dtype=np.int64)
    if zero_cols:
        y[:, rng.random(n) < zero_cols] = 0
    return (x @ y) % p


def _rank(a: np.ndarray, p: int) -> int:
    if a.size == 0:
        return 0
    return int(flint.nmod_mat(a.shape[0], a.shape[1], a.ravel().tolist(), p).rank())


def _check_rref(a: np.ndarray, rows: np.ndarray, piv: np.ndarray, p: int) -> None:
    """Rows are in reduced echelon form and span the row space of a."""
    rank = _rank(a, p)
    _check(len(piv) == rank == rows.shape[0])
    if rank == 0:
        return
    _check(bool(np.all(np.diff(piv) > 0)))
    _check(bool(np.all(rows[np.arange(rank), piv] == 1)))
    pivot_block = rows[:, piv]
    _check(bool(np.array_equal(pivot_block, np.eye(rank, dtype=np.int64))))
    first = np.argmax(rows != 0, axis=1)
    _check(bool(np.array_equal(first, piv)))
    stacked = np.vstack([a, rows])
    _check(_rank(stacked, p) == rank)


def test_rref_flint_small_known_case() -> None:
    a = np.array([[2, 4, 1, 3], [1, 2, 0, 1], [3, 6, 1, 4], [0, 0, 0, 0]], dtype=np.int64)
    rows, piv = me.rref_flint(a, P)
    _equal(piv, np.array([0, 2]))
    _equal(rows, np.array([[1, 2, 0, 1], [0, 0, 1, 1]], dtype=np.int64))


def test_rref_flint_degenerate_shapes() -> None:
    for shape in ((0, 5), (4, 0), (3, 3)):
        rows, piv = me.rref_flint(np.zeros(shape, dtype=np.int64), P)
        _check(rows.shape == (0, shape[1]) and piv.shape == (0,))


@pytest.mark.parametrize("family", ["full", "low_rank", "zero_columns", "wide", "tall"])
def test_rref_flint_reduced_form(family: str) -> None:
    rng = np.random.default_rng(TEST_SEEDS[0])
    shapes = {"full": (40, 40, 40, 0.0), "low_rank": (60, 50, 12, 0.0), "zero_columns": (50, 90, 20, 0.4)}
    m, n, k, zc = shapes.get(family, (30, 80, 25, 0.0) if family == "wide" else (80, 30, 25, 0.0))
    a = _low_rank(rng, m, n, k, P, zc)
    rows, piv = me.rref_flint(a, P)
    _check_rref(a, rows, piv, P)


def test_echelon_flint_invariants() -> None:
    rng = np.random.default_rng(TEST_SEEDS[1])
    ech = me.Echelon(70, P)
    new_total = 0
    for k in (9, 15, 5):
        x = _low_rank(rng, 40, 70, k, P).astype(np.float64)
        before = len(ech)
        new_total += len(ech.insert(x, chunk=17))
        _check(len(ech) >= before)
    _check(len(ech) == new_total == len(ech.piv) == ech.B.shape[0])
    block = ech.B[:, ech.piv]
    _check(bool(np.array_equal(block, np.eye(len(ech)))))
    reduced = ech.reduce(_low_rank(rng, 20, 70, 6, P).astype(np.float64))
    _check(bool(np.all(reduced[:, ech.piv] == 0)))
    _check(ech.insert(ech.B, chunk=11).size == 0)
    fresh = ech.new_rows({int(c) for c in ech.piv[:-3]})
    _equal(fresh, ech.rows(np.arange(len(ech) - 3, len(ech))))


def test_echelon_compact_equals_flint_insertion_sequence() -> None:
    rng = np.random.default_rng(TEST_SEEDS[5])
    cpu = me.Echelon(173, P)
    compact = me.Echelon(173, P, "compact")
    for k, count in ((13, 47), (29, 61), (17, 38), (70, 83)):
        x = _low_rank(rng, count, 173, k, P, 0.17).astype(np.float64)
        _equal(compact.insert(x, chunk=19), cpu.insert(x, chunk=19))
        _equal(compact.piv, cpu.piv)
        _equal(compact.B, cpu.B)
        _equal(compact.reduce(x[:11]), cpu.reduce(x[:11]))
    start = {int(c) for c in cpu.piv[: len(cpu) // 2]}
    _equal(compact.new_indices(start), cpu.new_indices(start))
    _equal(compact.new_rows(start), cpu.new_rows(start))
    _check(compact.insert(cpu.B[:23], chunk=7).size == 0)


def test_echelon_compact_crosses_storage_panels() -> None:
    rng = np.random.default_rng(TEST_SEEDS[1])
    ncols = me.COMPACT_COLS + 37
    a = _low_rank(rng, 42, ncols, 31, P, 0.2).astype(np.float64)
    want = me.Echelon(ncols, P)
    got = me.Echelon(ncols, P, "compact")
    want.insert(a, chunk=11)
    got.insert(a, chunk=11)
    _equal(got.piv, want.piv)
    _equal(got.B, want.B)


def test_echelon_rejects_unknown_backend() -> None:
    with pytest.raises(ValueError, match="unknown backend"):
        me.Echelon(4, P, "tpu")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="unknown backend"):
        me.rref(np.zeros((2, 2), dtype=np.int64), P, "tpu")  # type: ignore[arg-type]


def test_modulus_checks() -> None:
    for bad in (2, 9, 2**15 + 3, 65537):
        with pytest.raises(ValueError, match="odd prime"):
            me.check_modulus(bad)
    me.check_modulus(P)
    _check(me.modular_matmul_exact_bound(4000, P))
    _check(not me.modular_matmul_exact_bound(10**7, P))


@needs_gpu
@pytest.mark.parametrize("p", [P, P2])
@pytest.mark.parametrize(
    ("m", "n", "k", "zero_cols"),
    [(5, 7, 3, 0.0), (64, 64, 64, 0.0), (300, 700, 200, 0.33), (700, 300, 120, 0.0), (257, 513, 513, 0.0)],
)
def test_rref_gpu_equals_flint(p: int, m: int, n: int, k: int, zero_cols: float) -> None:
    rng = np.random.default_rng(TEST_SEEDS[2])
    a = _low_rank(rng, m, n, k, p, zero_cols)
    want_rows, want_piv = me.rref_flint(a, p)
    got_rows, got_piv = me.rref_gpu(a, p)
    _equal(got_piv, want_piv)
    _equal(got_rows, want_rows)


@needs_gpu
def test_rref_gpu_special_matrices() -> None:
    rng = np.random.default_rng(TEST_SEEDS[3])
    zero = np.zeros((40, 50), dtype=np.int64)
    perm = np.zeros((300, 400), dtype=np.int64)
    perm[rng.permutation(300), rng.permutation(400)[:300]] = rng.integers(1, P, 300)
    rank_one = _low_rank(rng, 90, 600, 1, P)
    sparse = np.zeros((350, 350), dtype=np.int64)
    sparse[rng.integers(0, 350, 900), rng.integers(0, 350, 900)] = rng.integers(1, P, 900)
    for a in (zero, perm, rank_one, sparse):
        want_rows, want_piv = me.rref_flint(a, P)
        got_rows, got_piv = me.rref_gpu(a, P)
        _equal(got_piv, want_piv)
        _equal(got_rows, want_rows)
    _check(me.rref(rank_one, P, "gpu")[1].shape == (1,))


@needs_gpu
def test_rref_gpu_degenerate_shapes() -> None:
    for shape in ((0, 5), (4, 0)):
        rows, piv = me.rref_gpu(np.zeros(shape, dtype=np.int64), P)
        _check(rows.shape == (0, shape[1]) and piv.shape == (0,))


@needs_gpu
def test_device_matmul_long_inner_dimension_matches_integers() -> None:
    rng = np.random.default_rng(TEST_SEEDS[4])
    arith = me.DeviceArithmetic.get(P)
    torch = arith.torch
    inner = me.KMAX + 4100
    x = rng.integers(0, P, (37, inner), dtype=np.int64)
    y = rng.integers(0, P, (inner, 29), dtype=np.int64)
    # exact integer reference in chunks that stay inside int64
    want = np.zeros((37, 29), dtype=np.int64)
    for s in range(0, inner, 2048):
        want = (want + x[:, s : s + 2048] @ y[s : s + 2048]) % P
    got = arith.matmul(
        torch.as_tensor(x, dtype=torch.int32).cuda().contiguous(),
        torch.as_tensor(y, dtype=torch.int32).cuda().contiguous(),
    )
    _equal(got.cpu().numpy().astype(np.int64), want)


@needs_gpu
def test_echelon_gpu_equals_flint_insertion_sequence() -> None:
    rng = np.random.default_rng(TEST_SEEDS[5])
    ncols = 330
    cpu = me.Echelon(ncols, P)
    dev = me.Echelon(ncols, P, "gpu")
    for k, rows in ((20, 150), (60, 200), (30, 90), (150, 400)):
        x = _low_rank(rng, rows, ncols, k, P, 0.2).astype(np.float64)
        fresh_cpu = cpu.insert(x, chunk=64)
        fresh_dev = dev.insert(x, chunk=64)
        _equal(fresh_dev, fresh_cpu)
        _equal(dev.piv, cpu.piv)
        _equal(dev.B, cpu.B)
        _equal(dev.reduce(x[:25]), cpu.reduce(x[:25]))
    _check(len(dev) == len(cpu) > 0)
    start = {int(c) for c in cpu.piv[: len(cpu) // 2]}
    _equal(dev.new_rows(start), cpu.new_rows(start))
    _check(dev.insert(cpu.B[:50], chunk=32).size == 0)
