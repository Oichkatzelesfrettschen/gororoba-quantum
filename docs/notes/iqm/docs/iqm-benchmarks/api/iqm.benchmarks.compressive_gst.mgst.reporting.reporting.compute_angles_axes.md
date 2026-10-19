> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.reporting.reporting.compute_angles_axes.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.reporting.reporting.compute_angles_axes.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 10b29fc4d9784c5e328e24183b3dbfc5cf8464ad158707d4bed969754e090a88.

# iqm.benchmarks.compressive_gst.mgst.reporting.reporting.compute_angles_axes

iqm.benchmarks.compressive_gst.mgst.reporting.reporting.compute_angles_axes(*U_set: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *alternative_phase: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") = False*) → [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\], [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")\], [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")\]  
Takes the matrix logarithm of the given unitaries and returns the Hamiltonian parameters.

The parametrization is U = exp(-i pi H/2), i.e. H = i log(U)\*2/pi

Parameters:  
- **U_set** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – A list contining unitary matrices

- **alternative_phase** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Whether an attempt should be made to report more intuitive rotations, for example a rotation of 3 pi/2 around the -X axis would be turned into a pi/2 rotation around the X-axis.

Returns:  
- The rotation angle on the Bloch sphere for all gates

- The normalized rotation axes in the Pauli basis for all gates

- The full list of Pauli basis coefficients of the Hamiltonian for all gates

Return type:  
[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\], [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")\], [*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")\]

Notes

sqrt(pdim) factor is due to Pauli basis normalization
