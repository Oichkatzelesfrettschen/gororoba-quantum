> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.reporting.reporting.compute_sparsest_Pauli_Hamiltonian.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.reporting.reporting.compute_sparsest_Pauli_Hamiltonian.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 a63dbc7b0f40c38588d506da1a1677dc43a27b21958614078f03a2350e18367c.

# iqm.benchmarks.compressive_gst.mgst.reporting.reporting.compute_sparsest_Pauli_Hamiltonian

iqm.benchmarks.compressive_gst.mgst.reporting.reporting.compute_sparsest_Pauli_Hamiltonian(*U_set: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*) → [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")  
Takes the matrix logarithms of the given unitaries and returns sparsest Hamiltonian parameters in Pauli basis.

The parametrization is U = exp(-i pi H/2), i.e. H = i log(U)\*2/pi. Different branches in the matrix logarithm lead to different Hamiltonians. This function optimizes over combinations of adding 2\*pi to different eigenvalues, in order arrive at the branch with the Hamiltonian whose Pauli basis representation is the most sparse.

Parameters:  
**U_set** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – A list contining unitary matrices

Returns:  
The full list of Pauli basis coefficients of the Hamiltonian for all gates

Return type:  
[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")

Notes

sqrt(pdim) factor is due to Pauli basis normalization
