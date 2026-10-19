> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.randomized_benchmarking_common.validate_rb_qubits.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.randomized_benchmarking_common.validate_rb_qubits.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 7eb90195a047eb514e3ccedd6a13d065e97fe60287ae6886bc4544d823a83ead.

# iqm.benchmarks.randomized_benchmarking.randomized_benchmarking_common.validate_rb_qubits

iqm.benchmarks.randomized_benchmarking.randomized_benchmarking_common.validate_rb_qubits(*qubits_array: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\]*, *backend_arg: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [IQMBackendBase](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "(in IQM client v36.0.0)")*) → [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")  
Validate qubit inputs for a Clifford RB experiment.

Parameters:  
- **qubits_array** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]\]*) – The array of qubits

- **backend_arg** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* [*IQMBackendBase*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "(in IQM client v36.0.0)")) – The IQM backend

Raises:  
**ValueError if specified pairs** **of** **qubits are not connected** –

Return type:  
None
