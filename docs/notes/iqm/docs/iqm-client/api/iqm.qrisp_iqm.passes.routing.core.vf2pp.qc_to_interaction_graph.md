> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.vf2pp.qc_to_interaction_graph.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.vf2pp.qc_to_interaction_graph.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 220c324d588b2753fd8a9193b163ab4431e9af42f73681e14c6f9fdb2e4a00b1.

# iqm.qrisp_iqm.passes.routing.core.vf2pp.qc_to_interaction_graph

iqm.qrisp_iqm.passes.routing.core.vf2pp.qc_to_interaction_graph(*qc: QuantumCircuit*) → [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)"), [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")\]  
Extract the qubit-interaction graph of a quantum circuit.

Builds an undirected graph with one node per circuit qubit, where edges represent two-qubit interactions in the circuit. Single-qubit gates, barriers, and measurements are ignored.

Parameters:  
**qc** (*QuantumCircuit*) – The quantum circuit to extract the interaction graph from.

Returns:  
- CSR index pointer array of the interaction graph

- CSR indices array of the interaction graph

Return type:  
[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)"), [*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")\]
