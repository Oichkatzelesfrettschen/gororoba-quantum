> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.utils_gst.std2pp.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.utils_gst.std2pp.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 cee9574e4b73877d060d814b778863f2f55ada30f6bbb49783a55ddc99d844a5.

# iqm.benchmarks.compressive_gst.mgst.utils_gst.std2pp

iqm.benchmarks.compressive_gst.mgst.utils_gst.std2pp(*X: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *E: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *rho: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*) → [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)"), [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)"), [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")\]  
Basis change of an mGST model from the standard basis to the Pauli basis.

Parameters:  
- **X** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – Gate set tensor of shape (Number of Gates, Kraus rank, dimension^2, dimension^2) in standard basis

- **E** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – POVM matrix of shape (#POVM elements, dimension^2) in standard basis

- **rho** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – Initial state vector of shape (dimension^2) in standard basis

Returns:  
Gate set tensor of shape (Number of Gates, Kraus rank, dimension^2, dimension^2) in Pauli basis Epp: POVM matrix of shape (#POVM elements, dimension^2) in Pauli basis rhopp: Initial state vector of shape (dimension^2) in Pauli basis

Return type:  
Xpp
