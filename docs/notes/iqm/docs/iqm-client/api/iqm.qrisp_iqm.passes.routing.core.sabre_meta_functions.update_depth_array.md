> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.sabre_meta_functions.update_depth_array.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.sabre_meta_functions.update_depth_array.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 bf2a6060ffe55eaaaafded0ca7172d505a9da4b6e16a6e2e7813cac20b1d5109.

# iqm.qrisp_iqm.passes.routing.core.sabre_meta_functions.update_depth_array

iqm.qrisp_iqm.passes.routing.core.sabre_meta_functions.update_depth_array(*instruction_list: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[int16, int16, int16\]\]*, *depth_array: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*) → [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")  
Update the per-physical-qubit depth array from a compiled instruction list.

Processes a list of instruction tuples and updates the depth tracking array in-place. Two-qubit gates increment the depth of both qubits involved; SWAP gates receive a larger increment when both qubits are at the same depth (used as a “booster pad” to encourage efficient swap chains).

Parameters:  
- **instruction_list** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[int16,* *int16,* *int16\]\]*) – Instructions produced by SABRE.

- **depth_array** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – Per-physical-qubit depth array to update in-place.

Return type:  
None
