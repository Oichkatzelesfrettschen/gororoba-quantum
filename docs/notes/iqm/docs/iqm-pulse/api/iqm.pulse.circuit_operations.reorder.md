> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.circuit_operations.reorder.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.circuit_operations.reorder.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 d939b60ddddf96f10bd8a4511d5b21cf63a0bc930ea0310e95809e9d6c84e1ac.

# iqm.pulse.circuit_operations.reorder

iqm.pulse.circuit_operations.reorder(*A*, *perm*)  
Permutes the order of the qubits in an n-qubit operator matrix.

Parameters:  
- **A** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – Matrix of an operator acting on the state space of `n` qubits, to be reordered.

- **perm** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – Permutation vector for the `n` qubits. `perm[k]` is the new index for the k:th qubit in the old ordering. For example, `reorder(kron(A, B, C)), [2, 0, 1]) == kron(B, C, A)`.

Returns:  
Reordered `A`.

Return type:  
[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")
