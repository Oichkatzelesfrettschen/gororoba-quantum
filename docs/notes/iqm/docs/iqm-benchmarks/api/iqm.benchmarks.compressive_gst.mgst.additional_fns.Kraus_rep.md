> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.additional_fns.Kraus_rep.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.additional_fns.Kraus_rep.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 3080f89ba2af2ba091cfbf1bc85a945dbb7417ac099cc7927e21877a34b5b12b.

# iqm.benchmarks.compressive_gst.mgst.additional_fns.Kraus_rep

iqm.benchmarks.compressive_gst.mgst.additional_fns.Kraus_rep(*X: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *d: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *pdim: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *rK: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*) → [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")  
Compute the Kraus representations for all gates in the gate set.

Parameters:  
- **X** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – Current gate estimate

- **d** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Number of gates

- **pdim** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Physical dimension

- **rK** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Target Kraus rank

Returns:  
Each subarray along the first axis contains a set of Kraus operators. The second axis enumerates Kraus operators for a gate specified by the first axis.

Return type:  
[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")

Notes

The Kraus representation is obtained from a singular value decomposition of the Choi matrix. If parameter rK is smaller than the true rank of the Choi matrix, a rank rK approximation is used. Approximations are only CPT in the special case where the original gate was already of rank \<= rK.
