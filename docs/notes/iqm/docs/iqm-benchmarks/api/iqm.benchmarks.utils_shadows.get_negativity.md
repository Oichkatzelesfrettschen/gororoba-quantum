> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils_shadows.get_negativity.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils_shadows.get_negativity.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 ed35a336e03416b8f25c2f49b27a420f1e05bda31152fcc55479b18dec1cfc8a.

# iqm.benchmarks.utils_shadows.get_negativity

iqm.benchmarks.utils_shadows.get_negativity(*rho: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *n_qubits_a: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *n_qubits_b: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*) → [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")  
Computes the negativity of a given density matrix.

Note that a negativity \>0 is only a necessary and sufficient condition for entanglement if n_qubits_a = n_qubits_b = 1. For more qubits per subsystems it is merely a necessary condition.

Parameters:  
- **rho** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – Density matrix.

- **n_qubits_a** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Number of qubits for subsystem A.

- **n_qubits_b** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Number of qubits for subsystem B.

Returns:  
The negativity of the input density matrix.

Return type:  
[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")
