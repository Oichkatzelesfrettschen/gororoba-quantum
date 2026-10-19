> Full piece: [https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.utils.qiskit_utils.from_iqm_to_qiskit.html](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.utils.qiskit_utils.from_iqm_to_qiskit.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 907d6674da08971eee37a6dc8cafd999ef15fbbaf2fdbe0247d7307b2bf54cac.

# iqm.error_reduction_tools.utils.qiskit_utils.from_iqm_to_qiskit

iqm.error_reduction_tools.utils.qiskit_utils.from_iqm_to_qiskit(*circuit*, *qubit_index_to_name*, *backend=None*)  
Convert an IQM quantum circuit to a Qiskit quantum circuit.

Parameters:  
- **circuit** ([*TwirledCircuit*](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.utils.circuit_utils.TwirledCircuit.html#iqm.error_reduction_tools.utils.circuit_utils.TwirledCircuit "iqm.error_reduction_tools.utils.circuit_utils.TwirledCircuit")) – IQM twirled quantum circuit.

- **qubit_index_to_name** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*,* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*) – Mapping from qubit indices to names.

- **backend** ([*IQMBackendBase*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "(in IQM client v36.0.0)") *\|* *None*) – Quantum computer to utilise.

Returns:  
Reconstructed Qiskit quantum circuit.

Return type:  
*QuantumCircuit*
