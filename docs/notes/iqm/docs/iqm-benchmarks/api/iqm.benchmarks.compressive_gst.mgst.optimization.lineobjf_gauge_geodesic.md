> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.optimization.lineobjf_gauge_geodesic.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.optimization.lineobjf_gauge_geodesic.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 1a5ff1e0cc0d200eebd6c9b61172691e3fded8f1f841753b195000abdb49d1bc.

# iqm.benchmarks.compressive_gst.mgst.optimization.lineobjf_gauge_geodesic

iqm.benchmarks.compressive_gst.mgst.optimization.lineobjf_gauge_geodesic(*a: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*, *Delta: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *U: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *gates: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")\]*, *target_gates: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")\]*, *weights: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")*) → [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")  
Compute objective function at position on geodesic for gauge optimization Parameters.

Parameters:  
- **a** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – Geodesic curve parameter

- **Delta** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – Element of the tangent space at U and local direction of the geodesic

- **U** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – Current gauge transformation matrix

- **gates** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*\]*) – Current gate, POVM, and state estimates \[X, E, rho\]

- **target_gates** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*\]*) – Target gates, POVM, and state \[X_target, E_target, rho_target\]

- **weights** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]* *\|* *None*) – Weights for gates and SPAM

Returns:  
Objective function value at new position along the geodesic

Return type:  
[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")
