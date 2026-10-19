> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.utils_gst.pp2std.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.utils_gst.pp2std.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 9e79242f60e467f920460861d0deb41e6b4da5b1a138728b9c1fd34e4d6afe09.

# iqm.benchmarks.compressive_gst.mgst.utils_gst.pp2std

iqm.benchmarks.compressive_gst.mgst.utils_gst.pp2std(*Xpp: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *Epp: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *rhopp: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*) → [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)"), [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)"), [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")\]  
Basis change of an mGST model from the Pauli basis to the standard basis.

Parameters:  
- **Xpp** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – Gate set tensor of shape (Number of Gates, Kraus rank, dimension^2, dimension^2) in Pauli basis

- **Epp** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – POVM matrix of shape (#POVM elements, dimension^2) in Pauli basis

- **rhopp** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – Initial state vector of shape (dimension^2) in Pauli basis

Returns:  
Gate set tensor of shape (Number of Gates, Kraus rank, dimension^2, dimension^2) in standard basis E: POVM matrix of shape (#POVM elements, dimension^2) in standard basis rho: Initial state vector of shape (dimension^2) in standard basis

Return type:  
X
