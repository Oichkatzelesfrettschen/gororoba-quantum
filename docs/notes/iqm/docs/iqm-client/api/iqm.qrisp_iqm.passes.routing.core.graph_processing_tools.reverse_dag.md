> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.reverse_dag.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.reverse_dag.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 5aeffd29ad61bbdde4a8bb58b4fc8081ce201ef94789b7dc46195f7918c7716d.

# iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.reverse_dag

iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.reverse_dag(*circuit_dag: [CircuitDAG](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG.html#iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG "iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG")*) → [CircuitDAG](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG.html#iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG "iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG")  
Build a backward instruction DAG by reversing the topological order.

Given a forward CSR instruction DAG whose rows are in topological order, return a new DAG where:

- All dependency edges are reversed (transposed).

- The row ordering is reversed so that the last forward node becomes backward row 0.

Mathematically the backward adjacency matrix is `B = P · A^T · P` where `A` is the forward adjacency matrix and `P` is the order-reversal permutation. This ensures that [`prune_dag()`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.prune_dag.html#iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.prune_dag "iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.prune_dag") (which slices the first `k` rows) peels off gates in backward order.

Parameters:  
**circuit_dag** ([*CircuitDAG*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG.html#iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG "iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG")) – CSR instruction DAG.

Returns:  
CSR instruction DAG with reversed topological order and reversed edges.

Return type:  
[*CircuitDAG*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG.html#iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG "iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG")
