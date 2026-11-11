"""Bounded deterministic checks of the exact integer Walsh transform."""

from __future__ import annotations

import numpy as np
import pytest

from walsh_counts import INT64_MAX, parity_numerators


def _check(condition: object, message: str) -> None:
    if not condition:
        raise AssertionError(message)


@pytest.mark.parametrize("bits", [0, 1, 2, 3, 6, 8])
def test_dense_reference_and_input_preservation(bits: int) -> None:
    size = 1 << bits
    counts = (np.arange(size, dtype=np.int64) ** 2 + 3) % 17
    before = counts.copy()
    coordinates = np.arange(size, dtype=np.int64)
    overlap = coordinates[:, None] & coordinates[None, :]
    parity = np.bitwise_count(overlap.astype(np.uint64)) & 1
    signs = 1 - 2 * parity.astype(np.int64)
    expected = counts @ signs
    _check(np.array_equal(parity_numerators(counts), expected), "dense and butterfly coefficients differ")
    _check(np.array_equal(counts, before), "transform mutated its input")


def test_large_histogram_needs_no_dense_sign_matrix() -> None:
    # 8 early/terminal pairs: the old sign matrix alone occupied 32 GiB.
    counts = np.zeros(1 << 16, dtype=np.int64)
    counts[0] = 7
    _check(np.all(parity_numerators(counts) == 7), "zero-coordinate point mass has nonconstant parities")


def test_int64_boundary_and_unsigned_input() -> None:
    _check(parity_numerators([INT64_MAX, 0]).tolist() == [INT64_MAX, INT64_MAX], "boundary changed")
    _check(parity_numerators(np.array([0, 2], dtype=np.uint64)).tolist() == [2, -2], "unsigned input changed")
    with pytest.raises(OverflowError):
        parity_numerators([INT64_MAX, 1])
    with pytest.raises(OverflowError):
        parity_numerators(np.array([1 << 63, 0], dtype=np.uint64))


@pytest.mark.parametrize("counts", [[], [1, 2, 3], [[1, 2]], [-1, 2], [1.0, 2.0], [True, False]])
def test_invalid_histograms_are_refused(counts: object) -> None:
    with pytest.raises(ValueError):
        parity_numerators(counts)  # type: ignore[arg-type]
