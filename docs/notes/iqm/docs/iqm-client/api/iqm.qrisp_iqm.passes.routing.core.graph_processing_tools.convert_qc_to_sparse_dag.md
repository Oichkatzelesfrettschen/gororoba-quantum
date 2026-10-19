> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.convert_qc_to_sparse_dag.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.convert_qc_to_sparse_dag.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 168927ec45c47c50363e823ce79a2d3a31968dc3c725157aba759f8044e353dd.

# iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.convert_qc_to_sparse_dag

iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.convert_qc_to_sparse_dag(*qc: QuantumCircuit*, *topo_sort: [Callable](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Callable "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*) → [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[CircuitDAG](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG.html#iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG "iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG"), [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[Instruction \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")\]\]  
Convert a quantum circuit into a DAG.

The DAG representation used here is the permeability DAG, which allows the routing algorithms to leverage permeability-induced commutation relations for shortcuts. See the preamble of this file for a full description.

Parameters:  
- **qc** (*QuantumCircuit*) – Quantum circuit that is to be converted.

- **topo_sort** ([*Callable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Callable "(in Python v3.11)") *\|* *None*) – Function that performs a topological sort on the PermeabilityGraph. Must accept a networkx DiGraph and return an iterable of nodes in topological order. The node ordering determines which instructions end up in which section when sectionized routing is used (prune_dag removes nodes by index threshold). By default, nx.topological_sort is used.

Returns:  
- circuit DAG

- corresponding Qrisp Instruction objects

Return type:  
[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*CircuitDAG*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG.html#iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG "iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG"), [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[*Instruction* \| None\]\]
