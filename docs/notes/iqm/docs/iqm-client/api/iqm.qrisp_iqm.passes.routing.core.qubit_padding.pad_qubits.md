> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.qubit_padding.pad_qubits.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.qubit_padding.pad_qubits.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 4ce4b51bfaf101254fb108f21e65997b9137e8f9caf780c246f83593e91c6a10.

# iqm.qrisp_iqm.passes.routing.core.qubit_padding.pad_qubits

iqm.qrisp_iqm.passes.routing.core.qubit_padding.pad_qubits(*qc: QuantumCircuit*, *n_qubits: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*) → [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[Qubit\]  
Pad a quantum circuit in-place until it holds the given number of qubits.

The padding counter continues from the padding qubits already present in `qc`, so chaining layout passes never produces duplicate qubit names.

Parameters:  
- **qc** (*QuantumCircuit*) – The circuit to pad. Modified in-place.

- **n_qubits** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The desired qubit count. If `qc` already holds at least that many qubits, nothing is added.

Returns:  
The freshly created qubits, in the order they were appended.

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[*Qubit*\]
