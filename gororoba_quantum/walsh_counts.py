"""Exact parity numerators of a nonnegative integer histogram in linear storage.

The coordinate order is unchanged: coefficient m is
sum_x counts[x] * (-1)**popcount(x & m). The butterfly stages are dependent;
each stage uses batched NumPy operations across all independent butterflies.
The signed-int64 bound is checked before arithmetic, not after overflow.
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np

INT64_MAX = int(np.iinfo(np.int64).max)


def parity_numerators(counts: Sequence[int] | np.ndarray) -> np.ndarray:
    """Return all unnormalized Walsh coefficients, without mutating counts.

    The histogram has a nonzero power-of-two length, integer entries, and a
    total at most INT64_MAX. Every intermediate magnitude is bounded by that
    total. O(n log n) integer work and O(n) auxiliary storage replace the
    O(n**2) parity-sign matrix. The zero-bit histogram of length one is valid.

    Raises ValueError for malformed histograms and OverflowError if the
    exact histogram total cannot be represented in signed int64.
    """
    raw = np.asarray(counts)
    if raw.ndim != 1 or raw.size == 0 or raw.size & (raw.size - 1):
        raise ValueError("counts need a nonempty power-of-two length")
    # Python integers beyond uint64 arrive as an object array; each entry is checked as an exact integer.
    entries = raw.tolist()
    if raw.dtype.kind not in "iuO" or any(type(v) is not int or v < 0 for v in entries):
        raise ValueError("counts need nonnegative integers, not floats or booleans")
    total = sum(entries)
    if total > INT64_MAX:
        raise OverflowError("histogram total exceeds signed int64")
    values = np.array(entries, dtype=np.int64)
    half = 1
    while half < values.size:
        blocks = values.reshape(-1, 2 * half)
        left = blocks[:, :half].copy()
        right = blocks[:, half:].copy()
        blocks[:, :half] = left + right
        blocks[:, half:] = left - right
        half *= 2
    return values
