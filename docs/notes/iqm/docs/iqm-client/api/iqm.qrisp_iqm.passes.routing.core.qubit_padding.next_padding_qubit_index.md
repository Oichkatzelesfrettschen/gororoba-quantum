> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.qubit_padding.next_padding_qubit_index.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.qubit_padding.next_padding_qubit_index.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 ea527b2296d7f69ef90db342ceb2665c48392bbb8399d622a4dad78b971cc7c6.

# iqm.qrisp_iqm.passes.routing.core.qubit_padding.next_padding_qubit_index

iqm.qrisp_iqm.passes.routing.core.qubit_padding.next_padding_qubit_index(*qc: QuantumCircuit*) → [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")  
First padding-qubit counter value that is free in `qc`.

Parameters:  
**qc** (*QuantumCircuit*) – The circuit to inspect.

Returns:  
`0` if `qc` carries no padding qubits, otherwise one above the largest counter found among its qubit identifiers.

Return type:  
[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")
