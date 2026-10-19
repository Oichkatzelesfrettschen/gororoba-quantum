> Full piece: [https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.utils.qiskit_utils.from_qiskit_to_iqm.html](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.utils.qiskit_utils.from_qiskit_to_iqm.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 ae170d624cdc6502050d703703aa64fafb33a9f06d76320904645ca6ec05dcf1.

# iqm.error_reduction_tools.utils.qiskit_utils.from_qiskit_to_iqm

iqm.error_reduction_tools.utils.qiskit_utils.from_qiskit_to_iqm(*qc*, *backend=None*)  
Convert a Qiskit quantum circuit to IQM format.

Parameters:  
- **qc** (*QuantumCircuit*) – Qiskit quantum circuit to convert.

- **backend** ([*IQMBackendBase*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "(in IQM client v36.0.0)") *\|* *None*) – Optional IQM Qiskit backend for qubit naming.

Returns:  
Converted `qc`, qubit index to name mapping.

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If `backend` is not None or an IQMBackend instance

Return type:  
[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*TwirledCircuit*](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.utils.circuit_utils.TwirledCircuit.html#iqm.error_reduction_tools.utils.circuit_utils.TwirledCircuit "iqm.error_reduction_tools.utils.circuit_utils.TwirledCircuit"), [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"), [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]\]
