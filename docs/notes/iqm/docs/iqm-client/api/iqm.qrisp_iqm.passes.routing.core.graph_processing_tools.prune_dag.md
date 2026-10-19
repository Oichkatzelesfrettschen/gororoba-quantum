> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.prune_dag.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.prune_dag.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 61f455e87d61849abe1e93916dc9200343748c5cd219539aba3af740df6df1da.

# iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.prune_dag

iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.prune_dag(*circuit_dag: [CircuitDAG](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG.html#iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG "iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG")*, *pruning_threshold: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*) → [CircuitDAG](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG.html#iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG "iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG")  
Prune instructions below a threshold from an instruction DAG.

All instructions below the given threshold are removed.

Parameters:  
- **circuit_dag** ([*CircuitDAG*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG.html#iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG "iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG")) – Quantum circuit as a DAG.

- **pruning_threshold** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Any node that has an instruction index less than this number will be removed.

Returns:  
The pruned quantum circuit DAG. Note that the indices array can still contain nodes that are pruned, however these indices are negative, which is considered to be “invalid”

Return type:  
[*CircuitDAG*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG.html#iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG "iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.CircuitDAG")
