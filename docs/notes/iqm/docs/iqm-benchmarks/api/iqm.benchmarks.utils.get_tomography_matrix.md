> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.get_tomography_matrix.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.get_tomography_matrix.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 80568b5a23475f743322ece169bd018e766ee4ddc8b76fa04a646987ab609861.

# iqm.benchmarks.utils.get_tomography_matrix

iqm.benchmarks.utils.get_tomography_matrix(*pauli_expectations: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]*) → [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")  
Reconstructs a density matrix from given Pauli expectations.

Parameters:  
**pauli_expectations** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]*) – A dictionary of Pauli expectations, with keys being Pauli strings.

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If not all 4\*\*n Pauli expectations are specified.

Returns:  
A tomographically reconstructed density matrix.

Return type:  
[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")
