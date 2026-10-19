> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.set_coupling_map.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.set_coupling_map.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 1f174fb9f6847a6551409d2dc95c6280db7e2012b5f3d19bbf68983856edbdde.

# iqm.benchmarks.utils.set_coupling_map

iqm.benchmarks.utils.set_coupling_map(*qubits: [Sequence](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]*, *backend: [IQMBackendBase](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "(in IQM client v36.0.0)")*, *physical_layout: [PhysicalLayout](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.PhysicalLayout.html#iqm.benchmarks.utils.PhysicalLayout "iqm.benchmarks.utils.PhysicalLayout") = PhysicalLayout.FIXED*) → CouplingMap  
Set a coupling map according to the specified physical layout.

Parameters:  
- **qubits** ([*Sequence*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – A list of physical qubits to consider.

- **backend** ([*IQMBackendBase*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "(in IQM client v36.0.0)")) – A backend from IQM.

- **physical_layout** ([*PhysicalLayout*](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.PhysicalLayout.html#iqm.benchmarks.utils.PhysicalLayout "iqm.benchmarks.utils.PhysicalLayout")) – A physical layout type to consider. “fixed” sets a coupling map restricted to the input qubits; the results will be constrained to measure those qubits. “batching” sets the coupling map of the backend; the results in a benchmark will be “batched” according to final layouts.

Returns:  
A coupling map according to the specified physical layout.

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If the physical layout is not “fixed” or “batching”.

Return type:  
*CouplingMap*
