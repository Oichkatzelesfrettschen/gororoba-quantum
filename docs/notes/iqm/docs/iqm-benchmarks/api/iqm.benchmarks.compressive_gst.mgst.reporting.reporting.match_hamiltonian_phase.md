> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.reporting.reporting.match_hamiltonian_phase.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.reporting.reporting.match_hamiltonian_phase.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 e933907e99385c5246dc7cb23b82befeeba3a88dd8820e18b9e764b03fddded6.

# iqm.benchmarks.compressive_gst.mgst.reporting.reporting.match_hamiltonian_phase

iqm.benchmarks.compressive_gst.mgst.reporting.reporting.match_hamiltonian_phase(*pauli_coeffs: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *pauli_coeffs_target: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*) → [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")  
Matches the sign of the phase of a target Hamiltonian represented by Pauli coeffs to a measured Hamiltonian.

Parameters:  
- **pauli_coeffs** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – Pauli coefficients of the measured Hamiltonian.

- **pauli_coeffs_target** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – Pauli coefficients of the target Hamiltonian.

Returns:  
Pauli coefficients of the target Hamiltonian with matched phase.

Return type:  
[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")
