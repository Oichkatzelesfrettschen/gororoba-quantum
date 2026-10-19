> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.utils_gst.average_gate_fidelities.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.utils_gst.average_gate_fidelities.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 bb701a94c6b602d53ea2eb2fecf42ac6dbd704b737be9934f596243d84eed223.

# iqm.benchmarks.compressive_gst.mgst.utils_gst.average_gate_fidelities

iqm.benchmarks.compressive_gst.mgst.utils_gst.average_gate_fidelities(*X1: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *X2: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*) → [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]  
Return the average gate fidelities between gates of two pygsti models.

Parameters:  
- **X1** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – Gate set tensor of shape (Number of Gates, Kraus rank, dimension^2, dimension^2)

- **X2** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – Gate set tensor of shape (Number of Gates, Kraus rank, dimension^2, dimension^2)

Returns:  
Average gate fidelities between all gate pairs gates of the input models

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]
