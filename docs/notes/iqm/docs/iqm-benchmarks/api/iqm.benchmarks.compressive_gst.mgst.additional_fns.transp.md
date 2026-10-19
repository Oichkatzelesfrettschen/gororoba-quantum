> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.additional_fns.transp.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.additional_fns.transp.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 f45c881130f7725ef64bd8db7e179b9e0cbefa4baef1a0d96bf78109ee0a19bc.

# iqm.benchmarks.compressive_gst.mgst.additional_fns.transp

iqm.benchmarks.compressive_gst.mgst.additional_fns.transp(*dim1: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *dim2: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*) → [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")  
Superoperator of a map that performs the transpose operation.

Parameters:  
- **dim1** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – First dimension of the matrix to be transposed

- **dim2** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Second dimension of the matrix to be transposed

Returns:  
Transpose superoperator that turns a dim1xdim2 matrix into a dim2xdim1 matrix

Return type:  
[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")

Notes

The projection is done with respect to the canonical metrik.
