> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.utils_gst.basis_transform.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.utils_gst.basis_transform.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 97356dffcb8e9918a5232f99e9d64439160b13a8fcd20cc0f47449a4ffe9252a.

# iqm.benchmarks.compressive_gst.mgst.utils_gst.basis_transform

iqm.benchmarks.compressive_gst.mgst.utils_gst.basis_transform(*matrix: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *in_basis: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") = 'std'*, *out_basis: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") = 'pp'*) → [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")  
Transform a matrix or vector between standard and Pauli bases.

Parameters:  
- **matrix** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – Input matrix (superoperator) or vector (vectorized density matrix) to transform. For vectors: shape (pdim^2,) For matrices: shape (pdim^2, pdim^2)

- **in_basis** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – Input basis, either “std” (standard) or “pp” (Pauli).

- **out_basis** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – Output basis, either “std” (standard) or “pp” (Pauli).

Returns:  
Transformed matrix or vector in the output basis. Returns real part for transformations involving Pauli basis.

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If in_basis or out_basis is not “std” or “pp”.

Return type:  
[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")
