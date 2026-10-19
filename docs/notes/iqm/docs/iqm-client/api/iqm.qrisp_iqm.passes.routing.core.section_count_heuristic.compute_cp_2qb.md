> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.section_count_heuristic.compute_cp_2qb.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.section_count_heuristic.compute_cp_2qb.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 c0046a46379e5a42581214f3a1e21a21722839a8c72e845f0dbfda072c8ede7b.

# iqm.qrisp_iqm.passes.routing.core.section_count_heuristic.compute_cp_2qb

iqm.qrisp_iqm.passes.routing.core.section_count_heuristic.compute_cp_2qb(*forward_dag: [CircuitDAG](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG.html#iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG "iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG")*, *instruction_list: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*) → [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")  
Compute the routing-relevant critical path length.

The longest path through the instruction DAG counting only 2-qubit gate nodes.

Single-qubit gates, measurements, and TerminatorNodes contribute weight 0 — they don’t create routing constraints.

Parameters:  
- **forward_dag** ([*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")) – Circuit DAG as returned by `convert_qc_to_sparse_dag()`.

- **instruction_list** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")) – Instruction list from `convert_qc_to_sparse_dag`. Entries are `Instruction` objects or `None` (for terminator nodes).

Returns:  
The 2-qubit critical path length.

Return type:  
[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")
