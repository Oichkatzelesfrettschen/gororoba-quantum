> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.circuit_operations.reshape_unitary.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.circuit_operations.reshape_unitary.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 e440bb5d5396ef21251df88caf22ce13320617e8b1c6d6cf27eeadba5c7ed3c5.

# iqm.pulse.circuit_operations.reshape_unitary

iqm.pulse.circuit_operations.reshape_unitary(*unitary*, *indices*, *n_qubits*)  
Extend a unitary propagator to act on a larger system.

Given a unitary matrix acting on N qubits, indices of N qubits in a larger Hilbert space, and the number of qubits in that Hilbert space, calculate a unitary acting on the larger Hilbert space, which acts as the given unitary on the N selected qubits and as identity on the others.

Parameters:  
- **unitary** ([*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*,* *...\],* *...\]*) – original unitary as a nested tuple for hashing & caching purposes.

- **indices** ([*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*,* *...\]*) – qubit indices in the larger Hilbert space, all in `range(num_qubits)`

- **n_qubits** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – number of qubits in the larger Hilbert space

Returns:  
Unitary matrix acting as `unitary` on the selected qubits in the larger Hilbert space.

Return type:  
[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")
