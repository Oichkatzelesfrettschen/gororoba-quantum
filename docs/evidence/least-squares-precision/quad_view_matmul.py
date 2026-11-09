"""Reproducers for numpy-quaddtype 1.0.0 matmul: a strided-view operand returns wrong products without an error, and
an empty inner dimension raises RuntimeError("QBLAS operation failed") where NumPy returns zeros."""

import numpy as np
from numpy_quaddtype import QuadPrecDType

a64 = np.arange(48.0).reshape(8, 6)
a = a64.astype(QuadPrecDType())
truth = a64[2:, 1] @ a64[2:, 1:]
view = a[2:, 1] @ a[2:, 1:]
contiguous = np.ascontiguousarray(a[2:, 1]) @ np.ascontiguousarray(a[2:, 1:])
print("float64   ", truth)
print("quad view ", view)
print("quad contig", contiguous)
print("view correct:", bool((view == truth.astype(QuadPrecDType())).all()))
try:
    print("quad empty:", np.ones(0, dtype=QuadPrecDType()) @ np.ones((0, 2), dtype=QuadPrecDType()))
except RuntimeError as exc:
    print("quad empty raises:", exc, "| float64 empty:", np.ones(0) @ np.ones((0, 2)))
