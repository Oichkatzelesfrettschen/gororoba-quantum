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


def _equal_to_rref(ech: me.Echelon, stacked: np.ndarray, p: int) -> None:
    """The basis, ordered by pivot column, is the unique FLINT `nmod_mat.rref` of every row inserted."""
    rows, piv = me.rref_flint(stacked.astype(np.int64), p)
    order = np.argsort(ech.piv)
    _equal(ech.piv[order], piv)
    _equal(ech.B[order].astype(np.int64), rows)


@pytest.mark.parametrize("p", [32769, 32771, 65521, 65537])
def test_echelon_compact_rejects_moduli_outside_the_shared_range(p: int) -> None:
    """uint16 residues and 4,096-term float64 tiles would admit more, but every backend shares p < PMAX = 2^15."""
    with pytest.raises(ValueError, match="odd prime below"):
        me.Echelon(8, p, "compact")
    me.Echelon(8, 65537)


def test_compact_tile_width_stays_inside_the_exact_float64_range_for_every_accepted_prime() -> None:
    """The tile width COMPACT_INNER and the largest accepted prime keep every float64 tile sum below 2^53."""
    _check(me.modular_matmul_exact_bound(me.COMPACT_INNER, me.PMAX - 1))
    _check(not me.modular_matmul_exact_bound(2**24, me.PMAX - 1))


def test_echelon_compact_accepts_the_largest_prime_below_the_bound() -> None:
    p = 32749
    _check(me.is_odd_prime(p) and p < me.PMAX and not me.is_odd_prime(me.PMAX + 1))
    rng = np.random.default_rng(TEST_SEEDS[2])
    x = _low_rank(rng, 30, 60, 11, p).astype(np.float64)
    cpu, compact = me.Echelon(60, p), me.Echelon(60, p, "compact")
    _equal(compact.insert(x, chunk=9), cpu.insert(x, chunk=9))
    _equal(compact.B, cpu.B)


def test_echelon_compact_tiles_inner_dimension_and_panels_against_flint_rref(monkeypatch: pytest.MonkeyPatch) -> None:
    """A tile width of 8 and a panel width of 16 put the basis rank (37) above one tile and across three panels."""
    monkeypatch.setattr(me, "COMPACT_INNER", 8)
    monkeypatch.setattr(me, "COMPACT_COLS", 16)
    rng = np.random.default_rng(TEST_SEEDS[2])
    ncols = 70
    batches = [_low_rank(rng, 30, ncols, k, P, 0.1).astype(np.float64) for k in (11, 19, 7)]
    compact, cpu = me.Echelon(ncols, P, "compact"), me.Echelon(ncols, P)
    _check(len(compact._compact_cols) >= 4)
    for batch in batches:
        _equal(compact.insert(batch, chunk=10), cpu.insert(batch, chunk=10))
    _check(len(compact) > 3 * me.COMPACT_INNER)
    _equal_to_rref(compact, np.vstack(batches), P)
    probe = _low_rank(rng, 25, ncols, 9, P).astype(np.float64)
    _equal(compact.reduce(probe), cpu.reduce(probe))


def test_echelon_compact_rows_follow_the_requested_order(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(me, "COMPACT_COLS", 16)
    rng = np.random.default_rng(TEST_SEEDS[3])
    x = _low_rank(rng, 40, 70, 25, P).astype(np.float64)
    compact, cpu = me.Echelon(70, P, "compact"), me.Echelon(70, P)
    compact.insert(x, chunk=13)
    cpu.insert(x, chunk=13)
    take = np.array([7, 2, 20, 0, 2])
    _equal(compact.rows(take), cpu.rows(take).astype(np.uint16))
    _equal(compact.rows([]), cpu.rows(np.zeros(0, dtype=np.int64)).astype(np.uint16))


def test_echelon_compact_reduces_inputs_outside_the_residue_range() -> None:
    rng = np.random.default_rng(TEST_SEEDS[4])
    x = _low_rank(rng, 30, 64, 12, P).astype(np.float64)
    compact, cpu = me.Echelon(64, P, "compact"), me.Echelon(64, P)
    for shift in (-2 * P, 5 * P, 0):
        _equal(compact.insert(x + shift, chunk=11), cpu.insert(x + shift, chunk=11))
        _equal(compact.B, cpu.B)
    _equal(compact.reduce(x - 3 * P), cpu.reduce(x - 3 * P))


def test_echelon_compact_refuses_an_inexact_tile(monkeypatch: pytest.MonkeyPatch) -> None:
    compact = me.Echelon(40, P, "compact")
    compact.insert(_low_rank(np.random.default_rng(TEST_SEEDS[5]), 12, 40, 5, P).astype(np.float64), chunk=6)
    monkeypatch.setattr(me, "modular_matmul_exact_bound", lambda inner, p: False)
    with pytest.raises(RuntimeError, match="exact float64 range"):
        compact.reduce(np.ones((2, 40)))


@pytest.mark.audit
def test_echelon_compact_crosses_the_default_inner_tile_against_flint_rref() -> None:
    """Rank 4,250 puts the reduction coefficients across the 4,096-term tile; FLINT rref is the reference."""
    rng = np.random.default_rng(TEST_SEEDS[0])

    def rows(count: int, rank: int) -> np.ndarray:
        left = rng.integers(0, P, (count, rank)).astype(np.float64)
        right = rng.integers(0, P, (rank, 4400)).astype(np.float64)
        return np.mod(left @ right, P)

    first, second = rows(4300, 4250), rows(200, 90)
    compact = me.Echelon(4400, P, "compact")
    compact.insert(first, chunk=4300)
    compact.insert(second, chunk=200)
    _check(len(compact) > me.COMPACT_INNER)
    _equal_to_rref(compact, np.vstack([first, second]), P)


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
